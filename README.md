# meld-deepresearch

English · [中文](ZH/README-ZH.md)

A portable Agent Skill that turns a vague topic into a verifiable,
citation-backed research report. It follows the Agent Skills open standard
(`SKILL.md`), so any compatible host can load it straight from a path — no
framework, no vendor lock-in. The repository ships three cooperating skills:
the core research loop plus two optional capability skills.

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

## What it gives you

- Every claim links back to a source that was actually opened; anything
  unverified is labelled `unknown`, never guessed.
- Counter-evidence is searched for on purpose — contradictions and gaps are
  reported, not smoothed over.
- Three hard gates stop a bad run: `check_evidence.py` validates the evidence
  contract, `render_citations.py` rejects orphan or unresolved markers, and
  `content_review.py --clean` fails the reading copy on five codes:
  `E_RUNTIME_TERM`, `E_STANDALONE_SECTION`, `E_FAILURE_NARRATION`,
  `E_APPARATUS_LEAK`, `E_ADVERSARY_CALLOUT` (a labelled
  strongest-counter-evidence callout block).
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
| `skills/meld-da` | Excel & spreadsheet data-analysis workflow (port of SenseNova-Skills `sn-da-excel-workflow`) | Optional Python packages in `requirements.txt`; documented fallback without them |
| `skills/meld-search-academic` | Academic search, paper reading, citation-tree tracing (port of SenseNova-Skills `sn-search-academic`) | Optional Python packages in `requirements.txt` (+ `requirements-optional.txt`); documented fallback without them |

Each skill stands alone; they may invoke one another only along the hand-offs
documented in [`references/protocol.md`](skills/meld-deepresearch/references/protocol.md) §2a.

## Quick start

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

The core skill reuses the host's own search, fetch, file and command
capabilities; it ships no keys and stores no credentials.

## How a run works

```text
probe → clarify → tier → plan → per-axis research → merge → gate ①
     → write → draft review → readability weave → re-run gates
     → dual render → content gate → deliver
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
  the pool, at most three rounds per axis; snippets are never evidence.
- **merge** — `merge_evidence.py` folds the per-axis files into one
  `evidence.json`.
- **gate ①** — `check_evidence.py` on the merged file (plus `--plan` on
  `normal`); a failure stops the run.
- **write** — one draft, `report.src.md`, from validated evidence only; the
  header info block, table of contents, heading rules and the draft's
  standalone discipline chapters are specified in
  [`references/report-template.md`](skills/meld-deepresearch/references/report-template.md).
- **draft review** — warn-only structural checks (section order and the
  expected chapters) run against the draft / cited copy.
- **readability pass** — the discipline material is woven in at any heading
  level: `## Contradictions & Counter-evidence`, `## Gaps & Unknowns`,
  `## Observations` and their H3 stand-ins must not exist in the delivered
  report. Counter-evidence is woven into the paragraph of the claim it
  qualifies; a labelled callout block (`**最强反证：**` /
  `**Strongest counter-evidence:**`) is now a delivery failure, and every
  `unknown` label must survive the weave (weave rules:
  [`references/report-template.md`](skills/meld-deepresearch/references/report-template.md)).
- **re-gate** — every gate runs again on the woven draft.
- **dual render** — one `render_citations.py` run (gate ②) emits both files:
  `report.cited.md` into `.work/`, and its marker-free twin `report.md` at
  the top level; the reading copy never carries an `## Observations`
  section — observations stay in `evidence.json` and `.work/report.cited.md`.
- **content gate** — `content_review.py --clean` on `report.md`, the delivery
  gate: exit 1 on five codes — `E_RUNTIME_TERM`, `E_STANDALONE_SECTION`,
  `E_FAILURE_NARRATION`, `E_APPARATUS_LEAK` and `E_ADVERSARY_CALLOUT`. What
  each code means, and the warn-only list, live in
  [`references/protocol.md`](skills/meld-deepresearch/references/protocol.md)
  §9.
- **deliver** — `dedupe_sources.py` writes the de-duplicated `sources.md`,
  then the full artifact manifest is reported, including gaps and failed
  fetches.

Each gate gets at most one fix-and-retry; a second failure stops the run and
is reported honestly instead of delivered.

## Outputs

Default directory `meld-deepresearch-reports/YYYY-MM-DD-{slug}-{hex4}/`
(a user-supplied path replaces that naming entirely):

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

## License & attribution

MIT — see [`LICENSE`](LICENSE). Author: **sogeisetsu**.
[`NOTICE`](NOTICE) lists every upstream project whose material is ported or
borrowed, including the two SenseNova-Skills ports.
