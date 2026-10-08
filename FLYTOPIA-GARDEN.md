# Flytopia v0.2 — sanctuary garden (visual pass)

- Add a decorative orchard overlay to the same viewport as FlyBrain's canvas.
- Add a Garden On/Off toggle beside Feed.
- Correct garbled emoji/punctuation by declaring HTML UTF-8 encoding.
- All visual scene elements deliberately use pointer-events: none.
- The **native Feed** tool continues to place real simulation food.
- The painted banana grove, apple clearing, berry meadow, and pond are **not yet sensory objects**. They do not currently emit odor, provide water, or influence neural signals.
- No original neural, locomotion, render, or simulation files are modified.

**Next scientific milestone:** map the original FlyBrain `main.js`, `fly-logic.js`,
`brain-worker-bridge.js`, and food implementation, then add world objects through its
actual sensory pathways. Do not imply a decorative apple is sensed by the fly.

**If you need to troubleshoot:** Refresh using Cmd+Shift+R. Disable the scenery via
"Garden: Off". The original research tools can still be shown using
`http://localhost:8000/?flytopiaDebug=1`.

Based on MIT-licensed [snedea/flybrain](https://github.com/snedea/flybrain).
Keep the repository's original license and attribution intact.
