#!/usr/bin/env python3
"""Generate source-backed questions for Manna's least-populated categories.

The generated questions are deterministic and cite an exact KJV verse.  The
correct option is a verbatim clause from that verse; distractors are clauses
from other verses in the same category and are checked not to occur in the
question's verse.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path

from kjv_parse import BOOKID


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KJV = Path(
    "/Users/silvanoguzzo/Documents/MY APPS/lumina/lumina-bible/"
    "data/kjv_strongs/eng-kjv2006_usfx.xml"
)
DEFAULT_PLACES = Path(
    "/Users/silvanoguzzo/Documents/MY APPS/lumina/lumina-bible/"
    "data/people_places/bible_places.json"
)
DEFAULT_PARABLES = Path(
    "/Users/silvanoguzzo/Documents/MY APPS/lumina/lumina-bible/"
    "data/parables/parables.json"
)
TARGETS = {
    "Dreams & Visions": 75,
    "Angels & Demons": 75,
    "Food, Feasts & Offerings": 75,
    "Miracles": 75,
    "Places & Lands": 70,
    "Women of the Bible": 70,
    "Revelation & End Times": 65,
    "Parables": 60,
}


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = value.replace("¶", " ")
    value = re.sub(r"\s+([,.;:!?])", r"\1", value)
    return re.sub(r"\s+", " ", value).strip()


def parse_kjv(path: Path) -> dict[str, tuple[str, str]]:
    raw = path.read_text(encoding="utf-8")
    raw = re.sub(r"<f\b.*?</f>", "", raw, flags=re.S)
    verses: dict[str, tuple[str, str]] = {}
    pattern = r'<v id="[^"]*" bcv="([^"]+)" />(.*?)(?=<v id=|<ve\s*/>|</p>)'
    for match in re.finditer(pattern, raw, flags=re.S):
        parts = match.group(1).split(".")
        if len(parts) != 3 or parts[0] not in BOOKID:
            continue
        book = BOOKID[parts[0]]
        ref = f"{book} {int(parts[1])}:{int(parts[2])}"
        text = clean_text(match.group(2))
        if text:
            verses[ref] = (book, text)
    return verses


def compile_words(words: list[str]) -> re.Pattern[str]:
    alternatives = sorted((re.escape(word) for word in words), key=len, reverse=True)
    return re.compile(r"(?<![A-Za-z])(?:" + "|".join(alternatives) + r")(?![A-Za-z])", re.I)


def parse_ref_part(value: str) -> tuple[str, int, int, int] | None:
    match = re.fullmatch(r"(.+?)\s+(\d+):(\d+)(?:-(\d+))?", value.strip())
    if not match:
        return None
    return match.group(1), int(match.group(2)), int(match.group(3)), int(match.group(4) or match.group(3))


def parable_refs(path: Path, verses: dict[str, tuple[str, str]]) -> set[str]:
    refs: set[str] = set()
    for row in json.loads(path.read_text(encoding="utf-8")):
        for part in re.split(r"\s*[\u00b7;]\s*", row.get("passage", "")):
            parsed = parse_ref_part(part)
            if not parsed:
                continue
            book, chapter, first, last = parsed
            for verse in range(first, last + 1):
                ref = f"{book} {chapter}:{verse}"
                if ref in verses:
                    refs.add(ref)
    return refs


def category_pools(
    verses: dict[str, tuple[str, str]], places_path: Path, parables_path: Path
) -> dict[str, list[str]]:
    place_names = [row["name"] for row in json.loads(places_path.read_text(encoding="utf-8"))]
    # Include common biblical women whose names may not be represented in the
    # smaller people/places reference dataset.
    women = [
        "Eve", "Sarah", "Sarai", "Hagar", "Rebekah", "Rachel", "Leah", "Dinah",
        "Tamar", "Miriam", "Zipporah", "Rahab", "Deborah", "Jael", "Naomi", "Ruth",
        "Hannah", "Michal", "Abigail", "Bathsheba", "Jezebel", "Athaliah", "Esther",
        "Vashti", "Elizabeth", "Elisabeth", "Mary", "Martha", "Joanna", "Susanna",
        "Tabitha", "Dorcas", "Lydia", "Priscilla", "Phoebe", "Sapphira", "Damaris",
    ]
    patterns = {
        "Dreams & Visions": compile_words(["dream", "dreams", "dreamed", "vision", "visions"]),
        "Angels & Demons": compile_words([
            "angel", "angels", "archangel", "cherub", "cherubim", "seraphim", "Satan",
            "devil", "devils", "unclean spirit", "unclean spirits", "evil spirit",
        ]),
        "Food, Feasts & Offerings": compile_words([
            "offering", "offerings", "sacrifice", "sacrifices", "altar", "altars", "feast",
            "feasts", "Passover", "manna", "unleavened bread", "firstfruits", "tithe", "tithes",
            "meat offering", "drink offering", "burnt offering", "wave offering", "bread", "wine",
        ]),
        "Miracles": compile_words([
            "healed", "healeth", "healing", "miracle", "miracles", "wonders", "made whole",
            "leper", "leprosy", "blind", "lame", "deaf", "dumb", "raised from the dead",
            "rise from the dead", "cast out the devils", "cast out the unclean spirit",
        ]),
        "Places & Lands": compile_words(place_names),
        "Women of the Bible": compile_words(women),
    }
    pools = {category: [] for category in TARGETS}
    gospel_acts = {"Matthew", "Mark", "Luke", "John", "Acts"}
    for ref, (book, text) in verses.items():
        for category, pattern in patterns.items():
            if category == "Miracles" and book not in gospel_acts:
                continue
            if pattern.search(text):
                pools[category].append(ref)
        if book == "Revelation":
            pools["Revelation & End Times"].append(ref)
    pools["Parables"] = sorted(parable_refs(parables_path, verses))
    return pools


def clause_split(text: str) -> tuple[str, str] | None:
    text = text.rstrip(" .")
    boundaries = [match.end() for match in re.finditer(r"[,;:]\s+", text)]
    midpoint = len(text) / 2
    for position in sorted(boundaries, key=lambda value: abs(value - midpoint)):
        stem = text[:position].strip(" ,;:")
        answer = text[position:].strip(" ,;:.")
        if len(stem.split()) >= 5 and 4 <= len(answer.split()) <= 13:
            return stem, answer
    words = text.split()
    if 12 <= len(words) <= 38:
        answer_length = min(8, max(4, len(words) // 3))
        stem = " ".join(words[:-answer_length]).strip(" ,;:")
        answer = " ".join(words[-answer_length:]).strip(" ,;:.")
        if len(stem.split()) >= 6:
            return stem, answer
    return None


FAMILIAR_BOOKS = {
    "Genesis", "Exodus", "Joshua", "Judges", "Ruth", "1 Samuel", "Psalms", "Proverbs",
    "Daniel", "Matthew", "Mark", "Luke", "John", "Acts", "Revelation",
}
OBSCURE_BOOKS = {
    "Leviticus", "2 Chronicles", "Ezra", "Nehemiah", "Ecclesiastes", "Lamentations",
    "Hosea", "Joel", "Amos", "Obadiah", "Nahum", "Habakkuk", "Zephaniah", "Haggai",
    "Zechariah", "Jude",
}


def difficulty(book: str, answer: str, index: int) -> str:
    words = len(answer.split())
    if book in OBSCURE_BOOKS or words >= 11:
        return "Pastor"
    if book in FAMILIAR_BOOKS and words <= 6 and index % 3 == 0:
        return "Layperson"
    return "Deacon"


def load_seen_texts() -> set[str]:
    seen: set[str] = set()
    for name in ("manna_questions.json", "manna_questions_v2.json", "manna_questions_v3.json"):
        for question in json.loads((ROOT / name).read_text(encoding="utf-8")):
            seen.add(normalized(question["question"]))
    return seen


def make_questions(
    verses: dict[str, tuple[str, str]], pools: dict[str, list[str]], seed: int
) -> list[dict]:
    rng = random.Random(seed)
    seen_texts = load_seen_texts()
    used_refs: set[str] = set()
    output: list[dict] = []

    for category, target in TARGETS.items():
        candidates: list[tuple[str, str, str, str]] = []
        for ref in pools[category]:
            book, verse_text = verses[ref]
            split = clause_split(verse_text)
            if split:
                candidates.append((ref, book, split[0], split[1]))
        rng.shuffle(candidates)
        answer_pool = list(dict.fromkeys(item[3] for item in candidates))
        made = 0
        for ref, book, stem, answer in candidates:
            if made >= target:
                break
            if ref in used_refs or len(normalized(answer)) < 12:
                continue
            question_text = f'Complete {ref} in the KJV: "{stem} ..."'
            if normalized(question_text) in seen_texts:
                continue
            answer_words = len(answer.split())
            distractor_candidates = [
                value for value in answer_pool
                if value != answer
                and abs(len(value.split()) - answer_words) <= 2
                and normalized(value) not in normalized(verses[ref][1])
            ]
            rng.shuffle(distractor_candidates)
            distractors: list[str] = []
            for value in distractor_candidates:
                if normalized(value) not in {normalized(item) for item in distractors}:
                    distractors.append(value)
                if len(distractors) == 3:
                    break
            if len(distractors) != 3:
                continue
            options = [answer, *distractors]
            rng.shuffle(options)
            digest = hashlib.sha256((category + "\0" + ref + "\0" + question_text).encode()).hexdigest()[:16]
            output.append({
                "category": category,
                "difficulty": difficulty(book, answer, made),
                "question": question_text,
                "options": options,
                "correct": answer,
                "explanation": ref,
                "id": f"v4-{digest}",
            })
            seen_texts.add(normalized(question_text))
            used_refs.add(ref)
            made += 1
        if made != target:
            raise RuntimeError(f"{category}: generated {made}, expected {target}")
    return output


def verify(questions: list[dict], verses: dict[str, tuple[str, str]]) -> None:
    if len(questions) != sum(TARGETS.values()):
        raise RuntimeError("wrong total")
    if Counter(row["category"] for row in questions) != Counter(TARGETS):
        raise RuntimeError("wrong category allocation")
    if len({row["id"] for row in questions}) != len(questions):
        raise RuntimeError("duplicate generated ID")
    if len({normalized(row["question"]) for row in questions}) != len(questions):
        raise RuntimeError("duplicate generated question text")
    for row in questions:
        verse = normalized(verses[row["explanation"]][1])
        if normalized(row["correct"]) not in verse:
            raise RuntimeError(f"answer not found in source verse: {row['id']}")
        if row["correct"] not in row["options"] or len(row["options"]) != 4:
            raise RuntimeError(f"invalid options: {row['id']}")
        if len({normalized(value) for value in row["options"]}) != 4:
            raise RuntimeError(f"duplicate options: {row['id']}")
        for option in row["options"]:
            if option != row["correct"] and normalized(option) in verse:
                raise RuntimeError(f"distractor also occurs in source verse: {row['id']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kjv", type=Path, default=DEFAULT_KJV)
    parser.add_argument("--places", type=Path, default=DEFAULT_PLACES)
    parser.add_argument("--parables", type=Path, default=DEFAULT_PARABLES)
    parser.add_argument("--output", type=Path, default=ROOT / "manna_questions_v4.json")
    parser.add_argument("--seed", type=int, default=40000)
    args = parser.parse_args()
    for source in (args.kjv, args.places, args.parables):
        if not source.exists():
            raise FileNotFoundError(source)
    verses = parse_kjv(args.kjv)
    pools = category_pools(verses, args.places, args.parables)
    questions = make_questions(verses, pools, args.seed)
    verify(questions, verses)
    args.output.write_text(json.dumps(questions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(questions)} source-verified questions to {args.output}")
    print("Category additions:", dict(Counter(row["category"] for row in questions)))
    print("Difficulty additions:", dict(Counter(row["difficulty"] for row in questions)))


if __name__ == "__main__":
    main()
