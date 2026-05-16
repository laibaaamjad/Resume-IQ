import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.extractor import extract_text_from_txt


def test_extract_txt():
    sample = b"John Doe\nPython Developer\nSkills: Python, React, SQL"
    result = extract_text_from_txt(sample)
    assert "Python" in result
    assert "John Doe" in result
    print("✅ test_extract_txt passed")


def test_extract_empty():
    result = extract_text_from_txt(b"")
    assert result == ""
    print("✅ test_extract_empty passed")


if __name__ == "__main__":
    test_extract_txt()
    test_extract_empty()
    print("\n✅ All extractor tests passed!")
