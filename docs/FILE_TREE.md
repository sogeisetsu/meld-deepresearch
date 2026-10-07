# File Tree

> Authoritative, annotated file tree for this repository.
> **Depth: 2 levels.** Every entry has a comment explaining what it is for.
> See the update rule at the bottom of this file.

```text
meld-deepresearch/                    # repository root
├── .gitignore                        # ignored: OS/editor junk, Python caches, venvs, build/dist and temp/backup artifacts, Node install/pack artifacts, .env, local run outputs, .opencode/, .openchamber/, local-only ZH translations, local .worktrees/
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
│   ├── eval/                         # evaluation standard (README.md, with a Records index) + records/: design-score.md, live-runs.md, skill-creator-iterations/, sensenova-live/ (frozen-baseline live comparison: protocol, per-example scores, and baseline-f05bcbc.json — the frozen per-axis medians exported from the committed round-3 record)
│   └── .nojekyll                     # tells GitHub Pages to serve docs/ as-is instead of running Jekyll
├── skills/                           # skill packages (this repo ships three)
│   ├── meld-deepresearch/            # core research/evidence/citation skill (contents in the note below)
│   ├── meld-da/                      # Excel/spreadsheet analysis workflow: SKILL.md + capability/**/SKILL.md sub-skills + tests/ degrade unit test (adapted from SenseNova sn-da-excel-workflow)
│   └── meld-search-academic/         # academic search/paper/refTree skill: SKILL.md, references/, scripts/, tests/ degrade unit test, requirements.txt + requirements-optional.txt (adapted from SenseNova sn-search-academic)
├── examples/                         # example artifacts, used by CI
│   ├── sample-run/                   # one complete illustrative run: report.src.md, report.cited.md (the cited copy is middleware — .work/report.cited.md in a real run, committed here at the top level for the CI fixtures only), report.md (reading copy), sources.md, evidence.json, citations.json, plan.json
│   ├── chronicle-run/                # a chronicle-genre run: background claims, gaps[], source_type, plan genre + must_have_materials
│   ├── downgrade-run/                # positive fixture: a tertiary-only factual claim that passes because it carries its 'downgrade' annotation (W_DOWNGRADE)
│   ├── merge-run/                    # a two-axis merge fixture: sub_reports/{d1,d2}.evidence.json share one URL, which folds to a single source id with references re-pointed
│   ├── cli-run/                      # CLI fixture with the real .work/ layout (runs meld.py verify end-to-end): .work/plan.json, .work/report.src.md, .work/sub_reports/axis.evidence.json
│   └── invalid/                      # negative fixtures: evidence.json files that each fail for exactly one reason + gate-② drafts (orphan, blank) + four content_review --clean drafts (runtime jargon → E_RUNTIME_TERM, standalone discipline section → E_STANDALONE_SECTION, narrated run failure → E_FAILURE_NARRATION, labelled counter-evidence callout → E_ADVERSARY_CALLOUT)
└── .github/                          # GitHub configuration
    └── workflows/                    # CI: validate.yml — core job (zero-dep spec check + script self-test + meld.py CLI self-test + degrade unit tests) and optional job (full dependency install, recorded skips)
```

**Note — contents of `skills/meld-deepresearch/` (level 3; summarized here to
keep the tree at depth 2).** All entries exist:

```text
skills/meld-deepresearch/
├── SKILL.md                          # the entry point: frontmatter (name/description/license/compatibility/metadata) + workflow
├── references/                       # progressive-disclosure detail, loaded on demand by the model
│   ├── protocol.md                   # per-axis loop, cross-skill hand-offs (§2a), source-class routing, mandatory refutation, time-sensitivity, merge, gaps[], soft budgets + 2-round extension, gates, failure/retry table, artifacts
│   ├── evidence-contract.md          # claims / evidence / sources / observations / writing_context / key_findings / gaps schema, plan.json, hard rules (incl. the tertiary 'downgrade' path and the key-finding basis)
│   ├── tier-selection.md             # auto quick-vs-normal decision rules, genre note, worked examples
│   └── report-template.md            # structure by reader's cognitive task, dual output, readability pass, runtime-jargon rule, length tiers, citation mechanism, self-check
├── templates/                        # genre append-templates, chosen at plan time
│   └── genres/                       # panorama.md, comparison.md, entity.md, chronicle.md
└── scripts/                          # Python 3 stdlib only, no dependencies
    ├── meld.py                       # thin CLI over the six gate scripts (prepare/render/review/sources/verify/table); protocol.md §9 lists its commands
    ├── check_evidence.py             # hard gate: validate evidence.json (incl. background, gaps[], source_type, --plan genre/must_have_materials); errors may carry a "hint"
    ├── render_citations.py           # markers -> GFM footnotes (default), anchors (--anchors), legacy plain (--legacy-plain); ONE run writes report.cited.md (cited copy, middleware — .work/report.cited.md in a real run) + report.md (marker-free reading copy whose first line links to the cited copy by a relative path) + citations.json (--citations; else it lands next to --output)
    ├── dedupe_sources.py             # normalize and de-duplicate URLs; emits sources.md (optional source_type column)
    ├── merge_evidence.py             # fold sub_reports/*.evidence.json into one evidence.json, folding duplicate sources and re-pointing references
    ├── content_review.py             # structural self-review of the draft/cited copy (warn-only) plus, with --clean, the delivery gate on report.md that FAILS on runtime-failure jargon (E_RUNTIME_TERM) or a standalone discipline chapter left standing (E_STANDALONE_SECTION); TOC / header-info-block / uncertainty / prose-ratio stay warn-only
    └── read_table.py                 # stdlib-only local .xlsx/.csv/.docx reader -> JSON/CSV/Markdown, with --selftest; the zero-dependency inspection layer that complements meld-da (docx support salvaged from test/tools/docx_to_md.py)
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
