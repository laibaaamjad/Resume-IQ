import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.matcher import cosine_similarity, compute_composite_score, get_score_label
import numpy as np


def test_cosine_identical():
    v = np.array([1.0, 2.0, 3.0])
    result = cosine_similarity(v, v)
    assert abs(result - 1.0) < 0.001
    print("✅ test_cosine_identical passed")


def test_cosine_orthogonal():
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([0.0, 1.0, 0.0])
    result = cosine_similarity(v1, v2)
    assert result == 0.0
    print("✅ test_cosine_orthogonal passed")


def test_composite_score():
    score = compute_composite_score(0.8, 0.7, 0.45, 0.55)
    expected = round((0.45 * 0.8 + 0.55 * 0.7) * 100, 1)
    assert abs(score - expected) < 0.1
    print(f"✅ test_composite_score passed — score: {score}%")


def test_score_labels():
    assert "Excellent" in get_score_label(85)[0]
    assert "Good" in get_score_label(70)[0]
    assert "Moderate" in get_score_label(55)[0]
    assert "Weak" in get_score_label(40)[0]
    assert "Poor" in get_score_label(20)[0]
    print("✅ test_score_labels passed")


if __name__ == "__main__":
    test_cosine_identical()
    test_cosine_orthogonal()
    test_composite_score()
    test_score_labels()
    print("\n✅ All matcher tests passed!")
