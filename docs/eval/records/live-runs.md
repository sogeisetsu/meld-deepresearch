# Live runs

Rubric and question set are defined in [`../README.md`](../README.md) §2–§3.

All three skills were installed into the OpenCode host
(`~/.config/opencode/skills/`) and run on **the same question** for comparison:

> **Q2** — "核实一下：OpenAI 在 2024 年的营收是否真的达到了 37 亿美元？请给出一份带引用的核查报告。"
> (Verify whether OpenAI's 2024 revenue really reached 3.7 billion USD; produce a
> citation-backed verification report. The number is deliberately unverified.)

## Status

| Question | meld-deepresearch | SenseNova | Weizhena |
|---|---|---|---|
| Q2 wrong-number check (live) | run (see below) | run — **did not execute** | run — executed after adaptation |
| Q1 / Q3–Q6 | not run | not run | not run |

## Self-validation (executed)

The skill's own gate suite was run end-to-end and passes:

| Check | Result |
|---|---|
| `check_evidence.py examples/sample-run/evidence.json` | `ok: true` |
| `check_evidence.py … --plan …/plan.json` | `ok: true` |
| `render_citations.py` on the sample | `ok: true`, 4 citations, 0 orphans, 0 uncited |
| `dedupe_sources.py` on the sample | `ok: true`, 4 sources, 0 duplicates |
| 5 negative fixtures | each fails for exactly its own reason, exit 1; `evidence.no-refute.json` → `ok: true` + `W_NO_REFUTE`, exit 0 |

## Q2 — SenseNova `sn-deep-research`

**Result: the skill's own Tier-1 probe forced a stop; it never ran.**

- Web search, by the skill's own definition, was **not ready**: `sn-search-*`
  scripts depend on `SERPER_API_KEY`/etc., which were unset. A live call to
  `serper_image_search.py` returned
  `Serper image search is unavailable in the current environment.` **exit 1**.
- The skill's rule — "web search missing → pause, dispatch no role" — fired. No
  scout/plan/research role was dispatched and no pipeline artifacts exist.
- The skill did **not fire in OpenCode at all** (no `sn-*` under
  `~/.config/opencode/skills/`; the run was a manual reading of `SKILL.md` from
  the clone).
- Host incompatibilities beyond search: the `{baseDir}` / `${SKILL_DIR}`
  placeholders are not substituted by OpenCode; the skill's mandatory
  `progress_event.py` / `launch_workbench.py` bootstrap scripts **do not exist in
  the repo at all**; the Anthropic/OpenClaw dispatch mechanism is absent.
- A best-effort verdict was produced **outside the skill's pipeline** (clearly
  labelled): the $3.7B figure is **true** as 2024 calendar-year revenue —
  NYT/CNBC 2024 document reports, later confirmed by audited FY2024 statements
  reported in 2026.
- Artifacts: `eval-run-sensenova/probe-tier1.md`,
  `eval-run-sensenova/verdict-outside-skill.md`.

**Score note:** on this host, SenseNova scores **0 on axis G** for this question —
its own rules required it to refuse to run, and it did. Portability is the gap.

## Q2 — Weizhena `research`

**Result: the chain ran end to end, but only after non-trivial adaptation to
OpenCode.**

- **Hard break:** `research-deep` hardcodes
  `python ~/.claude/skills/research/validate_json.py …`. PowerShell does not
  expand `~` for native commands, and the `.claude` path does not exist → the
  literal command **failed, exit 2**. It worked only after being repointed at the
  OpenCode install path.
- **Claude-only tools:** all five skills declare `allowed-tools:
  Task, AskUserQuestion, WebSearch` — none exist on this host, so
  `allowed-tools` is unenforceable and every confirmation step had to be replaced
  with a recorded default. The mandated background `web-search-agent` (a `Task`)
  could not be launched as an agent.
- **Gate:** `validate_json.py` ran — PASS 6/6 (100 % field coverage), and a
  negative control correctly FAILED. But the gate is **coverage-only**: it does
  **not** verify citation truthfulness or evidence access.
- **Content verdict:** $3.7B is **true** (2024 calendar-year revenue; run-rate
  counter-figures like ~$5.5B were correctly classified as non-contradicting).
  Original pages opened (CNBC, Where's Your Ed At, Ars Technica); blocked access
  (NYT 403, Reuters 401, FT/Bloomberg paywalls) was recorded as `[uncertain]` and
  never treated as read.
- Artifacts: `eval-run-weizhena/ADAPTATION_LOG.md`, `DECISIONS.md`,
  `openai-2024-revenue-verification/` (outline, fields, 6 result JSONs,
  `report.md`).

## Q2 — `meld-deepresearch` (ours)

**Result: ran end to end on OpenCode with no adaptation; both gates fired.**

- **Tier:** `normal` (explicit report request + ≥2 independent axes + expected
  conflict).
- **Pipeline:** probe → anchors → assumptions recorded → `plan.json` (3 axes:
  primary-attributed / press corroboration / counter-evidence; `kq1`–`kq4`) →
  per-axis research loop → merge → Gate ① → one-pass Chinese report → Gate ② →
  `sources.md`. All four deliverables + `plan.json` + per-axis
  `sub_reports/dN.evidence.json` produced.
- **Evidence:** 23 fetch attempts (budget 25); every `sources[]` entry is a page
  that was opened — no snippet-only evidence. 6 originals were bot-walled
  (NYT/Reuters/Bloomberg/CNN/Axios/openai.com, HTTP 403) and recorded as an
  availability caveat, not cited as read. 11 claims, 15 distinct sources, 1
  observation, `writing_context` caveats, 3 key findings.
- **Refutation:** 2 `refute`-polarity claims (non-zero) — a revenue-share floor
  and an older $4B projection. Metric confusion (ARR vs calendar revenue) kept
  explicitly unresolved in a Contradictions section.
- **Gate ① FAILED on the first attempt and was fixed:**
  ```
  {"ok": false, "errors": [{"code": "E_FACTUAL_SOURCE",
   "message": "factual claim needs at least one evidence item backed by a primary
   or secondary source, or by an observation", "where": "claims[11]"}], "warnings": []}
  ```
  Fix: dropped the tertiary-only claim + its source. Second attempt:
  `{"ok": true, "errors": [], "warnings": []}`. **This is the decisive
  difference from the other two skills — the gate genuinely stopped a deliverable
  and forced a correction.**
- **Gate ②:** `{"ok": true, "citation_count": 15, "observation_count": 1,
  "orphans": [], "uncited": []}`; `dedupe_sources.py` →
  `{"ok": true, "sources": 15, "duplicates_merged": 0}`.
- **Verdict:** $3.7B corroborated as calendar-2024 revenue — a Sep-2024
  projection, a Mar-2025 reported actual, and a Jun-2026 leaked-audit figure,
  all consistent.
- **Honest soft spots named by the run itself:** a bot-walled primary voice
  (openai.com) only reachable via secondary quotes; the distinct-origin rule is
  URL-level while many outlets relay one release; two ProPublica URLs
  (org page vs API) counted as two sources (borderline); the single Gate-① fix
  chance was spent on a claim that arguably need not have been dropped.
- Artifacts: `eval-run-meld/meld-deepresearch-reports/2026-10-04-openai-2024-revenue-7c3f/`.

## Cross-run read

| | meld-deepresearch | SenseNova | Weizhena |
|---|---|---|---|
| Ran on OpenCode without adaptation? | yes | **no — refused** | **no — repointed a hardcoded path** |
| Opened original pages? | yes | n/a | yes |
| Counter-evidence handled? | yes (refute mandate) | n/a | yes (manual item) |
| Gate verifies citation truth, not just coverage? | yes | n/a | **no — coverage only** |
| Verdict on the $3.7B claim | confirmed | confirmed (outside pipeline) | confirmed |

This is exactly the axis the public benchmarks do not score: **whether the skill
actually runs, and whether it re-checks its own citations.** On those two,
`meld-deepresearch` and SenseNova diverge completely on this host — not on report
prose.
