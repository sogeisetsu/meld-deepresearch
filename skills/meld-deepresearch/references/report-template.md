# Report Template

Structure and writing rules for the research report. The **report body is written in the end user's
language**; this template is English and stays English. Shape is part of correctness: a report with a
collapsed info block, a one-line TOC, generic headings or a standalone discipline chapter fails review even
when every claim is sourced.

## Structure follows the reader's cognitive task

The organising principle is **the cognitive task the reader must complete**, not the information domain:
material read for a decision and read for a mental map needs two organisations. **Domain conventions**
(academic / medical / legal / policy) override this *only* when the deliverable **is** that document type
and the reader strongly expects its format; medical or legal content inside a business request is chosen by
cognitive task first. **Composite intent:** the main intent picks the frame; the secondary intent collapses
into exactly one section ("understand the industry, then assess one company" → main intent *entity*,
panorama material into one "Industry background" section).

## Structure chooser

### Four base structures → genre templates

| The reader's task | Base structure | Genre template |
|---|---|---|
| Understand a space — build a complete mental map (industry, feasibility or trend survey) | Panorama (全景叙述) | `templates/genres/panorama.md` |
| Compare and choose — a documented decision among options (competitive analysis, tech selection, buying decision) | Comparison (对比选型) | `templates/genres/comparison.md` |
| Dig into one subject — understand it fully and form a judgment (due diligence, investment research, person / organisation background) | Entity (实体调查) | `templates/genres/entity.md` |
| Reconstruct an event — what happened, its impact and where it goes (breaking event, crisis, regulatory change) | Chronicle (时序追踪) | `templates/genres/chronicle.md` |

A genre is chosen at plan time (`plan.json` `genre`, one of `panorama | comparison | entity | chronicle |
general`) and only *appends* sections after the findings material (`general` appends nothing). **Genre
templates only APPEND** — they never remove, reorder or rename a required section.

### Domain-specific shapes — explicit request only

Allowed **only when the request explicitly asks for that document type** and the reader expects its format;
otherwise choose by cognitive task from the table above.

| Shape | Sections (in order) | Special rules |
|---|---|---|
| Academic literature review | Abstract → Introduction (background, review scope, structure) → Research lineages (literature by timeline or school) → Methodology comparison → Synthesis of core findings (consensus and disputes) → Research gaps & outlook → Conclusion → References (academic style) | Every key conclusion points to a specific work; disputes present each side's representative literature; never state a conclusion the literature does not explicitly support |
| Medical / health report | Structured abstract (background / objective / methods / results / conclusion) → Disease or intervention overview → Graded evidence review — Grade A: RCT or systematic review; Grade B: cohort study or authoritative guideline; Grade C: expert opinion or case report → Clinical application notes → Special-population cautions (elderly / children / pregnancy / comorbidities) → Limitations & uncertainties → References | Every recommendation carries its A/B/C evidence grade; drug content states indications and contraindications; uncertainty is labelled explicitly, never implied away |
| Legal memorandum (IRAC) | Issue (the legal question) → Rule (statutes, interpretations, precedent) → Analysis (the facts applied to the rule) → Conclusion (the legal opinion, with its certainty grade) → Appendix (optional: provisions, case summaries) | Name the jurisdiction; cite each provision's version and effective date; state uncertainty — never an opinion more certain than the evidence |
| Policy brief | Executive summary (policy core + recommendations) → Policy background (problem, status quo, history) → Policy content analysis (provisions, goals, mechanism) → Impact assessment (affected groups, economic / social impact, international comparison) → Stakeholder analysis → Recommendations → References | The executive summary must stand alone; recommendations are differentiated per audience (business / government / individuals) |

### What each genre appends after the findings material

| Genre | Appends after the findings material |
|---|---|
| `panorama` | Background & current state, Core dimension 1..N, Synthesis, Outlook, Appendix |
| `comparison` | Evaluation basis (needs / dimensions / weights), Option overview, **Comparison matrix — a table is required**, Per-dimension analysis, Recommendation, Risks & limits |
| `entity` | Subject profile, Operations, Financials, Legal / compliance, Team, Red flags, Conclusion & recommendation |
| `chronicle` | **Background & people** (consumes `background` claims), Timeline, Key-node analysis, Evidence & disputes, Conclusion & aftermath, Appendix |

## The evidence spine comes first

Structure decides *how material is organised*; it never negotiates *what must be verifiable*. Three layers,
highest precedence first:

| Layer | Rule |
|---|---|
| 1. **Binding user-requested structure** | A chapter count, outline or required section list wins over both layers below — see *Requested structure overrides the skeleton*. |
| 2. **Evidence layer** | The content slots below, in this order, never dropped while drafting; gates judge this content, not literal heading names. At delivery the *pre-delivery readability pass* weaves the discipline slots (5 and 6) fully into the narrative — never surviving as a standalone chapter at any heading level — with counter-evidence written into the prose of the claim it qualifies (never a labelled callout) and every `unknown` label staying attached to its claim. |
| 3. **Cognitive-task structure** | How the findings material is organised internally (by dimension, option, argument or time), and which genre sections append after it. |

| # | Slot | Satisfied by |
|---|---|---|
| 1 | Title | `# Title` / `# 标题` — specific and scope-revealing |
| 2 | Definitions & scope | `## 定义与范畴` / `## Background and scope` — the first section after the TOC |
| 3 | Summary | `## Executive Summary` / `## 摘要` |
| 4 | Findings material | descriptive content headings from the genre template — never a generic container heading |
| 5 | Counter-evidence material | woven into the prose of the sections whose claims it contradicts — an ordinary contrastive clause (不过 / however / but), never a labelled callout |
| 6 | Unknowns | `unknown` labels and uncertainty grades next to the claims they qualify |
| 7 | Sources | renderer-owned `## Sources` / `## 来源` |

**Slots are satisfied by content, not by literal names.** The draft-stage review checks that the slot's
*content exists* — it does **not** require a heading literally named "Findings", "Contradictions &
Counter-evidence" or "Gaps & Unknowns", and the delivered report must contain none of those headings anyway.
Translate titles; the slot order stays. Observations are **not** a reading-copy slot: they live in
`evidence.json` and the cited copy only.

**No apparatus in the body.** Apart from the line-1 pointer to the cited copy, the delivered report shows no
trace of its own production: no skill or protocol names, no draft/run-log file names, no middleware paths,
no English process narration inside a Chinese report. First-hand observations stay, but record each
`observations[].method` in the **report's language**, phrased for a reader ("核对了路透调查页原文"),
tool-agnostically; machine environment belongs to the cited copy only. `content_review.py --clean` fails on
high-precision leaks (`E_APPARATUS_LEAK`) and warns on a `.work/` path outside line 1 (`W_APPARATUS_LEAK`).

`content_review.py --clean` warns when an opening element is missing or malformed (`W_NO_INFO_BLOCK`,
`W_NO_TOC`, `W_THIN_TOC`, `W_NO_DEFINITIONS`), flags a generic top-level heading (`W_GENERIC_HEADING`), and
**fails** on a standing discipline chapter or stand-in (`E_STANDALONE_SECTION`, H2 or H3, either language,
the Observations heading included), a narrated run failure (`E_FAILURE_NARRATION`) or a labelled
counter-evidence callout (`E_ADVERSARY_CALLOUT`).

## The opening block: info rows, contents, scope

Between the title and the first section every report carries a **header info block** and a **table of
contents** (both surviving into the reading copy); the body then opens with definitions and scope.

### Header info block — one item per rendered line

A cover-sheet-style block of 3–5 items (the canonical block has five) sits between the title and the TOC:

```markdown
- 报告日期：2026-10-05
- 报告类型：行业现状与竞争格局分析
- 数据截止：2026-10-05
- 范围：中国乘用车前装 ADAS 市场，2023-01 至 2025-09
- 依据：17 个已直接打开的来源、2 条现场核验记录
```

- **It MUST be a bullet list (or explicit hard line breaks) — one item per rendered line.** Consecutive
  Markdown text lines collapse into one paragraph, so a run-in paragraph turns the block into one sentence
  the reader must parse. **Never a run-in paragraph, never a blockquote paragraph** — the reader must see
  five separate rows, like a cover sheet.
- Items: report date, report type, data cut-off, scope, basis — in the report's language. **The `依据` /
  basis line describes evidence, never machinery** ("N 个已直接打开的来源、M 条现场核验记录"): never a tool,
  skill or protocol; the shape rule outruns the `W_NO_INFO_BLOCK` probe (a run-in can pass it).

### Table of contents — a vertical list whose titles carry content

`## 目录` / `## Contents` sits directly under the info block:

- **A vertical list, one entry per line** — a bullet list of anchor links such as `-
  [定义与范畴](#定义与范畴)`, one line per section. **Never a single line joined by `·` or `;`**, never a
  comma-separated run-on: it collapses into one unreadable sentence.
- **Every top-level content section appears, in order** (definitions, summary, each content section, `##
  Sources`), with **descriptive, content-bearing titles** aiming at what the report will conclude
  (`市场规模与增长`, `竞争格局与份额`, `产业链与成本结构`, `结论与展望`), not at container names — a reader
  must tell from the TOC alone what the report argues. A TOC of 3–4 generic entries (`分析`, `结果`, `讨论`)
  is a defect.
- A missing TOC warns `W_NO_TOC`; a TOC collapsed onto a single line warns `W_THIN_TOC`.

### `## 定义与范畴` opens the body

After the TOC — before the summary and before any findings — the body opens with a definitions-and-scope
section: `## 定义与范畴` (Chinese report) or `## Background and scope` (English report), named in the
report's language. It states:

- **what the subject is** — one plain paragraph a non-specialist can parse;
- **which terms the report uses and how** — the working definitions (what "市场份额", "出货量", "营收" mean
  *in this report*);
- **the boundary of what is counted** — inclusion and exclusion rules;
- **the time window** — observation period and data cut-off.

This section **carries no new claims** — no findings, no conclusions, no numbers beyond the scope and window
facts already in the evidence; it frames what follows. A reader who does not know the field must be able to
read it and then understand everything after it. A missing section warns `W_NO_DEFINITIONS`.

## Headings must carry content

Every top-level content section is titled with **what that section concludes**, taken from the chosen genre
template — not with the container it belongs to.

**Forbidden as top-level titles** — they tell the reader nothing: `## 主要发现`, `## Findings`, `## 分析`,
`## Analysis`, `## 结果`, `## Results`, and by the same rule `## 讨论` / `## Discussion`. Use the genre
template's descriptive names instead: 市场规模与增长, 竞争格局与份额, 产业链与成本结构, 结论与展望, …

- **The evidence spine's slots are satisfied by descriptive headings that contain the required content**:
  the draft-stage review checks that the content exists, not that the heading is literally named "Findings".
- Fixed conventional names are exempt: `# Title`, `## 定义与范畴` / `## Background and scope`, `## 摘要` /
  `## Executive Summary`, `## 目录`, `## Sources` / `## 来源`.
- Generic container titles are flagged `W_GENERIC_HEADING`; treat every generic container as banned even
  when the probe list is narrower. H3 subsections follow the same rule: name what the subsection argues.

## No standalone discipline chapters — at any level

The discipline material (counter-evidence, gaps, unknowns) lives **inside the narrative**, never as its own
section — at H2 *or* H3, in either language. None of the following may exist in the delivered report:

| Level | Forbidden headings |
|---|---|
| H2 | `## 矛盾与反证`, `## 未知与缺口`, `## 观测记录`, `## Contradictions & Counter-evidence`, `## Gaps & Unknowns`, `## Observations` |
| H3 stand-ins | `### 反证与边界`, `### 尚未证实的部分`, `### 未知与缺口`, `### Counter-evidence and limits`, `### What remains unknown` — and any heading whose only topic is "here is what we could not do" |

`content_review.py --clean` fails on all of them (`E_STANDALONE_SECTION`), at **any** heading level.
Instead:

- **Counter-evidence is woven into the paragraph of the claim it qualifies.** Write it into that claim's own
  sentence or the one immediately after, joined by an ordinary contrastive transition (不过 / 然而 / 但 /
  受限于…; however / but / limited by / although…): it supports, corrects or bounds the conclusion and is
  never displayed as an add-on — no `**最强反证：**` / `**Strongest counter-evidence:**` bold lead-in, no
  standalone paragraph appended after the argument, no heading. The most important limitation still appears
  in the Executive Summary, as an ordinary bullet or clause with no label.
- **Each `unknown` and each uncertainty grade sits next to the claim it qualifies** — same paragraph or the
  one immediately after, never collected into a separate block.
- **Never let a reader hit a chapter whose only topic is "here is what we could not do."** Disagreements,
  gaps and caveats are paragraphs inside the relevant sections; an appendix note only if the request allows
  one. Draft in place — the pre-delivery pass dissolves any placeholder heading.

## Observations are never part of the reading copy

Observations live in `evidence.json` (`observations[]`) and in the cited copy `.work/report.cited.md`, which
keeps the `[^oN]` markers and the full observation list. The renderer **no longer appends** a `##
Observations` section to `report.md`, and a writer who adds one is failed (`E_STANDALONE_SECTION`). The
reader gets a `sources.md`-style reference list — the plain `## Sources` — **and nothing else**: what an
observation *found* is ordinary prose in the narrative; the inventory itself never reaches the reader.

## Requested structure overrides the skeleton

The skeleton above is the **default**. When the request names a chapter count, an outline, or a required
section list, that structure is **binding**: the numbered chapters follow it exactly (e.g. "5–6 个章节" ⇒
five or six chapters, not the default set).

| Rule | Detail |
|---|---|
| **Remap, never add chapters** | The summary and the genre sections become chapters as the request names them; the discipline material (counter-evidence, unknowns) lives *inside* those chapters or in one non-numbered `## 附录：方法与局限` (Appendix: method & limits) — never as extra numbered chapters, never as its own H2/H3. `## Sources` stays as a reference block; `## Observations` never appears in the reading copy. |
| **Never reduce the evidence rules** | A binding structure may reduce the chapter count, never the rules: every number still carries a citation, counter-evidence is still woven into the paragraph of the claim it qualifies (the most important limitation still stated in the summary), unknowns are still labelled next to their claims. |
| **Match register and length** | "正式、简洁 / formal and concise" ⇒ a concise formal report, not an academic monograph: cite only sources that carry a claim; a management deliverable gets a consolidated `结论与改进建议` chapter; a stated length target is respected (method and observation detail move into the non-numbered appendix, still in the evidence files); internal identifiers (`kqN`, `dN`, axis codes) never appear. |

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

| | |
|---|---|
| **Must** | open with the info-block rows, a vertical content-bearing TOC and `## 定义与范畴` · the summary stand alone (reading only it gives the core conclusion) · a comparison report contain the matrix table (side-by-side prose does not count) · every conclusion carry a certainty grade (*Uncertainty grading (D3)*) · under composite intent the secondary intent collapse into one section · under a domain shape, its conventions followed strictly |
| **Never** | use one generic structure for every request · title a top-level section with a container name (`## Findings`, `## 分析`) · let a discipline chapter or stand-in stand at any level · split the matrix into per-option paragraphs · let the conclusion list information without judgment · repeat the same fact in several sections · pad by restating the body in the summary or the summary in the conclusion |

## Section-by-section rules

| Section | What belongs here |
|---|---|
| `# Title` | Specific, scope-revealing (topic + angle), not a generic label |
| `## 定义与范畴` | Subject, working definitions, counting boundary, time window; no new claims; first section after the TOC |
| `## Executive Summary` | **A TL;DR, not a dense paragraph.** Use 3–5 short bullets (or at most 4 sentences); each line carries at most one figure and reads on its own. Order: ① the direct answer ② the single strongest piece of supporting evidence ③ **the most important limitation — as an ordinary bullet, no label, never buried** ④ the confidence level and the biggest caveat. Do not restate the findings verbatim or stack many figures into one line. A reader who reads only this block must get the answer and the main doubt |
| Content sections (descriptive titles) | One finding per subsection/bullet, each carrying inline citations; organised by the chosen structure, optionally grouped by axis `dN`; each section's counter-evidence is woven into the paragraph of the claim it qualifies — same sentence or the one immediately after, joined by an ordinary contrastive transition, never a labelled callout; each `unknown` / uncertainty grade sits next to its claim |
| `## Sources` | Owned by `render_citations.py`: numbered citation list for every cited source, regenerated wholesale. The writer ends `report.src.md` with this heading and nothing after it; the renderer materialises it in both output files (footnote block in the cited copy, plain list in the reading copy) |
| Observations | Never a section in the reading copy: the inventory lives in `evidence.json` and in `.work/report.cited.md` (full `[^oN]` list). The writer never writes an Observations heading, and the renderer never appends one to `report.md` |

## Inline citation mechanism

While drafting (`report.src.md`), cite with a footnote marker keyed to an id in `evidence.json`:

```markdown
Adoption accelerated after the v1.0 release.[^s1]
The host's installed CLI reports version 2.100.0.[^o1]
```

- `[^sN]` — a **source** (`sN` in `sources[]`); `[^oN]` — a **first-hand observation** (`oN` in
  `observations[]`: a command run, a measurement taken, a file inspected). Observations are ordinary
  evidence; both families are cited exactly alike (`--legacy-plain`: `[ON]`).
- `render_citations.py` converts markers into numbered citations and emits `citations.json`. **The default
  output is GFM footnotes** (`[^N]` / `[^oN]` plus definitions) so a GFM renderer shows a jumping
  superscript — no inline HTML for a sanitiser to strip. `--anchors` opts into `[[N]](#ref-N)` + `<a id>`,
  `--legacy-plain` into bare `[N]`. **The model never hand-numbers citations** or invents a bibliography.
- **`render_citations.py` owns `## Sources`, and it alone emits the observation list:** everything after `##
  Sources` is regenerated; in the default GFM mode both tail headings become `[^N]:` / `[^oN]: method —
  environment (captured YYYY-MM-DD)` definitions in the cited copy, while the reading copy gets the plain
  `## Sources` list only — no Observations section, ever (*Dual output*).
- Gate ② vocabulary (orphan / unresolved / uncited) is defined in `protocol.md` §9. **`sources.md` is not
  `## Sources`**: it is the standalone de-duplicated source table (`dedupe_sources.py` deliverable); the
  report's `## Sources` is the renderer's numbered citation list — same sources, different purpose.

## Uncertainty grading (D3)

Every disagreement carries one of three explicit grades — never a binary verdict:

- `已确认` / **confirmed** — independent origins agree, or one primary source settles it.
- `存在争议` / **in dispute** — credible sources disagree and the run cannot adjudicate.
- `无法证实` / **unconfirmed** — the point cannot be checked from reachable evidence.

The grade sits **next to the disputed point** — inside the section whose claim it qualifies, never in a
standalone chapter — and is re-checked in the quality self-check. It adds no schema field: a writing rule
over existing claims; a body with no uncertainty marker anywhere warns `W_NO_UNCERTAINTY`.

## Writing rules

| Rule | Requirement |
|---|---|
| **Statement strength never exceeds evidence strength** | "Proves" needs a primary source on a settled fact; one secondary source gets "suggests"; projections stay explicitly projected; contested points name who says what |
| **No new facts** | Everything asserted exists in `evidence.json` (schema and hard rules: `evidence-contract.md`); the report adds structure, not evidence |
| **Every number is traceable** | Each figure carries a `[^sN]` / `[^oN]` marker in every section — the Executive Summary included — and matches the recorded snippet (date-stamped when time-sensitive) |
| **First-hand observations are ordinary evidence** | Cited with `[^oN]` like a sourced claim; the counter-evidence and unknown rules apply unchanged; an observation never upgrades a claim's strength by itself |
| **Write plainly and short** | The summary is a TL;DR: 3–5 bullets, one figure per line, each line readable alone; never restate the findings verbatim |
| **Weave counter-evidence into its claim** | The most damaging refutation is written **into the paragraph of the claim it qualifies** — same sentence or the one immediately after, joined by an ordinary contrastive transition (不过 / 然而 / 但; however / but / limited by) — and the most important limitation appears in the Executive Summary as an ordinary, unlabelled bullet: never a `**最强反证：**` / `**Strongest counter-evidence:**` bold lead-in, never an appended callout paragraph, never a chapter of its own (`E_ADVERSARY_CALLOUT` fails the delivery gate) |
| **Keep analytical claims on strong ground** | A conclusion about *what a number means* (a unit mismatch, a selection effect, a causal reading) is `interpretive`: it needs at least one primary or secondary origin, not only a blog or tertiary aggregator; with only weak origins, soften it to a labelled interpretation or mark the point `unknown` |
| **Label the unknown, next to its claim** | Never filled by plausibility, never collected into a "what we could not do" block |
| **State epistemic status, never a run failure** | "复购率尚无公开披露", not "因登录墙无法打开…" — see *Never narrate a run failure* |
| **The scope section frames, it does not argue** | `## 定义与范畴` introduces no finding, no counter-evidence, no number not already in the evidence |
| **Diagrams are optional and evidence-bound** | A text-based Mermaid fence whose data points all come from cited claims; never invent a data point. Binary images are out of scope (*Micro-format rules*) |

## Quality self-check (four dimensions)

Ask each question before delivering; fix the report, not the answers.

| Dimension | What good looks like | Check question |
|---|---|---|
| Comprehensiveness | All axes, key questions and their counter-evidence covered | Did any `kqN`, axis, or contradiction go unmentioned? |
| Insight | Findings synthesize *why* and *so what*, not a link dump | Does each finding say something the sources individually did not? |
| Instruction-following | Requested structure, language, scope, tone and format; skeleton only when the request is silent — and the shape rules always | If a chapter count / outline / tone was requested, does the body match it exactly (no extra chapters, no internal codes)? Does the opening show separate info rows, a vertical content-bearing TOC and `## 定义与范畴`? Is every top-level heading descriptive? Does any discipline chapter or run-failure sentence survive? |
| Readability | Scannable headings, short paragraphs, plain wording, consistent terms | Would a reader get the answer from the summary alone, and the report's argument from the TOC alone? |

## Do / Don't

| Do | Don't |
|---|---|
| Write the info block as a bullet list — one item per rendered line, five rows like a cover sheet | Collapse it into a run-in paragraph or a blockquote paragraph |
| Make the TOC a vertical list of descriptive titles covering every content section | Join TOC entries on one line with `·` or `;`, or list 3–4 generic entries |
| Open the body with `## 定义与范畴` (subject, terms, boundary, time window; no new claims) | Start directly with findings, or let the scope section argue |
| Title every content section with what it concludes (`## 竞争格局与份额`) | Ship a container heading (`## 主要发现`, `## Findings`, `## 分析`, `## Results`) |
| Weave counter-evidence into the paragraph of the claim it qualifies (不过 / however); keep every `unknown` next to its claim | Lead a paragraph with `**最强反证：**` / `**Strongest counter-evidence:**`, leave `## 矛盾与反证`, `## 未知与缺口` or an H3 stand-in (`### 反证与边界`) standing at any level |
| State the epistemic status: "复购率尚无公开披露" / "该数据尚无可核验的公开来源" | Narrate a run failure: 登录墙, 需要登录, 未能打开, 打不开, 无法访问, an HTTP status as narrative |
| Attribute claims to their sources and hedge appropriately | Publish a claim backed only by a single `tertiary` source |
| Cite every factual statement and every number with `[^sN]` or `[^oN]`, including figures in the Executive Summary | Leave a marker orphaned (id absent from `sources[]` / `observations[]`) or unresolved (left un-replaced) |
| Cite a first-hand observation with `[^oN]` and record its method so it is reproducible — a command must be re-runnable | Rest on an observation nobody could repeat: an unrecorded command, or a method with no `method`/`command` detail |
| Report what the evidence shows | State recommendations or prescriptions as findings, or present only the confirming side |
| Write unanswered items as `unknown` with a reader-facing reason, beside the claim | Paste `reason` enums, HTTP statuses or tool names into `report.md` |
| Let the script number the citations and emit `## Sources` | Hand-number citations or write a reference list by hand — the renderer owns `## Sources` |
| Keep `## Observations` out of the reading copy entirely | Add an Observations section to `report.md` (failed: `E_STANDALONE_SECTION`) |
| Honor a requested chapter count / outline / tone exactly — fold discipline material into the requested chapters or a non-numbered appendix | Let the summary / discipline material / genre sections push the body past the requested chapters, or expose `kqN` / `dN` codes |
| Run the readability pass on `report.src.md`, then re-gate and re-render | Hand-edit `report.cited.md` or `report.md` after rendering |

## Dual output: the cited copy is middleware, `report.md` is the deliverable

One renderer run writes **both** files; the cited one goes into `.work/`, because the reader is pointed at
`report.md`:

```bash
python scripts/render_citations.py --report .work/report.src.md \
  --evidence evidence.json \
  --output .work/report.cited.md --clean-output report.md
```

(`protocol.md` §9 holds the canonical gate block; adapt its paths to the run.)

| File | Contents |
|---|---|
| **`report.md` — THE deliverable** | Marker-free reading copy containing exactly: title + header info block (bullet rows) + vertical TOC + the content sections (opening with `## 定义与范畴`, discipline material woven in — see the readability pass) + `## Sources`. **No `## Observations` section**, no markers, no apparatus; and a **first line linking to `.work/report.cited.md`** (relative, in the report's language). |
| **`.work/report.cited.md` — middleware** | Every marker substituted, the full `[^oN]` **observation list** and the full reference block at the end (footnote definitions in the default GFM mode): the complete, checkable artefact, and the file gate ② judges. Never handed to the reader as the primary file. |
| **One run, no hand-edits** | Both files come from the same run and numbering, so they can never disagree about which source backs which passage. **Never hand-edit one to agree with the other** — fix `report.src.md` and re-render: the writer ends it at `## Sources` with **nothing after it** and never writes `## Sources` or `## Observations`. |
| **Delivery message** | Names `report.md` as the file to read and lists `report.cited.md` beside it as the citation-checkable artefact — both belong in the manifest (`protocol.md` §11). |

## Pre-delivery readability pass (mandatory)

After writing, take one deliberate pass so the text reads — then re-gate. The pass edits `report.src.md`,
never the rendered outputs; the draft shape is *input* here, not a constraint.

| Check | Action |
|---|---|
| **Weave the discipline material in** (required, not optional) | No `## 矛盾与反证`, `## 未知与缺口` or their English forms may stand, **and dissolve the H3 stand-ins too** — `### 反证与边界`, `### 尚未证实的部分`, `### Counter-evidence and limits`, `### What remains unknown` and anything like them: their content moves into the sections whose claims it bears. Everything must survive the weave: counter-evidence stays in the prose of the claim it qualifies — **dissolve the label too** (`**最强反证：**` / `**Strongest counter-evidence:**` never leads a delivered paragraph; the limitation is joined by however / 不过 instead), and **every `unknown` label and uncertainty grade stays attached to its claim**. Leaving any heading standing is a hard failure (`E_STANDALONE_SECTION`); a surviving labelled callout is a hard failure (`E_ADVERSARY_CALLOUT`). |
| **Opening block** | The info block as separate bullet rows (never a run-in or blockquote paragraph), the TOC as a vertical list covering every content section with content-bearing titles, and `## 定义与范畴` as the first body section. |
| **Shape rules held** | Descriptive top-level headings only; no `## Observations` in the reading copy; no run-failure narration left in the text. |
| **Allowed / forbidden** | Allowed: adjust heading levels; reorder paragraphs; adjust connective words; delete run-failure noise (fetch errors, retry chatter, internal apparatus); merge duplicated phrasing. Forbidden (touches the evidence): changing facts or numbers, conclusion strength, the citation mapping, source attribution. |
| **Then re-run all gates** | Gate ① and gate ② (`protocol.md` §9 — gate ② re-renders **both** output files from the edited draft) plus `content_review.py --clean` on `report.md`; only then deliver. |
| **Requested structure** | A user-requested structure is **binding and is not reordered** by the pass; the weave still applies — it is about *how* the discipline material is presented. Without a requested structure, reorder freely. |

## Never narrate a run failure

The evidence layer records what went wrong — a login wall, a timeout, an unreachable PDF — in
`observations[]` and `gaps[]`. **The report never tells the reader that the run failed to open something.**
It states the epistemic status of the data instead:

- ✗ 「因登录墙无法打开路透报道」 · ✗ 「复购率因需要登录无法获取」
- ✓ 「复购率尚无公开披露」 · ✓ 「该数据尚无可核验的公开来源」

Never in `report.md` as narrative: `登录墙`, `需要登录`, `未能打开`, `打不开`, `无法访问`, `抓取失败`,
`读取失败`, "login wall", "could not open", "unable to access", "failed to fetch", fetch-timeout stories,
and HTTP status codes (`403` / `401` / `429` / `503`). The review **fails** the high-precision subset — also
`页面要求登录`, `因超时`, "could not (be) opened" — with `E_FAILURE_NARRATION`, and the runtime-jargon
blacklist with `E_RUNTIME_TERM`: the list above is the writing rule, the two codes are the floor.

Render `gaps[]` reasons as **epistemic status** — what cannot yet be known, never the obstacle the run hit:

| `reason` (evidence layer only) | Reader-facing wording in the report |
|---|---|
| `no-source` | "尚无公开来源" / "no public source found yet" |
| `access-limited` | "该数据尚无已核验的公开披露" / "no verified public disclosure of this figure" |
| `stale` | "最新可得数据止于 <date>" / "the latest available data is from <date>" |
| `budget` | write the point up as `unknown` — never "the run ran out of budget" |
| `other` | state the epistemic status in plain words (e.g. "口径不明，暂无法核对"), never the obstacle |

## Runtime jargon never appears in `report.md`

`report.md` is for readers, not for run logs. These run-failure tokens must never appear in it:
`access-limited`, `webfetch`, `captured 20`, `word_count`, `extracted_main`, `bot-protection`, `抓取失败`,
`读取失败`, `运行故障` — `content_review.py --clean` **fails the run on any hit** (exit 1, code
`E_RUNTIME_TERM`). Failure-narration phrases (`未能打开`, `登录墙`, `无法访问` …) are covered by
`E_FAILURE_NARRATION` in the previous section — both gates must stay green.

- **Ambiguous network terms** (`403`, `401`, `429`, `503`, `timeout`, `blocked`, `forbidden`, `rate limit`,
  `captcha`, `bot-wall`, `paywall` …) are allowed **only when the subject genuinely needs them** (a
  technical discussion of access barriers *is* the topic); the review warns `W_RUNTIME_TERM` on each, and
  **every kept hit is recorded as an exemption in the run log** with the reason it is legitimate here.
- **`report.cited.md` may keep technical detail** — its review runs without `--clean`, where the blacklist
  is not enforced.

## Length tiers and the prose-first target

**First decide whether a long report is worth it** — for a narrow question the right answer may be a short
one — and record the decision and its reason in the run output. When a long report is worth it, pick a tier:

| Tier | Words |
|---|---|
| short | 1500–3000 |
| medium | 3000–6000 |
| long | 6000–12000 |

An explicit user-specified length overrides the tiers. These are **report length** tiers; the `quick` /
`normal` run tiers are a separate decision (`tier-selection.md`).

- **Write progressively:** one section at a time; never draft more than 2000 words of a section in a single
  pass.
- **Prose-first:** ratio = non-table / non-code / non-pure-list characters ÷ body characters of `report.md`
  (excluding `## Sources` and footnote definitions). Target **≥ 0.80**. Below it `content_review.py` emits
  `W_PROSE_RATIO` — a warn-only signal that does not block delivery; when it fires, convert more tables and
  bullets into connected prose.
