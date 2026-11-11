#!/usr/bin/env python3
"""Tests for Pastor session-format classification."""

from __future__ import annotations

import unittest

from scripts.pastor_balance import pastor_format


def question(prompt: str, correct: str = "Answer") -> dict:
    return {
        "question": prompt,
        "correct": correct,
        "options": [correct, "B", "C", "D"],
        "explanation": "",
    }


class PastorBalanceTests(unittest.TestCase):
    def test_scripture_memory(self) -> None:
        self.assertEqual(
            "scriptureMemory",
            pastor_format(question("Complete this verse from Leviticus: 'And he shall...'")),
        )
        self.assertEqual(
            "scriptureMemory",
            pastor_format(question("Which Gospel verse draws from Exodus 16:4?", "John 6:23")),
        )
        self.assertEqual(
            "scriptureMemory",
            pastor_format(question("Where is this verse found: 'Here am I. Send me!'", "Isaiah 6:8")),
        )

    def test_specialist_recall_is_separate(self) -> None:
        self.assertEqual(
            "originalLanguage",
            pastor_format(question("What does the Hebrew word 'Elohim' mean?")),
        )
        self.assertEqual(
            "churchFather",
            pastor_format(question("Which Church Father wrote about Luke 8:39?")),
        )

    def test_interpretation(self) -> None:
        self.assertEqual(
            "interpretation",
            pastor_format(question("What OT concept underlies the phrase in Mark 15:30?")),
        )
        self.assertEqual(
            "interpretation",
            pastor_format(question("What do the seven lampstands in Revelation represent?")),
        )

    def test_other_advanced_knowledge(self) -> None:
        self.assertEqual(
            "other",
            pastor_format(question("When did Assyria conquer the northern kingdom?", "722 BC")),
        )


if __name__ == "__main__":
    unittest.main()
