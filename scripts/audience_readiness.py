#!/usr/bin/env python3
"""Deterministic readiness rubric for the 11-17/Layperson boundary.

Higher scores indicate that a question asks for more independent Bible-study
skill and is therefore a better fit for the adult Layperson pool.  The rubric
is deliberately separate from the adult Layperson/Deacon/Pastor allocator:
age readiness and adult subject difficulty are related, but not identical.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from statistics import mean

from difficulty_assessment import FAMILIAR_STORY_RE, assess, question_family


RUBRIC_VERSION = "audience-readiness-v1"
COHORT_ORDER = {"11-17": 0, "Layperson": 1}
COMPONENT_MAXIMA = {
    "canonical_knowledge": 30,
    "task_abstraction": 25,
    "reading_burden": 20,
    "answer_specificity": 15,
    "distractor_competitiveness": 10,
}
TASK_ABSTRACTION = {
    "word-recognition": 2,
    "story-context": 8,
    "teen-trivia": 10,
    "adult-standard": 10,
    "missing-word": 20,
    "section-context": 18,
    "book-context": 24,
}


@dataclass(frozen=True)
class AudienceReadinessAssessment:
    score: int
    adult_content_score: int
    format: str
    family: str
    canonical_knowledge: int
    task_abstraction: int
    reading_burden: int
    answer_specificity: int
    distractor_competitiveness: int
    reasons: tuple[str, ...]


def normalized_answer(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def question_format(question: dict) -> str:
    return str(question.get("format") or "adult-standard")


def assess_readiness(
    question: dict,
    answer_frequency: int = 1,
) -> AudienceReadinessAssessment:
    """Score one boundary question without using its assigned audience label."""
    prompt = str(question.get("question", ""))
    answer = str(question.get("correct", ""))
    format_name = question_format(question)
    adult = assess(question)
    reasons: list[str] = []

    canonical = min(COMPONENT_MAXIMA["canonical_knowledge"], adult.recall_obscurity)
    if format_name == "word-recognition":
        canonical = min(canonical, 10)
        reasons.append("answer is recoverable from the displayed sentence")
    elif format_name == "story-context":
        canonical = min(canonical, 12)
        reasons.append("familiar story context supplies a strong cue")
    if (
        FAMILIAR_STORY_RE.search(prompt)
        and format_name in {"adult-standard", "story-context", "teen-trivia"}
    ):
        canonical = max(0, canonical - 4)
        reasons.append("widely familiar story cue")
    if canonical >= 20:
        reasons.append("less-familiar canonical setting")

    task = TASK_ABSTRACTION.get(format_name, TASK_ABSTRACTION["adult-standard"])
    if format_name == "book-context":
        reasons.append("must infer a Bible book from an unattributed passage")
    elif format_name == "section-context":
        reasons.append("must classify an unattributed passage by canon section")
    elif format_name == "missing-word":
        reasons.append("must retrieve an exact omitted word")
    elif task <= 10:
        reasons.append("one-step recognition or direct recall")

    words = re.findall(r"[A-Za-z]+", prompt)
    average_word_length = mean(map(len, words)) if words else 0.0
    word_count = len(words)
    if word_count <= 12:
        reading = 2
    elif word_count <= 20:
        reading = 5
    elif word_count <= 28:
        reading = 9
    elif word_count <= 36:
        reading = 13
    else:
        reading = 17
    if average_word_length >= 5.2:
        reading += 2
    if average_word_length >= 6.0:
        reading += 1
    if "…" in prompt or "..." in prompt:
        reading += 2
    reading = min(COMPONENT_MAXIMA["reading_burden"], reading)
    if reading >= 13:
        reasons.append("long or linguistically dense prompt")

    specificity = round(adult.specificity * 0.5)
    if answer_frequency <= 2 and len(answer) > 4:
        specificity += 3
        reasons.append("rare answer within the boundary pool")
    specificity = min(COMPONENT_MAXIMA["answer_specificity"], specificity)
    if format_name == "word-recognition":
        specificity = min(5, specificity)

    distractors = min(
        COMPONENT_MAXIMA["distractor_competitiveness"],
        round(adult.distractor_competitiveness * 2 / 3),
    )
    if distractors >= 8:
        reasons.append("closely shaped answer choices")

    score = canonical + task + reading + specificity + distractors
    if score > 100:
        raise AssertionError(f"Audience-readiness component overflow: {score}")
    return AudienceReadinessAssessment(
        score=score,
        adult_content_score=adult.score,
        format=format_name,
        family=question_family(question),
        canonical_knowledge=canonical,
        task_abstraction=task,
        reading_burden=reading,
        answer_specificity=specificity,
        distractor_competitiveness=distractors,
        reasons=tuple(reasons),
    )
