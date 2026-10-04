# File Tree

> Authoritative, annotated file tree for this repository.
> **Depth: 2 levels.** Every entry has a comment explaining what it is for.
> See the update rule at the bottom of this file.

```text
meld-deepresearch/                    # repository root
├── .gitignore                        # ignored: OS/editor junk, Python caches, venvs, .env, local run outputs, .opencode/, .openchamber/, local-only ZH translations
├── .gitattributes                    # line-ending policy: LF in repo for text/*.py/*.md, CRLF for Windows scripts, binary marked
├── AGENTS.md                         # agent-facing project guide: design philosophy, boundaries, conventions, validation commands
├── README.md                         # public overview: positioning, design philosophy, install matrix, usage
├── LICENSE                           # MIT license text (Copyright (c) 2026 sogeisetsu)
├── NOTICE                            # third-party attribution: borrowed projects and their licenses
├── CHANGELOG.md                      # release history, Keep a Changelog format
├── package.json                      # repo metadata for npx / skills CLI (name, version, license, files)
├── ZH/                               # Chinese docs: README-ZH.md is published; CHANGELOG-ZH.md + SKILL-ZH.md are local-only (gitignored)
├── docs/                             # project documentation
│   ├── PLAN.md                       # authoritative development plan: mechanism, milestones, borrow map (Chinese)
│   ├── FILE_TREE.md                  # this file: annotated file tree + update rule
│   ├── index.html                    # GitHub Pages landing page (single self-contained file, zero external requests)
│   ├── og.png                        # 1200x630 social-preview card, referenced by og:image / twitter:image (regenerate from the live hero if the hero changes)
│   ├── eval/                         # Deep Research evaluation standard + three-skill comparison + skill evaluations (README.md + records/)
│   └── .nojekyll                     # tells GitHub Pages to serve docs/ as-is instead of running Jekyll
├── skills/                           # skill packages (this repo ships exactly one)
│   └── meld-deepresearch/            # the skill directory (contents listed in the note below)
├── examples/                         # example artifacts, used by CI
│   ├── sample-run/                   # one complete illustrative run: report.src.md, report.md, sources.md, evidence.json, citations.json, plan.json
│   ├── chronicle-run/                # a chronicle-genre run: background claims, gaps[], source_type, plan genre + must_have_materials
│   └── invalid/                      # negative fixtures: evidence.json files that each fail for exactly one reason + one orphan-citation draft
└── .github/                          # GitHub configuration
    └── workflows/                    # CI: validate.yml (spec check + end-to-end script self-test)
```

**Note — contents of `skills/meld-deepresearch/` (level 3; summarized here to
keep the tree at depth 2).** All entries exist:

```text
skills/meld-deepresearch/
├── SKILL.md                          # the entry point: frontmatter (name/description/license/metadata) + workflow
├── references/                       # progressive-disclosure detail, loaded on demand by the model
│   ├── protocol.md                   # per-axis loop, source-class routing, mandatory refutation, time-sensitivity, merge, gaps[], budgets, gates, failure/retry table, artifacts
│   ├── evidence-contract.md          # claims / evidence / sources / observations / writing_context / key_findings / gaps schema, plan.json, hard rules
│   ├── tier-selection.md             # auto quick-vs-normal decision rules, genre note, worked examples
│   └── report-template.md            # report skeleton (zh/en titles), genre templates, uncertainty grading, citation mechanism, self-check
├── templates/                        # genre append-templates, chosen at plan time
│   └── genres/                       # panorama.md, comparison.md, entity.md, chronicle.md
└── scripts/                          # Python 3 stdlib only, no dependencies
    ├── check_evidence.py             # hard gate: validate evidence.json (incl. background, gaps[], source_type, --plan genre/must_have_materials); errors may carry a "hint"
    ├── render_citations.py           # markers -> clickable anchors/backlinks (default), GFM footnotes, or legacy plain; emits report.md + citations.json
    ├── dedupe_sources.py             # normalize and de-duplicate URLs; emits sources.md (optional source_type column)
    ├── merge_evidence.py             # fold sub_reports/*.evidence.json into one evidence.json, folding duplicate sources and re-pointing references
    └── content_review.py             # warn-only content self-review (sections, language, uncited numbers, gaps); never blocks delivery
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
