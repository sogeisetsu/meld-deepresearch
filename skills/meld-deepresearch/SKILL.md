---
name: meld-deepresearch
description: Turn a vague topic into a verifiable, citation-backed research report by searching multiple sources, opening the originals, and actively looking for counter-evidence instead of answering from the first few results. Use for deep research, systematic research, market research, competitive and landscape analysis, multi-source investigation, source verification, literature reviews, trend analysis, fact-checking, and any request for a cited report, brief, or deep dive.
license: MIT
compatibility: Requires web search, web fetch, file read/write and command execution; optional PDF, code-reading and subagent capabilities degrade gracefully when absent.
metadata:
  author: sogeisetsu
  repository: https://github.com/sogeisetsu/meld-deepresearch
  version: "0.4.0"
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

For answers that need **evidence from more than one source** and must be checkable: deep
research, market research, literature review, landscape/trend or competitive analysis, source
verification, fact-checking, any explicit request for a cited report or brief — not a one-line
answer, tidying up supplied sources or pure opinion.

## 2. Capability probe (do this first)

**Web search, web fetch and file read are blocking** — a missing one stops the
run: tell the user. **File write and command execution degrade** — continue,
stating the limitation. **PDF, code reading and subagents are optional** —
degrade and note it. Never deliver a silently degraded report (`protocol.md` §1).

## 3. Anchors, clarification, tier, length

Fix `language` (follow the user), `format` (default `report`), `structure` (a requested chapter count or outline is **binding** — discipline material folds in, never inflates it, internal ids `kqN`/`dN` stay out of the body) and `output_dir` (default naming and the user-path rule: `protocol.md` §11). Ask **1–3 scope-only questions** if the host can ask, else record the assumptions. Pick `quick`/`normal` (`tier-selection.md`), then judge **whether a long report is worth it and record why** — the length tiers and the user-length override live in `report-template.md` (*Length tiers*).

## 4. Workflow

| # | Stage | Action | Gate |
|---|---|---|---|
| 0 | Probe | capability probe (§2) | blocking capability missing → stop |
| 1 | Anchor | language, format, structure, output dir; 1–3 scope questions or recorded assumptions (§3) | — |
| 2 | Tier | tier + length tier, worth-it reason recorded | — |
| 3 | Plan | `quick`: `kq1..kqn`. `normal`: non-overlapping dimensions + `plan.json` | dimensions independently startable |
| 4 | Research | per axis: search → open originals → evaluate → gaps → again (§7) | stop at depth threshold |
| 5 | Merge | `scripts/meld.py prepare` (merge half) folds `sub_reports/*.evidence.json` → `evidence.json` | ids unique, duplicates collapse |
| 6 | Gate ① | `meld.py prepare` (gate half) → `check_evidence.py` (+ auto `--plan` for `normal`, `--tier` overrides) | must report `ok` |
| 7 | Write | one pass, inline citations, **no new facts**, header info block + TOC + discipline sections | strength ≤ evidence |
| 8 | Readability | prose polish of `report.src.md` (`report-template.md`); discipline material woven into the narrative | after prose edits re-run only `meld.py review --clean` |
| 9 | Gate ② | `scripts/meld.py render` → `.work/report.cited.md` **and** `report.md` (+ `citations.json`) | no orphan, no unresolved |
| 10 | Review | `scripts/meld.py review --clean` (file chosen automatically) | no jargon (hard); chapter left standing and labelled callout reported as warnings (§9) |
| 11 | Deliver | `scripts/meld.py sources` → `sources.md`, then the four artifacts + coverage gaps (§9) | — |

## 5. Evidence and citation rules

- **Enforced by the validator**; the rules and the full schema live in
  `references/evidence-contract.md` (claim kinds and their evidence floors,
  downgrade annotations, two-origin `interpretive` claims, referential
  integrity, `unknown` when unverifiable), with the research obligations
  they rest on in `references/protocol.md` §2–§3.

## 6. Cross-skill hand-offs

Two documented routes only (`protocol.md` §2a): local table files **plus**
analysis/cleaning/charting/export → `skills/meld-da` (`scripts/read_table.py` stays the
zero-dependency inspection layer); **academic, scientific or historical subjects route the
scholarly layer through `skills/meld-search-academic`** (`search.py` → `paper.py` →
`refTree.py`). A hand-off degrades instead of failing, is logged, and returns evidence here.

## 7. Budget and stop

Per-tier budgets (fetches, distinct sources, rounds per axis), the
fetch-counting rules, the bounded extension while key questions remain open
and every stop rule live in `references/protocol.md` §8 — their single
authority.

## 8. Gates, then stop or deliver

`references/protocol.md` §9 is the authoritative command list *and* code meaning (gate ①
passes only on `ok`; gate ② fails on an **orphan** or **unresolved** marker;
`content_review.py --clean` hard-fails on three delivery codes and reports two downgraded codes as warnings, all §9-defined); `scripts/meld.py`
is the primary CLI (`meld.py verify` runs prepare → render → review → review --clean, and
the raw script commands stay equivalents; gate ① also takes `--plan` on a `normal` run).
Stop rules — fix once and re-run, a second failure means **STOP**, one retry per stage —
live in `protocol.md` §9–§10. No command execution? Walk the gates by hand and say they
were skipped.

## 9. Deliverables

Four top-level artifacts — `report.md` (the marker-free reading copy the reader opens),
`sources.md`, `evidence.json`, `citations.json` — plus the manifest, directory layout,
delivery message and the no-file-write fallback are specified in `protocol.md` §11.
Return their paths, the tier, coverage, the manifest, every failed fetch and any budget
extension.

## 10. Non-negotiables

- Never invent a fact, number, quote or source; never conclude without a source.
- Always search for counter-evidence and report contradictions; label unknowns.
- Keep statement strength within evidence strength.
- Never hand-number citations: the renderer does it, once, for both files.
