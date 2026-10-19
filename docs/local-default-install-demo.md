# Install locally without a server or issued token

At base `ebe018b2833101969973592fb62ed24708169da3`, the self-serve section
said current installs required a server and issued token. Tambo 0.4.0 now
ships the local default. The section gives `tambo quickstart` and
`tambo verify`, states that no server or issued token is required, and
keeps remote shared-server access as an advanced option.

Release workflow [39321765478](https://github.com/scbrown/tambo/actions/runs/39321765478)
attempt 2 passed. The public crates.io 0.4.0 response was not yanked and its
checksum matched the workflow package. This is release evidence; the new
timed clean-room install remains separate. The existing historical Linux
timing and its preparation, credential and MCP exclusions remain unchanged.

These screenshots compare the same section before and after:

- [Before, desktop light](images/local-default-before-1440-light.png)
- [After, desktop light](images/local-default-after-1440-light.png)
- [Before, mobile dark](images/local-default-before-375-dark.png)
- [After, mobile dark](images/local-default-after-375-dark.png)

Both viewport checks assert the commands, the no-server/no-token statement,
the advanced remote option, historical timing, and absence of horizontal
overflow. The iframe was controlled for these copy-only screenshots; they
provide no new explorer-engine or deployed-site proof. No JavaScript, graph,
iframe or message-handling behavior changes in this PR.

To reproduce, serve the base and candidate `index.html`, view `#yourself`
at 1440px/light and 375px/dark, and compare the text above. The prior
playground contract and real-engine acceptance remain documented in
[self-serve-quickstart-demo.md](self-serve-quickstart-demo.md).
