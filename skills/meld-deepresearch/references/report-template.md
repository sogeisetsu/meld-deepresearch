# Report Template

Structure and writing rules for the research report. The **report body is
written in the end user's language**; this template file is English and stays
English.

## Skeleton (exact order)

1. `# Title`
2. `## Executive Summary`
3. `## Findings`
4. `## Contradictions & Counter-evidence`
5. `## Gaps & Unknowns`
6. `## Sources`

| Section | What belongs here |
|---|---|
| `# Title` | Specific, scope-revealing (topic + angle), not a generic label |
| `## Executive Summary` | 3–6 sentences: the answer, the biggest caveat, the confidence level; grounded in `key_findings[]`; **any figure stated here carries a `[^source_id]` marker** — summarising `key_findings[]` without markers is allowed only when the ES states no figures |
| `## Findings` | One finding per subsection/bullet, each carrying inline citations; may be grouped by axis `dN` |
| `## Contradictions & Counter-evidence` | **Mandatory, never empty.** Sources that disagree, failed or disconfirmed claims, and why the report leaned one way; if genuinely nothing contradicts, say so explicitly and cite what was checked |
| `## Gaps & Unknowns` | Questions the evidence could not answer, each labeled `unknown` with the reason (no source found, access limited, data stale) — never a guess |
| `## Sources` | Owned by `render_citations.py`: numbered citation list for every source the report cites, regenerated wholesale by the renderer. The writer ends `report.src.md` with this heading and nothing after it |

## Inline citation mechanism

While drafting (`report.src.md`), cite with a footnote marker keyed to the
source id from `evidence.json`:

```markdown
Adoption accelerated after the v1.0 release.[^s1]
```

- Marker form: `[^source_id]`, where `source_id` is an id in `evidence.json`'s
  `sources[]`.
- A later script (`render_citations.py`) converts markers into numbered
  citations and emits `citations.json`.
- **The model never hand-numbers citations** and never invents `[1]`-style
  markers or a manual bibliography; numbering belongs to the script.
- **`render_citations.py` owns `## Sources`:** it regenerates everything after
  that heading (appending the heading only if the draft lacks it).
  `report.src.md` must **end with a `## Sources` heading and nothing after
  it** — the writer never writes the list itself.
- Gate ② vocabulary, matching `render_citations.py` exactly:
  - **orphan** — a `[^source_id]` marker whose id is **absent from
    `sources[]`** → gate ② fails.
  - **unresolved** — a marker left un-replaced (empty id, or a residual `[^`
    in the rendered output) → gate ② fails.
  - **uncited** — a source present in `sources[]` that the report never cites →
    **warning only**, never a failure.
- **`sources.md` is not `## Sources`.** `sources.md` is the standalone
  de-duplicated source table (a deliverable produced by `dedupe_sources.py`);
  the report's `## Sources` is the numbered citation list produced by the
  renderer. Same sources, different purpose — do not confuse them.

## Writing rules

- **Statement strength never exceeds evidence strength.** "Proves" needs a
  primary source on a settled fact; one secondary source gets "suggests";
  projections stay explicitly projected.
- **No new facts.** Everything asserted in the report exists in
  `evidence.json`; the report adds structure and synthesis, not evidence.
- **Every number is traceable.** Each figure carries a `[^source_id]` marker
  in every section — the Executive Summary included — and matches the snippet
  recorded for it (date-stamped when time-sensitive).
- **Attribute and hedge.** Contested points name who says what instead of
  asserting a single view.
- **Label the unknown.** Unanswered items are written as `unknown`, never
  filled by plausibility.

## Quality self-check (four dimensions)

Ask each question before delivering; fix the report, not the answers.

| Dimension | What good looks like | Check question |
|---|---|---|
| Comprehensiveness | All axes, key questions and their counter-evidence covered | Did any `kqN`, axis, or contradiction go unmentioned? |
| Insight | Findings synthesize *why* and *so what*, not a link dump | Does each finding say something the sources individually did not? |
| Instruction-following | Skeleton order, language, scope and format as requested | Does the report match the requested language, scope and sections? |
| Readability | Scannable headings, short paragraphs, plain wording, consistent terms | Would a reader get the answer from the summary alone? |

## Do / Don't

| Do | Don't |
|---|---|
| Attribute claims to their sources and hedge appropriately | Publish a claim backed only by a single `tertiary` source |
| Cite every factual statement and every number with `[^source_id]`, including figures in the Executive Summary | Leave a marker orphaned (id absent from `sources[]`) or unresolved (left un-replaced) |
| State counter-evidence and where the disagreement lies | Present only the confirming side |
| Report what the evidence shows | State recommendations or prescriptions as findings |
| Write unanswered items as `unknown` with a reason | Guess or silently drop a question |
| Let the script number the citations and emit `## Sources` | Hand-number citations or write a reference list by hand — the renderer owns `## Sources` |
