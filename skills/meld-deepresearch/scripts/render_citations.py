#!/usr/bin/env python3
"""Render ``[^sN]`` / ``[^oN]`` citation markers into numbered reference lists.

Usage:
    python render_citations.py --report <report.src.md> --evidence <evidence.json> \
        --output <report.cited.md> [--clean-output <report.md>] \
        [--citations <citations.json>]

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
    ``[^oN]: method — environment (captured YYYY-MM-DD)`` in the default GFM
    mode (``--legacy-plain`` uses ``[ON] method — ...``; GFM mode also drops the
    heading, see "Three render modes"). An empty or null ``environment``
    renders as ``unknown``. A marker whose id resolves in neither family is an
    **orphan** and is left un-replaced so a human can find it.

    Three render modes:
      * default        GFM footnotes: the marker becomes ``[^N]`` (source) or
                       ``[^oN]`` (observation) and the reference list becomes
                       footnote definitions ``[^N]: ...``. A GFM renderer
                       (GitHub, most editors) shows a numbered superscript and
                       wires the jump and back-link itself, so it needs no
                       inline HTML and survives HTML sanitising. The standalone
                       ``## Sources`` / ``## Observations`` headings are dropped
                       in this mode (the GFM renderer builds its own footnotes
                       block).
      * ``--anchors``  ``[[N]](#ref-N)`` with a first-occurrence cite anchor
                       ``<a id="cite-N"></a>`` and a backlink ``[↩](#cite-N)``
                       on each reference line — clickable on hosts that keep
                       inline HTML (many strip ``id`` attributes, which is why
                       footnotes are the default).
      * ``--legacy-plain`` the old plain ``[N]`` / ``[ON]`` text, kept for
                       byte-for-byte backward compatibility.

    Two output files from one run:
      * ``--output`` is the **cited** version (``report.cited.md``): every
        marker substituted, the full footnote/anchor/plain reference block at
        the end. This is the complete, checkable artefact.
      * ``--clean-output`` (optional) is the **reading** version
        (``report.md``): all markers stripped, the renderer-owned tail removed
        and rebuilt as plain un-numbered ``## Sources`` / ``## Observations``
        lists, and one pointer line at the very top linking to the cited
        version. The pointer line follows the report's language (Chinese when
        the body contains CJK, English otherwise). The clean file is derived
        from the same numbers as the cited one, so the two can never disagree
        about which source backs which passage.
      * Both files are written by the same invocation; never hand-edit one into
        agreement with the other.

    The gate judgement: an orphan (id in neither array) still fails in every
    mode. In anchor/legacy mode any leftover ``[^`` marker also fails. In the
    default footnotes mode the rendered ``[^N]`` markers are expected, so the
    residual check cannot be used there; instead a marker whose captured id is
    empty after ``strip()`` (``[^]`` / ``[^ ]``) is detected in the rendered
    output and fails as unresolved, alongside orphans. The judgement is made
    on the cited rendering; the clean file has no markers left to judge.

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
SOURCES_HEADING_RE = re.compile(r"^## (?:Sources|来源)[^\n]*", re.MULTILINE)
OBSERVATIONS_HEADING_RE = re.compile(
    r"^## (?:Observations|观测记录)[^\n]*", re.MULTILINE)
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
    parser.add_argument("--output", required=True, help="rendered report.cited.md")
    parser.add_argument(
        "--clean-output",
        default=None,
        help="also write the marker-free reading copy (report.md) in the same "
             "run; its first line links to the cited version written to "
             "--output",
    )
    parser.add_argument(
        "--citations",
        default=None,
        help="citations.json path (default: citations.json next to --output)",
    )
    parser.add_argument(
        "--anchors",
        action="store_true",
        help="render clickable HTML anchors ([[N]](#ref-N) + <a id>) instead "
             "of the default GFM footnotes; note that many renderers strip "
             "id attributes, which is why footnotes are the default",
    )
    parser.add_argument(
        "--footnotes",
        action="store_true",
        help="deprecated no-op alias: GFM footnotes are already the default",
    )
    parser.add_argument(
        "--legacy-plain",
        action="store_true",
        help="render the old plain [N]/[ON] text (no links)",
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
            # empty marker -> unresolved: anchor/legacy modes catch it via the
            # residual-[^ scan below; footnotes mode has no residual scan (its
            # [^N] markers are expected), so it is caught by an explicit
            # blank-marker scan of the rendered output instead.
            continue
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


def substitute_markers(report_text, source_numbers, observation_numbers, mode):
    """Replace resolvable markers per ``mode``; leave orphans visible.

    ``mode`` is ``"footnotes"`` (default), ``"anchor"`` or ``"legacy"``.
    """
    source_cited = set()
    observation_cited = set()

    def replace(match):
        marker_id = match.group(1).strip()
        if not marker_id:
            return match.group(0)
        if marker_id in source_numbers:
            number = source_numbers[marker_id]
            if mode == "legacy":
                return "[%d]" % number
            if mode == "footnotes":
                return "[^%d]" % number
            link = "[[%d]](#ref-%d)" % (number, number)
            if number in source_cited:
                return link
            source_cited.add(number)
            return '<a id="cite-%d"></a>%s' % (number, link)
        if marker_id in observation_numbers:
            number = observation_numbers[marker_id]
            if mode == "legacy":
                return "[O%d]" % number
            if mode == "footnotes":
                return "[^o%d]" % number
            link = "[[O%d]](#oref-%d)" % (number, number)
            if number in observation_cited:
                return link
            observation_cited.add(number)
            return '<a id="ocite-%d"></a>%s' % (number, link)
        return match.group(0)

    return MARKER_RE.sub(replace, report_text)


def reference_line(number, source, mode):
    title = str(source.get("title") or "")
    url = str(source.get("url") or "")
    quality = str(source.get("quality") or "unknown")
    published_at = source.get("published_at")
    if published_at in (None, ""):
        published_at = "unknown"
    body = "%s — %s (%s, %s)" % (title, url, quality, published_at)
    if mode == "footnotes":
        return "[^%d]: %s" % (number, body)
    if mode == "legacy":
        return "[%d] %s" % (number, body)
    return '<a id="ref-%d"></a>[%d] %s [↩](#cite-%d)' % (
        number, number, body, number)


def build_sources_section(text, numbers, by_id, mode):
    """Replace everything after the ## Sources heading, or append the heading."""
    ordered = sorted(numbers.items(), key=lambda item: item[1])
    lines = [reference_line(number, by_id[source_id], mode)
             for source_id, number in ordered]
    block = "\n".join(lines)

    heading = SOURCES_HEADING_RE.search(text)
    if mode == "footnotes":
        # GFM footnote definitions render into the host's own footnotes block,
        # so the standalone ## Sources heading is dropped in this mode.
        base = (text[: heading.start()] if heading else text).rstrip("\n")
        if block:
            return base + "\n\n" + block + "\n"
        return base + "\n"

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


def observation_line(number, observation, mode):
    method = str(observation.get("method") or "")
    environment = observation.get("environment")
    if environment in (None, ""):
        environment = "unknown"
    captured_at = observation.get("captured_at")
    if captured_at in (None, ""):
        captured_at = "unknown"
    body = "%s — %s (captured %s)" % (method, environment, captured_at)
    if mode == "footnotes":
        return "[^o%d]: %s" % (number, body)
    if mode == "legacy":
        return "[O%d] %s" % (number, body)
    return '<a id="oref-%d"></a>[O%d] %s [↩](#ocite-%d)' % (
        number, number, body, number)


def build_observations_section(text, numbers, by_id, mode):
    """Append ## Observations, or rebuild the content after an existing one.

    Only called when at least one observation is cited. In ``footnotes`` mode
    the heading is dropped: the GFM renderer wires both marker families into
    one footnotes block.
    """
    ordered = sorted(numbers.items(), key=lambda item: item[1])
    lines = [
        observation_line(number, by_id[observation_id], mode)
        for observation_id, number in ordered
    ]
    block = "\n".join(lines)

    heading = OBSERVATIONS_HEADING_RE.search(text)
    if mode == "footnotes":
        base = (text[: heading.start()] if heading else text).rstrip("\n")
        if block:
            return base + "\n\n" + block + "\n"
        return base + "\n"

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


CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_SENTINEL = "\u0000"


def strip_markers(line, had_marker):
    """Delete every ``[^...]`` marker from one line and repair the spacing.

    Lines that carried no marker are returned untouched, so the clean copy is
    byte-identical to the draft everywhere the renderer did not act.
    """
    if not had_marker:
        return line
    text = MARKER_RE.sub(_SENTINEL, line)
    text = text.replace(_SENTINEL, "")
    # a marker glued between a word and its punctuation leaves "word ."
    text = re.sub(r" +(?=[,.;:!?…，。；：！？、）)】》\"'])", "", text)
    return re.sub(r"[ \t]+$", "", text)


def build_clean_copy(
    report_text, source_numbers, observation_numbers, by_id, obs_by_id,
    clean_path, cited_path,
):
    """Build the marker-free reading copy from the same numbers as the cited file."""
    lines = []
    for line in report_text.split("\n"):
        lines.append(strip_markers(line, MARKER_RE.search(line) is not None))
    body = "\n".join(lines)

    # Drop the renderer-owned tail (Sources and, if present, Observations).
    cuts = [
        match.start()
        for match in (SOURCES_HEADING_RE.search(body),
                      OBSERVATIONS_HEADING_RE.search(body))
        if match
    ]
    if cuts:
        body = body[: min(cuts)]
    body = body.rstrip("\n")

    is_cjk = bool(CJK_RE.search(body))
    if is_cjk:
        pointer = "> 引用标注版（含角标与出处）：[%s](%s)"
        sources_heading = "## 来源"
        observations_heading = "## 观测记录"
    else:
        pointer = "> Citation-annotated version with footnote markers: [%s](%s)"
        sources_heading = "## Sources"
        observations_heading = "## Observations"

    # The pointer must resolve from wherever the reading copy lives, so the
    # cited file can sit in .work/ while report.md stays at the top level.
    try:
        link = os.path.relpath(
            os.path.abspath(cited_path),
            start=os.path.dirname(os.path.abspath(clean_path)),
        )
    except ValueError:  # different drives on Windows
        link = os.path.abspath(cited_path)
    link = str(link).replace("\\", "/")
    parts = [pointer % (link, link), "", body, "", sources_heading, ""]

    ordered_sources = sorted(
        source_numbers.items(), key=lambda item: item[1])
    for source_id, _number in ordered_sources:
        source = by_id[source_id]
        title = str(source.get("title") or "")
        url = str(source.get("url") or "")
        quality = str(source.get("quality") or "unknown")
        published_at = source.get("published_at")
        if published_at in (None, ""):
            published_at = "unknown"
        parts.append("- %s — %s (%s, %s)" % (title, url, quality, published_at))

    if observation_numbers:
        parts += ["", observations_heading, ""]
        ordered_observations = sorted(
            observation_numbers.items(), key=lambda item: item[1])
        for observation_id, _number in ordered_observations:
            observation = obs_by_id[observation_id]
            method = str(observation.get("method") or "")
            environment = observation.get("environment")
            if environment in (None, ""):
                environment = "unknown"
            captured_at = observation.get("captured_at")
            if captured_at in (None, ""):
                captured_at = "unknown"
            # The reading copy is for the reader: state what was checked and
            # when, not the machine environment (that stays in the cited copy)
            # and never the word "captured" (content_review fails on it).
            parts.append("- %s (%s)" % (method, captured_at))

    return "\n".join(parts).rstrip("\n") + "\n"


def main(argv=None):
    args = build_parser().parse_args(argv)

    report_text = read_text(args.report, "report file")
    evidence = load_evidence(args.evidence)

    by_id, ordered_ids = index_by_id(evidence["sources"])
    obs_by_id, obs_ordered_ids = index_by_id(evidence["observations"])
    source_numbers, observation_numbers, orphans = assign_numbers(
        report_text, by_id, obs_by_id
    )
    mode = "legacy" if args.legacy_plain else (
        "anchor" if args.anchors else "footnotes")
    rendered = substitute_markers(
        report_text, source_numbers, observation_numbers, mode)
    rendered = build_sources_section(rendered, source_numbers, by_id, mode)
    if observation_numbers:
        rendered = build_observations_section(
            rendered, observation_numbers, obs_by_id, mode
        )

    if mode == "footnotes":
        # [^N] / [^N]: are expected in this mode, so a residual scan would be
        # meaningless. Fail instead on any marker whose id is empty after
        # strip() ([^] / [^ ]) — those are neither numbered nor substituted.
        blank = any(
            not match.group(1).strip() for match in MARKER_RE.finditer(rendered)
        )
        unresolved = bool(orphans) or blank
    else:
        # anchor/legacy mode: every substituted marker lost its ``[^`` prefix,
        # so any residual ``[^`` (blank or unresolved) is a failure.
        unresolved = MARKER_RE.search(rendered) is not None
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
    clean_path = None
    if args.clean_output:
        clean_text = build_clean_copy(
            report_text, source_numbers, observation_numbers,
            by_id, obs_by_id, args.clean_output, args.output,
        )
        write_text(args.clean_output, clean_text)
        clean_path = args.clean_output
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
            "clean_output": clean_path,
        }
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
