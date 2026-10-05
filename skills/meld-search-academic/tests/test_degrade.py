#!/usr/bin/env python3
"""Stdlib-only tests for graceful degradation when optional crawler deps are missing.

Run:
    python skills/meld-search-academic/tests/test_degrade.py

Covers, without network access and without playwright installed:
- crawler CLI entry points report {"ok": false, "degraded": true, ...} and exit 1
  instead of raising an unhandled exception or printing a traceback;
- the core entry points (search.py / paper.py / refTree.py) never require the
  optional crawler tier: with the core requirements installed they import, and
  in a dependency-free environment they exit with a clean "install
  requirements.txt" hint instead of an unhandled traceback;
- the requirements.txt / requirements-optional.txt split is real.

Exit code: 0 on success, 1 on failure.
"""

from __future__ import annotations

import contextlib
import importlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# Keep the working tree clean: never write __pycache__ during this test run.
sys.dont_write_bytecode = True

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Simulate "playwright is not installed" regardless of the host environment.
PLAYWRIGHT_ABSENT = {
    "playwright": None,
    "playwright.async_api": None,
    "playwright.sync_api": None,
}


def run_cli(module, argv):
    """Run module.main(argv) with playwright absent; return (exit_code, stdout)."""
    stdout = io.StringIO()
    with mock.patch.dict(sys.modules, PLAYWRIGHT_ABSENT), contextlib.redirect_stdout(stdout):
        code = module.main(argv)
    return code, stdout.getvalue()


class CrawlerDegradeTests(unittest.TestCase):
    def _assert_degraded_payload(self, code: int, stdout: str) -> dict:
        self.assertEqual(code, 1, f"expected exit code 1, got {code!r}; stdout={stdout!r}")
        lines = [line for line in stdout.splitlines() if line.strip()]
        self.assertEqual(len(lines), 1, f"expected a single-line JSON object, got {stdout!r}")
        payload = json.loads(lines[0])
        self.assertIsInstance(payload, dict)
        self.assertIs(payload.get("ok"), False)
        self.assertIs(payload.get("degraded"), True)
        self.assertTrue(payload.get("error"), "error must be a non-empty string")
        self.assertTrue(payload.get("fallback"), "fallback must be a non-empty string")
        return payload

    def test_arxiv_crawler_search_degrades_without_playwright(self):
        import arxiv_crawler_search as module

        with tempfile.TemporaryDirectory() as tmp:
            argv = ["--query", "qwen", "--output", str(Path(tmp) / "out.json")]
            code, stdout = run_cli(module, argv)
        payload = self._assert_degraded_payload(code, stdout)
        self.assertIn("playwright", payload["error"])

    def test_semantic_scholar_crawler_search_degrades_without_playwright(self):
        import semantic_scholar_crawler_search as module

        with tempfile.TemporaryDirectory() as tmp:
            argv = ["--query", "qwen", "--output", str(Path(tmp) / "out.json")]
            code, stdout = run_cli(module, argv)
        self._assert_degraded_payload(code, stdout)

    def test_semantic_scholar_crawler_reftree_degrades_without_playwright(self):
        import semantic_scholar_crawler_refTree as module

        with tempfile.TemporaryDirectory() as tmp:
            argv = ["--title", "Qwen Technical Report", "--output", str(Path(tmp) / "out.json")]
            code, stdout = run_cli(module, argv)
        self._assert_degraded_payload(code, stdout)

    def test_crawler_modules_import_without_playwright(self):
        with mock.patch.dict(sys.modules, PLAYWRIGHT_ABSENT):
            for name in (
                "arxiv_crawler_search",
                "semantic_scholar_crawler_search",
                "semantic_scholar_crawler_refTree",
            ):
                sys.modules.pop(name, None)
                module = importlib.import_module(name)
                self.assertTrue(hasattr(module, "create_page"), name)


class CoreEntryPointImportTests(unittest.TestCase):
    def test_core_entry_points_import_without_playwright(self):
        expected_attr = {
            "search": "search",
            "paper": "read_paper",
            "refTree": "ref_tree",
        }
        # The entry points depend on the declared CORE requirements (httpx,
        # arxiv, ...) but never on the optional crawler tier. A job that
        # installs nothing -- the zero-dependency core CI job -- therefore sees
        # the documented degradation: one clean SystemExit carrying the
        # "install requirements.txt" hint, never an unhandled traceback. With
        # the core requirements present, the same modules must import.
        core_deps_present = importlib.util.find_spec("httpx") is not None
        with mock.patch.dict(sys.modules, PLAYWRIGHT_ABSENT):
            for name in ("search", "paper", "refTree"):
                sys.modules.pop(name, None)
                if not core_deps_present:
                    with self.assertRaises(SystemExit, msg=name) as caught:
                        importlib.import_module(name)
                    self.assertIn(
                        "requirements.txt",
                        str(caught.exception),
                        f"{name}.py must fail with the install hint when the "
                        "core requirements are absent, not a traceback",
                    )
                    continue
                module = importlib.import_module(name)
                self.assertTrue(
                    hasattr(module, expected_attr[name]),
                    f"{name}.py must import without playwright and expose {expected_attr[name]}",
                )


class RequirementsSplitTests(unittest.TestCase):
    def test_requirements_split_is_real(self):
        core = (SKILL_DIR / "requirements.txt").read_text(encoding="utf-8")
        optional = (SKILL_DIR / "requirements-optional.txt").read_text(encoding="utf-8")
        self.assertNotIn(
            "playwright",
            core,
            "requirements.txt must be the core (always-installable) list without playwright",
        )
        self.assertIn(
            "playwright",
            optional,
            "requirements-optional.txt must declare playwright for the crawler tier",
        )
        for package in ("httpx", "arxiv", "beautifulsoup4", "semanticscholar", "pypdf", "deepxiv-sdk"):
            self.assertIn(package, core, f"core requirement missing: {package}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
