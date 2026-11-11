#!/usr/bin/env python3
"""Audit whether Manna's adult difficulty labels increase monotonically."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from statistics import median

from build_question_bank import (
    AUDIENCE_OVERRIDES,
    DEFAULT_SOURCES,
    DIFFICULTY_OVERRIDES,
    build,
    load_audience_overrides,
    load_difficulty_overrides,
)
from difficulty_assessment import TIER_ORDER, allocate_difficulty, assess, question_family


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BANK = ROOT / "Manna/Resources/manna_questions.json"
DEFAULT_OUTPUT = ROOT / "reports/difficulty_audit"


def percentile(values: list[int], p: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * p
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bank", type=Path, default=DEFAULT_BANK)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--difficulty-overrides", type=Path, default=DIFFICULTY_OVERRIDES)
    parser.add_argument("--audience-overrides", type=Path, default=AUDIENCE_OVERRIDES)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    rows = json.loads(args.bank.read_text(encoding="utf-8"))
    adults = [row for row in rows if row.get("ageGroup") is None]
    if not adults:
        raise ValueError("The selected bank contains no adult questions.")
    invalid_labels = sorted({
        str(row.get("difficulty"))
        for row in adults
        if row.get("difficulty") not in TIER_ORDER
    })
    if invalid_labels:
        raise ValueError(f"Unknown adult difficulty labels: {invalid_labels}")
    overrides = load_difficulty_overrides(args.difficulty_overrides)
    audience_overrides = load_audience_overrides(args.audience_overrides)
    override_payload = json.loads(args.difficulty_overrides.read_text(encoding="utf-8"))
    retained_exceptions = {
        str(item["id"]): item
        for item in override_payload.get("retainedExceptions", [])
    }
    baseline_rows, _ = build(
        DEFAULT_SOURCES,
        difficulty_overrides=overrides,
        audience_overrides={},
        persist_registry=False,
    )
    baseline_adults = [
        row for row in baseline_rows if row.get("ageGroup") is None
    ]
    answer_frequencies = Counter(
        re.sub(r"[^a-z0-9]+", " ", str(row["correct"]).casefold()).strip()
        for row in baseline_adults
    )
    audited: list[dict] = []
    allocation_drift: list[dict] = []
    for row in adults:
        result = assess(row)
        override = overrides.get(str(row["id"]))
        audience_override = audience_overrides.get(str(row["id"]))
        retained_exception = retained_exceptions.get(str(row["id"]))
        baseline = str(override["from"]) if override else str(row["difficulty"])
        allocation_input = dict(row)
        allocation_input["difficulty"] = baseline
        answer_key = re.sub(
            r"[^a-z0-9]+", " ", str(row["correct"]).casefold()
        ).strip()
        allocation = allocate_difficulty(
            allocation_input, max(1, answer_frequencies[answer_key])
        )
        recommended = (
            "Layperson"
            if audience_override
            and audience_override["from"] == "11-17"
            and audience_override["to"] == "Layperson"
            else str(override["to"])
            if override
            else str(retained_exception["tier"])
            if retained_exception
            else allocation.tier
        )
        if (
            override
            and not audience_override
            and not override.get("operationalFloor", False)
            and allocation.tier != recommended
        ):
            allocation_drift.append({
                "id": row["id"],
                "manifest": recommended,
                "rubric": allocation.tier,
            })
        component_total = (
            result.recall_obscurity
            + result.task_complexity
            + result.specificity
            + result.distractor_competitiveness
            + result.language_burden
        )
        if result.score != min(100, component_total):
            raise AssertionError(f"Component total mismatch for question {row['id']}")
        assigned = str(row["difficulty"])
        assigned_rank = TIER_ORDER[assigned]
        recommended_rank = TIER_ORDER[recommended]
        score_band_rank = TIER_ORDER[result.recommended]
        audited.append({
            "id": row["id"],
            "number": row.get("number"),
            "assigned": assigned,
            "recommended": recommended,
            "score_band": result.recommended,
            "score": result.score,
            "distance": recommended_rank - assigned_rank,
            "score_band_distance": score_band_rank - assigned_rank,
            "confidence": (
                str(audience_override.get("confidence", allocation.confidence))
                if audience_override else allocation.confidence
            ),
            "category": row["category"],
            "family": question_family(row),
            "question": row["question"],
            "correct": row["correct"],
            "recall_obscurity": result.recall_obscurity,
            "task_complexity": result.task_complexity,
            "specificity": result.specificity,
            "distractor_competitiveness": result.distractor_competitiveness,
            "language_burden": result.language_burden,
            "reasons": (
                str(audience_override["reason"])
                if audience_override
                and audience_override["from"] == "11-17"
                and audience_override["to"] == "Layperson"
                else "; ".join(allocation.basis)
            ),
        })

    summary: list[dict] = []
    for tier in TIER_ORDER:
        segment = [row for row in audited if row["assigned"] == tier]
        scores = [int(row["score"]) for row in segment]
        matches = sum(row["recommended"] == tier for row in segment)
        summary.append({
            "tier": tier,
            "count": len(segment),
            "median": median(scores),
            "p25": round(percentile(scores, 0.25), 1),
            "p75": round(percentile(scores, 0.75), 1),
            "min": min(scores),
            "max": max(scores),
            "agreement_count": matches,
            "agreement_rate": round(matches / len(segment), 4),
            "two_tier_mismatches": sum(abs(int(row["distance"])) == 2 for row in segment),
        })

    medians = {row["tier"]: float(row["median"]) for row in summary}
    monotonic = medians["Layperson"] < medians["Deacon"] < medians["Pastor"]
    minimum_gap = min(
        medians["Deacon"] - medians["Layperson"],
        medians["Pastor"] - medians["Deacon"],
    )
    confusion = Counter((row["assigned"], row["recommended"]) for row in audited)
    family_mix = Counter((row["assigned"], row["family"]) for row in audited)
    category_mix = Counter((row["category"], row["assigned"]) for row in audited)
    minimum_category_tier_pool = min(
        category_mix[category, tier]
        for category in {row["category"] for row in audited}
        for tier in TIER_ORDER
    )
    review_queue = sorted(
        (row for row in audited if row["assigned"] != row["recommended"]),
        key=lambda row: (abs(int(row["distance"])), row["confidence"] == "high", abs(int(row["score"]) - 47)),
        reverse=True,
    )
    score_band_review_queue = sorted(
        (row for row in audited if row["assigned"] != row["score_band"]),
        key=lambda row: (
            abs(int(row["score_band_distance"])),
            abs(int(row["score"]) - 55),
        ),
        reverse=True,
    )
    result = {
        "bank": str(args.bank),
        "adult_question_count": len(adults),
        "rubric_version": "content-difficulty-v2",
        "thresholds": {"Layperson": "0-42", "Deacon": "43-67", "Pastor": "68-100"},
        "strictly_increasing_medians": monotonic,
        "minimum_adjacent_median_gap": minimum_gap,
        "minimum_category_tier_pool": minimum_category_tier_pool,
        "summary": summary,
        "confusion": [
            {"assigned": assigned, "recommended": recommended, "count": count}
            for (assigned, recommended), count in sorted(confusion.items())
        ],
        "family_mix": [
            {"assigned": assigned, "family": family, "count": count}
            for (assigned, family), count in sorted(family_mix.items())
        ],
        "mismatch_count": len(review_queue),
        "mismatch_rate": round(len(review_queue) / len(audited), 4),
        "score_band_disagreement_count": len(score_band_review_queue),
        "score_band_disagreement_rate": round(
            len(score_band_review_queue) / len(audited), 4
        ),
        "two_tier_score_band_disagreement_count": sum(
            abs(int(row["score_band_distance"])) == 2 for row in audited
        ),
        "allocation_drift_count": len(allocation_drift),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    fieldnames = list(audited[0])
    with (args.output_dir / "all_questions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(audited)
    with (args.output_dir / "review_queue.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(review_queue)
    with (args.output_dir / "score_band_review_queue.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(score_band_review_queue)

    print(json.dumps(result, indent=2))
    print(f"Review queue: {args.output_dir / 'review_queue.csv'}")
    print(f"Score-band review queue: {args.output_dir / 'score_band_review_queue.csv'}")
    if args.enforce and (
        not monotonic
        or minimum_gap < 5
        or review_queue
        or allocation_drift
        or minimum_category_tier_pool < 20
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
