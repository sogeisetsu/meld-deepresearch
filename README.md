# meld-deepresearch

A **lightweight, portable Agent Skill** that turns a vague topic into a
**verifiable, citation-backed research report**.

One skill, no framework. It runs on any host that supports the
[Agent Skills](https://agentskills.io) open standard — opencode, Claude Code,
Codex, Cursor, GitHub Copilot, Gemini CLI, and more — and it never locks you
into one vendor.

> **Status:** the skill is implemented (`SKILL.md`, `references/`, `scripts/`)
> and exercised by CI on a curated example; publication is still pending (M4).
> See [`docs/PLAN.md`](docs/PLAN.md).

## Why another deep-research skill

Most deep-research tooling is either a heavy multi-agent framework or a thin
prompt. `meld-deepresearch` takes the middle path:

1. **Discipline over orchestration.** Quality comes from traceable evidence and
   active falsification, not from more agents.
2. **Lightweight and portable.** One skill, zero runtime dependencies (scripts
   are Python standard library only), no host-specific tool names.
3. **Files are the source of truth.** Research artifacts are written to disk;
   the model context keeps only conclusions.
4. **Mechanical gates over good intentions.** A validator enforces the evidence
   rules and can fail the run.
5. **Two tiers, not three.** `quick` / `normal`, chosen automatically from the
   question. No heavy orchestration.
6. **Verifiability over polish.** Every claim is clickable; anything unverified
   is labeled `unknown`.
7. **Falsification is mandatory.** Counter-evidence and contradictions are
   actively searched, never assumed absent.

It borrows the best ideas from both open-source and big-tech deep research
(evidence contracts, source quality tiers, refute obligations, budget-aware
stopping, multi-perspective questioning) and distills them into a single,
self-contained skill. See [`NOTICE`](NOTICE) and `docs/PLAN.md` section 7.

## Install

The skill is a directory containing `SKILL.md`, `references/`, and `scripts/`.
Install it with any of the following.

### One-liners

```bash
# skills.sh / Vercel skills CLI (installs into ~40 supported hosts)
npx skills add sogeisetsu/meld-deepresearch

# GitHub CLI (v2.90.0+), works across Copilot, Claude Code, Cursor, Codex, Gemini
gh skill install sogeisetsu/meld-deepresearch meld-deepresearch
```

### Manual (per host)

Copy `skills/meld-deepresearch/` into your host's skills directory.
The cross-tool path `~/.agents/skills/` is recognized by several hosts.

| Host | Global | Project-local |
|---|---|---|
| opencode | `~/.config/opencode/skills/` or `~/.agents/skills/` | `.opencode/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Codex | `~/.codex/skills/` or `~/.agents/skills/` | `.codex/skills/` |
| Cursor | — | `.cursor/skills/` |
| GitHub Copilot | `~/.copilot/skills/` or `~/.agents/skills/` | `.github/skills/` |
| Gemini CLI | `~/.gemini/skills/` or `~/.agents/skills/` | `.gemini/skills/` |

> Discovery paths vary by host and version; check your host's documentation if
> a skill does not appear.

No configuration is required. The skill uses the host's model; you do not
configure a model for it.

## Usage

Just ask for research. The skill advertises itself via its `description` and is
loaded on demand when the request matches (deep research, systematic research,
competitive analysis, literature review, trend analysis, fact-checking, a cited
report, ...).

It then picks a tier automatically:

- **`quick`** — one self-contained research thread (a brief, a single answer, a
  point check).
- **`normal`** — several independently searchable axes, entity comparison, a
  full report, or conflicting evidence expected.

You can override the tier explicitly.

### Output

Each run produces four artifacts under
`meld-deepresearch-reports/YYYY-MM-DD-{slug}-{hex4}/`:

| File | What it is |
|---|---|
| `report.md` | The final report, with inline numbered citations |
| `sources.md` | De-duplicated source list |
| `evidence.json` | Structured claims, evidence, sources, and boundaries |
| `citations.json` | The citation map used to render `report.md` |

If the host has no filesystem access, the report is returned inline instead.

## How it works

```text
probe capabilities
  -> anchor language / format / output dir
  -> clarify (1-3 questions, or write explicit assumptions)
  -> choose tier (quick | normal)
  -> plan (normal: named research axes)
  -> research loop: search -> URL pool -> fetch -> read -> evaluate -> gaps
  -> merge per-axis evidence  ->  evidence.json
  -> self-check (hard gate: evidence validator)
  -> write report  ->  report.src.md
  -> render citations (hard gate: no orphan/unresolved)  ->  report.md + citations.json
  -> build sources.md (URL normalization + de-duplication)
  -> deliver report.md + sources.md + evidence.json + citations.json
```

Key rules: search before fetch, never admit a snippet without reading the
original page, actively search counter-evidence, respect time-sensitivity, and
stop at the budget (returning the best coverage found rather than looping
forever).

## Requirements

- A host that supports the Agent Skills standard.
- Network search and fetch capability.
- File read/write and command execution (for the scripts and artifacts).
- Python 3 (standard library only) for the validator, the citation renderer and
  the source de-duplicator; the run degrades gracefully when those scripts
  cannot be executed, and says so in its output.

## References and acknowledgements

This skill stands on the shoulders of many projects. The full borrow map is in
`docs/PLAN.md` section 7 and the attribution list is in [`NOTICE`](NOTICE).
The two clearest influences are:

- [SenseNova-Skills](https://github.com/OpenSenseNova/SenseNova-Skills) (MIT)
  — the evidence contract, validators, and citation rendering.
- [Weizhena/Deep-Research-skills](https://github.com/Weizhena/Deep-Research-skills)
  (MIT) — the two-phase flow and human-in-the-loop checkpoints.

## Development

- Project conventions for agents: [`AGENTS.md`](AGENTS.md)
- Authoritative plan and milestones: [`docs/PLAN.md`](docs/PLAN.md)

Run the local checks from the repository root:

```bash
python skills/meld-deepresearch/scripts/check_evidence.py \
  examples/sample-run/evidence.json
```

The full validation set — the positive example plus the negative fixtures in
`examples/invalid/` — is listed in [`AGENTS.md`](AGENTS.md) and is executed by
CI in `.github/workflows/validate.yml`.

## License

MIT. See [`LICENSE`](LICENSE).
