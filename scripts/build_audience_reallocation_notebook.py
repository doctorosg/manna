#!/usr/bin/env python3
"""Create and execute a dependency-free audit notebook with the stdlib."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports/audience_reallocation/audience_reallocation.ipynb"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(True)}


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(True),
    }


def main() -> int:
    cells = [
        markdown(
            "# Manna 11–17 to Layperson boundary audit\n\n"
            "Reproducible checks for the complete 8,741-question boundary analysis. "
            "This notebook uses only Python's standard library and reads the generated "
            "question-level outputs; it does not contain a second copy of the allocator."
        ),
        code(
            "from pathlib import Path\n"
            "import csv, json, statistics\n\n"
            "ROOT = Path.cwd().resolve()\n"
            "while ROOT != ROOT.parent and not (ROOT / 'reports/audience_reallocation/summary.json').exists():\n"
            "    ROOT = ROOT.parent\n"
            "REPORT = ROOT / 'reports/audience_reallocation'\n"
            "summary = json.loads((REPORT / 'summary.json').read_text(encoding='utf-8'))\n"
            "with (REPORT / 'all_questions.csv').open(encoding='utf-8', newline='') as handle:\n"
            "    rows = list(csv.DictReader(handle))\n"
            "with (REPORT / 'changes.csv').open(encoding='utf-8', newline='') as handle:\n"
            "    changes = list(csv.DictReader(handle))\n"
            "print(f\"Loaded {len(rows):,} boundary questions and {len(changes):,} changes.\")\n"
        ),
        markdown("## Before and after distribution"),
        code(
            "print('Stage  Audience    Count  Readiness median  P25  P75  Adult-content median')\n"
            "for stage in ('before', 'after'):\n"
            "    for item in summary[stage]:\n"
            "        print(f\"{stage.title():<6} {item['cohort']:<11} {item['count']:>5,} \"\n"
            "              f\"{item['readiness_median']:>17} {item['readiness_p25']:>4} \"\n"
            "              f\"{item['readiness_p75']:>4} {item['adult_content_median']:>21}\")\n"
            "print(f\"\\nReadiness median gap: {summary['readiness_median_gap_before']:+.0f} before, \"\n"
            "      f\"{summary['readiness_median_gap_after']:+.0f} after.\")\n"
        ),
        markdown("## Reallocation matrix"),
        code(
            "print('Before      After        Count')\n"
            "for item in summary['transitions']:\n"
            "    print(f\"{item['before']:<11} {item['after']:<11} {item['count']:>5,}\")\n"
        ),
        markdown("## Formats that crossed the boundary"),
        code(
            "print('Before      After        Format                 Count')\n"
            "for item in summary['format_transitions']:\n"
            "    if item['before'] != item['after']:\n"
            "        print(f\"{item['before']:<11} {item['after']:<11} \"\n"
            "              f\"{item['format']:<22} {item['count']:>5,}\")\n"
        ),
        markdown("## Reconciliation and guardrails"),
        code(
            "assert len(rows) == summary['boundary_question_count'] == 8741\n"
            "assert len(changes) == summary['changed_question_count'] == 3822\n"
            "final_counts = {cohort: sum(row['final'] == cohort for row in rows)\n"
            "                for cohort in ('11-17', 'Layperson')}\n"
            "assert final_counts == {'11-17': 6667, 'Layperson': 2074}\n"
            "assert summary['readiness_median_gap_before'] < 0\n"
            "assert summary['readiness_median_gap_after'] >= 5\n"
            "assert summary['actual_layperson_to_deacon_median_gap'] >= 5\n"
            "assert summary['minimum_actual_layperson_category_pool'] >= 20\n"
            "assert sum(row['before'] == '11-17' and row['final'] == 'Layperson' for row in rows) == 1911\n"
            "assert sum(row['before'] == 'Layperson' and row['final'] == '11-17' for row in rows) == 1911\n"
            "print('PASS — counts reconcile, progression is monotonic, and every safeguard holds.')\n"
        ),
        markdown(
            "## Interpretation\n\n"
            "The original boundary was inverted because passage-inference templates in "
            "the teen pool demanded more independent canonical knowledge than most adult "
            "Layperson questions. The revised allocation fixes the population ordering while "
            "preserving audience sizes, four-choice teen records, safety screens, stable IDs, "
            "and all 21 adult gameplay categories. Individual placement remains an editorial "
            "estimate until response-rate data is available."
        ),
    ]

    namespace: dict = {"__name__": "__notebook__"}
    execution_count = 0
    for cell in cells:
        if cell["cell_type"] != "code":
            continue
        execution_count += 1
        stream = io.StringIO()
        try:
            with contextlib.redirect_stdout(stream):
                exec("".join(cell["source"]), namespace)
        except Exception as error:
            cell["execution_count"] = execution_count
            cell["outputs"] = [{
                "output_type": "error",
                "ename": type(error).__name__,
                "evalue": str(error),
                "traceback": [],
            }]
            raise
        cell["execution_count"] = execution_count
        output = stream.getvalue()
        if output:
            cell["outputs"] = [{
                "output_type": "stream",
                "name": "stdout",
                "text": output.splitlines(True),
            }]

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    OUTPUT.write_text(
        json.dumps(notebook, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Executed and wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
