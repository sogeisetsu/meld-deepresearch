# skill-creator evaluation loop — meld-deepresearch

Archive of the `opencode-skill-creator` evaluation loop run on 2026-10-04:
three behaviour iterations plus a description (trigger) optimization pass.
Raw `benchmark.json` / `benchmark.md` / `feedback.json` for each iteration
live in `iteration-1/`, `iteration-2/`, `iteration-3/`.

## Setup

- **Host**: OpenCode, `opencode run`, one fresh session per run.
- **Model**: `opencode-go/deepseek-v4.1-flash` (pinned, same for every config).
- **Configs**: `with_skill` (the worktree skill) vs `without_skill` (no skill).
- **Evals** (from `docs/eval/README.md` §3): `openai-revenue-quick` (Q2, a
  deliberately unverified number) and `remote-work-normal` (Q3, a contested
  question). One run per eval per config.
- **Grading**: deterministic assertions (report present, structured evidence
  passes `check_evidence.py`, citations resolve, counter-evidence present,
  fetch budget respected); iteration 2+ adds "citations render as portable GFM
  footnotes". Human review via the skill-creator viewer.

## Results

| Iteration | with_skill pass | without_skill pass | with_skill time | with_skill tokens |
|---|---|---|---|---|
| 1 | 7/7, 7/7 | 2/7, 4/7 | 231.7s, 473.8s | 134,575 / 357,405 |
| 2 | 8/8, 8/8 | 2/7, 4/7 | 878s*, 501.4s | n/a*, 374,150 |
| 3 | 8/8, 8/8 | 2/7, 4/7 | 473.8s, 950.7s | 239,762 / 344,431 |

\* iteration-2 `eval-0/with_skill` lost its event stream when a concurrent run
crashed the OpenCode server DB; duration is approximated and the token count
was not captured.

## What changed and why

- **Iteration 1 → 2 (from review feedback).** Citations did not jump: the
  default `<a id>` anchors are stripped by sanitising renderers such as GitHub.
  `render_citations.py` now emits **GFM footnotes by default** (`--anchors`
  restores the old form, `--legacy-plain` the bare text). The Executive Summary
  was also made shorter, and `## Contradictions & Counter-evidence` is required
  to open with a `**Strongest counter-evidence:**` line.
- **Iteration 2 → 3 (from review feedback).** The summary was still a dense
  number-stuffed paragraph. The template now requires a **3–5 bullet TL;DR**
  (answer first, one figure per line, strongest counter-evidence by the third
  line). `content_review.py` gained `W_REVIEW_NO_STRONGEST_COUNTER`,
  `W_REVIEW_SUMMARY_LONG` and `W_REVIEW_SUMMARY_DENSE`, and accepts GFM footnote
  definitions in place of a `## Sources` heading.

## Trigger (description) optimization

18 queries (9 should-trigger, 9 should-not), 60/40 train/test split. The
**original description scored best** (train 11/12, test 6/6); two rewrites did
not beat it on the held-out test, so the description was left unchanged. Most
recorded "failures" were infrastructure errors, not trigger mistakes
(`runsPerQuery=1`, small sample).

## Caveats

- Environment noise: a concurrent evaluation in another worktree plus parallel
  `opencode run` sessions crashed the OpenCode server DB (`insert into "event"`
  failures); iteration-3 was re-run serially after that.
- The iteration-3 human review was not submitted; its verdict rests on the
  deterministic assertions and on the iteration-2 feedback it was built to fix.
