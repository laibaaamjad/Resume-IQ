import streamlit as st
import sys
import os
import time
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

#Path setup 
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Page config (MUST be first Streamlit call) 
st.set_page_config(
    page_title="ResumeIQ – AI Resume Screener",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS 
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

import db

@st.cache_resource
def _init_db():
    db.init_db()
_init_db()

from core.extractor import extract_text
from core.preprocessor import preprocess, extract_sections
from core.skill_extractor import extract_skills, extract_skills_by_category, compare_skills
from core.matcher import compute_semantic_similarity, compute_composite_score, get_score_label
from core.classifier import get_classifier
from core.feedback import generate_suggestions, generate_quick_wins
from utils.text_cleaner import extract_contact_info, extract_name_heuristic, get_text_stats
from utils.report_generator import generate_text_report


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar():
    with st.sidebar:
        st.markdown("## 🧠 ResumeIQ")
        st.radio("Navigate", ["🔍 Analyze", "📜 History"], key="page")
        st.caption(f"Signed in as **{st.session_state['user']['username']}**")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
        st.divider()

        st.markdown("### ⚙️ Settings")

        weight_skill = st.slider(
            "Skill Match Weight",
            min_value=0.3, max_value=0.8, value=0.55, step=0.05,
            help="How much skill keyword overlap influences your score"
        )
        weight_semantic = round(1.0 - weight_skill, 2)
        st.caption(f"Semantic similarity weight: {weight_semantic}")

        st.divider()

        show_raw = st.checkbox("Show extracted text preview", value=False)
        show_debug = st.checkbox("Show preprocessing stats", value=False)

        st.divider()

        st.markdown("### 📖 How It Works")
        st.markdown("""
1. Upload your **resume** (PDF or TXT)
2. Paste the **job description**
3. Click **Analyze**
4. Get your **match score**, skill gaps & tips
        """)

        st.divider()

    return {
        "weight_skill": weight_skill,
        "weight_semantic": weight_semantic,
        "show_raw": show_raw,
        "show_debug": show_debug,
        "page": st.session_state.get("page", "🔍 Analyze"),
    }


# ══════════════════════════════════════════════════════════════════════════════
#  ANALYSIS PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def run_analysis(resume_text: str, jd_text: str, weight_skill: float, weight_semantic: float) -> dict:
    """
    Full analysis pipeline. Cached so re-runs don't recompute unnecessarily.

    Args:
        resume_text: Raw text from resume
        jd_text: Raw text from job description
        weight_skill: Weight for skill matching
        weight_semantic: Weight for semantic similarity

    Returns:
        dict with all analysis results
    """
    # 1. Preprocess both texts
    resume_proc = preprocess(resume_text)
    jd_proc = preprocess(jd_text)

    # 2. Extract skills
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    resume_skills_by_cat = extract_skills_by_category(resume_text)
    jd_skills_by_cat = extract_skills_by_category(jd_text)

    # 3. Compare skills
    skill_comparison = compare_skills(resume_skills, jd_skills)

    # 4. Semantic similarity
    semantic_score = compute_semantic_similarity(
        resume_proc["joined"],
        jd_proc["joined"]
    )

    # 5. Composite score
    composite_score = compute_composite_score(
        semantic_score=semantic_score,
        skill_match_ratio=skill_comparison["match_ratio"],
        weight_semantic=weight_semantic,
        weight_skill=weight_skill,
    )
    score_label, score_color = get_score_label(composite_score)

    # 6. Job category classification
    classifier = get_classifier()
    category_result = classifier.predict_both(resume_text, jd_text)

    # 7. Contact info
    contact = extract_contact_info(resume_text)
    name = extract_name_heuristic(resume_text)

    # 8. Resume sections
    sections = extract_sections(resume_text)

    # 9. Feedback
    suggestions = generate_suggestions(
        missing_skills=skill_comparison["missing"],
        score=composite_score,
        resume_text=resume_text,
        jd_text=jd_text,
    )
    quick_wins = generate_quick_wins(
        missing_skills=skill_comparison["missing"],
        matched_skills=skill_comparison["matched"],
    )

    # 10. Text stats
    resume_stats = get_text_stats(resume_text)
    jd_stats = get_text_stats(jd_text)

    return {
        "score": composite_score,
        "score_label": score_label,
        "score_color": score_color,
        "semantic_score": round(semantic_score * 100, 1),
        "skill_match_ratio": round(skill_comparison["match_ratio"] * 100, 1),
        "matched_skills": skill_comparison["matched"],
        "missing_skills": skill_comparison["missing"],
        "extra_skills": skill_comparison["extra"],
        "resume_skills_by_cat": resume_skills_by_cat,
        "jd_skills_by_cat": jd_skills_by_cat,
        "skill_comparison": skill_comparison,
        "category": category_result,
        "contact": contact,
        "name": name,
        "sections": sections,
        "suggestions": suggestions,
        "quick_wins": quick_wins,
        "resume_stats": resume_stats,
        "jd_stats": jd_stats,
        "resume_proc": resume_proc,
        "jd_proc": jd_proc,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  UI COMPONENTS
# ══════════════════════════════════════════════════════════════════════════════

def render_score_gauge(score: float, color: str, label: str):
    """Render an animated Plotly gauge chart for the match score."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        number={"suffix": "%", "font": {"size": 48, "color": color}},
        title={"text": label, "font": {"size": 20, "color": "#E0E0F0"}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 2,
                "tickcolor": "#E0E0F0",
                "tickfont": {"color": "#E0E0F0"},
            },
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 35],   "color": "rgba(213,0,0,0.15)"},
                {"range": [35, 50],  "color": "rgba(255,109,0,0.15)"},
                {"range": [50, 65],  "color": "rgba(255,214,0,0.15)"},
                {"range": [65, 80],  "color": "rgba(100,221,23,0.15)"},
                {"range": [80, 100], "color": "rgba(0,200,83,0.2)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 4},
                "thickness": 0.8,
                "value": score,
            },
        },
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=20, b=20),
        height=280,
        font={"color": "#E0E0F0"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_score_breakdown(semantic: float, skill_ratio: float, composite: float):
    """Bar chart comparing score components."""
    fig = go.Figure(go.Bar(
        x=["Semantic\nSimilarity", "Skill\nMatch", "Overall\nScore"],
        y=[semantic, skill_ratio, composite],
        marker_color=["#48CFAD", "#6C63FF", "#FFD600"],
        text=[f"{v:.1f}%" for v in [semantic, skill_ratio, composite]],
        textposition="outside",
        textfont={"color": "#E0E0F0", "size": 14},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=10),
        height=250,
        yaxis=dict(range=[0, 110], showgrid=False, color="#E0E0F0"),
        xaxis=dict(color="#E0E0F0", tickfont=dict(size=12)),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_skills_treemap(skills_by_cat: dict, title: str):
    """Treemap of skills grouped by category."""
    if not skills_by_cat:
        st.info("No skills detected in this text.")
        return

    labels, parents, values = [], [], []
    labels.append(title)
    parents.append("")
    values.append(0)

    for category, skills in skills_by_cat.items():
        labels.append(category)
        parents.append(title)
        values.append(len(skills))
        for skill in skills:
            labels.append(skill)
            parents.append(category)
            values.append(1)

    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        textinfo="label",
        marker=dict(
            colorscale="Viridis",
            line=dict(width=1, color="#0F0F1A"),
        ),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_skill_pills(skills: list[str], pill_class: str):
    """Render skills as colored HTML pills."""
    if not skills:
        st.caption("None detected.")
        return
    pills_html = "".join(
        f'<span class="skill-pill {pill_class}">{s}</span>'
        for s in skills
    )
    st.markdown(f'<div style="line-height:2.2">{pills_html}</div>', unsafe_allow_html=True)


def render_category_donut(all_scores: dict):
    """Donut chart for category confidence scores."""
    if not all_scores:
        return
    labels = list(all_scores.keys())
    values = list(all_scores.values())
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        textinfo="label+percent",
        marker=dict(
            colors=px.colors.qualitative.Vivid[:len(labels)],
            line=dict(color="#0F0F1A", width=2),
        ),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=280,
        showlegend=False,
        font={"color": "#E0E0F0"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_missing_skills_bar(missing_skills: list[str], jd_text: str):
    """Horizontal bar chart for missing skills (simulated importance)."""
    if not missing_skills:
        st.success("✅ No missing skills! You match all detected JD requirements.")
        return

    from core.skill_extractor import get_skill_importance
    importance = get_skill_importance(missing_skills[:12], jd_text)
    skills = list(importance.keys())
    counts = list(importance.values())

    fig = go.Figure(go.Bar(
        x=counts,
        y=skills,
        orientation='h',
        marker_color="#FF5252",
        text=counts,
        textposition="outside",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=max(200, len(skills) * 35),
        xaxis=dict(color="#E0E0F0", showgrid=False),
        yaxis=dict(color="#E0E0F0", autorange="reversed"),
        font={"color": "#E0E0F0"},
    )
    st.plotly_chart(fig, use_container_width=True)

def make_jd_title(jd_text: str) -> str:
    first = next((l.strip() for l in jd_text.splitlines() if l.strip()), "Untitled job")
    return first[:200]


def require_login():
    if "user" in st.session_state:
        return
    st.markdown("## 🔐 Sign in to ResumeIQ")
    tab_in, tab_up = st.tabs(["Login", "Sign up"])
    with tab_in:
        u = st.text_input("Username", key="li_u")
        p = st.text_input("Password", type="password", key="li_p")
        if st.button("Login"):
            user = db.authenticate(u, p)
            if user:
                st.session_state["user"] = {"id": user.id, "username": user.username}
                st.rerun()
            else:
                st.error("Invalid username or password")
    with tab_up:
        nu = st.text_input("Choose a username", key="su_u")
        npw = st.text_input("Choose a password (6+ chars)", type="password", key="su_p")
        if st.button("Create account"):
            if len(nu) < 3 or len(npw) < 6:
                st.error("Username needs 3+ chars and password 6+ chars.")
            elif db.create_user(nu, npw):
                st.success("Account created. Switch to the Login tab.")
            else:
                st.error("That username is taken.")
    st.stop()


def load_into_analyze(jd_text, resume_text, resume_name):
    st.session_state["loaded_jd"] = jd_text
    st.session_state["loaded_resume"] = {"text": resume_text, "name": resume_name}
    st.session_state["page"] = "🔍 Analyze"


def render_history():
    uid = st.session_state["user"]["id"]
    st.markdown("## 📜 Analysis History")
    rows = db.get_history(uid)
    if not rows:
        st.info("No analyses yet. Run one from the Analyze page.")
        return
    for c in rows:
        label = f"{c.jd.title}  ×  {c.resume.filename}  |  {c.score:.0f}%  |  {c.created_at:%d %b %Y %H:%M}"
        with st.expander(label):
            t1, t2, t3 = st.tabs(["Summary", "Job description", "Resume"])
            with t1:
                st.markdown("**Matched:** " + (", ".join(c.matched_skills) or "None"))
                st.markdown("**Missing:** " + (", ".join(c.missing_skills) or "None"))
                for tip in c.insights[:6]:
                    st.markdown(f"- {tip}")
            with t2:
                st.text(c.jd.content)
            with t3:
                st.text(c.resume.content)
            b1, b2 = st.columns(2)
            b1.button("📂 Load into Analyze", key=f"load{c.id}",
                      on_click=load_into_analyze,
                      args=(c.jd.content, c.resume.content, c.resume.filename))
            if b2.button("🗑 Delete", key=f"del{c.id}"):
                db.delete_comparison(uid, c.id)
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    require_login()
    settings = render_sidebar()
    if settings["page"] == "📜 History":
        render_history()
        return

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown("""
        <div style="text-align:center; padding: 1.5rem 0 0.5rem 0;">
            <h1 style="font-size:3rem; font-weight:700; margin:0;">
                🧠 Resume<span style="color:#6C63FF;">IQ</span>
            </h1>
            <p style="color:#9090B0; font-size:1.1rem; margin-top:0.3rem;">
                AI-Powered Resume Screening &amp; Skill Gap Analyzer
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Input Section ─────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("### 📄 Upload Your Resume")
        use_sample = st.checkbox("Use sample resume (for testing)", value=False)
        resume_text_raw = ""
        resume_name = ""
        loaded = st.session_state.get("loaded_resume")

        if loaded:
            resume_text_raw = loaded["text"]
            resume_name = loaded["name"]
            st.info(f"📂 Loaded from history: {resume_name}")
            if st.button("✖ Clear loaded data"):
                st.session_state.pop("loaded_resume", None)
                st.session_state.pop("loaded_jd", None)
                st.rerun()
        elif use_sample:
            sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_resume.txt")
            with open(sample_path, "r") as f:
                resume_text_raw = f.read()
            resume_name = "sample_resume.txt"
            st.success("✅ Sample resume loaded.")

        else:
            uploaded_file = st.file_uploader(
                "Upload PDF or TXT",
                type=["pdf", "txt"],
                help="Scanned PDFs (image-only) may not extract well. Use a text-based PDF."
            )
            if uploaded_file is not None:
                resume_name = uploaded_file.name
                try:
                    with st.spinner("Extracting text from resume..."):
                        resume_text_raw = extract_text(uploaded_file)
                    st.success(f"✅ Extracted {len(resume_text_raw.split())} words.")
                except ValueError as e:
                    st.error(str(e))

        if settings["show_raw"] and resume_text_raw:
            with st.expander("📋 Resume Text Preview"):
                st.text(resume_text_raw[:1500] + ("..." if len(resume_text_raw) > 1500 else ""))

    with col_right:
        st.markdown("### 📋 Paste Job Description")
        sample_jd = """Software Engineer – Full Stack (Python / React)

We are looking for a skilled Software Engineer to join our growing team.

Requirements:
• 2+ years experience with Python and JavaScript/TypeScript
• Strong proficiency in React and Node.js
• Experience with PostgreSQL and MongoDB
• Familiarity with Docker, AWS, and CI/CD pipelines (GitHub Actions)
• Experience with REST API design and GraphQL
• Knowledge of machine learning or data science (TensorFlow/PyTorch is a plus)
• Proficiency with Git, Agile/Scrum methodology
• Strong communication and teamwork skills

Nice to have:
• Experience with Kubernetes and cloud deployments
• Redis caching, microservices architecture
• TypeScript proficiency
"""
        jd_text_raw = st.text_area(
            "Paste JD here",
                        value=st.session_state.get("loaded_jd") or (sample_jd if use_sample else ""),
            height=340,
            placeholder="Paste the full job description text here...",
        )

    # ── Analyze Button ────────────────────────────────────────────────────────
    st.markdown("")
    col_btn, col_note = st.columns([1, 3])
    with col_btn:
        analyze_clicked = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)
    with col_note:
        st.caption(
            "First run loads the AI model (~30 seconds). Subsequent runs are fast."
        )

    # ── Validation ───────────────────────────────────────────────────────────
    if analyze_clicked:
        if not resume_text_raw.strip():
            st.error("⚠️ Please upload a resume or check 'Use sample resume'.")
            st.stop()
        if not jd_text_raw.strip():
            st.error("⚠️ Please paste a job description.")
            st.stop()

        # ── Run Pipeline ──────────────────────────────────────────────────────
        with st.spinner("🧠 Analyzing... (first run loads AI model, ~20–30 sec)"):
            start = time.time()
            result = run_analysis(
                resume_text=resume_text_raw,
                jd_text=jd_text_raw,
                weight_skill=settings["weight_skill"],
                weight_semantic=settings["weight_semantic"],
            )
            elapsed = round(time.time() - start, 2)

        st.success(f"✅ Analysis complete in {elapsed}s")
        try:
            uid = st.session_state["user"]["id"]
            if db.find_cached(uid, jd_text_raw, resume_text_raw) is None:
                db.save_comparison(
                    uid, jd_text_raw, make_jd_title(jd_text_raw),
                    resume_text_raw, resume_name or "pasted_resume",
                    {
                        "score": float(result["score"]),
                        "matched": list(result["matched_skills"]),
                        "missing": list(result["missing_skills"]),
                        "insights": [str(x) for x in
                                     list(result["quick_wins"]) + list(result["suggestions"]["general_tips"])],
                    },
                )
                st.toast("Saved to history 📜")
        except Exception as e:
            st.warning(f"Could not save to history: {e}")
        
        st.divider()

        # ════════════════════════════════════════════════════════════════════
        #  RESULTS — ROW 1: Score + Breakdown
        # ════════════════════════════════════════════════════════════════════

        st.markdown("## 📊 Match Analysis")

        r1_col1, r1_col2, r1_col3 = st.columns([1.5, 1.5, 1], gap="large")

        with r1_col1:
            st.markdown("#### Overall Match Score")
            render_score_gauge(result["score"], result["score_color"], result["score_label"])

        with r1_col2:
            st.markdown("#### Score Breakdown")
            render_score_breakdown(
                result["semantic_score"],
                result["skill_match_ratio"],
                result["score"],
            )

        with r1_col3:
            st.markdown("#### Quick Stats")
            st.metric("Matched Skills", f"{result['skill_comparison']['matched_count']}")
            st.metric("Missing Skills", f"{result['skill_comparison']['missing_count']}")
            st.metric("Resume Skills", f"{result['skill_comparison']['resume_count']}")
            st.metric("JD Skills", f"{result['skill_comparison']['jd_count']}")
            st.metric("Semantic Score", f"{result['semantic_score']}%")

            if result["name"]:
                st.markdown(f"**Candidate:** {result['name']}")
            if result["contact"].emails:
                st.markdown(f"**Email:** {result['contact'].emails[0]}")

        st.divider()

        # ════════════════════════════════════════════════════════════════════
        #  RESULTS — ROW 2: Skills
        # ════════════════════════════════════════════════════════════════════

        st.markdown("## 🛠️ Skill Analysis")

        tab1, tab2, tab3, tab4 = st.tabs([
            "✅ Matched Skills", "❌ Missing Skills", "➕ Extra Skills", "📂 By Category"
        ])

        with tab1:
            st.markdown(f"**{len(result['matched_skills'])} skills matched** between your resume and the JD:")
            render_skill_pills(result["matched_skills"], "skill-matched")

        with tab2:
            st.markdown(f"**{len(result['missing_skills'])} skills missing** — present in JD but not in your resume:")
            if result["missing_skills"]:
                render_missing_skills_bar(result["missing_skills"], jd_text_raw)
            render_skill_pills(result["missing_skills"], "skill-missing")

        with tab3:
            st.markdown(
                f"**{len(result['extra_skills'])} extra skills** — in your resume but not required by this JD:"
            )
            st.caption("These are still valuable! Keep them for roles that need them.")
            render_skill_pills(result["extra_skills"], "skill-extra")

        with tab4:
            cat_col1, cat_col2 = st.columns(2)
            with cat_col1:
                st.markdown("**Resume Skills by Category**")
                render_skills_treemap(result["resume_skills_by_cat"], "Resume")
            with cat_col2:
                st.markdown("**JD Skills by Category**")
                render_skills_treemap(result["jd_skills_by_cat"], "Job Description")

        st.divider()

        # ════════════════════════════════════════════════════════════════════
        #  RESULTS — ROW 3: Classification
        # ════════════════════════════════════════════════════════════════════

        st.markdown("## 🏷️ Job Category Classification")

        cl_col1, cl_col2 = st.columns([2, 1])

        with cl_col1:
            cat_data = result["category"]

            # Alignment banner
            if cat_data["aligned"]:
                st.success(cat_data["alignment_note"])
            else:
                st.warning(cat_data["alignment_note"])

            # Resume vs JD category comparison
            compare_df = pd.DataFrame([
                {
                    "Text": "Your Resume",
                    "Detected Category": cat_data["resume"]["category"],
                    "Confidence": f"{cat_data['resume']['confidence']}%",
                },
                {
                    "Text": "Job Description",
                    "Detected Category": cat_data["jd"]["category"],
                    "Confidence": f"{cat_data['jd']['confidence']}%",
                },
            ])
            st.dataframe(compare_df, use_container_width=True, hide_index=True)

        with cl_col2:
            st.markdown("**Category Confidence (JD)**")
            render_category_donut(cat_data["jd"]["all_scores"])

        st.divider()

        # ════════════════════════════════════════════════════════════════════
        #  RESULTS — ROW 4: Feedback & Suggestions
        # ════════════════════════════════════════════════════════════════════

        st.markdown("## 💡 Improvement Suggestions")

        suggestions = result["suggestions"]

        # Resume structural issues
        if suggestions["resume_issues"]:
            st.markdown("### ⚠️ Resume Issues Detected")
            for issue in suggestions["resume_issues"]:
                st.warning(issue)

        # Quick wins
        st.markdown("### ⚡ Quick Wins (Do These First)")
        for qw in result["quick_wins"]:
            st.markdown(f'<div class="tip-card">{qw}</div>', unsafe_allow_html=True)

        # General tips
        st.markdown("### 📝 General Tips")
        for tip in suggestions["general_tips"]:
            st.markdown(f'<div class="tip-card">{tip}</div>', unsafe_allow_html=True)

        # Per-skill tips
        if suggestions["skill_suggestions"]:
            st.markdown("### 🛠️ Skill-Specific Tips")
            for item in suggestions["skill_suggestions"][:10]:
                with st.expander(f"🔴 How to add: **{item['skill'].title()}** ({item['category']})"):
                    st.markdown(item["tip"])

        st.divider()

        # ════════════════════════════════════════════════════════════════════
        #  RESULTS — ROW 5: Debug + Report
        # ════════════════════════════════════════════════════════════════════

        if settings["show_debug"]:
            st.markdown("## 🔬 Preprocessing Stats")
            debug_col1, debug_col2 = st.columns(2)
            with debug_col1:
                st.markdown("**Resume Stats**")
                st.json(result["resume_stats"])
                st.caption(f"Lemmatized token count: {len(result['resume_proc']['lemmatized'])}")
            with debug_col2:
                st.markdown("**JD Stats**")
                st.json(result["jd_stats"])
                st.caption(f"Lemmatized token count: {len(result['jd_proc']['lemmatized'])}")

        # ── Download Report ───────────────────────────────────────────────
        st.markdown("### 📥 Download Report")
        report_text = generate_text_report(
            analysis_result={
                "score": result["score"],
                "score_label": result["score_label"],
                "matched_skills": result["matched_skills"],
                "missing_skills": result["missing_skills"],
                "category": result["category"]["jd"],
                "suggestions": result["suggestions"],
            },
            candidate_name=result["name"] or "Candidate",
        )

        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            st.download_button(
                label="📄 Download Text Report",
                data=report_text,
                file_name="resumeiq_report.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with dl_col2:
            import json
            json_report = json.dumps({
                "score": result["score"],
                "score_label": result["score_label"],
                "semantic_score": result["semantic_score"],
                "skill_match_ratio": result["skill_match_ratio"],
                "matched_skills": result["matched_skills"],
                "missing_skills": result["missing_skills"],
                "extra_skills": result["extra_skills"],
                "category": result["category"],
                "suggestions": result["suggestions"],
            }, indent=2)
            st.download_button(
                label="📊 Download JSON Report",
                data=json_report,
                file_name="resumeiq_report.json",
                mime="application/json",
                use_container_width=True,
            )

    else:
        # ── Landing state ────────────────────────────────────────────────────
        st.markdown("""
            <div style="text-align:center; padding:3rem; color:#6060A0;">
                <div style="font-size:5rem;">🧠</div>
                <h3 style="color:#9090C0;">Upload your resume & paste a job description to get started</h3>
                <p>You'll get a match score, skill gap analysis, and personalized improvement tips.</p>
            </div>
        """, unsafe_allow_html=True)

        # Feature cards
        fc1, fc2, fc3, fc4 = st.columns(4)
        features = [
            ("📊", "Match Score", "AI-powered 0–100% compatibility score"),
            ("🛠️", "Skill Gaps", "See exactly what skills you're missing"),
            ("🏷️", "Job Category", "Naive Bayes classification of your field"),
            ("💡", "Smart Tips", "Actionable suggestions to improve your resume"),
        ]
        for col, (icon, title, desc) in zip([fc1, fc2, fc3, fc4], features):
            with col:
                st.markdown(f"""
                    <div style="background:rgba(108,99,255,0.08);border:1px solid rgba(108,99,255,0.2);
                    border-radius:12px;padding:1.2rem;text-align:center;height:140px;">
                        <div style="font-size:2rem;">{icon}</div>
                        <div style="font-weight:600;color:#C0BCFF;margin:0.3rem 0;">{title}</div>
                        <div style="font-size:0.82rem;color:#8080B0;">{desc}</div>
                    </div>
                """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
