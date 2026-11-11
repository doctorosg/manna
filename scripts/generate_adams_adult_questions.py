#!/usr/bin/env python3
"""Generate original adult trivia inspired by Adams's Bible study guide."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from adams_adult_facts import ADAMS_ADULT_FACTS, SOURCE_GUIDE_URL
from gen_v4_underrepresented import DEFAULT_KJV, parse_kjv


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "adams_adult_questions.json"


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def stable_number(value: str) -> int:
    return int.from_bytes(hashlib.sha256(value.encode("utf-8")).digest()[:8], "big")


def passage_text(reference: str, verses: dict[str, tuple[str, str]]) -> str:
    match = re.fullmatch(r"(.+?) (\d+):(\d+)(?:-(\d+))?", reference)
    if match is None:
        raise RuntimeError(f"Unsupported reference: {reference}")
    book, chapter = match.group(1), int(match.group(2))
    first, last = int(match.group(3)), int(match.group(4) or match.group(3))
    passage = " ".join(
        verses[f"{book} {chapter}:{verse}"][1]
        for verse in range(first, last + 1)
        if f"{book} {chapter}:{verse}" in verses
    )
    if not passage:
        raise RuntimeError(f"KJV passage not found: {reference}")
    return passage


def generate(verses: dict[str, tuple[str, str]]) -> list[dict]:
    rows: list[dict] = []
    seen_questions: set[str] = set()
    for index, (difficulty, category, reference, question, correct, distractors, evidence) in enumerate(ADAMS_ADULT_FACTS):
        if difficulty not in {"Deacon", "Pastor"}:
            raise RuntimeError(f"Wrong adult difficulty for {question}")
        if len(set(distractors)) != 3 or correct in distractors:
            raise RuntimeError(f"Invalid choices for {question}")
        source = normalized(passage_text(reference, verses))
        for fragment in evidence:
            if normalized(fragment) not in source:
                raise RuntimeError(f"Evidence {fragment!r} not found in {reference}")
        question_key = normalized(question)
        if question_key in seen_questions:
            raise RuntimeError(f"Duplicate curated question: {question}")
        seen_questions.add(question_key)
        salt = f"adams-guide-v1|{index}|{reference}|{correct}"
        options = sorted(
            [correct, *distractors],
            key=lambda value: stable_number(f"{salt}|position|{value}"),
        )
        identifier = hashlib.sha256(f"{salt}|{question}".encode("utf-8")).hexdigest()[:18]
        rows.append({
            "id": f"adams-guide-v1-{identifier}",
            "category": category,
            "difficulty": difficulty,
            "question": question,
            "options": options,
            "correct": correct,
            "explanation": f"{reference} (KJV).",
            "sourceGuide": SOURCE_GUIDE_URL,
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kjv", type=Path, default=DEFAULT_KJV)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    rows = generate(parse_kjv(args.kjv))
    args.output.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} Adams-guided adult questions to {args.output}")
    print("Difficulty counts:", dict(Counter(row["difficulty"] for row in rows)))


if __name__ == "__main__":
    main()
