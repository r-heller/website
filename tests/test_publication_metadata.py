import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('overview', ROOT / 'scripts/build_overview_graph.py')
overview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(overview)

class PublicationMetadata(unittest.TestCase):
    def test_citation_status_and_entities_survive_graph_parsing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'publications.md'
            path.write_text('''## 2026
<div class="publication-item">
<span class="pub-authors">A Author, <b>R Heller</b>.</span>
<span class="pub-title"><a href="https://doi.org/10.1234/example">Copper &amp; calcium</a>.</span>
<span class="pub-journal"><b><i>Research Square</i></b>. 2026.</span>
<span class="pub-status">Preprint</span>
</div>''')
            publication = overview.parse_publications(path)[0]
            self.assertEqual(publication['title'], 'Copper & calcium')
            self.assertEqual(publication['authors'], 'A Author, R Heller.')
            self.assertEqual(publication['citation'], 'Research Square. 2026.')
            self.assertEqual(publication['publication_status'], 'Preprint')

    def test_publication_dois_are_unique(self):
        publications = overview.parse_publications(ROOT / 'content/publications.md')
        dois = [p['doi'].lower() for p in publications]
        self.assertEqual(len(dois), len(set(dois)))
