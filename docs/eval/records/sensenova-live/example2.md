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
