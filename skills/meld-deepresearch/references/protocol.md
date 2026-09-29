# Research Protocol

Execution rules for `meld-deepresearch`. `SKILL.md` decides *whether* to run and *picks the tier* (see `tier-selection.md`); this file defines *how* research runs, stops, and is gated. Evidence shape is defined separately in `evidence-contract.md`.

## 1. Where this sits

| Phase | Action | Artifact |
|---|---|---|
| Probe / anchor / clarify / tier select | see `SKILL.md` | in-memory anchors, `assumptions` |
| Plan | quick: `kq1..kqn` in memory; normal: named dimensions | normal only: `plan.json` |
| **Research (this file, §2–§7)** | per-axis loop | `sub_reports/dN.evidence.json` |
| Gate ① | evidence validator | `{"ok": true}` |
| Write | one-shot draft, inline citations, no new facts | `report.src.md` |
| Gate ② | citation renderer | `report.md`, `citations.json` |
| Deliver | 4 artifacts + coverage note | see §8 |

## 2. The per-axis research loop

Each axis `dN` runs the same loop, at most **3 rounds**:

```
Search -> candidate URL pool -> Fetch -> read the ORIGINAL page
       -> evaluate -> find gaps -> Search again
```

Exact rules — all mandatory:

1. **Search before Fetch.** Never fetch a URL that did not come out of a search result, a cited reference inside an already-fetched page, or an explicit user-supplied link. No candidate URL ⇒ no fetch.
2. **Maintain a candidate URL pool per axis:** merge new results into the pool → normalize the URL → de-duplicate → sort by source quality (`primary` > `secondary` > `tertiary`), then relevance, then recency. Fetch from the top of the pool; never re-fetch a URL already consumed.
3. **Search-result snippets are NEVER evidence.** A claim may only be trusted after the original page has been opened and the snippet checked against it (numbers, dates, polarity, exact wording all verified). Snippets exist only to decide what to fetch next.
4. Each fetched page yields candidate claims written to that axis's evidence file (`sub_reports/dN.evidence.json`), with `source_id`, `snippet`, and `quote_type` per `evidence-contract.md`.

## 3. Mandatory refutation

- After the supporting evidence looks sufficient, **actively search for counter-evidence**: opposing findings, failed cases, debunkings, and claims that cannot be verified at all.
- Record refuting claims with `polarity: refute` (and `neutral` for ambiguous material) — never drop them because they are inconvenient.
- **A refute count of zero almost always means the refutation search was not done properly**, not that the topic has no counter-arguments. If a run ends with zero refutes, re-run at least one refutation-targeted search before writing.
- Contradictions between sources are reported in the report's `Contradictions & Counter-evidence` section, not silently reconciled.

## 4. Time-sensitivity: three cases

| Case | Condition | Rule |
|---|---|---|
| 1. Fixed window | The request fixes a time window | Take evidence **only** from inside the window; discard out-of-window material even if it is newer or better. |
| 2. Time-sensitive, no window | Fact changes over time (prices, versions, rankings, incidents) | Track the **latest** state and **stamp the time point on every number** ("as of YYYY-MM"). |
| 3. Stable fact | Fact does not drift (settled definitions, mathematical results) | Prefer current authoritative sources; record `published_at` when available. |

When uncertain which case applies, treat the fact as case 2 (the cheaper mistake).

## 5. Per-round evaluation and saturation

At the end of every round, judge the axis on three dimensions:

- **Independence** — are sources genuinely independent, or several outlets restating one press release? Count distinct origins, not distinct domains.
- **Recency** — does the evidence satisfy the time case chosen in §4?
- **Verifiability** — could a reader click the citation and confirm the claim? Claims failing this are dropped or marked `unknown`.

Then decide whether the axis is **saturated**: stop it early when its `depth` threshold from the plan is met (all key questions `kqN` for the axis answered, refutation pass done, no open gap that a new search would plausibly close). Otherwise continue to the next round, up to the 3-round cap.

## 6. Multi-perspective seeding and scope ownership

- Borrowed from Stanford STORM: **seed several perspectives up front** instead of following the first framing. For a `normal` run, derive the axes from distinct angles (e.g. technical / commercial / regulatory, or one axis per compared entity) to break single-view blind spots.
- Every axis must be **independently startable**: its own key questions (`kqN`), its own candidate URL pool, no prerequisite on another axis's results.
- **Scope ownership:** each axis declares a non-overlapping search scope in the plan (`scope_ownership`). Duplicate coverage across axes wastes fetch budget; if two axes need the same source, one owns it and the other references the shared `source_id`.
- quick runs still seed at least one explicit refutation angle (§3).

## 7. Gap detection

After each round, write down **what is still unknown** for this axis:

- unanswered `kqN`;
- claims whose only support is weak (`tertiary` or snippet-level);
- numbers missing a time stamp where §4 case 2 applies;
- expected counter-evidence not yet searched for.

The next round's queries target this gap list first. Any gap still open when the axis or the budget stops goes to the report's `Gaps & Unknowns` section, labeled `unknown`.

## 8. Budget and stop conditions

| Tier | Fetch budget | Distinct sources | Rounds per axis |
|---|---|---|---|
| `quick` | ≤ 8 | ≥ 5 | ≤ 3 |
| `normal` | ≤ 25 | ≥ 15 | ≤ 3 |

- Budget is counted across the whole run; axes share it.
- **When the budget is exhausted: STOP.** Return the best coverage achieved so far and **explicitly list what was not covered** (per-axis gaps from §7). Never loop forever, never take "just one more round" past the cap.
- If the source floor cannot be reached inside the fetch budget, report the shortfall honestly instead of padding with snippet-only or duplicate sources.

## 9. Hard gates

| Gate | Check | Pass condition |
|---|---|---|
| ① | evidence validator (`check_evidence.py`, see `evidence-contract.md`) | output reports `ok: true` |
| ② | citation renderer (`render_citations.py`) | no orphan citations, no unresolved reference IDs |

- Gate failure ⇒ **fix once and re-run** (at most one re-run per gate).
- Second failure ⇒ **stop and report honestly** (failing stage, artifact paths, last error). Do not deliver a report that failed a gate.

## 10. Failure and retry

- Stages with a retry budget of **1** each: plan, research, write, render.
- Retry once with a corrected approach. If it fails again, stop and report the failing stage, the artifact paths on disk, and the last error message.
- Never spin, never fake completion, never claim deliverables that do not exist.

## 11. Artifacts and directories

Default output directory (overridable by the user):

```
meld-deepresearch-reports/YYYY-MM-DD-{slug}-{hex4}/
├── report.md
├── sources.md
├── evidence.json
├── citations.json
├── plan.json                     # normal tier only
├── report.src.md                 # write-stage draft (pre-citation-render)
└── sub_reports/dN.evidence.json  # per-axis intermediate evidence
```

- `{slug}` is a short kebab-case digest of the topic; `{hex4}` is 4 random hex digits for uniqueness.
- If the host lacks file-write capability: return **the report body only** in the response and state plainly that nothing was persisted.

## 12. Files are the source of truth

Raw retrieval results and structured evidence are written to disk; the model's context keeps only conclusions, decisions, and pointers to file paths. Do not keep whole pages or long raw outputs in context — save them, then keep a one-line summary plus the path. This prevents context bloat on long runs.

## 13. Optional delegation

- Default: **inline execution** — the same agent runs every axis.
- If the host provides a subagent capability, axes **MAY** be delegated for context isolation. The delegated unit receives the axis scope and returns its result **through an absolute file path** (its `sub_reports/dN.evidence.json`).
- Delegation is never required and never assumed. Probe for it; if absent, run inline. Delegated results still pass through gates ① and ② unchanged.
