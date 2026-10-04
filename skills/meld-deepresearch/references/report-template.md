# Report Template

Structure and writing rules for the research report. The **report body is
written in the end user's language**; this template file is English and stays
English.

## Skeleton (exact order)

Required sections are always present, in this order, under these titles. Write
the report in the user's language: the Chinese form is given where it exists,
and any other language keeps this order (translating the titles is fine).

| # | English | Chinese |
|---|---|---|
| 1 | `# Title` | `# 标题` |
| 2 | `## Executive Summary` | `## 摘要` |
| 3 | `## Findings` | `## 主要发现` |
| 4 | `## Contradictions & Counter-evidence` | `## 矛盾与反证` |
| 5 | `## Gaps & Unknowns` | `## 未知与缺口` |
| 6 | `## Sources` | `## 来源` |
| 7 | `## Observations` | `## 观测记录` |

Sections 6 and 7 are **renderer-owned**: `## Sources` is regenerated wholesale,
and `## Observations` is appended only when at least one observation is cited.
The writer never writes either; the renderer matches both the English and the
Chinese heading forms.

**Genre templates only APPEND.** A genre template (see *Genre templates* below)
adds sections *after* `## Findings`; it never removes, reorders or renames the
required sections above.

| Section | What belongs here |
|---|---|
| `# Title` | Specific, scope-revealing (topic + angle), not a generic label |
| `## Executive Summary` | **A TL;DR, not a dense paragraph.** Use 3–5 short bullets (or at most 4 sentences); each line carries at most one figure and reads on its own. Order: ① the direct answer ② the single strongest piece of supporting evidence ③ **the strongest counter-evidence — by the third line, never buried** ④ the confidence level and the biggest caveat. Do not restate Findings verbatim or stack many figures into one line. A reader who reads only this block must get the answer and the main doubt |
| `## Findings` | One finding per subsection/bullet, each carrying inline citations; may be grouped by axis `dN` |
| `## Contradictions & Counter-evidence` | **Mandatory, never empty, and it opens with the strongest counter-evidence.** The first line is `**Strongest counter-evidence:**` naming the single most damaging refuting finding against the report's main answer, and why it is the strongest. Then the remaining disagreements, each carrying its uncertainty grade. If genuinely nothing contradicts, say so explicitly, still under that line, and cite what was checked |
| `## Gaps & Unknowns` | Questions the evidence could not answer, each labeled `unknown` with the reason (no source found, access limited, data stale) — never a guess |
| `## Sources` | Owned by `render_citations.py`: numbered citation list for every source the report cites, regenerated wholesale by the renderer. The writer ends `report.src.md` with this heading and nothing after it |
| `## Observations` | Owned by `render_citations.py`: appended **only when at least one observation is cited**, one line per cited observation — default GFM mode drops the heading and emits `[^oN]: method — environment (captured YYYY-MM-DD)`; `--legacy-plain` uses `[ON] method — …`. The writer never writes this section |

## Requested structure overrides the skeleton

The skeleton above is the **default**. When the request names a chapter count, an
outline, or a required section list, that structure is **binding**: the report's
numbered top-level chapters follow the request exactly (e.g. "5–6 个章节" ⇒ five
or six numbered chapters, not the default set).

- Remap the required content into the requested chapters. `Executive Summary`,
  `Contradictions & Counter-evidence`, `Gaps & Unknowns` and the genre sections
  are satisfied *inside* those chapters or in one non-numbered
  `## 附录：方法与局限` (Appendix: method & limits) — not as extra numbered
  chapters. The renderer-owned `## Sources` / `## Observations` remain; they are
  reference blocks, not chapters.
- A binding structure may reduce the chapter count, never the evidence rules:
  every number still carries a citation, the strongest counter-evidence still
  opens the contradictions material, unknowns are still labelled.
- **Match the requested register and length.** "正式、简洁 / formal and concise"
  means a concise formal report, not an academic monograph.
  - Keep external citations to sources that actually carry a claim; do not pad the
    body with background literature — the reference list is support, not content.
  - When the request implies a management deliverable (e.g. "解释数据背后的管理
    含义", an executive audience), include the corresponding business section — a
    consolidated `结论与改进建议` / *Conclusions & Recommendations* chapter — not
    just a research summary.
  - Respect a stated length target: keep the body within it and move method,
    observation detail and secondary contradictions into a compact, non-numbered
    appendix (they still live in the evidence files for axis G).
  - Do not surface internal identifiers (`kqN`, `dN`, axis codes) in the body —
    keep that apparatus in the appendix or the evidence files.

## Genre templates

A genre is chosen at plan time (`plan.json` `genre`) and only *adds* sections
after `## Findings`. The four templates live in `templates/genres/`:

| Genre | Appends after `## Findings` |
|---|---|
| `panorama` | Background & current state, Core dimension 1..N, Synthesis, Outlook, Appendix |
| `comparison` | Evaluation basis (needs / dimensions / weights), Option overview, **Comparison matrix — a table is required**, Per-dimension analysis, Recommendation, Risks & limits |
| `entity` | Subject profile, Operations, Financials, Legal / compliance, Team, Red flags, Conclusion & recommendation |
| `chronicle` | **Background & people** (consumes `background` claims), Timeline, Key-node analysis, Evidence & disputes, Conclusion & aftermath, Appendix |

`general` (the default) appends nothing. A genre template never replaces or
renames a required section.

## Uncertainty grading (D3)

Every disagreement in `## Contradictions & Counter-evidence` carries one of
three explicit grades — never a binary verdict:

- `已确认` / **confirmed** — independent origins agree, or one primary source settles it.
- `存在争议` / **in dispute** — credible sources disagree and the run cannot adjudicate.
- `无法证实` / **unconfirmed** — the point cannot be checked from reachable evidence.

The grade sits next to the disputed point and is re-checked in the quality
self-check. It adds no schema field: it is a writing rule over existing claims.

## Inline citation mechanism

While drafting (`report.src.md`), cite with a footnote marker keyed to an id
from `evidence.json`:

```markdown
Adoption accelerated after the v1.0 release.[^s1]
The host's installed CLI reports version 2.100.0.[^o1]
```

Two marker families, cited exactly alike:

- `[^sN]` — a **source**: `sN` is an id in `evidence.json`'s `sources[]`.
- `[^oN]` — a **first-hand observation**: `oN` is an id in
  `evidence.json`'s `observations[]` (a command run, a measurement taken, a
  file inspected). Observations are evidence like any other; the renderer keeps
  `[^oN]` in the default GFM-footnote mode (`--legacy-plain` renders `[ON]`).
- A later script (`render_citations.py`) converts markers into numbered
  citations and emits `citations.json`. **The default output is GFM footnotes**
  (`[^N]` / `[^oN]` plus definitions) so that a GFM renderer such as GitHub
  shows a numbered superscript that jumps on its own — no inline HTML, nothing
  for an HTML sanitiser to strip. `--anchors` opts into the older
  `[[N]](#ref-N)` + `<a id>` form, and `--legacy-plain` into bare `[N]` text.
- **The model never hand-numbers citations** and never invents `[1]`-style
  markers or a manual bibliography; numbering belongs to the script.
- **`render_citations.py` owns `## Sources`:** it regenerates everything after
  that heading (appending the heading only if the draft lacks it).
  `report.src.md` must **end with a `## Sources` heading and nothing after
  it** — the writer never writes the list itself. In the default GFM-footnote
  mode the heading is **removed** and the list becomes `[^N]: ...` definitions,
  so the GFM renderer wires them into its own numbered footnotes block.
- **`render_citations.py` owns `## Observations` too:** it appends that section
  after `## Sources` **only when the report cites at least one observation**,
  one line per cited observation. In the default GFM-footnote mode the heading
  is removed and each line becomes
  `[^oN]: method — environment (captured YYYY-MM-DD)`; `--legacy-plain` uses
  `[ON] method — ...`. The writer never writes this section either — same
  ownership rule as `## Sources`.
- Gate ② vocabulary (orphan / unresolved / uncited) is defined in `protocol.md` §9.
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
- **Every number is traceable.** Each figure carries a `[^sN]` or `[^oN]` marker
  in every section — the Executive Summary included — and matches the snippet
  recorded for it (date-stamped when time-sensitive).
- **First-hand observations are ordinary evidence.** A claim based on an
  observation is cited with `[^oN]` exactly like a sourced claim, and nothing
  else changes: the `Contradictions & Counter-evidence` and `Gaps & Unknowns`
  rules apply to it unchanged, and an observation never upgrades a claim's
  strength by itself.
- **Attribute and hedge.** Contested points name who says what instead of
  asserting a single view.
- **Write plainly and short.** The Executive Summary is a TL;DR, not a paragraph:
  3–5 bullets, one figure per line, each line readable on its own. If a line needs
  a second read to parse, split it. Never restate the Findings verbatim — the
  summary states the answer and the doubt, the body supplies the detail.
- **Lead with the strongest counter-evidence.** The single most damaging
  refutation appears **in the Executive Summary by the third line** and again as
  the opening `**Strongest counter-evidence:**` line of `## Contradictions &
  Counter-evidence`. Never bury it at the bottom of a long list.
- **Keep analytical claims on strong ground.** A conclusion about *what a number
  means* (a unit mismatch, a selection effect, a causal reading) is `interpretive`:
  it should rest on at least one primary or secondary origin, not only on a blog
  or a tertiary aggregator. If only weak origins exist, either soften it to a
  labelled interpretation or mark the point `unknown`.
- **Label the unknown.** Unanswered items are written as `unknown`, never
  filled by plausibility.
- **Diagrams are optional and evidence-bound.** A diagram is a text-based
  Mermaid fence (```` ```mermaid ````) whose data points all come from cited
  claims; never invent a data point to make a chart look complete. Binary
  image or chart rendering is out of scope for this skill.

## Quality self-check (four dimensions)

Ask each question before delivering; fix the report, not the answers.

| Dimension | What good looks like | Check question |
|---|---|---|
| Comprehensiveness | All axes, key questions and their counter-evidence covered | Did any `kqN`, axis, or contradiction go unmentioned? |
| Insight | Findings synthesize *why* and *so what*, not a link dump | Does each finding say something the sources individually did not? |
| Instruction-following | Requested structure, language, scope, tone and format; skeleton only when the request is silent | If a chapter count / outline / tone was requested, does the body match it exactly (no extra chapters, no internal codes)? |
| Readability | Scannable headings, short paragraphs, plain wording, consistent terms | Would a reader get the answer from the summary alone? |

## Do / Don't

| Do | Don't |
|---|---|
| Attribute claims to their sources and hedge appropriately | Publish a claim backed only by a single `tertiary` source |
| Cite every factual statement and every number with `[^sN]` or `[^oN]`, including figures in the Executive Summary | Leave a marker orphaned (id absent from `sources[]` / `observations[]`) or unresolved (left un-replaced) |
| Cite a first-hand observation with `[^oN]` and record its method so it is reproducible — a command must be re-runnable | Rest on an observation nobody could repeat: an unrecorded command, or a method with no `method`/`command` detail |
| State counter-evidence and where the disagreement lies | Present only the confirming side |
| Put the strongest counter-evidence on its own `**Strongest counter-evidence:**` line, up front | Bury the strongest refutation as the last bullet of a long list |
| Keep the Executive Summary short and plain — answer first, one idea per sentence | Cram many figures and clauses into one run-on sentence |
| Report what the evidence shows | State recommendations or prescriptions as findings |
| Write unanswered items as `unknown` with a reason | Guess or silently drop a question |
| Let the script number the citations and emit `## Sources` | Hand-number citations or write a reference list by hand — the renderer owns `## Sources` |
| Honor a requested chapter count / outline / tone exactly — fold discipline material into a non-numbered appendix | Let `Executive Summary` / `Contradictions` / `Gaps` / genre sections push the body past the requested chapters, or expose `kqN` / `dN` codes |
