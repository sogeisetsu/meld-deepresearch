# Skill evaluations — meld-deepresearch

Three evaluator skills were run against `skills/meld-deepresearch/` at `main`
(74fac71). Raw outputs are kept in the gitignored
`meld-deepresearch-reports/eval/` directory (`skill-vetter.md`,
`darwin-baseline.md`, `skill-creator.md`); this file is the committed synthesis.

## What each evaluator did

| Evaluator | Mode | Outcome |
|---|---|---|
| `skill-vetter` | full static security review of all 14 skill files | 🟢 LOW risk, ✅ safe; no red flags |
| `darwin-skill` | Phase 0.5 + Phase 1 evaluation only (no optimization loop) | baseline 82.0 / 100; dim8 was `dry_run` |
| `opencode-skill-creator` | `skill_validate` + `skill_parse`; trigger eval blocked | valid skill, 15 725 body chars; `skill_eval` refused (installed copy conflict) |

## Findings and disposition

| Finding | Source | Severity | Action | Status |
|---|---|---|---|---|
| `templates/genres/` was not listed among SKILL.md's resource pointers, so the model could miss the genre templates | darwin dim6; skill-creator | Low (docs) | add it to the SKILL.md resource list | **fixed** |
| Skill "stop" points were described in prose, not marked | darwin dim4 | Low (docs) | add explicit `STOP:` markers at the blocking-capability probe and the gate-failure path | **fixed** |
| dim8 (measured performance) was not actually run | darwin | Info | needs live test-prompt runs; out of scope for this design-level pass | deferred |
| `skill_eval` trigger accuracy could not run | skill-creator | Info | tool refuses while an installed copy of the skill shares the name; requires moving the user's `~/.config` copy aside | deferred (needs explicit confirmation) |
| Scripts import stdlib only, no network/exec/secret access | skill-vetter | — | none | done |

## Darwin baseline (triage only)

Total **82.0 / 100**. Strongest: dim5 actionable specificity (18), dim2 workflow
clarity and dim7 architecture (12 each). Weakest: dim4 checkpoints (weighted gap
2.4, now improved) and dim8 measured performance (unmeasured). The absolute
score is triage-only; darwin's own rubric warns an LLM-judge absolute score
carries roughly ±8 noise, so it is not a keep/revert signal.

## Notes

- The two fixed findings were applied on `fix/eval-findings` and merged.
- No evaluator suggested anything that violates the project's non-negotiables
  (no new dependency, no host-specific tool name, no second skill).
