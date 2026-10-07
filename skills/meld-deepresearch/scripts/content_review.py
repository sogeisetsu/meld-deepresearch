#!/usr/bin/env python3
"""Content self-review for a rendered report.

Usage:
    python content_review.py --report <report.md> --evidence <evidence.json>
                             [--clean] [--fix] [--llm] [--model <provider/model>]

Two review modes:

``--clean``
    The file is the **final reading copy** (``report.md``). This is the
    delivery-stage review — the acceptance check for the mandatory
    *pre-delivery readability pass* described in ``report-template.md``:
      * the runtime-failure blacklist below is enforced (exit 1 on a hit);
      * a narrated run failure (login wall, unopenable page) is an error
        (``E_FAILURE_NARRATION``) and internal apparatus in the body is an
        error (``E_APPARATUS_LEAK``) — together with the blacklist these are
        the three hard failures (exit 1);
      * a standalone discipline chapter — ``## Contradictions &
        Counter-evidence`` / ``## Gaps & Unknowns`` (or their Chinese forms,
        at H2 or H3) — is detected and reported as a **warning**
        (``E_STANDALONE_SECTION``, same code/message/hint, ``warnings[]``,
        exit 0): at delivery those sections are woven into the narrative,
        not left standing;
      * a labelled counter-evidence callout — a line opening with a bold
        ``**最强反证：**`` / ``**Strongest counter-evidence:**`` label — is
        detected and reported as a **warning** (``E_ADVERSARY_CALLOUT``,
        same code/message/hint, ``warnings[]``, exit 0): at delivery the
        counter-evidence is woven into the paragraph of the claim it
        qualifies;
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

``--fix`` (optional, orthogonal to both modes)
    Before reviewing, apply the two **closed** safe operations below to the
    ``--report`` target *and* its counterpart copy (the pair derives from the
    same outdir root: ``OUT/report.md`` <-> ``OUT/.work/report.cited.md``;
    either may be given as ``--report``, and a missing counterpart is simply
    not edited — never an error):

      1. **Label stripping** — remove the exact bold callout-label tokens in
         ``ADVERSARY_LABEL_TOKENS`` (the precise tokens ``E_ADVERSARY_CALLOUT``
         matches, both colon widths), keeping the sentence that follows inline
         and every surrounding byte otherwise identical;
      2. **Generic container headings** — demote one level the heading lines
         seeded in the closed map ``GENERIC_HEADING_FIX`` (the headings
         ``W_GENERIC_HEADING`` itself treats as generic). Headings absent from
         the map are never touched.

    Nothing else is ever rewritten: unsafe shapes — notably a standalone
    discipline chapter (``E_STANDALONE_SECTION``) — are NEVER auto-merged,
    restructured or deleted, so ``--fix`` on a report whose only remaining
    condition is unsafe changes nothing and reports ``E_STANDALONE_SECTION``
    as a warning (exit 0 under ``--clean``); the fix pass never hides a
    downgraded condition by editing around it.
    With ``--fix`` the JSON gains one extra field ``fixes`` (one record per
    applied edit: ``{"file","op","line","detail"}``); without ``--fix`` the
    stdout JSON and exit codes are unchanged byte-for-byte.

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
With ``--fix`` the object additionally carries ``"fixes": [...]``; without
the flag no field is added or reordered.

Hints (additive, on demand): every warning/failure entry whose ``code`` is a
key of the closed ``HINTS`` map below additionally carries a short actionable
``"hint"`` string — the fix side of the anti-pattern table migrated out of
``report-template.md``. The hint is attached only when its code fires, so a
run in which no mapped code fires contains no hint anywhere; every existing
field, exit code and greppable substring is unchanged in both normal and
``--fix`` modes.

Exit codes: 0 pass (warnings allowed), 1 delivery-gate failure in ``--clean``
mode, 2 bad input (unreadable file / invalid JSON / wrong usage).

Python 3 standard library only; no network access.
"""

import argparse
import json
import re
import sys
from pathlib import Path

HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
CITATION_MARK_RE = re.compile(r"\[\^?[so]?\d+\]|\[O\d+\]|\[\[\d+\]\]|\[\^o\d+\]")
NUMBER_RE = re.compile(r"\d[\d,]*(?:\.\d+)?\s*%?")
YEAR_RE = re.compile(r"^(?:19|20)\d{2}$")
# Counter-evidence / limitation wording, in either language, in any of its
# ordinary woven-in forms: a report that contains none of it at all shows the
# active refutation search never happened.
COUNTER_EVIDENCE_RE = re.compile(
    r"最强反证|最强反方|反证|反驳|相悖|相反|不过|然而|局限|限制|存疑|未能证实|"
    r"strongest counter|counter-evidence|however|contrary|contradict|"
    r"limited by|caveat|dispute",
    re.IGNORECASE)
# A labelled counter-evidence callout is a draft device. At delivery the
# counter-evidence is woven into the paragraph of the claim it qualifies, so a
# line that begins (after an optional list bullet) with the bold label is a
# delivery-stage defect reported as a warning (E_ADVERSARY_CALLOUT, downgraded
# from a hard fail; detection unchanged); either language form and both colon
# widths count.
ADVERSARY_CALLOUT_RE = re.compile(
    r"^[ \t]*(?:(?:[-*+]|\d+[.)])[ \t]+)?"
    r"\*\*(?:最强反证|最强反方|strongest counter-evidence)[:：]\*\*",
    re.IGNORECASE)
# Closed ``--fix`` label-token list: the exact bold callout-label prefixes
# enumerated from ADVERSARY_CALLOUT_RE — both Chinese words, both colon widths,
# and the English form in either colon width (removed case-insensitively, as
# the checker accepts any casing). This tuple is the whole vocabulary of
# operation 1; no other prose is ever matched or rewritten.
ADVERSARY_LABEL_TOKENS = (
    "**最强反证：**",
    "**最强反证:**",
    "**最强反方：**",
    "**最强反方:**",
    "**strongest counter-evidence:**",
    "**strongest counter-evidence：**",
)
# Removal unit = one token plus at most the single space right after it, so
# the surviving sentence stays joined by exactly one space and a line-start
# callout leaves no leading whitespace (``claim. **T:** x`` -> ``claim. x``).
ADVERSARY_LABEL_RE = re.compile(
    "(?:%s)[ \t]?" % "|".join(re.escape(token)
                             for token in ADVERSARY_LABEL_TOKENS),
    re.IGNORECASE)
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
# woven into the narrative, so seeing one in the reading copy is a defect —
# detected and reported as a warning (E_STANDALONE_SECTION, downgraded from a
# hard fail; detection unchanged).
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
# Closed ``--fix`` heading map, seeded ONLY with the headings
# GENERIC_HEADING_RE itself treats as generic containers (same order).
# Key = heading text (matched case-insensitively on a ``##`` heading line);
# value = the replacement line for the canonical form. Every shipped entry
# demotes exactly one level and preserves the line's own text bytes, so
# ``## Findings`` becomes ``### Findings`` and ``## findings`` becomes
# ``### findings``. Anything not in this map is never touched.
GENERIC_HEADING_FIX = {
    "主要发现": "### 主要发现",
    "Findings": "### Findings",
    "分析": "### 分析",
    "结果": "### 结果",
    "Results": "### Results",
    "Analysis": "### Analysis",
}
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
    """Delivery-stage layout rules for the reading copy (``report.md``).

    Three codes are hard failures (``failures``, exit 1): ``E_RUNTIME_TERM``
    (in ``check_runtime_terms``), ``E_FAILURE_NARRATION`` and
    ``E_APPARATUS_LEAK``. Two codes were downgraded: ``E_STANDALONE_SECTION``
    and ``E_ADVERSARY_CALLOUT`` keep their code, message and hint but are
    appended to ``warnings`` — same detection, warn severity, exit 0.
    """
    for line_number, line in enumerate(report.splitlines(), start=1):
        if ADVERSARY_CALLOUT_RE.match(line):
            warnings.append(_warn(
                "E_ADVERSARY_CALLOUT",
                "labelled counter-evidence callout reached the reading copy; "
                "weave the counter-evidence into the paragraph of the claim "
                "it qualifies — same sentence or the one immediately after, "
                "joined by an ordinary contrastive transition (不过 / however "
                "/ but / limited by), with no bold label and no standalone "
                "paragraph",
                "line %d" % line_number))

    for match in STANDALONE_DISCIPLINE_RE.finditer(report):
        line_number = report[: match.start()].count("\n") + 1
        warnings.append(_warn(
            "E_STANDALONE_SECTION",
            "standalone discipline chapter %r must not exist in the reading "
            "copy; weave it into the section whose claim it belongs to, "
            "keeping every limitation and `unknown` label attached to the "
            "claim it qualifies" % match.group(0).strip("# \r\n"),
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
        if COUNTER_EVIDENCE_RE.search(report):
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

    # Counter-evidence/limitation wording must exist somewhere in the report:
    # warn only when there is none at all, whatever form it takes.
    if not COUNTER_EVIDENCE_RE.search(report):
        warnings.append(_warn(
            "W_REVIEW_NO_STRONGEST_COUNTER",
            "no counter-evidence or limitation wording found anywhere in the "
            "report; weave the strongest refutation into the paragraph of the "
            "claim it qualifies (however / but / 不过 / 局限 …)",
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


# Closed hint map (additive output field, "failure hints on demand"): the fix
# side of the anti-pattern -> fix table formerly kept in
# ``references/report-template.md`` (its "Do / Don't" and readability-check
# rows), keyed only by codes this checker itself emits. An entry gains
# ``"hint"`` exactly when its code is a key here — no other field, no exit
# code and no existing substring changes, in normal or ``--fix`` mode. Rows
# of the old table with no code of ours (single-tertiary sourcing,
# observation reproducibility, prescriptions-as-findings, hand-numbered
# citations, requested chapter counts, running the readability pass) stay in
# ``report-template.md`` as pure writing rules and are deliberately absent.
HINTS = {
    # --clean delivery codes ----------------------------------------------
    # E_STANDALONE_SECTION and E_ADVERSARY_CALLOUT were downgraded to
    # warnings (same code, message and hint — only the bucket changed);
    # E_RUNTIME_TERM, E_FAILURE_NARRATION and E_APPARATUS_LEAK still fail.
    "E_ADVERSARY_CALLOUT":
        "weave the counter-evidence into the paragraph of the claim it "
        "qualifies (same sentence or the one immediately after, an ordinary "
        "contrastive transition, no bold label, no standalone paragraph); "
        "`content_review.py --fix` strips the exact **-style labels from "
        "both copies automatically",
    "E_STANDALONE_SECTION":
        "no automatic fix for this shape: edit report.src.md so the "
        "chapter's material sits inside the sections whose claims it "
        "qualifies — each `unknown` label stays beside its claim, and "
        "## Observations never enters the reading copy — then re-render",
    "E_FAILURE_NARRATION":
        "state the epistemic status instead ('复购率尚无公开披露' / 'no "
        "verifiable public source'); the obstacle the run hit belongs in "
        "observations[]/gaps[], never in report.md",
    "E_APPARATUS_LEAK":
        "rewrite the line in the report's own language without naming any "
        "tool, skill, protocol or draft file",
    "E_RUNTIME_TERM":
        "delete the run-failure jargon or rephrase it as reader-facing "
        "prose ('该数据尚无已核验的公开披露'); reason enums, HTTP statuses "
        "and process nouns belong in evidence.json, not in the report",
    # --clean warn-only ----------------------------------------------------
    "W_NO_INFO_BLOCK":
        "write the info block as a bullet list — one item per rendered "
        "line, five rows like a cover sheet; never a run-in or blockquote "
        "paragraph",
    "W_NO_TOC":
        "add a vertical TOC under the info block listing every top-level "
        "content section with a descriptive, content-bearing title",
    "W_THIN_TOC":
        "one TOC entry per line, one per section: a single joined line or "
        "3-4 generic entries is the defect",
    "W_GENERIC_HEADING":
        "retitle with what the section concludes (e.g. `## 竞争格局与份额`); "
        "`content_review.py --fix` demotes the generic container one level",
    "W_NO_DEFINITIONS":
        "open the body with the definitions-and-scope section before any "
        "finding: subject, working terms, counting boundary, time window, "
        "no new claims",
    "W_NO_UNCERTAINTY":
        "put an `unknown` label with a reader-facing reason next to the "
        "claim it qualifies; never collect unknowns into a block",
    "W_RUNTIME_TERM":
        "keep the term only when the subject genuinely needs it and record "
        "the exemption reason in the run log; otherwise delete it",
    "W_APPARATUS_LEAK":
        "only the line-1 pointer may mention .work/; drop the path from the "
        "body",
    "W_PROSE_RATIO":
        "convert more tables and bullets into connected prose until the "
        "ratio reaches the 0.80 target",
    # draft / structural review (no --clean) -------------------------------
    "W_REVIEW_NUMBER_UNCITED":
        "add a [^sN]/[^oN] marker to the number (Executive Summary "
        "included) or drop the figure; an id that resolves nowhere fails "
        "gate ② (protocol.md §9)",
}


def attach_hints(entries):
    """Attach the optional ``hint`` to each entry with a mapped code.

    Additive and on demand: entries whose code is not in ``HINTS`` — and a
    run where no mapped code fires at all — gain no field, so every existing
    key, exit code and greppable substring is untouched.
    """
    for entry in entries:
        hint = HINTS.get(entry["code"])
        if hint is not None:
            entry["hint"] = hint


def counterpart_path(report_path):
    """The other copy of the same report, derived from the same outdir root.

    ``OUT/report.md`` <-> ``OUT/.work/report.cited.md``; either member may be
    the ``--report`` target. A report under any other name has no counterpart
    and returns ``None``.
    """
    path = Path(report_path)
    if path.name == "report.md":
        return path.parent / ".work" / "report.cited.md"
    if path.name == "report.cited.md" and path.parent.name == ".work":
        return path.parent.parent / "report.md"
    return None


def apply_fixes(text, label):
    """Apply the two closed ``--fix`` operations to one file's text.

    Returns ``(new_text, fixes)``. Operation 1 strips the exact
    ``ADVERSARY_LABEL_TOKENS`` (outside code fences); operation 2 demotes one
    level the ``##`` heading lines seeded in ``GENERIC_HEADING_FIX``. Every
    other byte — footnote markers, prose, tables, headings outside the map —
    is preserved exactly. The unsafe shapes (a standalone discipline chapter,
    ``E_STANDALONE_SECTION``) are deliberately NOT an operation here: they are
    never auto-merged, restructured or deleted.
    """
    fixes = []
    segments = text.split("\n")
    in_fence = False
    for index, segment in enumerate(segments):
        if FENCE_RE.match(segment):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        updated = segment
        hits = list(ADVERSARY_LABEL_RE.finditer(segment))
        if hits:
            updated = ADVERSARY_LABEL_RE.sub("", segment)
            for hit in hits:
                fixes.append({
                    "file": label,
                    "op": "strip-label",
                    "line": index + 1,
                    "detail": hit.group(0).rstrip(" \t"),
                })
        heading = HEADING_RE.match(updated)
        if heading:
            key = heading.group(1).strip().casefold()
            for canonical, replacement in GENERIC_HEADING_FIX.items():
                if canonical.casefold() == key:
                    demoted = replacement.split(" ", 1)[0] + updated[2:]
                    if demoted != updated:
                        fixes.append({
                            "file": label,
                            "op": "demote-heading",
                            "line": index + 1,
                            "detail": updated.strip(),
                        })
                        updated = demoted
                    break
        if updated != segment:
            segments[index] = updated
    return "\n".join(segments), fixes


def fix_file(path):
    """Apply the closed ``--fix`` operations to one file on disk.

    Reads/writes bytes-preservingly (BOM and line endings survive); a file
    with no applicable change is not rewritten at all.
    """
    try:
        with open(path, "rb") as handle:
            raw = handle.read()
        text = raw.decode("utf-8-sig")
    except (OSError, UnicodeError) as exc:
        fail("cannot read report file: %s" % exc)
    updated, fixes = apply_fixes(text, str(path))
    if updated != text:
        payload = (b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b"")
        payload += updated.encode("utf-8")
        try:
            with open(path, "wb") as handle:
                handle.write(payload)
        except OSError as exc:
            fail("cannot write report file: %s" % exc)
    return fixes


def run_fix(report_path):
    """Apply the closed ``--fix`` operations to the report and its counterpart.

    Both copies of one report must not diverge, so the same edits go to
    ``--report`` and to its paired copy when that copy exists; a missing
    counterpart is never an error. Returns the fix records, ``--report``
    target first.
    """
    fixes = fix_file(report_path)
    other = counterpart_path(report_path)
    if other is not None and str(other) != str(report_path) and other.is_file():
        fixes.extend(fix_file(str(other)))
    return fixes


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
             "runtime-failure blacklist (hard fail) plus failure narration "
             "and apparatus leaks (hard fails); standalone discipline "
             "chapters and labelled counter-evidence callouts are detected "
             "and reported as warnings; structural section checks belong "
             "to the draft stage",
    )
    parser.add_argument(
        "--fix", action="store_true",
        help="before reviewing, apply the two closed safe edits (strip the "
             "ADVERSARY_LABEL_TOKENS callout labels; demote the "
             "GENERIC_HEADING_FIX container headings) to --report and to its "
             "counterpart copy (OUT/report.md <-> OUT/.work/report.cited.md); "
             "unsafe shapes such as a standalone discipline chapter are "
             "never auto-fixed, and the JSON gains a fixes[] field",
    )
    parser.add_argument(
        "--llm", action="store_true",
        help="request the (host-run) LLM judge; this script records that it "
             "did not run it")
    parser.add_argument("--model", default=None, help="provider/model for --llm")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    # Closed --fix pass runs BEFORE the review so the checks judge the fixed
    # content. Without the flag this block is skipped entirely and the emitted
    # JSON stays byte-for-byte identical to the no-fix output.
    fixes = run_fix(args.report) if args.fix else None

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
    # Additive hint pass: only entries whose code is in the closed HINTS map
    # gain a "hint" key; a run with no mapped code fires emits none at all.
    attach_hints(warnings)
    attach_hints(failures)
    if failures:
        payload = {"ok": False, "failures": failures, "warnings": warnings}
        if fixes is not None:
            payload["fixes"] = fixes
        emit(payload)
        return 1
    payload = {"ok": True, "warnings": warnings}
    if fixes is not None:
        payload["fixes"] = fixes
    emit(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
