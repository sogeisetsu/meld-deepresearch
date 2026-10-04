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

Median across the 3 blind passes, axes A–E (F excluded; max 25):

| axis | baseline (median) | meld (median) |
|---|---|---|
| A Coverage | 4 | 5 |
| B Depth | 3 | 5 |
| C Factual support | 1 | 5 |
| D Citation quality | 1 | 5 |
| E Instruction-following | 4 | 5 |
| **A–E total** | **13** | **25** |

Per-pass deliverable-visible totals (A–E,G) — baseline 15/13/16, meld 28/28/27 (range ≤ 2).

**PASS** — meld ≥ baseline on every in-scope axis. Two independent passes verified
meld's links by fetching (8/8 reachable; 4 checked content-level) and confirmed
the baseline has no resolvable reference list. The decisive spread is on C/D
(enforced evidence and citations), not on prose; the baseline keeps a real edge on
product-level parameter tables, which meld could later absorb without touching any
constraint.

## G axis (supplementary, full process artifacts)

The 3 passes above scored G from the deliverable only (cap 3) because the judge was
shown the reports without the process directory. A dedicated independent pass then
scored G per the rubric's intent — deliverable-visible (cap 3) for the baseline,
full process artifacts for the meld run:

| instance | G | basis |
|---|---|---|
| T1 baseline | **2** | deliverable only: all `[n]` markers dangling, no reference list / method / unknowns |
| T1 meld r1 (`ca6aa8c5…`) | **4** | plan.json, 4 axis sub_reports, gate-① failure + fix recorded, fetch-log, refutation + unknowns; only `o7` had a re-runnable command |

Full objective surface **A–E,G** (max 30): meld **29** vs baseline **15**; meld ≥
baseline on every axis.

## Round 2 (current skill: `main` `86b472d`, `SKILL.md` `e409856b…`)

Re-run on the post-merge skill (which now ships `read_table.py`). Output:
`test/runs/example1/round2/` (109 lines). tier `normal`, 20/25 fetches, 15 sources,
5 observations, 9 `refute` claims. Deterministic (orchestrator re-run): gate ① `ok`;
gate ② `ok`, 15 citations, 5 observations, 0 orphan/uncited.

| pass | order | total A | total B |
|---|---|---|---|
| 1 | A=baseline · B=meld2 | 13 | 28 |
| 2 | A=meld2 · B=baseline | 28 | 15 |
| 3 | A=baseline · B=meld2 | 13 | 28 |

Per-axis medians across the three round-2 passes (A–E,G; F excluded; max 30):

| axis | baseline (median) | meld2 (median) |
|---|---|---|
| A Coverage | 4 | 5 |
| B Depth | 2 | 5 |
| C Factual support | 1 | 5 |
| D Citation quality | 0 | 5 |
| E Instruction-following | 4 | 5 |
| G Process discipline | 1 | 3 |
| **total** | **12** | **28** |

Per-pass totals — meld2 28/28/28, baseline 13/15/13.

**PASS** — meld2 ≥ baseline on every axis (28 ≥ 12) on the **current** skill
(`main` `86b472d`, `SKILL.md` `e409856b…`). Compared with round 1 the picture is
unchanged: the baseline's citations remain unresolvable (D 0–1) and meld's
evidence chain is intact.

## Skill changes

None (round 1 already not-inferior). No skill file was modified in this round.
