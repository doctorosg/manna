# Manna 11–17 to Layperson boundary audit

This directory contains the complete, reproducible 8,741-question boundary
analysis. The shipping result swaps 1,911 questions in each direction while
preserving 6,667 ages 11–17 questions and 2,074 adult Layperson questions.

## Reproduce

Run from the repository root:

```bash
PYTHONPATH=scripts python3 scripts/plan_audience_reallocation.py
PYTHONPATH=scripts python3 scripts/build_question_bank.py
PYTHONPATH=scripts python3 scripts/validate_question_bank.py
PYTHONPATH=scripts python3 scripts/audit_difficulty_levels.py --enforce
python3 scripts/build_audience_reallocation_notebook.py
python3 scripts/build_audience_reallocation_report.py
```

## Outputs

- `summary.json`: before/after distributions, transitions, safeguards, and
  category coverage.
- `all_questions.csv`: all component scores and allocation decisions.
- `changes.csv`: all 3,822 questions that crossed the boundary.
- `audience_reallocation.ipynb`: executed, dependency-free reconciliation
  notebook.
- `artifact.json`: validated canonical Data Analytics report payload.
- `/audience_overrides.json`: frozen shipping changes keyed by stable question
  ID.

The readiness score is an editorial cold-start model. It is reproducible and
useful for population ordering, but individual placements should eventually be
calibrated against correctness rate, response time, and skip rate by audience.
