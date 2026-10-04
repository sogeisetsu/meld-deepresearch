# Darwin optimization pass — meld-deepresearch

A `darwin-skill` hill-climbing pass over `skills/meld-deepresearch/`, run on a
throwaway branch (`auto-optimize/20261004-0906`). Raw scratch (test prompts,
A/B run outputs, `results.tsv`, result card HTML) is gitignored under
`meld-deepresearch-reports/darwin/`; this file is the committed synthesis.

## Method

- **Baseline (triage only).** 9-dimension rubric read-scored; total ≈ **86.9 /
  100**. Absolute LLM-judge scores carry ~±8 noise, so they rank work, they do
  not decide keep/revert.
- **dim8 (measured) was actually run** — the highest-weight dimension was not
  dry-run:
  - prompt 1 (quick, "Python 3.13 version/date"): with_skill vs baseline output
    were equivalent — correct, the skill itself says a one-line fact needs no
    full loop.
  - prompt 2 (normal, Postgres-vs-MySQL write-heavy selection): the
    with_skill run produced the four artifacts + `plan.json`, passed Gate ①
    (`--plan`) and Gate ②, with 15 sources, 19 claims, 3 `refute` claims, 4
    gaps; a baseline answer was prose-only with no machine-checkable evidence.
    The run also self-reported **3 guessed documentation URLs that 404'd**,
    spending budget for nothing.
- **Keep/revert was a paired decision**, not an absolute-score delta: 3
  independent judges each read the before (`git show HEAD:…`) and after
  (working tree) versions in one context. Verdict **3–0 better, clear**.

## Changes (all on `auto-optimize/20261004-0906`)

| File | Change | Rubric |
|---|---|---|
| `references/protocol.md` | new §10 symptom → first-fix → fallback table (blocking capability, empty axis, walled source, unparsable page, guessed-URL 404, Gate ①/② failure, id collision, budget exhaustion, stage fails twice) | dim3 |
| `references/protocol.md` | §2 rule 1 now forbids **constructing/guessing a URL** and notes a guessed 404 still costs budget | dim3/dim5 |
| `references/protocol.md` | §7: a page that opened but parses to nothing is `access-limited`, not `other` | dim3 |
| `references/evidence-contract.md` | documents the `plan.json` `assumptions` field (used by `SKILL.md` §4 but previously undocumented — real doc drift) | dim6 |
| `SKILL.md` | §4/§5/§7/§10/§11/§13 tightened; §11 points to the protocol table instead of duplicating it; body **207 → 198 lines** (AGENTS.md ~200 cap) | dim5/dim7 |
| `docs/FILE_TREE.md` | protocol.md comment now mentions the failure/retry table | — |

No script, schema rule, or frontmatter behaviour was changed; no dependency was
added; no host-specific tool name was introduced.

## Verification

- Full gate suite green on `examples/sample-run` and `examples/chronicle-run`;
  all `examples/invalid/` fixtures still fail for exactly their own reason
  (`evidence.no-refute.json` → `ok: true` + `W_NO_REFUTE`, exit 0).
- CI-equivalent spec check (frontmatter lengths, ASCII-only description,
  `license: MIT`, `author: sogeisetsu`, no forbidden host tool names / POSIX-only
  snippets) passes.
- Result card rendered from `templates/result-card.html` (PNG skipped: no
  Playwright in this environment; the filled HTML opens directly).

## Result

Paired 3–0 **better, clear** — kept. Estimated total ≈ **89.0 / 100**
(triage-only). Largest remaining gap is dim8: the skill's discipline adds
verifiability over a fluent baseline answer, but that is hard to move further
without more live runs.
