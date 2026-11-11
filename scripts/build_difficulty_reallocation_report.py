#!/usr/bin/env python3
"""Build the source-linked portable report for the adult difficulty reallocation."""

from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REALLOCATION_DIR = ROOT / "reports/difficulty_reallocation"
AUDIT_DIR = ROOT / "reports/difficulty_audit"
TIER_ORDER = {"Layperson": 0, "Deacon": 1, "Pastor": 2}


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
    """Return executable SQLite that exactly reproduces a bounded dataset."""
    if not rows:
        raise ValueError("Report datasets may not be empty")
    columns = list(rows[0])
    selects: list[str] = []
    for index, row in enumerate(rows):
        values = []
        for column in columns:
            alias = f' AS "{column}"' if index == 0 else ""
            values.append(f"{sql_literal(row[column])}{alias}")
        selects.append("SELECT " + ", ".join(values))
    return "\nUNION ALL\n".join(selects)


def representative_changes(rows: list[dict[str, str]]) -> list[dict]:
    """Return a deterministic, bounded sample spanning every changed direction."""
    directions = [
        ("Layperson", "Deacon"),
        ("Layperson", "Pastor"),
        ("Deacon", "Layperson"),
        ("Deacon", "Pastor"),
        ("Pastor", "Layperson"),
        ("Pastor", "Deacon"),
    ]
    selected: list[dict] = []
    for before, after in directions:
        candidates = [
            row for row in rows
            if row["before"] == before
            and row["final"] == after
            and row["operational_floor"] == "no"
        ]
        candidates.sort(
            key=lambda row: (
                -abs(int(row["score"]) - (42 if after == "Layperson" else 68)),
                row["family"],
                int(row["number"]),
            )
        )
        used_families: set[str] = set()
        for row in candidates:
            if row["family"] in used_families:
                continue
            selected.append({
                "number": int(row["number"]),
                "before": before,
                "after": after,
                "score": int(row["score"]),
                "family": row["family"],
                "question": row["question"],
                "basis": row["basis"],
            })
            used_families.add(row["family"])
            if len(used_families) == 2:
                break
    return selected


def main() -> int:
    reallocation = json.loads(
        (REALLOCATION_DIR / "summary.json").read_text(encoding="utf-8")
    )
    audit = json.loads((AUDIT_DIR / "summary.json").read_text(encoding="utf-8"))
    changes = read_csv(REALLOCATION_DIR / "changes.csv")
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )

    if reallocation["changed_question_count"] != len(changes):
        raise AssertionError("changes.csv does not reconcile to summary.json")
    if audit["allocation_drift_count"] != 0 or audit["mismatch_count"] != 0:
        raise AssertionError("shipping bank does not match the approved allocation")

    unchanged = reallocation["adult_question_count"] - len(changes)
    before_gap = min(
        reallocation["before"][index + 1]["median"]
        - reallocation["before"][index]["median"]
        for index in range(2)
    )

    metrics = [{
        "adult_questions": reallocation["adult_question_count"],
        "changed_questions": len(changes),
        "changed_rate": reallocation["changed_question_rate"],
        "median_gap_before": before_gap,
        "median_gap_after": reallocation["minimum_adjacent_median_gap_after"],
        "minimum_category_pool": reallocation["minimum_category_tier_pool"],
        "allocation_drift": audit["allocation_drift_count"],
    }]

    tier_stage = []
    for stage in ("Before", "After"):
        for row in reallocation[stage.lower()]:
            tier_stage.append({
                "stage": stage,
                "tier": row["tier"],
                "count": row["count"],
                "median": row["median"],
                "p25": row["p25"],
                "p75": row["p75"],
            })

    transitions = sorted(
        reallocation["transitions"],
        key=lambda row: (TIER_ORDER[row["before"]], TIER_ORDER[row["after"]]),
    )
    transition_table = [
        {
            "before": row["before"],
            "after": row["after"],
            "count": row["count"],
            "share_of_adults": row["count"] / reallocation["adult_question_count"],
        }
        for row in transitions
    ]
    tier_table = []
    for stage in ("Before", "After"):
        for row in reallocation[stage.lower()]:
            tier_table.append({"stage": stage, **row})

    category_pools = sorted(
        reallocation["category_mix_after"],
        key=lambda row: (row["count"], row["category"], TIER_ORDER[row["tier"]]),
    )
    rubric_components = [
        {"component": "Recall obscurity", "maximum": 30, "signal": "Familiarity of the book, figure, event, or source knowledge"},
        {"component": "Task complexity", "maximum": 25, "signal": "Direct recall versus chronology, exact text, cross-reference, or interpretation"},
        {"component": "Specificity", "maximum": 20, "signal": "Verse precision, names, numbers, places, dates, and exact details"},
        {"component": "Distractor competitiveness", "maximum": 15, "signal": "Plausibility and similarity of the incorrect choices"},
        {"component": "Language burden", "maximum": 10, "signal": "Length, uncommon vocabulary, and specialist terminology"},
    ]
    allocation_rules = [
        {"tier": "Layperson", "score_band": "0–42", "typical_task": "Familiar, one-step direct recall", "hard_rules": "Familiar introductory stories and figures"},
        {"tier": "Deacon", "score_band": "43–67", "typical_task": "Book-level links, completion, genealogy, doctrine, or specific details", "hard_rules": "Intermediate tasks stay here unless specialist precision is required"},
        {"tier": "Pastor", "score_band": "68–100", "typical_task": "Exact references, original languages, Church Fathers, academic study, or advanced interpretation", "hard_rules": "Specialist task families override a deceptively low text score"},
    ]
    examples = representative_changes(changes)

    datasets = {
        "metrics": metrics,
        "tier_stage": tier_stage,
        "transitions": transition_table,
        "tier_table": tier_table,
        "category_pools": category_pools,
        "rubric_components": rubric_components,
        "allocation_rules": allocation_rules,
        "examples": examples,
    }
    source_descriptions = {
        "metrics": "Reconciles headline counts and progression checks from the reallocation and final audit summaries.",
        "tier_stage": "Reproduces the before-and-after tier distribution statistics.",
        "transitions": "Reproduces all nine before-to-after difficulty transitions.",
        "tier_table": "Reproduces exact before-and-after quartiles and ranges.",
        "category_pools": "Reproduces the final category-by-tier pool sizes.",
        "rubric_components": "Reproduces the five components of the deterministic 0–100 content score.",
        "allocation_rules": "Summarizes the score bands and task-family guardrails used by the allocator.",
        "examples": "Provides a deterministic sample of changed questions spanning every transition direction.",
    }
    query_sources = []
    with sqlite3.connect(":memory:") as connection:
        for dataset_id, rows in datasets.items():
            sql = rows_to_sql(rows)
            reproduced = connection.execute(sql).fetchall()
            if len(reproduced) != len(rows):
                raise AssertionError(f"SQL reproduction failed for {dataset_id}")
            query_sources.append({
                "id": f"{dataset_id}_sql",
                "query": {
                    "engine": "sqlite",
                    "language": "sql",
                    "sql": sql,
                    "description": source_descriptions[dataset_id],
                    "executed_at": generated_at,
                },
            })

    cards = []
    for card_id, label, field, fmt, description in (
        ("adult_count", "Adult questions assessed", "adult_questions", "compact", "The complete adult bank; children's questions were excluded."),
        ("changed_count", "Questions reallocated", "changed_questions", "compact", "Records whose adult difficulty label changed."),
        ("changed_rate", "Adult bank reallocated", "changed_rate", "percent", "Changed records divided by all adult records."),
        ("median_gap", "Minimum median gap after", "median_gap_after", "number", "The smaller adjacent difference among final tier medians."),
        ("minimum_pool", "Smallest category-tier pool", "minimum_category_pool", "number", "Minimum final pool across every category and adult tier."),
        ("allocation_drift", "Unresolved allocation drift", "allocation_drift", "number", "Shipping labels that differ from the frozen allocation."),
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
            "title": "Manna adult difficulty reallocation audit",
            "description": "Complete content-based assessment and reallocation of Layperson, Deacon, and Pastor questions.",
            "generatedAt": generated_at,
            "cards": cards,
            "charts": [
                {
                    "id": "tier_medians",
                    "title": "Median content score before and after reallocation",
                    "subtitle": "Higher scores indicate more demanding biblical-knowledge tasks.",
                    "headerMarkdown": "### Tier separation is materially stronger\n\nThe minimum adjacent median gap increased from **7** to **22 points**.",
                    "intent": "comparison",
                    "question": "Did the reallocation create a clearer Layperson-to-Deacon-to-Pastor progression?",
                    "rationale": "Grouped bars compare each tier's median before and after the same allocation change.",
                    "comparisonContext": {"grain": "adult question", "unit": "points on a 0–100 content score"},
                    "type": "bar",
                    "dataset": "tier_stage",
                    "sourceId": "tier_stage_sql",
                    "encodings": {
                        "x": {"field": "tier", "type": "ordinal", "label": "Difficulty tier"},
                        "y": {"field": "median", "type": "quantitative", "label": "Median content score", "unit": "points"},
                        "color": {"field": "stage", "type": "nominal", "label": "Allocation stage"},
                        "tooltip": [
                            {"field": "count", "type": "quantitative", "label": "Questions"},
                            {"field": "p25", "type": "quantitative", "label": "25th percentile"},
                            {"field": "p75", "type": "quantitative", "label": "75th percentile"},
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
                    "title": "Final tier composition by original tier",
                    "subtitle": "Each bar totals the questions originally assigned to that tier.",
                    "headerMarkdown": "### Most labels stayed in place, but both upward and downward corrections were material\n\n**30,229 of 40,020 questions (75.5%)** retained their original tier.",
                    "intent": "composition",
                    "question": "Where did questions move from each original tier?",
                    "rationale": "A normalized stacked bar makes transition shares comparable despite unequal original tier sizes.",
                    "comparisonContext": {"grain": "adult question", "denominator": "all adult questions within each original tier", "unit": "share of original tier"},
                    "type": "stackedBar100",
                    "dataset": "transitions",
                    "sourceId": "transitions_sql",
                    "encodings": {
                        "x": {"field": "before", "type": "ordinal", "label": "Original tier"},
                        "y": {"field": "count", "type": "quantitative", "label": "Questions"},
                        "color": {"field": "after", "type": "nominal", "label": "Final tier"},
                    },
                    "legend": {"position": "bottom", "sort": "spec", "title": "Final tier"},
                    "palette": {"kind": "categorical", "name": "difficulty-tier"},
                    "settings": {"sort": "none", "showPercent": True},
                    "surface": {"surface": "card", "viewMode": "both"},
                },
            ],
            "tables": [
                {
                    "id": "tier_details",
                    "title": "Tier distribution before and after",
                    "headerMarkdown": "### Exact distribution statistics\n\nCounts, quartiles, and ranges provide the context behind the median chart.",
                    "dataset": "tier_table",
                    "sourceId": "tier_table_sql",
                    "defaultSort": {"field": "median", "direction": "asc"},
                    "columns": [
                        {"field": "stage", "label": "Stage", "type": "text"},
                        {"field": "tier", "label": "Tier", "type": "text"},
                        {"field": "count", "label": "Questions", "format": "compact"},
                        {"field": "median", "label": "Median", "format": "number"},
                        {"field": "p25", "label": "P25", "format": "number"},
                        {"field": "p75", "label": "P75", "format": "number"},
                        {"field": "min", "label": "Minimum", "format": "number"},
                        {"field": "max", "label": "Maximum", "format": "number"},
                    ],
                },
                {
                    "id": "transition_details",
                    "title": "All allocation transitions",
                    "headerMarkdown": "### Transition counts reconcile to all 40,020 adult questions\n\nDiagonal rows are unchanged; off-diagonal rows are reallocations.",
                    "dataset": "transitions",
                    "sourceId": "transitions_sql",
                    "defaultSort": {"field": "count", "direction": "desc"},
                    "columns": [
                        {"field": "before", "label": "Original tier", "type": "text"},
                        {"field": "after", "label": "Final tier", "type": "text"},
                        {"field": "count", "label": "Questions", "format": "compact"},
                        {"field": "share_of_adults", "label": "Share of adult bank", "format": "percent"},
                    ],
                },
                {
                    "id": "category_pools",
                    "title": "Final category-by-tier pool sizes",
                    "headerMarkdown": "### Every adult category supports a 20-question game in every tier\n\nThe smallest category-tier pool is **20**, matching the largest selectable game length.",
                    "dataset": "category_pools",
                    "sourceId": "category_pools_sql",
                    "defaultSort": {"field": "count", "direction": "asc"},
                    "columns": [
                        {"field": "category", "label": "Category", "type": "text"},
                        {"field": "tier", "label": "Tier", "type": "text"},
                        {"field": "count", "label": "Questions", "format": "compact"},
                    ],
                },
                {
                    "id": "rubric_components",
                    "title": "Content score components",
                    "headerMarkdown": "### Five components produce a reproducible 0–100 score\n\nThe task-family allocator then applies explicit specialist guardrails.",
                    "dataset": "rubric_components",
                    "sourceId": "rubric_components_sql",
                    "defaultSort": {"field": "maximum", "direction": "desc"},
                    "columns": [
                        {"field": "component", "label": "Component", "type": "text"},
                        {"field": "maximum", "label": "Maximum", "format": "number"},
                        {"field": "signal", "label": "What raises the score", "type": "text"},
                    ],
                },
                {
                    "id": "allocation_rules",
                    "title": "Allocation rules by tier",
                    "headerMarkdown": "### Scores guide placement; task families prevent false simplicity\n\nA short prompt can still be Pastor-level when it requires Greek, exact references, or academic knowledge.",
                    "dataset": "allocation_rules",
                    "sourceId": "allocation_rules_sql",
                    "defaultSort": {"field": "score_band", "direction": "asc"},
                    "columns": [
                        {"field": "tier", "label": "Tier", "type": "text"},
                        {"field": "score_band", "label": "Score band", "type": "text"},
                        {"field": "typical_task", "label": "Typical task", "type": "text"},
                        {"field": "hard_rules", "label": "Task-family guardrail", "type": "text"},
                    ],
                },
                {
                    "id": "examples",
                    "title": "Representative reallocations",
                    "headerMarkdown": "### Examples span all six movement directions\n\nThis deterministic sample illustrates the rules; the full 9,791-row change log remains in CSV.",
                    "dataset": "examples",
                    "sourceId": "examples_sql",
                    "defaultSort": {"field": "number", "direction": "asc"},
                    "columns": [
                        {"field": "number", "label": "Question #", "format": "number"},
                        {"field": "before", "label": "Before", "type": "text"},
                        {"field": "after", "label": "After", "type": "text"},
                        {"field": "score", "label": "Score", "format": "number"},
                        {"field": "family", "label": "Task family", "type": "text"},
                        {"field": "question", "label": "Question", "type": "text"},
                        {"field": "basis", "label": "Allocation basis", "type": "text"},
                    ],
                },
            ],
            "sources": [
                {"id": "shipping_bank", "label": "Shipping iOS question bank", "path": "Manna/Resources/manna_questions.json"},
                {"id": "android_bank", "label": "Shipping Android question bank", "path": "android/app/src/main/assets/manna_questions.json"},
                {"id": "allocation_manifest", "label": "Frozen difficulty allocation", "path": "difficulty_overrides.json"},
                {"id": "reallocation_summary", "label": "Reallocation summary", "path": "reports/difficulty_reallocation/summary.json"},
                {"id": "audit_summary", "label": "Final allocation audit", "path": "reports/difficulty_audit/summary.json"},
                {"id": "changes_csv", "label": "Complete change log", "path": "reports/difficulty_reallocation/changes.csv"},
                *[
                    {"id": row["id"], "label": row["id"].replace("_", " ").title(), "path": "scripts/build_difficulty_reallocation_report.py"}
                    for row in query_sources
                ],
            ],
            "blocks": [
                {"id": "title", "type": "markdown", "body": "# Manna adult difficulty reallocation audit"},
                {
                    "id": "technical_summary",
                    "type": "markdown",
                    "sourceId": "metrics_sql",
                    "body": "## Technical summary\n\n**Outcome: complete and build-safe.** All **40,020 adult questions** were assessed with a deterministic content rubric and task-family rules. **9,791 questions (24.47%)** were reallocated. Final medians rise **35 → 58 → 80**, the minimum adjacent gap is **22 points**, every category-tier pool contains at least **20 questions**, and the shipping bank has **zero allocation drift** from the frozen manifest.",
                },
                {"id": "metrics", "type": "metric-strip", "cardIds": [card["id"] for card in cards]},
                {
                    "id": "key_findings",
                    "type": "markdown",
                    "sourceId": "transitions_sql",
                    "body": f"## Key findings\n\nThe prior labels were directionally ordered but weakly separated: the original medians were **53, 60, and 78**, leaving only a **7-point** Layperson-to-Deacon gap. The final allocation preserves **{unchanged:,} questions (75.5%)** and changes the remaining **{len(changes):,}**. The largest movements are **3,485 Pastor → Deacon**, **3,154 Deacon → Pastor**, and **1,649 Layperson → Deacon**.",
                },
                {"id": "median_chart", "type": "chart", "chartId": "tier_medians"},
                {
                    "id": "median_readout",
                    "type": "markdown",
                    "sourceId": "tier_stage_sql",
                    "body": "The reallocation lowers the Layperson median by **18 points**, lowers Deacon by **2**, and raises Pastor by **2**. That produces a clearer progression without forcing equal tier sizes. Tier sizes remain content-driven because specialist source material is intentionally concentrated in Pastor.",
                },
                {"id": "transition_chart", "type": "chart", "chartId": "transition_mix"},
                {
                    "id": "transition_readout",
                    "type": "markdown",
                    "sourceId": "transitions_sql",
                    "body": "Movement is not a blanket promotion or demotion. Familiar direct recall moves downward, while exact cross-references, original-language vocabulary, Church Father attribution, academic methods, and advanced interpretation move upward or remain Pastor-level.",
                },
                {"id": "tier_table_block", "type": "table", "tableId": "tier_details"},
                {"id": "transition_table_block", "type": "table", "tableId": "transition_details"},
                {
                    "id": "scope",
                    "type": "markdown",
                    "body": "## Scope, data, and definitions\n\nThe population is every shipping record without an `ageGroup`: **40,020 adult questions** from the five adult source files. Children ages 4–10 and 11–17 are excluded. “Before” is the reproducible calibrated source label, not a mutable prior shipping snapshot. “After” is the deterministic allocator plus a documented operational floor. A reallocation changes only the `difficulty` field; question IDs, numbers, wording, choices, correct answers, explanations, sources, categories, and child records remain unchanged.",
                },
                {"id": "category_pool_block", "type": "table", "tableId": "category_pools"},
                {
                    "id": "methodology",
                    "type": "markdown",
                    "body": "## Methodology\n\nEach item receives a label-independent 0–100 score from recall obscurity, task complexity, specificity, distractor competitiveness, and language burden. The allocator also classifies the requested task. Hard rules place specialist tasks—such as original-language lexicons, exact cross-references, Church Father attribution, connection classification, and academic biblical studies—at Pastor even when short wording yields a lower raw score. Familiar one-step recall can move to Layperson. Ambiguous direct-recall cases use the calibrated source label only as a tie-breaker. Finally, the planner preserves at least 20 questions in each adult category-tier pool so a 20-question category game remains possible. All decisions are frozen by stable question ID in `difficulty_overrides.json`.",
                },
                {"id": "rubric_block", "type": "table", "tableId": "rubric_components"},
                {"id": "rules_block", "type": "table", "tableId": "allocation_rules"},
                {
                    "id": "limitations",
                    "type": "markdown",
                    "sourceId": "metrics_sql",
                    "body": "## Limitations, uncertainty, and robustness\n\n**Confidence is high for reproducibility and population ordering; medium for individual pedagogical placement.** The planner is deterministic, its unit-test anchors pass, the final audit reports **zero manifest mismatch and zero allocation drift**, and all summary counts reconcile to question-level outputs. However, this remains an expert-system estimate, not a psychometric measurement. It cannot observe player age, church background, denomination, reading ability, ambiguity, or actual response rates. The raw score bands are therefore advisory; **3,151 final questions (7.87%)** sit outside their nominal score band because task-family or operational rules deliberately override the raw score. Sixteen cross two raw score bands. Those cases are traceable, not unexplained errors.",
                },
                {"id": "examples_block", "type": "table", "tableId": "examples"},
                {
                    "id": "recommendations",
                    "type": "markdown",
                    "body": "## Recommended next steps\n\n1. Keep `difficulty_overrides.json` under version control and run both the bank validator and `audit_difficulty_levels.py --enforce` on every content build.\n2. Treat `score_band_review_queue.csv` as a periodic editorial review list, with priority on the 16 two-band exceptions and the 40 operational-floor placements.\n3. Collect privacy-safe first-attempt outcomes by stable question ID. After adequate exposure, estimate empirical item difficulty with a Rasch/1PL model or shrinkage-adjusted correct rates.\n4. Calibrate tier targets using observed player success rather than changing the deterministic content rules ad hoc. Keep the content score as the cold-start prior for new questions.",
                },
                {
                    "id": "further_questions",
                    "type": "markdown",
                    "body": "## Further questions\n\n- What first-attempt correct-rate range should define a good Layperson, Deacon, and Pastor experience?\n- Should difficulty be calibrated separately by biblical category or test format?\n- How much item exposure is required before player outcomes can override the cold-start content allocation?\n- Should reading complexity and Bible-knowledge difficulty be shown as separate dimensions in editorial tooling?",
                },
            ],
        },
        "snapshot": {
            "version": 1,
            "generatedAt": generated_at,
            "status": "ready",
            "datasets": datasets,
        },
        "sources": query_sources,
        "package_info": {
            "originUrl": "artifact://manna/difficulty-reallocation-audit",
            "controls": {"edit": False, "refresh": False},
        },
    }

    output = REALLOCATION_DIR / "artifact.json"
    output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
