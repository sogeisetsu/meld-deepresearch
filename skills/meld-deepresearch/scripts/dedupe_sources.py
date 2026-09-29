#!/usr/bin/env python3
"""Normalize, de-duplicate and render evidence.json sources as sources.md.

Usage:
    python dedupe_sources.py --evidence <evidence.json> --output <sources.md>

URL normalization is applied strictly in this order:
  1. strip surrounding whitespace;
  2. lowercase the scheme and the host;
  3. drop the #fragment;
  4. drop tracking query params (utm_*, gclid, fbclid, ref, ref_src);
  5. drop default ports (:80 for http, :443 for https);
  6. drop a single trailing "/" from the path, but keep it when removing it
     would leave the path empty -- the root path "/" and an already empty
     path are both kept as they are.

The dedupe key is the normalized URL with its remaining query parameters
sorted, so parameter order never affects grouping. The scheme is only
lowercased, never rewritten, so http:// and https:// URLs never merge:
http://example.com/a and https://example.com/a stay two sources.

When several sources share a key they are merged into the first occurrence:
the table shows that occurrence's normalized URL (its query parameters keep
their original order -- sorting is used only for the dedupe key) with the
first occurrence's id kept as the canonical one, and the merged-in ids are
recorded in a note under the table. That note appears only when the
duplicate count is greater than zero. An unparseable URL never crashes the
run: the trimmed raw string becomes its dedupe key and a warning is
recorded.

sources.md is UTF-8 without BOM with LF line endings: a Markdown table with
columns id | title | quality | published_at | URL, sorted by quality
(primary -> secondary -> tertiary) and then by id (lexicographic).

stdout is a single ASCII-safe JSON object; the keys "ok", "sources" and
"duplicates_merged" are always present:
    {"ok": true, "sources": N, "duplicates_merged": M, "warnings": [...]}
    {"ok": false, "sources": 0, "duplicates_merged": 0, "error": "..."}

Exit codes:
    0  success (including runs that recorded URL warnings);
    1  evidence shape check failed (no sources[] array, or a source missing
       id/url);
    2  bad input (missing or unreadable file, invalid JSON, wrong usage, or
       an unwritable output file).
"""

import argparse
import json
import sys
import urllib.parse

TRACKING_PARAMS = frozenset({"gclid", "fbclid", "ref", "ref_src"})
TRACKING_PREFIX = "utm_"
DEFAULT_PORTS = {"http": "80", "https": "443"}
QUALITY_RANK = {"primary": 0, "secondary": 1, "tertiary": 2}
UNKNOWN_QUALITY_RANK = 3


class UsageError(Exception):
    """Raised by the argument parser so usage errors become JSON + exit 2."""


class _ArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that turns usage errors into UsageError instead of exit."""

    def error(self, message):
        raise UsageError(message)


def _lowercase_host(netloc):
    """Lowercase host and port; leave userinfo (before the last @) untouched."""
    if "@" in netloc:
        userinfo, hostport = netloc.rsplit("@", 1)
        return userinfo + "@" + hostport.lower()
    return netloc.lower()


def _drop_default_port(netloc, scheme):
    """Remove :80 from http URLs and :443 from https URLs; keep other ports."""
    default = DEFAULT_PORTS.get(scheme)
    if not netloc or default is None:
        return netloc
    if netloc.startswith("["):
        end = netloc.find("]")
        if end == -1:
            return netloc
        head, rest = netloc[: end + 1], netloc[end + 1:]
        if not rest.startswith(":"):
            return netloc
        port = rest[1:]
    elif ":" in netloc:
        head, port = netloc.rsplit(":", 1)
    else:
        return netloc
    if port == default:
        return head
    return netloc


def _drop_trailing_slash(path):
    """Drop a single trailing "/", never leaving the path empty (root kept)."""
    if len(path) > 1 and path.endswith("/"):
        return path[:-1]
    return path


def _drop_tracking_params(query):
    """Remove utm_*, gclid, fbclid, ref and ref_src query parameters."""
    if not query:
        return ""
    kept = []
    for pair in query.split("&"):
        if not pair:
            continue
        name = pair.split("=", 1)[0]
        if name.startswith(TRACKING_PREFIX) or name in TRACKING_PARAMS:
            continue
        kept.append(pair)
    return "&".join(kept)


def normalize_url(url):
    """Return the normalized form of ``url`` (rules in the module docstring)."""
    url = url.strip()                                   # 1. surrounding whitespace
    parts = urllib.parse.urlsplit(url)
    scheme = parts.scheme.lower()                       # 2a. lowercase scheme
    netloc = _lowercase_host(parts.netloc)              # 2b. lowercase host
    fragment = ""                                       # 3. drop the #fragment
    query = _drop_tracking_params(parts.query)          # 4. tracking params
    netloc = _drop_default_port(netloc, scheme)         # 5. default ports
    path = _drop_trailing_slash(parts.path)             # 6. trailing slash
    return urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))


def dedupe_key(url):
    """Dedupe key: normalized URL with its remaining query parameters sorted."""
    normalized = normalize_url(url)
    parts = urllib.parse.urlsplit(normalized)
    if not parts.query:
        return normalized
    pairs = sorted(pair for pair in parts.query.split("&") if pair)
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, parts.path, "&".join(pairs), "")
    )


def _quality_rank(source):
    quality = source.get("quality")
    if isinstance(quality, str):
        return QUALITY_RANK.get(quality, UNKNOWN_QUALITY_RANK)
    return UNKNOWN_QUALITY_RANK


def _cell(value):
    """Render one Markdown table cell (whitespace collapsed, pipes escaped)."""
    text = "unknown" if value is None else str(value)
    text = " ".join(text.split())
    return text.replace("|", "\\|")


def render_lines(records, duplicates):
    """Build sources.md as a list of lines (no trailing newlines)."""
    lines = [
        "| id | title | quality | published_at | URL |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in records:
        source = record["first"]
        lines.append("| {} | {} | {} | {} | {} |".format(
            _cell(source.get("id")),
            _cell(source.get("title")),
            _cell(source.get("quality")),
            _cell(source.get("published_at")),
            _cell(record["display"]),
        ))
    if duplicates > 0:
        pairs = []
        for record in records:
            survivor = record["first"]["id"]
            for merged_id in record["merged"]:
                pairs.append("{} -> {}".format(merged_id, survivor))
        noun = "duplicate" if duplicates == 1 else "duplicates"
        lines.append("")
        lines.append("_Merged {} {}: {}._".format(duplicates, noun, ", ".join(pairs)))
    return lines


def build_parser():
    parser = _ArgumentParser(
        prog="dedupe_sources.py",
        description="Normalize, de-duplicate evidence.json sources and write sources.md.",
    )
    parser.add_argument(
        "--evidence", required=True, metavar="<evidence.json>",
        help="evidence file to read (UTF-8; a BOM is tolerated)",
    )
    parser.add_argument(
        "--output", required=True, metavar="<sources.md>",
        help="Markdown table to write (UTF-8 without BOM, LF line endings)",
    )
    return parser


def emit(payload):
    sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")


def fail(message, code):
    emit({
        "ok": False,
        "sources": 0,
        "duplicates_merged": 0,
        "error": message,
    })
    return code


def main(argv=None):
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except UsageError as exc:
        return fail(str(exc), 2)

    try:
        with open(args.evidence, "r", encoding="utf-8-sig") as handle:
            raw = handle.read()
    except OSError as exc:
        return fail("cannot read evidence file: {}".format(exc), 2)

    try:
        data = json.loads(raw)
    except ValueError as exc:
        return fail("invalid JSON in evidence file: {}".format(exc), 2)

    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        return fail("evidence file has no sources[] array", 1)

    sources = data["sources"]
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            return fail("sources[{}] is not an object".format(index), 1)
        for field in ("id", "url"):
            value = source.get(field)
            if not isinstance(value, str) or not value.strip():
                return fail(
                    "sources[{}] is missing a non-empty '{}'".format(index, field), 1
                )

    records = []
    index_by_key = {}
    duplicates = 0
    warnings = []
    for index, source in enumerate(sources):
        try:
            display = normalize_url(source["url"])
            key = dedupe_key(display)
        except ValueError as exc:
            # A malformed URL must not crash the run: fall back to the
            # trimmed raw string as the key and record a warning.
            warnings.append(
                "sources[{}] ({}): unparseable URL ({}); keyed by the "
                "trimmed raw string".format(index, source["id"], exc)
            )
            display = source["url"].strip()
            key = display
        position = index_by_key.get(key)
        if position is None:
            index_by_key[key] = len(records)
            records.append({"first": source, "display": display, "merged": []})
        else:
            records[position]["merged"].append(source["id"])
            duplicates += 1

    records.sort(key=lambda record: (_quality_rank(record["first"]),
                                     record["first"]["id"]))

    text = "\n".join(render_lines(records, duplicates)) + "\n"
    try:
        with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    except OSError as exc:
        return fail("cannot write output file: {}".format(exc), 2)

    emit({
        "ok": True,
        "sources": len(records),
        "duplicates_merged": duplicates,
        "warnings": warnings,
    })
    return 0


if __name__ == "__main__":
    sys.exit(main())
