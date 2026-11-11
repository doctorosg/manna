#!/usr/bin/env python3
"""Build the shipping Manna question bank from every repository source.

The output is deterministic. Questions are de-duplicated by normalized question
text (not merely by ID), and structurally unsafe rows are rejected.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from pastor_balance import PASTOR_FORMATS, pastor_format


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCES = (
    ROOT / "adams_adult_questions.json",
    ROOT / "manna_questions.json",
    ROOT / "manna_questions_v2.json",
    ROOT / "manna_questions_v3.json",
    ROOT / "manna_questions_v4.json",
    ROOT / "children_questions.json",
)
NUMBER_REGISTRY = ROOT / "question_number_registry.json"
DIFFICULTY_OVERRIDES = ROOT / "difficulty_overrides.json"
AUDIENCE_OVERRIDES = ROOT / "audience_overrides.json"
VALID_DIFFICULTIES = {"Layperson", "Deacon", "Pastor"}
VALID_AGE_GROUPS = {"4-10", "11-17"}
VALID_BOUNDARY_COHORTS = {"11-17", "Layperson"}
AGE_GROUP_OPTION_COUNTS = {"4-10": 3, "11-17": 4}
VALID_CATEGORIES = {
    "Genesis & Creation", "Moses & the Exodus", "Kings & Kingdoms", "Prophets",
    "Psalms & Proverbs", "Life of Jesus", "Miracles", "Parables", "The Apostles",
    "Paul & His Letters", "Revelation & End Times", "Women of the Bible",
    "Battles & Wars", "Angels & Demons", "Laws & Commandments",
    "Prophecy & Fulfillment", "Places & Lands", "Numbers & Genealogies",
    "Food, Feasts & Offerings", "Dreams & Visions", "Words of Jesus & OT Roots",
}
ORIGINAL_LANGUAGE_CODE = re.compile(r"\b[HG]\d+\b")


def calibrated_difficulty(question: dict) -> str:
    """Keep specialist source material out of the introductory levels."""
    text = str(question.get("question", ""))
    if ORIGINAL_LANGUAGE_CODE.search(text) or "Church Father" in text or "Catena Aurea" in text:
        return "Pastor"
    return str(question.get("difficulty", ""))


def load_difficulty_overrides(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("version") != 1 or not isinstance(payload.get("overrides"), list):
        raise RuntimeError(f"Invalid difficulty override manifest: {path}")
    result: dict[str, dict] = {}
    for index, override in enumerate(payload["overrides"]):
        if not isinstance(override, dict):
            raise RuntimeError(f"Difficulty override {index} is not an object")
        question_id = str(override.get("id", ""))
        before = override.get("from")
        after = override.get("to")
        if not question_id or before not in VALID_DIFFICULTIES or after not in VALID_DIFFICULTIES:
            raise RuntimeError(f"Invalid difficulty override at index {index}")
        if before == after:
            raise RuntimeError(f"No-op difficulty override for {question_id}")
        if question_id in result:
            raise RuntimeError(f"Duplicate difficulty override for {question_id}")
        result[question_id] = override
    return result


def load_audience_overrides(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("version") != 1 or not isinstance(payload.get("overrides"), list):
        raise RuntimeError(f"Invalid audience override manifest: {path}")
    result: dict[str, dict] = {}
    for index, override in enumerate(payload["overrides"]):
        if not isinstance(override, dict):
            raise RuntimeError(f"Audience override {index} is not an object")
        question_id = str(override.get("id", ""))
        before = override.get("from")
        after = override.get("to")
        if (
            not question_id
            or before not in VALID_BOUNDARY_COHORTS
            or after not in VALID_BOUNDARY_COHORTS
        ):
            raise RuntimeError(f"Invalid audience override at index {index}")
        if before == after:
            raise RuntimeError(f"No-op audience override for {question_id}")
        if before == "11-17" and not isinstance(override.get("sourceFormat"), str):
            raise RuntimeError(f"Missing source format for audience override {question_id}")
        if after == "11-17" and not isinstance(override.get("targetFormat"), str):
            raise RuntimeError(f"Missing target format for audience override {question_id}")
        if question_id in result:
            raise RuntimeError(f"Duplicate audience override for {question_id}")
        result[question_id] = override
    return result


def normalized_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def validate(question: dict) -> str | None:
    required = ("id", "category", "difficulty", "question", "options", "correct", "explanation")
    if any(key not in question for key in required):
        return "missing field"
    if question["category"] not in VALID_CATEGORIES:
        return "invalid category"
    if question["difficulty"] not in VALID_DIFFICULTIES:
        return "invalid difficulty"
    age_group = question.get("ageGroup")
    if age_group is not None and age_group not in VALID_AGE_GROUPS:
        return "invalid age group"
    if not isinstance(question["options"], list) or not 2 <= len(question["options"]) <= 4:
        return "invalid option count"
    if age_group is not None and len(question["options"]) != AGE_GROUP_OPTION_COUNTS[age_group]:
        return "wrong option count for age group"
    session_format = question.get("pastorFormat")
    if session_format is not None and session_format not in PASTOR_FORMATS:
        return "invalid pastor format"
    if session_format is not None and (
        age_group is not None or question["difficulty"] != "Pastor"
    ):
        return "pastor format on ineligible question"
    normalized_options = [normalized_text(str(value)) for value in question["options"]]
    if len(set(normalized_options)) != len(normalized_options):
        return "duplicate options"
    if question["correct"] not in question["options"]:
        return "answer not in options"
    if not normalized_text(str(question["question"])):
        return "empty question"
    return None


def build(
    sources: tuple[Path, ...],
    difficulty_overrides: dict[str, dict] | None = None,
    audience_overrides: dict[str, dict] | None = None,
    persist_registry: bool = True,
) -> tuple[list[dict], Counter]:
    accepted: list[dict] = []
    seen_ids: set[str] = set()
    seen_texts: set[str] = set()
    rejected: Counter = Counter()
    overrides = difficulty_overrides or {}
    boundary_overrides = audience_overrides or {}
    applied_overrides: set[str] = set()
    applied_boundary_overrides: set[str] = set()

    for source in sources:
        rows = json.loads(source.read_text(encoding="utf-8"))
        for question in rows:
            question = dict(question)
            question["difficulty"] = calibrated_difficulty(question)
            question_id = str(question.get("id", ""))
            override = overrides.get(question_id)
            if override is not None:
                if question.get("ageGroup") is not None:
                    raise RuntimeError(f"Adult difficulty override targets child question {question_id}")
                if question["difficulty"] != override["from"]:
                    raise RuntimeError(
                        f"Stale difficulty override for {question_id}: expected "
                        f"{override['from']}, found {question['difficulty']}"
                    )
                question["difficulty"] = override["to"]
                applied_overrides.add(question_id)
            audience_override = boundary_overrides.get(question_id)
            if audience_override is not None:
                current_cohort = (
                    "11-17"
                    if question.get("ageGroup") == "11-17"
                    else "Layperson"
                    if question.get("ageGroup") is None
                    and question.get("difficulty") == "Layperson"
                    else None
                )
                if current_cohort != audience_override["from"]:
                    raise RuntimeError(
                        f"Stale audience override for {question_id}: expected "
                        f"{audience_override['from']}, found {current_cohort or 'outside boundary'}"
                    )
                if (
                    current_cohort == "11-17"
                    and question.get("format") != audience_override.get("sourceFormat")
                ):
                    raise RuntimeError(
                        f"Stale audience format for {question_id}: expected "
                        f"{audience_override.get('sourceFormat')}, found {question.get('format')}"
                    )
                if audience_override["to"] == "Layperson":
                    question.pop("ageGroup", None)
                    question["difficulty"] = "Layperson"
                else:
                    question["ageGroup"] = "11-17"
                    question["difficulty"] = "Pastor"
                    question["format"] = str(
                        audience_override.get("targetFormat") or "reallocated-direct"
                    )
                applied_boundary_overrides.add(question_id)
            if question.get("ageGroup") is None and question["difficulty"] == "Pastor":
                question["pastorFormat"] = pastor_format(question)
            else:
                question.pop("pastorFormat", None)
            reason = validate(question)
            text_key = normalized_text(str(question.get("question", "")))
            if reason:
                rejected[reason] += 1
            elif question_id in seen_ids:
                rejected["duplicate id"] += 1
            elif text_key in seen_texts:
                rejected["duplicate text"] += 1
            else:
                accepted.append(question)
                seen_ids.add(question_id)
                seen_texts.add(text_key)
    unapplied_overrides = sorted(set(overrides) - applied_overrides)
    if unapplied_overrides:
        raise RuntimeError(
            f"Difficulty overrides do not match accepted source questions: {unapplied_overrides[:5]}"
        )
    unapplied_boundary_overrides = sorted(
        set(boundary_overrides) - applied_boundary_overrides
    )
    if unapplied_boundary_overrides:
        raise RuntimeError(
            "Audience overrides do not match accepted source questions: "
            f"{unapplied_boundary_overrides[:5]}"
        )
    registry: dict[str, int] = {}
    if NUMBER_REGISTRY.exists():
        registry = {str(key): int(value) for key, value in json.loads(NUMBER_REGISTRY.read_text(encoding="utf-8")).items()}
    next_number = max(registry.values(), default=0) + 1
    for question in accepted:
        question_id = str(question["id"])
        if question_id not in registry:
            registry[question_id] = next_number
            next_number += 1
        question["number"] = registry[question_id]
    if persist_registry:
        permanent_registry = dict(sorted(registry.items(), key=lambda item: item[1]))
        NUMBER_REGISTRY.write_text(
            json.dumps(permanent_registry, indent=2) + "\n", encoding="utf-8"
        )
    return accepted, rejected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "Manna/Resources/manna_questions.json")
    parser.add_argument("--android-output", type=Path, default=ROOT / "android/app/src/main/assets/manna_questions.json")
    parser.add_argument("--difficulty-overrides", type=Path, default=DIFFICULTY_OVERRIDES)
    parser.add_argument("--skip-difficulty-overrides", action="store_true")
    parser.add_argument("--audience-overrides", type=Path, default=AUDIENCE_OVERRIDES)
    parser.add_argument("--skip-audience-overrides", action="store_true")
    parser.add_argument("sources", nargs="*", type=Path, default=list(DEFAULT_SOURCES))
    args = parser.parse_args()
    overrides = (
        {} if args.skip_difficulty_overrides
        else load_difficulty_overrides(args.difficulty_overrides)
    )
    boundary_overrides = (
        {} if args.skip_audience_overrides
        else load_audience_overrides(args.audience_overrides)
    )
    questions, rejected = build(
        tuple(args.sources), overrides, boundary_overrides
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(questions, ensure_ascii=False, indent=2) + "\n"
    args.output.write_text(encoded, encoding="utf-8")
    args.android_output.parent.mkdir(parents=True, exist_ok=True)
    args.android_output.write_text(encoded, encoding="utf-8")
    counts = Counter(q["difficulty"] for q in questions)
    age_counts = Counter(q.get("ageGroup", "adult") for q in questions)
    print(f"Wrote {len(questions):,} unique validated questions to {args.output}")
    print(f"Mirrored the validated bank to {args.android_output}")
    print("Difficulty counts:", dict(counts))
    print("Audience counts:", dict(age_counts))
    print("Rejected:", dict(rejected))
    print(f"Difficulty overrides applied: {len(overrides):,}")
    print(f"Audience overrides applied: {len(boundary_overrides):,}")


if __name__ == "__main__":
    main()
