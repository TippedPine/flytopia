#!/usr/bin/env python3
"""Install a reversible fix for the Flytopia v0.2 overlay bug.

Place in cloned flytopia repo root, run `python3 flytopia_fix_v03.py`.
Run `python3 flytopia_fix_v03.py --rollback` to restore backed-up v0.2 files.
"""
from pathlib import Path
import shutil
import sys

GARDEN_JS = '/* Flytopia v0.3 - draw orchard scenery INSIDE the original FlyBrain canvas.\n   Decorative only; normal food/brain/motor code still belongs to FlyBrain. */\n(function () {\n  "use strict";\n  let cachedCanvas = null;\n  let cachedKey = "";\n  const garden = {\n    enabled: true,\n    draw: function (target, width, height) {\n      if (!this.enabled || width <= 0 || height <= 0) return;\n      const dpr = Math.min(window.devicePixelRatio || 1, 2);\n      const key = [width, height, dpr].join("|");\n      if (key !== cachedKey) {\n        cachedCanvas = document.createElement("canvas");\n        cachedCanvas.width = Math.max(1, Math.round(width * dpr));\n        cachedCanvas.height = Math.max(1, Math.round(height * dpr));\n        const cacheCtx = cachedCanvas.getContext("2d");\n        if (!cacheCtx) return;\n        cacheCtx.setTransform(dpr, 0, 0, dpr, 0, 0);\n        paint(cacheCtx, width, height);\n        cachedKey = key;\n      }\n      if (cachedCanvas) {\n        target.save();\n        target.drawImage(cachedCanvas, 0, 0, width, height);\n        target.restore();\n      }\n    }\n  };\n  window.FlytopiaGarden = garden;\n  function setupUI() {\n    // The old overlay must not be used; garden now renders behind food/fly.\n    const obsolete = document.getElementById("flytopia-garden-layer");\n    if (obsolete) obsolete.remove();\n    const toolbar = document.querySelector("#toolbar .toolbar-left");\n    if (toolbar && !document.getElementById("flytopia-garden-toggle")) {\n      const toggle = document.createElement("button");\n      toggle.id = "flytopia-garden-toggle";\n      toggle.type = "button";\n      toggle.className = "tool-btn";\n      toggle.textContent = "Garden: On";\n      toggle.title = "Toggle decorative scenery. Neural simulation remains active.";\n      toggle.setAttribute("aria-pressed", "true");\n      const feed = toolbar.querySelector(\'[data-tool="feed"]\');\n      if (feed) feed.insertAdjacentElement("afterend", toggle);\n      else toolbar.prepend(toggle);\n      toggle.addEventListener("click", function () {\n        garden.enabled = !garden.enabled;\n        toggle.textContent = garden.enabled ? "Garden: On" : "Garden: Off";\n        toggle.setAttribute("aria-pressed", String(garden.enabled));\n        const caption = document.getElementById("flytopia-garden-caption");\n        if (caption) caption.hidden = !garden.enabled;\n      });\n    }\n    if (!document.getElementById("flytopia-garden-caption")) {\n      const caption = document.createElement("div");\n      caption.id = "flytopia-garden-caption";\n      caption.textContent = "SANCTUARY GROVE / SCENERY ONLY / USE FEED FOR REAL FOOD";\n      document.body.appendChild(caption);\n    }\n  }\n    function rng(seed) {\n      let v = seed >>> 0;\n      return function () { v = (Math.imul(1664525, v) + 1013904223) >>> 0; return v / 4294967296; };\n    }\n    function leaf(c, x, y, rx, ry, tilt, fill) {\n      c.save(); c.translate(x, y); c.rotate(tilt);\n      c.beginPath(); c.ellipse(0, 0, rx, ry, 0, 0, Math.PI * 2);\n      c.fillStyle = fill; c.fill(); c.restore();\n    }\n    function clump(c, x, y, scale, seed) {\n      const random = rng(seed);\n      c.save(); c.translate(x, y); c.scale(scale, scale);\n      c.lineWidth = 3;\n      c.strokeStyle = "rgba(90, 128, 68, 0.55)";\n      for (let i = 0; i < 17; i++) {\n        const a = random() * Math.PI * 2;\n        const dist = 14 + random() * 55;\n        const xx = Math.cos(a) * dist;\n        const yy = Math.sin(a) * dist * .7;\n        c.beginPath(); c.moveTo(0, 20); c.quadraticCurveTo(xx * .5, yy * .4, xx, yy); c.stroke();\n        const palette = ["#376b45", "#467e4a", "#6ca466", "#2b5d44", "#8cad61"];\n        leaf(c, xx, yy, 15 + random() * 13, 7 + random() * 8, a, palette[Math.floor(random() * palette.length)]);\n      }\n      c.restore();\n    }\n    function banana(c, x, y, scale) {\n      c.save(); c.translate(x, y); c.scale(scale, scale);\n      c.beginPath(); c.moveTo(-35, -15); c.bezierCurveTo(-17, 15, 18, 17, 40, -20);\n      c.bezierCurveTo(14, 38, -33, 30, -35, -15); c.closePath();\n      c.fillStyle = "#f4c968"; c.fill(); c.strokeStyle = "#b18b37"; c.lineWidth = 3; c.stroke();\n      c.beginPath(); c.arc(38, -20, 3, 0, 7); c.fillStyle = "#5b4d27"; c.fill();\n      c.restore();\n    }\n    function apple(c, x, y, scale) {\n      c.save(); c.translate(x, y); c.scale(scale, scale);\n      c.fillStyle = "#c94e4b";\n      c.beginPath(); c.arc(-14, 0, 20, 0, Math.PI * 2); c.arc(13, 0, 20, 0, Math.PI * 2); c.fill();\n      c.beginPath(); c.moveTo(0, -14); c.lineTo(4, -31); c.strokeStyle = "#79552a"; c.lineWidth = 4; c.stroke();\n      leaf(c, 12, -29, 14, 6, -.45, "#78b268");\n      c.restore();\n    }\n    function berry(c, x, y, scale) {\n      c.save(); c.translate(x, y); c.scale(scale, scale);\n      c.beginPath(); c.moveTo(-20, -12); c.bezierCurveTo(-37, 5, -6, 38, 0, 41);\n      c.bezierCurveTo(7, 37, 37, 3, 20, -12); c.quadraticCurveTo(0, -27, -20, -12); c.closePath();\n      c.fillStyle = "#dc6566"; c.fill();\n      c.fillStyle = "#f8d797";\n      for (let i = -1; i <= 1; i++) for (let j = 0; j < 2; j++) {\n        c.beginPath(); c.ellipse(i*9+(j?4:0), -1+j*16, 2, 3.2, -.25, 0, Math.PI*2); c.fill();\n      }\n      for (let i = -1; i <= 1; i++) leaf(c, i * 12, -19, 13, 5, i*.65, "#6ba75f");\n      c.restore();\n    }\n    function patch(c, x, y, size, kind, label) {\n      const glow = c.createRadialGradient(x, y, 3, x, y, size*1.4);\n      glow.addColorStop(0, "rgba(185, 219, 137, .16)");\n      glow.addColorStop(1, "rgba(42, 85, 46, 0)");\n      c.fillStyle = glow; c.fillRect(x-size*1.5, y-size*1.5, size*3, size*3);\n      clump(c, x, y + 20, .48 * size/65, Math.round(x*10));\n      const draw = kind === "banana" ? banana : kind === "apple" ? apple : berry;\n      draw(c, x, y-13, Math.min(1.1, Math.max(.65, size/65)));\n      c.textAlign = "center"; c.font = "600 12px system-ui, sans-serif";\n      c.fillStyle = "rgba(242, 250, 217, 0.88)"; c.fillText(label, x, y + size*.95);\n    }\n    function paint(c, w, h) {\n      c.clearRect(0, 0, w, h);\n      const wash = c.createLinearGradient(0, 0, 0, h);\n      wash.addColorStop(0, "rgba(39, 94, 71, .36)");\n      wash.addColorStop(.55, "rgba(25, 78, 51, .48)");\n      wash.addColorStop(1, "rgba(39, 86, 58, .53)");\n      c.fillStyle = wash; c.fillRect(0, 0, w, h);\n      const sunshine = c.createRadialGradient(w*.61, -h*.08, 0, w*.61, -h*.08, Math.max(w,h)*.56);\n      sunshine.addColorStop(0, "rgba(254, 230, 144, .29)");\n      sunshine.addColorStop(.65, "rgba(194, 205, 133, .07)");\n      sunshine.addColorStop(1, "rgba(194, 205, 133, 0)");\n      c.fillStyle = sunshine; c.fillRect(0, 0, w, h);\n      // A gently winding path. Kept translucent so it never hides the fly.\n      c.beginPath(); c.moveTo(w*.06, h*.73); c.bezierCurveTo(w*.32, h*.76, w*.42, h*.39, w*.73, h*.37);\n      c.strokeStyle = "rgba(226, 210, 158, .10)"; c.lineWidth = Math.min(80,w*.075); c.stroke();\n      c.strokeStyle = "rgba(247, 235, 189, .14)"; c.lineWidth = 1.5; c.stroke();\n      // Soft foliage stays near the perimeter: this is still a simulation viewport.\n      const k = Math.max(.6, Math.min(1.45, w/1300));\n      clump(c, w*.03, h*.09, 1.7*k, 62);\n      clump(c, w*.95, h*.04, 1.55*k, 82);\n      clump(c, w*.02, h*.77, 1.5*k, 98);\n      clump(c, w*.98, h*.77, 1.7*k, 141);\n      clump(c, w*.4, h*.99, 1.35*k, 132);\n      // A tiny pond, also decorative for now.\n      c.save(); c.translate(w*.81, h*.78);\n      c.beginPath(); c.ellipse(0, 0, 80*k, 29*k, -.13, 0, Math.PI*2);\n      c.fillStyle = "rgba(98, 176, 177, .44)"; c.fill();\n      c.strokeStyle = "rgba(167, 213, 174, .6)"; c.lineWidth = 3; c.stroke();\n      c.beginPath(); c.ellipse(-9*k, -5*k, 34*k, 7*k, -.13, 0, Math.PI*2);\n      c.strokeStyle = "rgba(212, 251, 216, .3)"; c.lineWidth = 2; c.stroke();\n      c.restore();\n      c.font = "600 12px system-ui, sans-serif"; c.fillStyle = "rgba(238, 249, 229, .8)";\n      c.textAlign = "center"; c.fillText("Quiet pond (scenery)", w*.81, h*.78+48*k);\n      // Fruit pictured here is art. Real food comes from the native Feed tool.\n      patch(c, w*.18, h*.5, 65*k, "banana", "Banana grove");\n      patch(c, w*.63, h*.22, 58*k, "apple", "Apple clearing");\n      patch(c, w*.61, h*.83, 57*k, "berry", "Berry meadow");\n      // A few fireflies / flowers, seeded for a reproducible scene.\n      const random = rng(20261007);\n      for (let i = 0; i < 65; i++) {\n        const x = random()*w, y = random()*h;\n        c.beginPath(); c.arc(x, y, 1+random()*2, 0, Math.PI*2);\n        c.fillStyle = i%3 === 0 ? "rgba(253, 230, 156, .54)" : "rgba(175, 226, 159, .24)"; c.fill();\n      }\n    }\n  if (document.readyState === "loading") {\n    document.addEventListener("DOMContentLoaded", setupUI, {once:true});\n  } else setupUI();\n})();\n'
GARDEN_CSS = '/* Flytopia v0.3: the garden is painted in main.js BEFORE food and the fly.\n   No full-screen overlay or high z-index. */\n#flytopia-garden-layer { display: none !important; }\n#flytopia-garden-caption {\n  position: fixed;\n  left: 14px;\n  bottom: 192px;\n  z-index: 12;\n  pointer-events: none;\n  max-width: calc(100vw - 40px);\n  border-radius: 999px;\n  border: 1px solid rgba(190, 227, 174, 0.3);\n  background: rgba(12, 38, 29, 0.82);\n  color: #e8f5dc;\n  font: 650 10px/1.3 system-ui, -apple-system, sans-serif;\n  letter-spacing: .04em;\n  padding: 7px 12px;\n}\n#flytopia-garden-caption[hidden] { display: none !important; }\n#flytopia-garden-toggle { white-space: nowrap; }\n#flytopia-garden-toggle[aria-pressed="false"] { opacity: 0.7; }\n@media(max-width:768px) {\n  #flytopia-garden-caption { left: 8px; bottom: 132px; font-size: 9px; padding: 5px 8px; }\n}\n@media (orientation: landscape) and (max-height:500px) {\n  #flytopia-garden-caption { bottom: 12px; max-width:calc(100vw - 310px); }\n}\n'

ANCHOR = "\tctx.translate(-cx, -cy);\n\n\tdrawFood();"
HOOK = "\tctx.translate(-cx, -cy);\n\n\t// Flytopia v0.3: draw garden beneath native food and fly rendering.\n\tif (window.FlytopiaGarden && window.FlytopiaGarden.enabled) {\n\t\twindow.FlytopiaGarden.draw(ctx, window.innerWidth, window.innerHeight);\n\t}\n\n\tdrawFood();"
REL_PATHS = ["index.html", "js/main.js", "css/flytopia-garden.css", "js/flytopia-garden.js"]
BACKUP_DIR = ".flytopia-backups/v03-before-fix"

def verify_repo(repo):
    for rel in REL_PATHS:
        if not (repo / rel).is_file():
            sys.exit(f"ERROR: Missing {rel}. Run this from the Flytopia repository root, after v0.2.")

def rollback(repo):
    archive = repo / BACKUP_DIR
    if not all((archive / rel).is_file() for rel in REL_PATHS):
        sys.exit("ERROR: No complete v0.3 backup exists in this repository.")
    for rel in REL_PATHS:
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(archive / rel, target)
    print("RESTORED v0.2 files from .flytopia-backups/v03-before-fix")
    print("Hard-refresh the browser. Note: this brings back the v0.2 overlay issue.")

def main():
    repo = Path.cwd()
    if len(sys.argv) > 1:
        if sys.argv[1:] == ["--rollback"]:
            rollback(repo)
            return
        sys.exit("Usage: python3 flytopia_fix_v03.py [--rollback]")
    verify_repo(repo)
    mainpath = repo / "js/main.js"
    original_main = mainpath.read_text(encoding="utf-8")
    indexpath = repo / "index.html"
    original_index = indexpath.read_text(encoding="utf-8")
    old_garden = (repo / "js/flytopia-garden.js").read_text(encoding="utf-8")

    if HOOK in original_main and "flytopia-garden.js?v=3" in original_index:
        print("Already installed. Nothing changed.")
        return
    if original_main.count(ANCHOR) != 1 or HOOK in original_main:
        sys.exit("ERROR: The FlyBrain draw() function differs from the expected v0.2 source. No changes made; share your local js/main.js to adapt the patch.")
    if not old_garden.startswith("/* Flytopia v0.2"):
        sys.exit("ERROR: js/flytopia-garden.js differs from the v0.2 installer. No changes made; please share your local copy.")
    if "./js/flytopia-garden.js?v=2" not in original_index or "./css/flytopia-garden.css?v=2" not in original_index:
        sys.exit("ERROR: Expected v0.2 garden stylesheet and script links in index.html. No changes made.")
    new_main = original_main.replace(ANCHOR, HOOK, 1)
    new_index = original_index.replace("./js/flytopia-garden.js?v=2", "./js/flytopia-garden.js?v=3").replace("./css/flytopia-garden.css?v=2", "./css/flytopia-garden.css?v=3")

    archive = repo / BACKUP_DIR
    if archive.exists() and any((archive / rel).exists() for rel in REL_PATHS):
        sys.exit("ERROR: A v0.3 backup already exists but the patch isn't fully installed. No changes made; inspect .flytopia-backups before retrying.")
    for rel in REL_PATHS:
        destination = archive / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo / rel, destination)
    mainpath.write_text(new_main, encoding="utf-8")
    indexpath.write_text(new_index, encoding="utf-8")
    (repo / "js/flytopia-garden.js").write_text(GARDEN_JS, encoding="utf-8")
    (repo / "css/flytopia-garden.css").write_text(GARDEN_CSS, encoding="utf-8")
    print("SUCCESS: Flytopia v0.3 garden fix installed.")
    print("Garden is now painted inside the original canvas, behind native food and fly.")
    print("Changed: js/main.js (one render hook), js/flytopia-garden.js, css/flytopia-garden.css, index.html (cache-busting).")
    print("Unchanged: neural connectome, worker, motor behavior, css/main.css.")
    print("Backup: .flytopia-backups/v03-before-fix")
    print("Reload http://localhost:8000 with Cmd+Shift+R.")

if __name__ == "__main__":
    main()
