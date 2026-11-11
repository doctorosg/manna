#!/usr/bin/env python3
"""Analyze every adult question and create deterministic difficulty overrides."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from statistics import median

from build_question_bank import calibrated_difficulty
from difficulty_assessment import TIER_ORDER, allocate_difficulty


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BANK = ROOT / "Manna/Resources/manna_questions.json"
DEFAULT_OUTPUT = ROOT / "reports/difficulty_reallocation"
DEFAULT_OVERRIDES = ROOT / "difficulty_overrides.json"
SOURCE_FILES = (
    ROOT / "adams_adult_questions.json",
    ROOT / "manna_questions.json",
    ROOT / "manna_questions_v2.json",
    ROOT / "manna_questions_v3.json",
    ROOT / "manna_questions_v4.json",
)
MINIMUM_CATEGORY_TIER_POOL = 20
PASTOR_FLOOR_FAMILIES = {
    "Book-level cross-reference",
    "Chronology",
    "Connection classification",
    "Doctrine or theological term",
    "Exact completion",
    "Genealogy",
    "Other",
    "Specific-detail recall",
    "Study terminology",
    "Symbolism or interpretation",
    "Verse location/book",
}
LAYPERSON_FLOOR_FAMILIES = {"Direct recall", "Genealogy", "Other"}


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def percentile(values: list[int], p: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * p
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def source_index() -> dict[str, tuple[str, str, str]]:
    result: dict[str, tuple[str, str, str]] = {}
    for path in SOURCE_FILES:
        for question in json.loads(path.read_text(encoding="utf-8")):
            question_id = str(question["id"])
            result.setdefault(
                question_id,
                (
                    path.name,
                    str(question["difficulty"]),
                    calibrated_difficulty(question),
                ),
            )
    return result


def enforce_operational_pool(rows: list[dict]) -> list[dict]:
    adjustments: list[dict] = []
    categories = sorted({row["category"] for row in rows})
    for category in categories:
        category_rows = [row for row in rows if row["category"] == category]
        for target in ("Layperson", "Pastor"):
            shortfall = MINIMUM_CATEGORY_TIER_POOL - sum(
                row["final"] == target for row in category_rows
            )
            if shortfall <= 0:
                continue
            allowed_families = (
                LAYPERSON_FLOOR_FAMILIES if target == "Layperson" else PASTOR_FLOOR_FAMILIES
            )
            candidates = [
                row for row in category_rows
                if row["final"] == "Deacon" and row["family"] in allowed_families
            ]
            if target == "Layperson":
                candidates.sort(key=lambda row: (
                    row["score"],
                    row["before"] != "Layperson",
                    row["number"],
                ))
            else:
                candidates.sort(key=lambda row: (
                    -row["score"],
                    row["before"] != "Pastor",
                    row["number"],
                ))
            if len(candidates) < shortfall:
                raise RuntimeError(
                    f"Cannot maintain {MINIMUM_CATEGORY_TIER_POOL} {target} questions in {category}"
                )
            for row in candidates[:shortfall]:
                previous = row["final"]
                row["final"] = target
                row["confidence"] = "medium"
                row["operational_floor"] = "yes"
                row["basis"] += (
                    f"; selected as the {'easiest' if target == 'Layperson' else 'hardest'} "
                    f"eligible question to preserve a {MINIMUM_CATEGORY_TIER_POOL}-question "
                    f"{category}/{target} gameplay pool"
                )
                adjustments.append({
                    "id": row["id"],
                    "category": category,
                    "from": previous,
                    "to": target,
                    "score": row["score"],
                    "family": row["family"],
                })
    return adjustments


def tier_summary(rows: list[dict], field: str) -> list[dict]:
    result = []
    for tier in TIER_ORDER:
        segment = [row for row in rows if row[field] == tier]
        scores = [int(row["score"]) for row in segment]
        result.append({
            "tier": tier,
            "count": len(segment),
            "median": median(scores),
            "p25": round(percentile(scores, 0.25), 1),
            "p75": round(percentile(scores, 0.75), 1),
            "min": min(scores),
            "max": max(scores),
        })
    return result


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bank", type=Path, default=DEFAULT_BANK)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES)
    args = parser.parse_args()

    bank = json.loads(args.bank.read_text(encoding="utf-8"))
    adults = [question for question in bank if question.get("ageGroup") is None]
    answer_frequencies = Counter(normalized(str(row["correct"])) for row in adults)
    sources = source_index()
    missing_sources = [row["id"] for row in adults if row["id"] not in sources]
    if missing_sources:
        raise RuntimeError(f"Adult questions missing from source files: {missing_sources[:5]}")

    rows: list[dict] = []
    for question in adults:
        answer_key = normalized(str(question["correct"]))
        source_file, source_difficulty, baseline_difficulty = sources[str(question["id"])]
        allocation_input = dict(question)
        allocation_input["difficulty"] = baseline_difficulty
        decision = allocate_difficulty(
            allocation_input, answer_frequencies[answer_key]
        )
        final = decision.tier
        rows.append({
            "id": str(question["id"]),
            "number": int(question["number"]),
            "category": str(question["category"]),
            "source_file": source_file,
            "source_difficulty": source_difficulty,
            "shipping_at_analysis": str(question["difficulty"]),
            "before": baseline_difficulty,
            "suggested": decision.tier,
            "final": final,
            "score": decision.score,
            "confidence": decision.confidence,
            "family": decision.family,
            "answer_frequency": answer_frequencies[answer_key],
            "operational_floor": "no",
            "basis": "; ".join(decision.basis),
            "question": str(question["question"]),
            "correct": str(question["correct"]),
        })

    floor_adjustments = enforce_operational_pool(rows)
    changes = [row for row in rows if row["before"] != row["final"]]
    overrides = [{
        "id": row["id"],
        "from": row["before"],
        "to": row["final"],
        "score": row["score"],
        "confidence": row["confidence"],
        "family": row["family"],
        "operationalFloor": row["operational_floor"] == "yes",
        "reason": row["basis"],
    } for row in changes]

    before_summary = tier_summary(rows, "before")
    after_summary = tier_summary(rows, "final")
    after_medians = [float(row["median"]) for row in after_summary]
    if not after_medians[0] < after_medians[1] < after_medians[2]:
        raise RuntimeError(f"Post-allocation medians do not increase: {after_medians}")

    transition_counts = Counter((row["before"], row["final"]) for row in rows)
    family_counts = Counter((row["family"], row["final"]) for row in rows)
    category_counts = Counter((row["category"], row["final"]) for row in rows)
    for category in sorted({row["category"] for row in rows}):
        for tier in TIER_ORDER:
            if category_counts[category, tier] < MINIMUM_CATEGORY_TIER_POOL:
                raise RuntimeError(f"Insufficient post-allocation pool for {category}/{tier}")

    summary = {
        "rubric_version": "content-difficulty-v2",
        "adult_question_count": len(rows),
        "changed_question_count": len(changes),
        "changed_question_rate": round(len(changes) / len(rows), 4),
        "minimum_category_tier_pool": MINIMUM_CATEGORY_TIER_POOL,
        "operational_floor_adjustment_count": len(floor_adjustments),
        "before": before_summary,
        "after": after_summary,
        "minimum_adjacent_median_gap_after": min(
            after_medians[1] - after_medians[0],
            after_medians[2] - after_medians[1],
        ),
        "transitions": [
            {"before": before, "after": after, "count": count}
            for (before, after), count in sorted(
                transition_counts.items(),
                key=lambda item: (TIER_ORDER[item[0][0]], TIER_ORDER[item[0][1]]),
            )
        ],
        "family_mix_after": [
            {"family": family, "tier": tier, "count": count}
            for (family, tier), count in sorted(family_counts.items())
        ],
        "category_mix_after": [
            {"category": category, "tier": tier, "count": count}
            for (category, tier), count in sorted(
                category_counts.items(),
                key=lambda item: (item[0][0], TIER_ORDER[item[0][1]]),
            )
        ],
        "floor_adjustments": floor_adjustments,
    }
    override_payload = {
        "version": 1,
        "rubricVersion": "content-difficulty-v2",
        "minimumCategoryTierPool": MINIMUM_CATEGORY_TIER_POOL,
        "overrides": overrides,
        "retainedExceptions": [{
            "id": row["id"],
            "tier": row["final"],
            "score": row["score"],
            "family": row["family"],
            "reason": row["basis"],
        } for row in rows if row["operational_floor"] == "yes" and row["before"] == row["final"]],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "all_questions.csv", rows)
    write_csv(args.output_dir / "changes.csv", changes)
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    args.overrides.write_text(
        json.dumps(override_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "adult_questions": len(rows),
        "changes": len(changes),
        "before": before_summary,
        "after": after_summary,
        "minimum_adjacent_median_gap_after": summary["minimum_adjacent_median_gap_after"],
        "floor_adjustments": len(floor_adjustments),
        "overrides": str(args.overrides),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
