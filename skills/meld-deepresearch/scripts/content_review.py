#!/usr/bin/env python3
"""Content self-review for a rendered report.

Usage:
    python content_review.py --report <report.md> --evidence <evidence.json>
                             [--clean] [--llm] [--model <provider/model>]

Two review modes:

``--clean``
    The file is the **final reading copy** (``report.md``). This is the
    delivery-stage review — the acceptance check for the mandatory
    *pre-delivery readability pass* described in ``report-template.md``:
      * the runtime-failure blacklist below is enforced (exit 1 on a hit);
      * a standalone discipline chapter — ``## Contradictions &
        Counter-evidence`` / ``## Gaps & Unknowns`` (or their Chinese forms,
        at H2 or H3) — is an error (``E_STANDALONE_SECTION``): at delivery
        those sections are woven into the narrative, not left standing;
      * a narrated run failure (login wall, unopenable page) is an error
        (``E_FAILURE_NARRATION``) and internal apparatus in the body is an
        error (``E_APPARATUS_LEAK``);
      * the opening must have survived the pass: header info block
        (``W_NO_INFO_BLOCK``), a vertical table of contents (``W_NO_TOC`` /
        ``W_THIN_TOC``), a definitions-and-scope section
        (``W_NO_DEFINITIONS``), content-bearing headings
        (``W_GENERIC_HEADING``), an uncertainty marker somewhere
        (``W_NO_UNCERTAINTY``);
      * warn-only: prose ratio (``W_PROSE_RATIO``);
      * the *structural* checks (required sections, their order, heading
        language, uncited numbers) do **not** run here — they belong to the
        draft/cited stage and would contradict the weave.

no flag
    The file is the **draft or cited copy**: full structural review (required
    sections, order, heading language, uncited numbers, gaps section), no
    blacklist — technical detail may stay there.

Runtime-failure blacklist (``--clean`` only)
--------------------------------------------
High-precision run-failure tokens never belong in a reader-facing report.
One hit fails the review (exit 1, code ``E_RUNTIME_TERM``)::

    access-limited, webfetch, captured 20, word_count, extracted_main,
    bot-protection, 抓取失败, 读取失败, 运行故障

Ambiguous tokens (``403``, ``401``, ``429``, ``503``, ``timeout``,
``blocked``, ``forbidden``, ``rate limit``, ``captcha``, ``bot-wall``,
``paywall`` ...) only warn (``W_RUNTIME_TERM``): they are legitimate in a
network/tech subject. Every kept hit is an exemption and must be recorded in
the run log with its reason.

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
  Bare 4-digit years are ignored to keep the heuristic quiet. Skipped in
  ``--clean`` mode, where no markers exist by design.
* If ``evidence.json`` carries ``gaps[]`` but the report has no
  ``Gaps & Unknowns`` section, that is a warning.
* Prose ratio (always computed): non-table, non-code, non-pure-list characters
  over the body characters (``Sources`` / ``Observations`` / footnote
  definitions excluded). Below 0.80 it warns ``W_PROSE_RATIO`` — a warn-only
  quality signal that never blocks delivery.

``--llm`` is accepted for interface stability but this script performs no
network call: the host is expected to run the judge. When ``--llm`` is passed,
a single ``W_LLM_NOT_RUN`` warning records that the language/why/background
judgement was not performed here.

stdout is one ASCII-safe JSON object:
    {"ok": bool, "warnings": [{"code","message","where"}], "sections": [...]}

Exit codes: 0 pass (warnings allowed), 1 blacklist hit in ``--clean`` mode,
2 bad input (unreadable file / invalid JSON / wrong usage).

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
# The report template requires the single strongest refutation to be called out
# on its own line; either language form satisfies it.
STRONGEST_RE = re.compile(r"最强反方|最强反证|strongest counter", re.IGNORECASE)
SUMMARY_SENTENCE_LIMIT = 140

# High-precision run-failure jargon: never allowed in the reading copy.
# ASCII entries are matched case-insensitively.
RUNTIME_BLACKLIST = (
    "access-limited",
    "webfetch",
    "captured 20",
    "word_count",
    "extracted_main",
    "bot-protection",
    "抓取失败",
    "读取失败",
    "运行故障",
)
# Context-dependent terms: legitimate in a network/tech subject, warn only.
# Every kept hit is an exemption and has to be recorded in the run log.
RUNTIME_AMBIGUOUS = (
    "403",
    "401",
    "429",
    "503",
    "timeout",
    "timed out",
    "blocked",
    "forbidden",
    "rate limit",
    "captcha",
    "bot-wall",
    "paywall",
)
PROSE_RATIO_MIN = 0.80
LIST_LINE_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
FENCE_RE = re.compile(r"^\s*(?:```|~~~)")
TAIL_HEADING_RE = re.compile(
    r"^##\s+(?:Sources|Observations|来源|观测记录)\s*$", re.MULTILINE)


# Sentence enders for the Executive-Summary checks: full/half-width CJK
# terminators plus English ``.!?`` when followed by whitespace and a
# sentence-starting character (or end of text). The English half is
# deliberately conservative so decimals (``3.7B``), versions (``v2.0``) and
# dotted abbreviations (``example.org``, ``U.S. officials``) are not read as
# sentence breaks.
_SENTENCE_END = re.compile(r"[。！？!?]+|(?<=[.!?])(?=\s+[A-Z0-9\"'(\[]|\s*$)")


def _summary_sentences(text):
    """Split an Executive Summary into sentences (CJK- and English-aware)."""
    return [s for s in (p.strip() for p in _SENTENCE_END.split(text)) if s]
FOOTNOTE_DEF_RE = re.compile(r"^\[\^\d+\]:", re.MULTILINE)

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


def section_body(report, slot_index):
    """Return the body text under the heading for ``slot_index`` (may be "")."""
    lines = []
    capturing = False
    for line in report.splitlines():
        match = HEADING_RE.match(line)
        if match:
            index, _ = slot_for(match.group(1))
            if index == slot_index:
                capturing = True
                continue
            if capturing:
                break
            continue
        if capturing:
            lines.append(line)
    return "\n".join(lines)


# Standalone discipline chapters are a draft-stage device: at delivery they are
# woven into the narrative, so seeing one in the reading copy is an error.
# H3 stand-ins count too — a chapter that exists only to say "here is what we
# could not do" is the defect, regardless of its level. Observations belong to
# the cited copy and the evidence file, never to the reader.
STANDALONE_DISCIPLINE_RE = re.compile(
    r"^#{2,3}\s+(?:"
    r"Contradictions\s*(?:&|and)\s*Counter-evidence|"
    r"Gaps\s*(?:&|and)\s*Unknowns|"
    r"Counter-evidence\s+and\s+limits|"
    r"What\s+remains\s+unknown|"
    r"Observations|"
    r"矛盾与反证|未知与缺口|观测记录|反证与边界|尚未证实的部分"
    r")\s*$",
    re.MULTILINE | re.IGNORECASE)
# The reader must never be told that the run failed to open something: state
# the epistemic status ("no verifiable public source") instead.
FAILURE_NARRATION_RE = re.compile(
    r"登录墙|页面要求登录|需要登录|未能打开|打不开|因超时|"
    r"login wall|could not (?:be )?opened|failed to fetch|could not access",
    re.IGNORECASE)
DEFINITIONS_HEADING_RE = re.compile(
    r"^#{2,3}\s+(?:定义与范畴|背景与范围|术语|"
    r"Background(?:\s+and\s+scope)?|"
    r"Scope(?:\s+and\s+(?:definitions|background))?|"
    r"Definitions?(?:\s+and\s+scope)?"
    r")\s*$",
    re.MULTILINE | re.IGNORECASE)
GENERIC_HEADING_RE = re.compile(
    r"^##\s+(?:主要发现|Findings|分析|结果|Results|Analysis)\s*$",
    re.MULTILINE | re.IGNORECASE)
TOC_HEADING_RE = re.compile(
    r"^#{2,3}\s+(?:目录|Contents|Table of Contents)\s*$", re.MULTILINE)
TOC_LINK_RE = re.compile(r"\[[^\]]+\]\(#[^)]+\)")
# Our own machinery must never surface in a client-facing report: the skill id,
# the draft file names, the run log, the protocol. The single pointer line on
# line 1 is the one sanctioned exception.
APPARATUS_RE = re.compile(
    r"meld-deepresearch|SKILL\.md|report\.src\.md|run-log|run_meta|run-meta|"
    r"references/protocol|[Ww]eb\s*fetch\s*tool", re.IGNORECASE)
UNCERTAINTY_RE = re.compile(
    r"unknown|未知|无法证实|存疑|存在争议|待核实|证据不足|口径不明|insufficient evidence",
    re.IGNORECASE)
# A header info block sits between the title and the first "## " heading and
# carries "label: value" pairs with at least one date.
INFO_LINE_RE = re.compile(r"[:：].*\d{4}|\d{4}.*[:：]")


def check_final_layout(report, evidence, warnings, failures):
    """Delivery-stage layout rules for the reading copy (``report.md``)."""
    for match in STANDALONE_DISCIPLINE_RE.finditer(report):
        line_number = report[: match.start()].count("\n") + 1
        failures.append(_warn(
            "E_STANDALONE_SECTION",
            "standalone discipline chapter %r must not exist in the reading "
            "copy; weave it into the section whose claim it belongs to, "
            "keeping the strongest-counter-evidence callout and every "
            "unknown label attached to that claim" % match.group(0).strip("# \r\n"),
            "line %d" % line_number))

    for match in FAILURE_NARRATION_RE.finditer(report):
        line_number = report[: match.start()].count("\n") + 1
        failures.append(_warn(
            "E_FAILURE_NARRATION",
            "the reader is told about a run failure (%r); record it in "
            "observations[]/gaps[] and state the epistemic status in the "
            "report instead ('no verifiable public source yet')" % match.group(0),
            "line %d" % line_number))

    if not TOC_HEADING_RE.search(report) and not TOC_LINK_RE.search(report):
        warnings.append(_warn(
            "W_NO_TOC",
            "no table of contents: add a TOC under the title",
            "$"))
    else:
        # The TOC must be a vertical list of content-bearing titles, not one
        # run-in line of linked words.
        toc = TOC_HEADING_RE.search(report)
        if toc:
            entries = []
            for line in report[toc.end():].splitlines():
                if HEADING_RE.match(line):
                    break
                if line.strip():
                    entries.append(line)
            if len(entries) <= 1:
                warnings.append(_warn(
                    "W_THIN_TOC",
                    "the table of contents is a single line; list every "
                    "top-level content section on its own line with a "
                    "descriptive title",
                    "line %d" % (report[: toc.start()].count("\n") + 1)))

    for match in GENERIC_HEADING_RE.finditer(report):
        line_number = report[: match.start()].count("\n") + 1
        warnings.append(_warn(
            "W_GENERIC_HEADING",
            "generic container heading %r tells the reader nothing; use a "
            "content-bearing section title" % match.group(0).strip("# \r\n"),
            "line %d" % line_number))

    if not DEFINITIONS_HEADING_RE.search(report):
        warnings.append(_warn(
            "W_NO_DEFINITIONS",
            "no definitions-and-scope section: open with what the subject is, "
            "which terms are used and how, before any finding",
            "$"))

    first_heading = HEADING_RE.search(report)
    head = report[: first_heading.start()] if first_heading else report
    if not any(INFO_LINE_RE.search(line) for line in head.splitlines()):
        warnings.append(_warn(
            "W_NO_INFO_BLOCK",
            "no header info block before the first section: list subject, "
            "report type, scope, data cut-off and basis as separate bullet "
            "lines (consecutive Markdown lines collapse into one paragraph)",
            "$"))

    if not UNCERTAINTY_RE.search(report):
        warnings.append(_warn(
            "W_NO_UNCERTAINTY",
            "no uncertainty marker anywhere in the body; the woven-in gaps "
            "must still label what is unknown",
            "$"))

    for line_number, line in enumerate(report.splitlines(), start=1):
        if line_number == 1:
            continue  # the sanctioned pointer line to the cited copy
        hit = APPARATUS_RE.search(line)
        if hit:
            failures.append(_warn(
                "E_APPARATUS_LEAK",
                "internal apparatus %r reached the reader-facing report; the "
                "report must read as if the pipeline behind it does not exist "
                "(rewrite the line in the report's own language and without "
                "naming the tool, the protocol or a file)" % hit.group(0),
                "line %d" % line_number))
        elif ".work/" in line:
            warnings.append(_warn(
                "W_APPARATUS_LEAK",
                "middleware path mentioned in the body; only the line-1 "
                "pointer may refer to .work/",
                "line %d" % line_number))


def check_runtime_terms(report, warnings, failures):
    """Scan for run-failure jargon.

    Blacklisted terms fail (reading copy only); ambiguous terms only warn,
    because they may be legitimate content of a network/tech report.
    """
    for line_number, line in enumerate(report.splitlines(), start=1):
        lowered = line.lower()
        for term in RUNTIME_BLACKLIST:
            if term.lower() in lowered:
                failures.append(_warn(
                    "E_RUNTIME_TERM",
                    "run-failure jargon %r must not appear in the reading "
                    "copy; rewrite it as reader-facing prose" % term,
                    "line %d" % line_number))
                break
        for term in RUNTIME_AMBIGUOUS:
            if term.isdigit():
                hit = re.search(r"(?<!\d)%s(?!\d)" % term, line)
            else:
                hit = term in lowered
            if hit:
                warnings.append(_warn(
                    "W_RUNTIME_TERM",
                    "ambiguous runtime term %r kept in the body; record the "
                    "exemption (why it is legitimate here) in the run log"
                    % term,
                    "line %d" % line_number))


def prose_ratio(report):
    """Non-table / non-code / non-pure-list chars over body chars.

    The denominator drops the renderer-owned ``Sources`` / ``Observations``
    sections and any footnote definitions, matching the rule in
    ``references/report-template.md``.
    """
    match = TAIL_HEADING_RE.search(report)
    body = report[: match.start()] if match else report
    lines = [line for line in body.split("\n")
             if not FOOTNOTE_DEF_RE.match(line)]
    total = 0
    prose = 0
    in_fence = False
    for line in lines:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            total += len(line)
            continue
        total += len(line)
        if in_fence or line.lstrip().startswith("|"):
            continue
        if not LIST_LINE_RE.match(line):
            prose += len(line)
    if total <= 0:
        return 1.0
    return prose / float(total)


def check_report(report, evidence, warnings, failures, clean=False):
    is_cjk = bool(CJK_RE.search(report))
    found = check_sections(report, warnings)

    if clean:
        # Delivery stage: the discipline chapters are woven into the narrative,
        # so section presence/order is judged by the final-layout rules below,
        # not by the draft skeleton.
        check_final_layout(report, evidence, warnings, failures)
    else:
        present = {index for index, _, _ in found}
        # In the default GFM-footnote mode the renderer drops the standalone
        # "## Sources" heading and emits [^N]: definitions instead, so a footnote
        # block satisfies the sources slot.
        if FOOTNOTE_DEF_RE.search(report):
            present.add(SLOTS.index(("sources", "来源")))
        # A discipline section that was woven into the narrative still
        # satisfies its slot as long as its in-body markers survive.
        if STRONGEST_RE.search(report):
            present.add(SLOTS.index(
                ("contradictions & counter-evidence", "矛盾与反证")))
        if UNCERTAINTY_RE.search(report):
            present.add(SLOTS.index(("gaps & unknowns", "未知与缺口")))
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

    # Obvious uncited numbers (meaningless in the reading copy, where every
    # marker has been stripped by design).
    if not clean:
        in_heading = False
        for line_number, line in enumerate(report.splitlines(), start=1):
            if HEADING_RE.match(line):
                in_heading = True
                continue
            if line.strip().startswith("|"):
                continue  # table rows (the sources table) are handled by the gate
            if TOC_LINK_RE.search(line):
                continue  # the contents list is links, not claims
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

    # gaps[] present in evidence but no Gaps section in the report (draft
    # stage only — the reading copy weaves them into the narrative).
    has_gaps = isinstance(evidence, dict) and isinstance(
        evidence.get("gaps"), list) and len(evidence.get("gaps")) > 0
    slot_index = {index for index, _, _ in found}
    if not clean and has_gaps and (SLOTS.index(("gaps & unknowns", "未知与缺口"))
                                   not in slot_index):
        warnings.append(_warn(
            "W_REVIEW_GAPS_UNSHOWN",
            "evidence.json carries gaps[] but the report has no "
            "'Gaps & Unknowns' section",
            "$"))

    # Strongest counter-evidence must be called out on its own line.
    if not STRONGEST_RE.search(report):
        warnings.append(_warn(
            "W_REVIEW_NO_STRONGEST_COUNTER",
            "no explicit 'strongest counter-evidence' callout found; "
            "Contradictions & Counter-evidence should open with a "
            "'Strongest counter-evidence:' line",
            "$"))

    # Executive Summary should read as short, plain sentences.
    # W_REVIEW_SUMMARY_LONG is a conservative screen: it splits on CJK sentence
    # enders and on physical line breaks, so for wrapped English prose it
    # degrades to a per-line check. W_REVIEW_SUMMARY_DENSE below is the primary
    # English signal.
    summary = section_body(report, 0)
    for sentence in re.split(r"[。！？!?]\s*|\n+", summary):
        stripped = sentence.strip()
        if len(stripped) > SUMMARY_SENTENCE_LIMIT:
            warnings.append(_warn(
                "W_REVIEW_SUMMARY_LONG",
                "Executive Summary has a %d-character sentence; split it into "
                "shorter ones" % len(stripped),
                "Executive Summary"))
            break

    # Executive Summary should be a TL;DR (short bullets), not a dense paragraph.
    summary_lines = [line for line in summary.splitlines() if line.strip()]
    has_bullets = any(
        re.match(r"\s*(?:[-*+]|\d+[.)])\s+", line) for line in summary_lines)
    sentence_count = len(_summary_sentences(summary))
    if not has_bullets and sentence_count > 4:
        warnings.append(_warn(
            "W_REVIEW_SUMMARY_DENSE",
            "Executive Summary is a %d-sentence paragraph; use 3-5 short "
            "bullets, one figure per line, instead" % sentence_count,
            "Executive Summary"))

    # Prose-first quality signal (warn only, never a delivery blocker).
    ratio = prose_ratio(report)
    if ratio < PROSE_RATIO_MIN:
        warnings.append(_warn(
            "W_PROSE_RATIO",
            "prose ratio is %.2f (target >= %.2f): non-table, non-code, "
            "non-pure-list characters over body characters; convert more "
            "tables/bullets into connected prose" % (ratio, PROSE_RATIO_MIN),
            "$"))

    # Run-failure jargon: reader-facing reading copy only.
    if clean:
        check_runtime_terms(report, warnings, failures)


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
    parser.add_argument("--report", required=True, help="rendered report file")
    parser.add_argument("--evidence", required=True, help="evidence.json")
    parser.add_argument(
        "--clean", action="store_true",
        help="the file is the FINAL reading copy (report.md): enforce the "
             "runtime-failure blacklist and reject standalone discipline "
             "chapters; structural section checks belong to the draft stage",
    )
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
    failures = []
    check_report(report, evidence, warnings, failures, clean=args.clean)
    if args.llm:
        warnings.append(_warn(
            "W_LLM_NOT_RUN",
            "content_review.py performs no network call; run the LLM judge on "
            "the host (requested model: %s)" % (args.model or "unspecified"),
            "$"))

    warnings.sort(key=lambda item: (item["code"], item["where"]))
    if failures:
        failures.sort(key=lambda item: (item["code"], item["where"]))
        emit({"ok": False, "failures": failures, "warnings": warnings})
        return 1
    emit({"ok": True, "warnings": warnings})
    return 0


if __name__ == "__main__":
    sys.exit(main())
