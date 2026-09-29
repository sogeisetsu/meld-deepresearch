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
| `## Executive Summary` | 3–6 sentences: the answer, the biggest caveat, the confidence level; grounded in `key_findings[]`; citations allowed |
| `## Findings` | One finding per subsection/bullet, each carrying inline citations; may be grouped by axis `dN` |
| `## Contradictions & Counter-evidence` | **Mandatory, never empty.** Sources that disagree, failed or disconfirmed claims, and why the report leaned one way; if genuinely nothing contradicts, say so explicitly and cite what was checked |
| `## Gaps & Unknowns` | Questions the evidence could not answer, each labeled `unknown` with the reason (no source found, access limited, data stale) — never a guess |
| `## Sources` | Every source referenced by the report: id, title, URL, quality tier, publication date |

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
- Every marker must resolve to a known source id (unresolved or orphaned
  markers fail the render gate).

## Writing rules

- **Statement strength never exceeds evidence strength.** "Proves" needs a
  primary source on a settled fact; one secondary source gets "suggests";
  projections stay explicitly projected.
- **No new facts.** Everything asserted in the report exists in
  `evidence.json`; the report adds structure and synthesis, not evidence.
- **Every number is traceable.** Each figure carries a `[^source_id]` marker
  and matches the snippet recorded for it (date-stamped when time-sensitive).
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
| Cite every factual sentence and every number with `[^source_id]` | Leave a citation marker orphaned or pointing at an unknown id |
| State counter-evidence and where the disagreement lies | Present only the confirming side |
| Report what the evidence shows | State recommendations or prescriptions as findings |
| Write unanswered items as `unknown` with a reason | Guess or silently drop a question |
| Let the script number the citations | Hand-number citations or build a manual reference list |
