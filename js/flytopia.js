/* Flytopia v0.1 — sanctuary interface, not a modification of the connectome. */
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
