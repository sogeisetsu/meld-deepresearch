#!/usr/bin/env python3
"""Unit test for content_review.py --fix (Lever B, phase 2).

stdlib only, no network, no third-party package. Every invocation of the
script is a subprocess — exactly the way a host or CI runs it — and all
fixtures are built inline under ``.work/tmp/fix-tests/`` (gitignored);
``examples/`` is never touched.

Three cases, exactly as specified:

1. label stripping — the closed ADVERSARY_LABEL_TOKENS disappear, the
   following sentences survive intact, both copies (``report.md`` and
   ``.work/report.cited.md``) are edited consistently with their ``[^n]``
   markers untouched, and a plain ``--clean`` re-run carries the
   ``E_ADVERSARY_CALLOUT`` code in neither bucket (neither failure nor
   warning); before the fix that same code is reported as a WARNING
   (exit 0) since its downgrade;
2. generic heading — a heading seeded in the closed GENERIC_HEADING_FIX map
   is demoted per that map and every other byte of the file is untouched;
3. unsafe case — the standalone-discipline-chapter shape is reported as a
   WARNING ``E_STANDALONE_SECTION`` (exit 0) under ``--fix --clean``, the
   fix pass reports no fixes, and its bytes are unchanged in both copies
   (the never-auto-merge guard).

Run:  python skills/meld-deepresearch/tests/test_content_review_fix.py
Exit: 0 pass / 1 fail (an ASCII-safe JSON summary is printed either way).
"""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]  # skills/meld-deepresearch
REPO = SKILL_DIR.parents[1]
SCRIPT = SKILL_DIR / "scripts" / "content_review.py"
SCRATCH = REPO / ".work" / "tmp" / "fix-tests"

# The closed label-token list, stated independently of the script under test.
EXPECTED_TOKENS = (
    "**最强反证：**",
    "**最强反证:**",
    "**最强反方：**",
    "**最强反方:**",
    "**strongest counter-evidence:**",
    "**strongest counter-evidence：**",
)
# The closed heading map, stated independently of the script under test.
EXPECTED_HEADING_FIX = {
    "主要发现": "### 主要发现",
    "Findings": "### Findings",
    "分析": "### 分析",
    "结果": "### 结果",
    "Results": "### Results",
    "Analysis": "### Analysis",
}

results = []


def check(name, ok, detail=""):
    results.append({"name": name, "ok": bool(ok), "detail": detail})
    return ok


def load_module():
    """Import content_review.py to assert its module-level closed data."""
    spec = importlib.util.spec_from_file_location(
        "content_review_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def review(report, evidence, *flags):
    """Run content_review.py in a subprocess; return (exit code, JSON)."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--report", str(report),
         "--evidence", str(evidence), *flags],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        payload = json.loads(proc.stdout)
    except ValueError:
        payload = {"ok": None, "raw": proc.stdout}
    return proc.returncode, payload


def codes(payload, key):
    return sorted({item["code"] for item in payload.get(key, [])})


def write_case(name, reading, cited=None):
    """Create a scratch case dir with evidence.json and the report pair."""
    case_dir = SCRATCH / name
    shutil.rmtree(case_dir, ignore_errors=True)
    (case_dir / ".work").mkdir(parents=True)
    (case_dir / "evidence.json").write_text(
        json.dumps({"claims": [], "sources": [], "observations": [],
                    "gaps": [], "key_findings": [], "writing_context": []}),
        encoding="utf-8")
    (case_dir / "report.md").write_text(reading, encoding="utf-8")
    if cited is not None:
        (case_dir / ".work" / "report.cited.md").write_text(
            cited, encoding="utf-8")
    return case_dir


# --------------------------------------------------------------------------
# Case 1 — label stripping
# --------------------------------------------------------------------------
READING = """# Label strip fixture

**Subject:** fixture · **Data cut-off:** 2026-01-01 · **Basis:** one source

## Contents

- [Definitions and scope](#definitions-and-scope)
- [Executive Summary](#executive-summary)
- [Industry growth](#industry-growth)

## Definitions and scope

A figure is any percentage stated in this fixture; the window is calendar 2025.

## Executive Summary

- The industry grew 12% last year.
- The quarterly breakdown stays `unknown`.

## Industry growth

The industry grew 12% last year. **strongest counter-evidence:** however, one source disputes the figure.

**最强反证：** a later release revises the figure downward.

**最强反方：** one analyst disputes the reading entirely.

- **最强反方:** a second analyst disputes the sample size.

**Strongest counter-evidence：** one chart contradicts the trend.

The revision note is quiet. **最强反证:** one editor flagged the change.

## Sources
"""
# The cited middleware: same body plus footnote markers (never touched by --fix).
CITED = READING.replace(
    "- The industry grew 12% last year.",
    "- The industry grew 12% last year.[^1]", 1) + \
    "[^1]: Example Corp, market note, 2025.\n"

# Independent oracle: every exact label occurrence (token + one space) is
# removed; nothing else changes.
LABELS_IN_FIXTURE = (
    "**strongest counter-evidence:** ",
    "**最强反证：** ",
    "**最强反方：** ",
    "**最强反方:** ",
    "**Strongest counter-evidence：** ",
    "**最强反证:** ",
)


def stripped(text):
    for label in LABELS_IN_FIXTURE:
        text = text.replace(label, "")
    return text


def case_label_stripping(module):
    case_dir = write_case("case1", READING, CITED)
    report = case_dir / "report.md"
    cited = case_dir / ".work" / "report.cited.md"
    evidence = case_dir / "evidence.json"
    before_reading = report.read_bytes()
    before_cited = cited.read_bytes()

    # Closed list assertions (module-level data the test can assert on).
    check("case1: closed label-token list",
          module.ADVERSARY_LABEL_TOKENS == EXPECTED_TOKENS,
          "got %r" % (module.ADVERSARY_LABEL_TOKENS,))

    # Baseline: without --fix the callout is reported as a WARNING (the
    # code was downgraded from a hard fail) and no fixes field exists.
    rc, payload = review(report, evidence, "--clean")
    check("case1: pre-fix --clean warns E_ADVERSARY_CALLOUT",
          rc == 0 and "E_ADVERSARY_CALLOUT" in codes(payload, "warnings")
          and "E_ADVERSARY_CALLOUT" not in codes(payload, "failures"),
          "rc=%s warnings=%s failures=%s" % (
              rc, codes(payload, "warnings"), codes(payload, "failures")))
    check("case1: default output has no fixes field",
          "fixes" not in payload, "keys=%s" % sorted(payload))

    # The fix pass: both copies edited, then the gate passes.
    rc, payload = review(report, evidence, "--clean", "--fix")
    fixes = payload.get("fixes", [])
    per_file = {}
    for record in fixes:
        per_file[record.get("file", "")] = per_file.get(
            record.get("file", ""), 0) + 1
    check("case1: --fix --clean passes", rc == 0 and payload.get("ok") is True,
          "rc=%s ok=%s" % (rc, payload.get("ok")))
    check("case1: fixes field lists only strip-label edits on both copies",
          all(r.get("op") == "strip-label" for r in fixes)
          and len(per_file) == 2
          and sorted(per_file.values()) == [6, 6]
          and any(f.endswith("report.md") for f in per_file)
          and any(f.endswith("report.cited.md") for f in per_file),
          "fixes=%r" % (fixes,))

    after_reading = report.read_text(encoding="utf-8")
    after_cited = cited.read_text(encoding="utf-8")
    check("case1: reading copy equals the byte-exact oracle transform",
          after_reading == stripped(READING),
          "differs from expected transform")
    check("case1: cited copy transformed identically, markers untouched",
          after_cited == stripped(CITED)
          and after_cited.count("[^1]") == CITED.count("[^1]"),
          "cited copy diverged or markers changed")
    lowered = after_reading.casefold()
    check("case1: no closed token survives anywhere",
          all(token.casefold() not in lowered for token in EXPECTED_TOKENS),
          "token still present")
    check("case1: following sentences survive intact and inline",
          "year. however, one source disputes the figure." in after_reading
          and "\na later release revises the figure downward." in after_reading
          and "\none analyst disputes the reading entirely." in after_reading
          and "- a second analyst disputes the sample size." in after_reading
          and "\none chart contradicts the trend." in after_reading
          and "The revision note is quiet. one editor flagged the change."
          in after_reading,
          "a following sentence was lost or split")

    # A plain --clean re-run on the fixed reading copy is clean of the code
    # entirely: neither bucket carries it.
    rc, payload = review(report, evidence, "--clean")
    check("case1: plain --clean after fix no longer reports "
          "E_ADVERSARY_CALLOUT",
          rc == 0 and "E_ADVERSARY_CALLOUT" not in codes(payload, "failures")
          and "E_ADVERSARY_CALLOUT" not in codes(payload, "warnings")
          and "fixes" not in payload,
          "rc=%s failures=%s warnings=%s" % (
              rc, codes(payload, "failures"), codes(payload, "warnings")))

    # Counterpart edited but never invented: reading copy changed, cited too.
    check("case1: both files really changed on disk",
          report.read_bytes() != before_reading
          and cited.read_bytes() != before_cited, "a copy was not rewritten")


# --------------------------------------------------------------------------
# Case 2 — generic heading mapped
# --------------------------------------------------------------------------
HEADING_READING = """# Heading fixture

**Subject:** fixture · **Data cut-off:** 2026-01-01 · **Basis:** one source

## Contents

- [Definitions and scope](#definitions-and-scope)
- [Findings](#findings)

## Definitions and scope

A figure is any percentage stated in this fixture; the window is calendar 2025.

## Findings

The industry grew 12% last year; the trend stays `unknown` beyond 2025. However, one source disputes the reading.

## Industry growth

Steady growth continues; the caveat is a small sample.

## Sources
"""


def case_generic_heading(module):
    case_dir = write_case("case2", HEADING_READING, HEADING_READING)
    report = case_dir / "report.md"
    cited = case_dir / ".work" / "report.cited.md"
    evidence = case_dir / "evidence.json"

    check("case2: closed heading map contents",
          module.GENERIC_HEADING_FIX == EXPECTED_HEADING_FIX,
          "got %r" % (module.GENERIC_HEADING_FIX,))
    check("case2: every seeded key is a heading the checker flags generic",
          all(module.GENERIC_HEADING_RE.search("## " + key)
              for key in module.GENERIC_HEADING_FIX),
          "a seeded key is outside GENERIC_HEADING_RE")

    # Baseline: the generic container only warns.
    rc, payload = review(report, evidence, "--clean")
    check("case2: pre-fix --clean warns W_GENERIC_HEADING",
          rc == 0 and "W_GENERIC_HEADING" in codes(payload, "warnings"),
          "rc=%s warnings=%s" % (rc, codes(payload, "warnings")))

    rc, payload = review(report, evidence, "--clean", "--fix")
    fixes = payload.get("fixes", [])
    check("case2: --fix --clean passes and reports one demote per copy",
          rc == 0 and len(fixes) == 2
          and all(r.get("op") == "demote-heading" and r.get("detail") == "## Findings"
                  for r in fixes),
          "rc=%s fixes=%r" % (rc, fixes))

    expected = HEADING_READING.replace("## Findings", "### Findings")
    after_reading = report.read_text(encoding="utf-8")
    after_cited = cited.read_text(encoding="utf-8")
    check("case2: heading demoted per the closed map, all other bytes intact",
          after_reading == expected
          and after_cited == expected
          and "### Findings" in after_reading
          and "## Industry growth" in after_reading,
          "file diverged from expected transform")

    rc, payload = review(report, evidence, "--clean")
    check("case2: plain --clean after fix no longer warns W_GENERIC_HEADING",
          rc == 0 and "W_GENERIC_HEADING" not in codes(payload, "warnings"),
          "rc=%s warnings=%s" % (rc, codes(payload, "warnings")))


# --------------------------------------------------------------------------
# Case 3 — the unsafe shape is never auto-fixed
# --------------------------------------------------------------------------
UNSAFE_READING = """# Unsafe fixture

**Subject:** fixture · **Data cut-off:** 2026-01-01 · **Basis:** one source

## Contents

- [Executive Summary](#executive-summary)
- [Key findings](#key-findings)

## Executive Summary

- The industry grew 12% last year.

## Key findings

The figure above rests on one opened source.

## Contradictions & Counter-evidence

A second source disputes the figure.

## Gaps & Unknowns

- The quarterly breakdown is `unknown`.

## Sources
"""


def case_unsafe_unchanged(_module):
    case_dir = write_case("case3", UNSAFE_READING, UNSAFE_READING)
    report = case_dir / "report.md"
    cited = case_dir / ".work" / "report.cited.md"
    evidence = case_dir / "evidence.json"
    before_reading = report.read_bytes()
    before_cited = cited.read_bytes()

    rc, payload = review(report, evidence, "--fix", "--clean")
    check("case3: --fix --clean warns E_STANDALONE_SECTION (exit 0)",
          rc == 0 and "E_STANDALONE_SECTION" in codes(payload, "warnings")
          and "E_STANDALONE_SECTION" not in codes(payload, "failures")
          and payload.get("ok") is True,
          "rc=%s warnings=%s failures=%s" % (
              rc, codes(payload, "warnings"), codes(payload, "failures")))
    check("case3: the never-auto-fix pass reports no fixes",
          payload.get("fixes") == [], "fixes=%r" % (payload.get("fixes"),))
    check("case3: file bytes unchanged in both copies",
          report.read_bytes() == before_reading
          and cited.read_bytes() == before_cited,
          "an unsafe file was rewritten")


def main():
    module = load_module()
    case_label_stripping(module)
    case_generic_heading(module)
    case_unsafe_unchanged(module)

    failures = [r for r in results if not r["ok"]]
    for r in results:
        print("%s %s%s" % (
            "PASS" if r["ok"] else "FAIL", r["name"],
            (" — " + r["detail"]) if (not r["ok"] and r["detail"]) else ""))
    print(json.dumps({"ok": not failures,
                      "total": len(results),
                      "failed": [r["name"] for r in failures]}))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
