"""Validate additive released-source publication mappings without changing old IRIs."""
import json
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS, OWL

BASE = 'https://w3id.org/intigraph/'
SH = 'http://www.w3.org/ns/shacl#'


def extend(data, spec, accepted, manifest):
    publication = json.loads((data/'publication-additions.json').read_text())
    if publication.get('format') != 'released-publication-additions/v1':
        raise ValueError('Unknown publication additions format')
    additions = publication['additions']
    if len(additions) != 12 or len({r['old'] for r in additions}) != 12:
        raise ValueError('Invalid reviewed addition inventory')
    old = {r['old']: r for r in accepted}
    pins = {r['repository'].split('/')[-1]+'/'+r['path']: r for r in manifest}
    for row in additions:
        owner, source = row['owner'], row['source']
        if row['old'] in old or source not in spec['entries'].get(owner, []) or source not in pins:
            raise ValueError('Addition ownership or pinned source mismatch')
        if owner.split('/')[0] != source.split('/')[0]:
            raise ValueError('Addition owner is not its defining source')
        if row['new'] != BASE+owner+'#'+row['old'].rsplit('/', 1)[-1]:
            raise ValueError('Addition destination changes namespace')
        graph = Graph().parse(data/'sources'/source, format='turtle')
        node = URIRef(row['old'])
        classes = (RDFS.Class, OWL.Class)
        if row['roles'] == ['class']:
            defined = any((node, RDF.type, kind) in graph for kind in classes) or (
                node, RDFS.subClassOf, None) in graph
        elif row['roles'] == ['property']:
            defined = (node, RDF.type, RDF.Property) in graph or (
                None, URIRef(SH+'path'), node) in graph
        elif row['roles'] == []:
            defined = (node, RDF.type, URIRef(SH+'NodeShape')) in graph
        else:
            raise ValueError('Unsupported addition role')
        if not defined:
            raise ValueError('Addition is not defined by released source')
    deprecated = publication['deprecated']
    # This is the explicit reviewed disappearance, not a generic missing-term escape.
    if len(deprecated) != 1 or deprecated[0]['old'] != (
            'http://aegis.gastown.local/ontology/DecisionShape'):
        raise ValueError('Invalid deprecated identity inventory')
    row = deprecated[0]
    if row['owner'] != 'quipu/ns' or row['old'] not in old or 'replacement' in row:
        raise ValueError('Deprecated identity continuity changed')
    ledger = {r['old']: r for r in spec['terms']}
    if ledger[row['old']]['new'] != old[row['old']]['new'] or not (
            ledger[row['old']].get('disposition', '').startswith('Deprecated:')):
        raise ValueError('Deprecated identity dropped or reassigned')
    return accepted + additions, {row['old']}
