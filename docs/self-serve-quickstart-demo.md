# Open the playground without setup

Click “Try the playground” in the self-serve section. At base
`a08fbbffb58cb2760c1050f936095fee371d0c3a`, the section first showed another
launch button. This candidate embeds the existing explorer immediately, so
the link goes straight to the graph. The engine and shipped repository pack
still load in the browser; there is no fabricated graph or sample answer.

The live engine loaded 108,750 triples, drew 149 nodes and 207 links, and the
first suggested question returned seven rows. Browser checks wait for a
populated graph, rather than treating the pack-loaded status as a rendered map.
The first load downloads the engine and pack; loading time is not zero input.
No tokens, URLs, uploads or setup form are required from the visitor.

The self-serve lead now calls the offering the Intigraph agent platform with
a centralized knowledge graph. The timing is a historical, single Linux test
of installation and verification of Quipu, Camayoc and Bobbin. Machine
preparation, credentials and a separate MCP check were excluded. This change
adds no new install-time measurement. Released Tambo prerequisites remain
explicit until the new local default is available; a new timed install and
that copy update follow the Tambo release.

These are still screenshots, not a recording:

- [Before: launch screen](images/quickstart-before-desktop-light.png)
- [After: self-serve copy](images/quickstart-desktop-light.png)
- [After: populated graph, desktop dark](images/quickstart-graph-desktop-dark.png)
- [After: populated graph, mobile light](images/quickstart-graph-mobile-light.png)

The local candidate embeds the existing public explorer; these screenshots
are not proof that this site candidate has been deployed. Desktop 1440px and
mobile 375px, light and dark, have no overflow or page errors. Both existing
diagrams decode. The host contract test retains trusted origin/source checks,
valid resize growth/shrinkage and invalid-message rejection; its controlled
iframe is distinct from the real-engine check above.

Reproduce the host controls with `node scripts/test-playground.cjs` after
installing Playwright. For the real engine, open the page, wait for a nonzero
node count, then choose the first starter question and inspect its result table.
