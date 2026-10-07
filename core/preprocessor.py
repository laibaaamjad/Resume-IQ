# NLP preprocessing pipeline: clean → tokenize → remove stopwords → lemmatize

import re
import string
import logging

logger = logging.getLogger(__name__)

# NLTK setup 
import nltk

# Built-in minimal English stopwords fallback (used if NLTK download fails)
_BUILTIN_STOPWORDS = {
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
    "yourself","yourselves","he","him","his","himself","she","her","hers",
    "herself","it","its","itself","they","them","their","theirs","themselves",
    "what","which","who","whom","this","that","these","those","am","is","are",
    "was","were","be","been","being","have","has","had","having","do","does",
    "did","doing","a","an","the","and","but","if","or","because","as","until",
    "while","of","at","by","for","with","about","against","between","into",
    "through","during","before","after","above","below","to","from","up",
    "down","in","out","on","off","over","under","again","further","then",
    "once","here","there","when","where","why","how","all","both","each",
    "few","more","most","other","some","such","no","nor","not","only","own",
    "same","so","than","too","very","s","t","can","will","just","don","should",
    "now","d","ll","m","o","re","ve","y","ain","aren","couldn","didn","doesn",
    "hadn","hasn","haven","isn","ma","mightn","mustn","needn","shan","shouldn",
    "wasn","weren","won","wouldn","also","get","may","might","us","any","many",
}

def _ensure_nltk_data():
    """Download NLTK resources if missing. Safe to call repeatedly."""
    for pkg in ("punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4"):
        try:
            nltk.download(pkg, quiet=True)
        except Exception:
            pass  # a missing optional package should not crash the app

_ensure_nltk_data()

# Load NLTK components with graceful fallbacks
try:
    from nltk.corpus import stopwords as _nltk_stopwords
    STOP_WORDS = set(_nltk_stopwords.words("english"))
except Exception:
    STOP_WORDS = set(_BUILTIN_STOPWORDS)

try:
    from nltk.stem import WordNetLemmatizer
    LEMMATIZER = WordNetLemmatizer()
    _HAS_LEMMATIZER = True
except Exception:
    _HAS_LEMMATIZER = False

try:
    from nltk.tokenize import word_tokenize
    _test = word_tokenize("test")
    _HAS_TOKENIZER = True
except Exception:
    _HAS_TOKENIZER = False

# Extra domain-specific stop words that add no signal
EXTRA_STOPWORDS = {
    "experience", "work", "working", "job", "position", "role",
    "year", "years", "month", "months", "strong", "good", "excellent",
    "ability", "knowledge", "understanding", "familiar", "familiarity",
    "proficient", "proficiency", "skill", "skills", "using", "use",
    "used", "including", "include", "etc", "well", "also", "must",
    "will", "would", "like", "preferred", "plus", "bonus", "require",
    "required", "requirement", "responsibilities", "responsibility",
    "candidate", "looking", "seeking", "apply", "application",
    "resume", "cv", "company", "team", "join", "opportunity"
}
STOP_WORDS.update(EXTRA_STOPWORDS)


def clean_text(text: str) -> str:
    """
    Basic text cleaning:
      - lowercase
      - remove emails, URLs, phone numbers
      - remove punctuation (except hyphens/dots in skill names like 'node.js')
      - collapse whitespace

    Args:
        text: Raw input string

    Returns:
        Cleaned string
    """
    text = text.lower()

    # Remove emails
    text = re.sub(r'\S+@\S+', ' ', text)
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    # Remove phone numbers
    text = re.sub(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', ' ', text)

    # Replace common separators with space (but keep . and - for skill names)
    text = re.sub(r'[|•►▶\*#@$%^&=+~`<>{}\\[\]\"\']+', ' ', text)

    # Collapse multiple whitespace
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def tokenize(text: str) -> list[str]:
    """
    Tokenize cleaned text into individual word tokens.
    Uses NLTK word_tokenize if available, else simple split.
    """
    if _HAS_TOKENIZER:
        from nltk.tokenize import word_tokenize
        tokens = word_tokenize(text)
    else:
        tokens = text.split()

    tokens = [
        t for t in tokens
        if re.match(r'^[a-z][a-z0-9.\-\+#]*$', t) and len(t) > 1
    ]
    return tokens


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Remove stopwords from token list."""
    return [t for t in tokens if t not in STOP_WORDS]


def lemmatize(tokens: list[str]) -> list[str]:
    """Apply WordNet lemmatization, or return tokens unchanged if unavailable."""
    if not _HAS_LEMMATIZER:
        return tokens
    result = []
    for t in tokens:
        try:
            result.append(LEMMATIZER.lemmatize(t))
        except Exception:
            result.append(t)
    return result


def preprocess(text: str) -> dict:
    """
    Full preprocessing pipeline.

    Args:
        text: Raw text (resume or JD)

    Returns:
        dict with keys:
          - 'cleaned': cleaned raw string
          - 'tokens': tokenized list
          - 'filtered': stopwords removed
          - 'lemmatized': final lemmatized list
          - 'joined': space-joined string of lemmatized tokens (for embeddings)
    """
    cleaned = clean_text(text)
    tokens = tokenize(cleaned)
    filtered = remove_stopwords(tokens)
    lemmatized = lemmatize(filtered)

    return {
        "cleaned": cleaned,
        "tokens": tokens,
        "filtered": filtered,
        "lemmatized": lemmatized,
        "joined": " ".join(lemmatized),
    }


def extract_sections(text: str) -> dict:
    """
    Heuristically split resume/JD into named sections.
    Looks for common section headers.

    Args:
        text: Raw text

    Returns:
        dict mapping section name → section text
    """
    section_headers = [
        "summary", "objective", "profile",
        "education", "academic",
        "experience", "employment", "work history",
        "skills", "technical skills", "core skills",
        "projects", "portfolio",
        "certifications", "certificates", "awards",
        "languages", "interests", "hobbies",
        "requirements", "responsibilities", "qualifications",
    ]

    pattern = r'(?i)\n\s*(' + '|'.join(section_headers) + r')[s]?\s*[\n:—\-_]+\s*'
    parts = re.split(pattern, text)

    sections = {}
    i = 0
    while i < len(parts):
        chunk = parts[i].strip()
        if any(h in chunk.lower() for h in section_headers) and i + 1 < len(parts):
            sections[chunk.lower()] = parts[i + 1].strip()
            i += 2
        else:
            i += 1

    return sections
