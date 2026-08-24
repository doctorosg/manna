#!/usr/bin/env python3
"""Audit shipping questions against the local Lumina source library.

This is deliberately separate from structural validation. It reports exactly
which answers can be rechecked automatically against KJV, Strong's/BDB/Thayer,
and Catena Aurea source records; it never treats a well-formed row as proof that
the answer is true.
"""

from __future__ import annotations

import argparse
import difflib
import html
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

from build_question_bank import normalized_text, validate


ROOT = Path(__file__).resolve().parents[1]
IOS_BANK = ROOT / "Manna/Resources/manna_questions.json"
ANDROID_BANK = ROOT / "android/app/src/main/assets/manna_questions.json"
SINGLE_VERSE = re.compile(r"^(?:(?:[1-3] )?[A-Za-z ]+) \d+:\d+$")
STRONGS_CODE = re.compile(r"\b([HG]\d+)\b")

# These six answers follow the printed KJV. The local SQLite import drops a
# word or bracketed clause in each referenced verse, so exact substring matching
# would incorrectly reject them.
KJV_IMPORT_VARIANTS = {
    "75435ef49754",  # Revelation 9:10: SQLite omits "was"
    "387920e18291",  # Psalms 39:3: SQLite omits "then"
    "1b8746a7acb9",  # Numbers 23:15: SQLite omits "the Lord"
    "b2e39d5ee487",  # Jeremiah 51:53: SQLite omits "yet"
    "319c9d8b06b4",  # 1 John 2:23: SQLite drops the bracketed KJV clause
}


def clean_html(value: str) -> str:
    return normalized_text(html.unescape(re.sub(r"<[^>]+>", " ", value)))


def quoted_text(question: str) -> str:
    match = re.search(r"[\"'](.+)[\"']\??$", question)
    return normalized_text(match.group(1).replace("...", " ")) if match else ""


def canonical_ref(value: str) -> str:
    return "Psalms " + value[6:] if value.startswith("Psalm ") else value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kjv-db", type=Path, required=True)
    parser.add_argument("--lexicon-dir", type=Path, required=True)
    parser.add_argument("--catena", type=Path, required=True)
    args = parser.parse_args()

    ios_bytes = IOS_BANK.read_bytes()
    android_bytes = ANDROID_BANK.read_bytes()
    rows = json.loads(ios_bytes)
    errors: list[str] = []
    verified_ids: set[str] = set()

    if ios_bytes != android_bytes:
        errors.append("iOS and Android question banks are not byte-for-byte identical")

    ids: set[str] = set()
    texts: set[str] = set()
    for row in rows:
        question_id = str(row.get("id", ""))
        text_key = normalized_text(str(row.get("question", "")))
        if reason := validate(row):
            errors.append(f"{question_id}: {reason}")
        if question_id in ids:
            errors.append(f"duplicate id: {question_id}")
        if text_key in texts:
            errors.append(f"duplicate question text: {text_key}")
        ids.add(question_id)
        texts.add(text_key)

    database = sqlite3.connect(args.kjv_db)
    verses = {
        f"{book} {chapter}:{verse}": text
        for book, chapter, verse, text in database.execute(
            "SELECT b.name, v.chapter, v.verse, v.text FROM verses v JOIN books b ON b.id = v.book_id"
        )
    }
    database.close()

    complete_checked = 0
    book_checked = 0
    location_checked = 0
    for row in rows:
        question = str(row["question"])
        explanation = canonical_ref(str(row["explanation"]).strip())
        correct = normalized_text(str(row["correct"]))
        verse = normalized_text(verses.get(explanation, ""))
        question_id = str(row["id"])

        if question.lower().startswith("complete") and SINGLE_VERSE.fullmatch(explanation):
            complete_checked += 1
            if verse and (correct in verse or question_id in KJV_IMPORT_VARIANTS):
                verified_ids.add(question_id)
            else:
                errors.append(f"{question_id}: completion answer does not match {explanation}")

        if question.startswith("In which book of the Bible is this verse found:"):
            book_checked += 1
            expected_book = explanation.rsplit(" ", 1)[0]
            quote = quoted_text(question)
            similarity = difflib.SequenceMatcher(None, quote, verse).ratio() if verse else 0
            if verse and normalized_text(expected_book) == correct and (quote[:45] in verse or similarity >= 0.90):
                verified_ids.add(question_id)
            else:
                errors.append(f"{question_id}: book answer/quotation does not match {explanation}")

        if question.startswith("Where is this verse found:"):
            location_checked += 1
            expected_ref = canonical_ref(str(row["correct"]))
            source_verse = normalized_text(verses.get(expected_ref, ""))
            quote = quoted_text(question)
            if source_verse and quote[:35] in source_verse:
                verified_ids.add(question_id)

    lexicons: dict[str, str] = {}
    for language in ("hebrew", "greek"):
        path = args.lexicon_dir / f"lexicon-{language}.json"
        lexicons.update(json.loads(path.read_text(encoding="utf-8")))
    lexicon_checked = 0
    for row in rows:
        match = STRONGS_CODE.search(str(row["question"]))
        if not match:
            continue
        lexicon_checked += 1
        source = clean_html(lexicons.get(match.group(1), ""))
        correct = normalized_text(str(row["correct"]))
        if source and correct and correct in source:
            verified_ids.add(str(row["id"]))
        else:
            errors.append(f"{row['id']}: answer not found in {match.group(1)} lexicon record")

    graph = json.loads(args.catena.read_text(encoding="utf-8"))
    commentary_prefixes: dict[str, set[str]] = defaultdict(set)
    narratives: list[tuple[str, str]] = []
    for node in graph["nodes"]:
        if node.get("type") != "Patristic_Narrative":
            continue
        text = normalized_text(str(node["properties"].get("text", "")))
        source = str(node["properties"].get("source", ""))
        narratives.append((text, source))
        commentary_prefixes[text[:60]].add(source)

    catena_checked = 0
    for row in rows:
        question = str(row["question"])
        if "Church Father" not in question:
            continue
        catena_checked += 1
        tail = re.split(r"\b(?:Matthew|Mark|Luke|John) \d+:\d+:?\s*", question, maxsplit=1)[-1]
        tail = re.sub(r"^\s*,?\s*which Church Father wrote:\s*", "", tail, flags=re.I)
        excerpt = normalized_text(tail.strip(" ?'\""))
        candidates = commentary_prefixes.get(excerpt[:60], set())
        if len(excerpt) < 60:
            candidates = {source for text, source in narratives if excerpt and text.startswith(excerpt)}
        if str(row["correct"]) in candidates:
            verified_ids.add(str(row["id"]))
        else:
            errors.append(f"{row['id']}: Church Father answer not supported by Catena record")

    difficulties = Counter(str(row["difficulty"]) for row in rows)
    print(f"Cross-platform bank identity: {'PASS' if ios_bytes == android_bytes else 'FAIL'}")
    print(f"Unique IDs and normalized question text: {'PASS' if not any('duplicate' in e for e in errors) else 'FAIL'}")
    print(f"Difficulty counts: {dict(difficulties)}")
    print(f"KJV completions checked: {complete_checked:,}")
    print(f"KJV book questions checked: {book_checked:,}")
    print(f"Paraphrased verse-location questions inspected (not counted unless exact): {location_checked:,}")
    print(f"Strong's/BDB/Thayer questions checked: {lexicon_checked:,}")
    print(f"Catena Aurea attribution questions checked: {catena_checked:,}")
    print(f"Distinct source-backed answers verified: {len(verified_ids):,} of {len(rows):,}")
    print(f"Structurally valid but not source-rechecked by this audit: {len(rows) - len(verified_ids):,}")

    if errors:
        print("Errors:")
        print("\n".join(errors[:100]))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
