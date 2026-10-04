#!/usr/bin/env python3
"""Validate an evidence.json file against the meld-deepresearch evidence contract.

Usage
-----
    python  check_evidence.py <evidence.json> [--plan <plan.json>]
    python3 check_evidence.py <evidence.json> [--plan <plan.json>]

Output
------
stdout receives exactly one JSON object:

    {"ok": bool, "errors": [...], "warnings": [...]}

Every entry is {"code": "...", "message": "...", "where": "...", "hint": "..."}
where ``where`` is a JSON-path-like locator such as
``claims[2].evidence[0].source_id`` or ``sources[1]``, and ``hint`` is an
optional "smallest safe fix" suggestion, present only when one clear corrective
action exists (absent otherwise). Both lists are sorted by code then by
``where``, so CI output is stable across runs. ``ok`` is true only when
``errors`` is empty; warnings never flip it.

``hint`` is deliberately separate from ``message`` so the machine contract stays
stable: a consumer that keys on ``code``/``where`` keeps working, and a model
that has to repair a run reads ``hint`` for the one fix that most likely clears
the error without dropping a claim it did not need to drop.

Exit codes
----------
    0   validation passed (ok: true; warnings may still be present)
    1   validation failed (ok: false)
    2   bad input: missing or unreadable file, invalid JSON, wrong CLI usage.
        Reported as {"ok": false, "errors": [{"code": "E_JSON", ...}]}.

Error codes
-----------
E_JSON (always exit 2, including CLI usage errors) / E_SHAPE / E_ID_PATTERN /
E_ID_UNIQUE / E_ENUM / E_REF_SOURCE / E_REF_OBSERVATION / E_REF_CLAIM /
E_REF_KQ / E_FACTUAL_SOURCE / E_INTERPRETIVE_TWO / E_PROJECTIVE_BASIS /
E_BACKGROUND_BASIS / E_FINDING_BACKGROUND / E_OBS_SHAPE / E_EMPTY /
E_GAP_SHAPE / E_GAP_ENUM / E_GAP_REF / E_PLAN_DIM_UNKNOWN /
E_PLAN_DIM_UNCOVERED.

Optional schema additions (all backward-compatible; an old evidence.json with
none of these still validates):
    claims[].kind            may also be ``background`` (context that needs
                             >=1 evidence item of any quality, is exempt from
                             E_FACTUAL_SOURCE, need not answer a kqN, and may
                             not back a key_finding).
    sources[].source_type    optional label: official | academic | archive |
                             press | oral | community | mixed. A label only —
                             it never changes the ``credible`` threshold.
    gaps[]                   optional top-level array of
                             {id (gN), text, reason, cost, source_ids[]}.
    plan.json genre          panorama | comparison | entity | chronicle |
                             general (checked only with --plan).
    plan dimensions[].must_have_materials[]
                             [{text, status (obtained|missing|unknown), note?}].

Warning codes
-------------
W_NORMATIVE / W_NO_FINDINGS / W_NO_REFUTE / W_KQ_UNANSWERED / W_SAME_PUBLISHER
(warnings keep ok: true).

Normative detection (W_NORMATIVE) is a documented best-effort heuristic: the
claim's ``text`` is lowercased and matched word-boundary / case-insensitively
against this fixed phrase list, which mirrors evidence-contract.md rule 4 byte
for byte: "should", "ought to", "we recommend", "is recommended",
"are recommended", "best practice", "advisable", "must adopt". It is a WARNING
only: the list cannot tell a descriptive paraphrase ("the docs recommend X")
from a prescription, and a heuristic must not consume a run's single fix
chance.

Standard library only: no third-party imports, no network, no shell calls, no
temporary files. Reads UTF-8 (a BOM is tolerated) and prints ASCII-safe JSON.
"""

import argparse
import json
import re
import sys

CLAIM_ID_RE = re.compile(r"^d\d+\.c\d+$")
CONTEXT_ID_RE = re.compile(r"^d\d+\.w\d+$")
APPLIES_TO_RE = re.compile(r"^d\d+(?:\.c\d+)?$")
KEY_QUESTION_RE = re.compile(r"^kq\d+$")
# oN: 1-based, no leading zeros (so neither "o0" nor "o01" is accepted).
OBSERVATION_ID_RE = re.compile(r"^o[1-9][0-9]*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[Tt ].+$")
# F3: reachability is NOT machine-checked; only the absolute http(s) shape is.
URL_RE = re.compile(r"^https?://\S+$")

KINDS = ("factual", "interpretive", "projective", "background")
POLARITIES = ("support", "refute", "neutral")
QUOTE_TYPES = ("direct", "paraphrase", "numeric")
QUALITIES = ("primary", "secondary", "tertiary")
CREDIBLE_QUALITIES = ("primary", "secondary")
OBSERVATION_KINDS = ("command", "measurement", "file", "inspection")
# Optional source label (plan §3.6): a label only, never a pass/fail input.
SOURCE_TYPES = ("official", "academic", "archive", "press", "oral",
                "community", "mixed")
# Structured gaps[] (plan §3.5).
GAP_REASONS = ("no-source", "access-limited", "budget", "stale", "other")
GAP_COSTS = ("cheap", "hard")
GAP_ID_RE = re.compile(r"^g[1-9][0-9]*$")
# plan.json additions (plan §3.3 / §3.7), checked only under --plan.
PLAN_GENRES = ("panorama", "comparison", "entity", "chronicle", "general")
MUST_HAVE_STATUSES = ("obtained", "missing", "unknown")

TOP_LEVEL_KEYS = ("claims", "sources", "writing_context", "key_findings")
# observations[] is optional: a file without first-hand evidence simply omits
# it (or passes an empty array), and that is not an error.
OPTIONAL_TOP_LEVEL_KEYS = ("observations", "gaps")
NON_EMPTY_KEYS = ("claims", "sources")
SOURCE_KEYS = ("id", "url", "title", "quality", "published_at")
CLAIM_KEYS = ("id", "text", "kind", "polarity", "topic_tag",
              "answers_key_question", "evidence")
EVIDENCE_KEYS = ("snippet", "quote_type")
CONTEXT_KEYS = ("id", "kind", "text", "source_ids", "applies_to", "use")
FINDING_KEYS = ("finding", "claim_ids")
OBSERVATION_KEYS = ("id", "kind", "method", "command", "captured_at",
                    "environment", "snippet")

# F6: fixed phrase list for the "no normative claims" heuristic. Keep this in
# sync with evidence-contract.md rule 4 — word boundaries, case folded first.
# C5: the list stays pinned and unchanged, but a hit is now a WARNING only.
NORMATIVE_PHRASES = (
    "should",
    "ought to",
    "we recommend",
    "is recommended",
    "are recommended",
    "best practice",
    "advisable",
    "must adopt",
)
NORMATIVE_RE = re.compile(r"\b(?:%s)\b" % "|".join(
    re.escape(phrase) for phrase in NORMATIVE_PHRASES))


def _domain_root(url):
    """Best-effort publisher root for a URL: host minus leading 'www.'.

    Used only for the W_SAME_PUBLISHER heuristic — never for pass/fail. Two
    urls on the same host (with or without 'www.') share a root; a shared root
    for several sources that prop up one interpretive claim is a hint that they
    may be one publisher, not independent origins. This is deliberately coarse:
    it cannot tell a wire story re-published across outlets from genuinely
    independent reporting, so it only ever warns.
    """
    match = re.match(r"^https?://([^/]+)", url.strip(), re.IGNORECASE)
    if not match:
        return None
    host = match.group(1).lower().split("@")[-1].split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    return host or None


def _entry(code, message, where, hint=None):
    entry = {"code": code, "message": message, "where": where}
    if hint:
        entry["hint"] = hint
    return entry


def _emit(ok, errors, warnings):
    """Print exactly one ASCII-safe JSON object on stdout."""
    errors = sorted(errors, key=lambda item: (item["code"], item["where"]))
    warnings = sorted(warnings, key=lambda item: (item["code"], item["where"]))
    payload = {"ok": ok, "errors": errors, "warnings": warnings}
    sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")
    sys.stdout.flush()


def _fail_input(message, where="$"):
    """Bad input: report E_JSON and exit 2."""
    _emit(False, [_entry("E_JSON", message, where)], [])
    raise SystemExit(2)


def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            text = handle.read()
    except (OSError, UnicodeError) as exc:
        _fail_input("cannot read %s: %s" % (path, exc), where=path)
        raise SystemExit(2)  # unreachable; _fail_input always raises
    try:
        return json.loads(text)
    except ValueError as exc:
        _fail_input("invalid JSON in %s: %s" % (path, exc), where=path)
        raise SystemExit(2)  # unreachable; _fail_input always raises


def _non_empty(value):
    return isinstance(value, str) and value.strip() != ""


def _check_keys(obj, keys, where, errors):
    for key in keys:
        if key not in obj:
            errors.append(_entry(
                "E_SHAPE", "missing required field '%s'" % key,
                "%s.%s" % (where, key)))


def _validate_sources(doc, errors):
    """Validate sources[]; return {source_id: {"quality", "url"}} metadata."""
    meta = {}
    sources = doc.get("sources")
    if not isinstance(sources, list):
        return meta
    seen = set()
    for index, source in enumerate(sources):
        where = "sources[%d]" % index
        if not isinstance(source, dict):
            errors.append(_entry("E_SHAPE", "source must be an object", where))
            continue
        _check_keys(source, SOURCE_KEYS, where, errors)
        source_id = source.get("id")
        if "id" in source:
            if not _non_empty(source_id):
                errors.append(_entry(
                    "E_SHAPE", "'id' must be a non-empty string",
                    where + ".id"))
            else:
                if source_id in seen:
                    errors.append(_entry(
                        "E_ID_UNIQUE", "duplicate source id '%s'" % source_id,
                        where + ".id"))
                seen.add(source_id)
                meta[source_id] = {
                    "quality": source.get("quality"),
                    "url": source.get("url"),
                }
        # F3: only the absolute http(s) shape is checked; reachability is not.
        if "url" in source:
            url = source.get("url")
            if not (isinstance(url, str) and URL_RE.match(url.strip())):
                errors.append(_entry(
                    "E_SHAPE",
                    "'url' must be a well-formed absolute http(s) URL "
                    "(reachability is not machine-checked)",
                    where + ".url"))
        if "title" in source and not _non_empty(source.get("title")):
            errors.append(_entry(
                "E_SHAPE", "'title' must be a non-empty string",
                where + ".title"))
        if "quality" in source:
            quality = source.get("quality")
            if quality not in QUALITIES:
                errors.append(_entry(
                    "E_ENUM",
                    "'quality' must be one of %s" % "|".join(QUALITIES),
                    where + ".quality"))
        if "source_type" in source:
            source_type = source.get("source_type")
            if source_type is not None and source_type not in SOURCE_TYPES:
                errors.append(_entry(
                    "E_ENUM",
                    "'source_type' must be null or one of %s"
                    % "|".join(SOURCE_TYPES),
                    where + ".source_type"))
        if "published_at" in source:
            published = source.get("published_at")
            if published is not None and not (
                    isinstance(published, str)
                    and (DATE_RE.match(published) or DATETIME_RE.match(published))):
                errors.append(_entry(
                    "E_SHAPE",
                    "'published_at' must be an ISO date (YYYY-MM-DD) or null",
                    where + ".published_at"))
    return meta


def _validate_observations(doc, errors):
    """Validate the optional observations[] array.

    Returns the set of well-formed observation ids that claims may cite.
    Every structural problem here is reported as E_OBS_SHAPE (including a
    duplicate or badly patterned id), except an unknown ``kind`` value, which
    is an enum violation like everywhere else (E_ENUM).
    """
    ids = set()
    if "observations" not in doc:
        return ids
    observations = doc.get("observations")
    if not isinstance(observations, list):
        # validate() already reported the top-level shape error.
        return ids
    seen = set()
    for index, observation in enumerate(observations):
        where = "observations[%d]" % index
        if not isinstance(observation, dict):
            errors.append(_entry(
                "E_OBS_SHAPE", "observation must be an object", where))
            continue
        for key in OBSERVATION_KEYS:
            if key not in observation:
                errors.append(_entry(
                    "E_OBS_SHAPE", "missing required field '%s'" % key,
                    "%s.%s" % (where, key)))

        observation_id = observation.get("id")
        if "id" in observation:
            if not _non_empty(observation_id):
                errors.append(_entry(
                    "E_OBS_SHAPE", "'id' must be a non-empty string",
                    where + ".id"))
            elif not OBSERVATION_ID_RE.match(observation_id):
                errors.append(_entry(
                    "E_OBS_SHAPE",
                    "'id' must match oN (1-based, no leading zeros), "
                    "e.g. o1 or o12", where + ".id"))
            elif observation_id in seen:
                errors.append(_entry(
                    "E_OBS_SHAPE",
                    "duplicate observation id '%s'" % observation_id,
                    where + ".id"))
            else:
                seen.add(observation_id)
                ids.add(observation_id)

        if "kind" in observation and observation.get("kind") not in \
                OBSERVATION_KINDS:
            errors.append(_entry(
                "E_ENUM",
                "'kind' must be one of %s" % "|".join(OBSERVATION_KINDS),
                where + ".kind"))

        for field in ("method", "snippet"):
            if field in observation and not _non_empty(observation.get(field)):
                errors.append(_entry(
                    "E_OBS_SHAPE",
                    "'%s' must be a non-empty string" % field,
                    "%s.%s" % (where, field)))

        if "captured_at" in observation:
            captured = observation.get("captured_at")
            if not (isinstance(captured, str) and DATE_RE.match(captured)):
                errors.append(_entry(
                    "E_OBS_SHAPE",
                    "'captured_at' must be a YYYY-MM-DD date",
                    where + ".captured_at"))

        if "environment" in observation:
            environment = observation.get("environment")
            if environment is not None and not isinstance(environment, str):
                errors.append(_entry(
                    "E_OBS_SHAPE",
                    "'environment' must be a string or null",
                    where + ".environment"))

        if "command" in observation:
            command = observation.get("command")
            if command is not None and not isinstance(command, str):
                errors.append(_entry(
                    "E_OBS_SHAPE", "'command' must be a string or null",
                    where + ".command"))
            elif observation.get("kind") == "command" and (
                    not isinstance(command, str) or not command.strip()):
                errors.append(_entry(
                    "E_OBS_SHAPE",
                    "'command' must be a non-empty string when kind is "
                    "'command'", where + ".command"))
    return ids


def _validate_evidence(claim_where, evidence, source_meta, observation_ids,
                       errors):
    """Validate claims[].evidence[].

    Each item points at exactly one origin: ``source_id`` XOR
    ``observation_id``. Returns
    ``(evidence_ok, distinct_source_ids, distinct_source_urls,
    distinct_observation_ids, credible, distinct_domains)``; only entries that
    resolve are counted. ``distinct_domains`` is the set of publisher roots
    (``_domain_root``) behind the resolving sources, used only by the
    W_SAME_PUBLISHER heuristic.
    """
    distinct_ids = set()
    distinct_urls = set()
    distinct_obs = set()
    distinct_domains = set()
    credible = False
    if not isinstance(evidence, list):
        errors.append(_entry(
            "E_SHAPE", "'evidence' must be an array", claim_where + ".evidence"))
        return (False, distinct_ids, distinct_urls, distinct_obs, credible,
                distinct_domains)
    for index, item in enumerate(evidence):
        where = "%s.evidence[%d]" % (claim_where, index)
        if not isinstance(item, dict):
            errors.append(_entry("E_SHAPE", "evidence item must be an object",
                                 where))
            continue
        _check_keys(item, EVIDENCE_KEYS, where, errors)

        # Exactly one origin: a JSON null counts as "not filled in".
        has_source = "source_id" in item and item.get("source_id") is not None
        has_observation = ("observation_id" in item
                           and item.get("observation_id") is not None)
        if has_source == has_observation:
            errors.append(_entry(
                "E_SHAPE",
                "evidence item must carry exactly one of 'source_id' or "
                "'observation_id' (both filled in or neither is an error)",
                where))

        if has_source:
            source_id = item.get("source_id")
            if not _non_empty(source_id):
                errors.append(_entry(
                    "E_SHAPE", "'source_id' must be a non-empty string",
                    where + ".source_id"))
            elif source_id not in source_meta:
                errors.append(_entry(
                    "E_REF_SOURCE",
                    "source_id '%s' does not resolve to an entry in sources[]"
                    % source_id, where + ".source_id",
                    hint="smallest safe fix: point source_id at an id that "
                         "exists in sources[], or add the missing source entry, "
                         "or remove this evidence item."))
            else:
                distinct_ids.add(source_id)
                record = source_meta[source_id]
                if record.get("quality") in CREDIBLE_QUALITIES:
                    credible = True
                url = record.get("url")
                if isinstance(url, str) and url.strip():
                    distinct_urls.add(url.strip())
                    domain = _domain_root(url)
                    if domain:
                        distinct_domains.add(domain)

        if has_observation:
            observation_id = item.get("observation_id")
            if not _non_empty(observation_id):
                errors.append(_entry(
                    "E_SHAPE",
                    "'observation_id' must be a non-empty string",
                    where + ".observation_id"))
            elif observation_id not in observation_ids:
                errors.append(_entry(
                    "E_REF_OBSERVATION",
                    "observation_id '%s' does not resolve to an entry in "
                    "observations[]" % observation_id,
                    where + ".observation_id",
                    hint="smallest safe fix: point observation_id at an id that "
                         "exists in observations[], or add the missing "
                         "observation entry, or remove this evidence item."))
            else:
                distinct_obs.add(observation_id)

        if "snippet" in item and not _non_empty(item.get("snippet")):
            errors.append(_entry(
                "E_SHAPE", "'snippet' must be a non-empty string",
                where + ".snippet"))
        if "quote_type" in item:
            quote_type = item.get("quote_type")
            if quote_type not in QUOTE_TYPES:
                errors.append(_entry(
                    "E_ENUM",
                    "'quote_type' must be one of %s" % "|".join(QUOTE_TYPES),
                    where + ".quote_type"))
    return (True, distinct_ids, distinct_urls, distinct_obs, credible,
            distinct_domains)


def _validate_claims(doc, source_meta, observation_ids, errors, warnings):
    """Validate claims[].

    Returns ``(claim_ids, axes, answered_kqs, has_refute, background_ids)``.
    """
    claim_ids = set()
    seen = set()
    axes = []
    answered = set()
    has_refute = False
    background_ids = set()

    claims = doc.get("claims")
    if not isinstance(claims, list):
        return claim_ids, axes, answered, has_refute, background_ids

    for index, claim in enumerate(claims):
        where = "claims[%d]" % index
        if not isinstance(claim, dict):
            errors.append(_entry("E_SHAPE", "claim must be an object", where))
            continue
        _check_keys(claim, CLAIM_KEYS, where, errors)

        claim_id = claim.get("id")
        if "id" in claim:
            if not _non_empty(claim_id):
                errors.append(_entry(
                    "E_SHAPE", "'id' must be a non-empty string",
                    where + ".id"))
            elif not CLAIM_ID_RE.match(claim_id):
                errors.append(_entry(
                    "E_ID_PATTERN",
                    "'id' must match dN.cM (e.g. d1.c2)", where + ".id"))
            else:
                if claim_id in seen:
                    errors.append(_entry(
                        "E_ID_UNIQUE", "duplicate claim id '%s'" % claim_id,
                        where + ".id"))
                seen.add(claim_id)
                claim_ids.add(claim_id)
                axes.append((index, claim_id.split(".")[0]))
                if claim.get("kind") == "background":
                    background_ids.add(claim_id)

        text = claim.get("text")
        if "text" in claim and not _non_empty(text):
            errors.append(_entry(
                "E_SHAPE", "'text' must be a non-empty string",
                where + ".text"))
        if "topic_tag" in claim and not _non_empty(claim.get("topic_tag")):
            errors.append(_entry(
                "E_SHAPE", "'topic_tag' must be a non-empty string",
                where + ".topic_tag"))

        kind = claim.get("kind")
        if "kind" in claim and kind not in KINDS:
            errors.append(_entry(
                "E_ENUM", "'kind' must be one of %s" % "|".join(KINDS),
                where + ".kind"))

        polarity = claim.get("polarity")
        if "polarity" in claim:
            if polarity not in POLARITIES:
                errors.append(_entry(
                    "E_ENUM",
                    "'polarity' must be one of %s" % "|".join(POLARITIES),
                    where + ".polarity"))
            elif polarity == "refute":
                has_refute = True

        if "answers_key_question" in claim:
            key_question = claim.get("answers_key_question")
            if key_question is not None:
                if not (isinstance(key_question, str)
                        and KEY_QUESTION_RE.match(key_question)):
                    errors.append(_entry(
                        "E_REF_KQ",
                        "'answers_key_question' must be null or match kqN",
                        where + ".answers_key_question"))
                else:
                    answered.add(key_question)

        evidence_ok = False
        distinct_ids = set()
        distinct_urls = set()
        distinct_obs = set()
        distinct_domains = set()
        credible = False
        if "evidence" in claim:
            (evidence_ok, distinct_ids, distinct_urls, distinct_obs,
             credible, distinct_domains) = _validate_evidence(
                 where, claim.get("evidence"), source_meta, observation_ids,
                 errors)

        # An observation is first-hand evidence, so it satisfies `factual` on
        # its own; `interpretive` counts distinct origins, and one origin is
        # either a source (identified by its url) or an observation.
        origin_count = len(distinct_urls) + len(distinct_obs)

        if kind == "factual" and evidence_ok and not credible and not \
                distinct_obs:
            errors.append(_entry(
                "E_FACTUAL_SOURCE",
                "factual claim needs at least one evidence item backed by a "
                "primary or secondary source, or by an observation", where,
                hint="smallest safe fix: either change this claim's kind to "
                     "'interpretive' (if it is really a reading of the sources) "
                     "or add one evidence item resolving to a 'primary' or "
                     "'secondary' source, or record the fact as an observation. "
                     "Do not keep a 'factual' claim resting only on 'tertiary' "
                     "sources."))
        elif kind == "projective" and evidence_ok:
            evidence = claim.get("evidence")
            if not isinstance(evidence, list) or len(evidence) < 1:
                errors.append(_entry(
                    "E_PROJECTIVE_BASIS",
                    "projective claim needs at least one evidence item "
                    "recording its basis", where,
                    hint="smallest safe fix: add at least one evidence item "
                         "(any quality tier) showing what the projection is "
                         "based on, or drop the projection."))
        elif kind == "background" and evidence_ok:
            evidence = claim.get("evidence")
            if not isinstance(evidence, list) or len(evidence) < 1:
                errors.append(_entry(
                    "E_BACKGROUND_BASIS",
                    "background claim needs at least one evidence item "
                    "(any quality tier, or an observation)", where,
                    hint="smallest safe fix: add at least one evidence item "
                         "sourced from a source or observation, or drop the "
                         "background claim."))
        elif kind == "interpretive" and evidence_ok:
            # F5: two distinct origins — a source_id with its own url, or an
            # observation_id.
            if origin_count < 2:
                errors.append(_entry(
                    "E_INTERPRETIVE_TWO",
                    "interpretive claim needs at least two distinct origins "
                    "(distinct source_id with a distinct url, or distinct "
                    "observation_id); found %d distinct source_id(s) resolving "
                    "to %d distinct url(s) and %d distinct observation(s)" % (
                        len(distinct_ids), len(distinct_urls),
                        len(distinct_obs)),
                    where,
                    hint="smallest safe fix: add one more evidence item from a "
                         "DIFFERENT origin — a source whose url differs from "
                         "every url already cited here, or an observation_id. "
                         "Two ids sharing one url do not count as two origins, "
                         "and re-publishing the same url under a new id does "
                         "not help."))
            elif origin_count >= 2 and len(distinct_domains) == 1 and \
                    len(distinct_urls) >= 2:
                # Two or more distinct urls prop up the claim, but they all sit
                # on one publisher root — often one wire story re-published.
                # This is a heuristic, so it only ever warns.
                warnings.append(_entry(
                    "W_SAME_PUBLISHER",
                    "interpretive claim rests on %d distinct url(s) that all "
                    "share one publisher root ('%s'); they may be one outlet "
                    "restating one story, not independent origins"
                    % (len(distinct_urls), sorted(distinct_domains)[0]),
                    where))

        if isinstance(text, str):
            match = NORMATIVE_RE.search(text.lower())
            if match:
                # C5: a warning, never an error — the phrase list cannot tell
                # a descriptive paraphrase from a prescription.
                warnings.append(_entry(
                    "W_NORMATIVE",
                    "claim text reads as normative (matched %r); state what "
                    "the evidence shows, not what anyone should do"
                    % match.group(0), where))

    return claim_ids, axes, answered, has_refute, background_ids


def _validate_writing_context(doc, source_ids, errors):
    contexts = doc.get("writing_context")
    if not isinstance(contexts, list):
        return
    seen = set()
    for index, context in enumerate(contexts):
        where = "writing_context[%d]" % index
        if not isinstance(context, dict):
            errors.append(_entry("E_SHAPE", "writing context must be an object",
                                 where))
            continue
        _check_keys(context, CONTEXT_KEYS, where, errors)

        context_id = context.get("id")
        if "id" in context:
            if not _non_empty(context_id):
                errors.append(_entry(
                    "E_SHAPE", "'id' must be a non-empty string",
                    where + ".id"))
            elif not CONTEXT_ID_RE.match(context_id):
                errors.append(_entry(
                    "E_ID_PATTERN",
                    "'id' must match dN.wM (e.g. d1.w1)", where + ".id"))
            else:
                if context_id in seen:
                    errors.append(_entry(
                        "E_ID_UNIQUE",
                        "duplicate writing context id '%s'" % context_id,
                        where + ".id"))
                seen.add(context_id)

        for field in ("kind", "text", "use"):
            if field in context and not _non_empty(context.get(field)):
                errors.append(_entry(
                    "E_SHAPE", "'%s' must be a non-empty string" % field,
                    "%s.%s" % (where, field)))

        if "source_ids" in context:
            source_ids_value = context.get("source_ids")
            if not isinstance(source_ids_value, list):
                errors.append(_entry(
                    "E_SHAPE", "'source_ids' must be an array",
                    where + ".source_ids"))
            else:
                for offset, item in enumerate(source_ids_value):
                    item_where = "%s.source_ids[%d]" % (where, offset)
                    if not _non_empty(item):
                        errors.append(_entry(
                            "E_SHAPE",
                            "source id must be a non-empty string", item_where))
                    elif item not in source_ids:
                        errors.append(_entry(
                            "E_REF_SOURCE",
                            "source_id '%s' does not resolve to an entry in "
                            "sources[]" % item, item_where))

        if "applies_to" in context:
            applies_to = context.get("applies_to")
            if not isinstance(applies_to, list):
                errors.append(_entry(
                    "E_SHAPE", "'applies_to' must be an array",
                    where + ".applies_to"))
            else:
                for offset, item in enumerate(applies_to):
                    item_where = "%s.applies_to[%d]" % (where, offset)
                    if not _non_empty(item):
                        errors.append(_entry(
                            "E_SHAPE",
                            "applies_to entry must be a non-empty string",
                            item_where))
                    elif not APPLIES_TO_RE.match(item):
                        errors.append(_entry(
                            "E_ID_PATTERN",
                            "applies_to entry must be dN or dN.cM", item_where))


def _validate_key_findings(doc, claim_ids, background_ids, errors):
    findings = doc.get("key_findings")
    if not isinstance(findings, list):
        return
    for index, finding in enumerate(findings):
        where = "key_findings[%d]" % index
        if not isinstance(finding, dict):
            errors.append(_entry("E_SHAPE", "key finding must be an object",
                                 where))
            continue
        _check_keys(finding, FINDING_KEYS, where, errors)
        if "finding" in finding and not _non_empty(finding.get("finding")):
            errors.append(_entry(
                "E_SHAPE", "'finding' must be a non-empty string",
                where + ".finding"))
        if "claim_ids" in finding:
            referenced = finding.get("claim_ids")
            if not isinstance(referenced, list):
                errors.append(_entry(
                    "E_SHAPE", "'claim_ids' must be an array",
                    where + ".claim_ids"))
                continue
            if len(referenced) < 1:
                errors.append(_entry(
                    "E_SHAPE",
                    "'claim_ids' must reference at least one claim",
                    where + ".claim_ids"))
                continue
            for offset, item in enumerate(referenced):
                item_where = "%s.claim_ids[%d]" % (where, offset)
                if not _non_empty(item):
                    errors.append(_entry(
                        "E_SHAPE", "claim id must be a non-empty string",
                        item_where))
                elif item in background_ids:
                    errors.append(_entry(
                        "E_FINDING_BACKGROUND",
                        "claim id '%s' is a 'background' claim and may not "
                        "back a key finding" % item, item_where,
                        hint="smallest safe fix: reference a non-background "
                             "claim, or promote the background claim to a "
                             "factual/interpretive finding if it is load-"
                             "bearing."))
                elif item not in claim_ids:
                    errors.append(_entry(
                        "E_REF_CLAIM",
                        "claim id '%s' does not resolve to a claim in this "
                        "file" % item, item_where,
                        hint="smallest safe fix: reference a claim id that "
                             "exists, or drop this entry from claim_ids[]."))


def _validate_gaps(doc, source_ids, errors):
    """Validate the optional top-level gaps[] array (plan §3.5)."""
    gaps = doc.get("gaps")
    if gaps is None:
        return
    if not isinstance(gaps, list):
        # validate() already reports the top-level shape error.
        return
    seen = set()
    for index, gap in enumerate(gaps):
        where = "gaps[%d]" % index
        if not isinstance(gap, dict):
            errors.append(_entry("E_GAP_SHAPE", "gap must be an object", where))
            continue
        for key in ("id", "text", "reason", "cost"):
            if key not in gap:
                errors.append(_entry(
                    "E_GAP_SHAPE", "missing required field '%s'" % key,
                    "%s.%s" % (where, key)))

        gap_id = gap.get("id")
        if "id" in gap:
            if not _non_empty(gap_id):
                errors.append(_entry(
                    "E_GAP_SHAPE", "'id' must be a non-empty string",
                    where + ".id"))
            elif not GAP_ID_RE.match(gap_id):
                errors.append(_entry(
                    "E_GAP_SHAPE",
                    "'id' must match gN (1-based, no leading zeros), e.g. g1",
                    where + ".id"))
            elif gap_id in seen:
                errors.append(_entry(
                    "E_GAP_SHAPE", "duplicate gap id '%s'" % gap_id,
                    where + ".id"))
            else:
                seen.add(gap_id)

        if "text" in gap and not _non_empty(gap.get("text")):
            errors.append(_entry(
                "E_GAP_SHAPE", "'text' must be a non-empty string",
                where + ".text"))
        if "reason" in gap and gap.get("reason") not in GAP_REASONS:
            errors.append(_entry(
                "E_GAP_ENUM", "'reason' must be one of %s"
                % "|".join(GAP_REASONS), where + ".reason"))
        if "cost" in gap and gap.get("cost") not in GAP_COSTS:
            errors.append(_entry(
                "E_GAP_ENUM", "'cost' must be one of %s" % "|".join(GAP_COSTS),
                where + ".cost"))
        if "source_ids" in gap:
            value = gap.get("source_ids")
            if not isinstance(value, list):
                errors.append(_entry(
                    "E_GAP_SHAPE", "'source_ids' must be an array",
                    where + ".source_ids"))
            else:
                for offset, item in enumerate(value):
                    item_where = "%s.source_ids[%d]" % (where, offset)
                    if not _non_empty(item):
                        errors.append(_entry(
                            "E_GAP_SHAPE",
                            "source id must be a non-empty string", item_where))
                    elif item not in source_ids:
                        errors.append(_entry(
                            "E_GAP_REF",
                            "source_id '%s' does not resolve to an entry in "
                            "sources[]" % item, item_where))


def _cross_check_plan(plan, axes, answered, errors, warnings):
    if not isinstance(plan, dict):
        errors.append(_entry("E_SHAPE", "plan must be a JSON object", "$"))
        return
    dimensions = plan.get("dimensions")
    if not isinstance(dimensions, list):
        errors.append(_entry(
            "E_SHAPE", "plan must contain a 'dimensions' array", "dimensions"))
        return
    if "genre" in plan and plan.get("genre") is not None and \
            plan.get("genre") not in PLAN_GENRES:
        errors.append(_entry(
            "E_ENUM", "plan 'genre' must be one of %s"
            % "|".join(PLAN_GENRES), "genre"))

    dimension_ids = []
    key_questions = []
    for index, dimension in enumerate(dimensions):
        where = "dimensions[%d]" % index
        if not isinstance(dimension, dict):
            errors.append(_entry("E_SHAPE", "dimension must be an object",
                                 where))
            continue
        dimension_id = dimension.get("id")
        if not _non_empty(dimension_id):
            errors.append(_entry(
                "E_SHAPE", "dimension 'id' must be a non-empty string",
                where + ".id"))
        else:
            dimension_ids.append(dimension_id)
        if "key_questions" in dimension:
            questions = dimension.get("key_questions")
            if not isinstance(questions, list):
                errors.append(_entry(
                    "E_SHAPE", "'key_questions' must be an array",
                    where + ".key_questions"))
                continue
            for offset, question in enumerate(questions):
                question_where = "%s.key_questions[%d]" % (where, offset)
                if not isinstance(question, dict):
                    errors.append(_entry(
                        "E_SHAPE", "key question must be an object",
                        question_where))
                    continue
                question_id = question.get("id")
                if not _non_empty(question_id):
                    errors.append(_entry(
                        "E_SHAPE",
                        "key question 'id' must be a non-empty string",
                        question_where + ".id"))
                else:
                    key_questions.append((question_where, question_id))

        if "must_have_materials" in dimension:
            materials = dimension.get("must_have_materials")
            if not isinstance(materials, list):
                errors.append(_entry(
                    "E_SHAPE", "'must_have_materials' must be an array",
                    where + ".must_have_materials"))
            else:
                for offset, material in enumerate(materials):
                    material_where = "%s.must_have_materials[%d]" % (
                        where, offset)
                    if not isinstance(material, dict):
                        errors.append(_entry(
                            "E_SHAPE", "must-have material must be an object",
                            material_where))
                        continue
                    if not _non_empty(material.get("text")):
                        errors.append(_entry(
                            "E_SHAPE", "'text' must be a non-empty string",
                            material_where + ".text"))
                    if "status" in material and material.get("status") not in \
                            MUST_HAVE_STATUSES:
                        errors.append(_entry(
                            "E_ENUM", "'status' must be one of %s"
                            % "|".join(MUST_HAVE_STATUSES),
                            material_where + ".status"))

    declared = set(dimension_ids)
    for claim_index, axis in axes:
        if axis not in declared:
            errors.append(_entry(
                "E_PLAN_DIM_UNKNOWN",
                "claim axis '%s' is not a dimension declared by the plan"
                % axis, "claims[%d].id" % claim_index,
                hint="smallest safe fix: either add dimension '%s' to the "
                     "plan's dimensions[], or re-key this claim under a "
                     "declared dimension." % axis))

    covered = set(axis for _, axis in axes)
    for index, dimension_id in enumerate(dimension_ids):
        if dimension_id not in covered:
            errors.append(_entry(
                "E_PLAN_DIM_UNCOVERED",
                "plan dimension '%s' has no claim in this file" % dimension_id,
                "dimensions[%d]" % index,
                hint="smallest safe fix: add at least one claim under dimension "
                     "'%s', or remove it from the plan if the scope was "
                     "deliberately dropped (and say so in the coverage note)."
                     % dimension_id))

    for question_where, question_id in key_questions:
        if question_id not in answered:
            warnings.append(_entry(
                "W_KQ_UNANSWERED",
                "plan key question '%s' is not answered by any claim"
                % question_id, question_where))


def validate(doc, plan):
    errors = []
    warnings = []

    if not isinstance(doc, dict):
        errors.append(_entry("E_SHAPE", "top level must be a JSON object", "$"))
        return errors, warnings

    for key in TOP_LEVEL_KEYS:
        if key not in doc:
            errors.append(_entry(
                "E_SHAPE", "missing required top-level array '%s'" % key, key))
        elif not isinstance(doc[key], list):
            errors.append(_entry(
                "E_SHAPE", "'%s' must be an array" % key, key))
    # observations[] is optional, but when present it must be an array.
    for key in OPTIONAL_TOP_LEVEL_KEYS:
        if key in doc and not isinstance(doc[key], list):
            errors.append(_entry(
                "E_SHAPE", "'%s' must be an array" % key, key))

    # F2: claims[] and sources[] must be non-empty; key_findings[] may be
    # empty but that is reported as a warning only. writing_context[] may be
    # legitimately empty.
    for key in NON_EMPTY_KEYS:
        value = doc.get(key)
        if isinstance(value, list) and len(value) == 0:
            errors.append(_entry(
                "E_EMPTY",
                "'%s' must contain at least one entry" % key, key))
    findings = doc.get("key_findings")
    if isinstance(findings, list) and len(findings) == 0:
        warnings.append(_entry(
            "W_NO_FINDINGS",
            "no key_findings recorded; the report has no derived synthesis",
            "key_findings"))

    source_meta = _validate_sources(doc, errors)
    observation_ids = _validate_observations(doc, errors)
    claim_ids, axes, answered, has_refute, background_ids = _validate_claims(
        doc, source_meta, observation_ids, errors, warnings)
    _validate_writing_context(doc, set(source_meta), errors)
    _validate_key_findings(doc, claim_ids, background_ids, errors)
    _validate_gaps(doc, set(source_meta), errors)

    if not has_refute:
        warnings.append(_entry(
            "W_NO_REFUTE",
            "no claim has polarity 'refute'; active falsification was probably "
            "not attempted", "claims"))

    if plan is not None:
        _cross_check_plan(plan, axes, answered, errors, warnings)

    return errors, warnings


class _ArgumentParser(argparse.ArgumentParser):
    """argparse that reports bad CLI usage as JSON on stdout and exits 2."""

    def error(self, message):
        _fail_input("bad command-line usage: %s" % message, where="$")


def _build_parser():
    parser = _ArgumentParser(
        prog="check_evidence.py",
        description="Validate evidence.json against the meld-deepresearch "
                    "evidence contract.")
    parser.add_argument(
        "evidence", metavar="EVIDENCE_JSON",
        help="path to the evidence.json file to validate")
    parser.add_argument(
        "--plan", metavar="PLAN_JSON", default=None,
        help="optional plan.json: cross-check claim axes, plan dimensions and "
             "declared key questions")
    return parser


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    doc = _load_json(args.evidence)
    plan = _load_json(args.plan) if args.plan is not None else None

    errors, warnings = validate(doc, plan)
    ok = not errors
    _emit(ok, errors, warnings)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
