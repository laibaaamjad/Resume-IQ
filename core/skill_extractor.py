# Extracts skills from text by matching against the master skills database

import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.skills_db import ALL_SKILLS, SKILL_CATEGORIES


def _build_skill_patterns():
    """
    Pre-compile regex patterns for each skill (sorted longest first
    to prefer multi-word matches like 'machine learning' over 'machine').
    """
    sorted_skills = sorted(ALL_SKILLS, key=len, reverse=True)
    patterns = {}
    for skill in sorted_skills:
        # Escape special regex chars, then allow flexible spacing
        escaped = re.escape(skill)
        # Allow flexible word boundaries; handle things like 'node.js', 'c++'
        pattern = r'(?<![a-z0-9])' + escaped + r'(?![a-z0-9])'
        patterns[skill] = re.compile(pattern, re.IGNORECASE)
    return patterns


_SKILL_PATTERNS = _build_skill_patterns()


def extract_skills(text: str) -> list[str]:
    """
    Extract all recognized skills from a block of text.

    Args:
        text: Raw or cleaned text string

    Returns:
        Sorted list of unique matched skill names (lowercase)
    """
    text_lower = text.lower()
    found = set()

    for skill, pattern in _SKILL_PATTERNS.items():
        if pattern.search(text_lower):
            found.add(skill)

    return sorted(found)


def extract_skills_by_category(text: str) -> dict[str, list[str]]:
    """
    Extract skills and group them by category.

    Args:
        text: Raw text

    Returns:
        dict mapping category name → list of found skills in that category
    """
    all_found = set(extract_skills(text))
    result = {}

    for category, skill_list in SKILL_CATEGORIES.items():
        matched = sorted([s for s in skill_list if s in all_found])
        if matched:
            result[category] = matched

    # Skills not in any named category
    categorized = set()
    for skills in result.values():
        categorized.update(skills)

    uncategorized = sorted(all_found - categorized)
    if uncategorized:
        result["Other"] = uncategorized

    return result


def compare_skills(resume_skills: list[str], jd_skills: list[str]) -> dict:
    """
    Compare resume skills against job description skills.

    Args:
        resume_skills: Skills extracted from resume
        jd_skills: Skills extracted from job description

    Returns:
        dict with:
          - 'matched': skills present in both
          - 'missing': skills in JD but not in resume
          - 'extra': skills in resume but not required by JD
          - 'match_ratio': float 0.0 – 1.0
    """
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    matched = sorted(resume_set & jd_set)
    missing = sorted(jd_set - resume_set)
    extra = sorted(resume_set - jd_set)

    match_ratio = len(matched) / len(jd_set) if jd_set else 0.0

    return {
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "match_ratio": match_ratio,
        "resume_count": len(resume_set),
        "jd_count": len(jd_set),
        "matched_count": len(matched),
        "missing_count": len(missing),
    }


def get_skill_importance(skills: list[str], jd_text: str) -> dict[str, int]:
    """
    Score each skill by how many times it appears in the JD text.
    Higher count = more important to the role.

    Args:
        skills: List of skill names
        jd_text: Raw job description text

    Returns:
        dict mapping skill → frequency count in JD
    """
    jd_lower = jd_text.lower()
    importance = {}
    for skill in skills:
        count = len(re.findall(re.escape(skill), jd_lower))
        importance[skill] = max(count, 1)  # At least 1 if matched
    return importance
