# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-10-07

### Added

- **`meld.py`, a thin CLI over the six gate scripts**
  (`skills/meld-deepresearch/scripts/meld.py`): `prepare` merges
  `OUT/.work/sub_reports/*.evidence.json` into `OUT/evidence.json` (skipped
  when that directory is missing or empty) and then runs gate ①, adding
  `--plan OUT/.work/plan.json` automatically when the plan exists
  (`--tier quick|normal` only overrides that auto behaviour; `--tier normal`
  without a `plan.json` is a usage error, exit 2); `render` writes both report
  files plus `citations.json`; `review [--clean]` picks the structural pass or
  the delivery gate file automatically; `sources` writes `sources.md`;
  `verify` runs prepare → render → review → review --clean in order, stops at
  the first failure, prints `{"ok": false, "stage": ..., "exit": ...}` and
  exits with the underlying code; `table` passes through to `read_table.py`.
  JSON on stdout and exit 0/1/2 exactly as the wrapped scripts, which all stay
  independently runnable. New fixture `examples/cli-run/` carries the real
  `.work/` layout (`.work/plan.json`, `.work/report.src.md`,
  `.work/sub_reports/axis.evidence.json`) so `meld.py verify` runs end to end.
- **`content_review.py --fix`** — before the review, the two **closed** safe
  operations are applied to the `--report` target *and* its counterpart copy
  (the pair derives from the same outdir root: `OUT/report.md` ↔
  `OUT/.work/report.cited.md`; either may be given as `--report`, and a
  missing counterpart is simply not edited): stripping the exact bold
  callout-label tokens (`ADVERSARY_LABEL_TOKENS`, both colon widths — the
  precise tokens `E_ADVERSARY_CALLOUT` matches — keeping the sentence that
  follows inline) and demoting one level the heading lines seeded in the
  closed `GENERIC_HEADING_FIX` map (what `W_GENERIC_HEADING` itself treats
  as generic). Nothing else is ever rewritten: unsafe shapes, notably a
  standing discipline chapter (`E_STANDALONE_SECTION`), are never
  auto-merged, restructured or deleted. With `--fix` the JSON gains one
  `fixes` record per applied edit (`{"file","op","line","detail"}`), and
  both report copies are kept in sync; without the flag the stdout JSON and
  exit codes are unchanged byte-for-byte. Unit test:
  `skills/meld-deepresearch/tests/test_content_review_fix.py`.
- **Per-code failure hints.** Every warning/failure entry whose `code` is a
  key of the closed `HINTS` map carries an additive `"hint"` string naming
  the smallest safe fix — attached only when that code fires, so a run in
  which no mapped code fires contains no hint anywhere; every existing
  field, exit code and greppable substring is unchanged.

### Changed

- **Documentation converges on `references/protocol.md` §9 as the single
  command authority, with the CLI commands primary:** §9 now leads with the
  `meld.py` block and keeps every raw script command in a labelled
  "equivalent raw commands" block (the raw `render_citations.py` line gained
  `--citations "$OUTDIR/citations.json"` so both forms produce the same four
  deliverables). `SKILL.md` §4/§8, `README.md`, `ZH/README-ZH.md`,
  `ZH/SKILL-ZH.md`, `report-template.md` and `evidence-contract.md` restate
  the same stages via the CLI subcommands. No gate code, threshold, retry
  rule or tier rule changed.
- **CI runs a `meld.py` self-test in the core job** (documented in
  `AGENTS.md`): the happy path for `prepare` / `render` / `review` / `sources`
  / `verify` over the staged `examples/cli-run/` fixture, plus one deliberate
  failure per subcommand asserting the exit code — and, for `verify`, the
  failing stage name in its JSON body. Every pre-existing validation command
  stays in the battery.
- **The draft-shape / weave-as-a-separate-pass prose is gone, and with it the
  "re-run everything from gate ① after the readability pass" rule.** After
  prose edits only the delivery gate re-runs: `meld.py review --clean` —
  that is what `report-template.md`'s readability-pass section,
  `protocol.md` §9 stop rules, `SKILL.md` §4 row 8 and both READMEs'
  re-gate bullet now say.
- **The anti-pattern → fix table migrated out of `report-template.md` and
  into the gate itself:** every code `content_review.py` reports now carries
  its fix as a `hint` (see *Added*); the rows with no checker code remain in
  `report-template.md` as pure writing rules.
- **13 duplicate rules were converted to pointers — one authority per
  rule:** budgets and stop rules → `protocol.md` §8, gate commands and code
  meaning → §9, stop/retry → §9–§10, artifacts and directory layout → §11,
  evidence rules → `evidence-contract.md`, length tiers →
  `report-template.md`. `SKILL.md` shrinks 119 → 107 lines, `README.md`
  240 → 232, `templates/genres/*` 87 → 83 combined. Prose line counts for
  `references/` (before → after phase 2): `protocol.md` 502 → 504,
  `report-template.md` 422 → 417, `evidence-contract.md` 431 → 431,
  `tier-selection.md` 90 → 90 — total 1,445 → 1,442, with the delivery-gate
  severity wording (downgrade entry below) as the only material addition.
- **`E_STANDALONE_SECTION` and `E_ADVERSARY_CALLOUT` were downgraded from
  delivery-gate hard fail to warnings:** detection is unchanged — both are
  still reported with their `hint` and still must be fixed before delivery —
  but they land in `warnings[]` with exit 0. The three hard codes remain
  `E_RUNTIME_TERM`, `E_FAILURE_NARRATION` and `E_APPARATUS_LEAK`.
  Rollback clause honored: the full validation battery stayed green, so no
  rollback was needed.
- READMEs restructured to the Standard Readme spec — standard-readme badge,
  one-line short description matching `package.json`, a table of contents,
  Usage/Contributing/License section order (License last); language switchers
  preserved.

## [0.3.1] - 2026-10-06

### Changed

- Skill placement descriptions now carry the high-intent terms users actually
  type: `meld-deepresearch` lists **deep research**, **market research** and
  **source verification**, and `meld-search-academic` lists **find papers**,
  **systematic review** and **citation chain**. No capability changed; only the
  matching surface did.

## [0.3.0] - 2026-10-06

### Added

- **The delivery gate rejects a standalone discipline chapter**
  (`E_STANDALONE_SECTION`, exit 1): `content_review.py --clean` now fails when
  `## Contradictions & Counter-evidence` / `## Gaps & Unknowns` (or their
  Chinese forms `## 矛盾与反证` / `## 未知与缺口`) is still standing as its own
  top-level section — the pre-delivery readability pass weaves those chapters
  into the narrative, after which every gate runs again before the single
  render. The draft must also carry a **header info block** (subject / scope /
  data cut-off / compiled / basis as `label: value` lines) and a **table of
  contents** under the title; their absence stays warn-only (`W_NO_INFO_BLOCK`,
  `W_NO_TOC`, alongside `W_NO_UNCERTAINTY`, `W_PROSE_RATIO` and the
  ambiguous-term `W_RUNTIME_TERM`). New fixture
  `examples/invalid/report.standalone-section.src.md` (exit 1);
  `examples/sample-run/report.md` is the zero-warning positive.
- **The delivery gate rejects a labelled counter-evidence callout**
  (`E_ADVERSARY_CALLOUT`, exit 1): counter-evidence is now **woven into the
  paragraph of the claim it qualifies** — same sentence or the one immediately
  after, joined by an ordinary contrastive transition (不过 / however / but /
  limited by) — instead of appearing as a `**最强反证：**` /
  `**Strongest counter-evidence:**` block. The old "on its own line / by the
  third line of the summary" mandate is gone; the Executive Summary still
  states the most important limitation, as an ordinary bullet or clause.
  Searching for counter-evidence during research is unchanged (`protocol.md`
  §3). New fixture `examples/invalid/report.adversary-callout.src.md` (exit 1).
- **The README pair gained an `## Install` section** with the verified
  one-liners `npx skills add sogeisetsu/meld-deepresearch --all` and
  `gh skill install sogeisetsu/meld-deepresearch --all`; a bare
  `gh skill install owner/repo <name>` installs only that one skill, so `--all`
  is required for the repo's three. The run walkthrough was compressed and its
  micro-rules moved behind pointers into `references/`.
- **Both capability skills document their hand-off contract** in a new
  `## Hand-off entry & exit` section: each works standalone and may be handed
  off to from the core skill (`protocol.md` §2a), and returns reproducible
  numbers/quotes plus the re-runnable command for the caller's
  `observations[]`/`sources[]` instead of writing the caller's evidence files.
  Their frontmatter version is aligned to `0.3.0`, and `meld-da`'s Windows note
  no longer repeats the academic skill's crawler/Node.js bullet (meld-da has no
  crawler).
- **Scale redesign (0.3.0) — the repository now ships three cooperating
  skills** instead of one:
  - `skills/meld-da` — the Excel / spreadsheet analysis workflow, adapted from
    SenseNova-Skills `sn-da-excel-workflow` @ `5abde96f` (MIT) and translated to
    English, with sandbox paths removed, `requirements.txt`, and a stdlib
    degrade-path unit test that proves the `read_table.py` fallback.
  - `skills/meld-search-academic` — academic search, paper reading and
    citation-tree tracing, adapted from SenseNova-Skills `sn-search-academic`
    @ the same commit; `playwright`/`camoufox` are an **optional** tier
    (`requirements-optional.txt`) that degrades to the official APIs and then to
    generic search instead of aborting, with its own unit test.
  - Documented cross-skill hand-offs live in `references/protocol.md` §2a:
    spreadsheet analysis routes to `meld-da`, and **academic, scientific or
    historical subjects must route the scholarly layer through
    `meld-search-academic`**. Neither skill may require the other.
- **Dual-file output.** One `render_citations.py` run now writes
  `report.cited.md` (markers + full reference block, what gate ② judges) **and**
  `report.md` — a marker-free reading copy whose first line links to the cited
  copy, in the report's language.
- **Runtime-failure jargon gate.** `content_review.py --clean` fails the run
  (`E_RUNTIME_TERM`, exit 1) when the reading copy contains any of nine
  high-precision run-failure tokens (`access-limited`, `webfetch`,
  `captured 20`, `word_count`, `extracted_main`, `bot-protection`, …);
  ambiguous network terms only warn and must be recorded as exemptions. It also
  reports the prose-first ratio (`W_PROSE_RATIO`, warn-only).
- **Soft budget with a bounded extension.** Fetch caps raised (`quick` ≤ 12,
  `normal` ≤ 40; rounds per axis 4 / 5) and exhaustion no longer stops a run
  that still has open key questions: it extends **automatically, at most 2
  rounds**, logging new sources / still unresolved questions / cost per round —
  after which the open questions become `uncertainty` (`gaps[]` + `unknown`)
  and never a fabricated conclusion.
- **Evidence-rule refinements** (`check_evidence.py` + `evidence-contract.md`):
  a `factual` claim may now rest on `tertiary` support **only** with an explicit
  `downgrade` writing-context annotation (`E_FACTUAL_SOURCE` without it,
  `W_DOWNGRADE` with it); an `interpretive` claim needs two distinct origins
  **with at least one `primary`/`secondary`** (`E_INTERPRETIVE_CREDIBLE`); a
  `key_finding` needs the same basis (`E_FINDING_BASIS`). A `tertiary` source may
  be the second origin — never the only pillar.
- **Length tiers and the mandatory readability pass.** The writer records
  whether a long report is worth it and why, then picks short 1500–3000 /
  medium 3000–6000 / long 6000–12000 words (an explicit user length wins),
  writes ≤2000 words per section per pass, and runs a pre-delivery readability
  pass whose allowed/forbidden operations are spelled out in
  `references/report-template.md` — after which every gate runs again.
- **Layered CI.** A zero-dependency `core` job (spec check over every
  `skills/*/SKILL.md`, the full script self-test, both degrade-path unit tests)
  that must be green, plus an `optional` job that performs the full dependency
  install, re-runs the tests with packages present, AST-parses every script, and
  records a skip reason instead of failing when the network is unavailable.
- **Delivery-shape gates (after round-5/6 blind evals failed axis E).**
  `content_review.py --clean` now also fails on:
  - `E_STANDALONE_SECTION` — any standalone discipline chapter at H2 **or H3**,
    English or Chinese, including `反证与边界`, `尚未证实的部分` and
    `观测记录`: the counter-evidence callout and every `unknown` label are
    woven into the section they belong to instead;
  - `E_FAILURE_NARRATION` — telling the reader that a page needed a login or
    could not be opened (`登录墙`, `页面要求登录`, `未能打开`, …). Failures are
    recorded in `observations[]`/`gaps[]`; the report states the epistemic
    status only;
  - `E_APPARATUS_LEAK` — the skill id, draft/run-log file names, a protocol
    name or a tool name inside the body.
  Warn-only signals added: `W_THIN_TOC` (TOC is one run-in line),
  `W_NO_DEFINITIONS` (no definitions-and-scope section), `W_GENERIC_HEADING`
  (a container heading such as `## 主要发现`), `W_APPARATUS_LEAK` (a `.work/`
  path outside line 1).
- **Report opening spec.** A header info block as **one item per rendered
  line** (Markdown collapses consecutive lines into one paragraph), a
  **vertical table of contents** carrying every top-level section under a
  descriptive title, and a **definitions-and-scope section before the first
  finding**. Generic container headings are replaced by content-bearing ones.
- **`report.md` no longer carries an `## Observations` section** — the reader
  gets the reference list only; observations stay in `evidence.json` and
  `.work/report.cited.md`.
- New fixtures: `examples/downgrade-run/` (positive, `W_DOWNGRADE`),
  `examples/invalid/evidence.interpretive-tertiary-pair.json`,
  `examples/invalid/evidence.finding-single-source.json`,
  `examples/invalid/report.runtime-jargon.src.md` (`E_RUNTIME_TERM`),
  `examples/invalid/report.standalone-section.src.md` (`E_STANDALONE_SECTION`),
  `examples/invalid/report.failure-narration.src.md` (`E_FAILURE_NARRATION`).
- **`docs/eval/records/sensenova-live/baseline-f05bcbc.json`** — the frozen
  per-axis baseline (A5 / B3 / C1 / D0 / E5 / G1 = 15 of 30) exported from the
  committed round-3 record, so acceptance no longer depends on re-blinding.
- **Genre templates** (`skills/meld-deepresearch/templates/genres/`): a report
  can append a genre-specific structure — panorama, comparison (with a required
  comparison matrix), entity / due-diligence, or chronicle (history) — chosen at
  plan time via `plan.json` `genre`. Required sections never change; a genre
  only adds.
- **Structured gaps.** `evidence.json` gains an optional `gaps[]` array
  (`id` / `text` / `reason` / `cost`) so a reader can tell "no source exists"
  from "access was limited" from "the budget ran out". New codes `E_GAP_SHAPE`
  / `E_GAP_ENUM` / `E_GAP_REF`.
- **`background` claims.** A new claim kind carries context (period, people,
  prior events) with any-tier evidence, is exempt from `E_FACTUAL_SOURCE`, and
  may not back a `key_finding` (`E_FINDING_BACKGROUND`).
- **Source-type labels.** `sources[].source_type`
  (`official | academic | archive | press | oral | community | mixed`) labels
  the kind of source; it never changes the credibility threshold.
- **`merge_evidence.py`** — folds per-axis `sub_reports/*.evidence.json` into
  one `evidence.json`, de-duplicating sources by URL and re-pointing references.
- **`content_review.py`** — an optional, warn-only content self-check (required
  sections, heading language, uncited numbers, gaps versus report).
- **Source-class routing guidance** for academic and developer axes, and
  optional **text (Mermaid) diagrams** required to be evidence-bound.
- **`plan.json` `must_have_materials[]`** — an axis-level checklist whose
  missing items must be written to `gaps[]`.
- **Citations that jump on a sanitising renderer.** `render_citations.py` now
  emits **GFM footnotes by default**, so GitHub and other GFM renderers wire the
  numbered superscript and its back-link themselves instead of depending on
  `<a id>` anchors, which many renderers strip. `--anchors` restores the old
  `[[N]](#ref-N)` form and `--legacy-plain` the bare `[N]` text.
- **`read_table.py`** — a stdlib-only reader for **local** `.xlsx` / `.csv`
  files (with a built-in `--selftest`), so a run handed data files turns them
  into reproducible first-hand `observations[]` instead of guessing or needing a
  third-party spreadsheet library. Sheet mapping, shared/inline strings, sparse
  cells and Excel serial dates are handled. See `references/protocol.md` §2a.

### Changed

- **Delivery layout: the cited copy moved to `.work/`, four deliverables
  again.** A real run writes `report.cited.md` to `.work/report.cited.md` —
  middleware that gate ② judges and the reader never receives — so the top
  level keeps exactly four deliverables: `report.md`, `sources.md`,
  `evidence.json`, `citations.json`. The reading copy's first line links to
  the cited copy by a **relative path** (`report.cited.md` when both sit in
  the same directory, `.work/report.cited.md` in a real run), and
  `render_citations.py --citations citations.json` keeps the citation map at
  the top level instead of next to `--output`. `examples/sample-run/` keeps
  `report.cited.md` at the top level only as a CI fixture.
- **`SKILL.md` slimmed to 120 lines** (from 188): every rule that does not need
  to be in the entry point moved into `references/`, which is loaded on demand.
- **`references/report-template.md` restructured around the reader's cognitive
  task** — panorama / comparison / entity / chronicle, plus academic, medical,
  legal and policy shapes — excerpted and translated from SenseNova-Skills
  `sn-research-report` (attribution in `NOTICE`); the evidence spine stays
  mandatory and in fixed order, and a user-requested structure still binds.
- **`AGENTS.md` non-negotiables rewritten:** multiple skills are allowed,
  documented cross-skill hand-offs are allowed, third-party Python dependencies
  are allowed for capability skills (core scripts stay stdlib-only). Retained:
  no host-specific tool names, English published text, `main` always mergeable,
  JSON stdout with 0/1/2 exit codes.
- **`README.md` rewritten in English** in the concise style of
  `199-biotechnologies/claude-deep-research-skill` — structure imitated, no
  sentence copied. (That project declares **MIT** in its README but ships no
  standalone `LICENSE` file; the README statement is the licence of record.)
- **Fixtures re-tuned:** negative fixtures that test a non-finding rule now
  carry `key_findings: []` so each still fails for exactly its own reason, and
  the merge fixture's key finding gained a second independent origin.
- `report-template.md` now requires the **Executive Summary to be a 3–5 bullet
  TL;DR** (answer first, one figure per line, the key limitation as an ordinary
  clause), and the counter-evidence is **woven into the paragraph of the claim
  it qualifies** — the labelled callout block is gone (see the
  `E_ADVERSARY_CALLOUT` entry above). It also tells the writer to keep an
  analysis of *what a number means* on a primary/secondary origin, not only on a
  blog or tertiary aggregator.
- `content_review.py` gained `W_REVIEW_NO_STRONGEST_COUNTER`,
  `W_REVIEW_SUMMARY_LONG` and `W_REVIEW_SUMMARY_DENSE`, and now accepts GFM
  footnote definitions in place of a standalone `## Sources` heading.

- `.work/` now holds the run middleware (`plan.json`, `report.src.md`,
  `sub_reports/`), leaving the four top-level artifacts as the deliverables.
- `dedupe_sources.py` adds a `source_type` column only when a source uses it.
- `content_review.py`'s `W_REVIEW_SUMMARY_DENSE` now counts English sentences
  too (it previously split only on CJK punctuation, so it never fired on an
  English paragraph); `W_REVIEW_SUMMARY_LONG` remains a conservative, line-based
  screen for wrapped English prose.
- CI's script self-test now covers `merge_evidence.py` (including a
  writing-context collision regression), `content_review.py`, the
  chronicle-genre example, every negative fixture, and the new
  `examples/merge-run/` fold fixture.
- The npm package (`package.json` `files`) now ships only `docs/PLAN.md` instead
  of the whole `docs/` tree, dropping the landing page, `og.png` and the
  `docs/eval/` records from the tarball while keeping the README's relative link
  resolvable.
- `.gitignore` was hardened (build/temp/Node artifacts, `**/.work/`) and is now
  stored as UTF-8 without a BOM.
- CI's script self-test now pins all three render modes — default footnotes
  (`[^1]:` / `[^o1]:` definitions), `--anchors` (`[[1]](#ref-1)` plus
  `<a id="cite-1"></a>`) and `--legacy-plain` (`[1]` / `[O1]`) — and asserts
  the new blank-marker fixture fails, so a silent flip of the default mode
  cannot regress again unnoticed.
- The npm package (`package.json` `files`) additionally ships `AGENTS.md` and
  `ZH/README-ZH.md` (the README's relative links to them now resolve inside
  the tarball) and never packs compiled caches, via the negation patterns
  `"!**/__pycache__"` and `"!**/*.pyc"`.
- `docs/FILE_TREE.md` was re-synced with the hardened `.gitignore` (build/
  temp/Node artifacts, local `.worktrees/`) and the `SKILL.md` frontmatter
  field list (now including `compatibility`).
- `examples/sample-run/report.src.md`'s Executive Summary was reordered so the
  strongest counter-evidence (single snapshot vs archived time series) lands by
  the third sentence, with the plugin-support contradiction after it;
  `report.md` and `citations.json` were re-rendered from it (citation numbering
  and `sources.md` are unchanged).
- Footnote wiring is attributed to the **GFM renderer**, not the agent host,
  in `SKILL.md`, `references/report-template.md` and the renderer docstring.
- The archived skill-creator benchmark records use a portable
  `skill_path: skills/meld-deepresearch` instead of a machine-local absolute path.

### Fixed

- **The `meld-search-academic` degrade test no longer requires a
  dependency-free interpreter.** Its core-entry-point case asserted that
  `search.py` / `paper.py` / `refTree.py` import with no third-party packages at
  all, which failed in the zero-dependency CI job: those entry points
  legitimately depend on the declared core packages (`httpx`, `arxiv`, ...).
  The test now asserts the documented contract instead — with the core
  requirements present the modules import, and without them they exit with a
  clean "install `requirements.txt`" hint rather than a traceback.
- `check_evidence.py` no longer crashes with a Python traceback when a
  top-level array has the wrong shape (for example a non-array `claims`); it now
  reports a clean `E_SHAPE` JSON body, as the contract promises.
- `merge_evidence.py` re-keys a colliding `writing_context` id inside its own
  `dN.wM` family instead of to a bare `cN`, so the merged `evidence.json` still
  passes gate ① instead of failing with `E_ID_PATTERN`.
- **Gate ② now rejects blank citation markers in the default GFM-footnote
  mode.** `[^]` / `[^ ]` markers carried no id, so they were neither numbered
  nor substituted and, with the default flipped from anchors to footnotes, they
  escaped the residual-`[^` scan too — a draft containing them rendered with
  `ok: true` (exit 0) even though `--anchors` / `--legacy-plain` failed it. The
  renderer now scans the rendered output for markers whose id is empty after
  stripping and fails them alongside orphans. New fixture
  `examples/invalid/report.empty-marker.src.md` (exit 1); the gate ②
  vocabulary in `references/protocol.md` §9 documents the rule.
- **`NOTICE` corrected:** `199-biotechnologies/claude-deep-research-skill` is
  recorded as **MIT** (declared by its own README) instead of unlicensed. It
  ships no standalone `LICENSE` file, so the README statement is the licence of
  record; the borrowing scope is unchanged (style and structure only, no code
  and no prose).

### Removed

- **Three obsolete, unreferenced evaluation files were removed:**
  `docs/eval/records/darwin-optimization.md`,
  `docs/eval/records/skill-evaluations.md` and
  `docs/eval/sensenova-gap-analysis.md`. `docs/eval/README.md` now carries a
  **Records index** so every remaining record stays reachable, and the
  sensenova-live record gained an archive banner (the `test/` scratch area was
  deleted after the redesign; its inputs live in `.work/backup-baseline/`).
  Two deferred items from `skill-evaluations.md` are preserved here:
  (1) `skill_eval` trigger accuracy could not run — the tool refuses while an
  installed copy of the skill shares the name, and moving the user's config copy
  aside needs explicit confirmation; (2) darwin dim8 (measured performance) was
  a `dry_run`, out of scope for the design-level pass.
- **`test/` is retired (directory deleted).** It was a local, always-gitignored
  scratch area: the frozen SenseNova baseline, every live-run artifact, the
  blind-judge copies and a set of ad-hoc tooling. Deleting it now is safe
  because the scores, protocols and verdicts live in
  `docs/eval/records/sensenova-live/`, the checks live in CI, and the frozen
  per-axis baseline is exported as `docs/eval/records/sensenova-live/baseline-f05bcbc.json`.
  **Before** the deletion `test/baseline/` was copied to the gitignored
  `.work/backup-baseline/` (frozen reports + the ten T2 input `.xlsx` are not
  in git history and would otherwise be lost).
- **`test/tools/` — per-item verdicts (rescue first, then delete):**

  | file | verdict |
  |---|---|
  | `docx_to_md.py` | **rescued** → `read_table.py --docx` (`--format json` blocks, `--format md`, `--format jsonl`), with a Word fixture built in memory by `--selftest`. Generalised: namespace-agnostic parsing, heading-style detection, GFM tables. |
  | `xlsx_probe.py` | redundant — `read_table.py` already maps sheets through the workbook relationships, handles shared/inline strings and sparse cells; its raw `xl/` zip listing is covered by `--all-sheets --format json`. |
  | `t2_recompute.py` | obsolete — task-specific aggregates built on a duplicate stdlib xlsx reader; the aggregates belong to the run, not the tool. |
  | `verify_t2.py` | obsolete — task-specific cross-check of those same numbers. |
  | `spec_check.py` | superseded — CI's Spec check now covers every `skills/*/SKILL.md`, enforces name↔directory match and ASCII-only descriptions. |
  | `ci_selftest.py` | superseded — the workflow's own `run: \|` blocks are now replayed directly from `.github/workflows/validate.yml` instead of being re-implemented. |
  | `fetch_baseline.py` | obsolete — baseline downloads are retired with `test/`. |
  | `extract_baseline.py` | obsolete — same. |
  | `write_run_meta.py` | **reusable but not migrated**: writes `run-meta.json` (git SHA + every skill file hash) as the eval protocol §4 requires, which is version pinning, not reading-layer logic. Deleted with `test/`; recover it from this deletion commit if another round needs it. |
  | `check_links.py` | **reusable but not migrated**: stdlib sampler that prints the HTTP status of N links from a text file — verification tooling, not a table concern. Same disposition as above. |

  Everything in the table remains recoverable from the commit that precedes
  the deletion.

## [0.2.0] - 2026-10-04

### Added

- **Access-blocked sources are now a documented rule, not improvisation.**
  `references/protocol.md` gains a dedicated section on paywalled, bot-walled
  and region-blocked pages: the run records the failed fetch as an observation
  (with the HTTP status), notes the gap as an `availability` caveat, and never
  passes a search cache, snippet or syndicated repost off as the original. If
  the only support for a claim is unreachable primary material, the claim is
  labelled `unknown` rather than downgraded into a confident assertion.
- **The validator now tells you the smallest safe fix.** Every actionable
  validation error (`check_evidence.py`) carries an optional `hint` field naming
  the one repair most likely to clear it — for example, whether to re-key a
  claim, add a second distinct origin, or drop an unreachable reference. The
  `code`/`message`/`where` contract is unchanged, so existing consumers keep
  working.
- **A same-publisher warning.** When an `interpretive` claim's distinct source
  URLs all sit on one publisher root (a wire story re-published across the same
  outlet), the validator reports `W_SAME_PUBLISHER` — a warning only, because
  the check is a heuristic and never fails a run.
- **Mid-run budget uplift for wide topics.** The fetch budget and
  distinct-source floor can be raised explicitly during a run when a genuinely
  broad topic would otherwise be capped early. The tier never changes (there is
  still no third tier), and the ≤3-rounds-per-axis limit and stop rules are
  untouched.
- A **Deep Research evaluation standard and three-skill comparison**
  (`docs/eval/`): the recognized report-quality benchmarks (RACE/FACT,
  ResearchRubrics, DEER, DRACO and more), a seven-axis rubric, a shared test
  question, and a live comparison against SenseNova-Skills and
  Weizhena/Deep-Research-skills — including what none of the public benchmarks
  measure (process discipline, forced refutation, honest stopping).

### Changed

- The landing page (`docs/index.html`) was reworked from user feedback: the
  English footer's README link now points at the English README (each language
  links to its own), clicking the wordmark returns to the top of the page, the
  card fade-and-slide reveal now applies only to the "How it works" chapter (the
  top progress line keeps its animation), the hero copy reads more naturally in
  both languages, and both language versions now share the same chapter
  background alternation.
- Chinese `README-ZH.md` lost the stray spaces the translation had left around
  the em dashes.

## [0.1.0] - 2026-09-30

### Added

- Project initialized (M0): repository skeleton, `README.md`, `LICENSE` (MIT),
  `NOTICE`, `.gitignore`, `package.json`.
- `AGENTS.md` (project conventions) and `docs/PLAN.md` (authoritative
  development plan, with design philosophy and borrow map).
- The skill (M1): `skills/meld-deepresearch/SKILL.md` plus `references/protocol.md`,
  `references/evidence-contract.md`, `references/tier-selection.md` and
  `references/report-template.md`.
- Validation scripts (M2), Python 3 standard library only:
  `check_evidence.py`, `render_citations.py`, `dedupe_sources.py`.
- `examples/sample-run/` (a complete illustrative run) and `examples/invalid/`
  (negative fixtures for the validator).
- CI workflow `.github/workflows/validate.yml`.
- Verification on a real host (M3): the skill was installed into opencode, hot-
  discovered there and exercised end to end in both tiers (`quick` and
  `normal`), plus a packaging-level install into a second host
  (`gh skill install`, claude-code).
- First-hand evidence (M3): a first-class `observations[]` type for commands
  run, measurements, files inspected and direct inspection, with validator and
  renderer support (`[^oN]` markers and an `## Observations` section); the
  heuristic normative check was relaxed from `E_NORMATIVE` to the non-fatal
  `W_NORMATIVE` after it misfired on a descriptive paraphrase.
- Chinese documentation (`ZH/`): `README-ZH.md`, plus a language switch in both
  READMEs. The Chinese `CHANGELOG` and `SKILL.md` translations are deliberately
  local-only and ignored by git.
- GitHub Pages landing page: `docs/index.html` (one self-contained file, no
  external requests) and `docs/.nojekyll`.
- The landing page is bilingual (English and Chinese) and ships both a light and
  a dark theme, each with its own control in the header. English is the default
  on every first visit — the language is never inferred from the browser — and
  the page stays fully readable with JavaScript disabled.
- Landing-page redesign: a hero wordmark for the skill name, the twelve stages
  redrawn as a three-act timeline with the two hard gates as full-width gate
  bars, a section for why the skill exists next to heavy frameworks and thin
  prompts, a credits section ("Standing on the shoulders of many" / 集百家之长)
  that separates projects whose text or mechanisms were reused from those that
  only inspired the approach, and a theme-following install section.
- Landing-page motion: reveals and the pipeline rail are driven by scroll
  position, with the reader's progress and current section shown in the header.
  The reveal state is computed in script for every browser, so no content can be
  left invisible; everything still settles fully visible under
  `prefers-reduced-motion`.
- Landing-page chapters align to the fold: a chapter whose content fits occupies
  exactly one screen below the header, chapter boundaries are carried by
  alternating surfaces instead of rules, and `scroll-snap-type: y proximity`
  settles a chapter into place when the reader comes to rest.
- Social preview: `og:`/`twitter:` metadata with a canonical URL, and
  `docs/og.png`, a 1200x630 card rendered from the live hero.

### Notes

- The skill is at version `0.1.0` and is published. See `docs/PLAN.md`
  milestones M1-M4.

[Unreleased]: https://github.com/sogeisetsu/meld-deepresearch/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/sogeisetsu/meld-deepresearch/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/sogeisetsu/meld-deepresearch/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/sogeisetsu/meld-deepresearch/releases/tag/v0.3.0
[0.2.0]: https://github.com/sogeisetsu/meld-deepresearch/releases/tag/v0.2.0
[0.1.0]: https://github.com/sogeisetsu/meld-deepresearch/releases/tag/v0.1.0
