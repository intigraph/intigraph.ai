# intigraph.ai

The Intigraph website: one static page served by GitHub Pages at https://intigraph.ai.

- `index.html` — the page (no build step)
- `logo.svg`, `icon.svg` — the Intigraph mark
- `steve.jpg`, `steve.webp` — retained portrait assets (not displayed on the page)
- `CNAME` — custom domain for GitHub Pages

The "Try it" section embeds https://scbrown.github.io/quipu/explore/?embed=1&theme=intigraph.
The child starts on Map in the Intigraph theme and sends bounded height messages;
the host accepts them only from that iframe at the expected origin.

[Before/after browser demonstration](docs/playground-embed-demo.md).
The `Playground` workflow checks the host URL, cross-origin sizing, invalid
messages and the mobile layout. It adds no build step or runtime dependency.
