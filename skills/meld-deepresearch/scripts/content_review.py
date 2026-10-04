#!/usr/bin/env python3
"""Content self-review for a rendered report (warn-only).

Usage:
    python content_review.py --report <report.md> --evidence <evidence.json>
                             [--llm] [--model <provider/model>]

This is a *warn-only* reviewer: it prints warnings and never fails a run. A
render that is legible but imperfect should not be blocked, so the exit code is
0 unless a required file cannot be read (exit 2).

Mechanical checks
-----------------
* Required sections are present and in order (Executive Summary / Findings /
  Contradictions & Counter-evidence / Gaps & Unknowns / Sources; an optional
  Observations section, when present, must come last). Either the English or
  the Chinese heading form satisfies a slot.
* If the report is predominantly Chinese but uses the English form of a
  required heading, that is a language-consistency warning.
* A line that carries a number (a measurement, a percentage, a figure) but no
  citation marker on the same line gets a warning ("obvious uncited number").
  Bare 4-digit years are ignored to keep the heuristic quiet.
* If ``evidence.json`` carries ``gaps[]`` but the report has no
  ``Gaps & Unknowns`` section, that is a warning.

``--llm`` is accepted for interface stability but this script performs no
network call: the host is expected to run the judge. When ``--llm`` is passed,
a single ``W_LLM_NOT_RUN`` warning records that the language/why/background
judgement was not performed here.

stdout is one ASCII-safe JSON object:
    {"ok": true, "warnings": [{"code","message","where"}], "sections": [...]}

Python 3 standard library only; no network access.
"""

import argparse
import json
import re
import sys

HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
CITATION_MARK_RE = re.compile(r"\[\^?[so]?\d+\]|\[O\d+\]|\[\[\d+\]\]|\[\^o\d+\]")
NUMBER_RE = re.compile(r"\d[\d,]*(?:\.\d+)?\s*%?")
YEAR_RE = re.compile(r"^(?:19|20)\d{2}$")

# canonical slot -> (english form, chinese form); order is the required order.
SLOTS = (
    ("executive summary", "摘要"),
    ("findings", "主要发现"),
    ("contradictions & counter-evidence", "矛盾与反证"),
    ("gaps & unknowns", "未知与缺口"),
    ("sources", "来源"),
    ("observations", "观测记录"),
)
REQUIRED_SLOTS = len(SLOTS) - 1  # Observations is optional


def emit(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=True) + "\n")


def fail(message):
    emit({"ok": False, "error": message})
    raise SystemExit(2)


def read_text(path, what):
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            return handle.read()
    except (OSError, UnicodeError) as exc:
        fail("cannot read %s: %s" % (what, exc))


def slot_for(heading):
    lowered = heading.strip().lower()
    for index, (english, chinese) in enumerate(SLOTS):
        if lowered == english or heading.strip() == chinese:
            return index, ("zh" if heading.strip() == chinese else "en")
    return None, None


def check_sections(report, warnings):
    found = []
    for line_number, line in enumerate(report.splitlines(), start=1):
        match = HEADING_RE.match(line)
        if not match:
            continue
        index, language = slot_for(match.group(1))
        if index is not None:
            found.append((index, language, line_number))
    return found


def check_report(report, evidence, warnings):
    is_cjk = bool(CJK_RE.search(report))
    found = check_sections(report, warnings)

    present = {index for index, _, _ in found}
    for index in range(REQUIRED_SLOTS):
        if index not in present:
            warnings.append(_warn(
                "W_REVIEW_MISSING_SECTION",
                "required section '%s' is missing" % SLOTS[index][0],
                "$"))

    order = [index for index, _, _ in found]
    if order != sorted(order):
        warnings.append(_warn(
            "W_REVIEW_SECTION_ORDER",
            "required sections are not in the documented order",
            "$"))

    if is_cjk:
        for index, language, line_number in found:
            if index < REQUIRED_SLOTS and language == "en":
                warnings.append(_warn(
                    "W_REVIEW_HEADING_LANG",
                    "Chinese report uses the English heading '%s'"
                    % SLOTS[index][0],
                    "line %d" % line_number))

    # Obvious uncited numbers.
    in_heading = False
    for line_number, line in enumerate(report.splitlines(), start=1):
        if HEADING_RE.match(line):
            in_heading = True
            continue
        if line.strip().startswith("|"):
            continue  # table rows (the sources table) are handled by the gate
        if CITATION_MARK_RE.search(line):
            continue
        for token in NUMBER_RE.findall(line):
            bare = token.rstrip("%").strip()
            if YEAR_RE.match(bare) and "%" not in token:
                continue
            warnings.append(_warn(
                "W_REVIEW_NUMBER_UNCITED",
                "line carries a number (%s) without a citation marker"
                % token.strip(),
                "line %d" % line_number))
            break

    # gaps[] present in evidence but no Gaps section in the report.
    has_gaps = isinstance(evidence, dict) and isinstance(
        evidence.get("gaps"), list) and len(evidence.get("gaps")) > 0
    slot_index = {index for index, _, _ in found}
    if has_gaps and (SLOTS.index(("gaps & unknowns", "未知与缺口"))
                     not in slot_index):
        warnings.append(_warn(
            "W_REVIEW_GAPS_UNSHOWN",
            "evidence.json carries gaps[] but the report has no "
            "'Gaps & Unknowns' section",
            "$"))


def _warn(code, message, where):
    return {"code": code, "message": message, "where": where}


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        emit({"ok": False, "error": message})
        raise SystemExit(2)


def build_parser():
    parser = _Parser(
        prog="content_review.py",
        description="Warn-only content self-review of a rendered report.",
    )
    parser.add_argument("--report", required=True, help="rendered report.md")
    parser.add_argument("--evidence", required=True, help="evidence.json")
    parser.add_argument(
        "--llm", action="store_true",
        help="request the (host-run) LLM judge; this script records that it "
             "did not run it")
    parser.add_argument("--model", default=None, help="provider/model for --llm")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    report = read_text(args.report, "report file")
    raw = read_text(args.evidence, "evidence file")
    try:
        evidence = json.loads(raw)
    except ValueError as exc:
        fail("invalid JSON in evidence file: %s" % exc)

    warnings = []
    check_report(report, evidence, warnings)
    if args.llm:
        warnings.append(_warn(
            "W_LLM_NOT_RUN",
            "content_review.py performs no network call; run the LLM judge on "
            "the host (requested model: %s)" % (args.model or "unspecified"),
            "$"))

    warnings.sort(key=lambda item: (item["code"], item["where"]))
    emit({"ok": True, "warnings": warnings})
    return 0


if __name__ == "__main__":
    sys.exit(main())
