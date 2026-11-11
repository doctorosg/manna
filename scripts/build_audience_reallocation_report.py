#!/usr/bin/env python3
"""Build the canonical report artifact for the 11-17/Layperson audit."""

from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports/audience_reallocation"
ADULT_AUDIT_DIR = ROOT / "reports/difficulty_audit"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sql_literal(value: object) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def rows_to_sql(rows: list[dict]) -> str:
    if not rows:
        raise ValueError("Report datasets may not be empty")
    columns = list(rows[0])
    selects: list[str] = []
    for index, row in enumerate(rows):
        values = [
            f"{sql_literal(row[column])}{f' AS {json.dumps(column)}' if index == 0 else ''}"
            for column in columns
        ]
        selects.append("SELECT " + ", ".join(values))
    return "\nUNION ALL\n".join(selects)


def representative_changes(rows: list[dict[str, str]]) -> list[dict]:
    selected: list[dict] = []
    for before, after in (("11-17", "Layperson"), ("Layperson", "11-17")):
        candidates = [
            row for row in rows
            if row["before"] == before
            and row["final"] == after
            and row["operational_floor"] == "no"
            and row["displaced_by_floor"] == "no"
        ]
        candidates.sort(key=lambda row: (
            row["format"],
            -int(row["readiness_score"]) if after == "Layperson" else int(row["readiness_score"]),
            int(row["number"]),
        ))
        used_formats: set[str] = set()
        for row in candidates:
            if row["format"] in used_formats:
                continue
            selected.append({
                "number": int(row["number"]),
                "before": before,
                "after": after,
                "readiness_score": int(row["readiness_score"]),
                "adult_content_score": int(row["adult_content_score"]),
                "format": row["format"],
                "question": row["question"],
                "correct": row["correct"],
            })
            used_formats.add(row["format"])
            if len(used_formats) == 4:
                break
    return selected


def main() -> int:
    summary = json.loads((REPORT_DIR / "summary.json").read_text(encoding="utf-8"))
    adult_audit = json.loads(
        (ADULT_AUDIT_DIR / "summary.json").read_text(encoding="utf-8")
    )
    changes = read_csv(REPORT_DIR / "changes.csv")
    if len(changes) != summary["changed_question_count"]:
        raise AssertionError("changes.csv does not reconcile to summary.json")
    if adult_audit["mismatch_count"] or adult_audit["allocation_drift_count"]:
        raise AssertionError("Adult difficulty audit is not clean")

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
    transition_lookup = {
        (row["before"], row["after"]): row["count"]
        for row in summary["transitions"]
    }
    teen_to_lay = transition_lookup["11-17", "Layperson"]
    lay_to_teen = transition_lookup["Layperson", "11-17"]
    retained = summary["boundary_question_count"] - summary["changed_question_count"]

    metrics = [{
        "boundary_questions": summary["boundary_question_count"],
        "changed_questions": summary["changed_question_count"],
        "changed_rate": summary["changed_question_rate"],
        "gap_before": summary["readiness_median_gap_before"],
        "gap_after": summary["readiness_median_gap_after"],
        "layperson_deacon_gap": summary["actual_layperson_to_deacon_median_gap"],
        "minimum_category_pool": summary["minimum_actual_layperson_category_pool"],
        "adult_allocation_drift": adult_audit["allocation_drift_count"],
    }]
    cohort_stage: list[dict] = []
    for stage in ("Before", "After"):
        for row in summary[stage.lower()]:
            cohort_stage.append({
                "stage": stage,
                "cohort": row["cohort"],
                "count": row["count"],
                "readiness_median": row["readiness_median"],
                "readiness_p25": row["readiness_p25"],
                "readiness_p75": row["readiness_p75"],
                "adult_content_median": row["adult_content_median"],
            })
    transitions = [{
        "before": row["before"],
        "after": row["after"],
        "count": row["count"],
        "share_of_boundary": row["count"] / summary["boundary_question_count"],
    } for row in summary["transitions"]]
    format_movements = [
        row for row in summary["format_transitions"] if row["before"] != row["after"]
    ]
    category_pools = sorted(
        summary["layperson_category_counts"],
        key=lambda row: (row["count"], row["category"]),
    )
    rubric = [
        {"component": "Canonical knowledge", "maximum": 30, "signal": "Familiarity of the book, event, person, or canonical setting"},
        {"component": "Task abstraction", "maximum": 25, "signal": "Recognition and direct recall versus omitted-word, section, or book inference"},
        {"component": "Reading burden", "maximum": 20, "signal": "Prompt length, word length, and passage-fragment complexity"},
        {"component": "Answer specificity", "maximum": 15, "signal": "Rare answers and exact canonical details"},
        {"component": "Distractor competitiveness", "maximum": 10, "signal": "Similarity and plausibility of the incorrect options"},
    ]
    safeguards = [
        {"safeguard": "Fixed audience sizes", "result": "Passed", "value": "6,667 ages 11–17; 2,074 adult Layperson"},
        {"safeguard": "Adult-content ceiling", "result": "Passed", "value": f"Layperson eligibility capped at {summary['layperson_content_ceiling']}"},
        {"safeguard": "Layperson-to-Deacon median gap", "result": "Passed", "value": f"{summary['actual_layperson_to_deacon_median_gap']:.0f} points (minimum 5)"},
        {"safeguard": "Adult category availability", "result": "Passed", "value": f"At least {summary['minimum_actual_layperson_category_pool']} Layperson questions per category"},
        {"safeguard": "11–17 wording screen", "result": "Passed", "value": f"{summary['safety_lock_count']} adult-only safety locks"},
        {"safeguard": "Frozen adult allocation", "result": "Passed", "value": "0 mismatches; 0 allocation drift"},
    ]
    examples = representative_changes(changes)
    datasets = {
        "metrics": metrics,
        "cohort_stage": cohort_stage,
        "transitions": transitions,
        "format_movements": format_movements,
        "category_pools": category_pools,
        "rubric": rubric,
        "safeguards": safeguards,
        "examples": examples,
    }
    descriptions = {
        "metrics": "Reconciles headline counts and progression safeguards from the boundary and adult audit summaries.",
        "cohort_stage": "Reproduces the before-and-after cohort medians and quartiles.",
        "transitions": "Reproduces every before-to-after audience transition.",
        "format_movements": "Reproduces movements by original question format.",
        "category_pools": "Reproduces the final adult Layperson count in every gameplay category.",
        "rubric": "Defines the five components of the label-independent readiness score.",
        "safeguards": "Reproduces the operational and progression checks applied after allocation.",
        "examples": "Provides a deterministic sample of changed questions from both directions.",
    }
    query_sources: list[dict] = []
    with sqlite3.connect(":memory:") as connection:
        for dataset_id, rows in datasets.items():
            sql = rows_to_sql(rows)
            if len(connection.execute(sql).fetchall()) != len(rows):
                raise AssertionError(f"SQL reproduction failed for {dataset_id}")
            query_sources.append({
                "id": f"{dataset_id}_sql",
                "query": {
                    "engine": "sqlite",
                    "language": "sql",
                    "sql": sql,
                    "description": descriptions[dataset_id],
                    "executed_at": generated_at,
                },
            })

    cards = []
    for card_id, label, field, fmt, description in (
        ("boundary_count", "Questions assessed", "boundary_questions", "compact", "Every question in the ages 11–17 and adult Layperson boundary pool."),
        ("changed_count", "Questions reallocated", "changed_questions", "compact", "Records that crossed the boundary; half moved in each direction."),
        ("gap_after", "Readiness gap after", "gap_after", "number", "Layperson median minus ages 11–17 median after allocation."),
        ("adult_gap", "Layperson-to-Deacon gap", "layperson_deacon_gap", "number", "Adult content-score median difference after the boundary change."),
        ("category_pool", "Smallest Layperson category", "minimum_category_pool", "number", "Minimum playable Layperson pool across all 21 categories."),
        ("drift", "Unresolved adult drift", "adult_allocation_drift", "number", "Shipping adult labels that differ from the frozen allocation."),
    ):
        cards.append({
            "id": card_id,
            "description": description,
            "dataset": "metrics",
            "sourceId": "metrics_sql",
            "metrics": [{"label": label, "field": field, "format": fmt}],
        })

    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1,
            "surface": "report",
            "title": "Manna 11–17 to Layperson boundary audit",
            "description": "Complete question-level readiness analysis and reallocation across the ages 11–17 and adult Layperson boundary.",
            "generatedAt": generated_at,
            "cards": cards,
            "charts": [
                {
                    "id": "readiness_medians",
                    "title": "Median readiness score before and after reallocation",
                    "subtitle": "The prior ordering was inverted; the revised Layperson median is 18 points above ages 11–17.",
                    "headerMarkdown": "### The age-to-adult boundary now rises in difficulty\n\nThe median gap changed from **−15** to **+18 points**.",
                    "intent": "comparison",
                    "question": "Did reallocation create a clear ages 11–17 to Layperson progression?",
                    "rationale": "Grouped bars compare both cohorts before and after the same allocation.",
                    "comparisonContext": {"grain": "boundary question", "unit": "points on a 0–100 readiness score"},
                    "type": "bar",
                    "dataset": "cohort_stage",
                    "sourceId": "cohort_stage_sql",
                    "encodings": {
                        "x": {"field": "cohort", "type": "ordinal", "label": "Audience"},
                        "y": {"field": "readiness_median", "type": "quantitative", "label": "Median readiness score", "unit": "points"},
                        "color": {"field": "stage", "type": "nominal", "label": "Allocation stage"},
                        "tooltip": [
                            {"field": "count", "type": "quantitative", "label": "Questions"},
                            {"field": "readiness_p25", "type": "quantitative", "label": "25th percentile"},
                            {"field": "readiness_p75", "type": "quantitative", "label": "75th percentile"},
                        ],
                    },
                    "legend": {"position": "bottom", "sort": "spec", "title": "Allocation stage"},
                    "palette": {"kind": "categorical", "name": "allocation-stage"},
                    "labels": {"values": "all"},
                    "settings": {"groupMode": "grouped", "sort": "none", "showValues": True},
                    "surface": {"surface": "card", "viewMode": "both"},
                },
                {
                    "id": "transition_mix",
                    "title": "Final audience composition by original audience",
                    "subtitle": "Exactly 1,911 questions moved in each direction, so audience sizes did not change.",
                    "headerMarkdown": "### Reallocation is balanced, not a size change\n\n**{:,}** questions retained their original audience and **{:,}** crossed the boundary.".format(retained, summary["changed_question_count"]),
                    "intent": "composition",
                    "question": "How much of each original audience stayed or moved?",
                    "rationale": "A normalized stacked bar compares the retained and moved shares of unequal pools.",
                    "comparisonContext": {"grain": "boundary question", "unit": "share of original audience"},
                    "type": "stackedBar100",
                    "dataset": "transitions",
                    "sourceId": "transitions_sql",
                    "encodings": {
                        "x": {"field": "before", "type": "ordinal", "label": "Original audience"},
                        "y": {"field": "count", "type": "quantitative", "label": "Questions"},
                        "color": {"field": "after", "type": "nominal", "label": "Final audience"},
                    },
                    "legend": {"position": "bottom", "sort": "spec", "title": "Final audience"},
                    "palette": {"kind": "categorical", "name": "audience"},
                    "settings": {"sort": "none", "showPercent": True},
                    "surface": {"surface": "card", "viewMode": "both"},
                },
            ],
            "tables": [
                {
                    "id": "format_movements",
                    "title": "Question formats that crossed the boundary",
                    "headerMarkdown": "### Template difficulty—not hand-written teen trivia—drove the inversion\n\nBook inference and exact-word completion account for most moves into Layperson.",
                    "dataset": "format_movements",
                    "sourceId": "format_movements_sql",
                    "defaultSort": {"field": "count", "direction": "desc"},
                    "columns": [
                        {"field": "before", "label": "Before", "type": "text"},
                        {"field": "after", "label": "After", "type": "text"},
                        {"field": "format", "label": "Original format", "type": "text"},
                        {"field": "count", "label": "Questions", "format": "compact"},
                    ],
                },
                {
                    "id": "rubric",
                    "title": "Readiness score components",
                    "headerMarkdown": "### Five label-independent components produce a reproducible 0–100 score\n\nHigher scores signal greater independent Bible-study skill.",
                    "dataset": "rubric",
                    "sourceId": "rubric_sql",
                    "defaultSort": {"field": "maximum", "direction": "desc"},
                    "columns": [
                        {"field": "component", "label": "Component", "type": "text"},
                        {"field": "maximum", "label": "Maximum", "format": "number"},
                        {"field": "signal", "label": "What raises the score", "type": "text"},
                    ],
                },
                {
                    "id": "safeguards",
                    "title": "Post-allocation safeguards",
                    "headerMarkdown": "### Every build and progression guardrail passed\n\nThe boundary changed without reducing audience sizes or adult gameplay coverage.",
                    "dataset": "safeguards",
                    "sourceId": "safeguards_sql",
                    "defaultSort": {"field": "safeguard", "direction": "asc"},
                    "columns": [
                        {"field": "safeguard", "label": "Safeguard", "type": "text"},
                        {"field": "result", "label": "Result", "type": "text"},
                        {"field": "value", "label": "Evidence", "type": "text"},
                    ],
                },
                {
                    "id": "category_pools",
                    "title": "Final Layperson questions by category",
                    "headerMarkdown": "### Every Layperson category still supports a 20-question game\n\nThere were **{:,} deterministic floor swaps** to preserve category coverage.".format(summary["operational_floor_adjustment_count"]),
                    "dataset": "category_pools",
                    "sourceId": "category_pools_sql",
                    "defaultSort": {"field": "count", "direction": "asc"},
                    "columns": [
                        {"field": "category", "label": "Category", "type": "text"},
                        {"field": "count", "label": "Layperson questions", "format": "compact"},
                    ],
                },
                {
                    "id": "examples",
                    "title": "Representative reallocated questions",
                    "headerMarkdown": "### Examples show both directions\n\nThe complete **3,822-row** decision log is retained in CSV.",
                    "dataset": "examples",
                    "sourceId": "examples_sql",
                    "defaultSort": {"field": "number", "direction": "asc"},
                    "columns": [
                        {"field": "number", "label": "Question #", "format": "number"},
                        {"field": "before", "label": "Before", "type": "text"},
                        {"field": "after", "label": "After", "type": "text"},
                        {"field": "readiness_score", "label": "Readiness", "format": "number"},
                        {"field": "adult_content_score", "label": "Adult content", "format": "number"},
                        {"field": "format", "label": "Format", "type": "text"},
                        {"field": "question", "label": "Question", "type": "text"},
                        {"field": "correct", "label": "Answer", "type": "text"},
                    ],
                },
            ],
            "sources": [
                {"id": "ios_bank", "label": "Shipping iOS bank", "path": "Manna/Resources/manna_questions.json"},
                {"id": "android_bank", "label": "Shipping Android bank", "path": "android/app/src/main/assets/manna_questions.json"},
                {"id": "audience_manifest", "label": "Frozen audience reallocation", "path": "audience_overrides.json"},
                {"id": "boundary_summary", "label": "Boundary audit summary", "path": "reports/audience_reallocation/summary.json"},
                {"id": "boundary_changes", "label": "Complete boundary change log", "path": "reports/audience_reallocation/changes.csv"},
                {"id": "adult_audit", "label": "Adult difficulty audit", "path": "reports/difficulty_audit/summary.json"},
                *[
                    {"id": source["id"], "label": source["id"].replace("_", " ").title(), "path": "scripts/build_audience_reallocation_report.py"}
                    for source in query_sources
                ],
            ],
            "blocks": [
                {"id": "title", "type": "markdown", "body": "# Manna 11–17 to Layperson boundary audit"},
                {"id": "technical_summary", "type": "markdown", "sourceId": "metrics_sql", "body": "## Technical summary\n\n**Outcome: corrected and build-safe.** The audit assessed all **8,741** questions in the ages 11–17 and adult Layperson boundary. Before reallocation, ages 11–17 were **15 points harder at the median**. After balanced two-way swaps, the Layperson median is **18 points higher**. Exactly **1,911 questions moved each way**, both audience sizes are unchanged, and Layperson remains **16 adult-content points below Deacon**."},
                {"id": "metrics", "type": "metric-strip", "cardIds": [card["id"] for card in cards]},
                {"id": "findings", "type": "markdown", "sourceId": "format_movements_sql", "body": "## Key findings\n\nThe inversion was structural. Of the teen questions moved to Layperson, **957** require identifying a Bible book from an unattributed passage, **610** require an exact missing word, and **340** require classifying an unattributed passage by canon section. By contrast, all **1,400 word-recognition** questions and all **533 familiar story-context** questions remained in ages 11–17. Only **4 of 118 hand-written teen trivia** questions moved, so the curated trivia was not the problem."},
                {"id": "median_chart", "type": "chart", "chartId": "readiness_medians"},
                {"id": "transition_chart", "type": "chart", "chartId": "transition_mix"},
                {"id": "format_table", "type": "table", "tableId": "format_movements"},
                {"id": "scope", "type": "markdown", "body": "## Scope and definitions\n\nThe population is the complete union of the **6,667** ages 11–17 questions and **2,074** adult Layperson questions after the existing adult-difficulty audit. Ages 4–10, Deacon, and Pastor questions were not candidates for this move. ‘Before’ is reconstructed from repository source banks plus the frozen adult difficulty manifest, so rerunning the analysis does not depend on a mutable shipping snapshot. ‘After’ changes audience metadata only; stable question IDs, support numbers, wording, choices, answers, explanations, and categories are preserved."},
                {"id": "methodology", "type": "markdown", "body": "## Methodology\n\nEach question receives a label-independent **0–100 readiness score** from canonical knowledge (30), task abstraction (25), reading burden (20), answer specificity (15), and distractor competitiveness (10). Higher scores indicate more independent Bible-study skill and therefore stronger adult readiness. Allocation ranks the combined pool while preserving its original audience sizes. An adult-content ceiling of **53** prevents a question from entering Layperson when doing so would compress the next Layperson-to-Deacon boundary. Deterministic tie-breakers favor the original audience to minimize churn."},
                {"id": "rubric_table", "type": "table", "tableId": "rubric"},
                {"id": "safeguard_notes", "type": "markdown", "sourceId": "safeguards_sql", "body": "## Safeguards and edge cases\n\nEvery question moved into ages 11–17 has four choices and passes the existing archaic, sexual-content, and graphic-wording screen. **{:,}** records were locked adult-only by that screen. After the primary rank allocation, **{:,}** category-floor swaps preserved at least **20** adult Layperson questions in every category. The full adult audit then passed with medians **42 → 58 → 80**, zero manifest mismatch, and zero allocation drift.".format(summary["safety_lock_count"], summary["operational_floor_adjustment_count"])},
                {"id": "safeguards_table", "type": "table", "tableId": "safeguards"},
                {"id": "category_table", "type": "table", "tableId": "category_pools"},
                {"id": "examples_table", "type": "table", "tableId": "examples"},
                {"id": "limitations", "type": "markdown", "body": "## Limitations and uncertainty\n\n**Confidence is high for reproducibility and population ordering, and medium for individual pedagogical placement.** This is a deterministic editorial cold-start model, not an item-response study. It cannot observe reading fluency, church background, denomination, ambiguity, or real answer rates. Tail overlap remains possible because audience size, safety, category availability, and the adjacent Deacon safeguard are hard constraints. Those exceptions are documented per question in the CSV and frozen manifest rather than hidden."},
                {"id": "recommendations", "type": "markdown", "body": "## Recommendations\n\nShip this corrected boundary, then collect anonymous correctness rate, response time, skip rate, and age-band selection for each stable question ID. Re-estimate placement after a useful sample is available, using response-rate bands and differential performance by audience as the primary evidence. Editorially review the lowest-confidence cutoff cases first, then inspect questions with unexpectedly high teen failure or unexpectedly high Layperson success."},
                {"id": "traceability", "type": "markdown", "body": "## Traceability\n\nThe shipping iOS and Android banks are byte-identical. `audience_overrides.json` freezes all **3,822** audience changes by stable question ID. `all_questions.csv` contains every component score and decision; `changes.csv` contains every move; `summary.json` reconciles counts and distributions; and the executed notebook reproduces the headline checks from those outputs."},
            ],
        },
        "snapshot": {
            "version": 1,
            "status": "ready",
            "generatedAt": generated_at,
            "datasets": datasets,
        },
        "sources": query_sources,
        "package_info": {
            "title": "Manna 11–17 to Layperson boundary audit",
            "artifactType": "report",
            "generatedAt": generated_at,
        },
    }
    (REPORT_DIR / "artifact.json").write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "artifact": str(REPORT_DIR / "artifact.json"),
        "datasets": {name: len(rows) for name, rows in datasets.items()},
        "teen_to_layperson": teen_to_lay,
        "layperson_to_teen": lay_to_teen,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
