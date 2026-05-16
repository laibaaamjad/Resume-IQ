import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.skill_extractor import extract_skills, compare_skills


def test_extract_known_skills():
    text = "I have experience with Python, React, PostgreSQL, Docker, and AWS."
    skills = extract_skills(text)
    assert "python" in skills
    assert "react" in skills
    assert "postgresql" in skills
    assert "docker" in skills
    assert "aws" in skills
    print(f"✅ test_extract_known_skills passed — found: {skills}")


def test_compare_skills():
    resume_skills = ["python", "react", "sql", "git"]
    jd_skills = ["python", "react", "docker", "kubernetes", "sql"]
    result = compare_skills(resume_skills, jd_skills)
    assert "python" in result["matched"]
    assert "docker" in result["missing"]
    assert result["match_ratio"] == pytest_approx(0.6, abs=0.01)
    print(f"✅ test_compare_skills passed — ratio: {result['match_ratio']}")


def pytest_approx(value, abs=0.01):
    """Simple approximate comparison helper."""
    class Approx:
        def __init__(self, v, a): self.v, self.a = v, a
        def __eq__(self, other): return abs(other - self.v) <= self.a
    return Approx(value, abs)


if __name__ == "__main__":
    test_extract_known_skills()
    test_compare_skills()
    print("\n✅ All skill extractor tests passed!")
