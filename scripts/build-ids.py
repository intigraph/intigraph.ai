#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["rdflib==7.1.4"]
# ///
"""Build pinned public vocabulary documents without network access or runtime loading."""
import argparse
import hashlib
import html
import json
from pathlib import Path

import rdflib
from rdflib import Graph, URIRef, BNode, Literal
rdflib.NORMALIZE_LITERALS = False
from rdflib.compare import to_canonical_graph

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://w3id.org/intigraph/'
OWL_SAME = URIRef('http://www.w3.org/2002/07/owl#sameAs')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def page(title, body):
    return ('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>'+html.escape(title)+' · Intigraph IDs</title>'
            '<style>body{max-width:70rem;margin:2rem auto;padding:0 1rem;font:18px/1.6 system-ui;color:#152d31;background:#faf9f4}'
            'a{color:#075d68}code,dd,h2{overflow-wrap:anywhere}article{border-top:1px solid #ccc;padding:1rem 0}h1{overflow-wrap:anywhere}</style>'
            '<nav><a href="/">Intigraph</a> / <a href="/ids/">Identifiers</a></nav><main><h1>'
            +html.escape(title)+'</h1>'+body+'</main></html>\n').encode()


def build(root=ROOT):
    data = root/'data/ids'
    manifest = json.loads((data/'sources.json').read_text())
    for item in manifest:
        source = data/'sources'/item['repository'].split('/')[-1]/item['path']
        raw = source.read_bytes()
        if digest(raw) != item['sha256'] or len(raw) != item['bytes']:
            raise ValueError('Pinned source mismatch: '+item['path'])
    spec = json.loads((data/'ownership.json').read_text())
    rows = spec['terms']
    mapping = {r['old']:r['new'] for r in rows}
    if len(mapping) != len(rows) or len(set(mapping.values())) != len(rows):
        raise ValueError('Non-bijective ownership ledger')
    for row in rows:
        if row['owner'] not in spec['entries'] or not row['new'].startswith(BASE+row['owner']+'#') and row['new'] != BASE+row['owner']:
            raise ValueError('Invalid owner or destination')
    expected_entries = {'quechua/ns','quipu/ns','seeds/ns'} | {'camayoc/'+n+'/ns' for n in ('core','delivery','code-entities','session-transcript','usage-breakdown','homelab-infra','personal-media','software-factory')}
    if set(spec['entries']) != expected_entries:raise ValueError('Namespace coverage mismatch')
    pinned = {i['repository'].split('/')[-1]+'/'+i['path'] for i in manifest}
    prefixes = ('https://scbrown.github.io/quechua/ns#','https://seeds.local/ontology/','http://aegis.gastown.local/ontology/','http://aegis.gastown.local/rules/','https://camayoc.dev/ontology#','https://camayoc.local/ontology/','http://quipu.dev/ontology/','https://quipu.dev/ontology/','http://quipu.local/graph#','http://quipu.local/rule#','urn:quipu:shape:')
    seen = set()
    for files in spec['entries'].values():
        if not files or len(files) != len(set(files)):raise ValueError('Empty or repeated source list')
        for source in files:
            if source not in pinned:raise ValueError('Unpinned source')
            for triple in Graph().parse(data/'sources'/source,format='turtle'):
                for node in triple:
                    if isinstance(node,URIRef) and (str(node).startswith(prefixes) or str(node) == 'https://scbrown.github.io/quechua/ns'):seen.add(str(node))
    if seen != set(mapping):raise ValueError('Identity ledger coverage mismatch')
    outputs = {}
    catalog = []
    for name, sources in sorted(spec['entries'].items()):
        graph = Graph()
        for source in sources:
            graph += Graph().parse(data/'sources'/source,format='turtle')
        renamed = Graph()
        for triple in graph:
            renamed.add(tuple(URIRef(mapping[str(n)]) if isinstance(n,URIRef) and str(n) in mapping else n for n in triple))
        own = [r for r in rows if r['owner'] == name]
        for row in own:
            renamed.add((URIRef(row['old']),OWL_SAME,URIRef(row['new'])))
        canonical = to_canonical_graph(renamed)
        # N-Triples is a Turtle subset. Canonical labels make committed bytes reproducible.
        ttl = ('\n'.join(sorted(' '.join(n.n3() for n in triple)+' .' for triple in canonical))+'\n').encode()
        nodes_by_id = {}
        def node_id(n):
            return '_:'+str(n) if isinstance(n,BNode) else str(n)
        for subject,predicate,obj in canonical:
            node = nodes_by_id.setdefault(node_id(subject),{'@id':node_id(subject)})
            if isinstance(obj,Literal):
                value = {'@value':str(obj)}
                if obj.language:value['@language'] = obj.language
                elif obj.datatype:value['@type'] = str(obj.datatype)
            else:value = {'@id':node_id(obj)}
            node.setdefault(str(predicate),[]).append(value)
        nodes = list(nodes_by_id.values())
        for node in nodes:
            for key,value in node.items():
                if isinstance(value,list):node[key] = sorted(value,key=lambda v:json.dumps(v,sort_keys=True))
        jsonld = (json.dumps(sorted(nodes,key=lambda n:n['@id']),sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
        for suffix,raw in [('.ttl',ttl),('.jsonld',jsonld)]:outputs[name+suffix] = raw
        links = '<p><a href="/ids/'+name+'.ttl">Turtle</a> · <a href="/ids/'+name+'.jsonld">JSON-LD</a></p>'
        note = '<p>Pinned source publication. Existing identifiers remain aliases; this does not load shapes, rewrite stored data, or activate runtime validation. Rule text and literals retain their source spelling.</p>'
        provenance = '<details><summary>Source provenance</summary><ul>'+''.join('<li><code>'+html.escape(s)+'</code></li>' for s in sources)+'</ul><p><a href="/ids/sources.json">Exact commits and SHA-256 digests</a> · <a href="/ids/ownership.json">Complete identity ledger</a></p></details>'
        terms = ''.join('<article id="'+html.escape(r['new'].split('#')[-1],quote=True)+'"><h2>'+html.escape(r['new'].split('#')[-1])+'</h2><p><code>'+html.escape(r['new'])+'</code></p><p>Source identity: <code>'+html.escape(r['old'])+'</code></p>'+('<p>'+html.escape(r['disposition'])+'</p>' if 'disposition' in r else '')+'</article>' for r in own)
        outputs[name+'/index.html'] = page(name,links+note+provenance+terms)
        catalog.append(dict(path=name,triples=len(renamed),terms=len(own),sha256={'.ttl':digest(ttl),'.jsonld':digest(jsonld)}))
    outputs['index.html'] = page('Identifiers','<p>Stable vocabulary documents and source-preserving aliases. Content negotiation is provided by the upstream w3id redirect rules; these static targets expose explicit formats.</p><ul>'+''.join('<li><a href="/ids/'+c['path']+'/">'+c['path']+'</a></li>' for c in catalog)+'</ul>')
    outputs['catalog.json'] = (json.dumps(catalog,indent=2)+'\n').encode()
    for name in ('ownership.json','sources.json'):outputs[name] = (data/name).read_bytes()
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    outputs = build()
    target = ROOT/'ids'
    expected = set(outputs)
    actual = {str(p.relative_to(target)) for p in target.rglob('*') if p.is_file()} if target.exists() else set()
    if args.write:
        if actual-expected:raise ValueError('Unexpected output files; refusing deletion')
        for name,raw in outputs.items():
            dest = target/name
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(raw)
    else:
        if actual != expected:raise ValueError('Output inventory mismatch')
        for name,raw in outputs.items():
            if (target/name).read_bytes() != raw:raise ValueError('Stale output: '+name)
    print(f'{len(outputs)} output files; 11 namespaces; pinned sources and ownership verified')

if __name__ == '__main__':main()
