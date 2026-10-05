# AGENTS.md

Guidance for AI agents working in this repository. Keep this file lean and
stable; the full development plan lives in `docs/PLAN.md`.

## What this project is

`meld-deepresearch` is a **portable Agent Skill** (Agent Skills open
standard, `SKILL.md`) that turns a vague topic into a **verifiable,
citation-backed research report**. It is deliberately *not* a multi-agent
framework: quality comes from evidence discipline, not from orchestration.
The repository ships **several cooperating skills** — the core research
skill plus optional capability skills it can invoke:

- `skills/meld-deepresearch` — the core research / evidence / citation loop.
- `skills/meld-da` — spreadsheet & data-analysis workflow (port of
  SenseNova-Skills `sn-da-excel-workflow`).
- `skills/meld-search-academic` — academic search, paper reading and
  citation-tree tracing (port of SenseNova-Skills `sn-search-academic`).

Skills may call each other where a documented hand-off exists (see
`references/protocol.md` §2a). Any Agent Skills-compatible host (opencode,
Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, ...) can load them as-is.

- Repo (planned): https://github.com/sogeisetsu/meld-deepresearch
- License: MIT

## Design philosophy (do not violate)

1. **Discipline over orchestration.** Quality comes from traceable evidence and
   active falsification, not from more agents.
2. **Lightweight and portable.** Skills ship as plain `SKILL.md` trees a host
   can load without installation; no host-specific tool names. Third-party
   Python packages are allowed where a capability genuinely needs them, but the
   core research scripts stay Python-stdlib-only.
3. **Files are the source of truth.** Research artifacts are written to disk;
   the model context keeps only conclusions.
4. **Mechanical gates over good intentions.** Evidence rules are enforced by a
   validator that can fail the run.
5. **Two tiers, not three.** `quick` / `normal`, auto-selected. No heavy
   multi-agent orchestration.
6. **Verifiability over polish.** Every claim is clickable; unknown is labeled
   `unknown`.
7. **Falsification is mandatory.** Counter-evidence and contradictions must be
   actively searched, never assumed absent.
8. **Cooperating skills, one direction of dependency.** Multiple skills are
   allowed and may invoke each other only along documented hand-offs; no
   undocumented coupling, no skill that only works when another is installed
   (every skill degrades on its own).
9. **Tool-agnostic.** Never hardcode host tool names — describe the host's
   own search, fetch, delegate and ask-user tools by capability, not by the
   name one particular host happens to give them.
10. **English artifacts, user-language output.** SKILL.md, references and code
    are English; the generated report follows the user's language.
11. **Delegation is optional.** If the host provides subagents, research axes
    MAY be delegated; otherwise run inline. Never require subagents.

## Repository layout

The authoritative, annotated file tree lives in
**[`docs/FILE_TREE.md`](docs/FILE_TREE.md)**. This file does not duplicate it.

## Non-negotiables (boundaries)

- Multiple skills in this repo are allowed, and skills may invoke each other
  only through documented hand-offs (`references/protocol.md` §2a).
- Third-party Python dependencies are allowed for capability skills that need
  them (`skills/meld-da`, `skills/meld-search-academic`); they must be declared
  in that skill's `requirements.txt` and must degrade to a documented fallback
  when absent. The core `skills/meld-deepresearch/scripts/*.py` stay Python 3
  stdlib only.
- Do NOT hardcode host-specific tool names or POSIX-only shell
  (`date +`, `cp -r`, `~/.config`).
- Published text stays English (SKILL.md, references, README, docs); the
  generated report follows the user's language.
- `main` is always mergeable; nothing is ever pushed without explicit approval.
- Every script prints JSON to stdout and exits 0 (pass) / 1 (fail) / 2 (bad input).
- Do NOT let `skills/meld-deepresearch/SKILL.md` exceed ~120 lines; push detail
  into `references/`.
- Do NOT store secrets/credentials anywhere; skills read credentials from
  environment variables and never persist keys.
- Do NOT commit artifacts from a live run except the curated
  `examples/sample-run/`.

## Conventions

- **`ZH/` mirrors stay in sync with their English originals — in the same
  change.** `ZH/README-ZH.md` mirrors `README.md` (published), and
  `ZH/SKILL-ZH.md` / `ZH/CHANGELOG-ZH.md` mirror
  `skills/meld-deepresearch/SKILL.md` / `CHANGELOG.md` (local-only). A mirror
  must stay **section-parallel**: same sections, same order, same tables, same
  codes and paths — translate the change, never drop it and never leave a
  mirror silently stale. English frontmatter (`name` / `description` /
  `compatibility`) stays byte-identical in a mirror; it is spec-facing English.
  If a change genuinely cannot be translated in this pass, say so explicitly in
  the commit message and leave a dated TODO at the top of the mirror — silence
  is the only forbidden state.
- Skill IDs and directory names: `meld-deepresearch`, `meld-da`,
  `meld-search-academic` (lowercase kebab; each directory name matches its
  `name:` frontmatter).
- Frontmatter must satisfy the Agent Skills spec: `name` <= 64 chars,
  lowercase-kebab; `description` <= 1024 chars and ASCII-only English;
  `license: MIT`; no host-specific fields.
- `description` is **English only**.
- All published text (SKILL.md, references, README) is English.
- Scripts: Python 3 stdlib, UTF-8 without BOM, accept both `python` and
  `python3`, print JSON to stdout, exit codes 0 (pass) / 1 (fail) / 2 (bad input).
- Report deliverables: four top-level files — `report.md` (clean reading
  copy), `sources.md`, `evidence.json`, `citations.json`. The
  citation-annotated `report.cited.md` is middleware that lives in
  `.work/report.cited.md`; it sits at the top level of
  `examples/sample-run/` only as a CI fixture.
- Project author: `sogeisetsu`. Use this in `SKILL.md` `metadata.author`, in
  `package.json`, and in the `LICENSE` copyright line.
- One authoritative home per topic, so copies cannot drift silently:
  budgets and stop rules live in `references/protocol.md` §8; the evidence
  schema and its hard rules live in `references/evidence-contract.md`; the gate
  commands live in `references/protocol.md` §9 (`SKILL.md` §9 only points
  there). Other files may summarise them, but a summary must always match its
  source.

## Keep the file tree current

The authoritative file tree is **`docs/FILE_TREE.md`**. Whenever you **add a new
file, delete a file, rename or move a file, or change what a file does**, update
`docs/FILE_TREE.md` **in the same change** — add/remove the entry and keep its
comment accurate. Never let the tree drift from reality.

## Validation

Run these from the repository root. Use `python3` if `python` is not available.

```bash
# positive: the curated example must be valid
python skills/meld-deepresearch/scripts/check_evidence.py \
  examples/sample-run/evidence.json

# positive: cross-check the sample against its research plan
python skills/meld-deepresearch/scripts/check_evidence.py \
  examples/sample-run/evidence.json --plan examples/sample-run/plan.json

# citation rendering — ONE run writes both report files:
#   .work/report.cited.md keeps the markers and the full reference block
#     (middleware; gate ② judges this file; committed at the top level of
#     examples/sample-run/ only as a CI fixture)
#   report.md is the marker-free reading copy, first line linking to the cited
#     copy by a RELATIVE path (.work/report.cited.md in a real run,
#     report.cited.md when both live in the same directory, as in this fixture)
# Real-run shape (four top-level deliverables: report.md, sources.md,
# evidence.json, citations.json; --citations keeps citations.json at the top
# level instead of next to --output in .work/):
#   python skills/meld-deepresearch/scripts/render_citations.py \
#     --report .work/report.src.md --evidence evidence.json \
#     --output .work/report.cited.md --clean-output report.md \
#     [--citations citations.json]
# Fixture render (both copies side by side, for the CI fixtures):
python skills/meld-deepresearch/scripts/render_citations.py \
  --report examples/sample-run/report.src.md \
  --evidence examples/sample-run/evidence.json \
  --output examples/sample-run/report.cited.md \
  --clean-output examples/sample-run/report.md

# standalone source list
python skills/meld-deepresearch/scripts/dedupe_sources.py \
  --evidence examples/sample-run/evidence.json \
  --output examples/sample-run/sources.md

# positive: the chronicle-genre example must be valid
python skills/meld-deepresearch/scripts/check_evidence.py \
  examples/chronicle-run/evidence.json --plan examples/chronicle-run/plan.json

# positive: merging the two-axis fixture must yield a gate-passing file
# (a source shared across axes folds to one id with references re-pointed)
python skills/meld-deepresearch/scripts/merge_evidence.py \
  --subreports examples/merge-run/sub_reports \
  --output .work/tmp/merge-run.json
python skills/meld-deepresearch/scripts/check_evidence.py .work/tmp/merge-run.json

# content review runs twice. First the structural pass on the cited copy
# (warn-only, exit 0; in a real run that copy is .work/report.cited.md)
python skills/meld-deepresearch/scripts/content_review.py \
  --report examples/sample-run/report.cited.md \
  --evidence examples/sample-run/evidence.json
# then the delivery gate on the reading copy: --clean fails (exit 1) on the
# runtime-failure blacklist (E_RUNTIME_TERM), on a standalone discipline
# chapter that survived the weave (E_STANDALONE_SECTION, H2 or H3, EN or ZH,
# including the observation section), on narration of a run failure to the
# reader (E_FAILURE_NARRATION), on internal apparatus (E_APPARATUS_LEAK) and
# on a labelled counter-evidence callout (E_ADVERSARY_CALLOUT);
# warn-only: W_PROSE_RATIO, W_NO_TOC, W_THIN_TOC, W_NO_INFO_BLOCK,
# W_NO_UNCERTAINTY, W_NO_DEFINITIONS, W_GENERIC_HEADING, W_APPARATUS_LEAK and
# the ambiguous-term W_RUNTIME_TERM (expected here: exit 0)
python skills/meld-deepresearch/scripts/content_review.py --clean \
  --report examples/sample-run/report.md \
  --evidence examples/sample-run/evidence.json

# a tertiary-only factual claim passes ONLY with its downgrade annotation
# (expected: ok true, warning W_DOWNGRADE, exit 0)
python skills/meld-deepresearch/scripts/check_evidence.py \
  examples/downgrade-run/evidence.json

# capability-skill degrade paths (stdlib only, no network)
python skills/meld-da/tests/test_degrade.py
python skills/meld-search-academic/tests/test_degrade.py

# zero-dependency reader self-test (stdlib only; builds a fixture xlsx and a
# fixture .docx in memory)
python skills/meld-deepresearch/scripts/read_table.py --selftest

# gate ② must reject blank markers in the default (GFM-footnote) mode
# (expected output {"ok": false, ...}, exit 1)
python skills/meld-deepresearch/scripts/render_citations.py \
  --report examples/invalid/report.empty-marker.src.md \
  --evidence examples/invalid/evidence.no-refute.json \
  --output .work/tmp/empty-marker.md

# the three render modes must each emit their own marker form
# default: footnote definitions [^1]: / [^o1]:
python skills/meld-deepresearch/scripts/render_citations.py \
  --report examples/sample-run/report.src.md \
  --evidence examples/sample-run/evidence.json \
  --output .work/tmp/report.fn.md
# --anchors: [[1]](#ref-1) links plus <a id="cite-1"></a> cite anchors
# --legacy-plain: bare [1] source markers plus [O1] observation markers
python skills/meld-deepresearch/scripts/render_citations.py --anchors \
  --report examples/sample-run/report.src.md \
  --evidence examples/sample-run/evidence.json \
  --output .work/tmp/report.anchors.md
python skills/meld-deepresearch/scripts/render_citations.py --legacy-plain \
  --report examples/sample-run/report.src.md \
  --evidence examples/sample-run/evidence.json \
  --output .work/tmp/report.legacy.md
```

Negative fixtures in `examples/invalid/` must each fail for exactly their own
reason: `evidence.unknown-source.json` → `E_REF_SOURCE`, `evidence.tertiary-only.json`
→ `E_FACTUAL_SOURCE`, `evidence.single-source-interpretive.json` →
`E_INTERPRETIVE_TWO`, `evidence.interpretive-tertiary-pair.json` →
`E_INTERPRETIVE_CREDIBLE`, `evidence.finding-single-source.json` →
`E_FINDING_BASIS`, `evidence.bad-observation.json` → `E_REF_OBSERVATION`,
`evidence.finding-background.json` → `E_FINDING_BACKGROUND`,
`evidence.gap-bad-enum.json` → `E_GAP_ENUM`, `evidence.gap-bad-ref.json` →
`E_GAP_REF`, `evidence.gap-bad-shape.json` → `E_GAP_SHAPE`
(all exit 1); `evidence.no-refute.json` → `ok: true` with
`W_NO_REFUTE` (exit 0). Fixtures that test a non-finding rule carry
`key_findings: []` so no second rule can fire. `report.orphan.src.md` fails
gate ② (exit 1), and so does `report.empty-marker.src.md` — its blank `[^]` /
`[^ ]` markers must fail gate ② in the default GFM-footnote mode (exit 1).
`report.runtime-jargon.src.md` renders cleanly but its reading copy must fail
`content_review.py --clean` with `E_RUNTIME_TERM` (exit 1); likewise
`report.standalone-section.src.md` → `E_STANDALONE_SECTION`,
`report.failure-narration.src.md` → `E_FAILURE_NARRATION` (the reader is never
told that a page needed a login or could not be opened — that belongs in
`observations[]`/`gaps[]`, while the report states the epistemic status
instead), and `report.adversary-callout.src.md` → `E_ADVERSARY_CALLOUT` (a
labelled `**最强反证：**` / `**Strongest counter-evidence:**` block; the
counter-evidence belongs in the paragraph of the claim it qualifies). The delivery-gate positive is `examples/sample-run/report.md`
(`content_review.py --clean`, exit 0); the evidence-gate positive counterpart
is `examples/downgrade-run/evidence.json` (exit 0, `W_DOWNGRADE`).

CI has **two jobs**. The `core` job installs nothing and must be green: the
frontmatter/spec check over every `skills/*/SKILL.md` (field lengths, English-only
ASCII `description`, `license`, `metadata.author`, name-matches-directory), the
whole script self-test above — including the delivery-gate negatives
(runtime jargon → `E_RUNTIME_TERM`, standalone discipline chapter →
`E_STANDALONE_SECTION`, labelled counter-evidence callout →
`E_ADVERSARY_CALLOUT`) against the zero-warning positive
`examples/sample-run/report.md` — and the stdlib-only degrade-path unit tests of
both capability skills. The `optional` job runs the **full install** of the declared
`requirements.txt` files (plus the optional browser tier), re-runs the
degrade-path tests with the packages present, AST-parses every shipped script,
and re-runs the core gates; when `pip install` fails it records the reason in the
job summary and skips those steps instead of failing — network unavailability is
never a CI failure, a code problem always is.

## Development plan

The full, authoritative plan (milestones M0-M4, file-by-file contents, and the
borrow map) lives in **`docs/PLAN.md`** (written in Chinese). Read it before
implementing. Do not duplicate the plan here; keep this file lean.

## How to work here

- **Work on a branch.** Never develop directly on `main`. Create a short-lived
  branch for each change or milestone (`feat/...`, `fix/...`, `chore/...`), do
  the work and validate it there, then merge it back into `main` once it is
  done. Keep `main` always valid.
- **Write file contents in English whenever possible.** Docs, code, comments
  and commit messages default to English, so the project stays readable to an
  international audience. (Known exception: `docs/PLAN.md` is currently
  written in Chinese. The *generated research report* follows the end user's
  language.)
- Follow the milestones in `docs/PLAN.md` in order.
- After changing files, read them back and run the validation commands.
- Keep `SKILL.md` lean; move detail into `references/`.
- When borrowing from another project, record it in `NOTICE` and in the borrow
  map in `docs/PLAN.md`.

## License

MIT. See `LICENSE`. Third-party attributions are listed in `NOTICE`.
