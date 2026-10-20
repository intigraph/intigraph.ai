# One canonical stack list

The website's static stack cards are generated from Tambo's
[`docs/stack-table.md`](https://github.com/scbrown/tambo/blob/b11f4a67be11094a73a35157dcccf8d12c48d693/docs/stack-table.md).
`data/stack-table.md` preserves the entire source file byte for byte;
`data/stack-source.json` pins its repository, immutable commit, path and SHA256.
Names, descriptions, links and ordering come from that table. There is no
second component registry and no visitor-side fetch or rendering dependency.

To update, obtain the canonical file at the chosen immutable source revision,
verify its bytes, update the pin, then run:

```sh
python3 scripts/stack-section.py --write
python3 scripts/test-stack-section.py
xvfb-run -a node scripts/test-playground.cjs
```

The existing Playground test entrypoint checks the source pin, omitted or
changed cards/links, duplicate rows, malformed URLs and incomplete/corrupt
source. Its browser checks every canonical card/link/description and layout
at desktop and mobile sizes, alongside the existing iframe controls.
A local test proves candidate behavior; it does not prove Pages deployment.

## Before and after

Same stack-section browser observation at 1280×900 and 390×860: the base
`408c3794d3f0692aa535c4200d43df32879f906f` has ten cards and no component
repository links. The candidate adds Camayoc and Rikuy, and renders all twelve
canonical rows as repository links. Existing Quechua, Chaski and Tambo remain.
These are screenshots of local source, not recordings or proof of publication.
The public base page independently showed the same ten-card result.

| View | Before | Candidate |
| --- | --- | --- |
| Desktop | [Screenshot](images/stack-before-desktop.png) | [Screenshot](images/stack-after-desktop.png) |
| Mobile | [Screenshot](images/stack-before-mobile.png) | [Screenshot](images/stack-after-mobile.png) |

Small sanitized screenshots follow this repository's existing demo-image
retention. Revert the source change to restore the former page; the canonical
Tambo table is not modified here.
