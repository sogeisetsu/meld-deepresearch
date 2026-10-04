# Example 2 — employee-performance analysis (T2)

Protocol: [`README.md`](README.md). Baseline: frozen SenseNova example 2
(`test/baseline/`, gitignored). Skill under test: branch
`feat/sensenova-live-compare`, git `7c17f7f`, `SKILL.md`
`ca6aa8c53b971e0e…` (see `run-meta.json`).

## Task (adapted — dropped the proprietary `sn-da-excel-workflow` token)

> 请根据我 10 个风电事业部月度绩效考核表格文件，生成一份正式员工绩效分析报告，
> 报告建议分为 5–6 个章节，篇幅约 14 页。报告需从月份、岗位、员工三个层级分析
> 总体绩效、趋势变化、绩效等级分布、不合格率、岗位差异、高低绩效员工和连续进步
> 员工。报告格式正式、结构清晰、语言专业简洁，不只罗列数据，要解释数据背后的
> 管理含义。

Charts and deliverable container (docx/html) are F-axis → excluded (protocol §6).

## Run round 1

- Output: `test/runs/example2/round1/` (gitignored). `report.md` 168 lines;
  four artifacts + `.work/` (`analyze.py`, `analysis.json`, `plan.json`,
  `sub_reports/d1..d4.evidence.json`).
- tier `normal`, genre `panorama`; fetch 25/25 exhausted, 17 distinct sources,
  31 claims, 8 observations, 6 gaps.

## Deterministic checks (independently re-run)

| Check | Result |
|---|---|
| Gate ① `check_evidence.py --plan` | `{"ok": true, "errors": [], "warnings": []}` exit 0 |
| Gate ② `render_citations.py` | `{"ok": true, "citation_count": 17, "observation_count": 8, "orphans": [], "uncited": []}` exit 0 |
| `dedupe_sources.py` | 17 sources, 0 duplicates |
| numeric cross-check | **932** records; mean **50.03**, median **49.12**, fail **61.7 %**, **38** posts — identical across raw xlsx, `recompute.json` and the run's `analysis.json` |
| employee key | 117 distinct `姓名` vs 119 distinct `工号` — a convention difference, both defensible; the run used 工号 and stated the 60-line/band convention as an assumption |

**Provenance caveat (important).** The run's local helper
`.work/analyze.py` imports **openpyxl** (not stdlib). The skill's *shipped* scripts
remain stdlib-only, so no hard constraint is broken, but the demonstrated numeric
capability depended on an external library being present in the run workspace.
Making this reproducible for any host would require a stdlib-only ingestion path
inside the skill (a candidate follow-up, not a defect of this run).

## Blind judge passes (axes A–E; F and G excluded for T2; max 25)

| pass | order | Report A | Report B | total A | total B |
|---|---|---|---|---|---|
| 1 | A=baseline · B=meld | baseline | meld | 19 | 22 |
| 2 | A=meld · B=baseline | meld | baseline | 24 | 17 |
| 3 | A=baseline · B=meld | baseline | meld | 17 | 24 |

Median across the three passes:

| axis | baseline (median) | meld (median) |
|---|---|---|
| A Coverage | 5 | 5 |
| B Depth | 3 | 5 |
| C Factual accuracy | 3 | 5 |
| D Provenance | 2 | 5 |
| E Instruction-following | 5 | 4 |
| **total** | **18** | **24** |

Per-pass totals — baseline 19/17/17, meld 22/24/24.

## Verdict — round 1: FAIL (one axis lags)

Total 24 ≥ 18 and meld ≥ baseline on A/B/C/D, but **E: meld 4 < baseline 5**, so
the goal's "no in-scope axis lags" rule is not met.

**Root cause (E).** The prompt says "报告建议分为 5–6 个章节…语言专业简洁".
The baseline delivered exactly 5 chapters; meld emitted **11 top-level
sections** (摘要/主要发现/背景/三核心维度/综合分析/结论/附录/矛盾与反证/未知与缺口),
leaked internal codes (`kq1/kq2`), and read academically rather than as a concise
formal report. Meld's substance (B/C/D) is far ahead — the loss is purely that it
ignores an explicit structural/tone instruction.

**Fix (round 2).** Add a structural anchor to the skill: when the request names a
chapter count/outline/tone, the report body must follow it; the genre template is
only a default; evidence-discipline material (method, contradictions, gaps,
observations) folds into a non-numbered appendix rather than extra chapters; no
internal identifiers in the body.

## Skill changes (round 1 → round 2)

Commit `639f408` — "fix(skill): honor a requested report structure and register":

- `SKILL.md` §3: added a `structure` anchor (a requested chapter count / outline
  is binding; skeleton + genre are the default only).
- `references/report-template.md`: new "Requested structure overrides the
  skeleton" section — fold discipline material into a non-numbered appendix,
  match the requested register/length, no internal `kqN`/`dN` codes in the body;
  plus an updated instruction-following self-check row and a Do/Don't row.

Doc-only, zero-dependency, single skill — within every hard constraint. The
skill's own gates still pass on `examples/sample-run/`; `SKILL.md` is 187 lines.

## Round 2 (after the structure fix)

- Output: `test/runs/example2/round2/`. Structure now **6 numbered chapters +
  1 non-numbered appendix** (matches "5–6 章节"); genre `general`.
- tier `normal`; fetch 22/25, 15 distinct sources, 32 claims, 17 observations, 5 gaps.
- Gates independently re-run: ① `{"ok": true}`; ② `{"ok": true, "citation_count": 15,
  "observation_count": 17, "orphans": [], "uncited": []}`.

| pass | order | total A | total B |
|---|---|---|---|
| 1 | A=baseline · B=meld2 | 18 | 24 |
| 2 | A=meld2 · B=baseline | 25 | 16 |
| 3 | A=baseline · B=meld2 | 16 | 25 |

Median across the three round-2 passes:

| axis | baseline (median) | meld (median) |
|---|---|---|
| A Coverage | 5 | 5 |
| B Depth | 3 | 5 |
| C Factual accuracy | 2 | 5 |
| D Provenance | 2 | 5 |
| E Instruction-following | 4 | 5 |
| **total** | **18** | **25** |

Per-pass totals — baseline 18/16/16, meld 24/25/25.

## Verdict — round 2: PASS

**PASS** — meld ≥ baseline on every in-scope axis (25 ≥ 18). The round-1 E gap
is closed: after the structure fix the body has 6 numbered chapters and the E
median is meld 5 vs baseline 4. Residual E variance (meld scored 4 once, 5 twice)
is judges weighing meld's citation density/length against "简洁"; the same
passes docked the baseline's short length. No further skill change needed.

## G axis (supplementary, full process artifacts)

The passes above excluded G (the baseline has no process trace). A dedicated
independent pass scored G per the rubric's intent — deliverable-visible (cap 3)
for the baseline, full process artifacts for the meld run:

| instance | G | basis |
|---|---|---|
| T2 baseline | **3** | deliverable only: data source and thresholds stated, but inferences stated as facts, no unknowns / counter-evidence / repro |
| T2 meld r2 (`97210300…`) | **5** | 17 observations with re-runnable `analyze.py` commands, both gates' stdout in run-log, budget honesty, active threshold self-falsification, unknowns listed |

Full objective surface **A–E,G** (max 30): meld **30** vs baseline **21**; meld ≥
baseline on every axis.

## Round 3 (current skill: `main` `b6422ad`, `SKILL.md` `e409856b…`)

Re-run on the current skill, which now ships `read_table.py`. Output:
`test/runs/example2/round3/`. tier `normal`, genre `panorama`, 6 numbered
chapters + non-numbered appendix; 22/25 fetches, 15 sources, 32 claims, 15
observations.

Deterministic (orchestrator re-run): gate ① `ok`; gate ② `ok`, 15 citations, 15
observations, 0 orphan/uncited. The run read the 10 xlsx with the skill's own
stdlib `read_table.py` — **0** references to `openpyxl`, 96 to `read_table.py`
(closing the earlier ad-hoc-helper caveat) — and its `.work/verify.py`
independently re-checks 23 headline figures (23/23 PASS). Headline numbers match
the orchestrator's independent stdlib recompute (932 / 50.03 / 49.12 / 61.70%).
`run-meta.json` pins `b6422ad` / `e409856b…`.

| pass | order | total A | total B |
|---|---|---|---|
| 1 | A=baseline · B=meld3 | 19 | 24 |
| 2 | A=meld3 · B=baseline | 24 | 19 |
| 3 | A=baseline · B=meld3 | 18 | 24 |

Per-axis medians across the three round-3 passes (A–E; F excluded; max 25):

| axis | baseline (median) | meld3 (median) |
|---|---|---|
| A Coverage | 5 | 5 |
| B Depth | 3 | 5 |
| C Factual accuracy | 4 | 5 |
| D Provenance | 2 | 5 |
| E Instruction-following | **5** | **4** |
| **total** | **19** | **24** |

Per-pass totals — meld3 24/24/24, baseline 19/19/18.

**FAIL (round 3) — E lags by 1.** Total 24 ≥ 19 and meld ≥ baseline on A/B/C/D,
but **E: meld 4 < baseline 5** (all three passes). The judges' reason is register,
not structure (the body already has 6 chapters): meld reads as an academic
research memo — 15 external references, a "strongest counter-evidence" framing,
no consolidated `结论与改进建议` chapter — and likely exceeds the ~14-page target;
the baseline is a concise 5-chapter business report with a recommendations
chapter. This is a narrow, consistent gap, so a targeted fix is warranted.

### Fix (round 4)

`references/report-template.md` — extend the "Match the requested register and
length" rule: (a) keep external citations to sources that carry a claim, not
background literature; (b) when the request implies a management deliverable,
include a consolidated `结论与改进建议` chapter; (c) respect a stated length
target, moving method/observation/secondary-contradiction detail into a compact
non-numbered appendix (it still lives in the evidence files for axis G).
