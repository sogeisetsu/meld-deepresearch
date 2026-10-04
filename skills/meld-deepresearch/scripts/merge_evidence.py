#!/usr/bin/env python3
"""Merge per-axis evidence subreports into one evidence.json.

Usage:
    python merge_evidence.py --subreports <dir> --output <evidence.json>

Reads every ``*.evidence.json`` in ``--subreports`` (sorted by filename), then
merges the six contract arrays: ``sources``, ``observations``, ``claims``,
``writing_context``, ``key_findings`` and ``gaps``.

Merge rules
-----------
* Sources are folded by normalized URL (the same normalization
  ``dedupe_sources.py`` uses). The first occurrence keeps its (possibly
  re-keyed) id; later occurrences of the same URL are dropped and every
  reference to their id — in ``claims[].evidence[].source_id``,
  ``writing_context[].source_ids[]`` and ``gaps[].source_ids[]`` — is
  repointed at the surviving id.
* Any id that would collide across subreports but is NOT the same URL is
  re-keyed to the next free id in its family, and references inside that
  subreport are repointed too.
* Observation ids, writing-context ids and gap ids are likewise made unique.
* Claim ids are assumed globally unique (``dN.cM``); a collision is reported
  as a warning and the claim is still kept.

The output preserves contract key order and is UTF-8 without BOM. stdout is
one ASCII-safe JSON object:
    {"ok": bool, "sources": N, "observations": N, "claims": N,
     "subreports": N, "warnings": [...]}

Exit codes:
    0  merged (warnings possible)
    1  a subreport is not a JSON object, or the directory has no
       ``*.evidence.json`` files
    2  bad input (missing/unreadable file, invalid JSON, wrong usage)

Python 3 standard library only; no network access.
"""

import argparse
import copy
import glob
import json
import os
import re
import sys

try:  # the sibling script ships next to this one
    from dedupe_sources import dedupe_key
except Exception:  # pragma: no cover - fallback if imported oddly
    def dedupe_key(url):
        return (url or "").strip().lower()

# Writing-context ids must keep the contract shape ``dN.wM`` (see
# evidence-contract.md); a collision is re-keyed inside that family, never to a
# bare ``cN`` that the validator would reject.
CONTEXT_ID_RE = re.compile(r"^(d\d+)\.w\d+$")


def emit(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=True) + "\n")


def fail(message, code):
    emit({"ok": False, "error": message})
    raise SystemExit(code)


def next_id(prefix, used):
    index = 1
    while "%s%d" % (prefix, index) in used:
        index += 1
    return "%s%d" % (prefix, index)


def next_context_id(context_id, used):
    """Next free ``dN.wM`` id in ``context_id``'s own axis family.

    Keeps the contract pattern when the incoming id already matches ``dN.wM``;
    a malformed id falls back to the ``d0`` family so the merged file still
    validates with ``check_evidence.py`` instead of carrying a bare ``cN``.
    """
    match = CONTEXT_ID_RE.match(context_id)
    axis = match.group(1) if match else "d0"
    index = 1
    while "%s.w%d" % (axis, index) in used:
        index += 1
    return "%s.w%d" % (axis, index)


def _deep(obj):
    return copy.deepcopy(obj)


def merge_docs(docs):
    """Merge a list of (name, doc) pairs; return (merged, warnings)."""
    sources = []
    url_to_id = {}
    used_sources = set()

    observations = []
    used_observations = set()

    claims = []
    claim_ids = set()

    contexts = []
    used_contexts = set()

    findings = []

    gaps = []
    used_gaps = set()

    warnings = []

    for name, doc in docs:
        if not isinstance(doc, dict):
            warnings.append("%s is not a JSON object; skipped" % name)
            continue

        source_map = {}
        for source in doc.get("sources") or []:
            if not isinstance(source, dict):
                continue
            source_id = source.get("id")
            url = source.get("url")
            if not isinstance(source_id, str) or not isinstance(url, str):
                continue
            key = dedupe_key(url)
            if key in url_to_id:
                source_map[source_id] = url_to_id[key]
                continue
            new_id = source_id if source_id not in used_sources else next_id(
                "s", used_sources)
            used_sources.add(new_id)
            url_to_id[key] = new_id
            merged = _deep(source)
            merged["id"] = new_id
            sources.append(merged)
            source_map[source_id] = new_id

        observation_map = {}
        for observation in doc.get("observations") or []:
            if not isinstance(observation, dict):
                continue
            observation_id = observation.get("id")
            if not isinstance(observation_id, str):
                continue
            new_id = observation_id if observation_id not in used_observations \
                else next_id("o", used_observations)
            used_observations.add(new_id)
            merged = _deep(observation)
            merged["id"] = new_id
            observations.append(merged)
            observation_map[observation_id] = new_id

        for claim in doc.get("claims") or []:
            if not isinstance(claim, dict):
                continue
            merged = _deep(claim)
            claim_id = merged.get("id")
            if isinstance(claim_id, str):
                if claim_id in claim_ids:
                    warnings.append(
                        "duplicate claim id %r (%s); kept but references may "
                        "be ambiguous" % (claim_id, name))
                claim_ids.add(claim_id)
            for item in merged.get("evidence") or []:
                if not isinstance(item, dict):
                    continue
                source_id = item.get("source_id")
                if isinstance(source_id, str) and source_id in source_map:
                    item["source_id"] = source_map[source_id]
                observation_id = item.get("observation_id")
                if isinstance(observation_id, str) and \
                        observation_id in observation_map:
                    item["observation_id"] = observation_map[observation_id]
            claims.append(merged)

        for context in doc.get("writing_context") or []:
            if not isinstance(context, dict):
                continue
            merged = _deep(context)
            context_id = merged.get("id")
            if isinstance(context_id, str):
                new_id = context_id if context_id not in used_contexts \
                    else next_context_id(context_id, used_contexts)
                used_contexts.add(new_id)
                merged["id"] = new_id
            if isinstance(merged.get("source_ids"), list):
                merged["source_ids"] = [
                    source_map.get(item, item)
                    for item in merged["source_ids"]
                ]
            contexts.append(merged)

        for finding in doc.get("key_findings") or []:
            if isinstance(finding, dict):
                findings.append(_deep(finding))

        for gap in doc.get("gaps") or []:
            if not isinstance(gap, dict):
                continue
            merged = _deep(gap)
            gap_id = merged.get("id")
            if isinstance(gap_id, str):
                new_id = gap_id if gap_id not in used_gaps else next_id(
                    "g", used_gaps)
                used_gaps.add(new_id)
                merged["id"] = new_id
            if isinstance(merged.get("source_ids"), list):
                merged["source_ids"] = [
                    source_map.get(item, item)
                    for item in merged["source_ids"]
                ]
            gaps.append(merged)

    result = {
        "claims": claims,
        "sources": sources,
        "writing_context": contexts,
        "key_findings": findings,
    }
    if observations:
        result["observations"] = observations
    if gaps:
        result["gaps"] = gaps
    return result, warnings


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        emit({"ok": False, "error": message})
        raise SystemExit(2)


def build_parser():
    parser = _Parser(
        prog="merge_evidence.py",
        description="Merge per-axis evidence subreports into one evidence.json.",
    )
    parser.add_argument(
        "--subreports", required=True, metavar="<dir>",
        help="directory containing *.evidence.json subreports")
    parser.add_argument(
        "--output", required=True, metavar="<evidence.json>",
        help="merged evidence.json to write")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    if not os.path.isdir(args.subreports):
        fail("subreports directory not found: %s" % args.subreports, 2)
    paths = sorted(glob.glob(os.path.join(args.subreports, "*.evidence.json")))
    if not paths:
        fail("no *.evidence.json files in %s" % args.subreports, 1)

    docs = []
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8-sig") as handle:
                raw = handle.read()
        except OSError as exc:
            fail("cannot read %s: %s" % (path, exc), 2)
            raise SystemExit(2)
        try:
            data = json.loads(raw)
        except ValueError as exc:
            fail("invalid JSON in %s: %s" % (path, exc), 2)
            raise SystemExit(2)
        if not isinstance(data, dict):
            fail("subreport %s is not a JSON object" % os.path.basename(path), 1)
        docs.append((os.path.basename(path), data))

    merged, warnings = merge_docs(docs)

    try:
        directory = os.path.dirname(os.path.abspath(args.output))
        os.makedirs(directory, exist_ok=True)
        with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(merged, ensure_ascii=False, indent=2) + "\n")
    except OSError as exc:
        fail("cannot write %s: %s" % (args.output, exc), 2)

    emit({
        "ok": True,
        "sources": len(merged["sources"]),
        "observations": len(merged.get("observations", [])),
        "claims": len(merged["claims"]),
        "subreports": len(docs),
        "warnings": warnings,
    })
    return 0


if __name__ == "__main__":
    sys.exit(main())
