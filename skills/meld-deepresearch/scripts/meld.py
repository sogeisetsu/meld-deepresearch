#!/usr/bin/env python3
"""Thin CLI over the meld-deepresearch evidence/report scripts.

Usage:
    python meld.py prepare  --outdir OUT [--tier {quick,normal}]
    python meld.py render   --outdir OUT
    python meld.py review   --outdir OUT [--clean]
    python meld.py sources  --outdir OUT
    python meld.py verify   --outdir OUT [--tier {quick,normal}]
    python meld.py table    [ARGS...]    # passed verbatim to read_table.py

Every artifact path derives from the single --outdir value:
    OUT/evidence.json  OUT/report.md  OUT/sources.md  OUT/citations.json
    OUT/.work/{plan.json, report.src.md, report.cited.md, sub_reports/}

The CLI only removes mechanical errors (wrong flags, files, order); it never
changes the sibling scripts' assertions.  meld.py's own messages are JSON on
stdout, as are the scripts' outputs, which pass through untouched.
Exit codes: 0 pass, 1 fail, 2 bad input.
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
COMMANDS = ("prepare", "render", "review", "sources", "verify", "table")


def emit(payload):
    """Print one JSON line on stdout."""
    sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")


def die(message):
    """Report bad usage as JSON on stdout and exit 2."""
    emit({"ok": False, "error": message})
    raise SystemExit(2)


def paths_for(outdir):
    """Derive every artifact path from --outdir."""
    out = Path(outdir)
    work = out / ".work"
    return {
        "evidence": out / "evidence.json",
        "report": out / "report.md",
        "sources": out / "sources.md",
        "citations": out / "citations.json",
        "plan": work / "plan.json",
        "src": work / "report.src.md",
        "cited": work / "report.cited.md",
        "subreports": work / "sub_reports",
    }


def run_script(name, args):
    """Run one sibling script with this interpreter; return its exit code."""
    done = subprocess.run([sys.executable, str(SCRIPTS / name),
                           *[str(a) for a in args]])
    return done.returncode


def plan_args(paths, tier):
    """Return (check_evidence --plan argv, error or None) for the tier.

    quick forces the plan off, normal requires it, default is auto: the
    presence of OUT/.work/plan.json alone decides.
    """
    if tier == "quick":
        return [], None
    if paths["plan"].is_file():
        return ["--plan", str(paths["plan"])], None
    if tier == "normal":
        return [], "--tier normal requires {}".format(paths["plan"])
    return [], None


def stage_prepare(paths, tier):
    """Merge per-axis subreports (when present), then gate the evidence."""
    plan, error = plan_args(paths, tier)
    if error:
        emit({"ok": False, "error": error})
        return 2
    sub = paths["subreports"]
    if sub.is_dir() and any(sub.glob("*.evidence.json")):
        code = run_script("merge_evidence.py",
                          ["--subreports", str(sub),
                           "--output", str(paths["evidence"])])
        if code:
            return code
    return run_script("check_evidence.py", [str(paths["evidence"]), *plan])


def stage_render(paths):
    """Render markers into the cited copy, reading copy and citations.json."""
    return run_script("render_citations.py", [
        "--report", str(paths["src"]),
        "--evidence", str(paths["evidence"]),
        "--output", str(paths["cited"]),
        "--clean-output", str(paths["report"]),
        "--citations", str(paths["citations"]),
    ])


def stage_review(paths, clean=False):
    """Review the cited copy, or with --clean gate the reading copy."""
    if clean:
        return run_script("content_review.py", [
            "--report", str(paths["report"]), "--clean",
            "--evidence", str(paths["evidence"]),
        ])
    return run_script("content_review.py", [
        "--report", str(paths["cited"]),
        "--evidence", str(paths["evidence"]),
    ])


def stage_sources(paths):
    """De-duplicate evidence sources into sources.md."""
    return run_script("dedupe_sources.py", [
        "--evidence", str(paths["evidence"]),
        "--output", str(paths["sources"]),
    ])


def parse_args(rest, allow_tier=False, allow_clean=False):
    """Parse --outdir (always required) plus the flags this command allows."""
    opts = {"outdir": None, "tier": None, "clean": False}
    index = 0
    while index < len(rest):
        token = rest[index]
        name, sep, inline = token.partition("=")
        index += 1
        if name in ("--outdir", "--tier") and sep:
            value = inline
        elif name in ("--outdir", "--tier"):
            if index >= len(rest):
                die("{} needs a value".format(name))
            value = rest[index]
            index += 1
        else:
            value = None
        if name == "--outdir":
            opts["outdir"] = value
        elif name == "--tier":
            if not allow_tier:
                die("unknown argument: {}".format(token))
            if value not in ("quick", "normal"):
                die("--tier must be quick or normal, got {!r}".format(value))
            opts["tier"] = value
        elif name == "--clean" and allow_clean and not sep:
            opts["clean"] = True
        else:
            die("unknown argument: {}".format(token))
    if not opts["outdir"]:
        die("--outdir is required for this subcommand")
    return opts


def main(argv):
    if not argv:
        die("usage: meld.py prepare|render|review|sources|verify|table ...")
    command, rest = argv[0], argv[1:]
    if command == "table":
        # Documented exception: read_table.py takes its own positional path
        # and flags, so every remaining argument is forwarded verbatim.
        return run_script("read_table.py", rest)
    if command not in COMMANDS:
        die("unknown subcommand: {}".format(command))
    opts = parse_args(rest, allow_tier=command in ("prepare", "verify"),
                      allow_clean=command == "review")
    paths = paths_for(opts["outdir"])
    if command == "prepare":
        return stage_prepare(paths, opts["tier"])
    if command == "render":
        return stage_render(paths)
    if command == "review":
        return stage_review(paths, opts["clean"])
    if command == "sources":
        return stage_sources(paths)
    stages = (
        ("prepare", lambda: stage_prepare(paths, opts["tier"])),
        ("render", lambda: stage_render(paths)),
        ("review", lambda: stage_review(paths)),
        ("review --clean", lambda: stage_review(paths, clean=True)),
    )
    for name, stage in stages:
        code = stage()
        if code:
            emit({"ok": False, "stage": name, "exit": code})
            return code
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
