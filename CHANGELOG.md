# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

### Notes

- The skill is at version `0.1.0`; publication (M4) is still pending. See
  `docs/PLAN.md` milestones M1-M4.
