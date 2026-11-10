import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("software_meta", ROOT / "scripts" / "update_software_meta.py")
meta = importlib.util.module_from_spec(spec)
spec.loader.exec_module(meta)


class SoftwareMeta(unittest.TestCase):
    def test_every_card_with_github_link_is_mapped(self):
        repos = meta.catalogue()
        text = (ROOT / "data" / "software.yml").read_text(encoding="utf-8")
        linked = text.count('repo: "https://github.com/')
        self.assertEqual(len(repos), linked)
        self.assertEqual(repos["synesthR"], "r-heller/synesthR")
        self.assertTrue(all("/" in r and not r.endswith(".git") for r in repos.values()))

    def test_snapshot_only_lists_catalogue_entries(self):
        import json
        snapshot = json.loads((ROOT / "data" / "software_meta.json").read_text(encoding="utf-8"))
        self.assertTrue(set(snapshot) <= set(meta.catalogue()))
        for entry in snapshot.values():
            self.assertRegex(entry.get("updated", "2000-01-01"), r"^\d{4}-\d{2}-\d{2}$")


if __name__ == "__main__":
    unittest.main()
