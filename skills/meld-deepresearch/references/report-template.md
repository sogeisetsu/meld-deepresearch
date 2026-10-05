# Report Template

Structure and writing rules for the research report. The **report body is
written in the end user's language**; this template file is English and stays
English.

## Structure follows the reader's cognitive task

The organising principle of a report is **the cognitive task the reader must
complete**, not the information domain: the same material read for a decision
and read for a mental map needs two different organisations.

- **Domain conventions** (academic / medical / legal / policy) override this
  *only* when the deliverable **is** that document type **and** the reader has
  a strong format expectation of it. Medical or legal content inside a
  business or investment request is chosen by cognitive task first; domain
  terminology is layered on afterwards.
- **Composite intent:** the main intent picks the frame; the secondary intent
  collapses into exactly one section. "First understand the industry, then
  assess one company" → main intent *entity*; the panorama material collapses
  into one "Industry background" section, frame not rebuilt.

## Structure chooser

### Four base structures → genre templates

| The reader's task | Base structure | Genre template |
|---|---|---|
| Understand a space — build a complete mental map (industry, feasibility or trend survey) | Panorama (全景叙述) | `templates/genres/panorama.md` |
| Compare and choose — a documented decision among options (competitive analysis, tech selection, buying decision) | Comparison (对比选型) | `templates/genres/comparison.md` |
| Dig into one subject — understand it fully and form a judgment (due diligence, investment research, person / organisation background) | Entity (实体调查) | `templates/genres/entity.md` |
| Reconstruct an event — what happened, its impact and where it goes (breaking event, crisis, regulatory change) | Chronicle (时序追踪) | `templates/genres/chronicle.md` |

A genre is chosen at plan time (`plan.json` `genre`, one of `panorama |
comparison | entity | chronicle | general`) and only *appends* sections after
`## Findings` (`general`, the default, appends nothing). **Genre templates only
APPEND** — they never remove, reorder or rename a required section.

### Domain-specific shapes — explicit request only

All four shapes are allowed **only when the request explicitly asks for that
document type** and the reader expects its format; otherwise choose by
cognitive task from the table above.

| Shape | Sections (in order) | Special rules |
|---|---|---|
| Academic literature review | Abstract → Introduction (background, review scope, structure) → Research lineages (literature by timeline or school) → Methodology comparison → Synthesis of core findings (consensus and disputes) → Research gaps & outlook → Conclusion → References (academic style) | Every key conclusion points to a specific work; disputes present each side's representative literature; never state a conclusion the literature does not explicitly support |
| Medical / health report | Structured abstract (background / objective / methods / results / conclusion) → Disease or intervention overview → Graded evidence review — Grade A: RCT or systematic review; Grade B: cohort study or authoritative guideline; Grade C: expert opinion or case report → Clinical application notes → Special-population cautions (elderly / children / pregnancy / comorbidities) → Limitations & uncertainties → References | Every recommendation carries its A/B/C evidence grade; drug content states indications and contraindications; uncertainty is labelled explicitly, never implied away |
| Legal memorandum (IRAC) | Issue (the legal question) → Rule (statutes, interpretations, precedent) → Analysis (the facts applied to the rule) → Conclusion (the legal opinion, with its certainty grade) → Appendix (optional: provisions, case summaries) | Name the jurisdiction; cite each provision's version and effective date; state uncertainty — never an opinion more certain than the evidence |
| Policy brief | Executive summary (policy core + recommendations) → Policy background (problem, status quo, history) → Policy content analysis (provisions, goals, mechanism) → Impact assessment (affected groups, economic / social impact, international comparison) → Stakeholder analysis → Recommendations → References | The executive summary must stand alone; recommendations are differentiated per audience (business / government / individuals) |

### What each genre appends after `## Findings`

| Genre | Appends after `## Findings` |
|---|---|
| `panorama` | Background & current state, Core dimension 1..N, Synthesis, Outlook, Appendix |
| `comparison` | Evaluation basis (needs / dimensions / weights), Option overview, **Comparison matrix — a table is required**, Per-dimension analysis, Recommendation, Risks & limits |
| `entity` | Subject profile, Operations, Financials, Legal / compliance, Team, Red flags, Conclusion & recommendation |
| `chronicle` | **Background & people** (consumes `background` claims), Timeline, Key-node analysis, Evidence & disputes, Conclusion & aftermath, Appendix |

## The evidence spine comes first

The structure rules above decide *how the material is organised*; they never
negotiate *what must be verifiable*. Three layers, highest precedence first:

1. **A binding user-requested structure** (chapter count, outline, required
   section list) wins over both layers below — see *Requested structure
   overrides the skeleton*.
2. **The evidence layer** — the required sections, in this exact order, in
   every report. The writer never drops, reorders or renames them.
3. **The cognitive-task structure** — decides how `## Findings` is organised
   internally (by dimension, option, argument or time) and which genre sections
   are appended after it.

| # | English | Chinese |
|---|---|---|
| 1 | `# Title` | `# 标题` |
| 2 | `## Executive Summary` | `## 摘要` |
| 3 | `## Findings` | `## 主要发现` |
| 4 | `## Contradictions & Counter-evidence` | `## 矛盾与反证` |
| 5 | `## Gaps & Unknowns` | `## 未知与缺口` |
| 6 | `## Sources` | `## 来源` |
| 7 | `## Observations` | `## 观测记录` |

Translate the titles when needed; the order stays. Sections 6 and 7 are
**renderer-owned** (`## Sources` regenerated wholesale; `## Observations`
appended only when an observation is cited) and the writer writes neither —
what belongs in each section: *Section-by-section rules* below.

### Requested structure overrides the skeleton

The skeleton above is the **default**. When the request names a chapter count,
an outline, or a required section list, that structure is **binding**: the
numbered chapters follow it exactly (e.g. "5–6 个章节" ⇒ five or six numbered
chapters, not the default set).

- Remap the required content into the requested chapters: `Executive Summary`,
  `Contradictions & Counter-evidence`, `Gaps & Unknowns` and the genre sections
  live *inside* those chapters or in one non-numbered `## 附录：方法与局限`
  (Appendix: method & limits) — never as extra numbered chapters. The
  renderer-owned `## Sources` / `## Observations` remain as reference blocks.
- A binding structure may reduce the chapter count, never the evidence rules:
  every number still carries a citation, the strongest counter-evidence still
  opens the contradictions material, unknowns are still labelled.
- **Match the requested register and length** ("正式、简洁 / formal and
  concise" ⇒ a concise formal report, not an academic monograph): cite only
  sources that carry a claim (no background-literature padding); a management
  deliverable ("解释数据背后的管理含义", an executive audience) gets a
  consolidated `结论与改进建议` / *Conclusions & Recommendations* chapter; a
  stated length target is respected (method, observation detail and secondary
  contradictions move into the non-numbered appendix, still in the evidence
  files); internal identifiers (`kqN`, `dN`, axis codes) never appear.

## Micro-format rules

Each information block takes the format its information type demands:

| Information type | Format | Never |
|---|---|---|
| Multi-object, multi-attribute comparison | **Table** (mandatory) | Describing option by option in paragraphs |
| Time series of events | Timeline table or ordered list | Mixing it into narrative prose |
| Ordered steps / process | Numbered list (1. 2. 3.) | Bullets or prose paragraphs |
| Parallel points (≤ 5) | Bullets | Stacked long paragraphs |
| Causal reasoning / complex analysis | **Connected prose** | Forcing it into bullets |
| Key figures / metrics | Bold or a table | Burying them mid-paragraph |
| Evidence grades / ratings | Label markers (Grade A / 🔴 / Buy) | Describing the grade in prose only |
| Market share / distributions | **Mermaid `pie`** | Listing percentages in text |
| Relations / value chains / flows | **Mermaid `graph` / `flowchart`** | Prose "A → B → C" |
| Trend data (several data points) | **Mermaid `xychart-beta`** | Only saying "it trended upward" |
| Conceptual or illustrative imagery | **Out of scope — Mermaid only** | Binary image generation (no image skill is used) |

## Execution discipline

**Must:** the summary stand alone (a reader who reads only it gets the core
conclusion) · a comparison report contain the matrix table (side-by-side prose
does not count) · every conclusion carry a certainty grade (*Uncertainty
grading (D3)*) · under composite intent the secondary intent collapse into one
section · under a domain shape, its conventions followed strictly without
mixing in other structures.

**Never:** use one generic structure for every request — pick one above ·
split the matrix into per-option paragraphs · let the conclusion list
information without judgment · repeat the same fact in several sections · pad
by restating the body in the summary or the summary in the conclusion.

## Section-by-section rules

| Section | What belongs here |
|---|---|
| `# Title` | Specific, scope-revealing (topic + angle), not a generic label |
| `## Executive Summary` | **A TL;DR, not a dense paragraph.** Use 3–5 short bullets (or at most 4 sentences); each line carries at most one figure and reads on its own. Order: ① the direct answer ② the single strongest piece of supporting evidence ③ **the strongest counter-evidence — by the third line, never buried** ④ the confidence level and the biggest caveat. Do not restate Findings verbatim or stack many figures into one line. A reader who reads only this block must get the answer and the main doubt |
| `## Findings` | One finding per subsection/bullet, each carrying inline citations; organised by the chosen structure, optionally grouped by axis `dN` |
| `## Contradictions & Counter-evidence` | **Mandatory, never empty, and it opens with the strongest counter-evidence.** The first line is `**Strongest counter-evidence:**` naming the single most damaging refuting finding against the report's main answer, and why it is the strongest. Then the remaining disagreements, each carrying its uncertainty grade. If genuinely nothing contradicts, say so explicitly, still under that line, and cite what was checked |
| `## Gaps & Unknowns` | Questions the evidence could not answer, each labeled `unknown` with a reason — reader-facing prose, never a raw `reason` enum (see *Runtime jargon never appears in `report.md`*), never a guess |
| `## Sources` | Owned by `render_citations.py`: numbered citation list for every cited source, regenerated wholesale. The writer ends `report.src.md` with this heading and nothing after it; the renderer materialises it in both output files (footnote block in the cited copy, plain list in the reading copy) |
| `## Observations` | Owned by `render_citations.py`: appended **only when at least one observation is cited**, one line per cited observation — default GFM mode drops the heading and emits `[^oN]: method — environment (captured YYYY-MM-DD)`; `--legacy-plain` uses `[ON] method — …`. The writer never writes this section |

## Inline citation mechanism

While drafting (`report.src.md`), cite with a footnote marker keyed to an id in `evidence.json`:

```markdown
Adoption accelerated after the v1.0 release.[^s1]
The host's installed CLI reports version 2.100.0.[^o1]
```

Two marker families, cited exactly alike:

- `[^sN]` — a **source**: `sN` is an id in `evidence.json`'s `sources[]`.
- `[^oN]` — a **first-hand observation**: `oN` is an id in `evidence.json`'s
  `observations[]` (a command run, a measurement taken, a file inspected).
  Observations are ordinary evidence; GFM mode keeps `[^oN]` (`--legacy-plain`:
  `[ON]`).
- `render_citations.py` converts markers into numbered citations and emits
  `citations.json`. **The default output is GFM footnotes** (`[^N]` / `[^oN]`
  plus definitions) so a GFM renderer shows a numbered superscript that jumps
  on its own — no inline HTML for a sanitiser to strip. `--anchors` opts into
  `[[N]](#ref-N)` + `<a id>`; `--legacy-plain` into bare `[N]`. **The model
  never hand-numbers citations** or invents a manual bibliography.
- **`render_citations.py` owns `## Sources` and `## Observations`:** everything
  after `## Sources` is regenerated, and `## Observations` is appended only
  when an observation is cited — the writer writes neither. In default GFM
  mode both headings disappear from the cited copy and become `[^N]:` /
  `[^oN]: method — environment (captured YYYY-MM-DD)` definitions
  (`--legacy-plain`: `[ON]`); the reading copy gets plain lists (*Dual output*).
- Gate ② vocabulary (orphan / unresolved / uncited) is defined in `protocol.md` §9.
- **`sources.md` is not `## Sources`.** `sources.md` is the standalone
  de-duplicated source table (a `dedupe_sources.py` deliverable); the report's
  `## Sources` is the renderer's numbered citation list — same sources,
  different purpose.

## Uncertainty grading (D3)

Every disagreement in `## Contradictions & Counter-evidence` carries one of
three explicit grades — never a binary verdict:

- `已确认` / **confirmed** — independent origins agree, or one primary source settles it.
- `存在争议` / **in dispute** — credible sources disagree and the run cannot adjudicate.
- `无法证实` / **unconfirmed** — the point cannot be checked from reachable evidence.

The grade sits next to the disputed point and is re-checked in the quality
self-check. It adds no schema field: it is a writing rule over existing claims.

## Writing rules

- **Statement strength never exceeds evidence strength.** "Proves" needs a
  primary source on a settled fact; one secondary source gets "suggests";
  projections stay explicitly projected.
- **No new facts.** Everything asserted exists in `evidence.json` (schema and
  hard rules: `evidence-contract.md`); the report adds structure, not evidence.
- **Every number is traceable.** Each figure carries a `[^sN]` or `[^oN]`
  marker in every section — the Executive Summary included — and matches the
  snippet recorded for it (date-stamped when time-sensitive).
- **First-hand observations are ordinary evidence.** Cited with `[^oN]` like a
  sourced claim; the `Contradictions` and `Gaps` rules apply unchanged, and an
  observation never upgrades a claim's strength by itself.
- **Attribute and hedge.** Contested points name who says what instead of
  asserting a single view.
- **Write plainly and short.** The Executive Summary is a TL;DR: 3–5 bullets,
  one figure per line, each line readable on its own; if a line needs a second
  read to parse, split it. Never restate the Findings verbatim.
- **Lead with the strongest counter-evidence.** The single most damaging
  refutation appears **in the Executive Summary by the third line** and again
  as the opening `**Strongest counter-evidence:**` line of `## Contradictions
  & Counter-evidence`. Never bury it at the bottom of a long list.
- **Keep analytical claims on strong ground.** A conclusion about *what a
  number means* (a unit mismatch, a selection effect, a causal reading) is
  `interpretive`: it needs at least one primary or secondary origin, not only a
  blog or tertiary aggregator; with only weak origins, soften it to a labelled
  interpretation or mark the point `unknown`.
- **Label the unknown.** Unanswered items are written as `unknown`, never
  filled by plausibility.
- **Diagrams are optional and evidence-bound.** A diagram is a text-based
  Mermaid fence (```` ```mermaid ````) whose data points all come from cited
  claims; never invent a data point to make a chart look complete. Binary
  image rendering is out of scope — Mermaid only (*Micro-format rules*).

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
| Write unanswered items as `unknown` with a reader-facing reason | Paste `reason` enums, HTTP statuses or tool names into `report.md` |
| Let the script number the citations and emit `## Sources` | Hand-number citations or write a reference list by hand — the renderer owns `## Sources` |
| Honor a requested chapter count / outline / tone exactly — fold discipline material into a non-numbered appendix | Let `Executive Summary` / `Contradictions` / `Gaps` / genre sections push the body past the requested chapters, or expose `kqN` / `dN` codes |
| Run the readability pass on `report.src.md`, then re-gate and re-render | Hand-edit `report.cited.md` or `report.md` after rendering |

## Dual output: `report.cited.md` and `report.md`

One renderer run writes **both** files:

```bash
python scripts/render_citations.py --report .work/report.src.md --evidence evidence.json --output report.cited.md --clean-output report.md
```

(`protocol.md` §9 holds the canonical gate block; adapt its paths to the run.)

- **`report.cited.md`** — the cited copy: every marker substituted, full
  reference block at the end (footnote definitions in the default GFM mode).
  The **complete, checkable artefact**, and the file gate ② judges.
- **`report.md`** — the marker-free reading copy: markers stripped, the
  renderer-owned tail rebuilt as plain un-numbered `## Sources` /
  `## Observations` lists, and a **first line linking to `report.cited.md`**
  (the pointer follows the report's language).
- Both files come from the same run and numbering, so they can never disagree
  about which source backs which passage. **Never hand-edit one to agree with
  the other** — fix `report.src.md` and re-render: the writer ends it at
  `## Sources` with **nothing after it** and never writes `## Sources` or
  `## Observations` itself.
- **The delivery message names `report.md`** as the file to read and lists
  `report.cited.md` beside it as the citation-checkable artefact — both belong
  in the manifest (`protocol.md` §11).

## Pre-delivery readability pass (mandatory)

After writing, take one deliberate pass so the text reads — then re-gate. The
pass edits `report.src.md`, never the rendered outputs.

- **Allowed:** adjust heading levels; reorder paragraphs; adjust connective
  words; delete run-failure noise (fetch errors, retry chatter, internal
  apparatus); merge duplicated phrasing.
- **Forbidden** (anything touching the evidence): changing facts or numbers;
  changing conclusion strength; changing the citation mapping; changing source
  attribution.
- **Then:** re-run **all** evidence gates — gate ① and gate ② as defined in
  `protocol.md` §9, where gate ② re-renders **both** output files from the
  edited draft — and only then deliver.
- A structure the user explicitly requested is **binding and is not reordered**
  by the pass. Without a requested structure, reorder freely.

## Runtime jargon never appears in `report.md`

`report.md` is for readers, not for run logs. These run-failure tokens must
never appear in it: `access-limited`, `webfetch`, `captured 20`, `word_count`,
`extracted_main`, `bot-protection`, `抓取失败`, `读取失败`, `运行故障` —
`content_review.py --clean` **fails the run on any hit** (exit 1, code
`E_RUNTIME_TERM`).

- **Render `gaps[]` reasons as reader-facing language** — say what the reader
  needs to know, never the raw `reason` enum, an HTTP status or a tool name:

  | `reason` (evidence layer only) | Reader-facing wording in the report |
  |---|---|
  | `no-source` | "no source found yet" |
  | `access-limited` | "the source could not be opened" |
  | `stale` | "the data is stale" |
  | `budget` | "checking this was cut short by the run's limits" |
  | `other` | describe the actual obstacle in plain words |

- **Ambiguous network terms** (`403`, `401`, `429`, `503`, `timeout`,
  `blocked`, `forbidden`, `rate limit`, `captcha`, `bot-wall`, `paywall` …) are
  allowed **only when the subject genuinely needs them**; the review warns
  `W_RUNTIME_TERM` on each, and **every kept hit is recorded as an exemption in
  the run log** with the reason it is legitimate here.
- **`report.cited.md` may keep technical detail** — its review runs without
  `--clean`, where the blacklist is not enforced.

## Length tiers and the prose-first target

**First decide whether a long report is worth it** — for a narrow question the
right answer may be a short one — and record the decision and its reason in the
run output. When a long report is worth it, pick a tier:

| Tier | Words |
|---|---|
| short | 1500–3000 |
| medium | 3000–6000 |
| long | 6000–12000 |

An explicit user-specified length overrides the tiers. These are **report
length** tiers; the `quick` / `normal` run tiers are a separate decision
(`tier-selection.md`).

- **Write progressively:** one section at a time; never draft more than 2000
  words of a section in a single pass.
- **Prose-first:** ratio = non-table / non-code / non-pure-list characters ÷
  body characters of `report.md` (excluding `## Sources` / `## Observations`
  and footnote definitions). Target **≥ 0.80**. Below it `content_review.py`
  emits `W_PROSE_RATIO` — a warn-only signal that does not block delivery;
  when it fires, convert more tables and bullets into connected prose.
