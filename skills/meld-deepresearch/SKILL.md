---
name: meld-deepresearch
description: Turn a vague topic into a verifiable, citation-backed research report by searching multiple sources, opening the originals, and actively looking for counter-evidence instead of answering from the first few results. Use for systematic research, multi-source investigation, competitive analysis, literature reviews, trend analysis, fact-checking, and any request for a cited report, brief, or deep dive.
license: MIT
compatibility: Requires web search, web fetch, file read/write and command execution; optional PDF, code-reading and subagent capabilities degrade gracefully when absent.
metadata:
  author: sogeisetsu
  repository: https://github.com/sogeisetsu/meld-deepresearch
  version: "0.3.0"
---

# meld-deepresearch

Turn a vague topic into a **verifiable, citation-backed research report**:
every claim traces to a source that was actually opened, unknowns are labelled,
counter-evidence is searched on purpose. Discipline, not orchestration. Paths below are relative
to this skill's directory; detail loads on demand.

- `references/protocol.md` — loop, budgets, cross-skill hand-offs, gates, stop rules.
- `references/evidence-contract.md` — `evidence.json` schema and hard rules.
- `references/tier-selection.md` — `quick` vs `normal`.
- `references/report-template.md` — structure by reader's cognitive task, length tiers, readability pass.
- `templates/genres/` — append-templates per genre, chosen via `plan.json` `genre`.

## 1. When to use this skill

For answers that need **evidence from more than one source** and must be checkable: research,
literature review, landscape/trend or competitive analysis, fact-checking, any explicit request
for a cited report or brief — not a one-line answer, tidying up supplied sources or pure opinion.

## 2. Capability probe (do this first)

**Web search, web fetch and file read are blocking** — a missing one stops the
run: tell the user. **File write and command execution degrade** — continue,
stating the limitation. **PDF, code reading and subagents are optional** —
degrade and note it. Never deliver a silently degraded report (`protocol.md` §1).

## 3. Anchors, clarification, tier, length

Fix `language` (follow the user), `format` (default `report`), `structure` (a requested chapter count or outline is **binding** — discipline material folds in, never inflates it, internal ids `kqN`/`dN` stay out of the body) and `output_dir` (default `meld-deepresearch-reports/YYYY-MM-DD-{slug}-{hex4}/`; a user path replaces it). Ask **1–3 scope-only questions** if the host can ask, else record the assumptions. Pick `quick`/`normal` (`tier-selection.md`), then judge **whether a long report is worth it and record why**: short 1500–3000, medium 3000–6000, long 6000–12000 words; a user-specified length wins.

## 4. Workflow

| # | Stage | Action | Gate |
|---|---|---|---|
| 0 | Probe | capability probe (§2) | blocking capability missing → stop |
| 1 | Anchor | language, format, structure, output dir; 1–3 scope questions or recorded assumptions (§3) | — |
| 2 | Tier | tier + length tier, worth-it reason recorded | — |
| 3 | Plan | `quick`: `kq1..kqn`. `normal`: non-overlapping dimensions + `plan.json` | dimensions independently startable |
| 4 | Research | per axis: search → open originals → evaluate → gaps → again (§7) | stop at depth threshold |
| 5 | Merge | `scripts/merge_evidence.py` folds `sub_reports/*.evidence.json` → `evidence.json` | ids unique, duplicates collapse |
| 6 | Gate ① | `scripts/check_evidence.py` (+ `--plan` for `normal`) | must report `ok` |
| 7 | Write | one pass, inline citations, **no new facts**, header info block + TOC + discipline sections | strength ≤ evidence |
| 8 | Readability | weave the discipline chapters into the narrative (`report-template.md`) | re-run every gate after it |
| 9 | Gate ② | `scripts/render_citations.py` → `.work/report.cited.md` **and** `report.md` | no orphan, no unresolved |
| 10 | Review | `scripts/content_review.py --clean --report report.md` | no jargon, no chapter left standing |
| 11 | Deliver | `scripts/dedupe_sources.py` → `sources.md`, then the four artifacts + coverage gaps (§9) | — |

## 5. Evidence and citation rules

- **Enforced by the validator**; full schema in `references/evidence-contract.md`.
- Every claim carries evidence — a web source, or a reproducible first-hand
  `observations[]` entry cited `[^oN]`. A snippet is never evidence;
  counter-evidence is searched on purpose (zero `refute` warns).
- A `factual` claim needs a `primary`/`secondary` source or an observation; a
  lone `tertiary` source must carry an explicit "insufficient evidence / to
  verify" downgrade or it is rejected. An `interpretive` claim and any key
  finding need two distinct origins with at least one `primary`/`secondary` —
  `tertiary` may be the second origin, never the only pillar. Unverifiable ⇒
  `unknown`.

## 6. Cross-skill hand-offs

Two documented routes only (`protocol.md` §2a): local table files **plus**
analysis/cleaning/charting/export → `skills/meld-da` (`scripts/read_table.py` stays the
zero-dependency inspection layer); **academic, scientific or historical subjects route the
scholarly layer through `skills/meld-search-academic`** (`search.py` → `paper.py` →
`refTree.py`). A hand-off degrades instead of failing, is logged, and returns evidence here.

## 7. Budget and stop

| Tier | Fetches (soft) | Distinct sources | Rounds per axis |
|---|---|---|---|
| `quick` | ≤ 12 | ≥ 5 | ≤ 4 |
| `normal` | ≤ 40 | ≥ 15 | ≤ 5 |

Every fetch attempt counts (failures too); searches and local reads do not. On
exhaustion with key questions open, extend **at most 2 rounds**, logging new
sources, open questions and cost per round — then those questions become
`uncertainty` (`gaps[]` + `unknown`), never a fabricated conclusion (§8).

## 8. Gates, then stop or deliver

Run the commands exactly as `references/protocol.md` §9 lists them (gate ① also takes
`--plan` on a `normal` run). Gate ① passes only on `ok`; gate ② fails on an **orphan** or
**unresolved** marker; `content_review.py --clean` fails on run-failure jargon, a discipline
chapter left standing, a narrated run failure, or internal apparatus leaking into `report.md`.
Fix once and re-run — a second failure means **STOP** and report honestly. Every stage
(plan / research / merge / write / render) retries once, then stops with the failing stage,
artifacts and last error (`protocol.md` §10). No command execution? Walk the gates by hand
and say they were skipped.

## 9. Deliverables

`report.md` — the file the reader opens: no markers, header info block, table of contents,
discipline chapters woven into the narrative, first line linking to `.work/report.cited.md`.
Also `sources.md`, `evidence.json`, `citations.json`; `.work/` holds the middleware including
the cited copy. Return the four paths, the tier, coverage, the manifest, every failed fetch and
any budget extension; without file write, return the report body and say nothing was persisted.

## 10. Non-negotiables

- Never invent a fact, number, quote or source; never conclude without a source.
- Always search for counter-evidence and report contradictions; label unknowns.
- Keep statement strength within evidence strength.
- Never hand-number citations: the renderer does it, once, for both files.
