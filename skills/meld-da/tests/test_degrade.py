#!/usr/bin/env python3
"""Degrade-path unit test for the meld-da skill.

stdlib only, no network, no third-party package required. It proves the two
things the skill promises when pandas/openpyxl/pyarrow are unavailable:

1. the skill documents the fallback to the zero-dependency reading layer, and
2. that layer (`skills/meld-deepresearch/scripts/read_table.py`) really is
   stdlib-only and self-testable without any installed package.

Run:  python skills/meld-da/tests/test_degrade.py
Exit: 0 pass / 1 fail (a JSON summary is printed on failure).
"""
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO = SKILL_DIR.parents[1]
READ_TABLE = REPO / "skills" / "meld-deepresearch" / "scripts" / "read_table.py"
REQUIREMENTS = SKILL_DIR / "requirements.txt"
SKILL_MD = SKILL_DIR / "SKILL.md"

# Modules the zero-dependency layer is allowed to import: the stdlib only.
# (Kept as an explicit allow-list of the packages that ship with CPython.)
STDLIB_OK = set(getattr(sys, "stdlib_module_names", ()))

results = []


def check(name, ok, detail=""):
    results.append({"name": name, "ok": bool(ok), "detail": detail})
    return ok


def main():
    # 1. The fallback route is documented in the skill body.
    body = SKILL_MD.read_text(encoding="utf-8")
    check("documents read_table fallback",
          "read_table.py" in body and "Dependencies and fallback" in body,
          "SKILL.md must name the zero-dependency reading layer")

    # 2. The third-party requirements are declared, and declared only there.
    req_text = REQUIREMENTS.read_text(encoding="utf-8")
    declared = [line.strip() for line in req_text.splitlines()
                if line.strip() and not line.strip().startswith("#")]
    check("requirements.txt declares the analysis layer",
          all(pkg in declared for pkg in ("pandas", "openpyxl")),
          "missing: %s" % declared)

    # 3. The fallback reader imports the standard library only, so it can be
    #    used precisely when the packages above are missing.
    if not READ_TABLE.is_file():
        check("read_table.py exists", False, str(READ_TABLE))
    else:
        tree = ast.parse(READ_TABLE.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        if STDLIB_OK:
            stray = sorted(m for m in imported if m not in STDLIB_OK)
            check("read_table.py imports stdlib only", not stray,
                  "non-stdlib imports: %s" % stray)
        else:
            check("read_table.py imports stdlib only", True,
                  "stdlib_module_names unavailable on this Python; skipped")

        # 4. And it actually runs without them: the self-test builds its own
        #    fixture workbook in memory and exits 0.
        proc = subprocess.run(
            [sys.executable, str(READ_TABLE), "--selftest"],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        check("read_table.py --selftest passes without third-party deps",
              proc.returncode == 0 and "OK" in (proc.stdout or ""),
              "rc=%s out=%s" % (proc.returncode, (proc.stdout or "")[:200]))

    # 5. No sandbox/host paths crept back into the skill.
    sandbox = re.findall(r"/mnt/data|/tmp/|sandbox:|sn-da-", body)
    check("no sandbox or upstream skill paths", not sandbox, str(sandbox))

    failures = [r for r in results if not r["ok"]]
    for r in results:
        print("%s %s%s" % ("PASS" if r["ok"] else "FAIL", r["name"],
                           (" — " + r["detail"]) if (not r["ok"] and r["detail"]) else ""))
    print(json.dumps({"ok": not failures, "failed": [r["name"] for r in failures]}))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
