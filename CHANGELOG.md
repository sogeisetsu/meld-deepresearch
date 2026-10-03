# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
