# Former-name contracts

Current tools are Tambo and Yupana. The following is the per-path allowlist
for retained former-name mentions, including this explicit compatibility ledger.

| Path | Reason |
| --- | --- |
| `docs/self-serve-install-demo.md` | Historical October 7, 2026 timing measurement names the actual installer version and explicitly maps its former name to Tambo. It is not a new measurement. |
| `data/ids/sources/camayoc/shapes/aegis/aegis-properties.ttl` | Pinned upstream vocabulary source; do not change bytes under its existing commit and digest. |
| `data/ids/sources/camayoc/shapes/core.shapes.ttl` | Pinned upstream shape snapshot. |
| `data/ids/sources/quipu/shapes/governance.ttl` | Pinned upstream vocabulary source. |
| `data/ids/sources/quipu/shapes/graph-labels.ttl` | Pinned upstream vocabulary source. |
| `data/ids/sources/quipu/shapes/provenance.ttl` | Pinned upstream vocabulary source. |
| `ids/camayoc/core/ns.jsonld` | Generated from pinned source; refresh through the normal vocabulary generation path after the upstream release. |
| `ids/camayoc/core/ns.ttl` | Generated from the same pinned source; must stay consistent with its provenance. |

The pinned-source mentions require a normal refresh after the upstream release.
This allowlist records that dependency; it does not claim that source refresh
or public default-branch rename acceptance has completed.
