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


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCES = (
    ROOT / "manna_questions.json",
    ROOT / "manna_questions_v2.json",
    ROOT / "manna_questions_v3.json",
    ROOT / "manna_questions_v4.json",
)
NUMBER_REGISTRY = ROOT / "question_number_registry.json"
VALID_DIFFICULTIES = {"Layperson", "Deacon", "Pastor"}
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
    if not isinstance(question["options"], list) or not 2 <= len(question["options"]) <= 4:
        return "invalid option count"
    normalized_options = [normalized_text(str(value)) for value in question["options"]]
    if len(set(normalized_options)) != len(normalized_options):
        return "duplicate options"
    if question["correct"] not in question["options"]:
        return "answer not in options"
    if not normalized_text(str(question["question"])):
        return "empty question"
    return None


def build(sources: tuple[Path, ...]) -> tuple[list[dict], Counter]:
    accepted: list[dict] = []
    seen_ids: set[str] = set()
    seen_texts: set[str] = set()
    rejected: Counter = Counter()

    for source in sources:
        rows = json.loads(source.read_text(encoding="utf-8"))
        for question in rows:
            question = dict(question)
            question["difficulty"] = calibrated_difficulty(question)
            reason = validate(question)
            question_id = str(question.get("id", ""))
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
    permanent_registry = dict(sorted(registry.items(), key=lambda item: item[1]))
    NUMBER_REGISTRY.write_text(json.dumps(permanent_registry, indent=2) + "\n", encoding="utf-8")
    return accepted, rejected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "Manna/Resources/manna_questions.json")
    parser.add_argument("--android-output", type=Path, default=ROOT / "android/app/src/main/assets/manna_questions.json")
    parser.add_argument("sources", nargs="*", type=Path, default=list(DEFAULT_SOURCES))
    args = parser.parse_args()
    questions, rejected = build(tuple(args.sources))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(questions, ensure_ascii=False, indent=2) + "\n"
    args.output.write_text(encoded, encoding="utf-8")
    args.android_output.parent.mkdir(parents=True, exist_ok=True)
    args.android_output.write_text(encoded, encoding="utf-8")
    counts = Counter(q["difficulty"] for q in questions)
    print(f"Wrote {len(questions):,} unique validated questions to {args.output}")
    print(f"Mirrored the validated bank to {args.android_output}")
    print("Difficulty counts:", dict(counts))
    print("Rejected:", dict(rejected))


if __name__ == "__main__":
    main()
