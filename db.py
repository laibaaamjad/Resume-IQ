"""
ResumeIQ backend: users + comparison history.

DATABASE_URL examples
  local dev : sqlite:///resumeiq.db                      (default)
  MySQL     : mysql+pymysql://user:pass@host:3306/resumeiq
Set DATABASE_URL as an environment variable (EC2: systemd/.env, Beanstalk: Environment properties).

First-time setup:  python db.py      (creates tables + demo user + one sample record)
"""
import os
import re
import hashlib
from contextlib import contextmanager
from datetime import datetime

import bcrypt
from sqlalchemy import (create_engine, String, Text, Float, Integer, ForeignKey,
                        DateTime, JSON, UniqueConstraint, select, desc)
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column,
                            relationship, sessionmaker)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///resumeiq.db")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=1800)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class JobDescription(Base):
    __tablename__ = "job_descriptions"
    __table_args__ = (UniqueConstraint("user_id", "content_hash"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Resume(Base):
    __tablename__ = "resumes"
    __table_args__ = (UniqueConstraint("user_id", "content_hash"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    filename: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)          # extracted text
    content_hash: Mapped[str] = mapped_column(String(64))
    s3_key: Mapped[str | None] = mapped_column(String(500), nullable=True)  # optional original PDF
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Comparison(Base):
    __tablename__ = "comparisons"
    __table_args__ = (UniqueConstraint("jd_id", "resume_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    jd_id: Mapped[int] = mapped_column(ForeignKey("job_descriptions.id", ondelete="CASCADE"))
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"))
    score: Mapped[float] = mapped_column(Float)
    matched_skills: Mapped[list] = mapped_column(JSON)
    missing_skills: Mapped[list] = mapped_column(JSON)
    insights: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    jd = relationship("JobDescription", lazy="joined")
    resume = relationship("Resume", lazy="joined")


# ---------------------------------------------------------------- helpers
@contextmanager
def session_scope():
    s = SessionLocal()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


def _hash(text: str) -> str:
    norm = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(norm.encode()).hexdigest()


def init_db():
    Base.metadata.create_all(engine)


# ------------------------------------------------------------------- auth
def create_user(username: str, password: str) -> User | None:
    with session_scope() as s:
        if s.scalar(select(User).where(User.username == username)):
            return None
        pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        u = User(username=username, password_hash=pw)
        s.add(u)
        s.flush()
        return u


def authenticate(username: str, password: str) -> User | None:
    with session_scope() as s:
        u = s.scalar(select(User).where(User.username == username))
        if u and bcrypt.checkpw(password.encode(), u.password_hash.encode()):
            return u
    return None


# ---------------------------------------------------------------- history
def find_cached(user_id: int, jd_text: str, resume_text: str) -> Comparison | None:
    """Return a stored comparison if this exact JD + CV pair was already analysed."""
    with session_scope() as s:
        return s.scalar(
            select(Comparison)
            .join(JobDescription, Comparison.jd_id == JobDescription.id)
            .join(Resume, Comparison.resume_id == Resume.id)
            .where(Comparison.user_id == user_id,
                   JobDescription.content_hash == _hash(jd_text),
                   Resume.content_hash == _hash(resume_text)))


def save_comparison(user_id: int, jd_text: str, jd_title: str,
                    resume_text: str, resume_name: str, result: dict,
                    s3_key: str | None = None) -> Comparison:
    """result = {"score": float, "matched": [...], "missing": [...], "insights": [...]}"""
    with session_scope() as s:
        jh, rh = _hash(jd_text), _hash(resume_text)
        jd = s.scalar(select(JobDescription).where(
            JobDescription.user_id == user_id, JobDescription.content_hash == jh))
        if not jd:
            jd = JobDescription(user_id=user_id, title=jd_title or "Untitled job",
                                content=jd_text, content_hash=jh)
            s.add(jd)
        rs = s.scalar(select(Resume).where(
            Resume.user_id == user_id, Resume.content_hash == rh))
        if not rs:
            rs = Resume(user_id=user_id, filename=resume_name, content=resume_text,
                        content_hash=rh, s3_key=s3_key)
            s.add(rs)
        s.flush()
        c = Comparison(user_id=user_id, jd_id=jd.id, resume_id=rs.id,
                       score=result["score"], matched_skills=result.get("matched", []),
                       missing_skills=result.get("missing", []),
                       insights=result.get("insights", []))
        s.add(c)
        s.flush()
        return c


def get_history(user_id: int) -> list[Comparison]:
    with session_scope() as s:
        return list(s.scalars(select(Comparison)
                              .where(Comparison.user_id == user_id)
                              .order_by(desc(Comparison.created_at))).unique())


def delete_comparison(user_id: int, comparison_id: int) -> None:
    with session_scope() as s:
        c = s.get(Comparison, comparison_id)
        if c and c.user_id == user_id:
            s.delete(c)


# ------------------------------------------------------------------ seed
def seed_demo():
    """Demo account for the professor + one sample record so the tables are not empty."""
    init_db()
    u = create_user(os.getenv("DEMO_USER", "demo"), os.getenv("DEMO_PASS", "Demo@12345"))
    if u:
        save_comparison(
            u.id,
            "Looking for a Python backend developer with Docker, AWS and FastAPI experience.",
            "Backend Developer (sample)",
            "Python developer with Flask, SQL and Git experience. Built REST APIs.",
            "sample_resume.pdf",
            {"score": 72.5, "matched": ["python", "sql", "rest"],
             "missing": ["docker", "aws", "fastapi"],
             "insights": ["Add cloud and container keywords", "Quantify project impact"]})
        print("Demo user + sample comparison created.")
    else:
        print("Demo user already exists.")


if __name__ == "__main__":
    seed_demo()