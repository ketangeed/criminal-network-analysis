"""
entity_extractor.py
=========================================================
Lightweight regex-based entity extraction for the
Text Extraction panel on the Entity Intelligence page.

This is intentionally simple for the prototype stage:
- PHONE     : Indian mobile numbers (with/without +91, spaces, hyphens)
- EMAIL     : standard email addresses
- VEHICLE   : Indian vehicle registration plates (e.g. MH12AB1234)

extract_entities() always returns a dict with all three keys
present (each a list, possibly empty) so callers in app.py can
safely do extracted["PHONE"], len(extracted["EMAIL"]), etc.
without KeyErrors.
=========================================================
"""

import re

PHONE_PATTERN = re.compile(
    r"(?:\+91[\s-]?)?[6-9]\d{9}"
)

EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)

# Indian plate format: 2 letters, 1-2 digits, 1-3 letters, 4 digits
# Accepts optional spaces/hyphens between groups, e.g.
# "MH12AB1234", "MH-12-AB-4582", "MH 12 AB 4582"
VEHICLE_PATTERN = re.compile(
    r"\b[A-Za-z]{2}[\s-]?\d{1,2}[\s-]?[A-Za-z]{1,3}[\s-]?\d{4}\b"
)


def _clean(matches: list[str]) -> list[str]:
    """De-duplicate matches while preserving first-seen order."""
    seen = set()
    cleaned = []
    for m in matches:
        normalized = m.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            cleaned.append(normalized)
    return cleaned


def extract_entities(text: str) -> dict:
    """
    Extract PHONE, EMAIL, and VEHICLE entities from free text.

    Returns:
        {
            "PHONE":   [str, ...],
            "EMAIL":   [str, ...],
            "VEHICLE": [str, ...],
        }
    """
    if not text or not text.strip():
        return {"PHONE": [], "EMAIL": [], "VEHICLE": []}

    phones = _clean(PHONE_PATTERN.findall(text))
    emails = _clean(EMAIL_PATTERN.findall(text))

    # Emails can contain digit-letter sequences that look like plates
    # (e.g. "john123@example.com") — strip anything that overlaps an
    # already-matched email span before searching for vehicle plates.
    vehicle_search_text = text
    for email in emails:
        vehicle_search_text = vehicle_search_text.replace(email, " ")

    vehicles = _clean(VEHICLE_PATTERN.findall(vehicle_search_text))

    return {
        "PHONE": phones,
        "EMAIL": emails,
        "VEHICLE": vehicles,
    }