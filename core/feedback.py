# Rule-based feedback engine: generates actionable improvement suggestions
# based on skill gaps, score, and analysis results

import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.skills_db import (
    PROGRAMMING_LANGUAGES, WEB_FRONTEND, WEB_BACKEND,
    DATABASES, CLOUD_DEVOPS, DATA_SCIENCE_ML,
    TOOLS_PLATFORMS, SOFT_SKILLS, CYBERSECURITY, MOBILE
)


# ── Category lookup for smarter suggestions ──────────────────────────────────

SKILL_TO_CATEGORY = {}
_category_map = {
    "Programming Language": PROGRAMMING_LANGUAGES,
    "Frontend Technology": WEB_FRONTEND,
    "Backend Technology": WEB_BACKEND,
    "Database": DATABASES,
    "Cloud / DevOps Tool": CLOUD_DEVOPS,
    "Data Science / ML Library": DATA_SCIENCE_ML,
    "Development Tool": TOOLS_PLATFORMS,
    "Soft Skill": SOFT_SKILLS,
    "Cybersecurity Tool": CYBERSECURITY,
    "Mobile Technology": MOBILE,
}
for _cat, _skills in _category_map.items():
    for _s in _skills:
        SKILL_TO_CATEGORY[_s] = _cat


# ── Suggestion templates ─────────────────────────────────────────────────────

SUGGESTION_TEMPLATES = {
    "Programming Language": (
        "Add hands-on experience with **{skill}** — consider building a small project "
        "or completing a free course on freeCodeCamp / CS50 / YouTube."
    ),
    "Frontend Technology": (
        "Learn **{skill}** for frontend development. "
        "The official docs + a small UI project are the fastest path."
    ),
    "Backend Technology": (
        "Get familiar with **{skill}** by building a REST API or integrating it "
        "into an existing project."
    ),
    "Database": (
        "Add **{skill}** experience — include a project where you designed a schema "
        "and wrote queries. Mention it explicitly in your skills section."
    ),
    "Cloud / DevOps Tool": (
        "Learn **{skill}** — even a free-tier AWS/GCP/Azure project or a Docker "
        "tutorial counts. Cloud certifications (free tier available) are a plus."
    ),
    "Data Science / ML Library": (
        "Add **{skill}** by working through a Kaggle notebook or a guided project. "
        "Include it in a GitHub repo employers can see."
    ),
    "Development Tool": (
        "Mention proficiency in **{skill}** explicitly in your resume. "
        "If you haven't used it, a 1-day tutorial is usually enough to add it honestly."
    ),
    "Soft Skill": (
        "Demonstrate **{skill}** through concrete examples — "
        "mention a time you led a team, resolved a conflict, or delivered under pressure."
    ),
    "Cybersecurity Tool": (
        "Add **{skill}** experience through platforms like TryHackMe, HackTheBox, "
        "or a personal homelab. Document it in a GitHub repo."
    ),
    "Mobile Technology": (
        "Build a simple mobile app using **{skill}** and publish it "
        "or put the code on GitHub to show recruiters."
    ),
    "default": (
        "Consider adding **{skill}** to your resume — it appears in the job description "
        "and could improve your ATS match score."
    ),
}


def generate_suggestions(
    missing_skills: list[str],
    score: float,
    resume_text: str,
    jd_text: str,
) -> dict:
    """
    Generate structured improvement suggestions based on analysis.

    Args:
        missing_skills: Skills in JD but not in resume
        score: Composite match score 0–100
        resume_text: Raw resume text
        jd_text: Raw job description text

    Returns:
        dict with:
          - 'skill_suggestions': list of per-skill tips
          - 'general_tips': list of general resume tips
          - 'priority_skills': top 5 most critical missing skills
          - 'resume_issues': structural issues detected
    """
    skill_suggestions = _generate_skill_suggestions(missing_skills)
    general_tips = _generate_general_tips(score, resume_text, jd_text)
    resume_issues = _detect_resume_issues(resume_text)
    priority_skills = missing_skills[:5]  # Top 5 most impactful

    return {
        "skill_suggestions": skill_suggestions,
        "general_tips": general_tips,
        "priority_skills": priority_skills,
        "resume_issues": resume_issues,
    }


def _generate_skill_suggestions(missing_skills: list[str]) -> list[dict]:
    """Generate a tip for each missing skill."""
    suggestions = []
    for skill in missing_skills[:15]:  # Cap at 15
        category = SKILL_TO_CATEGORY.get(skill, "default")
        template = SUGGESTION_TEMPLATES.get(category, SUGGESTION_TEMPLATES["default"])
        suggestions.append({
            "skill": skill,
            "category": category,
            "tip": template.format(skill=skill.title()),
        })
    return suggestions


def _generate_general_tips(score: float, resume_text: str, jd_text: str) -> list[str]:
    """Rule-based general resume improvement tips."""
    tips = []

    # Score-based advice
    if score < 35:
        tips.append(
            "🔴 **Your match score is very low.** "
            "Rewrite your resume to closely mirror the language in this job description. "
            "Use the same keywords, tools, and phrases the JD uses."
        )
    elif score < 50:
        tips.append(
            "🟠 **Moderate gaps detected.** "
            "Focus on adding the missing skills through projects or certifications, "
            "and update your summary to align with this role."
        )
    elif score < 65:
        tips.append(
            "🟡 **You're a reasonable candidate.** "
            "Adding 2–3 missing skills to real projects could push you into the top tier."
        )
    else:
        tips.append(
            "🟢 **Strong match!** Fine-tune your bullet points to mirror the JD's "
            "exact phrasing for maximum ATS score."
        )

    # Quantification check
    quantifiers = re.findall(r'\b\d+[\%x]?\b', resume_text)
    if len(quantifiers) < 3:
        tips.append(
            "📊 **Add numbers to your bullet points.** "
            "E.g., 'Improved load time by 40%', 'Managed a team of 6', "
            "'Processed 10,000+ records/day'. Quantified achievements stand out."
        )

    # Length check
    word_count = len(resume_text.split())
    if word_count < 200:
        tips.append(
            "📝 **Your resume seems short** (under 200 words detected). "
            "Add more detail about your projects, responsibilities, and impact."
        )
    elif word_count > 1000:
        tips.append(
            "✂️ **Consider condensing your resume.** "
            "ATS systems and recruiters prefer 1 page for <3 years experience. "
            "Focus on your most relevant achievements."
        )

    # Action verbs check
    action_verbs = [
        "developed", "built", "designed", "implemented", "led", "managed",
        "optimized", "reduced", "improved", "created", "architected",
        "deployed", "automated", "integrated", "launched"
    ]
    found_verbs = [v for v in action_verbs if v in resume_text.lower()]
    if len(found_verbs) < 3:
        tips.append(
            "💪 **Use strong action verbs.** Start bullet points with words like: "
            "Built, Developed, Designed, Optimized, Led, Automated, Deployed, Reduced."
        )

    # Project section check
    if "project" not in resume_text.lower():
        tips.append(
            "🚀 **Add a Projects section.** "
            "For students and junior devs, projects substitute for work experience. "
            "Include GitHub links for every project."
        )

    # GitHub / portfolio
    if "github" not in resume_text.lower() and "portfolio" not in resume_text.lower():
        tips.append(
            "🔗 **Add your GitHub / Portfolio URL.** "
            "Recruiters check GitHub. Make sure your pinned repos are clean and documented."
        )

    # Certifications
    jd_lower = jd_text.lower()
    cert_keywords = ["certification", "certified", "certificate", "aws", "gcp", "azure"]
    jd_wants_certs = any(k in jd_lower for k in cert_keywords)
    resume_has_certs = "certif" in resume_text.lower()
    if jd_wants_certs and not resume_has_certs:
        tips.append(
            "🏆 **Consider adding certifications.** "
            "The JD mentions certifications. Free options: AWS Cloud Practitioner, "
            "Google IT Support, Meta Front-End Developer (Coursera), or freeCodeCamp."
        )

    return tips


def _detect_resume_issues(resume_text: str) -> list[str]:
    """
    Detect common structural problems in the resume.
    """
    issues = []
    text_lower = resume_text.lower()

    # Check for contact info
    has_email = bool(re.search(r'[a-z0-9.]+@[a-z0-9.]+\.[a-z]{2,}', text_lower))
    if not has_email:
        issues.append("⚠️ No email address detected. Make sure your contact info is present.")

    # Check for key sections
    key_sections = {
        "education": ["education", "academic", "degree", "university", "college"],
        "experience": ["experience", "employment", "work history", "internship"],
        "skills": ["skills", "technologies", "tech stack", "proficiencies"],
    }

    for section, keywords in key_sections.items():
        if not any(k in text_lower for k in keywords):
            issues.append(
                f"⚠️ No '{section.title()}' section detected. "
                f"Add a clear {section} section for ATS compatibility."
            )

    # Objective / summary
    if not any(k in text_lower for k in ["summary", "objective", "profile", "about"]):
        issues.append(
            "💡 Consider adding a 2–3 line professional summary at the top. "
            "Tailor it to each specific job application."
        )

    return issues


def generate_quick_wins(missing_skills: list[str], matched_skills: list[str]) -> list[str]:
    """
    Generate 'quick win' actions — easy things to fix right now.
    """
    quick_wins = []

    if len(missing_skills) > 0:
        top_missing = missing_skills[:3]
        skill_str = ", ".join(f"**{s}**" for s in top_missing)
        quick_wins.append(
            f"➕ Add {skill_str} to your Skills section if you have any experience "
            "with them — even personal projects count."
        )

    if len(matched_skills) >= 5:
        quick_wins.append(
            "✅ You already match several key skills. "
            "Make sure each matched skill appears in your bullet points "
            "with a concrete example, not just in the skills list."
        )

    quick_wins.append(
        "🎯 **Tailor your resume summary** to echo this specific job description. "
        "Copy 2–3 phrases directly from the JD into your summary."
    )

    quick_wins.append(
        "🔍 **Run your resume through another ATS simulator** (like Jobscan or Resume Worded) "
        "for a second opinion after making changes."
    )

    return quick_wins
