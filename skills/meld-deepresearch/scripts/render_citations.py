#!/usr/bin/env python3
"""Render ``[^sN]`` / ``[^oN]`` citation markers into numbered reference lists.

Usage:
    python render_citations.py --report <report.src.md> --evidence <evidence.json> \
        --output <report.md> [--citations <citations.json>]

Marker format:
    Two marker families, both written inline in the draft report (see
    ``references/evidence-contract.md``):

    ``[^sN]``  a source id present in ``evidence.json``'s ``sources[]``
    ``[^oN]``  an observation id present in ``evidence.json``'s
               ``observations[]`` (an optional top-level array; an absent
               array is treated as empty)

    The two families are numbered independently, each in order of first
    appearance: source markers become ``[N]``, observation markers become
    ``[ON]``, so a source and an observation may both be number 1. Repeated
    markers reuse the same number.

    Everything after the ``## Sources`` heading is replaced by the generated
    numbered source list (the heading is appended when the report has none).
    When at least one observation is cited, a ``## Observations`` section is
    appended as well, one line per cited observation in the form
    ``[ON] method — environment (captured YYYY-MM-DD)`` (an empty or null
    ``environment`` renders as ``unknown``). A marker whose id resolves in
    neither family is an **orphan** and is left un-replaced so a human can
    find it.

Results:
    stdout is one JSON object: ``{"ok": bool, "citation_count": N,
    "observation_count": N, "orphans": [...], "uncited": [...]}``.
    ``--citations`` (default: ``citations.json`` next to ``--output``) gets
    ``{"ok": bool, "citations": [...], "observations": [...],
    "orphans": [...], "uncited": [...]}``.

Exit codes:
    0  rendered successfully (uncited sources and observations are a warning,
       never a failure)
    1  orphan markers (id not in ``sources[]`` / ``observations[]``) or
       unresolved markers remain
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
OBSERVATIONS_HEADING_RE = re.compile(r"^## Observations[^\n]*", re.MULTILINE)
# Observation ids follow the contract pattern ``oN`` (1-based, no leading
# zeros); anything else is treated as a source id.
OBSERVATION_ID_RE = re.compile(r"^o\d+$")


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
    # ``observations[]`` is optional: absent or null means "no observations".
    if data.get("observations") is None:
        data["observations"] = []
    elif not isinstance(data["observations"], list):
        fail("evidence file 'observations' must be an array")
    return data


class _Parser(argparse.ArgumentParser):
    """ArgumentParser whose usage errors are JSON bodies with exit 2."""

    def error(self, message):
        emit({"ok": False, "error": message})
        raise SystemExit(2)


def build_parser():
    parser = _Parser(
        prog="render_citations.py",
        description="Render [^sN] / [^oN] markers into numbered citation lists.",
    )
    parser.add_argument("--report", required=True, help="draft report (report.src.md)")
    parser.add_argument(
        "--evidence",
        required=True,
        help="evidence.json with sources[] (and optional observations[])",
    )
    parser.add_argument("--output", required=True, help="rendered report.md")
    parser.add_argument(
        "--citations",
        default=None,
        help="citations.json path (default: citations.json next to --output)",
    )
    return parser


def index_by_id(entries):
    """First occurrence wins; preserve array order for uncited reporting."""
    ordered_ids = []
    by_id = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or not entry_id:
            continue
        if entry_id not in by_id:
            by_id[entry_id] = entry
            ordered_ids.append(entry_id)
    return by_id, ordered_ids


def resolve_marker(marker_id, by_source_id, by_observation_id):
    """Classify a marker id: ``"source"``, ``"observation"``, or ``None``.

    Ids matching the observation pattern ``oN`` resolve against
    ``observations[]`` first (falling back to ``sources[]`` for any legacy
    source id shaped like an observation); every other id resolves against
    ``sources[]`` first (falling back to ``observations[]``). An id that
    resolves in neither family is an orphan.
    """
    if OBSERVATION_ID_RE.match(marker_id):
        if marker_id in by_observation_id:
            return "observation"
        return "source" if marker_id in by_source_id else None
    if marker_id in by_source_id:
        return "source"
    return "observation" if marker_id in by_observation_id else None


def assign_numbers(report_text, by_source_id, by_observation_id):
    """Number each marker family by first appearance; collect orphan ids.

    The two sequences are independent: a source and an observation may both
    be number 1.
    """
    source_numbers = {}
    observation_numbers = {}
    orphans = []
    for match in MARKER_RE.finditer(report_text):
        marker_id = match.group(1).strip()
        if not marker_id:
            continue  # empty marker -> unresolved, caught by the residual check
        family = resolve_marker(marker_id, by_source_id, by_observation_id)
        if family == "source":
            if marker_id not in source_numbers:
                source_numbers[marker_id] = len(source_numbers) + 1
        elif family == "observation":
            if marker_id not in observation_numbers:
                observation_numbers[marker_id] = len(observation_numbers) + 1
        elif marker_id not in orphans:
            orphans.append(marker_id)
    return source_numbers, observation_numbers, orphans


def substitute_markers(report_text, source_numbers, observation_numbers):
    """Replace resolvable markers with [N] / [ON]; leave orphans visible."""

    def replace(match):
        marker_id = match.group(1).strip()
        if not marker_id:
            return match.group(0)
        if marker_id in source_numbers:
            return "[%d]" % source_numbers[marker_id]
        if marker_id in observation_numbers:
            return "[O%d]" % observation_numbers[marker_id]
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


def observation_line(number, observation):
    method = str(observation.get("method") or "")
    environment = observation.get("environment")
    if environment in (None, ""):
        environment = "unknown"
    captured_at = observation.get("captured_at")
    if captured_at in (None, ""):
        captured_at = "unknown"
    return "[O%d] %s — %s (captured %s)" % (number, method, environment, captured_at)


def build_observations_section(text, numbers, by_id):
    """Append ## Observations, or rebuild the content after an existing one.

    Only called when at least one observation is cited.
    """
    ordered = sorted(numbers.items(), key=lambda item: item[1])
    lines = [
        observation_line(number, by_id[observation_id])
        for observation_id, number in ordered
    ]
    block = "\n".join(lines)

    heading = OBSERVATIONS_HEADING_RE.search(text)
    if heading:
        head = text[: heading.end()]  # heading line without its newline
        if block:
            return head + "\n\n" + block + "\n"
        return head + "\n"

    body = text
    if body and not body.endswith("\n"):
        body += "\n"
    body += "\n## Observations\n"
    if block:
        body += "\n" + block + "\n"
    return body


def main(argv=None):
    args = build_parser().parse_args(argv)

    report_text = read_text(args.report, "report file")
    evidence = load_evidence(args.evidence)

    by_id, ordered_ids = index_by_id(evidence["sources"])
    obs_by_id, obs_ordered_ids = index_by_id(evidence["observations"])
    source_numbers, observation_numbers, orphans = assign_numbers(
        report_text, by_id, obs_by_id
    )
    rendered = substitute_markers(report_text, source_numbers, observation_numbers)
    rendered = build_sources_section(rendered, source_numbers, by_id)
    if observation_numbers:
        rendered = build_observations_section(
            rendered, observation_numbers, obs_by_id
        )

    unresolved = "[^" in rendered
    uncited = [
        source_id for source_id in ordered_ids if source_id not in source_numbers
    ] + [
        observation_id
        for observation_id in obs_ordered_ids
        if observation_id not in observation_numbers
    ]
    ok = not orphans and not unresolved

    citations = [
        {
            "number": source_numbers[source_id],
            "source_id": source_id,
            "title": by_id[source_id].get("title"),
            "url": by_id[source_id].get("url"),
            "quality": by_id[source_id].get("quality"),
            "published_at": by_id[source_id].get("published_at"),
        }
        for source_id, _ in sorted(
            source_numbers.items(), key=lambda item: item[1]
        )
    ]
    observation_citations = [
        {
            "number": observation_numbers[observation_id],
            "observation_id": observation_id,
            "kind": obs_by_id[observation_id].get("kind"),
            "method": obs_by_id[observation_id].get("method"),
            "command": obs_by_id[observation_id].get("command"),
            "captured_at": obs_by_id[observation_id].get("captured_at"),
            "environment": obs_by_id[observation_id].get("environment"),
        }
        for observation_id, _ in sorted(
            observation_numbers.items(), key=lambda item: item[1]
        )
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
                "observations": observation_citations,
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
            "citation_count": len(source_numbers),
            "observation_count": len(observation_numbers),
            "orphans": orphans,
            "uncited": uncited,
        }
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
