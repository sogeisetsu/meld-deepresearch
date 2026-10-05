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

## Round 3 (frozen skill: `main` `0958af1`, `SKILL.md` `e409856b…`)

Re-run on the frozen skill (which now includes the report-register fix) so both
examples are pinned to one SHA. Output: `test/runs/example1/round3b/` (13
headings). tier `normal`, 18/25 fetches, 15 sources, 3 observations, 32 claims.
Gates independently re-run: ① `ok`; ② `ok`, 15 citations, 3 observations, 0
orphan/uncited. `run-meta.json` pins `0958af1` / `e409856b…`.

| pass | order | total A | total B |
|---|---|---|---|
| 1 | A=baseline · B=meld3 | 18 | 28 |
| 2 | A=meld3 · B=baseline | 28 | 14 |
| 3 | A=baseline · B=meld3 | 14 | 27 |

Per-axis medians across the three round-3 passes (A–E,G; F excluded; max 30):

| axis | baseline (median) | meld3 (median) |
|---|---|---|
| A Coverage | 5 | 5 |
| B Depth | 3 | 5 |
| C Factual support | 1 | 5 |
| D Citation quality | 0 | 5 |
| E Instruction-following | 5 | 5 |
| G Process discipline | 1 | 3 |
| **total** | **15** | **28** |

Per-pass totals — meld3 28/28/27, baseline 18/14/14. Two passes fetched 6 of
meld's 15 links (all 200, content matches); the baseline has no resolvable links.

**PASS** — meld3 ≥ baseline on every axis (28 ≥ 15) on the **frozen** skill
(`main` `0958af1`, `SKILL.md` `e409856b…`) — the same version T2 round 4 was
scored on.

## Skill changes

None (round 1 already not-inferior). No skill file was modified in this round.

## Round 4 (scale redesign: `feat/scale-redesign` `1ab18aa`, skill `SKILL.md` `6b47969a…`)

Re-run on the scale-redesigned skill: three cooperating skills
(`meld-deepresearch` + `meld-da` + `meld-search-academic`), 120-line entry
point, soft budget with a 2-round extension rule, dual-file render
(`report.cited.md` + `report.md`), readability pass, `content_review --clean`
runtime-jargon gate. Output: `test/runs/example1/round4/` (fresh sub agent,
fresh directory, no other round read).

- `tier normal`, genre `panorama`, length tier **long** (worth-it reason
  recorded in `run-log.md`); 22/40 fetch attempts (21 opened, 1 HTTP 451),
  21 distinct sources, 31 claims, **11 `refute` claims**, 4 axes, 0 budget
  extensions; `report.md` 8,057 words, Chinese.

Deterministic checks (independently re-run by the orchestrator):

| Check | Result |
|---|---|
| Gate ① `check_evidence.py --plan` | `{"ok": true, "errors": [], "warnings": []}` exit 0 — run before **and** after the readability pass |
| Gate ② `render_citations.py --output report.cited.md --clean-output report.md` | `{"ok": true, "citation_count": 21, "observation_count": 0, "orphans": [], "uncited": ["o1"]}` exit 0 |
| `content_review.py --clean --report report.md` | `{"ok": true, "warnings": []}` exit 0 |
| `dedupe_sources.py` | `{"ok": true, "sources": 21, "duplicates_merged": 0}` |
| runtime-jargon scan of `report.md` (9 high-precision tokens) | **0** hits; `[^` markers: **0**; first line links to `report.cited.md` |
| link sample (8 of 21) | 8/8 HTTP 200, content matches |

`o1` (the HTTP 451 blocked page) is the only uncited observation — a warning,
not a failure. It was deliberately not cited inline because the cited render's
definition line reads `(captured 2026-10-05)`, which contains the reading
copy's blacklist substring `captured 20`; the fact is carried instead by gap
`g3` and an `availability` writing-context. Worth noting for a future pass:
the **clean** render already rewrites observation lines without the word
`captured`, so the avoidance was unnecessary.

### Blind judge passes (axes A,B,C,D,E,G; F excluded; max 30)

Identity hidden; only the A/B order varied. Fresh independent judge per pass;
each judge was shown the deliverables only (G therefore capped at 3), never a
branch, commit or version-bearing path.

| pass | order | Report A | Report B | total A | total B |
|---|---|---|---|---|---|
| 1 | A=baseline · B=redesign | baseline | redesign | 17 | 28 |
| 2 | A=redesign · B=baseline | redesign | baseline | 28 | 13 |
| 3 | A=baseline · B=redesign | baseline | redesign | 14 | 28 |

Per-axis scores:

| axis | pass1 base | pass1 new | pass2 base | pass2 new | pass3 base | pass3 new |
|---|---|---|---|---|---|---|
| A Coverage | 4 | 5 | 4 | 5 | 4 | 5 |
| B Depth | 4 | 5 | 3 | 5 | 4 | 5 |
| C Factual support | 2 | 5 | 2 | 5 | 2 | 5 |
| D Citation quality | 1 | 5 | 0 | 5 | 0 | 5 |
| E Instruction-following | 4 | 5 | 3 | 5 | 3 | 5 |
| G Process discipline | 2 | 3 | 1 | 3 | 1 | 3 |
| **total** | **17** | **28** | **13** | **28** | **14** | **28** |

Medians across the three passes:

| axis | frozen baseline (`baseline-f05bcbc.json`) | this round's baseline | redesign (median) | redesign ≥ frozen? |
|---|---|---|---|---|
| A Coverage | 5 | 4 | **5** | ✓ (=) |
| B Depth | 3 | 4 | **5** | ✓ |
| C Factual support | 1 | 2 | **5** | ✓ |
| D Citation quality | 0 | 0 | **5** | ✓ |
| E Instruction-following | 5 | 3 | **5** | ✓ (=) |
| G Process discipline | 1 | 1 | **3** | ✓ |
| **total** | **15** | 14 | **28** | ✓ (28 ≥ max(15, 15)) |

**PASS** — every axis median is ≥ the frozen baseline's, and the total median
(28) is ≥ `max(frozen 15, 15)`. One attempt, no repair round needed.

Judge notes (why the spread): the baseline remains broad and professionally
shaped but its bracketed markers resolve to nothing (no reference list, no
URL), several headline figures are uncited, internal apparatus leaks into the
body (`编制单位`, `版本：1.0`, image filenames), and no unknowns section
exists. The redesigned run's report is narrower in raw page count but carries
21 dated resolvable references, a dedicated contradiction section with the
strongest counter-evidence first, labelled unknowns, and a visible method
appendix.

## Round 5 (new delivery form: four deliverables, woven chapters) — **FAIL on E**

Round 4 had passed while the judge was still shown `report.cited.md`. The
delivery form then changed (cited copy moved to `.work/`; the reading copy must
carry a header info block, a table of contents and the discipline chapters
woven in), so round 5 re-ran the task on the new skill
(`test/runs/example1/round5/`) and this time the judge was shown **`report.md`
itself** — the file a reader actually gets.

- Run: `normal`, genre `panorama`, 4 axes, 15 distinct sources, 8 `refute`
  claims, 21/40 fetches, 0 extensions, ~18.5 minutes (the efficiency rules
  landed: incremental `run-log.md`, small scripts).
- Deterministic: gate ① `ok` (twice, before and after the weave), gate ②
  `ok` (15 citations, 2 observations, 0 orphan/uncited), `content_review
  --clean` exit 0 under the rules then in force, 0 standalone discipline
  chapters, 0 markers, 0 blacklist hits; 8/8 sampled links HTTP 200 (the
  ninth check, BBC, returned 200 via curl).

Blind passes (A/B order swapped, fresh judge per pass, deliverables only):

| pass | order | total A | total B |
|---|---|---|---|
| 1 | A=baseline · B=round5 | 13 | 26 |
| 2 | A=round5 · B=baseline | 26 | 16 |
| 3 | A=baseline · B=round5 | 16 | 26 |

Per-axis medians:

| axis | frozen baseline | this round's baseline | round5 | ≥ frozen? |
|---|---|---|---|---|
| A Coverage | 5 | 4 | **5** | ✓ |
| B Depth | 3 | 3 | **5** | ✓ |
| C Factual support | 1 | 2 | **5** | ✓ |
| D Citation quality | 0 | 1 | **5** | ✓ |
| E Instruction-following | 5 | 4 | **3** | ✗ |
| G Process discipline | 1 | 1 | **3** | ✓ |
| **total** | **15** | 16 | **26** | ✓ |

**FAIL on axis E** (3 < 5). All three judges independently gave E = 3 and
named the same three causes — internal apparatus inside the delivered report:

1. line 1 linked `.work/report.cited.md` (middleware path visible to the reader);
2. the header info block said `依据：meld-deepresearch 研究协议` — the skill
   and the protocol named in a client-facing report;
3. `## 观测记录` carried English process narration (`web fetch tool`,
   `Windows 11`) in a Chinese report.

Coverage, depth, citations, evidence and process discipline all still beat the
frozen baseline (26 vs 15 overall); only presentation discipline regressed,
because the new opening block and the observation section were introduced
without rules about what may appear in them.

### Repair (attempt 1 of at most 2) — commit `4b5cf24`

- `content_review.py --clean` now fails on apparatus leaks
  (`E_APPARATUS_LEAK`: skill id, `SKILL.md` / `report.src.md` / `run-log` /
  protocol names, "web fetch tool") and warns on any `.work/` path after line 1.
- The reading copy renders observations as `method (date)` — the machine
  environment stays in the cited copy.
- `report-template.md` states the rules explicitly: the info block's `依据`
  line describes the evidence basis only and never names a tool, skill or
  protocol; observation methods are written in the report's language, for
  readers, tool-agnostically; "no apparatus in the body" is a named rule.
- Checked retroactively: round 5's `report.md` now fails `content_review
  --clean` with three `E_APPARATUS_LEAK` hits — the gate catches exactly what
  the judges caught.

Round 6 is the repair run; its verdict follows below.

## Round 6 (repair attempt 1) — **FAIL on E**

The skill under test was `f601e39`'s predecessor `4b5cf24` (the round-5 fix).
Run in `test/runs/example1/round6/` (fresh sub agent, fresh directory; the
artifacts were later deleted with `test/`, so this record is the surviving
evidence).

- `normal`, genre `panorama`, 4 axes, 19 fetch attempts / **17 distinct
  sources**, 2 observations, ≥8 `refute` claims, 0 budget extensions, ~20
  minutes (20:47 → 21:08). Length tier `medium`, reason recorded in
  `run-log.md`.
- Deterministic checks (orchestrator re-run):

| Check | Result |
|---|---|
| Gate ① `check_evidence.py --plan` | `{"ok": true, "errors": [], "warnings": []}` exit 0 |
| Gate ② one render → both files | `{"ok": true, "citation_count": 17, "observation_count": 2, "orphans": [], "uncited": []}` exit 0 |
| `content_review.py --clean` | `{"ok": true, "warnings": []}` exit 0 |
| shape (orchestrator re-scan) | standalone discipline headings **0**, `[^` markers **0**, blacklist hits **0**, apparatus hits **0** |
| opening | 6-row info block, vertical `## 目录`, `## 定义与范畴` present |
| link sample (8 of 17) | 8/8 HTTP 200 (6 via the fetch client, 2 re-checked with `curl`, both 200) |

Blind judges (three fresh sessions, A/B order swapped, deliverables only,
`blind7/8/9` — no branch, commit or version-bearing path):

| pass | order | total A | total B |
|---|---|---|---|
| 1 | A=baseline · B=round6 | 17 | 26 |
| 2 | A=round6 · B=baseline | 26 | 14 |
| 3 | A=baseline · B=round6 | 17 | 26 |

Per-axis medians:

| axis | frozen baseline | round6 baseline | round6 | ≥ frozen? |
|---|---|---|---|---|
| A Coverage | 5 | 5 | **5** | ✓ |
| B Depth | 3 | 3 | **5** | ✓ |
| C Factual support | 1 | 2 | **5** | ✓ |
| D Citation quality | 0 | 1 | **5** | ✓ |
| E Instruction-following | 5 | 5 | **4** | ✗ |
| G Process discipline | 1 | 1 | **3** | ✓ |
| **total** | **15** | 17 | **26** | ✓ |

**FAIL on axis E** (4 < 5). All three judges named the same two remaining
causes: line 1 exposed `.work/report.cited.md` and `## 观测记录` carried
English process narration inside a Chinese report. Fix committed as `f601e39`
(see the round-history table under Round 7); round 7 is the second and final
repair attempt.

## Round 7 (repair attempt 2) — **PASS on the new delivery form**

Round 6 had failed axis E (median 4 vs the frozen 5) with both remaining
defects named by all three judges: line 1's `.work/` pointer and the
`## 观测记录` process log. The shape rules were then enforced mechanically
(commit `f601e39`) — and a line-by-line review of the delivered reports added
five more constraints: a definitions/scope section, an info block with one row
per rendered line, a vertical table of contents whose titles carry the
argument, content-bearing section headings instead of `## 主要发现`, and no
narration of run failures (`登录墙` etc.) in reader-facing text.

Run (`test/runs/example1/round7/`): `normal`, genre `panorama`, 5 axes,
21 fetch attempts / 16 opened sources, 30 claims (8 `refute`), 4 gaps, ~20
minutes.

| Check | Result |
|---|---|
| Gate ① `check_evidence.py --plan` (before and after the weave) | `{"ok": true}` exit 0, one expected `W_DOWNGRADE` |
| Gate ② one render → both files | `{"ok": true, "citation_count": 16, "observation_count": 0, "orphans": [], "uncited": []}` exit 0 |
| `content_review.py --clean` | exit 0, **zero warnings** |
| Shape assertions (orchestrator re-run) | standalone discipline headings **0**, `[^` markers **0**, blacklist hits **0**, generic container headings **0** |
| Info block | six `- label：value` rows, one per line; `依据：16 个已直接打开的来源` (no tool/protocol name) |
| `## 目录` | vertical list, 10 entries, all argument-bearing (e.g. `市场规模与增长：同一市场的两个口径相差逾一倍`) |
| `## 定义与范畴` | present, opens the body before any finding |
| link sample (8 of 16) | 8/8 HTTP 200 |

Delivered headings, in order: `目录`, `定义与范畴`, `摘要`, `市场规模与增长…`,
`竞争格局与份额…`, `产业链与成本结构…`, `技术进展与落地场景…`,
`政策与标准…`, `需求真实性与泡沫风险…`, `结论与展望`, `来源`.

### Blind judges (axes A,B,C,D,E,G; F excluded; max 30)

| pass | order | total A | total B |
|---|---|---|---|
| 1 | A=baseline · B=round7 | 13 | 27 |
| 2 | A=round7 · B=baseline | 28 | 13 |
| 3 | A=baseline · B=round7 | 15 | 28 |

Per-axis medians:

| axis | frozen baseline (`baseline-f05bcbc.json`) | round7 baseline | round7 | ≥ frozen? |
|---|---|---|---|---|
| A Coverage | 5 | 4 | **5** | ✓ |
| B Depth | 3 | 3 | **5** | ✓ |
| C Factual support | 1 | 2 | **5** | ✓ |
| D Citation quality | 0 | 1 | **5** | ✓ |
| E Instruction-following | 5 | 3 | **5** | ✓ (=) |
| G Process discipline | 1 | 1 | **3** | ✓ |
| **total** | **15** | 13 | **28** | ✓ (28 ≥ max(15, 15)) |

**PASS** — every axis median ≥ the frozen baseline, total 28 ≥ 15, on the
second and final permitted repair round. Judge notes on E: "readable opening
info block one row per line … argumentative TOC titles … 定义与范畴 section";
the single remaining deduction in pass 1 was the sanctioned line-1 pointer to
the cited copy.

### Round history (scale redesign)

| round | form judged | verdict | cause |
|---|---|---|---|
| 4 | `report.cited.md` (old layout) | PASS 28 vs 15 | — |
| 5 | `report.md`, first new-layout run | **FAIL** E=3 | apparatus in body, no info-block/TOC rules |
| 6 | `report.md`, after `E_APPARATUS_LEAK` | **FAIL** E=4 | `.work/` pointer + `## 观测记录` log |
| 7 | `report.md`, full shape rules enforced | **PASS** 28 vs 15 | — |
