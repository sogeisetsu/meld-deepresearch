# Example 1 — embodied-AI landscape (T1)

Protocol: [`README.md`](README.md). Baseline: frozen SenseNova example 1
(`test/baseline/`, gitignored). Skill under test: branch
`feat/sensenova-live-compare`, git `7c17f7f`, `SKILL.md`
`ca6aa8c53b971e0e…` (see `run-meta.json`).

## Task

> 帮我对具身智能行业做个调研，生成一份专业的行业调研报告

## Run round 1

- Output: `test/runs/example1/round1/` (gitignored). `report.md` 161 lines / 13
  headings; four artifacts + `.work/`.
- tier `normal`, genre `panorama`; 23/25 fetch attempts (7 failed), 16 distinct
  sources, 35 claims, 8 `refute` claims, 7 observations.

## Deterministic checks (independently re-run by the orchestrator)

| Check | Result |
|---|---|
| Gate ① `check_evidence.py --plan` | `{"ok": true, "errors": [], "warnings": []}` exit 0 |
| Gate ② `render_citations.py` | `{"ok": true, "citation_count": 16, "observation_count": 7, "orphans": [], "uncited": []}` exit 0 |
| `dedupe_sources.py` | `{"ok": true, "sources": 16, "duplicates_merged": 0}` |
| link sample (8 of 16) | 8/8 reachable |
| baseline artifact | `report.md` **and** `report.html` contain **0** `http` URLs and no reference list → citations non-resolvable in the frozen artifact |

## Blind judge passes (axes A,B,C,D,E,G; F excluded; max 30)

Identity was hidden; only order varied between passes.

| pass | order | Report A | Report B | total A | total B |
|---|---|---|---|---|---|
| 1 | A=baseline · B=meld | baseline | meld | 15 | 28 |
| 2 | A=meld · B=baseline | meld | baseline | 28 | 13 |
| 3 | A=baseline · B=meld | baseline | meld | 16 | 27 |

Pass-1 per-axis:

| axis | baseline | meld |
|---|---|---|
| A Coverage | 5 | 5 |
| B Depth | 3 | 5 |
| C Factual support | 1 | 5 |
| D Citation quality | 0 | 5 |
| E Instruction-following | 5 | 5 |
| G Process discipline | 1 | 3 |

Pass-1 notes: baseline = broad and well-formed (product parameter tables, cost
breakdown, investment advice) but no resolvable references, internally
contradictory share figures (tier-1 shares sum >100%), no unknowns/uncertainty.
meld = every figure traceable to a dated, graded citation; contradictions and
unknowns handled explicitly; method reproducible — but weaker on product-level
parameter tables and overseas vendor coverage, and no charts (F, excluded).

## Verdict

Median across the 3 blind passes (F excluded, max 30):

| axis | baseline (median) | meld (median) |
|---|---|---|
| A Coverage | 4 | 5 |
| B Depth | 3 | 5 |
| C Factual support | 1 | 5 |
| D Citation quality | 1 | 5 |
| E Instruction-following | 4 | 5 |
| G Process discipline | 1 | 3 |
| **total** | **14** | **28** |

Per-pass totals — baseline **15 / 13 / 16**, meld **28 / 28 / 27** (range ≤ 2).

**PASS** — meld ≥ baseline on every in-scope axis and 28 ≥ 14 overall. No skill
change is required for example 1.

Two independent passes verified meld's links by fetching (8/8 reachable; 4
checked content-level) and confirmed the baseline has no resolvable reference
list. The decisive spread is on C/D/G (enforced evidence and citations), not on
prose; the baseline keeps a real edge on product-level parameter tables, which
meld could later absorb without touching any constraint.

## Skill changes

None (round 1 already not-inferior). No skill file was modified in this round.
