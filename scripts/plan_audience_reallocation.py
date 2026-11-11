#!/usr/bin/env python3
"""Audit and reallocate the 11-17/Layperson boundary deterministically."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path
from statistics import median

from audience_readiness import RUBRIC_VERSION, assess_readiness, normalized_answer
from build_question_bank import (
    AUDIENCE_OVERRIDES,
    DEFAULT_SOURCES,
    DIFFICULTY_OVERRIDES,
    build,
    load_difficulty_overrides,
)
from generate_children_questions import ARCHAIC_RE, GRAPHIC_RE, SEXUAL_RE


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "reports/audience_reallocation"
TARGET_COUNTS = {"11-17": 6_667, "Layperson": 2_074}
MINIMUM_LAYPERSON_CATEGORY_POOL = 20
MINIMUM_DEACON_MEDIAN_GAP = 5
REALLOCATED_TEEN_FORMAT = "reallocated-direct"


def percentile(values: list[int], p: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * p
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def cohort_summary(rows: list[dict], field: str) -> list[dict]:
    result: list[dict] = []
    for cohort in ("11-17", "Layperson"):
        segment = [row for row in rows if row[field] == cohort]
        readiness = [int(row["readiness_score"]) for row in segment]
        adult_content = [int(row["adult_content_score"]) for row in segment]
        result.append({
            "cohort": cohort,
            "count": len(segment),
            "readiness_median": median(readiness),
            "readiness_p25": round(percentile(readiness, 0.25), 1),
            "readiness_p75": round(percentile(readiness, 0.75), 1),
            "readiness_min": min(readiness),
            "readiness_max": max(readiness),
            "adult_content_median": median(adult_content),
            "adult_content_p25": round(percentile(adult_content, 0.25), 1),
            "adult_content_p75": round(percentile(adult_content, 0.75), 1),
            "adult_content_min": min(adult_content),
            "adult_content_max": max(adult_content),
        })
    return result


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def source_files_by_id() -> dict[str, str]:
    result: dict[str, str] = {}
    for path in DEFAULT_SOURCES:
        for question in json.loads(path.read_text(encoding="utf-8")):
            result.setdefault(str(question["id"]), path.name)
    return result


def assignment_rank(row: dict) -> tuple:
    """Hardest readiness first, with stable churn-minimizing tie breaks."""
    return (
        -int(row["readiness_score"]),
        row["before"] != "Layperson",
        int(row["number"]),
        str(row["id"]),
    )


def safety_violation(question: dict) -> str | None:
    combined = f"{question.get('question', '')} {question.get('explanation', '')}"
    if ARCHAIC_RE.search(combined):
        return "archaic wording"
    if SEXUAL_RE.search(combined):
        return "age-sensitive sexual content"
    if GRAPHIC_RE.search(combined):
        return "graphic wording"
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overrides", type=Path, default=AUDIENCE_OVERRIDES)
    parser.add_argument(
        "--difficulty-overrides", type=Path, default=DIFFICULTY_OVERRIDES
    )
    args = parser.parse_args()

    difficulty_overrides = load_difficulty_overrides(args.difficulty_overrides)
    baseline, rejected = build(
        DEFAULT_SOURCES,
        difficulty_overrides=difficulty_overrides,
        audience_overrides={},
        persist_registry=False,
    )
    pool = [
        question for question in baseline
        if question.get("ageGroup") == "11-17"
        or (
            question.get("ageGroup") is None
            and question.get("difficulty") == "Layperson"
        )
    ]
    actual_targets = Counter(
        "11-17" if row.get("ageGroup") == "11-17" else "Layperson"
        for row in pool
    )
    if dict(actual_targets) != TARGET_COUNTS:
        raise RuntimeError(
            f"Expected boundary counts {TARGET_COUNTS}, found {dict(actual_targets)}"
        )

    deacon_scores = [
        assess_readiness(question).adult_content_score
        for question in baseline
        if question.get("ageGroup") is None
        and question.get("difficulty") == "Deacon"
    ]
    deacon_median = float(median(deacon_scores))
    layperson_content_ceiling = math.floor(
        deacon_median - MINIMUM_DEACON_MEDIAN_GAP
    )
    answer_frequencies = Counter(
        normalized_answer(str(question["correct"])) for question in pool
    )
    sources = source_files_by_id()

    rows: list[dict] = []
    for question in pool:
        question_id = str(question["id"])
        before = "11-17" if question.get("ageGroup") == "11-17" else "Layperson"
        assessment = assess_readiness(
            question,
            answer_frequencies[normalized_answer(str(question["correct"]))],
        )
        component_total = (
            assessment.canonical_knowledge
            + assessment.task_abstraction
            + assessment.reading_burden
            + assessment.answer_specificity
            + assessment.distractor_competitiveness
        )
        if component_total != assessment.score:
            raise AssertionError(f"Component total mismatch for {question_id}")
        violation = safety_violation(question)
        rows.append({
            "id": question_id,
            "number": int(question["number"]),
            "category": str(question["category"]),
            "source_file": sources.get(question_id, "unknown"),
            "before": before,
            "final": "",
            "changed": "",
            "readiness_score": assessment.score,
            "adult_content_score": assessment.adult_content_score,
            "format": assessment.format,
            "family": assessment.family,
            "canonical_knowledge": assessment.canonical_knowledge,
            "task_abstraction": assessment.task_abstraction,
            "reading_burden": assessment.reading_burden,
            "answer_specificity": assessment.answer_specificity,
            "distractor_competitiveness": assessment.distractor_competitiveness,
            "layperson_content_eligible": (
                "yes"
                if assessment.adult_content_score <= layperson_content_ceiling
                else "no"
            ),
            "safety_lock": "yes" if violation else "no",
            "safety_reason": violation or "",
            "operational_floor": "no",
            "displaced_by_floor": "no",
            "confidence": "",
            "basis": "; ".join(assessment.reasons),
            "question": str(question["question"]),
            "correct": str(question["correct"]),
        })

    selected = {
        index for index, row in enumerate(rows) if row["safety_lock"] == "yes"
    }
    eligible = [
        index for index, row in enumerate(rows)
        if index not in selected and row["layperson_content_eligible"] == "yes"
    ]
    eligible.sort(key=lambda index: assignment_rank(rows[index]))
    remaining_slots = TARGET_COUNTS["Layperson"] - len(selected)
    if remaining_slots < 0 or len(eligible) < remaining_slots:
        raise RuntimeError("Insufficient eligible questions for the Layperson target")
    selected.update(eligible[:remaining_slots])

    category_counts = Counter(rows[index]["category"] for index in selected)
    floor_adjustments: list[dict] = []
    categories = sorted({str(row["category"]) for row in rows})
    for category in categories:
        while category_counts[category] < MINIMUM_LAYPERSON_CATEGORY_POOL:
            incoming_candidates = [
                index for index, row in enumerate(rows)
                if index not in selected
                and row["category"] == category
                and row["layperson_content_eligible"] == "yes"
            ]
            incoming_candidates.sort(key=lambda index: assignment_rank(rows[index]))
            if not incoming_candidates:
                raise RuntimeError(
                    f"Cannot preserve {MINIMUM_LAYPERSON_CATEGORY_POOL} Layperson "
                    f"questions in {category}"
                )
            incoming = incoming_candidates[0]
            outgoing_candidates = [
                index for index in selected
                if rows[index]["safety_lock"] == "no"
                and rows[index]["operational_floor"] == "no"
                and category_counts[rows[index]["category"]]
                > MINIMUM_LAYPERSON_CATEGORY_POOL
            ]
            outgoing_candidates.sort(key=lambda index: (
                int(rows[index]["readiness_score"]),
                rows[index]["before"] == "Layperson",
                -int(rows[index]["number"]),
                str(rows[index]["id"]),
            ))
            if not outgoing_candidates:
                raise RuntimeError("Cannot displace a Layperson question for a category floor")
            outgoing = outgoing_candidates[0]
            selected.remove(outgoing)
            selected.add(incoming)
            category_counts[rows[outgoing]["category"]] -= 1
            category_counts[category] += 1
            rows[incoming]["operational_floor"] = "yes"
            rows[outgoing]["displaced_by_floor"] = "yes"
            floor_adjustments.append({
                "incoming_id": rows[incoming]["id"],
                "incoming_category": category,
                "incoming_score": rows[incoming]["readiness_score"],
                "outgoing_id": rows[outgoing]["id"],
                "outgoing_category": rows[outgoing]["category"],
                "outgoing_score": rows[outgoing]["readiness_score"],
            })

    if len(selected) != TARGET_COUNTS["Layperson"]:
        raise AssertionError("Layperson selection count drifted")
    if min(category_counts.values()) < MINIMUM_LAYPERSON_CATEGORY_POOL:
        raise AssertionError("Layperson category floor was not preserved")

    regular_selected = [
        row for index, row in enumerate(rows)
        if index in selected
        and row["safety_lock"] == "no"
        and row["operational_floor"] == "no"
    ]
    regular_cutoff = min(int(row["readiness_score"]) for row in regular_selected)
    for index, row in enumerate(rows):
        row["final"] = "Layperson" if index in selected else "11-17"
        row["changed"] = "yes" if row["before"] != row["final"] else "no"
        if row["safety_lock"] == "yes":
            row["confidence"] = "high"
            assignment_reason = "kept adult because it fails the 11-17 wording screen"
        elif row["operational_floor"] == "yes":
            row["confidence"] = "medium"
            assignment_reason = (
                f"selected to preserve the {MINIMUM_LAYPERSON_CATEGORY_POOL}-question "
                f"Layperson category floor"
            )
        elif row["displaced_by_floor"] == "yes":
            row["confidence"] = "medium"
            assignment_reason = "displaced by a higher-priority category-floor selection"
        elif row["layperson_content_eligible"] == "no":
            row["confidence"] = "high"
            assignment_reason = (
                f"not moved into Layperson because adult content score exceeds "
                f"the {layperson_content_ceiling}-point ceiling"
            )
        else:
            distance = abs(int(row["readiness_score"]) - regular_cutoff)
            row["confidence"] = (
                "high" if distance >= 8 else "medium" if distance >= 4 else "low"
            )
            assignment_reason = (
                f"ranked {'above' if row['final'] == 'Layperson' else 'below'} "
                f"the operational readiness cutoff ({regular_cutoff})"
            )
        row["basis"] = "; ".join(
            item for item in (row["basis"], assignment_reason) if item
        )

    changes = [row for row in rows if row["changed"] == "yes"]
    transitions = Counter((row["before"], row["final"]) for row in rows)
    format_transitions = Counter(
        (row["before"], row["final"], row["format"]) for row in rows
    )
    before_summary = cohort_summary(rows, "before")
    after_summary = cohort_summary(rows, "final")
    before_medians = {
        row["cohort"]: float(row["readiness_median"]) for row in before_summary
    }
    after_medians = {
        row["cohort"]: float(row["readiness_median"]) for row in after_summary
    }
    if not after_medians["11-17"] < after_medians["Layperson"]:
        raise RuntimeError(f"Post-allocation medians do not increase: {after_medians}")
    after_lay_content_median = next(
        float(row["adult_content_median"])
        for row in after_summary if row["cohort"] == "Layperson"
    )
    if deacon_median - after_lay_content_median < MINIMUM_DEACON_MEDIAN_GAP:
        raise RuntimeError(
            "Layperson-to-Deacon adult-content median gap is below the safeguard"
        )

    final_counts = Counter(row["final"] for row in rows)
    if dict(final_counts) != TARGET_COUNTS:
        raise AssertionError(f"Final cohort count drift: {dict(final_counts)}")

    summary = {
        "rubric_version": RUBRIC_VERSION,
        "boundary_question_count": len(rows),
        "target_counts": TARGET_COUNTS,
        "changed_question_count": len(changes),
        "changed_question_rate": round(len(changes) / len(rows), 4),
        "layperson_content_ceiling": layperson_content_ceiling,
        "deacon_content_median": deacon_median,
        "minimum_layperson_to_deacon_median_gap": MINIMUM_DEACON_MEDIAN_GAP,
        "actual_layperson_to_deacon_median_gap": (
            deacon_median - after_lay_content_median
        ),
        "operational_readiness_cutoff": regular_cutoff,
        "minimum_layperson_category_pool": MINIMUM_LAYPERSON_CATEGORY_POOL,
        "minimum_actual_layperson_category_pool": min(category_counts.values()),
        "safety_lock_count": sum(row["safety_lock"] == "yes" for row in rows),
        "operational_floor_adjustment_count": len(floor_adjustments),
        "rejected_source_rows": dict(rejected),
        "before": before_summary,
        "after": after_summary,
        "readiness_median_gap_before": (
            before_medians["Layperson"] - before_medians["11-17"]
        ),
        "readiness_median_gap_after": (
            after_medians["Layperson"] - after_medians["11-17"]
        ),
        "transitions": [
            {"before": before, "after": after, "count": count}
            for (before, after), count in sorted(transitions.items())
        ],
        "format_transitions": [
            {"before": before, "after": after, "format": format_name, "count": count}
            for (before, after, format_name), count in sorted(format_transitions.items())
        ],
        "layperson_category_counts": [
            {"category": category, "count": category_counts[category]}
            for category in categories
        ],
        "floor_adjustments": floor_adjustments,
    }
    override_payload = {
        "version": 1,
        "rubricVersion": RUBRIC_VERSION,
        "targetCounts": TARGET_COUNTS,
        "laypersonContentCeiling": layperson_content_ceiling,
        "operationalReadinessCutoff": regular_cutoff,
        "minimumLaypersonCategoryPool": MINIMUM_LAYPERSON_CATEGORY_POOL,
        "overrides": [{
            "id": row["id"],
            "from": row["before"],
            "to": row["final"],
            "score": row["readiness_score"],
            "adultContentScore": row["adult_content_score"],
            "confidence": row["confidence"],
            "sourceFormat": None if row["format"] == "adult-standard" else row["format"],
            **(
                {"targetFormat": REALLOCATED_TEEN_FORMAT}
                if row["final"] == "11-17"
                else {}
            ),
            "operationalFloor": row["operational_floor"] == "yes",
            "displacedByFloor": row["displaced_by_floor"] == "yes",
            "reason": row["basis"],
        } for row in changes],
        "retainedExceptions": [{
            "id": row["id"],
            "cohort": row["final"],
            "score": row["readiness_score"],
            "reason": row["basis"],
        } for row in rows if row["safety_lock"] == "yes"],
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
        "boundary_questions": len(rows),
        "changes": len(changes),
        "before": before_summary,
        "after": after_summary,
        "readiness_median_gap_before": summary["readiness_median_gap_before"],
        "readiness_median_gap_after": summary["readiness_median_gap_after"],
        "layperson_to_deacon_median_gap": summary[
            "actual_layperson_to_deacon_median_gap"
        ],
        "floor_adjustments": len(floor_adjustments),
        "safety_locks": summary["safety_lock_count"],
        "overrides": str(args.overrides),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
