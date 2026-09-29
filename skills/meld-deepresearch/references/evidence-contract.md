# Evidence Contract — `evidence.json`

The data contract for the structured evidence file. A validator script
(`scripts/check_evidence.py`, written in a later milestone) enforces every rule
below; a file that fails validation is not delivered. Field names, object names
and enum values here are **exact** — the validator matches them literally.

## Top-level shape

`evidence.json` is one JSON object with five arrays:

| Array | What it holds |
|---|---|
| `claims[]` | Atomic statements the report may make, each with its own evidence |
| `sources[]` | Every source any claim or context refers to, with a quality tier |
| `writing_context[]` | Scope, sample, method and availability caveats, kept out of claims |
| `key_findings[]` | Derived synthesis that points back to claims; adds no new facts |

(`evidence[]` is nested inside each claim; it is not a top-level array.)

## ID conventions

| Pattern | Meaning |
|---|---|
| `dN` | Research axis / dimension `N` (1-based, no leading zeros) |
| `dN.cM` | Claim `M` under axis `N` — e.g. `d2.c1` |
| `kqN` | Key question `N`, generated during planning; claims answer or are `null` |
| `dN.wM` | Writing-context entry `M` under axis `N` |
| `sN` | Source `N`. Only uniqueness and referential integrity are enforced; any opaque, unique string is accepted |

## Field reference

### `claims[]`

| Field | Type | Required | Allowed values | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `dN.cM` | Unique claim id |
| `text` | string | yes | non-empty | The statement, one atomic assertion |
| `kind` | string | yes | `factual` \| `interpretive` \| `projective` | Fact / interpretation / projection |
| `polarity` | string | yes | `support` \| `refute` \| `neutral` | Which side of the question the claim takes |
| `topic_tag` | string | yes | non-empty | Free tag grouping claims by topic |
| `answers_key_question` | string \| null | yes | `kqN` or `null` | Key question this claim answers, if any |
| `evidence[]` | array | yes | ≥ 1 for `factual` (primary/secondary); ≥ 1 for `projective`; ≥ 2 distinct sources for `interpretive` | Supporting snippets; see below |

### `evidence[]` (inside a claim)

| Field | Type | Required | Allowed values | Meaning |
|---|---|---|---|---|
| `source_id` | string | yes | must exist in `sources[]` | Which source this snippet comes from |
| `snippet` | string | yes | non-empty | Verbatim or closely paraphrased excerpt actually read in the source |
| `quote_type` | string | yes | `direct` \| `paraphrase` \| `numeric` | How the snippet relates to the source text |

A search-result summary is never evidence: the snippet must come from the
opened source itself.

### `sources[]`

| Field | Type | Required | Allowed values | Meaning |
|---|---|---|---|---|
| `id` | string | yes | unique | Source id referenced by `evidence[].source_id` |
| `url` | string | yes | resolvable URL | Where the source was read |
| `title` | string | yes | non-empty | Source title |
| `quality` | string | yes | `primary` \| `secondary` \| `tertiary` | Evidence tier (see below) |
| `published_at` | string \| null | yes | ISO date `YYYY-MM-DD`, or `null` when unknown | Publication date; `null` means unknown, never guessed |

### `writing_context[]`

| Field | Type | Required | Allowed values | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `dN.wM` | Unique context id |
| `kind` | string | yes | non-empty tag (`scope`, `sample`, `method`, `availability`, ...) | What kind of caveat this is |
| `text` | string | yes | non-empty | The caveat itself |
| `source_ids[]` | array | yes | ids in `sources[]` (may be empty) | Sources the caveat is grounded in |
| `applies_to[]` | array | yes | `dN` or `dN.cM` ids (may be empty) | Axis or claims the caveat constrains |
| `use` | string | yes | non-empty | How the writer should use it (e.g. qualify a number) |

### `key_findings[]`

| Field | Type | Required | Allowed values | Meaning |
|---|---|---|---|---|
| `finding` | string | yes | non-empty | One-line synthesis for the Executive Summary / Findings |
| `claim_ids[]` | array | yes | ≥ 1 ids of claims in this same file | Claims the finding is derived from |

`key_findings` is a **derived layer**: it may combine claims but introduces no
fact absent from the claims it cites.

## Hard rules (these can FAIL the run)

1. **`factual` needs a credible source.** Every claim with `kind: factual`
   carries at least one `evidence` item whose source has `quality` of
   `primary` or `secondary`. `tertiary` alone fails.
2. **`projective` needs a basis.** Every claim with `kind: projective`
   carries at least one `evidence` item (any quality tier) recording what the
   projection is based on. A projection with no source is an opinion, and is
   rejected.
3. **`interpretive` needs two distinct sources.** Every claim with
   `kind: interpretive` has `evidence` items pointing at at least two
   *different* `source_id` values.
4. **No normative claims.** Claims that say what anyone *should* do
   ("ought to", "must adopt", "we recommend") are forbidden. The skill states
   what the evidence shows, not what anyone should do.
5. **Referential integrity.** Every `evidence[].source_id` and every
   `writing_context[].source_ids[]` entry resolves to an id present in
   `sources[]`; every `key_findings[].claim_ids[]` entry resolves to a claim id
   in this file; every `answers_key_question` value matches `kqN`.
6. **Enum membership.** `kind`, `polarity` and `quote_type` values come only
   from the allowed sets above; ids match their patterns (`dN.cM`, `dN.wM`,
   `kqN`); ids are unique within their array.
7. **Missing `refute` coverage is a WARNING, not an error.** If no claim in the
   file has `polarity: refute`, the validator reports a warning (falsification
   was probably not attempted) but does not fail on it alone.

Rules 1–6 are errors: the validator returns `{"ok": false, "errors": [...]}`
and the run stops. Rule 7 is reported in `warnings[]` while `ok` stays `true`.
The validator's stdout shape is `{"ok": bool, "errors": [...], "warnings": [...]}`.

## Source quality tiers

| Tier | Meaning | Examples |
|---|---|---|
| `primary` | The thing itself | Official docs, regulatory filings, raw data, the original paper |
| `secondary` | Reporting or analysis *about* the thing | News report, review article, expert commentary |
| `tertiary` | Aggregated or encyclopedic | Encyclopedia entry, roundup, aggregated index |

`tertiary` sources may support `interpretive` claims (as one of two) but never
carry a `factual` claim alone.

## `writing_context` and `projective` claims

`writing_context` records **scope and caveats** — sample size, method,
geographic or time-window limits, availability gaps — separately from claims, so
a qualifier can constrain how a number is stated without rewriting the claim.
Route each caveat into the report through its `use` field.

`kind: projective` marks a statement as a **projection or forecast, not a fact**.
Projective claims must read as projections ("X is projected to ..."), must cite
their source, and are never promoted to `factual` in the report.

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
