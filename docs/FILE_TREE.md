# File Tree

> Authoritative, annotated file tree for this repository.
> **Depth: 2 levels.** Every entry has a comment explaining what it is for.
> See the update rule at the bottom of this file.

```text
meld-deepresearch/                    # repository root
├── .gitignore                        # ignored paths: OS/editor junk, Python caches, venvs, .env, local run outputs, .opencode/
├── .gitattributes                    # line-ending policy: LF in repo for text/*.py/*.md, CRLF for Windows scripts, binary marked
├── AGENTS.md                         # agent-facing project guide: design philosophy, boundaries, conventions, validation commands
├── README.md                         # public overview: positioning, design philosophy, install matrix, usage
├── LICENSE                           # MIT license text (Copyright (c) 2026 sogeisetsu)
├── NOTICE                            # third-party attribution: borrowed projects and their licenses
├── CHANGELOG.md                      # release history, Keep a Changelog format
├── package.json                      # repo metadata for npx / skills CLI (name, version, license, files)
├── docs/                             # project documentation
│   ├── PLAN.md                       # authoritative development plan: mechanism, milestones, borrow map (Chinese)
│   └── FILE_TREE.md                  # this file: annotated file tree + update rule
├── skills/                           # skill packages (this repo ships exactly one)
│   └── meld-deepresearch/            # the skill directory (contents listed in the note below)
├── examples/                         # example outputs, used by CI
│   └── sample-run/                   # planned (M2): one real end-to-end run (report.md, sources.md, evidence.json, citations.json)
└── .github/                          # GitHub configuration
    └── workflows/                    # planned (M2): CI workflows (validate.yml: spec check + script self-test)
```

**Note — contents of `skills/meld-deepresearch/` (level 3; summarized here to
keep the tree at depth 2).** `SKILL.md` and all four `references/` files exist
(M1). `scripts/` is still **planned** (M2) and currently holds only a
`.gitkeep` placeholder:

```text
skills/meld-deepresearch/
├── SKILL.md                          # the entry point: frontmatter (name/description/license/metadata) + workflow
├── references/                       # progressive-disclosure detail, loaded on demand by the model
│   ├── protocol.md                   # search/fetch loop, time-sensitivity, refute obligation, budgets, stop rules
│   ├── evidence-contract.md          # claims / evidence / sources / writing_context / key_findings schema and hard rules
│   ├── tier-selection.md             # auto quick-vs-normal decision rules with examples
│   └── report-template.md            # report skeleton + quality self-check checklist
└── scripts/                          # planned (M2): Python 3 stdlib only, no dependencies
    ├── check_evidence.py             # hard gate: validate evidence.json against the evidence contract
    ├── render_citations.py           # footnotes -> numbered citations; emits report.md + citations.json
    └── dedupe_sources.py             # normalize and de-duplicate URLs; emits sources.md
```

---

## Update rule

Whenever a file or directory is **added, deleted, renamed/moved, or its purpose
changes**, update this file tree **in the same change**:

1. Add or remove the corresponding entry.
2. Keep the comment accurate — it must describe what the entry actually does.
3. Keep the tree at **depth 2** (use a summary note like the one above for
   deeper nesting such as `skills/meld-deepresearch/`).

Related: `AGENTS.md` (project conventions) and `docs/PLAN.md` section 4 both
point here instead of duplicating the tree.
