# Playground embed URL and sizing

The same browser probe launches the real site HTML and an explicitly controlled,
cross-origin playground frame. Before this change, the URL had no presentation
flags and valid child height messages did not resize it. Afterward, the URL
selects the Intigraph Map embed and the frame grows to 920px and shrinks to 640px.
Messages with the wrong origin, source or type, and invalid height bounds, leave
it unchanged. The 390px layout fits without horizontal overflow.

[Actual before/after browser output](playground-embed-demo.txt).

Source before: `56b8207eb8582ed6d886834639e42966c3184117`.
Source after: `cabbb5c5c28cfc41eb6b0933a1cf0cbcb44453c3`.

The controlled child isolates the host message listener; it does not demonstrate
the Quipu engine. [Quipu's separate real-engine recordings and limits](https://github.com/scbrown/quipu/blob/8da6533570cb9bac681e610f12b8f46156556eab/docs/design/explore-intigraph-embed-demo.md)
cover the Map, queries and write refusal. Deployment and the custom domain's TLS
certificate still need verification after landing.

Reproduce on each revision with the same probe from this change:

```sh
npm install --no-save --package-lock=false playwright@1.61.0
npx playwright install --with-deps chromium
xvfb-run -a node scripts/test-playground.cjs --observe
```

Run without `--observe` to require the completed host contract, as CI does.
Both local runs and the strict check passed through the HOME guard with 157
watched paths and five resources untouched.
