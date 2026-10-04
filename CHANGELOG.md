# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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

### Changed

- `report-template.md` now requires the **Executive Summary to be a 3–5 bullet
  TL;DR** (answer first, one figure per line, strongest counter-evidence by the
  third line) and a `**Strongest counter-evidence:**` line opening
  `## Contradictions & Counter-evidence`, so the single most damaging refutation
  is never buried. It also tells the writer to keep an analysis of *what a number
  means* on a primary/secondary origin, not only on a blog or tertiary aggregator.
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

[Unreleased]: https://github.com/sogeisetsu/meld-deepresearch/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/sogeisetsu/meld-deepresearch/releases/tag/v0.1.0
