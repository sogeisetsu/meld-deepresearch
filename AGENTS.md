# AGENTS.md

Guidance for AI agents working in this repository. Keep this file lean and
stable; the full development plan lives in `docs/PLAN.md`.

## What this project is

`meld-deepresearch` is a **single, portable Agent Skill** (Agent Skills open
standard, `SKILL.md`) that turns a vague topic into a **verifiable,
citation-backed research report**. It is deliberately *not* a multi-agent
framework: it is one skill that any Agent Skills-compatible host (opencode,
Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, ...) can load as-is.

- Repo (planned): https://github.com/sogeisetsu/meld-deepresearch
- License: MIT

## Design philosophy (do not violate)

1. **Discipline over orchestration.** Quality comes from traceable evidence and
   active falsification, not from more agents.
2. **Lightweight and portable.** One skill, zero runtime dependencies (scripts
   are Python stdlib only), no host-specific tool names.
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
8. **No cross-skill dependencies.** This repo ships exactly one self-contained
   skill.
9. **Tool-agnostic.** Never hardcode host tool names
   (`websearch` / `WebFetch` / `Task` / `AskUserQuestion`).
10. **English artifacts, user-language output.** SKILL.md, references and code
    are English; the generated report follows the user's language.
11. **Delegation is optional.** If the host provides subagents, research axes
    MAY be delegated; otherwise run inline. Never require subagents.

## Repository layout

The authoritative, annotated file tree lives in
**[`docs/FILE_TREE.md`](docs/FILE_TREE.md)**. This file does not duplicate it.

## Non-negotiables (boundaries)

- Do NOT add runtime dependencies; scripts must run on Python 3 stdlib alone.
- Do NOT hardcode host-specific tool names or POSIX-only shell
  (`date +`, `cp -r`, `~/.config`).
- Do NOT create cross-skill dependencies or a second skill in this repo.
- Do NOT let the SKILL.md body exceed ~200 lines; push detail into `references/`.
- Do NOT store secrets/credentials anywhere; the skill reads capabilities from
  the host and never persists keys.
- Do NOT commit artifacts from a live run except the curated
  `examples/sample-run/`.

## Conventions

- Skill ID and directory name: `meld-deepresearch` (lowercase kebab; must match
  the repo name).
- Frontmatter must satisfy the Agent Skills spec: `name` <= 64 chars,
  lowercase-kebab; `description` <= 1024 chars; `license: MIT`; no
  host-specific fields.
- `description` is **English only**.
- All published text (SKILL.md, references, README) is English.
- Scripts: Python 3 stdlib, UTF-8 without BOM, accept both `python` and
  `python3`, print JSON to stdout, exit codes 0 (pass) / 1 (fail) / 2 (bad input).
- Report deliverables: `report.md`, `sources.md`, `evidence.json`,
  `citations.json`.
- Project author: `sogeisetsu`. Use this in `SKILL.md` `metadata.author`, in
  `package.json`, and in the `LICENSE` copyright line.

## Keep the file tree current

The authoritative file tree is **`docs/FILE_TREE.md`**. Whenever you **add a new
file, delete a file, rename or move a file, or change what a file does**, update
`docs/FILE_TREE.md` **in the same change** — add/remove the entry and keep its
comment accurate. Never let the tree drift from reality.

## Validation

```bash
# evidence contract (must be {"ok": true})
python skills/meld-deepresearch/scripts/check_evidence.py \
  examples/sample-run/evidence.json

# citation rendering (must report no orphan / unresolved)
python skills/meld-deepresearch/scripts/render_citations.py \
  --report examples/sample-run/report.src.md \
  --evidence examples/sample-run/evidence.json \
  --output examples/sample-run/report.md
```

CI additionally checks: frontmatter field lengths, English-only `description`,
and that no host-specific tool names appear anywhere in `skills/`.

## Development plan

The full, authoritative plan (milestones M0-M4, file-by-file contents, and the
borrow map) lives in **`docs/PLAN.md`** (written in Chinese). Read it before
implementing. Do not duplicate the plan here; keep this file lean.

## How to work here

- Follow the milestones in `docs/PLAN.md` in order.
- After changing files, read them back and run the validation commands.
- Keep `SKILL.md` lean; move detail into `references/`.
- When borrowing from another project, record it in `NOTICE` and in the borrow
  map in `docs/PLAN.md`.

## License

MIT. See `LICENSE`. Third-party attributions are listed in `NOTICE`.
