# Skill Benchmark: meld-deepresearch — iteration 1

**Model**: opencode-go/deepseek-v4.1-flash
**Date**: 2026-10-04T01:54:33.717Z
**Evals**: 0, 1 (1 run each per configuration)

## Summary

| Metric | with_skill | without_skill | Delta |
|---|---|---|---|
| Pass Rate | 1.00 | 0.43 | +0.57 |
| Time | 352.8s | 126.7s | +226.1s |
| Tokens | 245990 | 93565 | +152425 |

## Per-eval

### openai-revenue-quick

| Configuration | Pass rate | Passed | Time | Tokens |
|---|---|---|---|---|
| with_skill | 1.00 | 7/7 | 231.7s | 134575 |
| without_skill | 0.29 | 2/7 | 70.6s | 51478 |

### remote-work-normal

| Configuration | Pass rate | Passed | Time | Tokens |
|---|---|---|---|---|
| with_skill | 1.00 | 7/7 | 473.8s | 357405 |
| without_skill | 0.57 | 4/7 | 182.8s | 135652 |

## Notes

- with_skill runs produce the full artifact set (report.md, sources.md, evidence.json, citations.json) and pass the skill's own gates; without_skill runs produce a report only.
- without_skill cites sources but never opens originals as machine-checkable evidence; some baseline runs answer largely from search snippets.
- The discipline (open originals, structured evidence, two gates) is the cost: with_skill is slower and more token-hungry.
