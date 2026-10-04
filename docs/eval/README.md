# Deep Research — Evaluation Standard and Three-Skill Comparison

Status: research + design-level scoring complete; live runs partially executed.
Author: sogeisetsu. Language: English (repo convention).

This document answers three questions:

1. What are the recognized, widely-cited **evaluation standards** for Deep
   Research (DR) agents?
2. How do three DR skills score against a rubric built from those standards, on a
   common set of test questions?
3. Where does `meld-deepresearch` fall short of the others, and what is a
   deliberate design trade-off rather than a defect?

> Live-run caveat: the rubric and the question set are final. Design-level
> scoring (reading each skill's own files) covers all three skills. Live
> execution covers a restricted subset — see [`records/`](records/). Where a
> score depends on a live run that was not performed, the cell says so.

## 1. The evaluation standard

### 1.1 Report-quality benchmarks

| Benchmark | Dimensions | What it measures |
|---|---|---|
| **DeepResearch Bench — RACE** (USTC, ICLR 2026) | Comprehensiveness, Insight/Depth, Instruction-Following, Readability | LLM-judge scores a report against a reference, with task-adaptive criteria and dynamic weights |
| **DeepResearch Bench — FACT** | Citation Accuracy, Effective Citations | Extracts statement→URL pairs, verifies the cited page actually supports the claim |
| **ResearchRubrics** (Scale AI) | Explicit Requirements, Implicit Reasoning, Synthesis, References, Communication Quality, Instruction Following | Binary + ternary rubric compliance, ~26 expert criteria per task |
| **DEER** (ICML 2026) | 7 dimensions / 25 sub-dimensions / 101 rubrics | Expert taxonomy + claim-level verification (cited *and* uncited claims, implicit-claim back-tracking) |
| **DRACO** (Perplexity + HBS) | Factual Accuracy, Breadth & Depth, Presentation, Citation Quality | Weighted task-specific rubrics; negative weights penalize unsupported content |
| **Dr. Bench** | Semantic Quality × (1 − Semantic Drift) × TrustworthyBoost; 7 GRR dimensions | Composite quality + topical focus + retrieval trustworthiness |
| **DeepEval** (LiveResearchBench) | Presentation & Organization, Factual & Logical Consistency, Coverage, Analysis Depth, Citation Association, Citation Accuracy | 6 dimensions incl. claim↔source linkage |

Closed-ended suites — **GAIA**, **BrowseComp**, **HLE** — grade a short answer
against a gold target. They measure retrieval/reasoning accuracy and say nothing
about coverage, structure, citation support, or synthesis, so they are not
report-quality benchmarks.

### 1.2 What the report-quality benchmarks agree on

Six dimensions recur across nearly all of them: coverage/completeness;
depth/insight; factual accuracy/claim support; citation presence and quality;
instruction-following; presentation/readability. A seventh — source credibility
and diversity — appears in most.

### 1.3 What none of them measure

Every benchmark above grades the **final document**. None scores the **process**:

- process discipline (opening the original page rather than trusting a snippet,
  a candidate-URL pool, per-axis loops);
- forced refutation (a run with zero counter-evidence is not penalized);
- budget and honest stop rules (fetch caps, source floors, "budget exhausted →
  stop and list what was not covered");
- process reproducibility (a plan file, per-axis evidence files, a re-runnable
  command log);
- plan conformance and scope ownership (each declared axis actually covered);
- `unknown` labeling (a confident guess where evidence is absent);
- first-hand/observational evidence as a first-class citation type;
- degradation honesty (stating which gates or capabilities were skipped).

This gap is the reason the rubric below adds a **process-discipline** axis on top
of the industry dimensions. It is the one place where `meld-deepresearch` claims
a distinction, so it must be measured explicitly — and, being unmeasured by the
industry, it cannot be borrowed from any public leaderboard.

## 2. The scoring rubric

Seven axes, each scored 0–5. Total 35. A score of `n/a` is allowed when an axis
does not apply or could not be evaluated.

| # | Axis | Source standard | What a 5 looks like |
|---|---|---|---|
| A | Coverage & completeness | RACE / ResearchRubrics / DRACO | Every declared sub-question answered; gaps named |
| B | Depth & analysis | RACE / DEER / DeepEval | Multi-layer synthesis, causal chains, not a link list |
| C | Factual accuracy & claim support | RACE / DRACO / DEER | Each claim traceable to a source that supports it |
| D | Citation quality | FACT / DEER / ReportBench | Citations resolve, are non-duplicate, and are accurate |
| E | Instruction-following | RACE / ResearchRubrics | Format, scope, tier and constraints honored |
| F | Presentation & readability | RACE / DEER / Dr. Bench | Structured, legible, no dead links or orphan markers |
| G | Process discipline (added) | *not scored by any public benchmark* | Original pages opened, counter-evidence searched, budget respected, unknowns labeled, process reproducible, degradations stated |

Scoring notes:

- Axes A–F can be judged from the deliverable alone (industry-style).
- Axis G requires the **process artifacts** (`plan.json`, per-axis
  `sub_reports/`, `evidence.json`, gate output, run log). An agent that only
  returns a Markdown string cannot be scored on G above 2 — this is by design:
  process discipline is only visible when the process leaves a trace.

## 3. The test questions

Six questions, each stressing a different weak point. `Tier` is the tier a
correct run should pick.

| ID | Question | Tier | What it stresses |
|---|---|---|---|
| Q1 | A landscape survey of one industry (e.g. humanoid robotics / embodied AI): market size, players, funding, cost structure, roadmap. | normal | Coverage, multi-axis planning, synthesis |
| Q2 | Verify a specific number that is **deliberately wrong** in the prompt (e.g. "vendor X's 2024 revenue was $Y — confirm"). | quick | Opening originals, not trusting snippets; refutation |
| Q3 | A contested question (e.g. does remote work raise productivity?): present both sides and the strongest counter-evidence. | normal | Forced refutation, contradiction handling |
| Q4 | The latest value of a time-sensitive figure (a ranking, a policy threshold). | quick | Time-sensitivity strategy, citation accuracy |
| Q5 | A sparse evidence question with almost no public sources. | quick | `unknown` labeling, honest stopping |
| Q6 | A deliberately vague request ("research AI for me"). | normal | Clarify / record assumptions, tier selection |

Q1 mirrors the SenseNova worked example, so it also serves as a cross-skill
apples-to-apples comparison.

## 4. How the three skills orchestrate

| | `meld-deepresearch` (ours) | SenseNova `sn-deep-research` | Weizhena `Deep-Research-skills` |
|---|---|---|---|
| License | MIT | MIT (repo) | MIT |
| Install | `npx skills add` / `gh skill install` / manual copy; ~6 hosts | `git clone` + copy to OpenClaw/hermes only | `git clone` + copy to Claude Code/OpenCode/Codex; `pip install pyyaml`; needs `OPENCODE_ENABLE_EXA=1` |
| Orchestration | **Single agent, inline**; delegation optional, never required; no skill chaining | **Multi-agent controller** dispatching ~9 specialist roles, parallel work packages; reuses sibling-skill *scripts* | **Sequential `/research*` command chain**, with **parallel per-item agents** inside `/research-deep` |
| Hard gates | 2 (`check_evidence.py`, `render_citations.py`), 13 error codes | per-role validators + render gate + supplement gate | `validate_json.py` schema check |
| Budget / stop rules | explicit (quick 8/5/3, normal 25/15/3, stop + list gaps) | modes quick/normal/heavy + retry caps; fetch budgets not enumerated | `unknown` at this level of detail |
| Forced refutation | yes — mandatory, `W_NO_REFUTE` warning | explicit refutation mandate `unknown` from the SKILL.md excerpt | `unknown` |
| HTML / chart rendering | none (by design) | `sn-md-to-html-report` + chart generation | none |

### 4.1 SenseNova's two-skill example, explained

`examples/embodied-ai-deep-research/README_CN.md` invokes two skills:
`sn-deep-research` (research → Markdown + 5 charts) and `sn-md-to-html-report`
(Markdown → self-contained HTML). The mechanism is **plain sequential skill
chaining driven by the user**, not a framework:

1. Step 1 prompt ("调研具身智能行业") matches `sn-deep-research`'s description and
   the host selects it; the skill itself internally dispatches specialist roles
   and calls sibling-skill *scripts*.
2. Step 2 heading is literally "第二步：渲染为 HTML" and the body says **continue
   by asking** to convert the Markdown. Only then does the host select
   `sn-md-to-html-report` from its own description triggers.

There is no hook, no auto-chaining, and no orchestrator between the two skills.
`sn-deep-research` does **not** call `sn-md-to-html-report`. The README's
skills table documents the two steps; it does not wire them.

## 5. Scoring

### 5.1 Design-level scores (all three skills)

Scored by reading each skill's own files. See
[`records/design-score.md`](records/design-score.md) for per-axis justification.

| Axis | meld-deepresearch | SenseNova | Weizhena |
|---|---|---|---|
| A Coverage & completeness | 4 | 4 | 3 |
| B Depth & analysis | 4 | 4 | 3 |
| C Factual accuracy & claim support | **5** | 4 | 3 |
| D Citation quality | **5** | 4 | 3 |
| E Instruction-following | 4 | 4 | 4 |
| F Presentation & readability | 3 | **5** | 3 |
| G Process discipline | **5** | 4 | 2 |
| **Total (35)** | **30** | **29** | **21** |

### 5.2 Live-run scores (Q2, same question, all three skills)

The three skills were installed into the same OpenCode host and run on the same
question (verify a deliberately-unverified "$3.7B" OpenAI-2024-revenue claim).
Full artifacts and per-step notes are in [`records/live-runs.md`](records/live-runs.md).

| Axis | meld-deepresearch | SenseNova | Weizhena |
|---|---|---|---|
| Ran on OpenCode, no adaptation | **yes** | **no — refused at its own probe** (needs a separate search-API key; OpenClaw/hermes only) | **no — hardcoded `~/.claude/...` validator path had to be repointed** |
| Opened original pages | yes | n/a | yes |
| Counter-evidence | yes (2 `refute` claims) | n/a | yes (manual item) |
| Gate caught a real defect | **yes — Gate ① failed once, forced a fix** | n/a | no (coverage-only gate, PASS 6/6) |
| Verdict on the claim | confirmed (calendar-2024 revenue) | confirmed (outside pipeline) | confirmed |
| Runs here (0–5 for this question) | **5** | **0** | **3** |

The headline is not the prose — all three reached the same verdict. It is that
**only one of the three actually ran and re-checked its own citations on this
host.** That is precisely the axis (G) the public benchmarks never score.

### 5.3 skill-creator iteration loop

A separate, controlled loop (`opencode-skill-creator`) graded the skill against
its own deliverable and against a no-skill baseline on two of the questions
above, over three iterations — see
[`records/skill-creator-iterations/`](records/skill-creator-iterations/README.md).
It drove three fixes (GFM-footnote citations, a bulleted TL;DR summary, and an
explicit strongest-counter-evidence line) and left the description unchanged
after a trigger-optimization pass.

## 6. Gap analysis

### 6.1 Where `meld-deepresearch` leads

- **Factual support and citation quality (C, D):** the only one of the three with
  a machine-enforced evidence contract — `tertiary` alone cannot carry a factual
  claim, an interpretive claim needs two distinct origins, snippets are never
  evidence.
- **Process discipline (G):** the only one that mechanizes the dimensions no
  public benchmark scores — forced refutation (`W_NO_REFUTE`), budget/stop
  honesty, plan coverage (`--plan`), process reproducibility
  (`observations[]` with a re-runnable command), two fail-closed gates.

### 6.2 Where `meld-deepresearch` trails

1. **Presentation (F, 3 vs SenseNova 5).** We produce Markdown only. SenseNova
   chains a dedicated HTML-report skill to produce visual, chart-bearing
   deliverables. This is a *deliberate* design trade-off (rule 8: no cross-skill
   dependencies; rule 2: zero runtime deps) — but on a deliverable-quality
   benchmark it is a real, scoreable loss, and should be stated as such rather
   than hidden.
2. **Scale of orchestration.** SenseNova's multi-role controller and Weizhena's
   parallel per-item agents distribute retrieval across many axes; our single
   inline agent does the same work serially. Our design claims this is a
   feature (discipline over orchestration), and on axis G it wins — but on
   wall-clock throughput at large scope it is slower.
3. **Coverage breadth (A, 4 vs SenseNova 4).** Roughly even; SenseNova's
   scout/review/supplement roles give it a structural edge on very broad topics
   that our two-tier budget may cap early.

### 6.4 What the live runs changed

The live Q2 comparison (section 5.2) sharpened the picture in a way the
design-level scoring could not:

- **Portability is the real gap, and it runs our way.** On a stock OpenCode host,
  only `meld-deepresearch` ran without modification. SenseNova refused at its own
  Tier-1 probe (its search path needs a separate `SERPER_API_KEY`; it targets
  OpenClaw/hermes, and a mandatory script it references does not even exist in
  its repo). Weizhena ran only after a hardcoded `~/.claude/...` validator path
  was repointed, and its `allowed-tools` are Claude-only names that OpenCode
  ignores.
- **The gate is not ceremonial.** Our Gate ① genuinely failed once (a
  tertiary-only `factual` claim) and forced a fix before delivery. Weizhena's
  gate passed 6/6 but checks only field coverage — it would not have caught that
  class of defect at all.
- **All three reached the same verdict** on the $3.7B claim, so the difference is
  not report prose; it is *whether the skill runs, and whether it re-checks its
  own citations.*

This is the concrete evidence behind the design-level axis-G spread
(5 / 4 / 2): the design score predicted a gap, and the live run confirmed it.

### 6.3 Recommendation

Do **not** add a chart/HTML skill to close the presentation gap — that violates
two design rules for a cosmetic axis. Instead, record the trade-off explicitly
(here and in the README positioning), so the lower F score is a documented
choice. If presentation ever becomes a requirement, the correct move is a
**separate opt-in companion skill**, not a dependency of this one.

## 7. Sources

- DeepResearch Bench (RACE/FACT): https://arxiv.org/abs/2506.11763 ·
  https://deepresearch-bench.github.io
- ResearchRubrics (Scale AI): https://arxiv.org/abs/2511.07685
- DEER (ICML 2026): https://arxiv.org/abs/2512.17776
- DRACO (Perplexity + HBS): https://arxiv.org/html/2602.11685v1
- Dr. Bench: https://arxiv.org/abs/2510.02190
- DeepEval / LiveResearchBench: https://arxiv.org/abs/2510.14240
- GAIA: https://arxiv.org/abs/2311.12983 · BrowseComp:
  https://arxiv.org/abs/2504.12516 · HLE: https://arxiv.org/abs/2503.14499
- SenseNova-Skills: https://github.com/OpenSenseNova/SenseNova-Skills
- Weizhena/Deep-Research-skills:
  https://github.com/Weizhena/Deep-Research-skills
