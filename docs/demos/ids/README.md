# Identifier publication demo

Trigger: request the same namespace resources from two private local static
servers. The base revision is `9c55a60d7487b43f98ef327d678e9917d7fbf90f`;
the candidate is the source committed with this recording. The homepage is a
positive control. Namespace resources change from 404 to 200.

This is a replayable terminal recording, not a video or deployed-site proof.
Download `output.log` and `timing.log`, then run:

```sh
scriptreplay --log-out output.log --log-timing timing.log
```

Readable output is in `output.log`; repeat with `python3 scripts/demo-ids.py`.
The private HTTP server does not reproduce GitHub Pages or upstream w3id
content negotiation. Those require the separate post-publication curl proofs.
Recording retained in the source repository alongside the implementation.
