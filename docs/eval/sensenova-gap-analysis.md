# SenseNova vs `meld-deepresearch` — Independent Gap Analysis

**Scope.** SenseNova-Skills pinned at SHA `5abde96fed2148aaf6a0ed55f0f4708f2b0845f5` (verified `git rev-parse HEAD`), tree at `.worktrees/sensenova-skills/`. Our skill at `.worktrees/sensenova/skills/meld-deepresearch/` (branch `feat/sensenova-benchmark`, HEAD `0940247`). Shorthand used below:

- `SN` = `.worktrees/sensenova-skills`
- `MD` = `.worktrees/sensenova/skills/meld-deepresearch`

**Builds on (not redone).** The 7-axis rubric (A–G), the 6 test questions, and the three-skill design-level comparison already exist in `MD/../docs/eval/README.md`, `MD/../docs/eval/records/design-score.md`, `MD/../docs/eval/records/live-runs.md`. This document adds the SenseNova-specific capability diff and the Q1 design-level per-axis breakdown; it does not re-score Weizhena or re-derive the rubric.

**Uncertainty policy.** Anything not directly readable in the clone is labelled `unknown`. Where the prior art already flagged a limit, that limit is preserved rather than upgraded.

---

## 1. Capability table

`SenseNova` column cites clone-relative paths. `Root cause` cites our `file:line`. "Gap" is stated relative to *our* design, not as an absolute defect.

| Capability | SenseNova | meld | Gap | In-scope? | Root cause (our file:line) | Action |
|---|---|---|---|---|---|---|
| **Academic / paper search adaptation** | Dedicated skill `sn-search-academic` with `search.py` / `paper.py` / `refTree.py` entries (`SN/skills/sn-search-academic/SKILL.md:12-27`); sources arxiv/semantic google_scholar/pubmed/ssrn/wikipedia (`…:77-85`); section-level paper reading (`…:97-123`); backward/forward **citation-graph traversal** (`…:310-343`); ArXiv category table (`…:345-378`). | Generic web search + fetch only; no repository adapter, no reference-graph traversal, no venue/citation-count ranking. PDF reading is an optional capability with no routing (`MD/SKILL.md:59`). | No way to systematically walk citation chains or query arXiv/PubMed/SSRN syntax; a literature review relies on whatever generic search surfaces. | **PARTLY IN-SCOPE** | `MD/SKILL.md:104-105` (plan/research stages are "search → candidate pool → open originals"); `MD/references/protocol.md:18-37` (§2 loop has no source-class adapters or graph traversal); `MD/references/protocol.md:32-35` (pool sorted by quality/relevance/recency only). | Add protocol.md guidance: for academic axes, prefer academic repositories via generic search, adapt queries (venue/year/field terms), traverse references by fetching the cited URLs, and read sections/PDFs rather than abstracts. **Do not** add API-key scripts (runtime-deps rule). Citation-graph *breadth* stays a recorded trade-off. |
| **Developer / code search adaptation** | Dedicated `sn-search-code` over GitHub, Stack Overflow, Hacker News, HuggingFace (`SN/skills/sn-search-code/SKILL.md:3,12,14-21`); GitHub `code` search requires a token (`…:48-50`). | Code reading is optional (`MD/SKILL.md:60`), but no developer-source routing. | Same class as academic: no platform-internal search, no vote/citation sorting. | **PARTLY IN-SCOPE** | `MD/references/protocol.md:18-37` (no source adapters); `MD/SKILL.md:60` (capability listed, never routed). | Doc-level routing guidance to GitHub/SO/HN/HF via generic search; platform-internal `code:` search (needs token) recorded as trade-off. |
| **Source-class taxonomy & routing** | `plan.json` requires `sources[].category` from a 23-value enum (`official, news, social_media, github, developer, community, trend, academic, forum, analyst, review, data, legal, financial, finance, securities, annual_report, filing, market_cn, policy, regulation, multi_platform`) (`SN/skills/sn-deep-research/schemas/plan.schema.md:43-56`), and `research.md` maps each category to a **mandatory** specialist skill (`SN/skills/sn-deep-research/agents/research.md:52-74`). | No `source_type` / category field; `plan.json` carries `source_classes` as free text (`MD/references/evidence-contract.md:293`). | Absent. | **ALREADY COVERED (parallel lane)** | — | **No action.** The parallel lane is adding `source_type`; do not re-add it. |
| **Domain-specific genre layering** | `sn-research-report` selects a structure by reader cognitive task and domain: 4 base structures (panorama / comparison / entity / chronicle) plus academic / medical / legal / policy domain templates (`SN/skills/sn-research-report/SKILL.md:12-36`, `45-142`, `146-213`). | One fixed skeleton for every report (`MD/references/report-template.md:7-27`). | No genre selection; every report gets the same section order. | **ALREADY COVERED (parallel lane)** | `MD/references/report-template.md:7-27` (single skeleton) — but see action. | **No action.** The parallel lane is adding `templates/genres/{panorama,comparison,entity,chronicle}.md`; do not re-propose. |
| **Chart / Mermaid diagram rendering** | Outline unit types include `bar-chart`, `distribution-chart`, `quadrant-chart`, `timeline`, `flowchart` (`SN/skills/sn-deep-research/scripts/validate_outline.py:62-63`); writer renders `mermaid` fences with evidence-bound constraints (`SN/skills/sn-deep-research/agents/report-writer.md:190-211`); `sn-research-report` mandates Mermaid for pies/graphs/timelines/xy-charts (`SN/skills/sn-research-report/SKILL.md:229-233`). | No figure slot, no diagram guidance, no chart script. Deliverables are Markdown + JSON only (`MD/SKILL.md:161-177`). | Reports cannot carry a chart or diagram. | **PARTLY IN-SCOPE** | `MD/references/report-template.md:7-27` (skeleton has no figure slot); `MD/scripts/` contains only `check_evidence.py`, `render_citations.py`, `dedupe_sources.py` (no chart code). | In-scope, zero-dep: add optional guidance that diagrams use text-based Mermaid fences, must be evidence-bound, and must not invent data points. Binary chart/image rendering stays a recorded trade-off. |
| **AI concept image generation** | `SN/skills/sn-deep-research/SKILL.md:37` (`SN_IMAGE_GEN_API_KEY` → AI concept figures, else "no-image version"); `sn-image-imitate` full generation pipeline (`SN/skills/sn-image-imitate/SKILL.md:27,134-231`); worked example ships 5 `.jpg` figures (`SN/examples/embodied-ai-deep-research/README_CN.md:30,42-46`). | None. | No image generation at all. | **DELIBERATE TRADE-OFF** | `MD/SKILL.md:5` (compatibility lists only web/PDF/code/subagent); `MD/AGENTS.md` rule 2/8 (zero runtime deps, one skill). | Record, don't build. Requires external API + keys, which the design forbids. |
| **HTML report skill** | `sn-md-to-html-report` produces a self-contained HTML article from Markdown, with a mandatory `plan.md` design pass (`SN/skills/sn-md-to-html-report/SKILL.md:3,31-38,40-49,69-75`); chained by the user in the example (`SN/examples/embodied-ai-deep-research/README_CN.md:13-18,32-34`). | Markdown only. | No HTML deliverable. | **DELIBERATE TRADE-OFF** | `MD/SKILL.md:161-177` (deliverables), `MD/SKILL.md:5`. Prior art already recommends *against* adding it (`MD/../docs/eval/README.md:228-233`). | Keep recorded. A companion skill, never a dependency. |
| **PPT / PPTX skill** | `sn-ppt-entry` routes to `sn-ppt-standard` / `sn-ppt-dazzle` / `sn-ppt-creative`, can invoke `sn-deep-research` for deep mode, and exports PPTX via a bundled Node exporter (`SN/skills/sn-ppt-entry/SKILL.md:19-20,48-55,239-278,278`). | None. | No deck output. | **DELIBERATE TRADE-OFF** | Same as above; Node/JS runtime + qn of sibling skills. | Keep recorded. |
| **Report-format discovery (`format`)** | Request-level `format` string chosen by rule, no schema/file (`SN/skills/sn-report-format-discovery/SKILL.md:16-31`); values `report/paper/table/memo/timeline/faq` (`…:20`). | `format` anchor exists, default `report` (`MD/SKILL.md:71-73`), but no discovery rule and only one structural template. | Minor: `format` is anchored but not acted on structurally. | **ALREADY COVERED (parallel lane)** | `MD/SKILL.md:71-73`; `MD/references/report-template.md:7-27`. | Covered by the genre lane; no separate action. |
| **Multi-role orchestration** | Controller dispatches `scout` / `plan` / `research` / `review` / `perspective` / `supplement-planner` / `report-planner` / `report-writer` / `report-stitcher` with per-role contracts in `SN/skills/sn-deep-research/agents/*.md`; three pipelines quick/normal/heavy (`SN/skills/sn-deep-research/SKILL.md:190-217`, `248-534`). | Single inline agent; axes MAY be delegated but never required; two tiers only. | Lower wall-clock throughput and (heavy-mode-only) coverage breadth at very large scope. | **DELIBERATE TRADE-OFF** | `MD/references/protocol.md:263-267` (§13 delegation optional, inline default); `MD/SKILL.md:194-200`; `MD/references/tier-selection.md:6-11` (two tiers). | Keep recorded (rules 1, 5, 11). Never require subagents. |
| **Citation preparation / render gate** | `sn-prepare-citations` dedupes `[^key]`, assigns `[N]`, resolves `[^dN.cM]` claim-id leakage, inserts L0/TOC, appends references, emits `citations.json`; gate on orphan/unresolved (`SN/skills/sn-prepare-citations/SKILL.md:8,31-47`). | `render_citations.py` assigns `[N]`/`[ON]`, owns `## Sources`/`## Observations`, fails on orphan/unresolved (`MD/scripts/render_citations.py:1-47,304-312`); `check_evidence.py` is a second fail-closed gate. | At parity or leading on the gate; no TOC/L0 (presentation, not evidence). | **DELIBERATE TRADE-OFF** (residual only) | `MD/scripts/render_citations.py:314-360` (emits citations, no TOC/L0); `MD/references/report-template.md:7-27`. | No evidence-integrity action. TOC/L0 is presentation and belongs to the recorded F trade-off. |
| **Progress WebUI & resumability** | Mandatory Research Workbench + `progress_event.py` at run start (`SN/skills/sn-deep-research/SKILL.md:103-151`); resumability via `task_pack.json` in PPT (`SN/skills/sn-ppt-entry/SKILL.md:280-289`). | No UI; resumability is "retry a stage once, else report honestly" (`MD/SKILL.md:179-183`). | No live progress surface. | **DELIBERATE TRADE-OFF** | `MD/SKILL.md:179-183`; no host-UI dependency in design. | Keep recorded. Installing a WebUI runtime violates zero-dep/portability. |

**Note on the parallel lane.** The overlap items — `templates/genres/{panorama,comparison,entity,chronicle}.md`, `source_type`, `gaps[]`, `background` kind, `must_have_materials` — are **not present** in this worktree's tree as read (a glob of `MD` returned only `SKILL.md`, `scripts/*`, `references/*`). They are treated as **already covered by the parallel lane and deliberately excluded from every Action above.**

---

## 2. Q1 design-level 7-axis diff (SenseNova vs meld)

**Q1** = "A landscape survey of one industry (e.g. humanoid robotics / embodied AI): market size, players, funding, cost structure, roadmap." Correct tier = `normal` (`MD/../docs/eval/README.md:97`).

> **Q1 was NOT live-run.** The prior-art records state Q1 (and Q3–Q6) were not executed for any skill: "Q1 / Q3–Q6 | not run | not run | not run" (`MD/../docs/eval/records/live-runs.md:17`), under the live-run caveat at `MD/../docs/eval/README.md:15-18`. Everything below is **design-level only** — scored by reading each skill's own files. No Q1 artifact exists for either skill, so no axis below claims observed behaviour.

Scores are on the prior-art 0–5 rubric. `Δ` = SenseNova − meld (design-level).

| Axis | SenseNova | meld | Δ | Justification |
|---|---|---|---|---|
| **A Coverage & completeness** | 4 | 4 | 0 | SenseNova plans non-overlapping work packages from a category enum and can escalate to `heavy` for a broad landscape (`SN/skills/sn-deep-research/SKILL.md:184-217`; `…/schemas/plan.schema.md:38-56`). meld names non-overlapping axes and its `--plan` gate fails an uncovered axis (`MD/references/protocol.md:155-189`; `MD/references/evidence-contract.md:302-307`), but the `normal` cap (25 fetches / 15 sources) can end a wide landscape early by design (`MD/references/protocol.md:121-136`). Even. |
| **B Depth & analysis** | 4 | 4 | 0 | SenseNova's review / perspective / supplement passes add analytical depth, **but only in `heavy`** — its `normal` pipeline explicitly omits them (`SN/skills/sn-deep-research/SKILL.md:207`). Q1's correct tier is `normal`, so on this question the depth edge is **not** exercised; meld's per-axis depth threshold + `key_findings` derived layer (`MD/references/protocol.md:93-101`, `MD/references/evidence-contract.md:160-168`) is comparable. Even at the required tier. |
| **C Factual accuracy & claim support** | 4 | 5 | −1 | meld's contract is machine-enforced: `factual` needs primary/secondary or an observation, `tertiary` alone fails, snippets are never evidence (`MD/references/evidence-contract.md:170-180`, `254-267`; `MD/scripts/check_evidence.py:529-540`). SenseNova enforces the same rule in `validate_evidence.py` (`SN/skills/sn-deep-research/agents/research.md:161,247`; error code `V040`) and forbids snippets in evidence (`…:16,328`), but its schema is a per-role check rather than a standalone contract, and meld's observation-as-first-hand-evidence path has no SenseNova equivalent. Per prior art (`MD/../docs/eval/records/design-score.md:14,26`). |
| **D Citation quality** | 4 | 5 | −1 | Both gate on orphans: meld `render_citations.py` fails orphan/unresolved (`MD/scripts/render_citations.py:304-312`); SenseNova `prepare_citations` fails orphan + unresolved claim-id leakage (`SN/skills/sn-prepare-citations/SKILL.md:43-47`). meld additionally normalizes/dedupes URLs (`MD/scripts/dedupe_sources.py:1-46`) and forces two distinct origins for `interpretive` claims (`MD/scripts/check_evidence.py:551-581`). SenseNova dedupes by URL inside the citation step (`SN/skills/sn-prepare-citations/SKILL.md:34`), so the gap is narrow. Per prior art. |
| **E Instruction-following** | 4 | 4 | 0 | Both anchor language and a request-level `format` (`SN/skills/sn-deep-research/SKILL.md:20-25`; `MD/SKILL.md:71-73`). SenseNova adds an explicit start-of-run confirmation and three modes (`SN/…/SKILL.md:153-188`), which is more guided but blocks on a user reply; meld records assumptions when it cannot ask (`MD/SKILL.md:83-85`). Even. |
| **F Presentation & readability** | 5 | 3 | +2 | SenseNova: `sn-md-to-html-report` (`SN/skills/sn-md-to-html-report/SKILL.md:3`), chart unit types + Mermaid (`SN/skills/sn-deep-research/scripts/validate_outline.py:62-63`, `agents/report-writer.md:190-211`), and the worked example's 5 figures + HTML (`SN/examples/embodied-ai-deep-research/README_CN.md:30,36-46`). meld: Markdown only (`MD/SKILL.md:161-177`). **Deliberate trade-off** (rules 2 and 8), already documented (`MD/../docs/eval/records/design-score.md:17`). |
| **G Process discipline** | 4 | 5 | −1 | meld: forced refutation `W_NO_REFUTE` (`MD/scripts/check_evidence.py:839-843`), enumerated budgets/stop rules (`MD/references/protocol.md:121-136`), reproducible `observations[]` with a re-runnable command (`MD/references/evidence-contract.md:75-96`), two fail-closed gates, stated degradation (`MD/SKILL.md:63-65`). SenseNova: per-role validators + retry caps (`SN/skills/sn-deep-research/SKILL.md:219-242`) and a refute mandate (`SN/skills/sn-deep-research/agents/research.md:174,330`), but **no enumerated fetch budget** and its own rules force a stop when a Tier-1 capability is missing (`SN/skills/sn-deep-research/SKILL.md:27-40`) — which the live Q2 run showed it does (`MD/../docs/eval/records/live-runs.md:33-56`). |
| **Total (35)** | **29** | **30** | **−1** | Matches the prior-art design-level totals (`MD/../docs/eval/records/design-score.md`), with Q1 specifics: SenseNova's depth edge is `heavy`-only and therefore inactive at Q1's `normal` tier; its presentation edge is real; meld's edge is the two enforced gates. |

**Reading the Q1 diff.** On the required `normal` tier, SenseNova and meld are close on A/B/E, meld leads on C/D/G by enforcement, and SenseNova leads on F by deliverable format. SenseNova's headline structural advantages (review/perspective/supplement, HTML) either sit in a tier Q1 does not use (`normal`) or a cross-skill chain our design forbids.

---

## 3. Root causes traced to our files

Each gap's mechanism, in our own artifacts:

- **No academic/code adaptation.** The per-axis loop is deliberately generic: "Search → candidate URL pool → Fetch → read the ORIGINAL page" (`MD/references/protocol.md:20-25`), and the pool sorts only by "source quality (`primary` > `secondary` > `tertiary`), then relevance, then recency" (`MD/references/protocol.md:32-35`). Nothing in the plan or research stage mentions repository selection or query-language adaptation (`MD/SKILL.md:104-105`). PDF/code reading are listed as capabilities but never routed to a source class (`MD/SKILL.md:59-60`).
- **Genre layering absent.** One skeleton is mandated for every report, "exact order" (`MD/references/report-template.md:7-27`); the only format signal is the `format` anchor defaulting to `report` (`MD/SKILL.md:71-73`). *Covered by the parallel lane; no fix proposed here.*
- **Chart/figure rendering absent.** The skeleton has no figure/diagram slot (`MD/references/report-template.md:7-27`); deliverables are `report.md`/`sources.md`/`evidence.json`/`citations.json` (`MD/SKILL.md:161-177`); `MD/scripts/` has no rendering code.
- **HTML/PPT/image absent by construction.** The skill declares only web/PDF/code/subagent capabilities (`MD/SKILL.md:5`) and the design forbids cross-skill deps and runtime deps (`MD/AGENTS.md` rules 2, 8).
- **Single-agent, two-tier.** Delegation is optional and inline is the default (`MD/references/protocol.md:263-267`; `MD/SKILL.md:194-200`); the tier table has exactly two rows (`MD/references/tier-selection.md:6-11`), with no `heavy` pipeline (`MD/references/tier-selection.md:73-84` only covers a mid-run `quick`→`normal` upgrade).
- **Citation prep residual.** The renderer emits `citations.json` with sources/observations but no TOC/L0 (`MD/scripts/render_citations.py:314-360`); the fixed skeleton has no anchored summary layer (`MD/references/report-template.md:7-27`). This is a presentation gap, not an evidence-integrity one.

---

## 4. Classification

**IN-SCOPE** (satisfies: one skill, zero runtime deps, no cross-skill deps, no host-specific tool names, two tiers):

1. **Source-adaptation guidance** (academic + developer). Documentation-only additions to `references/protocol.md` §2: when an axis is academic/developer, prefer the relevant repositories via the existing generic search, adapt query syntax, traverse cited references by fetching their URLs, and read sections/PDFs rather than abstracts. No new scripts, no keys. *Distinct from the `source_type` field the parallel lane is adding — this is behaviour guidance, not schema.*
2. **Text-diagram guidance** (Mermaid). Zero-dep: allow optional Mermaid code fences in the report skeleton, required to be evidence-bound and forbidden from inventing data points. No binary rendering.
3. **(Optional, low priority) `format` → structure hook**, so the existing `format` anchor can select among the genre templates the parallel lane adds. Only if the genre lane does not already wire it.

**DELIBERATE TRADE-OFFS to record** (do not build):

- HTML report, PPT/PPTX, AI image generation — all require a cross-skill chain and/or external runtimes/keys; the prior art already recommends against closing the F gap with a dependency (`MD/../docs/eval/README.md:228-233`).
- Multi-role orchestration and the `heavy` tier — rule 1 (discipline over orchestration) and rule 5 (two tiers). Cost: wall-clock throughput and heavy-only coverage breadth; recorded as a known loss, not a defect.
- Enumerated fetch budgets stay in our favor; do not import SenseNova's missing-budget behavior.
- Progress WebUI / resumability — a runtime dependency; out of scope.
- TOC/L0 summary layer — presentation, belongs to the recorded F trade-off.
- API-backed breadth for academic/code (citation counts, platform-internal `code:` search) — needs tokens/keys a portable skill must not persist.

**ALREADY COVERED — no action** (parallel lane): `templates/genres/{panorama,comparison,entity,chronicle}.md`, `source_type`, `gaps[]`, `background` kind, `must_have_materials`.

---

## 5. Overlap note

The parallel lane's additions are acknowledged as **already-covered** and are explicitly **not re-proposed** anywhere in this document:

- **Genre layering** (capability row 4) — the four genre templates are the parallel lane's job; our single-skeleton root cause (`MD/references/report-template.md:7-27`) is noted only to explain the gap, not to request work.
- **Source-class taxonomy** (row 3) — `source_type` is the parallel lane's job; the in-scope item above is *adaptation behaviour*, which the field alone does not provide.
- **`gaps[]` / `background` kind / `must_have_materials`** — not analysed as gaps here; treated as covered.

None of these files/fields exist in this worktree's tree as read (glob of `MD` returned only `SKILL.md`, `scripts/*`, `references/*`); the acknowledgement is that a sibling lane owns them, not that they are present.

---

## Uncertain items

- **SenseNova's chart production mechanism is `unknown` at script level.** The example reports 5 `.jpg` figures (`SN/examples/embodied-ai-deep-research/README_CN.md:30,42-46`) and `SKILL.md:37` ties concept figures to `SN_IMAGE_GEN_API_KEY`, but the exact script path that emits them is not in the files read. The Mermaid/chart-unit mechanism is confirmed at `SN/skills/sn-deep-research/scripts/validate_outline.py:62-63` and `agents/report-writer.md:190-211`.
- **SenseNova `heavy`-mode refutation/coverage quality** is inferred from `SKILL.md` excerpts; the prior art already marked these `unknown` (`MD/../docs/eval/records/design-score.md:30`). Not upgraded here.
- **Whether generic search can adequately substitute** for `sn-search-academic`/`sn-search-code` on Q1 is untested — Q1 was not run for either skill (`MD/../docs/eval/records/live-runs.md:17`). Under-claimed deliberately.
- **Q1 design scores for both skills carry the prior-art caveat**: design-level only, no live artifact (`MD/../docs/eval/README.md:15-18`).
