#!/usr/bin/env python3
"""Regression tests for public_safety_audit.py.

Proves:
1. Official GTM-53DPJ88F snippets / normal HTML / JS / Python do not fail the audit.
2. Representative exposed-secret patterns still fail.
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "scripts" / "public_safety_audit.py"


def _load_audit():
    spec = importlib.util.spec_from_file_location("public_safety_audit", AUDIT_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class PublicSafetyAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = _load_audit()

    def test_repo_with_gtm_passes(self) -> None:
        findings = self.audit.collect_findings(ROOT)
        self.assertEqual(
            findings,
            [],
            msg="Live site tree with GTM-53DPJ88F must PASS the public safety audit:\n"
            + "\n".join(findings),
        )

    def test_official_gtm_snippet_not_flagged_in_html(self) -> None:
        head = (ROOT / "includes" / "gtm-head.html").read_text(encoding="utf-8")
        body = (ROOT / "includes" / "gtm-body.html").read_text(encoding="utf-8")
        html = (
            "<!DOCTYPE html><html><head>\n"
            f"{head}"
            "</head><body>\n"
            f"{body}"
            "</body></html>\n"
        )
        findings = self.audit.scan_text(html, Path("index.html"))
        self.assertEqual(findings, [], msg="\n".join(findings))

    def test_python_and_html_false_positives_not_flagged(self) -> None:
        py = "ROOT = Path(__file__).resolve().parents[1]\nPAGES = [\n"
        jsish = "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=\n"
        html_attr = '<iframe height="0" width="0" style="display:none;visibility:hidden"></iframe>\n'
        for text, path in (
            (py, Path("scripts/example.py")),
            (jsish, Path("assets/js/site.js")),
            (html_attr, Path("index.html")),
        ):
            findings = self.audit.scan_text(text, path)
            self.assertEqual(findings, [], msg=f"{path}: {findings}")

    def test_named_secret_assignments_fail(self) -> None:
        samples = [
            "API_KEY=secret",
            "API_KEY = secret",
            'API_KEY="secret"',
            'API_KEY = "secret"',
            "api_key=secret",
            "client_secret = 'abc'",
            "ACCESS_TOKEN=shorttoken",
        ]
        for sample in samples:
            findings = self.audit.scan_text(sample + "\n", Path("index.html"))
            self.assertTrue(
                findings,
                msg=f"Expected FAIL for secret assignment in HTML context: {sample!r}",
            )

    def test_dotenv_context_flags_generic_assignments(self) -> None:
        text = "DATABASE_URL=postgres://user:pass@host/db\nFEATURE_FLAG=1\n"
        findings = self.audit.scan_text(text, Path(".env"))
        self.assertTrue(findings, msg="Dotenv file must flag KEY=value lines")
        # Same content in Python must NOT use dotenv rule (no named secret keys here)
        py_findings = self.audit.scan_text(text, Path("scripts/config_loader.py"))
        self.assertEqual(
            py_findings,
            [],
            msg="Generic KEY=value in Python must not use dotenv detector",
        )

    def test_bearer_aws_private_key_still_fail(self) -> None:
        samples = [
            ("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abcdef", Path("notes.txt")),
            ("AWS_KEY AKIAIOSFODNN7EXAMPLE leaked", Path("notes.txt")),
            ("-----BEGIN PRIVATE KEY-----\nMIIE\n", Path("notes.txt")),
            ("GOOGLE 123456789012-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com", Path("notes.txt")),
        ]
        for text, path in samples:
            findings = self.audit.scan_text(text, path)
            self.assertTrue(findings, msg=f"Expected FAIL for {text!r}")

    def test_dotenv_context_helper(self) -> None:
        self.assertTrue(self.audit.is_dotenv_context(Path(".env")))
        self.assertTrue(self.audit.is_dotenv_context(Path(".env.local")))
        self.assertTrue(self.audit.is_dotenv_context(Path("prod.env")))
        self.assertTrue(self.audit.is_dotenv_context(Path("env.example")))
        self.assertFalse(self.audit.is_dotenv_context(Path("index.html")))
        self.assertFalse(self.audit.is_dotenv_context(Path("scripts/sync_gtm_snippets.py")))
        self.assertFalse(self.audit.is_dotenv_context(Path("config/contact.example.json")))


if __name__ == "__main__":
    unittest.main()
