#!/usr/bin/env python3
"""Anchor tests for the adult difficulty allocator."""

from __future__ import annotations

import unittest

from scripts.difficulty_assessment import allocate_difficulty


def question(
    prompt: str,
    correct: str,
    options: list[str],
    difficulty: str = "Deacon",
    explanation: str = "",
) -> dict:
    return {
        "id": "test",
        "category": "Genesis & Creation",
        "difficulty": difficulty,
        "question": prompt,
        "options": options,
        "correct": correct,
        "explanation": explanation,
    }


class DifficultyAllocationTests(unittest.TestCase):
    def assert_tier(self, expected: str, item: dict, answer_frequency: int = 1) -> None:
        self.assertEqual(expected, allocate_difficulty(item, answer_frequency).tier)

    def test_layperson_story_recall(self) -> None:
        cases = [
            question("Who built the ark?", "Noah", ["Noah", "Moses", "David", "Paul"]),
            question("Who defeated Goliath?", "David", ["David", "Saul", "Samuel", "Solomon"]),
            question(
                "In which book of the Bible do we find the story of creation?",
                "Genesis",
                ["Genesis", "Exodus", "Psalms", "Matthew"],
                difficulty="Layperson",
            ),
            question(
                "Which came first: The creation of the world or The flood of Noah?",
                "The creation of the world",
                ["The creation of the world", "The flood of Noah"],
                difficulty="Layperson",
            ),
        ]
        for item in cases:
            with self.subTest(item=item["question"]):
                self.assert_tier("Layperson", item, answer_frequency=20)

    def test_deacon_canonical_detail(self) -> None:
        cases = [
            question(
                "What wood was Noah's ark made from?",
                "Gopher wood",
                ["Gopher wood", "Cedar", "Acacia", "Oak"],
                explanation="Genesis 6:14 (KJV).",
            ),
            question(
                "Complete John 3:16 in the KJV: 'For God so loved the world ...'",
                "that he gave his only begotten Son",
                ["that he gave his only begotten Son", "that none should perish", "and sent an angel", "and judged the nations"],
            ),
            question(
                "Which prophet is echoed by 'out of Egypt have I called my son' in Matthew?",
                "Hosea",
                ["Hosea", "Joel", "Amos", "Micah"],
            ),
            question(
                "Who was the father of Mephibosheth?",
                "Jonathan",
                ["Jonathan", "Saul", "David", "Abner"],
                explanation="2 Samuel 4:4 (KJV).",
            ),
        ]
        for item in cases:
            with self.subTest(item=item["question"]):
                self.assert_tier("Deacon", item)

    def test_pastor_specialist_and_synthesis(self) -> None:
        cases = [
            question(
                "What does the Greek word 'Christos' mean?",
                "Anointed One",
                ["Anointed One", "Servant", "Prophet", "Teacher"],
                difficulty="Layperson",
            ),
            question(
                "Which Church Father wrote this commentary on Matthew 6:27?",
                "Hilary",
                ["Hilary", "Bede", "Jerome", "Origen"],
            ),
            question(
                "Which Gospel verse draws from Exodus 16:4?",
                "John 6:23",
                ["John 6:23", "Matthew 4:4", "Mark 1:2", "Luke 2:4"],
            ),
            question(
                "What type of connection links Hebrews 4 to Genesis 2?",
                "A shared theological theme",
                ["A shared theological theme", "A genealogy", "A place name", "A chronological marker"],
            ),
            question(
                "When did the Exodus occur in biblical chronology?",
                "c. 1446 BC",
                ["c. 1446 BC", "c. 1000 BC", "c. 586 BC", "c. AD 30"],
            ),
            question(
                "What is the documentary hypothesis?",
                "A theory of sources behind the Pentateuch",
                ["A theory of sources behind the Pentateuch", "A list of kings", "A feast calendar", "A translation method"],
            ),
            question(
                "How many people were aboard the ship carrying Paul toward Rome?",
                "276",
                ["276", "120", "153", "300"],
                difficulty="Pastor",
                explanation="Acts 27:37 (KJV).",
            ),
        ]
        for item in cases:
            with self.subTest(item=item["question"]):
                self.assert_tier("Pastor", item)


if __name__ == "__main__":
    unittest.main()
