#!/usr/bin/env python3
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.dont_write_bytecode = True

spec = importlib.util.spec_from_file_location('stack', Path(__file__).with_name('stack-section.py'))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


class StackTests(unittest.TestCase):
    def setUp(self):
        self.text = (s.ROOT / 'data/stack-table.md').read_text()
        self.rows = s.components(self.text)
        self.document = '<p>preserve</p>' + s.START + '\n' + s.render(self.rows) + '\n    ' + s.END + '<p>after</p>'

    def test_current_site_is_exact_canonical_render(self):
        s.check_source(s.ROOT)
        page = (s.ROOT / 'index.html').read_text()
        self.assertEqual(page, s.update_document(page, self.rows))

    def test_omission_and_wrong_link_detected_without_changing_other_content(self):
        for old, new in [(s.render(self.rows[:1]), ''), (self.rows[0][1], 'https://github.com/wrong/target')]:
            candidate = self.document.replace(old, new, 1)
            self.assertNotEqual(candidate, s.update_document(candidate, self.rows))
        self.assertEqual(self.document, s.update_document(self.document, self.rows))
        self.assertTrue(s.update_document(self.document, self.rows).startswith('<p>preserve</p>'))

    def test_missing_duplicate_and_bad_row_refused(self):
        line = next(line for line in self.text.splitlines() if '| [tambo]' in line)
        for candidate in [self.text.replace(line, ''), self.text.replace(line, line+'\n'+line),
                          self.text.replace('https://github.com/scbrown/tambo', 'javascript:bad'),
                          self.text.replace('<!-- stack-table:start -->', '')]:
            with self.assertRaises(ValueError):
                s.components(candidate)

    def test_corrupt_source_or_missing_immutable_ref_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'data').mkdir()
            (root/'data/stack-table.md').write_text(self.text)
            pin = dict(repository='scbrown/tambo', path='docs/stack-table.md', commit='a'*40,
                       sha256=hashlib.sha256(self.text.encode()).hexdigest())
            (root/'data/stack-source.json').write_text(json.dumps(pin))
            self.assertEqual(s.check_source(root), self.rows)
            for key,value in [('sha256', '0'*64), ('commit', 'main'), ('repository','other/repo')]:
                bad = dict(pin);bad[key]=value
                (root/'data/stack-source.json').write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    s.check_source(root)

    def test_html_text_escaped(self):
        self.assertIn('a &amp; b', s.render([('fixture', 'https://github.com/example/fixture', 'a & b')]))


if __name__ == '__main__':
    unittest.main()
