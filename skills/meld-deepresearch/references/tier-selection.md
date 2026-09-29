# Tier Selection

Two tiers, chosen automatically from the request. Default is **`quick`**.
Details of *how* to research after the tier is chosen: `protocol.md`.

## 1. The two tiers

| Tier | Shape of the run |
|---|---|
| `quick` | Single research line, in-memory key questions `kq1..kqn`, no plan file, small budget. |
| `normal` | Named, independently searchable dimensions written to `plan.json`, cross-dimension synthesis, larger budget. |

## 2. Decision table

| Tier | Conditions (any one ⇒ that tier) |
|---|---|
| `quick` | A single self-contained question · one research line · at most 3 sub-questions · no independent search axes · the user wants a brief answer or a single-point check |
| `normal` | ≥ 2 independently searchable axes · cross-dimension synthesis required · entity comparison · the user explicitly asks for a report or white paper · conflicting evidence is expected |

**Precedence rule: `normal` beats `quick`.** If ANY `normal` condition
matches, upgrade to `normal` — even if the question also looks quick. The user
can always override the tier explicitly (explicit user choice > rule), and the
chosen tier plus the reason is recorded in the run output.

## 3. Scoring procedure

Apply in order; stop at the first decisive answer:

1. **User override?** The user named a tier or a format that implies one
   (e.g. "full report", "white paper", "one-line answer") → use it.
2. **Count independent axes.** Could each line of inquiry be researched with
   its own search scope and its own source pool, without depending on another
   line's results? If the count is ≥ 2 → `normal`.
3. **Check for comparison or synthesis.** Two or more entities compared, or
   findings must be combined across dimensions (technical + market +
   regulatory, etc.) → `normal`.
4. **Check for expected conflict.** Competing claims, contested numbers, or a
   known dispute → `normal` (refutation and contradiction handling need the
   bigger budget).
5. **Check sub-question count.** Decompose into sub-questions. ≤ 3, all on one
   research line, all answerable from a shared source pool → `quick`;
   otherwise → `normal`.
6. **Tie-break: still unsure → `quick`.** A quick run that hits its depth
   threshold early is cheap; the upgrade rule in §2 rescues any quick run that
   turns out to need more axes mid-flight.

## 4. Worked examples

| # | Request | Tier | Reason |
|---|---|---|---|
| 1 | "What is the current version of Python 3.13 and when was it released?" | `quick` | Single self-contained fact, one line, one authoritative source. |
| 2 | "Compare Postgres and MySQL for a write-heavy workload and recommend one." | `normal` | Entity comparison + synthesis (performance, ecosystem, cost are separate axes). |
| 3 | "Give me a one-paragraph status of the project in `docs/PLAN.md`." | `quick` | Single source, no search axes; user wants a brief answer. |
| 4 | "Write a white paper on EU AI Act compliance options for a medical-device startup." | `normal` | Explicitly requests a white paper; regulatory + clinical + commercial axes. |
| 5 | **Borderline:** "Is Rust suitable for our CLI tool? Consider startup time and binary size, and check whether the recent release changed either." | `normal` | Looks like a yes/no check, but it is ≥ 2 independently searchable axes (startup time, binary size, release changelog) with expected conflict across benchmarks → §2 rule upgrades it; the tie breaks toward `normal` because missing a dimension is costlier than overspending. |
| 6 | **Borderline:** "Did the vendor's outage on 2026-03-05 affect EU customers?" | `quick` | Narrow, single-line, single time window, one incident → stays `quick`; it would upgrade only if evidence turned out to be contradictory or the vendor's status page plus third-party reports had to be reconciled across axes. |

## 5. What the tier changes downstream

| Aspect | `quick` | `normal` |
|---|---|---|
| Fetch budget | ≤ 8 | ≤ 25 |
| Distinct sources floor | ≥ 5 | ≥ 15 |
| Rounds per axis | ≤ 3 | ≤ 3 |
| Plan artifact | none (key questions `kq1..kqn` stay in memory) | `plan.json` with named dimensions, `scope_ownership`, source classes, `depth`, time-sensitivity |
| Dimension naming | none | every axis `dN` named up front; evidence per axis in `sub_reports/dN.evidence.json` |
| Expected structure | brief report, fewer sections | full report: per-dimension findings, contradictions, gaps |
| Multi-perspective seeding | one line + one refutation angle | several perspectives seeded up front (see `protocol.md` §6) |

Budgets and stop conditions are defined in `protocol.md` §8 and apply
unchanged once the tier is fixed.

## 6. Mid-run upgrade

A `quick` run that discovers a second independent axis mid-research must not
pretend it is still quick:

- Stop the current line, re-apply §3, and if a `normal` condition now matches,
  switch to `normal`: create `plan.json`, name the dimensions found so far,
  and keep the evidence already collected (do not discard fetches already
  spent — they count against the `normal` budget of 25).
- Downgrade never happens automatically; only the user can downgrade.
- Record in the run output: `tier`, whether it was overridden by the user,
  whether/when it was upgraded, and the reason.
