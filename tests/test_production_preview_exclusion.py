"""The production page build must not contain the founder preview banner."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.build_production_site import FORBIDDEN_IN_PRODUCTION, PREVIEW_SOURCES, build

ROOT = Path(__file__).resolve().parents[1]


class ProductionPreviewExclusionTests(unittest.TestCase):
    def test_preview_source_keeps_fenced_banner(self) -> None:
        for relative in PREVIEW_SOURCES:
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("preview-only:start", text)
            self.assertIn("preview-only:end", text)

    def test_production_build_has_no_preview_banner_code(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            written = build(Path(directory))
            self.assertEqual(len(written), 3)
            combined = "\n".join(path.read_text(encoding="utf-8") for path in written)
            for phrase in FORBIDDEN_IN_PRODUCTION:
                self.assertNotIn(phrase, combined)
            self.assertNotIn("founder review", combined.lower())
            self.assertIn("Growth intelligence and optimization.", combined)
            self.assertIn("GTM-53DPJ88F", combined)
            self.assertIn("capability-list--five", combined)


if __name__ == "__main__":
    unittest.main()
