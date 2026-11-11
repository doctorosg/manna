# Manna adult difficulty assessment

The adult bank uses a deterministic two-layer allocation:

1. A label-independent 0–100 content score measures recall obscurity, task
   complexity, specificity, distractor competitiveness, and language burden.
2. Task-family rules account for difficulty that word count cannot capture. Exact
   cross-references, original-language vocabulary, Church Father attribution,
   connection classification, and academic biblical studies are Pastor tasks even
   when their prompts are short.

The current advisory score bands are:

- Layperson: 0–42
- Deacon: 43–67
- Pastor: 68–100

The assigned tier may intentionally differ from the raw score band when a task-family
rule or the documented category game-size floor applies. These are traceable
exceptions, not unexplained audit failures.

## Rebuild and audit

Run the complete deterministic workflow from the repository root:

```bash
python3 scripts/plan_difficulty_reallocation.py
python3 scripts/build_question_bank.py
python3 scripts/validate_question_bank.py
python3 scripts/audit_difficulty_levels.py --enforce
python3 scripts/build_difficulty_reallocation_report.py
```

`difficulty_overrides.json` freezes every changed adult label by stable question ID.
The bank builder rejects stale `from` labels, child targets, duplicate IDs, and
orphaned overrides. The final audit fails if tier medians stop increasing, the
minimum adjacent median gap falls below five points, a category-tier pool falls below
20 questions, or the shipping bank drifts from the frozen allocation.

## Outputs

- `reports/difficulty_reallocation/all_questions.csv` contains all 40,020 adult
  decisions.
- `reports/difficulty_reallocation/changes.csv` contains every changed label.
- `reports/difficulty_reallocation/summary.json` contains the before/after statistics,
  transitions, family mix, category pools, and operational-floor placements.
- `reports/difficulty_reallocation/difficulty_reallocation.ipynb` independently
  reconciles the persisted outputs.
- `reports/difficulty_reallocation/difficulty_reallocation_report.html` is the
  self-contained stakeholder report.
- `reports/difficulty_audit/score_band_review_queue.csv` lists advisory score-band
  exceptions for periodic editorial review.
- `reports/difficulty_audit/review_queue.csv` must remain empty after a successful
  enforced audit; it records manifest allocation mismatches.

## Empirical calibration

This system estimates content difficulty; it does not measure player performance.
Once enough privacy-safe outcomes exist, retain stable question IDs and analyze
first-attempt correctness with a Rasch/1PL model or shrinkage-adjusted correct rates.
The content model can remain the cold-start prior for new questions while observed
performance becomes the primary calibration layer.
