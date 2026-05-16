# Semantic similarity using MiniLM embeddings + cosine similarity
# Also computes a composite weighted score combining skill overlap + semantics

import numpy as np
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_model():
    """
    Load the sentence-transformer model once and cache it.
    Uses 'all-MiniLM-L6-v2' — lightweight, fast, accurate.
    """
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading MiniLM model...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model
    except Exception as e:
        logger.error(f"Could not load SentenceTransformer: {e}")
        return None


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.

    Returns:
        Float in range [-1, 1], clipped to [0, 1] for readability
    """
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    similarity = np.dot(vec_a, vec_b) / (norm_a * norm_b)
    return float(np.clip(similarity, 0.0, 1.0))


def compute_semantic_similarity(text_a: str, text_b: str) -> float:
    """
    Compute semantic similarity between two text blocks using MiniLM.

    Args:
        text_a: Resume text (preprocessed)
        text_b: Job description text (preprocessed)

    Returns:
        Similarity score 0.0 – 1.0
    """
    model = _load_model()

    if model is None:
        # Fallback: basic keyword overlap ratio
        logger.warning("Using keyword fallback for similarity (model not loaded)")
        return _keyword_overlap_fallback(text_a, text_b)

    try:
        embeddings = model.encode([text_a, text_b], convert_to_numpy=True)
        score = cosine_similarity(embeddings[0], embeddings[1])
        return score
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return _keyword_overlap_fallback(text_a, text_b)


def _keyword_overlap_fallback(text_a: str, text_b: str) -> float:
    """
    Simple word overlap ratio used if embedding model fails.
    Jaccard similarity on word sets.
    """
    set_a = set(text_a.lower().split())
    set_b = set(text_b.lower().split())
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def compute_composite_score(
    semantic_score: float,
    skill_match_ratio: float,
    weight_semantic: float = 0.45,
    weight_skill: float = 0.55,
) -> float:
    """
    Weighted composite match score combining:
      - Semantic similarity (embedding cosine similarity)
      - Skill match ratio (matched skills / total JD skills)

    Weights can be tuned. Default: skill overlap is weighted higher
    because ATS systems are keyword-driven.

    Args:
        semantic_score: Float 0–1 from compute_semantic_similarity
        skill_match_ratio: Float 0–1 from skill comparison
        weight_semantic: Weight for semantic score
        weight_skill: Weight for skill overlap

    Returns:
        Composite score as percentage 0–100 (rounded to 1 decimal)
    """
    assert abs(weight_semantic + weight_skill - 1.0) < 0.01, \
        "Weights must sum to 1.0"

    composite = (weight_semantic * semantic_score) + (weight_skill * skill_match_ratio)
    return round(composite * 100, 1)


def get_score_label(score: float) -> tuple[str, str]:
    """
    Map numeric score to a human-readable label and color hex.

    Args:
        score: Score 0–100

    Returns:
        (label, color_hex)
    """
    if score >= 80:
        return "Excellent Match ✅", "#00C853"
    elif score >= 65:
        return "Good Match 👍", "#64DD17"
    elif score >= 50:
        return "Moderate Match ⚠️", "#FFD600"
    elif score >= 35:
        return "Weak Match 🔻", "#FF6D00"
    else:
        return "Poor Match ❌", "#D50000"


def compute_section_similarities(
    resume_sections: dict,
    jd_text: str
) -> dict[str, float]:
    """
    Compute similarity of specific resume sections against full JD.
    Useful for showing which sections match best.

    Args:
        resume_sections: Dict of section_name → section_text
        jd_text: Full job description text

    Returns:
        Dict of section_name → similarity score 0–100
    """
    results = {}
    model = _load_model()

    if model is None or not resume_sections:
        return results

    try:
        jd_embedding = model.encode([jd_text], convert_to_numpy=True)[0]

        for section_name, section_text in resume_sections.items():
            if not section_text.strip():
                continue
            sec_embedding = model.encode([section_text], convert_to_numpy=True)[0]
            sim = cosine_similarity(sec_embedding, jd_embedding)
            results[section_name] = round(sim * 100, 1)
    except Exception as e:
        logger.error(f"Section similarity error: {e}")

    return results
