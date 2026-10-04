# SenseNova live comparison — protocol & progress

Status: **protocol v1** (2026-10-04). Baseline frozen in `test/baseline/`
(see `PROVENANCE.md`). This file is the "口径" (operationalization) referenced by
the goal; scores/changes/evidence for each round are appended under
`progress/`.

## 1. Objective

Make `meld-deepresearch` score **not inferior** to the two shipped
SenseNova-Skills examples on the *same task*, measured on the repository's
existing 7-axis rubric (`../README.md` §2) with **axis F excluded** (chart/HTML
loss is an acknowledged, accepted trade-off).

## 2. The two tasks (verbatim)

**T1 — embodied-AI landscape** (`examples/embodied-ai-deep-research/README_CN.md`):

> 帮我对具身智能行业做个调研，生成一份专业的行业调研报告

**T2 — employee-performance analysis** (`examples/employee-performance-analysis/README_CN.md`):

> 请根据我 10 个风电事业部月度绩效考核表格文件，生成一份正式员工绩效分析
> docx 报告，报告建议分为 5–6 个章节，篇幅约 14 页。报告需从月份、岗位、员工
> 三个层级分析总体绩效、趋势变化、绩效等级分布、不合格率、岗位差异、高低绩效
> 员工和连续进步员工。请必须加入图表展示关键结论。报告格式正式、结构清晰、
> 语言专业简洁，不只罗列数据，要解释数据背后的管理含义。

**Adaptation (documented):** T2's literal prompt names the proprietary skill
`sn-da-excel-workflow`. That clause is dropped so the skill under test can be
triggered; the underlying task is unchanged. The "must add charts" clause is
F-axis and excluded.

## 3. Frozen baseline (read-only)

- `test/baseline/example1-embodied-ai/extracted/具身智能行业调研/` — `report.md`
  (609 lines, 11 sections) + `report.html` + 5 `.jpg`.
- `test/baseline/example2-employee-performance/output.docx.txt` (extracted text, 5
  chapters) + `output_extracted/…/…html` + 8 `.png`.
- Baseline axes are scored from the deliverable only (no SenseNova process trace
  exists for these examples).

## 4. Skill version pinning

Every run writes `run-meta.json` recording: repo git SHA, branch, `SKILL.md`
sha256, and sha256 of every `scripts/*.py`. A run is only valid if its
`run-meta.json` matches the SHA the round claims to test.

**Execution mechanism:** runs are *path-based* — the executing subagent reads the
branch's `skills/meld-deepresearch/SKILL.md` and resolves `references/…` /
`scripts/…` relative to that directory. This deliberately avoids touching the
installed skill at `~/.config/opencode/skills/meld-deepresearch` (a
confirmation-gated config operation). If a run must use the *installed* skill,
that requires an explicit plan + user confirmation first.

## 5. Verdict rule ("not inferior")

Let `S` = the axes scorable for the baseline on that task (subset of
`{A,B,C,D,E,G}`; `F` always excluded).

Per example, using the **median across 3 blind judge passes** per axis:

- **PASS** iff `Σ_{a∈S} meld[a] ≥ Σ_{a∈S} base[a]` **and** `∀a∈S: meld[a] ≥ base[a]`.
- A baseline axis that cannot be grounded is marked `n/a` and excluded from `S`
  (an unobservable cannot be "lower than").
- Report per-axis scores, both totals, and the trial range.

## 6. Axis operationalization

Generic definitions: `../README.md` §2. Task-specific grounding below.

### T1 (web research) — scorable `{A,B,C,D,E,G}`

| Axis | Grounded meaning for T1 | 5 looks like |
|---|---|---|
| A | Covers the landscape dimensions the example advertises: market size/growth, players/share, funding, cost structure, roadmap/outlook — or names what it could not cover | all present, gaps named |
| B | Cross-source synthesis; causal/forecast reasoning; not a link list | multi-layer, quantified forecasts with basis |
| C | Every figure/claim traceable to a source actually opened; snippets never carry a claim; contradictions surfaced | each claim backed; refutation present |
| D | Citations resolve, non-duplicate, accurate; sampled links reachable | 0 orphans, 0 unresolved, links live |
| E | Chinese; "professional industry research report" shape; scoped to the request | reading like the baseline's shape |
| G | Process trace (plan.json, sub_reports, evidence.json, gate output, run-log); refutation non-zero; budget/stop honesty; unknowns labeled | full trace, gates green, reproducible |

Baseline G is grounded only in deliverable-visible signals (citations present,
unknowns labeled, visible contradiction handling) and is **capped at 3**; if it
cannot be grounded it is `n/a`.

### T2 (data analysis) — scorable `{A,B,C,D,E}`, baseline G = `n/a`

Deliverable **container format** (docx / html / md) is treated as **F
(presentation)** and excluded; `E` covers the *content/structure* instructions
only. This is a protocol decision, stated explicitly.

| Axis | Grounded meaning for T2 | 5 looks like |
|---|---|---|
| A | All named analyses present: month-level overall + trend, grade distribution, fail rate, post differences, high/low performers, continuous improvers; plus 5–6 chapters | all present, gaps named |
| B | Explains management meaning; not a data listing | causal/decision-relevant synthesis |
| C | Numbers correct vs the 10 `.xlsx` (deterministic recomputation on headline figures); no fabricated figures | headline figures match recomputation |
| D | Data provenance stated (which months/files, denominators, dedup rules); figures traceable to a source table | fully traceable; caveats named |
| E | 5–6 chapters, ~14-page scope, formal professional tone, required elements present | all met within the requested shape |
| G | meld process artifacts | full trace |

Baseline G = `n/a` (no process trace exists), so `S = {A,B,C,D,E}` for T2.

## 7. Judge protocol

- **Judge:** a fresh `oracle` session (independent, read-only), one per pass.
- **Blind:** artifacts are presented as "Report A" / "Report B" with identity and
  source hidden; the judge is never told which is meld; order is fixed by the
  harness, not the judge.
- **Trials:** ≥3 blind passes for a final recorded verdict (median + range per
  axis); ≥1 pass during iteration.
- **Grounding:** the judge must quote concrete evidence for every axis score;
  deterministic-check outputs are supplied as inputs, not conclusions.
- **Same model** across all passes.

## 8. Deterministic checks (independent of the judge)

- **T1:** gate ① `check_evidence.py` (with `--plan` for `normal`) must be `ok`;
  gate ② `render_citations.py` must show 0 orphan / 0 unresolved; sampled
  citation links tested for reachability (HTTP status).
- **T2:** independently recompute headline aggregates from the 10 `.xlsx` with
  stdlib (`zipfile` + XML) and compare both reports' figures; run an instruction
  checklist (chapters, scope, required elements).

## 9. Rounds & contamination policy

- Layout (all gitignored under `test/`):
  `test/runs/exampleN/roundK/` (deliverables), `run-log.md`, `run-meta.json`.
- Each round runs in a **fresh subagent** with a **fresh output directory**; a
  round never reads another round's artifacts.
- Shared inputs are only: the frozen baseline and the skill under test.

## 10. Iteration & stop

- After scoring, if any in-scope axis lags, make the **smallest** change to the
  skill addressing the lowest axis, within the hard constraints, commit on the
  branch, then run a fresh round.
- Cap: **5 improvement rounds per example**.
- **Stop and report honestly** if: the cap is reached; the baseline is
  unreadable; or a fix would violate a hard constraint. The report lists the
  lagging axes, attempted fixes, score evidence, and the constraint whose
  relaxation would unlock progress. Never fake a pass.

## 11. Hard constraints (from the goal)

One skill; Python-stdlib-only scripts; zero runtime deps; no cross-skill deps;
no host-specific tool names under `skills/`; published text in English;
`main` always mergeable; **no push**; no new chart/HTML/PPT capability; baseline
downloads and live-run artifacts live only in `test/` (gitignored, never
committed).

## 12. Progress

- [x] Baseline downloaded + extracted (`PROVENANCE.md`)
- [x] Protocol v1
- [x] T1 round 1 live run — done (`test/runs/example1/round1/`)
- [x] T1 scoring — **PASS** (meld 28 vs baseline 14, median of 3 blind passes) → [`example1.md`](example1.md)
- [ ] T2 round 1 live run — **in progress**
- [ ] T2 scoring
