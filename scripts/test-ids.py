"""Offline format, identity, corruption and omission controls for committed IDs."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from rdflib import Graph
from rdflib.compare import isomorphic

spec = importlib.util.spec_from_file_location('ids',Path(__file__).with_name('build-ids.py'))
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class PublicationTests(unittest.TestCase):
    def test_reproducible_and_equivalent(self):
        outputs = builder.build()
        self.assertEqual(outputs,builder.build())
        catalog = json.loads(outputs['catalog.json'])
        self.assertEqual(len(catalog),11)
        for item in catalog:
            name = item['path']
            ttl = Graph().parse(data=outputs[name+'.ttl'],format='turtle')
            ld = Graph().parse(data=outputs[name+'.jsonld'],format='json-ld')
            self.assertTrue(isomorphic(ttl,ld),name)
            self.assertGreater(len(ttl),0)
        for name,raw in outputs.items():self.assertEqual((builder.ROOT/'ids'/name).read_bytes(),raw,name)
        actual = {str(p.relative_to(builder.ROOT/'ids')) for p in (builder.ROOT/'ids').rglob('*') if p.is_file()}
        self.assertEqual(actual,set(outputs))

    def changed(self,change):
        with tempfile.TemporaryDirectory(prefix='ids-test-') as tmp:
            root = Path(tmp)
            shutil.copytree(builder.ROOT/'data/ids',root/'data/ids')
            change(root/'data/ids')
            with self.assertRaises((ValueError,FileNotFoundError)):builder.build(root)

    def test_source_corruption(self):
        self.changed(lambda d:(d/'sources/quechua/ns.ttl').write_text('corrupt'))

    def test_missing_source(self):
        self.changed(lambda d:(d/'sources/quechua/ns.ttl').unlink())

    def ledger_change(self,change):
        def mutate(d):
            path = d/'ownership.json'; value = json.loads(path.read_text());change(value);path.write_text(json.dumps(value))
        self.changed(mutate)

    def test_duplicate_destination(self):
        self.ledger_change(lambda v:v['terms'][1].update(new=v['terms'][0]['new']))

    def test_duplicate_source(self):
        self.ledger_change(lambda v:v['terms'].append(copy.deepcopy(v['terms'][0])))

    def test_foreign_owner(self):
        self.ledger_change(lambda v:v['terms'][0].update(new='https://example.org/elsewhere'))

    def test_missing_term(self):
        self.ledger_change(lambda v:v['terms'].pop())

    def test_missing_namespace(self):
        self.ledger_change(lambda v:v['entries'].pop('seeds/ns'))

    def test_distinct_source_schemes(self):
        ledger = json.loads((builder.ROOT/'data/ids/ownership.json').read_text())['terms']
        pairs = {r['old']:r['new'] for r in ledger}
        for term in ('derivedBy','derivationParams','derivationQuery','derivationSystem'):
            self.assertNotEqual(pairs['http://quipu.dev/ontology/'+term],pairs['https://quipu.dev/ontology/'+term])

if __name__ == '__main__':unittest.main()
