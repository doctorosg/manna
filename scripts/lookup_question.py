#!/usr/bin/env python3
"""Look up the exact shipping question and answer by its permanent support number."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "Manna/Resources/manna_questions.json"


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Usage: python3 scripts/lookup_question.py QUESTION_NUMBER", file=sys.stderr)
        return 2
    requested = int(sys.argv[1])
    for question in json.loads(BANK.read_text(encoding="utf-8")):
        if question.get("number") == requested:
            print(f"Question #{requested}")
            print(f"ID: {question['id']}")
            print(f"Category: {question['category']}")
            print(f"Difficulty: {question['difficulty']}")
            print(f"Question: {question['question']}")
            for index, option in enumerate(question["options"]):
                print(f"  {chr(65 + index)}. {option}")
            print(f"Correct answer: {question['correct']}")
            print(f"Explanation/source: {question['explanation']}")
            return 0
    print(f"Question #{requested} was not found.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
