# Live runs

Rubric and question set are defined in [`../README.md`](../README.md) §2–§3.

## Status

| Question | meld-deepresearch | SenseNova | Weizhena |
|---|---|---|---|
| Q1 industry survey | **run (see below)** | not run | not run |
| Q2 wrong-number check | pending | not run | not run |
| Q3 contested question | not run | not run | not run |
| Q4 latest figure | not run | not run | not run |
| Q5 sparse evidence | not run | not run | not run |
| Q6 vague request | not run | not run | not run |

Opponent skills (`sn-deep-research`, Weizhena `research`) are **not installed in
this environment**, so no cross-skill live comparison has been executed. The
design-level scores in [`design-score.md`](design-score.md) stand in for that
until the opponents are installed and run.

## Self-validation (executed)

The skill's own gate suite was run end-to-end in this worktree and passes:

| Check | Result |
|---|---|
| `check_evidence.py examples/sample-run/evidence.json` | `ok: true` |
| `check_evidence.py … --plan …/plan.json` | `ok: true` |
| `render_citations.py` on the sample | `ok: true`, 4 citations, 0 orphans, 0 uncited |
| `dedupe_sources.py` on the sample | `ok: true`, 4 sources, 0 duplicates |
| 5 negative fixtures | each fails for exactly its own reason, exit 1; `evidence.no-refute.json` → `ok: true` + `W_NO_REFUTE`, exit 0 |

This exercises the whole mechanical spine (contract → gates → render → dedupe)
but on the curated sample, so it scores **axis G on the tooling**, not on a live
research run.

## Q1 — industry survey (meld-deepresearch)

Not executed as a live agent run. `meld-deepresearch` is not installed into this
host's skill directory (`~/.config/opencode/skills/`), so running it "live" here
would be a manual imitation of the protocol rather than the skill actually
firing — which would not be evidence. A real live run must leave the process
artifacts required to score axis G: `plan.json`, per-axis
`sub_reports/dN.evidence.json`, merged `evidence.json`, both gate outputs, and
the four deliverables (`report.md`, `sources.md`, `evidence.json`,
`citations.json`).

Run command (from the repository root, in a scratch output dir):

```bash
python skills/meld-deepresearch/scripts/check_evidence.py \
  <output_dir>/evidence.json --plan <output_dir>/plan.json
python skills/meld-deepresearch/scripts/render_citations.py \
  --report <output_dir>/report.src.md \
  --evidence <output_dir>/evidence.json \
  --output <output_dir>/report.md
python skills/meld-deepresearch/scripts/dedupe_sources.py \
  --evidence <output_dir>/evidence.json \
  --output <output_dir>/sources.md
```

## Why the opponents are not run here

- **SenseNova `sn-deep-research`** requires a SenseNova API key and is documented
  for OpenClaw / hermes-agent only; it depends on sibling skills
  (`sn-prepare-citations`, `sn-ppt-standard`, `sn-search-*`) that must all be
  copied in.
- **Weizhena** requires `pip install pyyaml` and `OPENCODE_ENABLE_EXA=1`.

Both are installable, but installing third-party skills and a pip dependency is a
change to this machine outside the repository's own scope; it is left as an
explicit, separate decision rather than done silently.
