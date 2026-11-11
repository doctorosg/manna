#!/usr/bin/env python3
"""Build Manna's deterministic, offline, age-screened children's bank.

The generator verifies its material against the public-domain World English
Bible (WEB). Ages 4–10 use original, source-cited questions about familiar Bible
stories. Ages 11–17 use exact WEB excerpts plus curated direct trivia. Both age
bands use distinct vocabulary, passage length, subject-safety, format and
answer-choice rules.

The previous KJV/template bank is intentionally not read or overwritten by
this program. It is retained under archive/questions with its permanent IDs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from early_story_facts import EARLY_STORY_FACTS
from teen_trivia_facts import TEEN_TRIVIA_FACTS


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WEB = (
    ROOT.parent
    / "lumina/lumina-bible/data/translations-import/eng-web_usfx/eng-web_usfx.xml"
)
DEFAULT_OUTPUT = ROOT / "children_questions.json"
AGE_GROUP_SIZES = {"4-10": 3_333, "11-17": 6_667}
# The 7–10 profile remains an internal generation profile for the questions
# promoted into the 11–17 bank. It is never emitted as a public age group.
OPTION_COUNTS = {"4-10": 3, "7-10": 3, "11-17": 4}
DIFFICULTIES = {"4-10": "Layperson", "7-10": "Deacon", "11-17": "Pastor"}


@dataclass(frozen=True)
class Book:
    code: str
    name: str
    testament: str
    section: str
    category: str


@dataclass(frozen=True)
class Verse:
    book: Book
    chapter: int
    verse: int
    text: str

    @property
    def reference(self) -> str:
        return f"{self.book.name} {self.chapter}:{self.verse}"


@dataclass(frozen=True)
class Story:
    code: str
    first_chapter: int
    last_chapter: int
    title: str
    signatures: frozenset[str]

    def contains(self, verse: Verse) -> bool:
        return (
            verse.book.code == self.code
            and self.first_chapter <= verse.chapter <= self.last_chapter
        )


BOOK_ROWS = [
    ("GEN", "Genesis", "Old Testament", "Law", "Genesis & Creation"),
    ("EXO", "Exodus", "Old Testament", "Law", "Moses & the Exodus"),
    ("LEV", "Leviticus", "Old Testament", "Law", "Laws & Commandments"),
    ("NUM", "Numbers", "Old Testament", "Law", "Numbers & Genealogies"),
    ("DEU", "Deuteronomy", "Old Testament", "Law", "Laws & Commandments"),
    ("JOS", "Joshua", "Old Testament", "History", "Kings & Kingdoms"),
    ("JDG", "Judges", "Old Testament", "History", "Kings & Kingdoms"),
    ("RUT", "Ruth", "Old Testament", "History", "Women of the Bible"),
    ("1SA", "1 Samuel", "Old Testament", "History", "Kings & Kingdoms"),
    ("2SA", "2 Samuel", "Old Testament", "History", "Kings & Kingdoms"),
    ("1KI", "1 Kings", "Old Testament", "History", "Kings & Kingdoms"),
    ("2KI", "2 Kings", "Old Testament", "History", "Kings & Kingdoms"),
    ("1CH", "1 Chronicles", "Old Testament", "History", "Kings & Kingdoms"),
    ("2CH", "2 Chronicles", "Old Testament", "History", "Kings & Kingdoms"),
    ("EZR", "Ezra", "Old Testament", "History", "Places & Lands"),
    ("NEH", "Nehemiah", "Old Testament", "History", "Places & Lands"),
    ("EST", "Esther", "Old Testament", "History", "Women of the Bible"),
    ("JOB", "Job", "Old Testament", "Wisdom & Poetry", "Psalms & Proverbs"),
    ("PSA", "Psalms", "Old Testament", "Wisdom & Poetry", "Psalms & Proverbs"),
    ("PRO", "Proverbs", "Old Testament", "Wisdom & Poetry", "Psalms & Proverbs"),
    ("ECC", "Ecclesiastes", "Old Testament", "Wisdom & Poetry", "Psalms & Proverbs"),
    ("SNG", "Song of Solomon", "Old Testament", "Wisdom & Poetry", "Psalms & Proverbs"),
    ("ISA", "Isaiah", "Old Testament", "Major Prophets", "Prophets"),
    ("JER", "Jeremiah", "Old Testament", "Major Prophets", "Prophets"),
    ("LAM", "Lamentations", "Old Testament", "Major Prophets", "Prophets"),
    ("EZK", "Ezekiel", "Old Testament", "Major Prophets", "Prophets"),
    ("DAN", "Daniel", "Old Testament", "Major Prophets", "Dreams & Visions"),
    ("HOS", "Hosea", "Old Testament", "Minor Prophets", "Prophets"),
    ("JOL", "Joel", "Old Testament", "Minor Prophets", "Prophets"),
    ("AMO", "Amos", "Old Testament", "Minor Prophets", "Prophets"),
    ("OBA", "Obadiah", "Old Testament", "Minor Prophets", "Prophets"),
    ("JON", "Jonah", "Old Testament", "Minor Prophets", "Prophets"),
    ("MIC", "Micah", "Old Testament", "Minor Prophets", "Prophets"),
    ("NAM", "Nahum", "Old Testament", "Minor Prophets", "Prophets"),
    ("HAB", "Habakkuk", "Old Testament", "Minor Prophets", "Prophets"),
    ("ZEP", "Zephaniah", "Old Testament", "Minor Prophets", "Prophets"),
    ("HAG", "Haggai", "Old Testament", "Minor Prophets", "Prophets"),
    ("ZEC", "Zechariah", "Old Testament", "Minor Prophets", "Prophets"),
    ("MAL", "Malachi", "Old Testament", "Minor Prophets", "Prophets"),
    ("MAT", "Matthew", "New Testament", "Gospels", "Life of Jesus"),
    ("MRK", "Mark", "New Testament", "Gospels", "Life of Jesus"),
    ("LUK", "Luke", "New Testament", "Gospels", "Life of Jesus"),
    ("JHN", "John", "New Testament", "Gospels", "Life of Jesus"),
    ("ACT", "Acts", "New Testament", "Acts", "The Apostles"),
    ("ROM", "Romans", "New Testament", "Paul's Letters", "Paul & His Letters"),
    ("1CO", "1 Corinthians", "New Testament", "Paul's Letters", "Paul & His Letters"),
    ("2CO", "2 Corinthians", "New Testament", "Paul's Letters", "Paul & His Letters"),
    ("GAL", "Galatians", "New Testament", "Paul's Letters", "Paul & His Letters"),
    ("EPH", "Ephesians", "New Testament", "Paul's Letters", "Paul & His Letters"),
    ("PHP", "Philippians", "New Testament", "Paul's Letters", "Paul & His Letters"),
    ("COL", "Colossians", "New Testament", "Paul's Letters", "Paul & His Letters"),
    ("1TH", "1 Thessalonians", "New Testament", "Paul's Letters", "Paul & His Letters"),
    ("2TH", "2 Thessalonians", "New Testament", "Paul's Letters", "Paul & His Letters"),
    ("1TI", "1 Timothy", "New Testament", "Paul's Letters", "Paul & His Letters"),
    ("2TI", "2 Timothy", "New Testament", "Paul's Letters", "Paul & His Letters"),
    ("TIT", "Titus", "New Testament", "Paul's Letters", "Paul & His Letters"),
    ("PHM", "Philemon", "New Testament", "Paul's Letters", "Paul & His Letters"),
    ("HEB", "Hebrews", "New Testament", "General Letters", "The Apostles"),
    ("JAS", "James", "New Testament", "General Letters", "The Apostles"),
    ("1PE", "1 Peter", "New Testament", "General Letters", "The Apostles"),
    ("2PE", "2 Peter", "New Testament", "General Letters", "The Apostles"),
    ("1JN", "1 John", "New Testament", "General Letters", "The Apostles"),
    ("2JN", "2 John", "New Testament", "General Letters", "The Apostles"),
    ("3JN", "3 John", "New Testament", "General Letters", "The Apostles"),
    ("JUD", "Jude", "New Testament", "General Letters", "The Apostles"),
    ("REV", "Revelation", "New Testament", "Revelation", "Revelation & End Times"),
]
BOOKS = {row[0]: Book(*row) for row in BOOK_ROWS}


# Familiar narratives and teachings used for the read-together 4–10 bank.
STORIES = [
    Story("GEN", 1, 2, "God creates the world", frozenset("god light day night earth heaven stars garden".split())),
    Story("GEN", 6, 9, "Noah and the ark", frozenset("noah ark flood rainbow dove covenant".split())),
    Story("GEN", 12, 25, "Abraham and his family", frozenset("abraham abram sarah isaac promise angel".split())),
    Story("GEN", 27, 36, "Jacob and his family", frozenset("jacob esau rachel leah bethel israel".split())),
    Story("GEN", 37, 50, "Joseph in Egypt", frozenset("joseph pharaoh egypt brothers dreams".split())),
    Story("EXO", 1, 2, "Baby Moses", frozenset("moses baby basket river pharaoh mother".split())),
    Story("EXO", 3, 4, "Moses and the burning bush", frozenset("moses bush fire yahweh".split())),
    Story("EXO", 5, 15, "Moses leads God's people", frozenset("moses pharaoh israel egypt sea passover".split())),
    Story("EXO", 16, 20, "God cares for Israel", frozenset("moses manna bread water mountain commandments".split())),
    Story("JOS", 1, 6, "Joshua and Jericho", frozenset("joshua jericho jordan trumpet wall".split())),
    Story("RUT", 1, 4, "Ruth and Naomi", frozenset("ruth naomi boaz bethlehem".split())),
    Story("1SA", 1, 3, "Samuel listens to God", frozenset("samuel hannah eli voice called".split())),
    Story("1SA", 16, 17, "David and Goliath", frozenset("david goliath sling stone sheep".split())),
    Story("1SA", 18, 20, "David and Jonathan", frozenset("david jonathan friend covenant".split())),
    Story("1SA", 24, 24, "David shows mercy to Saul", frozenset("david saul cave mercy".split())),
    Story("2SA", 5, 7, "David becomes king", frozenset("david king jerusalem ark".split())),
    Story("2SA", 9, 9, "David is kind to Mephibosheth", frozenset("david mephibosheth kindness table".split())),
    Story("1KI", 3, 3, "Solomon asks for wisdom", frozenset("solomon wisdom dream king".split())),
    Story("1KI", 8, 8, "Solomon's temple", frozenset("solomon temple ark prayer".split())),
    Story("1KI", 10, 10, "The queen visits Solomon", frozenset("queen solomon wisdom gifts".split())),
    Story("1KI", 17, 19, "God cares for Elijah", frozenset("elijah raven widow bread fire".split())),
    Story("2KI", 2, 2, "Elijah and Elisha", frozenset("elijah elisha chariot jordan".split())),
    Story("2KI", 4, 6, "God works through Elisha", frozenset("elisha oil bread naaman jordan".split())),
    Story("EST", 1, 10, "Queen Esther is brave", frozenset("esther mordecai king queen jews".split())),
    Story("DAN", 1, 1, "Daniel chooses what is right", frozenset("daniel food water king".split())),
    Story("DAN", 2, 4, "Daniel explains dreams", frozenset("daniel dream king heaven".split())),
    Story("DAN", 6, 6, "Daniel and the lions", frozenset("daniel lions den angel prayer".split())),
    Story("JON", 1, 4, "Jonah learns to obey God", frozenset("jonah ship sea fish nineveh plant".split())),
    Story("MAT", 1, 2, "Jesus is born", frozenset("jesus mary joseph baby star bethlehem wise".split())),
    Story("MAT", 3, 4, "Jesus begins his work", frozenset("jesus john jordan disciples".split())),
    Story("MAT", 5, 7, "Jesus teaches on the mountain", frozenset("jesus blessed prayer father heaven".split())),
    Story("MAT", 8, 9, "Jesus helps and heals people", frozenset("jesus healed faith disciples".split())),
    Story("MAT", 13, 13, "Jesus tells parables", frozenset("jesus parable seed field kingdom".split())),
    Story("MAT", 14, 14, "Jesus feeds a crowd and walks on water", frozenset("jesus bread fish boat water peter".split())),
    Story("MAT", 17, 18, "Jesus teaches his disciples", frozenset("jesus disciples child mountain".split())),
    Story("MAT", 21, 22, "Jesus enters Jerusalem", frozenset("jesus jerusalem donkey temple".split())),
    Story("MAT", 26, 28, "Jesus rises again", frozenset("jesus disciples tomb angel risen".split())),
    Story("MRK", 1, 4, "Jesus calls disciples and calms a storm", frozenset("jesus disciples boat sea wind".split())),
    Story("MRK", 5, 10, "Jesus teaches and helps people", frozenset("jesus disciples child bread fish".split())),
    Story("MRK", 11, 16, "Jesus in Jerusalem", frozenset("jesus jerusalem temple disciples tomb risen".split())),
    Story("LUK", 1, 2, "Jesus is born", frozenset("jesus mary joseph baby angel shepherd bethlehem".split())),
    Story("LUK", 5, 9, "Jesus calls and teaches disciples", frozenset("jesus disciples boat fish bread".split())),
    Story("LUK", 10, 10, "The good Samaritan", frozenset("samaritan neighbor road helped".split())),
    Story("LUK", 15, 15, "Jesus tells stories about what was lost", frozenset("sheep coin son father found".split())),
    Story("LUK", 18, 19, "Jesus welcomes people", frozenset("jesus children zacchaeus jericho".split())),
    Story("LUK", 22, 24, "Jesus rises again", frozenset("jesus disciples tomb angel risen".split())),
    Story("JHN", 1, 4, "People meet Jesus", frozenset("jesus john disciples water samaritan".split())),
    Story("JHN", 6, 6, "Jesus feeds a crowd", frozenset("jesus bread fish disciples".split())),
    Story("JHN", 9, 9, "Jesus helps a man see", frozenset("jesus blind eyes light".split())),
    Story("JHN", 10, 10, "Jesus is the good shepherd", frozenset("jesus shepherd sheep door".split())),
    Story("JHN", 11, 11, "Jesus and Lazarus", frozenset("jesus lazarus martha mary tomb".split())),
    Story("JHN", 13, 17, "Jesus teaches his friends", frozenset("jesus disciples love friend father".split())),
    Story("JHN", 20, 21, "Jesus is alive", frozenset("jesus mary disciples tomb fish peter".split())),
    Story("ACT", 1, 2, "The church begins", frozenset("jesus disciples spirit church languages".split())),
    Story("ACT", 3, 5, "The apostles share about Jesus", frozenset("peter john apostles jesus".split())),
    Story("ACT", 8, 10, "Philip, Saul, and Peter obey God", frozenset("philip saul peter angel jesus".split())),
    Story("ACT", 12, 12, "An angel helps Peter", frozenset("peter angel prison prayer".split())),
    Story("ACT", 16, 16, "Paul and Silas", frozenset("paul silas prayer prison".split())),
]


WORD_RE = re.compile(r"[A-Za-z]+(?:[’'][A-Za-z]+)?")
SPACE_RE = re.compile(r"\s+")
ARCHAIC_RE = re.compile(
    r"\b(thou|thee|thy|thine|ye|hath|doth|shalt|wilt|art|unto|wherefore|"
    r"whosoever|verily|begat|behold|spake|saith)\b",
    re.IGNORECASE,
)
SEXUAL_RE = re.compile(
    r"\b(adulter\w*|fornicat\w*|prostitut\w*|harlot|whore|naked\w*|"
    r"circumcis\w*|foreskin|genitals?|semen|emission|menstru\w*|rape\w*|"
    r"concubine|breasts?|virginity|sexual\w*|incest\w*|conceiv\w*)\b",
    re.IGNORECASE,
)
GRAPHIC_RE = re.compile(
    r"\b(behead\w*|dismember\w*|gouged?|corpse|carcass|blood\w*|slaughter\w*|"
    r"stab\w*|pierc\w*|hanged?|suicide|bowels?|wound\w*)\b",
    re.IGNORECASE,
)
YOUNG_BLOCKED_RE = re.compile(
    r"\b(kill\w*|murder\w*|death|dead|died|die|slay\w*|slew|slain|smote|"
    r"sword|war|battle|enemy|enemies|demon\w*|unclean spirit|hell|damn\w*|"
    r"wrath|wicked\w*|evil|sin\w*|crucif\w*|beat(?:en|ing)?|mock\w*|"
    r"idols?|gods)\b",
    re.IGNORECASE,
)
MIDDLE_BLOCKED_RE = re.compile(
    r"\b(suicide|behead\w*|dismember\w*|gouged?|slaughter\w*|rape\w*|"
    r"murder\w*|kill\w*|slay\w*|slew|slain|smote|hanged?|firstborn)\b",
    re.IGNORECASE,
)
YOUNG_COMPLEX_RE = re.compile(
    r"\b(eunuchs?|province|governors?|commanders?|officers?|chaldeans?|syrian|"
    r"transgression|iniquity|righteousness|sanctif\w*|atonement|tabernacle|"
    r"ordinance|statutes?|ephah|shekels?|genealog\w*|inheritance|decrees?|"
    r"synagogue|pharisees?|sadducees?|tribulation|persecution|hypocrites?|"
    r"leprosy|lepers?|paralytic|redeemer|firstborn)\b",
    re.IGNORECASE,
)


VOCABULARY: dict[str, tuple[str, ...]] = {
    "person": tuple("God Jesus Noah Abraham Sarah Isaac Jacob Esau Joseph Moses Aaron Miriam Joshua Ruth Naomi Boaz Samuel Eli Saul David Jonathan Solomon Elijah Elisha Esther Mordecai Daniel Jonah Mary Martha Lazarus Peter John Andrew James Matthew Zacchaeus Paul Silas Timothy angel angels disciple disciples shepherd shepherds king queen father mother brother brothers sister sisters friend friends child children baby son daughter".split()),
    "place": tuple("Eden Egypt Canaan Israel Jerusalem Bethlehem Nazareth Galilee Jordan Jericho Nineveh Babylon Rome sea river mountain garden temple church house home city town land heaven earth wilderness desert field road".split()),
    "animal": tuple("animal animals bird birds dove raven fish sheep lamb lion lions donkey horse camel goat goats cattle serpent whale eagle worm".split()),
    "nature": tuple("light darkness day night morning evening sun moon star stars sky cloud rain rainbow wind storm fire water sea river rock stone stones tree trees fruit seed seeds grass flower flowers bread oil wine gold silver".split()),
    "object": tuple("ark boat ship basket table cup door net nets robe crown book scroll gift gifts food bread lamp trumpet wall tent altar staff sling sandals coin coins".split()),
    "value": tuple("love joy peace hope faith truth life grace mercy kindness wisdom prayer praise promise good holy happy blessed strong brave gentle forgive forgiven obey help helps helped".split()),
    "number": tuple("one two three four five six seven eight nine ten twelve forty hundred thousand first second third fourth fifth sixth seventh".split()),
}
VOCAB_CANONICAL = {
    value.casefold(): value
    for values in VOCABULARY.values()
    for value in values
}
VOCAB_GROUP = {
    value.casefold(): group
    for group, values in VOCABULARY.items()
    for value in values
}
EARLY_GROUPS = {"person", "place", "animal", "nature", "object", "value", "number"}
MIDDLE_BOOK_CODES = {
    "GEN", "EXO", "DEU", "JOS", "RUT", "1SA", "2SA", "1KI", "2KI",
    "EST", "JOB", "PSA", "PRO", "ISA", "JER", "DAN", "JON", "MIC",
    "MAT", "MRK", "LUK", "JHN", "ACT", "ROM", "1CO", "2CO", "GAL",
    "EPH", "PHP", "COL", "1TH", "2TH", "1TI", "2TI", "TIT", "PHM",
    "HEB", "JAS", "1PE", "2PE", "1JN", "2JN", "3JN", "JUD", "REV",
}
MIDDLE_TEACHING_CHAPTERS = {
    "DEU": {5, 6},
    "PSA": {1, 8, 19, 23, 24, 27, 34, 46, 63, 84, 91, 95, 96, 100, 103, 117, 118, 121, 127, 133, 136, 139, 145, 146, 147, 148, 149, 150},
    "PRO": {1, 2, 3, 4, 10, 12, 15, 16, 17, 18, 20, 22},
    "ISA": {9, 11, 40, 55},
    "MIC": {6},
    "ROM": {8, 12},
    "1CO": {13},
    "GAL": {5, 6},
    "EPH": {4, 5, 6},
    "PHP": {2, 4},
    "COL": {3},
    "1TH": {5},
    "1TI": {4, 6},
    "2TI": {1, 3},
    "JAS": {1, 2, 3},
    "1JN": {1, 2, 3, 4, 5},
}


def stable_number(value: str) -> int:
    return int.from_bytes(hashlib.sha256(value.encode("utf-8")).digest()[:8], "big")


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def clean_text(value: str) -> str:
    return SPACE_RE.sub(" ", value.replace("¶", " ")).strip()


def parse_verses(path: Path) -> list[Verse]:
    root = ET.parse(path).getroot()
    verses: list[Verse] = []
    ignored = {"f", "x"}

    for book_node in root.findall("book"):
        book = BOOKS.get(book_node.attrib.get("id", ""))
        if book is None:
            continue
        current_ref: str | None = None
        pieces: list[str] = []

        def flush() -> None:
            nonlocal current_ref, pieces
            text = clean_text("".join(pieces))
            if current_ref and text:
                parts = current_ref.split(".")
                if len(parts) == 3:
                    verses.append(Verse(book, int(parts[1]), int(parts[2]), text))
            current_ref = None
            pieces = []

        def walk(node: ET.Element) -> None:
            nonlocal current_ref
            if node.text and current_ref:
                pieces.append(node.text)
            for child in node:
                tag = child.tag.rsplit("}", 1)[-1]
                if tag == "v":
                    flush()
                    current_ref = child.attrib.get("bcv")
                    if child.text:
                        pieces.append(child.text)
                elif tag == "c":
                    flush()
                elif tag not in ignored:
                    walk(child)
                if child.tail and current_ref:
                    pieces.append(child.tail)

        walk(book_node)
        flush()
    return verses


def story_for(verse: Verse) -> Story | None:
    return next((story for story in STORIES if story.contains(verse)), None)


def words(value: str) -> list[str]:
    return [match.group() for match in WORD_RE.finditer(value)]


def acceptable_source(verse: Verse, age_group: str) -> bool:
    if ARCHAIC_RE.search(verse.text) or SEXUAL_RE.search(verse.text) or GRAPHIC_RE.search(verse.text):
        return False
    if age_group == "4-6":
        return (
            story_for(verse) is not None
            and not YOUNG_BLOCKED_RE.search(verse.text)
            and not YOUNG_COMPLEX_RE.search(verse.text)
        )
    if age_group == "7-10":
        is_familiar = story_for(verse) is not None
        is_teaching = verse.chapter in MIDDLE_TEACHING_CHAPTERS.get(verse.book.code, set())
        return (
            verse.book.code in MIDDLE_BOOK_CODES
            and (is_familiar or is_teaching)
            and not MIDDLE_BLOCKED_RE.search(verse.text)
            and not re.search(r"\b(wine|strong drink|drunk\w*)\b", verse.text, re.IGNORECASE)
        )
    return verse.book.code != "SNG" and not MIDDLE_BLOCKED_RE.search(verse.text)


def excerpt_around(text: str, target: str, max_words: int) -> tuple[str, str] | None:
    matches = list(WORD_RE.finditer(text))
    target_index = next(
        (index for index, match in enumerate(matches) if match.group().casefold() == target.casefold()),
        None,
    )
    if target_index is None:
        return None
    first = max(0, target_index - max_words // 2)
    last = min(len(matches), first + max_words)
    first = max(0, last - max_words)
    start = matches[first].start()
    end = matches[last - 1].end()
    excerpt = text[start:end].strip(" ,;:—–-\"“”‘’.!?()[]")
    if first > 0:
        excerpt = "…" + excerpt
    if last < len(matches):
        excerpt += "…"
    target_match = re.search(rf"\b{re.escape(target)}\b", excerpt, re.IGNORECASE)
    if target_match is None:
        return None
    blanked = excerpt[:target_match.start()] + "___" + excerpt[target_match.end():]
    return excerpt, blanked


def readable(excerpt: str, age_group: str, min_words: int | None = None) -> bool:
    tokens = words(excerpt)
    if not tokens:
        return False
    limits = {
        "4-6": (7, 14, 9, 4.6),
        "7-10": (8, 23, 13, 5.9),
        "11-17": (10, 30, 16, 6.6),
    }
    default_min, max_count, max_length, max_average = limits[age_group]
    minimum = default_min if min_words is None else min_words
    lengths = [len(token) for token in tokens]
    return (
        minimum <= len(tokens) <= max_count
        and max(lengths) <= max_length
        and sum(lengths) / len(lengths) <= max_average
    )


def typed_targets(verse: Verse, age_group: str) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    seen: set[str] = set()
    for token in words(verse.text):
        key = token.casefold()
        group = VOCAB_GROUP.get(key)
        if group is None or key in seen:
            continue
        if age_group == "4-6" and group not in EARLY_GROUPS:
            continue
        seen.add(key)
        result.append((VOCAB_CANONICAL[key], group))
    return result


def shuffled_options(
    correct: str,
    pool: Iterable[str],
    count: int,
    salt: str,
    forbidden_text: str = "",
) -> list[str]:
    forbidden = {token.casefold() for token in words(forbidden_text)}
    choices = [correct]
    for value in sorted(set(pool), key=lambda item: stable_number(f"{salt}|choice|{item}")):
        if value.casefold() == correct.casefold() or value.casefold() in forbidden:
            continue
        if value.casefold() not in {choice.casefold() for choice in choices}:
            choices.append(value)
        if len(choices) == count:
            break
    if len(choices) != count:
        raise RuntimeError(f"Could not build {count} choices for {correct!r}")
    return sorted(choices, key=lambda item: stable_number(f"{salt}|position|{item}"))


def make_row(
    *,
    verse: Verse,
    age_group: str,
    format_name: str,
    question: str,
    options: list[str],
    correct: str,
    excerpt: str,
) -> dict:
    # IDs describe the sourced record, not its display wording. Copy edits to a
    # prompt therefore do not consume a new permanent question number.
    identity = f"v2|{age_group}|{format_name}|{verse.reference}|{correct}|{excerpt}"
    identifier = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:18]
    return {
        "id": f"child-v2-{age_group}-{identifier}",
        "category": verse.book.category,
        "difficulty": DIFFICULTIES[age_group],
        "ageGroup": age_group,
        "format": format_name,
        "question": question,
        "options": options,
        "correct": correct,
        "explanation": f"{verse.reference} (WEB): “{excerpt}”",
    }


EARLY_PROMPT_FRAMES = (
    "Bible time: {question}",
    "{topic} — {question}",
    "Bible story: {topic}. {question}",
    "Story time: {topic}. {question}",
    "Think about this Bible story: {topic}. {question}",
    "Remember this Bible story: {topic}. {question}",
    "Quick Bible question: {question}",
    "Choose the right answer: {question}",
    "Can you remember? {question}",
    "What happened in the Bible? {question}",
    "Listen carefully: {question}",
    "Which answer is right? {question}",
    "Let's remember the Bible story. {question}",
    "A Bible story question: {question}",
    "Your turn: {question}",
    "Tell what you know: {question}",
)


def early_story_candidates(verses: list[Verse]) -> list[dict]:
    """Create direct, three-choice questions from manually reviewed facts."""
    verse_by_reference = {verse.reference: verse for verse in verses}
    rows: list[dict] = []
    for fact_index, (topic, reference, base_question, correct, distractors) in enumerate(EARLY_STORY_FACTS):
        verse = verse_by_reference.get(reference)
        if verse is None:
            raise RuntimeError(f"Unknown ages 4–10 reference: {reference}")
        if len(set(distractors)) != 3 or correct in distractors:
            raise RuntimeError(f"Invalid ages 4–10 choices for: {base_question}")

        wrong_pairs = (
            (distractors[0], distractors[1]),
            (distractors[0], distractors[2]),
            (distractors[1], distractors[2]),
        )
        for frame_index, frame in enumerate(EARLY_PROMPT_FRAMES):
            question = frame.format(topic=topic, question=base_question)
            for pair_index, wrong_pair in enumerate(wrong_pairs):
                salt = f"early-v4|{fact_index}|{frame_index}|{pair_index}"
                options = sorted(
                    [correct, *wrong_pair],
                    key=lambda value: stable_number(f"{salt}|position|{value}"),
                )
                identifier = hashlib.sha256(
                    f"{salt}|{reference}|{base_question}|{correct}".encode("utf-8")
                ).hexdigest()[:18]
                rows.append({
                    "id": f"child-v4-4-10-{identifier}",
                    "concept": f"early-story-{fact_index:03d}",
                    "category": verse.book.category,
                    "difficulty": DIFFICULTIES["4-10"],
                    "ageGroup": "4-10",
                    "format": "story-quiz",
                    "topic": topic,
                    "question": question,
                    "options": options,
                    "correct": correct,
                    "explanation": f"{reference} (WEB) — {topic}",
                })
    return rows


def teen_trivia_candidates(verses: list[Verse]) -> list[dict]:
    """Create direct, four-choice questions from manually reviewed teen facts."""
    verse_by_reference = {verse.reference: verse for verse in verses}
    rows: list[dict] = []
    for fact_index, (topic, reference, question, correct, distractors) in enumerate(TEEN_TRIVIA_FACTS):
        verse = verse_by_reference.get(reference)
        if verse is None:
            raise RuntimeError(f"Unknown ages 11–17 reference: {reference}")
        if len(set(distractors)) != 3 or correct in distractors:
            raise RuntimeError(f"Invalid ages 11–17 choices for: {question}")

        salt = f"teen-trivia-v3|{fact_index}|{reference}|{correct}"
        options = sorted(
            [correct, *distractors],
            key=lambda value: stable_number(f"{salt}|position|{value}"),
        )
        identifier = hashlib.sha256(
            f"{salt}|{question}".encode("utf-8")
        ).hexdigest()[:18]
        rows.append({
            "id": f"child-v3-11-17-{identifier}",
            "concept": f"teen-trivia-{fact_index:03d}",
            "category": verse.book.category,
            "difficulty": DIFFICULTIES["11-17"],
            "ageGroup": "11-17",
            "format": "teen-trivia",
            "topic": topic,
            "question": question,
            "options": options,
            "correct": correct,
            "explanation": f"{reference} (WEB) — {topic}",
        })
    return rows


def cloze_candidates(verses: list[Verse], age_group: str) -> list[dict]:
    max_words = {"4-6": 14, "7-10": 21, "11-17": 27}[age_group]
    prompt = {
        "4-6": "Read together and choose the missing word:",
        "7-10": "Which word completes this Bible sentence?",
        "11-17": "Which word accurately completes this Bible passage?",
    }[age_group]
    rows: list[dict] = []
    for verse in verses:
        if not acceptable_source(verse, age_group):
            continue
        for target, group in typed_targets(verse, age_group):
            excerpt_pair = excerpt_around(verse.text, target, max_words)
            if excerpt_pair is None:
                continue
            excerpt, blanked = excerpt_pair
            if not readable(excerpt, age_group):
                continue
            options = shuffled_options(
                target,
                VOCABULARY[group],
                OPTION_COUNTS[age_group],
                f"cloze|{age_group}|{verse.reference}|{target}",
                excerpt,
            )
            story = story_for(verse)
            if age_group == "4-6" and story:
                question = (
                    f"Read together. Which word completes this sentence from "
                    f"{story.title}? “{blanked}”"
                )
            else:
                question = f"{prompt} “{blanked}”"
            rows.append(make_row(
                verse=verse,
                age_group=age_group,
                format_name="missing-word",
                question=question,
                options=options,
                correct=target,
                excerpt=excerpt,
            ))
    return rows


def recognition_candidates(verses: list[Verse], age_group: str) -> list[dict]:
    max_words = {"4-6": 14, "7-10": 20, "11-17": 26}[age_group]
    rows: list[dict] = []
    for verse in verses:
        if not acceptable_source(verse, age_group):
            continue
        for target, group in typed_targets(verse, age_group):
            excerpt_pair = excerpt_around(verse.text, target, max_words)
            if excerpt_pair is None:
                continue
            excerpt, _ = excerpt_pair
            if not readable(excerpt, age_group):
                continue
            options = shuffled_options(
                target,
                VOCABULARY[group],
                OPTION_COUNTS[age_group],
                f"recognition|{age_group}|{verse.reference}|{target}",
                excerpt,
            )
            lead = "Listen to" if age_group == "4-6" else "Read"
            question = f"{lead}: “{excerpt}” Which answer is named in the sentence?"
            rows.append(make_row(
                verse=verse,
                age_group=age_group,
                format_name="word-recognition",
                question=question,
                options=options,
                correct=target,
                excerpt=excerpt,
            ))
    return rows


def story_candidates(verses: list[Verse], age_group: str) -> list[dict]:
    max_words = 15 if age_group == "4-6" else 21
    titles = [story.title for story in STORIES]
    rows: list[dict] = []
    for verse in verses:
        story = story_for(verse)
        if story is None or not acceptable_source(verse, age_group):
            continue
        for signature in sorted(story.signatures):
            if not re.search(rf"\b{re.escape(signature)}\b", verse.text, re.IGNORECASE):
                continue
            excerpt_pair = excerpt_around(verse.text, signature, max_words)
            if excerpt_pair is None:
                continue
            excerpt, _ = excerpt_pair
            if not readable(excerpt, age_group, min_words=2 if age_group == "4-6" else 5):
                continue
            # A generic word such as "Jesus" or "Moses" can occur in several
            # familiar accounts. Never offer another account with the same
            # signature as a distractor.
            incompatible_titles = {
                candidate.title for candidate in STORIES
                if signature in candidate.signatures
            }
            options = shuffled_options(
                story.title,
                [title for title in titles if title not in incompatible_titles],
                OPTION_COUNTS[age_group],
                f"story|{age_group}|{verse.reference}|{signature}",
            )
            question = (
                f"Which Bible story does this sentence belong to? “{excerpt}”"
                if age_group == "4-6"
                else f"Which familiar Bible account gives this sentence? “{excerpt}”"
            )
            rows.append(make_row(
                verse=verse,
                age_group=age_group,
                format_name="story-context",
                question=question,
                options=options,
                correct=story.title,
                excerpt=excerpt,
            ))
    return rows


def book_candidates(verses: list[Verse], age_group: str) -> list[dict]:
    max_words = 20 if age_group == "7-10" else 27
    candidate_rows: list[tuple[dict, str, str]] = []
    for verse in verses:
        if not acceptable_source(verse, age_group):
            continue
        token_candidates = [target for target, _ in typed_targets(verse, age_group)]
        if not token_candidates:
            continue
        target = sorted(
            token_candidates,
            key=lambda value: stable_number(f"book-target|{verse.reference}|{value}"),
        )[0]
        excerpt_pair = excerpt_around(verse.text, target, max_words)
        if excerpt_pair is None:
            continue
        excerpt, _ = excerpt_pair
        if not readable(excerpt, age_group, min_words=8):
            continue
        phrase = normalized(excerpt.replace("…", ""))
        books = [
            book.name for book in BOOKS.values()
            if book.testament == verse.book.testament
            and (age_group == "11-17" or book.code in MIDDLE_BOOK_CODES)
        ]
        options = shuffled_options(
            verse.book.name,
            books,
            OPTION_COUNTS[age_group],
            f"book|{age_group}|{verse.reference}",
        )
        question = (
            f"Which Bible book contains this sentence? “{excerpt}”"
            if age_group == "7-10"
            else f"Identify the Bible book containing this passage: “{excerpt}”"
        )
        candidate_rows.append((make_row(
            verse=verse,
            age_group=age_group,
            format_name="book-context",
            question=question,
            options=options,
            correct=verse.book.name,
            excerpt=excerpt,
        ), phrase, verse.book.code))
    phrase_owners: dict[str, set[str]] = defaultdict(set)
    for _, phrase, code in candidate_rows:
        phrase_owners[phrase].add(code)
    return [
        row for row, phrase, code in candidate_rows
        if phrase_owners[phrase] == {code}
    ]


def section_candidates(verses: list[Verse]) -> list[dict]:
    age_group = "11-17"
    candidate_rows: list[tuple[dict, str, str]] = []
    for verse in verses:
        if not acceptable_source(verse, age_group):
            continue
        targets = typed_targets(verse, age_group)
        if not targets:
            continue
        target = sorted(
            (value for value, _ in targets),
            key=lambda value: stable_number(f"section-target|{verse.reference}|{value}"),
        )[0]
        excerpt_pair = excerpt_around(verse.text, target, 27)
        if excerpt_pair is None:
            continue
        excerpt, _ = excerpt_pair
        if not readable(excerpt, age_group, min_words=10):
            continue
        phrase = normalized(excerpt.replace("…", ""))
        sections = sorted({
            book.section for book in BOOKS.values()
            if book.testament == verse.book.testament
        })
        if len(sections) < OPTION_COUNTS[age_group]:
            continue
        options = shuffled_options(
            verse.book.section,
            sections,
            OPTION_COUNTS[age_group],
            f"section|{verse.reference}",
        )
        question = f"Which section of the Bible contains this passage? “{excerpt}”"
        candidate_rows.append((make_row(
            verse=verse,
            age_group=age_group,
            format_name="section-context",
            question=question,
            options=options,
            correct=verse.book.section,
            excerpt=excerpt,
        ), phrase, verse.book.section))
    phrase_owners: dict[str, set[str]] = defaultdict(set)
    for _, phrase, section in candidate_rows:
        phrase_owners[phrase].add(section)
    return [
        row for row, phrase, section in candidate_rows
        if phrase_owners[phrase] == {section}
    ]


def take_balanced(
    candidates: list[dict],
    count: int,
    salt: str,
    used_ids: set[str],
    used_texts: set[str],
    bucket_key: Callable[[dict], str] = lambda row: str(row["category"]),
) -> list[dict]:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for row in candidates:
        if row["id"] in used_ids or normalized(row["question"]) in used_texts:
            continue
        buckets[bucket_key(row)].append(row)
    for key, bucket in buckets.items():
        bucket.sort(key=lambda row: stable_number(f"{salt}|{key}|{row['id']}"))
    keys = sorted(buckets, key=lambda key: stable_number(f"{salt}|bucket|{key}"))
    result: list[dict] = []
    while len(result) < count and keys:
        progressed = False
        for key in list(keys):
            while buckets[key]:
                row = buckets[key].pop()
                text_key = normalized(row["question"])
                if row["id"] not in used_ids and text_key not in used_texts:
                    result.append(row)
                    used_ids.add(row["id"])
                    used_texts.add(text_key)
                    progressed = True
                    break
            if not buckets[key]:
                keys.remove(key)
            if len(result) == count:
                break
        if not progressed:
            break
    if len(result) != count:
        raise RuntimeError(f"Needed {count} rows for {salt}, found {len(result)}")
    return result


def promote_middle_rows(rows: list[dict], verses: list[Verse]) -> list[dict]:
    """Move the former 7–10 set into 11–17 and expand it to four choices."""
    verse_by_reference = {verse.reference: verse for verse in verses}
    book_code_by_name = {book.name: book.code for book in BOOKS.values()}
    book_corpora = {
        code: " ¶ ".join(normalized(verse.text) for verse in verses if verse.book.code == code)
        for code in BOOKS
    }
    explanation_re = re.compile(r"^(.+ \d+:\d+) \(WEB\): “(.*)”$")
    story_titles = sorted({story.title for story in STORIES})
    promoted: list[dict] = []

    for source_row in rows:
        row = dict(source_row)
        match = explanation_re.match(str(row["explanation"]))
        if match is None or match.group(1) not in verse_by_reference:
            raise RuntimeError(f"Cannot promote question with invalid citation: {row['id']}")
        verse = verse_by_reference[match.group(1)]
        excerpt = match.group(2)
        correct = str(row["correct"])
        format_name = str(row["format"])
        salt = f"promoted-v4|{row['id']}|{correct}"

        if format_name in {"missing-word", "word-recognition"}:
            group = VOCAB_GROUP.get(correct.casefold())
            if group is None:
                raise RuntimeError(f"Cannot identify answer vocabulary for {row['id']}")
            pool: Iterable[str] = (*map(str, row["options"]), *VOCABULARY[group])
            options = shuffled_options(correct, pool, 4, salt, excerpt)
        elif format_name == "story-context":
            excerpt_words = {word.casefold() for word in words(excerpt)}
            pool = (
                title for title in story_titles
                if title == correct
                or not ({word.casefold() for word in words(title)} & excerpt_words)
            )
            options = shuffled_options(correct, (*map(str, row["options"]), *pool), 4, salt)
        elif format_name == "book-context":
            phrase = normalized(excerpt.replace("…", ""))
            eligible_books = (
                book.name for book in BOOKS.values()
                if book.testament == verse.book.testament
                and book.code in MIDDLE_BOOK_CODES
                and (book.name == correct or phrase not in book_corpora[book.code])
            )
            options = shuffled_options(
                correct,
                (*map(str, row["options"]), *eligible_books),
                4,
                salt,
            )
            if any(option not in book_code_by_name for option in options):
                raise RuntimeError(f"Unknown promoted book option for {row['id']}")
        else:
            raise RuntimeError(f"Unsupported promoted format {format_name} for {row['id']}")

        identifier = hashlib.sha256(
            f"{salt}|{row['question']}|{'|'.join(options)}".encode("utf-8")
        ).hexdigest()[:18]
        row.update({
            "id": f"child-v4-11-17-{identifier}",
            "difficulty": DIFFICULTIES["11-17"],
            "ageGroup": "11-17",
            "generation": "promoted-middle-v4",
            "options": options,
        })
        promoted.append(row)
    return promoted


def generate(verses: list[Verse]) -> list[dict]:
    rows: list[dict] = []
    used_ids: set[str] = set()
    used_texts: set[str] = set()

    # Ages 4–10: direct questions about familiar stories, with three choices.
    rows += take_balanced(
        early_story_candidates(verses), 3_333, "early-story-v4", used_ids, used_texts,
        bucket_key=lambda row: str(row["concept"]),
    )

    # Preserve the former 7–10 questions, but publish them as four-choice
    # questions inside the 11–17 bank.
    former_middle: list[dict] = []
    former_middle += take_balanced(cloze_candidates(verses, "7-10"), 1_200, "middle-cloze", used_ids, used_texts)
    former_middle += take_balanced(recognition_candidates(verses, "7-10"), 800, "middle-recognition", used_ids, used_texts)
    former_middle += take_balanced(story_candidates(verses, "7-10"), 533, "middle-story", used_ids, used_texts)
    former_middle += take_balanced(
        book_candidates(verses, "7-10"), 800, "middle-book", used_ids, used_texts,
        bucket_key=lambda row: str(row["correct"]),
    )
    promoted_middle = promote_middle_rows(former_middle, verses)
    used_ids.update(str(row["id"]) for row in promoted_middle)
    rows += promoted_middle

    # Ages 11–17: wider canon, longer context, four plausible choices.
    rows += take_balanced(cloze_candidates(verses, "11-17"), 1_200, "teen-cloze", used_ids, used_texts)
    rows += take_balanced(recognition_candidates(verses, "11-17"), 600, "teen-recognition", used_ids, used_texts)
    rows += take_balanced(
        book_candidates(verses, "11-17"), 800, "teen-book", used_ids, used_texts,
        bucket_key=lambda row: str(row["correct"]),
    )
    teen_trivia_count = len(TEEN_TRIVIA_FACTS)
    rows += take_balanced(
        section_candidates(verses), 734 - teen_trivia_count, "teen-section", used_ids, used_texts,
        bucket_key=lambda row: str(row["correct"]),
    )
    rows += take_balanced(
        teen_trivia_candidates(verses), teen_trivia_count, "teen-trivia-v3", used_ids, used_texts,
        bucket_key=lambda row: str(row["concept"]),
    )
    return rows


def validate(rows: list[dict]) -> None:
    actual = Counter(row.get("ageGroup") for row in rows)
    if dict(actual) != AGE_GROUP_SIZES:
        raise RuntimeError(f"Wrong age-group counts: {dict(actual)}")
    ids = [str(row["id"]) for row in rows]
    texts = [normalized(str(row["question"])) for row in rows]
    if len(set(ids)) != len(ids):
        raise RuntimeError("Generated child IDs are not unique")
    if len(set(texts)) != len(texts):
        raise RuntimeError("Generated child question text is not unique")
    for row in rows:
        age_group = str(row["ageGroup"])
        expected_prefix = (
            "child-v4-"
            if row["format"] == "story-quiz" or row.get("generation") == "promoted-middle-v4"
            else "child-v3-" if row["format"] == "teen-trivia"
            else "child-v2-"
        )
        if not str(row["id"]).startswith(expected_prefix):
            raise RuntimeError(f"Replacement ID has the wrong generation marker: {row['id']}")
        if len(row["options"]) != OPTION_COUNTS[age_group]:
            raise RuntimeError(f"Wrong option count for {row['id']}")
        if row["correct"] not in row["options"]:
            raise RuntimeError(f"Correct answer missing for {row['id']}")
        combined = f"{row['question']} {row['explanation']}"
        if ARCHAIC_RE.search(combined) or SEXUAL_RE.search(combined) or GRAPHIC_RE.search(combined):
            raise RuntimeError(f"Age-screening term in {row['id']}")
        if age_group == "4-10" and YOUNG_BLOCKED_RE.search(combined):
            raise RuntimeError(f"Young-child safety term in {row['id']}")
    format_counts = Counter((row["ageGroup"], row["format"]) for row in rows)
    required_formats = {
        "4-10": {"story-quiz"},
        "11-17": {"missing-word", "word-recognition", "story-context", "book-context", "section-context", "teen-trivia"},
    }
    for age_group, required in required_formats.items():
        found = {name for (group, name), count in format_counts.items() if group == age_group and count}
        if found != required:
            raise RuntimeError(f"Wrong format mix for {age_group}: {found}")


def validate_against_source(rows: list[dict], verses: list[Verse]) -> None:
    """Prove answers and offered choices against the local WEB source."""
    verse_by_reference = {verse.reference: verse for verse in verses}
    book_code_by_name = {book.name: book.code for book in BOOKS.values()}
    book_corpora = {
        code: " ¶ ".join(normalized(verse.text) for verse in verses if verse.book.code == code)
        for code in BOOKS
    }
    section_corpora = {
        section: " ¶ ".join(
            normalized(verse.text) for verse in verses if verse.book.section == section
        )
        for section in {book.section for book in BOOKS.values()}
    }
    explanation_re = re.compile(r"^(.+ \d+:\d+) \(WEB\): “(.*)”$")

    for row in rows:
        format_name = str(row["format"])
        if format_name in {"story-quiz", "teen-trivia"}:
            reference = str(row["explanation"]).split(" (WEB)", 1)[0]
            if reference not in verse_by_reference:
                raise RuntimeError(f"Invalid WEB citation for {row['id']}")
            continue

        match = explanation_re.match(str(row["explanation"]))
        if match is None or match.group(1) not in verse_by_reference:
            raise RuntimeError(f"Invalid WEB citation for {row['id']}")
        verse = verse_by_reference[match.group(1)]
        excerpt = match.group(2)
        phrase = normalized(excerpt.replace("…", ""))
        if phrase not in normalized(verse.text):
            raise RuntimeError(f"Quoted excerpt is not in the cited verse for {row['id']}")

        correct = str(row["correct"])
        excerpt_words = {word.casefold() for word in words(excerpt)}
        if format_name in {"missing-word", "word-recognition"}:
            if correct.casefold() not in excerpt_words:
                raise RuntimeError(f"Answer is absent from cited excerpt for {row['id']}")
        if format_name == "word-recognition":
            for option in row["options"]:
                if option != correct and str(option).casefold() in excerpt_words:
                    raise RuntimeError(f"Recognition distractor is also in excerpt for {row['id']}")
        elif format_name == "book-context":
            if correct != verse.book.name:
                raise RuntimeError(f"Wrong cited book for {row['id']}")
            offered_owners = {
                option for option in row["options"]
                if phrase in book_corpora[book_code_by_name[str(option)]]
            }
            if offered_owners != {correct}:
                raise RuntimeError(f"Offered book choices are source-ambiguous for {row['id']}")
        elif format_name == "section-context":
            if correct != verse.book.section:
                raise RuntimeError(f"Wrong cited section for {row['id']}")
            offered_owners = {
                option for option in row["options"]
                if phrase in section_corpora[str(option)]
            }
            if offered_owners != {correct}:
                raise RuntimeError(f"Offered section choices are source-ambiguous for {row['id']}")
        elif format_name == "story-context":
            story = story_for(verse)
            if story is None or correct != story.title:
                raise RuntimeError(f"Wrong familiar account for {row['id']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_WEB)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if not args.source.is_file():
        raise SystemExit(f"World English Bible source not found: {args.source}")
    verses = parse_verses(args.source)
    rows = generate(verses)
    validate(rows)
    validate_against_source(rows, verses)
    args.output.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows):,} age-screened child questions to {args.output}")
    for group in AGE_GROUP_SIZES:
        formats = Counter(row["format"] for row in rows if row["ageGroup"] == group)
        print(f"  Ages {group}: {sum(formats.values()):,} {dict(formats)}")


if __name__ == "__main__":
    main()
