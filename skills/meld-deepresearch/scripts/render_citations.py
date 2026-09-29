#!/usr/bin/env python3
"""Render ``[^source_id]`` citation markers into a numbered reference list.

Usage:
    python render_citations.py --report <report.src.md> --evidence <evidence.json> \
        --output <report.md> [--citations <citations.json>]

Marker format:
    ``[^source_id]`` written inline in the draft report, where ``source_id`` is
    an id present in ``evidence.json``'s ``sources[]`` (see
    ``references/evidence-contract.md``). Markers are numbered in order of
    first appearance, replaced inline with ``[N]``, and everything after the
    ``## Sources`` heading is replaced by the generated numbered list (the
    heading is appended when the report has none). Repeated markers reuse the
    same number.

Results:
    stdout is one JSON object: ``{"ok": bool, "citation_count": N,
    "orphans": [...], "uncited": [...]}``.
    ``--citations`` (default: ``citations.json`` next to ``--output``) gets
    ``{"ok": bool, "citations": [...], "orphans": [...], "uncited": [...]}``.

Exit codes:
    0  rendered successfully (uncited sources are a warning, never a failure)
    1  orphan markers (id not in ``sources[]``) or unresolved markers remain
    2  bad input (missing/unreadable file, invalid JSON, wrong usage)

Stdout is ASCII-safe (``ensure_ascii=True``); ``report.md`` and
``citations.json`` are written UTF-8 without BOM, LF line endings, on every
platform. Python 3 standard library only; no network access.
"""

import argparse
import json
import os
import re
import sys

MARKER_RE = re.compile(r"\[\^([^\]]*)\]")
SOURCES_HEADING_RE = re.compile(r"^## Sources[^\n]*", re.MULTILINE)


def emit(obj):
    """Print exactly one JSON object to stdout (ASCII-safe)."""
    sys.stdout.write(json.dumps(obj, ensure_ascii=True) + "\n")


def fail(message):
    """Bad input: report a JSON error body and exit 2."""
    emit({"ok": False, "error": message})
    raise SystemExit(2)


def read_text(path, what):
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            return handle.read()
    except OSError as exc:
        fail("cannot read %s: %s" % (what, exc))


def write_text(path, text):
    """Write UTF-8 without BOM, LF line endings, creating parent dirs."""
    try:
        directory = os.path.dirname(os.path.abspath(path))
        os.makedirs(directory, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    except OSError as exc:
        fail("cannot write %s: %s" % (path, exc))


def load_evidence(path):
    raw = read_text(path, "evidence file")
    try:
        data = json.loads(raw)
    except ValueError as exc:
        fail("invalid JSON in evidence file: %s" % exc)
    if not isinstance(data, dict):
        fail("evidence file must be a JSON object")
    if not isinstance(data.get("sources"), list):
        fail("evidence file must contain a 'sources' array")
    return data


class _Parser(argparse.ArgumentParser):
    """ArgumentParser whose usage errors are JSON bodies with exit 2."""

    def error(self, message):
        emit({"ok": False, "error": message})
        raise SystemExit(2)


def build_parser():
    parser = _Parser(
        prog="render_citations.py",
        description="Render [^source_id] markers into a numbered citation list.",
    )
    parser.add_argument("--report", required=True, help="draft report (report.src.md)")
    parser.add_argument("--evidence", required=True, help="evidence.json with sources[]")
    parser.add_argument("--output", required=True, help="rendered report.md")
    parser.add_argument(
        "--citations",
        default=None,
        help="citations.json path (default: citations.json next to --output)",
    )
    return parser


def index_sources(sources):
    """First occurrence wins; preserve sources[] order for uncited reporting."""
    ordered_ids = []
    by_id = {}
    for source in sources:
        if not isinstance(source, dict):
            continue
        source_id = source.get("id")
        if not isinstance(source_id, str) or not source_id:
            continue
        if source_id not in by_id:
            by_id[source_id] = source
            ordered_ids.append(source_id)
    return by_id, ordered_ids


def assign_numbers(report_text, by_id):
    """Number markers by first appearance; collect orphan ids in the same pass."""
    numbers = {}
    orphans = []
    for match in MARKER_RE.finditer(report_text):
        source_id = match.group(1).strip()
        if not source_id:
            continue  # empty marker -> unresolved, caught by the residual check
        if source_id not in by_id:
            if source_id not in orphans:
                orphans.append(source_id)
            continue
        if source_id not in numbers:
            numbers[source_id] = len(numbers) + 1
    return numbers, orphans


def substitute_markers(report_text, numbers):
    """Replace resolvable markers with [N]; leave orphans visible for humans."""

    def replace(match):
        source_id = match.group(1).strip()
        if source_id and source_id in numbers:
            return "[%d]" % numbers[source_id]
        return match.group(0)

    return MARKER_RE.sub(replace, report_text)


def reference_line(number, source):
    title = str(source.get("title") or "")
    url = str(source.get("url") or "")
    quality = str(source.get("quality") or "unknown")
    published_at = source.get("published_at")
    if published_at in (None, ""):
        published_at = "unknown"
    return "[%d] %s — %s (%s, %s)" % (number, title, url, quality, published_at)


def build_sources_section(text, numbers, by_id):
    """Replace everything after the ## Sources heading, or append the heading."""
    ordered = sorted(numbers.items(), key=lambda item: item[1])
    lines = [reference_line(number, by_id[source_id]) for source_id, number in ordered]
    block = "\n".join(lines)

    heading = SOURCES_HEADING_RE.search(text)
    if heading:
        head = text[: heading.end()]  # heading line without its newline
        if block:
            return head + "\n\n" + block + "\n"
        return head + "\n"

    body = text
    if body and not body.endswith("\n"):
        body += "\n"
    body += "\n## Sources\n"
    if block:
        body += "\n" + block + "\n"
    return body


def main(argv=None):
    args = build_parser().parse_args(argv)

    report_text = read_text(args.report, "report file")
    evidence = load_evidence(args.evidence)

    by_id, ordered_ids = index_sources(evidence["sources"])
    numbers, orphans = assign_numbers(report_text, by_id)
    rendered = substitute_markers(report_text, numbers)
    rendered = build_sources_section(rendered, numbers, by_id)

    unresolved = "[^" in rendered
    uncited = [source_id for source_id in ordered_ids if source_id not in numbers]
    ok = not orphans and not unresolved

    citations = [
        {
            "number": numbers[source_id],
            "source_id": source_id,
            "title": by_id[source_id].get("title"),
            "url": by_id[source_id].get("url"),
            "quality": by_id[source_id].get("quality"),
            "published_at": by_id[source_id].get("published_at"),
        }
        for source_id, _ in sorted(numbers.items(), key=lambda item: item[1])
    ]

    write_text(args.output, rendered)
    citations_path = args.citations or os.path.join(
        os.path.dirname(os.path.abspath(args.output)), "citations.json"
    )
    write_text(
        citations_path,
        json.dumps(
            {
                "ok": ok,
                "citations": citations,
                "orphans": orphans,
                "uncited": uncited,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )

    emit(
        {
            "ok": ok,
            "citation_count": len(numbers),
            "orphans": orphans,
            "uncited": uncited,
        }
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
