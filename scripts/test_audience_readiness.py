#!/usr/bin/env python3
"""Anchor tests for the 11-17/Layperson readiness rubric."""

from __future__ import annotations

import unittest

from audience_readiness import COMPONENT_MAXIMA, assess_readiness


def question(prompt: str, correct: str, *, format_name: str | None = None) -> dict:
    row = {
        "question": prompt,
        "correct": correct,
        "options": [correct, "Moses", "David", "Peter"],
        "explanation": "A concise Bible explanation.",
    }
    if format_name:
        row["format"] = format_name
    return row


class AudienceReadinessTests(unittest.TestCase):
    def test_components_sum_to_score_and_respect_maxima(self) -> None:
        result = assess_readiness(
            question(
                "Identify the Bible book containing this passage: "
                "‘Grace, mercy, and peace will be with us from God the Father.’",
                "2 John",
                format_name="book-context",
            )
        )
        components = {
            "canonical_knowledge": result.canonical_knowledge,
            "task_abstraction": result.task_abstraction,
            "reading_burden": result.reading_burden,
            "answer_specificity": result.answer_specificity,
            "distractor_competitiveness": result.distractor_competitiveness,
        }
        self.assertEqual(result.score, sum(components.values()))
        for name, value in components.items():
            self.assertLessEqual(value, COMPONENT_MAXIMA[name])

    def test_context_inference_is_harder_than_word_recognition(self) -> None:
        recognition = assess_readiness(
            question(
                "Which word in this sentence names a person? ‘David trusted God.’",
                "David",
                format_name="word-recognition",
            ),
            answer_frequency=20,
        )
        context = assess_readiness(
            question(
                "Identify the Bible book containing this passage: ‘The elder to "
                "the chosen lady and her children, whom I love in truth.’",
                "2 John",
                format_name="book-context",
            )
        )
        self.assertGreaterEqual(context.score - recognition.score, 20)

    def test_familiar_direct_recall_stays_at_the_teen_end(self) -> None:
        result = assess_readiness(
            question("Who built the ark before the flood?", "Noah"),
            answer_frequency=25,
        )
        self.assertLess(result.score, 40)
        self.assertEqual(result.task_abstraction, 10)


if __name__ == "__main__":
    unittest.main()
