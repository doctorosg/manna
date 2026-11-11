#!/usr/bin/env python3
"""Classify Pastor questions for balanced gameplay sessions.

Difficulty and session burden are separate concerns. A question can remain
Pastor-level while the app limits how often one rote-recall format appears in
the same session.
"""

from __future__ import annotations

try:
    from difficulty_assessment import question_family
except ModuleNotFoundError:  # Imported as scripts.pastor_balance in unit tests.
    from scripts.difficulty_assessment import question_family


PASTOR_FORMATS = {
    "scriptureMemory",
    "originalLanguage",
    "churchFather",
    "interpretation",
    "other",
}

SCRIPTURE_MEMORY_FAMILIES = {
    "Exact completion",
    "Exact cross-reference",
    "Verse location/book",
}
INTERPRETATION_FAMILIES = {
    "Academic biblical studies",
    "Connection classification",
    "Doctrine or theological term",
    "Study terminology",
    "Symbolism or interpretation",
}


def pastor_format(question: dict) -> str:
    """Return the session-balancing format for one adult Pastor question."""
    family = question_family(question)
    if family in SCRIPTURE_MEMORY_FAMILIES:
        return "scriptureMemory"
    if family == "Original-language lexicon":
        return "originalLanguage"
    if family == "Church Father attribution":
        return "churchFather"
    if family in INTERPRETATION_FAMILIES:
        return "interpretation"
    return "other"
