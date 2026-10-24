# Public identifier documents

`/ids/` is a static, pinned publication of eleven vocabulary namespaces. The
catalogue, ownership ledger and source manifest ship beside the documents.
Turtle and JSON-LD describe the same graph; HTML lists owned identities and
links to their exact source provenance.

Regenerate with `uv run --no-project scripts/build-ids.py --write`; omit
`--write` to verify committed bytes. The generator validates every pinned
source digest before writing and refuses missing namespaces, missing identities,
unpinned inputs and non-bijective mappings. The normal playground CI target
runs format equivalence, omission, corruption and resolver controls. No workflow
permission or new publisher is required. GitHub Pages uses its existing Jekyll
build with explicit data/ and scripts/ exclusions; raw pinned inputs are not served.

The ledger freezes one destination for each full source IRI. Shared terms have
one owner across packs. Four HTTP/HTTPS derivation-property pairs are distinct
in the source; each gets a source-digest suffix rather than an unsupported
identity merge. Public standards identifiers and replacement predicates remain
unchanged. Old-to-new `owl:sameAs` statements represent only the declared
one-to-one namespace aliases, not replacement targets or calendar identities.
Internal item references in literal text are replaced by neutral source-reference wording at generation time; other literal text retains its source spelling.
This publication is not a runnable replacement for the original SHACL packs.
No loaded shapes, graph data, rule execution or consumer defaults change.

The stage-one refresh pins Camayoc sources and its mapping ledger to merged
`6cff93433e8d5a895a17cef678aa9ead108f291d`. All 1,254 existing destinations stay
fixed. Property aliases also carry `owl:equivalentProperty`, and class aliases
carry `owl:equivalentClass` where the source ledger declares that role.
Core ontology and observation-debt source facts are included for documentation;
this does not combine their separate runtime loading policies.

The separate stage-two refresh pins merged Camayoc
`3e553637271a61ee01bd7e6428dfc63cb595cd01` and its additional ledger. It adds
45 destinations (36 properties, one class and eight named shapes), bringing
the total to 1,299. Every original stage-one destination stays fixed. Shape
identities carry identity aliases without being declared equivalent classes.
The two lifecycle identities `closedAt` and `assignedTo` remain legacy.
The upstream stage-two ledger's conservative publication marker is retained
as source provenance; actual availability requires verification of the deployed
site bytes. Pins and releases must wait for that verification, not this commit.
The generator resolves RDF identifiers, not source prefix spellings, and refuses
an unexplained identity, unpinned ledger or changed stage-one destination.

The fixed entity redirect accepts known `/ids/<namespace>/id/<identifier>`
paths and opens the existing Quipu explorer with the full w3id IRI in `entity`.
Encoded path separators, traversal, unknown namespaces and entity `.ttl` or
`.jsonld` requests stay not-found. Entity RDF responses are not implemented.
The source host serves static explicit-format resources; Accept negotiation
belongs to the separately reviewed upstream w3id Apache redirect rules.
An unpublished upstream rule is not claimed live by this site change.

Roll back the site source by reverting this publication commit through the
normal Pages path. That restores the previous site; it does not delete or
reassign an established public identifier. Verify exact Pages completion and
curl each catalogue HTML, Turtle and JSON-LD target before claiming availability.
The upstream w3id proposal remains a separate authorized publication step.

Pinned upstream LICENSE/NOTICE files accompany the copied sources. The pinned
Quechua root has no LICENSE/NOTICE file; no substitute license is invented.
Publication is under the repository owner’s explicit vocabulary-publication direction.
