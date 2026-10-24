"""Offline format, identity, corruption and omission controls for committed IDs."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from rdflib import Graph, URIRef
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

    def test_public_literal_scrubs_internal_item_references(self):
        from rdflib import Literal
        for value in ('internal case aegis-vj3uet', 'constraint (aegis-q9m5mp)', 'nested aegis-kzt0ql.9.3'):
            self.assertNotIn('aegis-',str(builder.public_literal(Literal(value,lang='en'))))
            self.assertEqual(builder.public_literal(Literal(value,lang='en')).language,'en')
        control = Literal('ordinary vocabulary text')
        self.assertEqual(builder.public_literal(control),control)

    def test_served_tree_rejects_item_and_raw_sources(self):
        spec = importlib.util.spec_from_file_location('public_check',Path(__file__).with_name('check-public-tree.py'))
        check = importlib.util.module_from_spec(spec);spec.loader.exec_module(check)
        with tempfile.TemporaryDirectory(prefix='public-tree-') as temporary:
            root = Path(temporary)
            (root/'index.html').write_text('safe vocabulary')
            self.assertTrue(check.check(root,actual=True))
            (root/'index.html').write_text('private case aegis-vj3uet')
            with self.assertRaises(ValueError):check.check(root,actual=True)
            (root/'index.html').write_text('https://unsafe.'+'svc/private')
            with self.assertRaises(ValueError):check.check(root,actual=True)
            (root/'index.html').write_text('safe vocabulary');(root/'data').mkdir()
            with self.assertRaises(ValueError):check.check(root,actual=True)
            (root/'data').rmdir();(root/'_config.yml').write_text('exclude: []\n')
            with self.assertRaises(ValueError):check.check(root,actual=False)

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

    def test_merged_destinations_and_role_bridges(self):
        ledger = json.loads((builder.ROOT/'data/ids/sources/camayoc/namespaces/intigraph/mapping.json').read_text())
        stage_two = json.loads((builder.ROOT/'data/ids/sources/camayoc/namespaces/intigraph/stage-two.json').read_text())
        spec = json.loads((builder.ROOT/'data/ids/ownership.json').read_text())
        self.assertEqual(len(spec['terms']),1299)
        outputs = builder.build()
        all_graphs = Graph()
        for name, raw in outputs.items():
            if name.endswith('.ttl'):all_graphs += Graph().parse(data=raw,format='turtle')
        for row in ledger['pairs'] + stage_two['pairs']:
            old, new = URIRef(row['old']), URIRef(row['new'])
            self.assertIn((old,builder.OWL_SAME,new),all_graphs)
            if 'property' in row['roles']:self.assertIn((old,builder.OWL_PROPERTY,new),all_graphs)
            if 'class' in row['roles']:self.assertIn((old,builder.OWL_CLASS,new),all_graphs)
            if not row['roles']:
                self.assertNotIn((old,builder.OWL_CLASS,new),all_graphs)
                self.assertNotIn((old,builder.OWL_PROPERTY,new),all_graphs)
        new_nodes = {str(node) for triple in all_graphs for node in triple if isinstance(node,URIRef)}
        self.assertEqual(len(stage_two['pairs']),45)
        self.assertEqual(sum(not r['roles'] for r in stage_two['pairs']),8)
        self.assertTrue({r['new'] for r in stage_two['pairs']} <= new_nodes)
        for old in spec['retained_legacy']:
            local = old.rsplit('/',1)[1]
            self.assertIn(local,('closedAt','assignedTo'))
            self.assertNotIn(builder.BASE+'camayoc/core/ns#'+local,new_nodes)

    def test_retained_identity_cannot_be_silently_published_or_dropped(self):
        self.ledger_change(lambda v:v['retained_legacy'].pop())
        self.ledger_change(lambda v:v['retained_legacy'].__setitem__(0,'https://example.org/unknown'))
        self.ledger_change(lambda v:v['terms'][0].update(new=builder.BASE+'camayoc/core/ns#unapproved'))

    def test_missing_or_unpinned_stage_two_refuses(self):
        self.changed(lambda d:(d/'sources/camayoc/namespaces/intigraph/stage-two.json').unlink())
        def remove_pin(d):
            p = d/'sources.json'
            rows = json.loads(p.read_text())
            p.write_text(json.dumps([r for r in rows if r['path'] != 'namespaces/intigraph/stage-two.json']))
        self.changed(remove_pin)

    def test_distinct_source_schemes(self):
        ledger = json.loads((builder.ROOT/'data/ids/ownership.json').read_text())['terms']
        pairs = {r['old']:r['new'] for r in ledger}
        for term in ('derivedBy','derivationParams','derivationQuery','derivationSystem'):
            self.assertNotEqual(pairs['http://quipu.dev/ontology/'+term],pairs['https://quipu.dev/ontology/'+term])

if __name__ == '__main__':unittest.main()
