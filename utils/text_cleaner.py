# Regex-based utilities for extracting and stripping contact information

import re
from dataclasses import dataclass, field


@dataclass
class ContactInfo:
    """Holds extracted contact details from resume."""
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""


#Regex Patterns 

EMAIL_PATTERN = re.compile(
    r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
    re.IGNORECASE
)

PHONE_PATTERN = re.compile(
    r'(?:\+?\d{1,3}[\s\-.]?)?(?:\(?\d{1,4}\)?[\s\-.]?)?\d{3,4}[\s\-.]?\d{3,4}[\s\-.]?\d{0,4}',
    re.IGNORECASE
)

URL_PATTERN = re.compile(
    r'https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+',
    re.IGNORECASE
)

LINKEDIN_PATTERN = re.compile(
    r'linkedin\.com/in/[\w\-]+',
    re.IGNORECASE
)

GITHUB_PATTERN = re.compile(
    r'github\.com/[\w\-]+',
    re.IGNORECASE
)


#Extraction Functions

def extract_contact_info(text: str) -> ContactInfo:
    """
    Extract all contact information from resume text.

    Args:
        text: Raw resume text

    Returns:
        ContactInfo dataclass with filled fields
    """
    info = ContactInfo()

    # Emails
    info.emails = list(set(EMAIL_PATTERN.findall(text)))

    # Phones (basic — remove very short matches)
    phones = PHONE_PATTERN.findall(text)
    info.phones = [p.strip() for p in phones if len(re.sub(r'\D', '', p)) >= 7]

    # URLs
    info.urls = list(set(URL_PATTERN.findall(text)))

    # LinkedIn
    linkedin_match = LINKEDIN_PATTERN.search(text)
    if linkedin_match:
        info.linkedin = linkedin_match.group(0)

    # GitHub
    github_match = GITHUB_PATTERN.search(text)
    if github_match:
        info.github = github_match.group(0)

    # Portfolio: any URL that's not linkedin/github
    for url in info.urls:
        if "linkedin" not in url.lower() and "github" not in url.lower():
            info.portfolio = url
            break

    return info


def strip_contact_info(text: str) -> str:
    """
    Remove emails, phone numbers, and URLs from text.
    Useful for cleaning text before NLP processing.

    Args:
        text: Raw text

    Returns:
        Text with contact info removed
    """
    text = EMAIL_PATTERN.sub(' ', text)
    text = URL_PATTERN.sub(' ', text)
    text = PHONE_PATTERN.sub(' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def normalize_whitespace(text: str) -> str:
    """Collapse multiple spaces/newlines into single spaces."""
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_name_heuristic(text: str) -> str:
    """
    Try to extract the candidate's name from the first 3 lines.
    Heuristic: First non-empty line that is NOT an email/phone/URL
    and is mostly alpha characters.

    Returns:
        Best guess at name, or empty string
    """
    lines = text.strip().split('\n')[:5]
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip lines with email/phone/URL signals
        if '@' in line or 'http' in line or re.search(r'\d{5,}', line):
            continue
        # Likely a name if it's 2–5 words, mostly alpha
        words = line.split()
        if 2 <= len(words) <= 5 and all(re.match(r'^[A-Za-z\.\-]+$', w) for w in words):
            return line
    return ""


def count_words(text: str) -> int:
    """Return word count of text."""
    return len(text.split())


def get_text_stats(text: str) -> dict:
    """
    Return basic statistics about the text.

    Returns:
        dict with word_count, char_count, line_count, sentence_count
    """
    return {
        "word_count": len(text.split()),
        "char_count": len(text),
        "line_count": len([l for l in text.split('\n') if l.strip()]),
        "sentence_count": len(re.split(r'[.!?]+', text)),
    }
