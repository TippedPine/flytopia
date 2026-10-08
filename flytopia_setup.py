#!/usr/bin/env python3
"""Install Flytopia v0.1's visual sanctuary overlay into a local FlyBrain fork.

Run from the root of your cloned flytopia repository:
    python3 ~/Downloads/flytopia_setup.py

Modifies index.html, creates css/flytopia.css, js/flytopia.js,
and FLYTOPIA.md. It does not alter the neural simulation scripts or data.
"""
from pathlib import Path
import sys

CSS = r"""/* Flytopia v0.1 — presentation only. No neural simulation changes. */
:root {
  --flytopia-deep: #122b24;
  --flytopia-forest: #1d4432;
  --flytopia-leaf: #b4e3a5;
  --flytopia-gold: #f4d995;
}

/* Experimental controls remain in the DOM for upstream JavaScript compatibility. */
body.flytopia-mode:not(.flytopia-debug) #toolbar [data-tool="touch"],
body.flytopia-mode:not(.flytopia-debug) #toolbar [data-tool="air"],
body.flytopia-mode:not(.flytopia-debug) #helpOverlay .flytopia-research-help {
  display: none !important;
}

body.flytopia-mode #toolbar {
  background: linear-gradient(112deg, var(--flytopia-deep), var(--flytopia-forest)) !important;
  border-bottom: 1px solid rgba(180, 227, 165, 0.22) !important;
  box-shadow: 0 5px 18px rgba(15, 40, 27, 0.18);
}

body.flytopia-mode #toolbar .toolbar-title {
  color: #f7f4dc !important;
  font-weight: 750;
  letter-spacing: 0.04em;
}

body.flytopia-mode #toolbar .tool-btn {
  color: #ecf5e5;
  background: rgba(255, 255, 255, 0.085);
  border-color: rgba(224, 241, 214, 0.3);
}

body.flytopia-mode #toolbar .tool-btn.active,
body.flytopia-mode #toolbar .tool-btn:hover {
  background: rgba(180, 227, 165, 0.24);
  border-color: rgba(180, 227, 165, 0.7);
}

.flytopia-welcome {
  position: fixed;
  top: 84px;
  right: 18px;
  width: min(348px, calc(100vw - 36px));
  padding: 21px 22px;
  z-index: 900;
  box-sizing: border-box;
  color: #f9f7e9;
  background: linear-gradient(152deg, rgba(26, 65, 45, 0.97), rgba(16, 43, 37, 0.97));
  border: 1px solid rgba(217, 236, 179, 0.3);
  border-radius: 18px;
  box-shadow: 0 15px 38px rgba(9, 28, 22, 0.32);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.flytopia-welcome .flytopia-kicker {
  color: var(--flytopia-leaf);
  font-size: 10px;
  letter-spacing: 0.15em;
  font-weight: 800;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.flytopia-welcome h2 {
  margin: 0 0 8px;
  color: #fff9e0;
  font-size: 22px;
  line-height: 1.22;
  font-weight: 750;
}

.flytopia-welcome p {
  margin: 8px 0;
  color: #d8e7d5;
  line-height: 1.5;
  font-size: 13px;
}

.flytopia-welcome .flytopia-tagline {
  font-size: 12px;
  color: var(--flytopia-gold);
  font-weight: 700;
}

.flytopia-welcome .flytopia-action {
  margin-top: 14px;
  padding: 9px 14px;
  border: 1px solid rgba(228, 240, 197, 0.55);
  border-radius: 999px;
  background: rgba(180, 227, 165, 0.19);
  color: #f6f7dd;
  cursor: pointer;
  font-weight: 700;
  font-size: 12px;
}

.flytopia-welcome .flytopia-action:hover,
.flytopia-welcome .flytopia-action:focus-visible {
  background: rgba(180, 227, 165, 0.32);
}

@media (max-width: 650px) {
  .flytopia-welcome {
    top: auto;
    bottom: 22px;
    right: 12px;
    width: min(330px, calc(100vw - 24px));
    padding: 17px 18px;
  }
}
"""

JS = r"""/* Flytopia v0.1 — sanctuary interface, not a modification of the connectome. */
(function () {
  "use strict";

  function begin() {
    document.body.classList.add("flytopia-mode");

    // This URL opt-in is for debugging only; nothing in the simulator is deleted.
    // Visit http://localhost:8000/?flytopiaDebug=1 to reveal research controls.
    if (new URLSearchParams(window.location.search).get("flytopiaDebug") === "1") {
      document.body.classList.add("flytopia-debug");
    }

    const help = document.getElementById("helpOverlay");
    if (help) {
      help.querySelectorAll(".help-item").forEach((item) => {
        if (/^(Touch|Air)\b/i.test(item.textContent.trim())) {
          item.classList.add("flytopia-research-help");
        }
      });
    }

    if (document.getElementById("flytopiaWelcome")) return;

    const welcome = document.createElement("section");
    welcome.className = "flytopia-welcome";
    welcome.id = "flytopiaWelcome";
    welcome.setAttribute("aria-label", "Flytopia welcome message");
    welcome.innerHTML = `
      <div class="flytopia-kicker">🌿 Sanctuary mode · version 0.1</div>
      <h2>Welcome home, little fly.</h2>
      <p class="flytopia-tagline">139,255 neurons. Zero experiments scheduled.</p>
      <p>Thank you for your contribution to neuroscience. Enjoy your retirement.</p>
      <p><strong>Feed</strong> still places real simulation food. Brain activity and movement still come from the original FlyBrain engine.</p>
      <button type="button" class="flytopia-action" id="flytopiaDismiss">Let the little guy explore →</button>
    `;
    document.body.appendChild(welcome);
    const dismiss = document.getElementById("flytopiaDismiss");
    dismiss.addEventListener("click", () => welcome.remove());
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", begin, { once: true });
  } else {
    begin();
  }
})();
"""

NOTES = """# Flytopia v0.1 — sanctuary interface

Flytopia is a playful fork of [snedea/flybrain](https://github.com/snedea/flybrain).

**What this version changes**
- Displays Flytopia branding and a garden-themed toolbar.
- Hides the Touch and Air controls in ordinary use (they are not deleted).
- Adds a dismissible welcome card.
- Keeps the original simulation JavaScript, connectome data, Feed, Light,
  Temperature, neural visualization and behavior interfaces unchanged.

**Diagnostics**
Add `?flytopiaDebug=1` to the end of the local URL if you need to display
Touch and Air again (for example `http://localhost:8000/?flytopiaDebug=1`).

**Important**
This version is **not yet** a true virtual orchard, an automated circadian
cycle, a new sensory environment, or a measure of the fly's welfare.
Those require careful simulation-level changes in later milestones.

**Attribution**
Based on FlyBrain by snedea and contributors, MIT-licensed. Keep the original
license and acknowledgments intact. The underlying connectome model does not
establish that a digital fly is conscious or experiences pleasure or pain.
"""


def main():
    repo = Path.cwd()
    index = repo / "index.html"
    if not index.is_file() or not (repo / "js" / "main.js").is_file():
        sys.exit("ERROR: Open a terminal in the root of your cloned flytopia repo first. "
                 "Expected index.html and js/main.js here: " + str(repo))

    original = index.read_text(encoding="utf-8")
    if "</head>" not in original or "</body>" not in original:
        sys.exit("ERROR: index.html has unexpected structure. No files were changed.")
    if './css/main.css' not in original or './js/main.js' not in original:
        sys.exit("ERROR: This is not the expected FlyBrain index.html. No files were changed.")

    html = original
    html = html.replace("<title>FlyBrain</title>",
                        "<title>Flytopia — a little fly's paradise</title>", 1)
    html = html.replace('<span class="toolbar-title">FlyBrain</span>',
                        '<span class="toolbar-title">🌿 Flytopia</span>', 1)

    if '<link rel="stylesheet" href="./css/flytopia.css?v=1">' not in html:
        html = html.replace("</head>",
                            '  <!-- Flytopia sanctuary theme -->\n'
                            '  <link rel="stylesheet" href="./css/flytopia.css?v=1">\n'
                            '</head>', 1)
    if '<script src="./js/flytopia.js?v=1"></script>' not in html:
        html = html.replace("</body>",
                            '  <!-- Flytopia sanctuary overlay -->\n'
                            '  <script src="./js/flytopia.js?v=1"></script>\n'
                            '</body>', 1)

    # Validate destinations before changing anything.
    destinations = {repo / "css" / "flytopia.css": CSS,
                    repo / "js" / "flytopia.js": JS,
                    repo / "FLYTOPIA.md": NOTES}
    for path in destinations:
        if path.exists() and not path.is_file():
            sys.exit(f"ERROR: Cannot overwrite non-file: {path}")

    index.write_text(html, encoding="utf-8")
    for path, contents in destinations.items():
        path.write_text(contents, encoding="utf-8")

    print("SUCCESS: Flytopia v0.1 sanctuary interface installed.")
    print("Updated: index.html")
    print("Created/updated: css/flytopia.css, js/flytopia.js, FLYTOPIA.md")
    print("Simulation source files and connectome data were NOT modified.")
    print("Refresh http://localhost:8000/ (Cmd+Shift+R on Mac).")
    if html == original:
        print("Note: Re-ran installer; index.html links were already installed.")


if __name__ == "__main__":
    main()
