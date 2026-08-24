#!/usr/bin/env python3
"""Fail CI when the shipping Manna question bank violates its invariants."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from build_question_bank import normalized_text, validate


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "Manna/Resources/manna_questions.json"
ANDROID_PATH = ROOT / "android/app/src/main/assets/manna_questions.json"
REGISTRY_PATH = ROOT / "question_number_registry.json"
EXPECTED_QUESTION_COUNT = 40_000


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
    for index, question in enumerate(rows):
        if reason := validate(question):
            errors.append(f"row {index} ({question.get('id', '?')}): {reason}")
        if registry.get(str(question.get("id", ""))) != question.get("number"):
            errors.append(f"row {index} ({question.get('id', '?')}): permanent number differs from registry")
    errors.extend(f"duplicate id: {key}" for key, count in ids.items() if count > 1)
    errors.extend(f"duplicate question number: {key}" for key, count in numbers.items() if count > 1)
    errors.extend(f"invalid question number at row {index}" for index, q in enumerate(rows) if not isinstance(q.get("number"), int) or q["number"] < 1)
    errors.extend(f"duplicate text: {key}" for key, count in texts.items() if count > 1)
    if errors:
        print("\n".join(errors[:100]), file=sys.stderr)
        return 1
    difficulties = Counter(q["difficulty"] for q in rows)
    categories = Counter(q["category"] for q in rows)
    print(f"Validated {len(rows):,} uniquely numbered questions, {len(categories)} categories: {dict(difficulties)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
