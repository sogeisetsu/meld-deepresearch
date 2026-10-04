# Research Protocol

Execution rules for `meld-deepresearch`. `SKILL.md` decides *whether* to run and *picks the tier* (see `tier-selection.md`); this file defines *how* research runs, stops, and is gated. Evidence shape is defined separately in `evidence-contract.md`.

## 1. Where this sits

| Phase | Action | Artifact |
|---|---|---|
| Probe / anchor / clarify / tier select | see `SKILL.md` | in-memory anchors, `assumptions` |
| Plan | quick: `kq1..kqn` in memory; normal: named dimensions | normal only: `plan.json` |
| **Research (this file, §2–§7)** | per-axis loop | `sub_reports/dN.evidence.json` |
| **Merge (this file, §9)** | `merge_evidence.py` folds every axis file into one | `evidence.json` |
| Gate ① | evidence validator on the **merged** `evidence.json` (normal: plus `--plan`) | `{"ok": true}` |
| Write | one-shot draft, inline citations, no new facts | `report.src.md` |
| Gate ② | citation renderer | `report.md`, `citations.json` |
| Deliver | 4 artifacts + coverage note | see §11 |

## 2. The per-axis research loop

Each axis `dN` runs the same loop, at most **3 rounds**:

```
Search -> candidate URL pool -> Fetch -> read the ORIGINAL page
       -> evaluate -> find gaps -> Search again
```

**One round = one search → fetch → evaluate cycle for an axis:** the search
that refills the candidate pool, every fetch made from that pool, and the
evaluation that follows (§5). The ≤3-rounds-per-axis cap in §8 counts these
cycles.

Exact rules — all mandatory:

1. **Search before Fetch.** Never fetch a URL that did not come out of a search result, a cited reference inside an already-fetched page, or an explicit user-supplied link. No candidate URL ⇒ no fetch. **Never construct or guess a URL from a pattern** (`/docs/latest/...`, `/blog/2026/...`): a guessed URL that 404s is still a fetch attempt and is charged to the budget (§8).
2. **Maintain a candidate URL pool per axis:** merge new results into the pool → normalize the URL → de-duplicate → sort by source quality (`primary` > `secondary` > `tertiary`), then relevance, then recency. Fetch from the top of the pool; never re-fetch a URL already consumed.
3. **Search-result snippets are NEVER evidence.** A claim may only be trusted after the original page has been opened and the snippet checked against it (numbers, dates, polarity, exact wording all verified). Snippets exist only to decide what to fetch next.
4. Each fetched page yields candidate claims written to that axis's evidence file (`sub_reports/dN.evidence.json`), with `source_id`, `snippet`, and `quote_type` per `evidence-contract.md`.
5. **Route by source class (academic / developer axes).** For an academic or
   scientific axis, prefer repositories generic search can reach (arXiv,
   PubMed, SSRN, Google Scholar, official venue pages): adapt the query with
   venue / year / field terms, open the paper and read the section that
   matters rather than the abstract alone; when the paper cites the work a
   claim rests on, fetching that cited URL is a legitimate candidate (rule 1)
   and a way to walk the reference chain. For a developer / code axis, prefer
   GitHub, Stack Overflow, Hacker News and code/model hubs, and read the file
   or thread itself. This is query-and-routing guidance only: it needs no API
   key and adds no dependency. Platform-internal `code:` search and
   citation-count ranking stay deliberately out of scope.

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

## 4a. Access-blocked sources

The strongest primary sources are often the hardest to open: paywalls, bot
walls, and region blocks (403/401, Cloudflare challenges, metered paywalls).
Wanting the primary source and *not being able to open it* is a normal
condition, not a failure — but it must be handled the same way every time.

**The rule is: the original-open requirement is never waived.** A page you could
not open is not evidence, no matter how authoritative it is.

When a fetch cannot open the original text:

1. **Record the attempt, not the source.** Add an `observations[]` entry with
   `kind: "inspection"`, `method` describing the attempted fetch, and `snippet`
   holding the observable outcome (the HTTP status, e.g. `403`, or
   `paywall`/`bot-wall`). This is first-hand evidence that the page was
   unreachable, and it is citable as `[^oN]`.
2. **Record availability as a caveat.** Add a `writing_context[]` entry with
   `kind: "availability"` stating which source class was unreachable and what
   the conclusion therefore rests on. Route it into the report through its
   `use` field.
3. **Never launder a blocked source into apparent evidence.** Do **not** cite a
   search-engine cache, a snippet, a syndicated repost, or a "read it here"
   aggregator as if you had opened the original. Those are snippets (§2 rule 3)
   and are never evidence. If the only place a number appears is a snippet of a
   page you could not open, that number is not claimable.
4. **Degrade, do not fabricate.** It is legitimate to deliver a conclusion
   supported only by sources you *did* open (e.g. a secondary report that quotes
   the blocked primary), as long as step 1 and step 2 record the gap. The
   blocked source is not listed in `sources[]` as cited support.
5. **When a claim rests on nothing openable, mark it `unknown`.** If, after the
   budget, the only support for a claim is unreachable primary material, do not
   downgrade it to a low-confidence assertion — label it `unknown` per §7.

This is what the existing rules already imply (a snippet is never evidence); this
section makes the handling explicit so two runs behave the same way.

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

The next round's queries target this gap list first. Any gap still open when the
axis or the budget stops is recorded as a structured `gaps[]` entry
(`evidence-contract.md`) with `reason` (`no-source` / `access-limited` /
`budget` / `stale` / `other`) and `cost` (`cheap` / `hard`), and rendered into
the report's `## Gaps & Unknowns` section. State the reason honestly: a page
that could not be opened is `access-limited`, not `no-source`, and a page that
opened but yielded no usable text (an unparsable PDF, an empty body) is
`access-limited` too, not `other`.

## 8. Budget and stop conditions

| Tier | Fetch budget | Distinct sources | Rounds per axis |
|---|---|---|---|
| `quick` | ≤ 8 | ≥ 5 | ≤ 3 |
| `normal` | ≤ 25 | ≥ 15 | ≤ 3 |

- Budget is counted across the whole run; axes share it.
- **Every fetch attempt counts against the fetch budget, including failed
  attempts** (timeouts, 403s, bot walls, unparsable pages). An attempt that
  cost a network round-trip still cost budget; do not retry past the cap.
- **Searches are not charged to the fetch budget.** They are counted separately
  as rounds — one round = one search → fetch → evaluate cycle (§2) — and are
  bound by the ≤3-rounds-per-axis limit, not by the fetch budget.
- **When the budget is exhausted: STOP.** Return the best coverage achieved so far and **explicitly list what was not covered** (per-axis gaps from §7). Never loop forever, never take "just one more round" past the cap.
- If the source floor cannot be reached inside the fetch budget, report the shortfall honestly instead of padding with snippet-only or duplicate sources.

### Raising the cap (wide topics only)

A genuinely wide topic (many entities, many independent axes) can exhaust the
`normal` fetch budget before the axes are saturated. The cap is a discipline,
not a prohibition, so it may be **raised mid-run** under two conditions:

- **Only the fetch/source numbers move; the tier never does.** There is no third
  tier. A `normal` run that needs more room stays `normal` with a higher cap; it
  does not become some `deep` tier.
- **The raise is explicit and recorded.** Either the user asks for it, or the run
  states in its coverage note that it raised the cap before doing so. Record the
  new numbers where the assumptions live (§11): `plan.json` for a `normal` run,
  the delivery message for a `quick` run.

The ≤3-rounds-per-axis limit and the stop-on-exhaustion rule are **not** part of
the raise: only the fetch budget and the distinct-source floor can move.

## 9. Merge and hard gates

### Merge (after every axis, before gate ①)

Run
`scripts/merge_evidence.py --subreports <output_dir>/.work/sub_reports --output <output_dir>/evidence.json`.
It folds the six contract arrays — `claims`, `sources`, `observations`,
`writing_context`, `key_findings`, `gaps` — from every
`sub_reports/dN.evidence.json` into one `evidence.json`:

- **Ids stay unique after merging.** The prefix discipline already makes this
  true: claims are `dN.cM` and writing contexts are `dN.wM` (axis-scoped),
  while sources (`sN`) and observations (`oN`) are taken from one run-wide
  counter, never a per-axis one. A collision found anyway is re-keyed before
  gate ①; the validator rejects duplicate ids.
- **A source appearing in more than one axis file becomes one `sources[]`
  entry with a single id.** Re-point every `evidence[].source_id` and
  `writing_context[].source_ids[]` that named a duplicate id at that surviving
  id, so referential integrity holds in the merged file. The same fold applies
  to duplicate `observations[]` entries: one `oN`, re-pointed
  `evidence[].observation_id`s.
- **The merged file is what gate ① validates.** Gate ① never reads
  `sub_reports/`.

### The two gates

| Gate | Check | Pass condition |
|---|---|---|
| ① | evidence validator (`check_evidence.py`, see `evidence-contract.md`); normal tier: also `--plan` | output reports `ok: true` |
| ② | citation renderer (`render_citations.py`) | no **orphan** markers, no **unresolved** markers; **uncited** sources/observations are a warning only |

**Gate ① must run with `--plan` on a `normal` run.** Because `plan.json` is a
required normal-tier artifact, gate ① for a `normal` run is
`check_evidence.py "$OUTDIR/evidence.json" --plan "$OUTDIR/plan.json"` — this
is the only gate that checks plan coverage (every declared dimension covered,
every declared `kqN` answered). A `normal` run whose gate ① omits `--plan` has
not passed gate ①. `quick` runs have no `plan.json` and omit the flag.

Gate ② vocabulary, matching `render_citations.py` exactly:

- **Orphan** = an inline marker whose id is **absent from the array it names** —
  `[^sN]` with no `sources[]` entry, or `[^oN]` with no `observations[]` entry
  → gate ② fails.
- **Unresolved** = a marker left un-replaced (an empty id, or a residual `[^`
  marker) → gate ② fails. In the default GFM-footnote mode the rendered `[^N]` /
  `[^oN]` markers are expected, so only orphans fail; the residual-`[^` check
  applies to `--anchors` / `--legacy-plain`.
- **Uncited** = a source in `sources[]` or an observation in `observations[]`
  that the report never cites → **warning only**, never a failure.

### Gate commands

Run this block **from the skill's own directory** — the script paths below are
relative to it. Set `OUTDIR` to the run's output directory first, and use
`python3` when `python` is unavailable.

```bash
OUTDIR="meld-deepresearch-reports/2026-09-29-my-topic-ab12"

python scripts/merge_evidence.py --subreports "$OUTDIR/.work/sub_reports" --output "$OUTDIR/evidence.json"
python scripts/check_evidence.py "$OUTDIR/evidence.json" --plan "$OUTDIR/.work/plan.json"   # normal tier
python scripts/render_citations.py --report "$OUTDIR/.work/report.src.md" --evidence "$OUTDIR/evidence.json" --output "$OUTDIR/report.md"
python scripts/dedupe_sources.py --evidence "$OUTDIR/evidence.json" --output "$OUTDIR/sources.md"
python scripts/content_review.py --report "$OUTDIR/report.md" --evidence "$OUTDIR/evidence.json"   # optional, warn-only
```

`merge_evidence.py` and `content_review.py` are new; `content_review.py` is
optional and only warns. A `quick` run has no `plan.json`, so it omits the
`--plan` flag. `render_citations.py` renders GFM footnotes by default (the
renderer wires the jump itself, so it survives HTML sanitising); add `--anchors`
only when the target host keeps inline `<a id>` anchors.

- Gate failure ⇒ **fix once and re-run** (at most one re-run per gate).
- Second failure ⇒ **stop and report honestly** (failing stage, artifact paths, last error). Do not deliver a report that failed a gate.

## 10. Failure and retry

Stages with a retry budget of **1** each: plan, research, merge, write, render.
Retry once with a corrected approach; if it fails again, stop and report the
failing stage, the artifact paths on disk, and the last error message. Never
spin, never fake completion, never claim deliverables that do not exist.

Apply the matching row of this table instead of inventing a recovery:

| Symptom | First fix | Still failing / no fix available |
|---|---|---|
| A **blocking** capability is missing (`SKILL.md` §2) | — | 🔴 **STOP**; tell the user which capability is missing |
| An axis returns nothing usable | re-query with different terms, and route by source class (§2 rule 5) | record that axis's unfilled questions in `gaps[]`; continue the other axes |
| A source will not open (403 / paywall / bot-wall) | record the attempt and an `availability` caveat per §4a | mark the dependent claim `unknown`; never cite a snippet as if the page were read |
| A page opened but parses to nothing (PDF, empty body) | try an alternate reachable copy of the same material | record the gap with `reason: access-limited` |
| A URL was guessed from a pattern and 404s | do not retry it; fetch only from the candidate pool (§2 rule 1) | — (the guess already spent budget; note it in the fetch log) |
| Gate ① fails | read the error's `hint`, apply the smallest safe fix, re-run once | 🔴 **STOP**; report the error — never deliver a failing `evidence.json` |
| Gate ② fails (orphan / unresolved marker) | fix the marker or add the missing source, then re-render once | 🔴 **STOP**; report the error |
| Two ids collide after merge | re-key per §9, then re-run gate ① | 🔴 **STOP** |
| Fetch budget exhausted (§8) | — | 🔴 **STOP**; return the best coverage reached and the explicit uncovered list |
| Any stage fails twice | — | 🔴 **STOP**; report the failing stage, the artifacts produced, and the last error |

## 11. Artifacts and directories

Default output directory:

```
meld-deepresearch-reports/YYYY-MM-DD-{slug}-{hex4}/
├── report.md                 # delivered: rendered report
├── sources.md                # delivered: de-duplicated source table
├── evidence.json             # delivered: merged evidence
├── citations.json            # delivered: citation map
└── .work/                    # middleware (not a delivery core)
    ├── plan.json             # normal tier only
    ├── report.src.md         # write-stage draft (pre-citation-render)
    └── sub_reports/dN.evidence.json   # per-axis intermediate evidence
```

The four top-level files are the deliverables; `.work/` holds the middleware.
The delivery message **must list the full manifest** — the four artifacts, the
`.work/` contents that exist, and every failed fetch (URL + type) — so a reader
can see exactly what was produced and what was skipped.

- `{slug}` is a short kebab-case digest of the topic; `{hex4}` is 4 random hex digits for uniqueness. **When the user supplies an output directory, it replaces this default naming entirely** — no `{slug}` or `{hex4}` is appended; the run writes to the user's path exactly as given.
- **First-hand evidence** — commands run, measurements taken, files inspected on
  the host — is recorded as `observations[]` in `evidence.json` (the entry shape
  and the `evidence[].observation_id` rule are defined in
  `evidence-contract.md`). The report cites an observation with `[^oN]`,
  rendered as `[ON]`. The merged `evidence.json` carries `observations[]`
  alongside `sources[]`; the merge step in §9 concatenates it too.
- **Assumptions when the host cannot ask the user** go into `plan.json` for a
  `normal` run, and into the delivery message for a `quick` run (a `quick` run
  has no `plan.json`). State them there, never only in the model's context.
- `sources.md` is produced by `dedupe_sources.py` and is the **standalone,
  de-duplicated source list** — distinct from the report's own `## Sources`
  section (which the citation renderer owns, see `report-template.md`):

  `python scripts/dedupe_sources.py --evidence <output_dir>/evidence.json --output <output_dir>/sources.md`

  Use `python3` when `python` is unavailable.
- If the host lacks file-write capability: return **the report body only** in the response and state plainly that nothing was persisted.

## 12. Files are the source of truth

Raw retrieval results and structured evidence are written to disk; the model's context keeps only conclusions, decisions, and pointers to file paths. Do not keep whole pages or long raw outputs in context — save them, then keep a one-line summary plus the path. This prevents context bloat on long runs.

## 13. Optional delegation

- Default: **inline execution** — the same agent runs every axis.
- If the host provides a subagent capability, axes **MAY** be delegated for context isolation. The delegated unit receives the axis scope and returns its result **through an absolute file path** (its `sub_reports/dN.evidence.json`).
- Delegation is never required and never assumed. Probe for it; if absent, run inline. Delegated results still go through the merge in §9 and then through gates ① and ② unchanged.
