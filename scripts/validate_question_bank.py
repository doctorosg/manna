#!/usr/bin/env python3
"""Fail CI when the shipping Manna question bank violates its invariants."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from build_question_bank import (
    AUDIENCE_OVERRIDES,
    DIFFICULTY_OVERRIDES,
    load_audience_overrides,
    load_difficulty_overrides,
    normalized_text,
    validate,
)
from adams_adult_facts import ADAMS_ADULT_FACTS, SOURCE_GUIDE_URL
from generate_children_questions import (
    ARCHAIC_RE,
    GRAPHIC_RE,
    SEXUAL_RE,
    YOUNG_BLOCKED_RE,
)
ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "Manna/Resources/manna_questions.json"
ANDROID_PATH = ROOT / "android/app/src/main/assets/manna_questions.json"
REGISTRY_PATH = ROOT / "question_number_registry.json"
RETIRED_CHILDREN_PATH = ROOT / "archive/questions/children_questions_legacy_kjv_template_2026-09-01.json"
EXPECTED_QUESTION_COUNT = 50_020
EXPECTED_AUDIENCE_COUNTS = {"adult": 40_020, "4-10": 3_333, "11-17": 6_667}
CHILDREN_SOURCE_PATH = ROOT / "children_questions.json"


def expected_child_format_counts(audience_overrides: dict[str, dict]) -> Counter:
    children = json.loads(CHILDREN_SOURCE_PATH.read_text(encoding="utf-8"))
    result = Counter(
        (str(question["ageGroup"]), str(question["format"]))
        for question in children
    )
    for override in audience_overrides.values():
        if override["from"] == "11-17":
            result[("11-17", str(override["sourceFormat"]))] -= 1
        else:
            result[("11-17", str(override["targetFormat"]))] += 1
    return Counter({key: count for key, count in result.items() if count})


def main() -> int:
    rows = json.loads(PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if len(rows) != EXPECTED_QUESTION_COUNT:
        errors.append(f"expected {EXPECTED_QUESTION_COUNT:,} shipping questions, found {len(rows):,}")
    if not ANDROID_PATH.exists():
        errors.append("Android question bank is missing")
    elif PATH.read_bytes() != ANDROID_PATH.read_bytes():
        errors.append("iOS and Android question banks are not byte-identical")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8")) if REGISTRY_PATH.exists() else {}
    ids = Counter(str(q.get("id", "")) for q in rows)
    numbers = Counter(q.get("number") for q in rows)
    texts = Counter(normalized_text(str(q.get("question", ""))) for q in rows)
    audiences = Counter(q.get("ageGroup", "adult") for q in rows)
    audience_overrides = load_audience_overrides(AUDIENCE_OVERRIDES)
    expected_child_formats = expected_child_format_counts(audience_overrides)
    child_formats = Counter(
        (str(q.get("ageGroup")), str(q.get("format")))
        for q in rows if q.get("ageGroup") is not None
    )
    if dict(audiences) != EXPECTED_AUDIENCE_COUNTS:
        errors.append(f"expected audience counts {EXPECTED_AUDIENCE_COUNTS}, found {dict(audiences)}")
    if child_formats != expected_child_formats:
        errors.append(
            f"expected child format counts {dict(expected_child_formats)}, "
            f"found {dict(child_formats)}"
        )
    curated = [question for question in rows if str(question.get("id", "")).startswith("adams-guide-v1-")]
    if len(curated) != len(ADAMS_ADULT_FACTS):
        errors.append(f"expected {len(ADAMS_ADULT_FACTS)} Adams-guided questions, found {len(curated)}")
    if any(question.get("sourceGuide") != SOURCE_GUIDE_URL for question in curated):
        errors.append("Adams-guided question is missing source provenance")
    overrides = load_difficulty_overrides(DIFFICULTY_OVERRIDES)
    questions_by_id = {str(question.get("id", "")): question for question in rows}
    for question_id, override in overrides.items():
        question = questions_by_id.get(question_id)
        if question is None:
            errors.append(f"difficulty override question is missing: {question_id}")
        elif (
            question_id not in audience_overrides
            or audience_overrides[question_id]["to"] != "11-17"
        ) and question.get("difficulty") != override["to"]:
            errors.append(
                f"difficulty override not applied for {question_id}: expected "
                f"{override['to']}, found {question.get('difficulty')}"
            )
    for question_id, override in audience_overrides.items():
        question = questions_by_id.get(question_id)
        if question is None:
            errors.append(f"audience override question is missing: {question_id}")
            continue
        if override["to"] == "11-17":
            if question.get("ageGroup") != "11-17":
                errors.append(f"audience override not applied for {question_id}: expected 11-17")
            if question.get("difficulty") != "Pastor":
                errors.append(f"reallocated teen question has wrong difficulty: {question_id}")
            if question.get("format") != override.get("targetFormat"):
                errors.append(f"reallocated teen question has wrong format: {question_id}")
        else:
            if question.get("ageGroup") is not None:
                errors.append(f"audience override not applied for {question_id}: expected adult")
            if question.get("difficulty") != "Layperson":
                errors.append(f"reallocated Layperson question has wrong difficulty: {question_id}")
    for index, question in enumerate(rows):
        if reason := validate(question):
            errors.append(f"row {index} ({question.get('id', '?')}): {reason}")
        if registry.get(str(question.get("id", ""))) != question.get("number"):
            errors.append(f"row {index} ({question.get('id', '?')}): permanent number differs from registry")
        if question.get("ageGroup") is not None:
            question_id = str(question.get("id", ""))
            combined = f"{question.get('question', '')} {question.get('explanation', '')}"
            audience_override = audience_overrides.get(question_id)
            if not (
                audience_override
                and audience_override["from"] == "Layperson"
                and audience_override["to"] == "11-17"
            ):
                expected_prefix = (
                    "child-v4-"
                    if question.get("format") == "story-quiz" or question.get("generation") == "promoted-middle-v4"
                    else "child-v3-" if question.get("format") == "teen-trivia"
                    else "child-v2-"
                )
                if not question_id.startswith(expected_prefix):
                    errors.append(f"row {index} ({question_id}): active child question is not from rebuilt bank")
            if ARCHAIC_RE.search(combined) or SEXUAL_RE.search(combined) or GRAPHIC_RE.search(combined):
                errors.append(f"row {index} ({question_id}): child age-screening violation")
            if question.get("ageGroup") == "4-10" and YOUNG_BLOCKED_RE.search(combined):
                errors.append(f"row {index} ({question_id}): ages 4-10 safety violation")
    errors.extend(f"duplicate id: {key}" for key, count in ids.items() if count > 1)
    errors.extend(f"duplicate question number: {key}" for key, count in numbers.items() if count > 1)
    errors.extend(f"invalid question number at row {index}" for index, q in enumerate(rows) if not isinstance(q.get("number"), int) or q["number"] < 1)
    errors.extend(f"duplicate text: {key}" for key, count in texts.items() if count > 1)
    adult_pool_counts = Counter(
        (str(question["category"]), str(question["difficulty"]))
        for question in rows if question.get("ageGroup") is None
    )
    for category in {str(question["category"]) for question in rows}:
        for difficulty in ("Layperson", "Deacon", "Pastor"):
            if adult_pool_counts[category, difficulty] < 20:
                errors.append(
                    f"adult gameplay pool below 20 for {category}/{difficulty}: "
                    f"{adult_pool_counts[category, difficulty]}"
                )
    if not RETIRED_CHILDREN_PATH.exists():
        errors.append("retired children question archive is missing")
    else:
        retired = json.loads(RETIRED_CHILDREN_PATH.read_text(encoding="utf-8"))
        retired_ids = {str(question.get("id", "")) for question in retired}
        active_ids = set(ids)
        if len(retired) != 10_000 or len(retired_ids) != 10_000:
            errors.append("retired children archive must contain 10,000 unique IDs")
        if overlap := retired_ids & active_ids:
            errors.append(f"retired child ID is active: {next(iter(overlap))}")
        missing_reserved = retired_ids - set(registry)
        if missing_reserved:
            errors.append(f"retired child ID lost from permanent registry: {next(iter(missing_reserved))}")
    if errors:
        print("\n".join(errors[:100]), file=sys.stderr)
        return 1
    difficulties = Counter(q["difficulty"] for q in rows)
    categories = Counter(q["category"] for q in rows)
    print(
        f"Validated {len(rows):,} uniquely numbered questions, {len(categories)} categories: "
        f"{dict(difficulties)}; audiences: {dict(audiences)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
