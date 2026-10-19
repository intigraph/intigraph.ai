# Self-serve installation section

Previously, the page offered a browser playground but no installation CTA or
measured self-serve result. The new section invites teams to try the core stack,
links to [Tambo's current install steps](https://github.com/scbrown/tambo#install),
and qualifies its timing as one historical Linux clean-room test.

## What the number measures

On October 7, 2026, an automated agent installed the retrieval profile from the
public README in a fresh Ubuntu 24.04 container. Its complete installation
session took 295.771 seconds (4.93 minutes), including indexing, registration
and final verification. The installed tools were Quipu, Camayoc and Bobbin,
using Caboodle v0.2.11. The session completed without errors or guesses.

A separate fresh agent session made a successful Bobbin MCP call in 12.289
seconds. That check is outside the under-five-minute claim. Machine preparation
and credential setup are also excluded. The page states these boundaries beside
the number and points to the current server and issued-token prerequisites.

This is one accepted historical sample. The page makes no universal installation
time promise. Current releases and other platforms require their own measurement.

## Browser demonstration

Select **Install with Tambo** to open the install guide, or **Try the playground**
to reach the existing browser demo. The screenshots are local source previews,
not deployment receipts.

Before:

- [Desktop, light](images/self-serve-before-desktop-light.png)
- [375px, dark](images/self-serve-before-mobile-dark.png)

After:

- [Desktop, light](images/self-serve-desktop-light.png)
- [Desktop, dark](images/self-serve-desktop-dark.png)
- [375px, light](images/self-serve-mobile-light.png)
- [375px, dark](images/self-serve-mobile-dark.png)

The before page is commit `2f842de9e3b3ca76633a9c27647c627e637de0d9`.
The after screenshots show the candidate section recorded on October 19, 2026.
Browser checks cover both widths and themes, readable timing exclusions,
44px CTA targets, no horizontal overflow, both diagrams decoding, four journey
stages and no displayed portrait. The existing playground URL, resize and
invalid-message contract also passes. No script or diagram content changed.
