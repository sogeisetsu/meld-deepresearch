# meld-deepresearch

English · [中文](ZH/README-ZH.md)

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

A lightweight, portable Agent Skill family for verifiable, citation-backed deep research reports.

A portable Agent Skill that turns a vague topic into a verifiable,
citation-backed research report. It follows the Agent Skills open standard
(`SKILL.md`), so any compatible host can load it straight from a path — no
framework, no vendor lock-in. The repository ships three cooperating skills:
the core research loop plus two optional capability skills.

## Table of Contents

- [Install](#install)
- [Usage](#usage)
- [What it gives you](#what-it-gives-you)
- [Skills in this repo](#skills-in-this-repo)
- [How a run works](#how-a-run-works)
- [Running the gates](#running-the-gates)
- [Outputs](#outputs)
- [When to use it / when not to](#when-to-use-it--when-not-to)
- [Requirements](#requirements)
- [Documentation](#documentation)
- [Validation](#validation)
- [Contributing](#contributing)
- [License](#license)

## Install

Two one-liners can install these skills — **use whichever CLI you already
have: they are alternatives, not two steps**:

- `npx skills add` (the skills.sh CLI) needs **Node.js**.
- `gh skill install` needs **GitHub CLI v2.90+** (the `gh skill` command is in
  preview).

All three skills — pick **one** of the two lines:

```bash
npx skills add sogeisetsu/meld-deepresearch --all    # with Node.js
gh skill install sogeisetsu/meld-deepresearch --all  # with GitHub CLI v2.90+
```

Core skill only — the same two options, naming the single skill:

```bash
npx skills add sogeisetsu/meld-deepresearch --skill meld-deepresearch
gh skill install sogeisetsu/meld-deepresearch meld-deepresearch
```

Manual install (no CLI): copy the skill directories from [`skills/`](skills/)
into the host's skills directory (e.g. `~/.agents/skills/`).

Notes:

- `npx` and `gh` install the same skills through different tools — running both
  would install them twice.
- A bare `gh skill install owner/repo <name>` installs only that one named
  skill — pass `--all` to install all three.
- Run non-interactively, `gh` defaults to `--agent github-copilot`, so pass
  `--agent <host>`; the `npx` equivalent is `-a <host>`.
- Both CLIs discover the repo's three skills via the `skills/*/SKILL.md`
  convention.

## Usage

1. Clone this repository anywhere on disk.
2. Point your host at it: a host loads a skill by reading
   `skills/<name>/SKILL.md`. Per-host skill directories are listed in your
   host's own documentation; a project-local `skills/` directory works in
   most hosts.
3. Optional — for the capability skills, install the packages listed in that
   skill's `requirements.txt`. Without them the skill degrades to its
   documented fallback.
4. Start a new session and ask for research: a cited report, a comparison, a
   literature review, a fact-check. The skill's `description` does the
   matching; there is nothing to configure.
5. Pick up the deliverables from the run's output directory (see
   **Outputs**).

A typical ask, once the skill is loaded:

```text
Write a cited comparison report on this topic — a source behind every
claim, gaps and contradictions reported, unverified claims labelled unknown.
```

The core skill reuses the host's own search, fetch, file and command
capabilities; it ships no keys and stores no credentials.

## What it gives you

- Every claim links back to a source that was actually opened; anything
  unverified is labelled `unknown`, never guessed.
- Counter-evidence is searched for on purpose — contradictions and gaps are
  reported, not smoothed over.
- Three hard gates stop a bad run — `meld.py prepare` (gate ①),
  `meld.py render` (gate ②) and `meld.py review --clean` (the content gate;
  each a subcommand of the thin CLI
  `skills/meld-deepresearch/scripts/meld.py` over the raw scripts): the
  evidence contract is validated by `check_evidence.py`, orphan or unresolved
  markers are rejected by `render_citations.py`, and the reading copy is
  judged against three hard delivery codes — with two more shapes
  (`E_STANDALONE_SECTION`, `E_ADVERSARY_CALLOUT`) reported as warnings —
  whose exact meaning and the warn-only
  list beside them live in
  [`references/protocol.md`](skills/meld-deepresearch/references/protocol.md) §9.
- Two effort tiers, `quick` and `normal`, selected from the question and
  overridable — no multi-agent machinery required.
- One renderer run yields both report files: `report.md`, the reading copy
  you hand over, and the citation-annotated `report.cited.md`, which stays in
  `.work/` as middleware rather than a deliverable.
- Core scripts are Python 3 standard library only; the skill itself has no
  runtime dependencies.
- Files are the source of truth: artifacts land on disk, the model context
  keeps conclusions only.

## Skills in this repo

| Directory | Purpose | Dependencies |
|---|---|---|
| `skills/meld-deepresearch` | Core research / evidence / citation loop | None — Python 3 stdlib |
| `skills/meld-da` | Excel & spreadsheet data-analysis workflow (adapted from SenseNova-Skills `sn-da-excel-workflow`) | Optional Python packages in `requirements.txt`; documented fallback without them |
| `skills/meld-search-academic` | Academic search, paper reading, citation-tree tracing (adapted from SenseNova-Skills `sn-search-academic`) | Optional Python packages in `requirements.txt` (+ `requirements-optional.txt`); documented fallback without them |

Each skill stands alone; they may invoke one another only along the hand-offs
documented in [`references/protocol.md`](skills/meld-deepresearch/references/protocol.md) §2a.

## How a run works

```text
probe → clarify → tier → plan → per-axis research → merge → gate ①
     → write → draft review → readability pass
     → gate ② (dual render) → content gate → deliver
```

- **probe** — check which host capabilities exist; a missing blocking one
  stops the run and says so.
- **clarify** — up to three questions, or explicit assumptions written down
  when nobody can answer.
- **tier** — `quick` (one self-contained thread) or `normal` (several
  independently searchable axes).
- **plan** — `normal` runs name their research axes and key questions in
  `plan.json`.
- **per-axis research** — search → open the original page → evaluate → refill
  the pool (per-tier rounds caps: [`references/protocol.md`](skills/meld-deepresearch/references/protocol.md)
  §8; snippets are never evidence: §2 rule 3).
- **merge** — `meld.py prepare` (its merge half, raw `merge_evidence.py`)
  folds the per-axis files into one `evidence.json`.
- **gate ①** — the same `meld.py prepare` then runs `check_evidence.py` on the
  merged file (plus `--plan` on `normal`, added automatically when
  `.work/plan.json` exists); a failure stops the run.
- **write** — one draft, `report.src.md`, from validated evidence only; the
  header info block, table of contents, heading rules and the draft's
  standalone discipline chapters are specified in
  [`references/report-template.md`](skills/meld-deepresearch/references/report-template.md).
- **draft review** — warn-only structural checks (section order and the
  expected chapters) run against the draft / cited copy.
- **readability pass** — the discipline material is woven into the narrative
  at every heading level and every `unknown` label survives the weave; the
  weave rules and the shapes the delivery gate checks live in
  [`references/report-template.md`](skills/meld-deepresearch/references/report-template.md).
- **re-gate** — after prose edits only the delivery gate re-runs:
  `meld.py review --clean`.
- **dual render** — one `meld.py render` run (gate ②; raw `render_citations.py`)
  emits both files:
  `report.cited.md` into `.work/`, and its marker-free twin `report.md` at
  the top level; the reading copy never carries an `## Observations`
  section — observations stay in `evidence.json` and `.work/report.cited.md`.
- **content gate** — `meld.py review --clean` (raw `content_review.py --clean`)
  on `report.md`, the delivery
  gate: exit 1 on three codes — `E_RUNTIME_TERM`, `E_FAILURE_NARRATION` and
  `E_APPARATUS_LEAK` — while `E_STANDALONE_SECTION` (chapter left standing)
  and `E_ADVERSARY_CALLOUT` (labelled callout) are detected and reported as
  warnings, exit 0. What
  each code means, and the warn-only list, live in
  [`references/protocol.md`](skills/meld-deepresearch/references/protocol.md)
  §9.
- **deliver** — `meld.py sources` (raw `dedupe_sources.py`) writes the
  de-duplicated `sources.md`,
  then the full artifact manifest is reported, including gaps and failed
  fetches.

Stop rules for a failing gate or stage — one fix-and-retry, then stop and
report honestly instead of delivering — live in
[`references/protocol.md`](skills/meld-deepresearch/references/protocol.md)
§9–§10.

## Running the gates

[`references/protocol.md`](skills/meld-deepresearch/references/protocol.md) §9
is the authoritative command list: copy its `OUTDIR` gate-command block and
run it from the skill's own directory. `scripts/meld.py` is the thin CLI
(`prepare`, `render`, `review [--clean]`, `sources`, `verify`) over the raw
scripts (`merge_evidence.py`, `check_evidence.py`, `render_citations.py`,
`content_review.py`, `dedupe_sources.py`), which stay equivalent and
independently runnable — both forms sit side by side in that §9 block.

## Outputs

Default directory `meld-deepresearch-reports/YYYY-MM-DD-{slug}-{hex4}/`
(the naming rule and what a user-supplied path does to it:
[`references/protocol.md`](skills/meld-deepresearch/references/protocol.md)
§11):

| File | Contents |
|---|---|
| `report.md` | **The deliverable** — marker-free reading copy: line-1 pointer → header info block → table of contents → content → `## Sources`; it never carries an `## Observations` section |
| `sources.md` | De-duplicated source list |
| `evidence.json` | Merged, gate-checked evidence behind every claim |
| `citations.json` | Citation map linking markers to their sources |

`.work/` beside them holds the middleware: `plan.json` (normal tier), the
pre-render draft `report.src.md`, the citation-annotated `report.cited.md`
that the same render produced (middleware, not a deliverable), and per-axis
`sub_reports/`.

## When to use it / when not to

**Use it when** the answer must rest on more than one source and be
checkable: landscape or trend scans, competitive comparisons, literature
reviews, fact-checking, any explicit request for a cited report or brief.

**Do not use it when** one direct answer would do: definitions, one-line
lookups, tidying sources you already hold, pure rewriting or translation, or
an opinion piece where no evidence is expected.

## Requirements

- A host that implements the Agent Skills standard (`SKILL.md`).
- Network search, page fetch, file read/write, and command execution; the
  skill degrades gracefully when optional capabilities are missing and says
  so in its output.
- Python 3 to run the gates and renderers (standard library only for the
  core skill).
- Runs on Linux, macOS and Windows; the two capability skills carry their own
  `Platform notes (pure Windows)` sections.

## Documentation

- Skill entry point: [`skills/meld-deepresearch/SKILL.md`](skills/meld-deepresearch/SKILL.md)
- Protocol, budgets, gates: [`references/protocol.md`](skills/meld-deepresearch/references/protocol.md)
- Evidence schema: [`references/evidence-contract.md`](skills/meld-deepresearch/references/evidence-contract.md)
- Evaluation standard and three-skill comparison: [`docs/eval/README.md`](docs/eval/README.md)
- Annotated file tree: [`docs/FILE_TREE.md`](docs/FILE_TREE.md)
- Development plan and milestones: [`docs/PLAN.md`](docs/PLAN.md)

## Validation

The full validation set — positive fixtures, negative fixtures, and every
renderer mode — is listed in [`AGENTS.md`](AGENTS.md) and executed by CI.

## Contributing

Questions are welcome — please open a
[GitHub issue](https://github.com/sogeisetsu/meld-deepresearch/issues).
Pull requests are accepted; the bar for a PR is that the validation battery
listed in [`AGENTS.md`](AGENTS.md) passes.

## License

MIT — see [`LICENSE`](LICENSE). Author: **sogeisetsu**.
[`NOTICE`](NOTICE) lists every upstream project whose material is ported or
borrowed, including the two SenseNova-Skills ports.
