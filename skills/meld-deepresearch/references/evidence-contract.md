# Evidence Contract — `evidence.json`

The data contract for the structured evidence file. A validator script
(`scripts/check_evidence.py`, run for gate ① through `scripts/meld.py prepare`
— the raw command stays equivalent, see `protocol.md` §9) enforces every rule
below; a file that fails validation is not delivered. Field names, object names
and enum values here are **exact** — the validator matches them literally.

## Top-level shape

`evidence.json` is one JSON object with five arrays (plus one optional array):

| Array | What it holds |
|---|---|
| `claims[]` | Atomic statements the report may make, each with its own evidence |
| `sources[]` | Every web source any claim or context refers to, with a quality tier |
| `observations[]` | First-hand evidence gathered by the run itself (commands, measurements, files, inspections) |
| `writing_context[]` | Scope, sample, method and availability caveats, kept out of claims |
| `key_findings[]` | Derived synthesis that points back to claims; adds no new facts |
| `gaps[]` | **Optional.** Structured unknowns: what could not be covered and why |

(`evidence[]` is nested inside each claim; it is not a top-level array.)

`observations[]` and `gaps[]` are **optional**: a run with no first-hand evidence
may omit `observations[]` altogether or pass an empty array, and a run with
nothing structured to report may omit `gaps[]`; neither is an error. When
present they must be arrays; `claims`, `sources`, `writing_context` and
`key_findings` are always required.

## ID conventions

| Pattern | Meaning |
|---|---|
| `dN` | Research axis / dimension `N` (1-based, no leading zeros) |
| `dN.cM` | Claim `M` under axis `N` — e.g. `d2.c1` |
| `kqN` | Key question `N` (1-based, no leading zeros), generated during planning; claims answer it or are `null` |
| `dN.wM` | Writing-context entry `M` under axis `N` |
| `sN` | Source `N`. Only uniqueness and referential integrity are enforced; any opaque, unique string is accepted |
| `oN` | Observation `N` (1-based, no leading zeros) — e.g. `o1`, `o12`; never `o0` or `o01` |

**`kqN` is globally unique across the whole run** (C1), exactly like `dN`:
numbering starts at 1, has no leading zeros, and is shared by every axis. Two
axes must not each invent their own `kq1` — a key question that two axes both
need is *one* `kqN` that both answer.

## Field reference

### `claims[]`

| Field | Type | Required | Allowed values | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `dN.cM` | Unique claim id |
| `text` | string | yes | non-empty | The statement, one atomic assertion |
| `kind` | string | yes | `factual` \| `interpretive` \| `projective` \| `background` | Fact / interpretation / projection / context |
| `polarity` | string | yes | `support` \| `refute` \| `neutral` | Which side of the question the claim takes |
| `topic_tag` | string | yes | non-empty | Free tag grouping claims by topic |
| `answers_key_question` | string \| null | yes | `kqN` or `null` | Key question this claim answers, if any |
| `evidence[]` | array | yes | ≥ 1 evidence item: for `factual` one that resolves to a `primary`/`secondary` source **or** to an observation; for `interpretive` ≥ 2 distinct origins; for `projective` ≥ 1 item (any tier); for `background` ≥ 1 item (any tier) | Supporting snippets; see below |

### `evidence[]` (inside a claim)

Every evidence item points at **exactly one origin**: a web source **or** a
first-hand observation.

| Field | Type | Required | Allowed values | Meaning |
|---|---|---|---|---|
| `source_id` | string \| null | exactly one of `source_id` / `observation_id` | must exist in `sources[]` | Which source this snippet comes from |
| `observation_id` | string \| null | exactly one of `source_id` / `observation_id` | must exist in `observations[]` | Which observation this snippet comes from |
| `snippet` | string | yes | non-empty | Verbatim or closely paraphrased excerpt actually read in the source, or copied from the observation |
| `quote_type` | string | yes | `direct` \| `paraphrase` \| `numeric` | How the snippet relates to the origin text |

`source_id` and `observation_id` must be **mutually exclusive**: filling in
both, or neither, is `E_SHAPE`. A JSON `null` counts as "not filled in".

A search-result summary is never evidence: the snippet must come from the
opened source itself (or from the recorded observation).

### `observations[]` (first-hand evidence)

First-hand evidence is a first-class citizen of the contract: anything the run
itself ran, measured or read on the machine under study is recorded here and
cited like any source, never smuggled into `writing_context`.

| Field | Type | Required | Allowed values | Meaning |
|---|---|---|---|---|
| `id` | string | yes | `oN` — 1-based, no leading zeros (`o1`, `o12`; never `o0`, `o01`), globally unique in the file | Observation id |
| `kind` | string | yes | `command` \| `measurement` \| `file` \| `inspection` | How the evidence was obtained |
| `method` | string | yes | non-empty | What was actually done to get it |
| `command` | string \| null | yes | **non-empty** when `kind: "command"`; otherwise a string or `null` | Reproducible command line |
| `captured_at` | string | yes | ISO date `YYYY-MM-DD` | When it was captured |
| `environment` | string \| null | yes | string or `null` | Environment (OS, versions, host) |
| `snippet` | string | yes | non-empty | The observed output, value or file content |

A malformed entry — not an object, a missing required field (`id`, `kind`,
`method`, `command`, `captured_at`, `environment` or `snippet`), an empty
`method` / `snippet`, a non-`YYYY-MM-DD` `captured_at`, a bad or duplicate `oN`
id, or `kind: "command"` with an empty `command` — is `E_OBS_SHAPE`; an unknown
`kind` value is `E_ENUM`. A claim's `observation_id` that does not resolve here
is `E_REF_OBSERVATION`.

Compact valid example — one observation cited by a `factual` claim, with no
web source backing it (an observation counts as first-hand, so this passes):

```json
{
  "claims": [
    {
      "id": "d1.c1",
      "text": "The installed CLI reports version 2.100.0.",
      "kind": "factual",
      "polarity": "support",
      "topic_tag": "tooling",
      "answers_key_question": null,
      "evidence": [
        {"observation_id": "o1", "snippet": "gh version 2.100.0 (windows amd64)", "quote_type": "direct"}
      ]
    }
  ],
  "observations": [
    {"id": "o1", "kind": "command", "method": "Ran the CLI version command in the repository root.", "command": "gh --version", "captured_at": "2026-09-29", "environment": "Windows 11, gh 2.100.0", "snippet": "gh version 2.100.0 (windows amd64)"}
  ],
  "sources": [
    {"id": "s1", "url": "https://example.org/nimbus/announcements/2-0", "title": "Nimbus 2.0 release notes", "quality": "primary", "published_at": "2026-03-14"}
  ],
  "writing_context": [],
  "key_findings": []
}
```

### `sources[]`

| Field | Type | Required | Allowed values | Meaning |
|---|---|---|---|---|
| `id` | string | yes | unique | Source id referenced by `evidence[].source_id` |
| `url` | string | yes | well-formed absolute `http(s)` URL; reachability is NOT machine-checked | Where the source was read |
| `title` | string | yes | non-empty | Source title |
| `quality` | string | yes | `primary` \| `secondary` \| `tertiary` | Evidence tier (see below) |
| `published_at` | string \| null | yes | ISO date `YYYY-MM-DD`, or `null` when unknown | Publication date; `null` means unknown, never guessed |
| `source_type` | string \| null | no | `official` \| `academic` \| `archive` \| `press` \| `oral` \| `community` \| `mixed`, or `null` | Optional label for the kind of source. **A label only — it never changes the `quality`-based `credible` threshold.** |

### `writing_context[]`

| Field | Type | Required | Allowed values | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `dN.wM` | Unique context id |
| `kind` | string | yes | open tag; the validator only checks it is a non-empty string (e.g. `scope`, `sample`, `method`, `availability`) | What kind of caveat this is |
| `text` | string | yes | non-empty | The caveat itself |
| `source_ids[]` | array | yes | ids in `sources[]` (may be empty) | Sources the caveat is grounded in |
| `applies_to[]` | array | yes | `dN` or `dN.cM` ids (may be empty) | Axis or claims the caveat constrains |
| `use` | string | yes | non-empty | How the writer should use it (e.g. qualify a number) |

`applies_to[]` entries are **pattern-checked only**: each must be `dN` or
`dN.cM`, and the validator does **not** verify that the referenced axis or claim
actually exists in this file.

`kind` is an open tag, but three values carry meaning elsewhere and should be
used verbatim: `availability` records an unreachable source class (see
`protocol.md` §4a — a paywalled or bot-walled primary source you could not open),
`downgrade` marks a claim whose support is `tertiary`-only (rule 1 — the entry
must list that claim id in `applies_to[]` and its `text`/`use` must tell the
writer to show "insufficient evidence / to verify" to the reader), and
`scope`/`sample`/`method` record the other standard caveats. Routing an
access-blocked source into a `kind: "availability"` entry is how the run states
"the conclusion rests on what was reachable" without pretending the blocked page
was read.

### `key_findings[]`

| Field | Type | Required | Allowed values | Meaning |
|---|---|---|---|---|
| `finding` | string | yes | non-empty | One-line synthesis for the Executive Summary / Findings |
| `claim_ids[]` | array | yes | ≥ 1 ids of claims in this same file | Claims the finding is derived from |

`key_findings` is a **derived layer**: it may combine claims but introduces no
fact absent from the claims it cites.

### `gaps[]` (optional)

| Field | Type | Required | Allowed values | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `gN` (1-based, no leading zeros), unique in the file | Gap id |
| `text` | string | yes | non-empty | The unknown, in one sentence |
| `reason` | string | yes | `no-source` \| `access-limited` \| `budget` \| `stale` \| `other` | Why it is unresolved |
| `cost` | string | yes | `cheap` \| `hard` | How expensive closing it would be |
| `source_ids[]` | array | no | ids in `sources[]` (may be empty) | Sources that bear on the gap |

`reason` separates "the material does not exist publicly" (`no-source`) from
"it exists but could not be opened" (`access-limited`) from "the budget ran
out" (`budget`), so a reader can tell a real absence from a self-imposed limit.
The report's `## Gaps & Unknowns` section is generated from `gaps[]`.

## Rules (errors fail the run; warnings do not)

1. **`factual` needs first-hand or credible evidence — or an explicit
   downgrade.** Every claim with `kind: factual` carries at least one `evidence`
   item that resolves either to a source with `quality` of `primary` or
   `secondary`, **or** to a valid entry in `observations[]` — an observation is
   first-hand evidence, so it counts as primary-grade for this rule. A claim
   supported **only** by `tertiary` sources passes only when a
   `writing_context[]` entry with `kind: "downgrade"` lists that claim id in its
   `applies_to[]`; the writer must then show the downgrade ("insufficient
   evidence / to verify") to the reader next to the claim. Without the
   annotation the error is `E_FACTUAL_SOURCE`; with it the run continues and
   reports `W_DOWNGRADE` so the downgrade is visible in the gate output too.
2. **`projective` needs a basis.** Every claim with `kind: projective`
   carries at least one `evidence` item (source or observation, any quality
   tier) recording what the projection is based on. A projection with no source
   is an opinion, and is rejected.
3. **`interpretive` needs two distinct, non-duplicate origins, at least one of
   them credible.** Every claim with `kind: interpretive` has `evidence` items
   pointing at at least two *different origins*, where an origin is either a
   distinct `source_id` whose `url` is distinct from every other source origin
   (compared after `strip()`), or a distinct `observation_id`. Fewer than two
   distinct resolvable origins, or two or more `source_id`s that all share one
   identical `url` (a duplicate source is one origin, not two), both fail as
   `E_INTERPRETIVE_TWO`. **Additionally at least one origin must be `primary`/
   `secondary` (or an observation)** — a `tertiary` source may be the second
   origin but never the only pillar; two `tertiary` origins fail as
   `E_INTERPRETIVE_CREDIBLE`. Note that this is only *source-level*
   independence: origin-level independence (same publisher publishing on
   different domains) is a judgement the gate cannot enforce — see
   `protocol.md` §5.
4. **No normative claims — best-effort heuristic, WARNING only (C5).** The skill
   states what the evidence shows, not what anyone should do. Because this
   cannot be decided mechanically, the validator only runs a
   **fixed-phrase heuristic**: it lowercases each claim's `text` and looks for a
   word-boundary, case-insensitive hit on this exact list —
   `should`, `ought to`, `we recommend`, `is recommended`, `are recommended`,
   `best practice`, `advisable`, `must adopt` —
   reported as `W_NORMATIVE`, **a warning that never fails the run**.
   Rationale: the phrase list cannot distinguish a descriptive paraphrase
   ("the docs recommend X") from a prescription, and a heuristic must not
   consume a run's single fix chance. The phrase list stays pinned and
   unchanged; a normative claim that avoids every listed phrase will pass, so
   the writer must still keep prescriptions out of `claims[]`.
5. **Referential integrity.** Every `evidence[].source_id` and every
   `writing_context[].source_ids[]` entry resolves to an id present in
   `sources[]`; every `evidence[].observation_id` resolves to an id present in
   `observations[]`; every `key_findings[].claim_ids[]` entry resolves to a claim id
   in this file; every `answers_key_question` value matches `kqN`.
   (`writing_context[].applies_to[]` is deliberately **not** part of this rule —
   it is pattern-checked only, see above.)
6. **Enum membership and id patterns.** `kind`, `polarity` and `quote_type`
   values come only from the allowed sets above (observation `kind` included);
   ids match their patterns (`dN.cM`, `dN.wM`, `kqN`, `oN`); ids are unique
   within their array. The shape and uniqueness of observation ids are reported
   as `E_OBS_SHAPE`.
7. **Minimum contents.** `claims[]` and `sources[]` must each contain at least
   one entry; an empty `claims` or empty `sources` array is an error (`E_EMPTY`).
   Separately, an empty `key_findings` array is a **warning** (`W_NO_FINDINGS`)
   that does not fail the run. An empty `writing_context` array is legitimate
   and produces neither, and an empty or absent `observations` array is
   legitimate too and produces no entry at all.
8. **Missing `refute` coverage is a WARNING, not an error.** If no claim in the
   file has `polarity: refute`, the validator reports a warning (falsification
   was probably not attempted) but does not fail on it alone.
9. **`background` needs context evidence, not credibility; key findings need a
   real basis.** A `background` claim (period, place, people, prior events)
   carries at least one evidence item of **any** quality tier, or an
   observation, and is **exempt** from rule 1. It need not answer a `kqN`
   (`answers_key_question` may be `null`). A `background` claim may **not** back
   a `key_finding` — that is `E_FINDING_BACKGROUND`. A `key_finding` is a
   load-bearing conclusion ("核心发现"): the claims it references must together
   provide **at least two distinct origins with at least one `primary`/
   `secondary` origin (or an observation)** — reported as `E_FINDING_BASIS`.
10. **`gaps[]` shape.** Each gap carries `id` (`gN`), `text`, `reason` and
    `cost`; a missing or malformed field is `E_GAP_SHAPE`, a bad `reason`/`cost`
    is `E_GAP_ENUM`, and every `source_ids[]` entry must resolve to `sources[]`
    (`E_GAP_REF`).

**Error codes** (`ok: false`, exit 1): `E_SHAPE`, `E_ID_PATTERN`,
`E_ID_UNIQUE`, `E_ENUM`, `E_REF_SOURCE`, `E_REF_OBSERVATION`, `E_REF_CLAIM`,
`E_REF_KQ`, `E_FACTUAL_SOURCE`, `E_INTERPRETIVE_TWO`, `E_INTERPRETIVE_CREDIBLE`,
`E_PROJECTIVE_BASIS`, `E_BACKGROUND_BASIS`, `E_FINDING_BACKGROUND`,
`E_FINDING_BASIS`, `E_OBS_SHAPE`, `E_EMPTY`, `E_GAP_SHAPE`, `E_GAP_ENUM`,
`E_GAP_REF` — plus `E_JSON` for unusable input (exit 2), and the `--plan` codes
`E_PLAN_DIM_UNKNOWN` / `E_PLAN_DIM_UNCOVERED`.
**Warning codes** (`ok` stays `true`): `W_NORMATIVE` (rule 4), `W_NO_FINDINGS`
and `W_NO_REFUTE` (rules 7 and 8), `W_DOWNGRADE` when rule 1 is satisfied by a
tertiary-only claim carrying its downgrade annotation, `W_KQ_UNANSWERED` when
`--plan` is used, and `W_SAME_PUBLISHER` when an `interpretive` claim's distinct
urls all share one publisher root (a heuristic hint that they may be one outlet
restating one story, never a failure).
There is no `E_NORMATIVE` any more: C5 downgraded rule 4 to `W_NORMATIVE`.

So rules 1–3, 5 and 6 plus the `claims`/`sources` half of rule 7 and the
key-finding half of rule 9 land in `errors[]` and stop the run; rule 4, the
`key_findings` half of rule 7, rule 8 and the `W_DOWNGRADE` path of rule 1 land
in `warnings[]` while `ok` stays `true`.
The validator's stdout shape is a single JSON object
`{"ok": bool, "errors": [...], "warnings": [...]}`, sorted by `code` then
`where`; `ok` is `true` if and only if `errors` is empty.

| each entry is `{"code", "message", "where"}` plus an **optional `hint`** — a
"smallest safe fix" suggestion present only on error codes that have one clear
corrective action (`E_FACTUAL_SOURCE`, `E_INTERPRETIVE_TWO`,
`E_INTERPRETIVE_CREDIBLE`, `E_FINDING_BASIS`, `E_PROJECTIVE_BASIS`,
`E_BACKGROUND_BASIS`, `E_FINDING_BACKGROUND`, `E_REF_SOURCE`,
`E_REF_OBSERVATION`, `E_REF_CLAIM`, `E_PLAN_DIM_UNKNOWN`,
`E_PLAN_DIM_UNCOVERED`). `hint` is additive: a consumer keyed on
`code`/`where` is unaffected, and a run that must repair itself reads `hint` to
apply the one fix most likely to clear the error without dropping a claim it did
not need to drop. It is absent everywhere else, including on a clean pass.

## Source quality tiers

| Tier | Meaning | Examples |
|---|---|---|
| `primary` | The thing itself | Official docs, regulatory filings, raw data, the original paper |
| `secondary` | Reporting or analysis *about* the thing | News report, review article, expert commentary |
| `tertiary` | Aggregated or encyclopedic | Encyclopedia entry, roundup, aggregated index |

`tertiary` sources may support `interpretive` claims (as one of two, never as
the only pillar) and may support a `factual` claim only when the claim carries
the `downgrade` annotation (rule 1).

An observation is **not** a `sources[]` entry: it lives in `observations[]`,
has no `url`, and is first-hand by construction, so it satisfies `factual`
(rule 1) on its own and counts as one origin for `interpretive` (rule 3).

## `writing_context` and `projective` claims

`writing_context` records **scope and caveats** — sample size, method,
geographic or time-window limits, availability gaps — separately from claims, so
a qualifier can constrain how a number is stated without rewriting the claim.
Route each caveat into the report through its `use` field.

`kind: projective` marks a statement as a **projection or forecast, not a fact**.
Projective claims must read as projections ("X is projected to ..."), must cite
their source, and are never promoted to `factual` in the report.

## `plan.json`

The research plan produced during the Plan phase, consumed by
gate ①: `meld.py prepare` adds the `--plan` flag automatically whenever
`.work/plan.json` exists (raw form `check_evidence.py --plan`). Its frozen shape is:

```json
{
  "tier": "normal",
  "genre": "general",
  "assumptions": ["what the run assumed when the host could not ask the user"],
  "dimensions": [
    {
      "id": "d1",
      "name": "human readable dimension name",
      "scope_ownership": "what this axis owns; must not overlap another axis",
      "source_classes": ["primary", "secondary"],
      "depth": "free-text stopping threshold description",
      "time_sensitivity": "window | sensitive | stable",
      "key_questions": [{"id": "kq1", "text": "the question"}],
      "must_have_materials": [
        {"text": "the material the axis must obtain", "status": "obtained", "note": "where it came from"}
      ]
    }
  ]
}
```

`check_evidence.py --plan` reads `dimensions[].id`, `dimensions[].key_questions[].id`,
`genre` (enum) and `dimensions[].must_have_materials[]` (shape + `status` enum) —
the machine-checked contract (claim axes must be declared, every dimension must
be covered, every declared key question must be answered, `genre` is in its
enum, and each must-have material has a `status` in
`obtained | missing | unknown`). Every other field (`tier`, `assumptions`,
`name`, `scope_ownership`, `source_classes`, `depth`, `time_sensitivity`, and
each key question's `text`) is human-readable metadata that the validator
ignores. `assumptions[]` is where a `normal` run records the scope assumptions
it made when the host could not ask the user (see `SKILL.md` §4).

`genre` is one of `panorama | comparison | entity | chronicle | general`
(default `general`); it selects a genre template at write time (see
`report-template.md`). `must_have_materials[]` is the axis's checklist of the
material it must actually obtain: at wrap-up, every `missing` item must be
written to `gaps[]`, and the delivery message reports "key material: obtained X
/ missing Y".

**One source needed by two axes (C7).** The owning axis declares it in its
`scope_ownership` (e.g. *"owns example.org/announcements/\*"*) so the two
retrieval scopes still do not overlap; after the per-axis
`sub_reports/dN.evidence.json` files are merged into one `evidence.json`, the
other axis's claims reference that **same `source_id`**. A shared source is
entered once and never duplicated under a second id — merge folds duplicates,
and two ids for one URL would defeat the origin counting in rule 3. The same
holds for a key question both axes answer: one `kqN`, shared (see *ID
conventions*).

## Valid example

One axis, two claims (one `factual`, one `interpretive`), two sources of
different quality, one writing context, one key finding:

```json
{
  "claims": [
    {
      "id": "d1.c1",
      "text": "The library reached 10k stars within three months of release.",
      "kind": "factual",
      "polarity": "support",
      "topic_tag": "adoption",
      "answers_key_question": "kq1",
      "evidence": [
        {"source_id": "s1", "snippet": "Repository statistics show 10,042 stars as of 2026-06-30.", "quote_type": "numeric"}
      ]
    },
    {
      "id": "d1.c2",
      "text": "Adoption was driven mainly by the zero-dependency design rather than by marketing.",
      "kind": "interpretive",
      "polarity": "refute",
      "topic_tag": "adoption",
      "answers_key_question": "kq1",
      "evidence": [
        {"source_id": "s1", "snippet": "The announcement highlights 'no runtime dependencies' as the core goal.", "quote_type": "direct"},
        {"source_id": "s2", "snippet": "Growth coincided with maintainer posts about installation size, not campaigns.", "quote_type": "paraphrase"}
      ]
    }
  ],
  "sources": [
    {"id": "s1", "url": "https://example.org/announcements/v1", "title": "v1.0 release announcement", "quality": "primary", "published_at": "2026-04-02"},
    {"id": "s2", "url": "https://example-news.example/2026/06/adoption-analysis", "title": "Why the library took off", "quality": "secondary", "published_at": "2026-06-15"}
  ],
  "writing_context": [
    {"id": "d1.w1", "kind": "availability", "text": "Star counts are a snapshot; historical daily data is not publicly archived.", "source_ids": ["s1"], "applies_to": ["d1.c1"], "use": "Date-stamp the star figure instead of presenting it as a trend."}
  ],
  "key_findings": [
    {"finding": "Adoption was fast and, per two independent sources, driven by design choices rather than promotion.", "claim_ids": ["d1.c1", "d1.c2"]}
  ]
}
```
