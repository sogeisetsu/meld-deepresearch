---
name: meld-deepresearch
description: Turn a vague topic into a verifiable, citation-backed research report by searching multiple sources, opening the originals, and actively looking for counter-evidence instead of answering from the first few results. Use for systematic research, multi-source investigation, competitive analysis, literature reviews, trend analysis, fact-checking, and any request for a cited report, brief, or deep dive.
license: MIT
compatibility: Requires web search, web fetch, file read/write and command execution; optional PDF, code-reading and subagent capabilities degrade gracefully when absent.
metadata:
  author: sogeisetsu
  repository: https://github.com/sogeisetsu/meld-deepresearch
  version: "0.2.0"
---

# meld-deepresearch

Turn a vague topic into a **verifiable, citation-backed research report**. This
skill enforces discipline, not orchestration: every claim traces back to a
source that was actually opened, unknowns are labelled, and counter-evidence is
searched on purpose.

Detail lives in `references/` and is loaded only when needed. Every path in
this file (`references/...`, `scripts/...`) is **relative to this skill's own
directory** — the directory that contains this `SKILL.md`.

- `references/protocol.md` — search/fetch loop, time-sensitivity, refutation, budgets, gates, stop rules.
- `references/evidence-contract.md` — the `evidence.json` schema and its hard rules.
- `references/tier-selection.md` — how to pick `quick` versus `normal`.
- `references/report-template.md` — report skeleton and the quality self-check.
- `templates/genres/` — append-templates per genre (panorama / comparison / entity / chronicle), selected via `plan.json` `genre`.

## 1. When to use this skill

Use it when the answer needs **evidence from more than one source** and must be
checkable:

- systematic research, literature review, landscape or trend analysis
- competitive or entity comparison, market and vendor overview
- fact-checking a claim, a number, or a widely repeated statement
- any explicit request for a report, brief, or deep dive with citations

Do **not** use it for:

- a one-line factual answer or a definition
- tidying up sources the user already handed over
- pure rewriting, translation, or copy-editing
- an opinion piece where no evidence is expected

If a quick search would genuinely settle the question, say so and answer
directly instead of running the full loop.

## 2. Capability probe (do this first)

Probe the host before planning and hold the result in memory:

| Capability | Need | If missing |
|---|---|---|
| web search | blocking | stop and tell the user |
| web fetch / open pages | blocking | stop and tell the user |
| file read | blocking | stop and tell the user |
| file write | degradable | still run, but return the report body inline and state that nothing was persisted |
| command execution | degradable | still run, but walk the gates as a manual checklist and state that they were skipped |
| PDF reading | optional | save the binary, then parse it with the host's PDF tool; if it cannot be parsed, record the URL + type as a gap — never a silent drop |
| code reading | optional | degrade and note it |
| subagent delegation | optional | run every axis inline |

**STOP:** a missing **blocking** capability pauses the run — tell the user and
stop. A **degradable** one lets the run continue, but the limitation must be
stated in the final output — never deliver a silently degraded report.

## 3. Request anchors

Fix three anchors before researching:

- `language` — the language of the final report; **follow the user**.
- `format` — default `report`.
- `output_dir` — default `meld-deepresearch-reports/YYYY-MM-DD-{slug}-{hex4}/`; a user-supplied directory replaces that naming entirely.

## 4. Clarify before researching

If the host can ask, ask **1–3 scope-only questions** (time window, geography,
comparison set, which definition). Never ask what the request already answers;
for a `normal` run the draft plan may also be offered for confirmation. If the
host cannot ask, record the assumptions — in `plan.json` (`normal`) or the
delivery message (`quick`) — and continue; never block on an answer.

## 5. Tier selection

Pick `quick` or `normal` automatically and continue — default `quick`, any
single `normal` condition upgrades, the user can override. See
`references/tier-selection.md` for the decision table and worked examples.

## 6. Workflow

| # | Stage | Action | Gate |
|---|---|---|---|
| 0 | Probe | capability probe (§2) | a blocking capability is missing → stop |
| 1 | Anchor | fix language, format, output dir (§3) | — |
| 2 | Clarify | ask 1–3 scope questions, or record assumptions (§4) | — |
| 3 | Tier | select `quick` or `normal` (§5) | — |
| 4 | Plan | `quick`: internal key questions `kq1..kqn`. `normal`: named dimensions with non-overlapping scope, plus `plan.json` | dimensions must be independently startable |
| 5 | Research | per dimension: search → candidate URL pool → open the originals → evaluate → find gaps → search again, at most 3 rounds | stop at the depth threshold |
| 6 | Merge | `scripts/merge_evidence.py` folds every `sub_reports/dN.evidence.json` into one `evidence.json` | ids stay unique; duplicate sources collapse to one entry |
| 7 | Gate ① | run the evidence validator on `evidence.json`, with `--plan` for a `normal` run | must report `ok` |
| 8 | Write | one pass, inline citations, **no new facts** | statement strength must not exceed evidence |
| 9 | Gate ② | render citations from the draft and the evidence | no orphan, no unresolved reference |
| 10 | Sources | normalize and de-duplicate URLs into `sources.md` | — |
| 11 | Deliver | return the four artifacts plus coverage and gaps (§10) | — |

The full loop, budgets and stop rules are in `references/protocol.md`.

## 7. Evidence and citation rules

Non-negotiable, enforced by the validator — the full schema, allowed values and every hard rule live in `references/evidence-contract.md`:

- Every claim carries evidence — a web source **or** a reproducible first-hand `observations[]` entry cited `[^oN]`; a search-result snippet is never evidence.
- A `factual` claim needs a `primary`/`secondary` source or an observation; an `interpretive` claim needs two **distinct** origins; anything unverifiable is labelled `unknown`.
- Counter-evidence is searched on purpose; a run with no `refute` claim at all draws a validator warning.

## 8. Budget and stop conditions

| Tier | Max fetches | Min distinct sources | Max rounds per axis |
|---|---|---|---|
| `quick` | 8 | 5 | 3 |
| `normal` | 25 | 15 | 3 |

Every fetch attempt counts against the cap, failures included. When the budget is
exhausted: **stop**, return the best coverage reached so far, and list explicitly
what was not covered. Never loop indefinitely.

## 9. Self-check gate (hard)

Before delivering, run the gate commands exactly as listed in `references/protocol.md` §9 (gate ① also takes `--plan` on a `normal` run):

- Gate ① passes only when the validator reports `ok` (warnings do not fail it); gate ② fails on an **orphan** or **unresolved** marker — vocabulary defined in `references/protocol.md` §9.
- If a gate fails: fix once and re-run. If it still fails, **STOP** and report honestly — do not deliver a failing report.
- If the host has no command execution, walk the gates by hand and state that they were skipped.

## 10. Deliverables

Write into `output_dir`:

- `report.md` — the report, rendered with numbered citations.
- `sources.md` — the normalized, de-duplicated source list.
- `evidence.json` — the structured evidence behind every claim.
- `citations.json` — the citation map emitted by the renderer.
- `.work/` — middleware (not a delivery core): `plan.json` (normal tier only),
  `report.src.md`, `sub_reports/dN.evidence.json`.

`content_review.py` is an optional, warn-only self-check (`--report` +
`--evidence`); it never blocks delivery.

The renderer owns the report's `## Sources` and `## Observations` sections;
leave `report.src.md` ending at `## Sources` with nothing after it
(`references/report-template.md`). It emits GFM footnotes by default, so the
rendered `report.md` carries a footnote block instead of that heading — the host
wires the numbered superscript and its back-link itself. `sources.md` and the
report's citation block cover the same sources in two forms.

Return the four artifact paths, plus the tier used, the coverage reached, the
full manifest (including `.work/` contents), and every failed fetch (URL +
type). If the host cannot write files, return the report body only and say that
nothing was persisted.

## 11. Failure and retry

Each pipeline stage (plan / research / merge / write / render) may be retried **once**, then stop and report the failing stage, the artifact paths produced so far, and the last error — never pretend a run completed.
Apply the symptom → first fix → fallback table in `references/protocol.md` §10 instead of inventing a recovery.

## 12. Non-negotiables

- Never invent a fact, number, quote, or source.
- Never state a conclusion without a source behind it.
- Always search for counter-evidence, and report the contradictions found.
- Always label the unknown as `unknown`.
- Keep the strength of a statement within the strength of its evidence.
- Never hand-number citations — always let the renderer do it.

## 13. Context strategy

Files are the source of truth: raw retrieval and structured evidence go to
disk, the context keeps only conclusions, and delegation is optional — see
`references/protocol.md` §12–§13.
