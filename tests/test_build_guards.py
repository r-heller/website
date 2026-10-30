import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
class BuildGuards(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.site = Path(self.tmp.name) / 'site'
    def run_guard(self, name):
        return subprocess.run(['sh', str(ROOT / 'scripts' / name), str(self.site)], capture_output=True, text=True)
    def page(self, name, content='<!doctype html><title>Reviewed fixture</title>'):
        p = self.site / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    def legal_site(self):
        for name in ['index.html', 'impressum/index.html', 'privacy/index.html']:
            self.page(name)
    def test_missing_output_is_not_a_pass(self):
        self.assertNotEqual(self.run_guard('check-legal-placeholders.sh').returncode, 0)
        self.site.mkdir()
        self.assertNotEqual(self.run_guard('check-legal-placeholders.sh').returncode, 0)
    def test_legal_pages_must_exist(self):
        self.page('index.html')
        self.assertNotEqual(self.run_guard('check-legal-placeholders.sh').returncode, 0)
    def test_current_legal_routes_and_generic_tokens_are_checked(self):
        self.legal_site()
        self.assertEqual(self.run_guard('check-legal-placeholders.sh').returncode, 0)
        for text in ['{{UNEXPECTED_CONTACT}}', 'TODO: review this', 'FIXME']:
            self.page('privacy/index.html', text)
            with self.subTest(text=text):
                self.assertNotEqual(self.run_guard('check-legal-placeholders.sh').returncode, 0)
    def test_empty_script_directory_is_not_a_pass(self):
        (self.site / 'js/overview').mkdir(parents=True)
        self.assertNotEqual(self.run_guard('check-overview-budget.sh').returncode, 0)
        self.page('js/overview/graph.js', 'console.log("synthetic");')
        self.assertEqual(self.run_guard('check-overview-budget.sh').returncode, 0)
