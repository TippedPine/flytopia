/* Flytopia v0.2 — a scene overlay, not a sensory simulation. */
(function () {
  "use strict";
  function start() {
    const original = document.getElementById("canvas");
    const toolbar = document.querySelector("#toolbar .toolbar-left");
    if (!original || !toolbar || document.getElementById("flytopia-garden-layer")) return;

    const layer = document.createElement("div");
    layer.id = "flytopia-garden-layer";
    layer.setAttribute("aria-hidden", "true");
    const scene = document.createElement("canvas");
    const caption = document.createElement("div");
    caption.id = "flytopia-garden-caption";
    caption.textContent = "SANCTUARY GROVE  /  SCENERY ONLY  /  USE FEED TO PLACE REAL FOOD";
    layer.append(scene, caption);
    document.body.appendChild(layer);

    const toggle = document.createElement("button");
    toggle.id = "flytopia-garden-toggle";
    toggle.type = "button";
    toggle.className = "tool-btn";
    toggle.textContent = "Garden: On";
    toggle.title = "Toggle the visual garden. It does not change neural stimuli.";
    toggle.setAttribute("aria-pressed", "true");
    const feed = toolbar.querySelector('[data-tool="feed"]');
    if (feed) feed.insertAdjacentElement("afterend", toggle);
    else toolbar.prepend(toggle);
    toggle.addEventListener("click", function () {
      const on = layer.hidden;
      layer.hidden = !on;
      toggle.textContent = on ? "Garden: On" : "Garden: Off";
      toggle.setAttribute("aria-pressed", String(on));
      if (on) sync();
    });

    const ctx = scene.getContext("2d");
    if (!ctx) {
      caption.textContent = "Garden scene requires 2D canvas support.";
      return;
    }
    let last = "";
    function sync() {
      const r = original.getBoundingClientRect();
      if (!(r.width > 0 && r.height > 0)) return;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const key = [r.left, r.top, r.width, r.height, dpr].map(n => n.toFixed(2)).join("|");
      if (key === last) return;
      last = key;
      layer.style.left = r.left + "px";
      layer.style.top = r.top + "px";
      layer.style.width = r.width + "px";
      layer.style.height = r.height + "px";
      scene.width = Math.max(1, Math.round(r.width * dpr));
      scene.height = Math.max(1, Math.round(r.height * dpr));
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      paint(ctx, r.width, r.height);
    }
    function rng(seed) {
      let v = seed >>> 0;
      return function () { v = (Math.imul(1664525, v) + 1013904223) >>> 0; return v / 4294967296; };
    }
    function leaf(c, x, y, rx, ry, tilt, fill) {
      c.save(); c.translate(x, y); c.rotate(tilt);
      c.beginPath(); c.ellipse(0, 0, rx, ry, 0, 0, Math.PI * 2);
      c.fillStyle = fill; c.fill(); c.restore();
    }
    function clump(c, x, y, scale, seed) {
      const random = rng(seed);
      c.save(); c.translate(x, y); c.scale(scale, scale);
      c.lineWidth = 3;
      c.strokeStyle = "rgba(90, 128, 68, 0.55)";
      for (let i = 0; i < 17; i++) {
        const a = random() * Math.PI * 2;
        const dist = 14 + random() * 55;
        const xx = Math.cos(a) * dist;
        const yy = Math.sin(a) * dist * .7;
        c.beginPath(); c.moveTo(0, 20); c.quadraticCurveTo(xx * .5, yy * .4, xx, yy); c.stroke();
        const palette = ["#376b45", "#467e4a", "#6ca466", "#2b5d44", "#8cad61"];
        leaf(c, xx, yy, 15 + random() * 13, 7 + random() * 8, a, palette[Math.floor(random() * palette.length)]);
      }
      c.restore();
    }
    function banana(c, x, y, scale) {
      c.save(); c.translate(x, y); c.scale(scale, scale);
      c.beginPath(); c.moveTo(-35, -15); c.bezierCurveTo(-17, 15, 18, 17, 40, -20);
      c.bezierCurveTo(14, 38, -33, 30, -35, -15); c.closePath();
      c.fillStyle = "#f4c968"; c.fill(); c.strokeStyle = "#b18b37"; c.lineWidth = 3; c.stroke();
      c.beginPath(); c.arc(38, -20, 3, 0, 7); c.fillStyle = "#5b4d27"; c.fill();
      c.restore();
    }
    function apple(c, x, y, scale) {
      c.save(); c.translate(x, y); c.scale(scale, scale);
      c.fillStyle = "#c94e4b";
      c.beginPath(); c.arc(-14, 0, 20, 0, Math.PI * 2); c.arc(13, 0, 20, 0, Math.PI * 2); c.fill();
      c.beginPath(); c.moveTo(0, -14); c.lineTo(4, -31); c.strokeStyle = "#79552a"; c.lineWidth = 4; c.stroke();
      leaf(c, 12, -29, 14, 6, -.45, "#78b268");
      c.restore();
    }
    function berry(c, x, y, scale) {
      c.save(); c.translate(x, y); c.scale(scale, scale);
      c.beginPath(); c.moveTo(-20, -12); c.bezierCurveTo(-37, 5, -6, 38, 0, 41);
      c.bezierCurveTo(7, 37, 37, 3, 20, -12); c.quadraticCurveTo(0, -27, -20, -12); c.closePath();
      c.fillStyle = "#dc6566"; c.fill();
      c.fillStyle = "#f8d797";
      for (let i = -1; i <= 1; i++) for (let j = 0; j < 2; j++) {
        c.beginPath(); c.ellipse(i*9+(j?4:0), -1+j*16, 2, 3.2, -.25, 0, Math.PI*2); c.fill();
      }
      for (let i = -1; i <= 1; i++) leaf(c, i * 12, -19, 13, 5, i*.65, "#6ba75f");
      c.restore();
    }
    function patch(c, x, y, size, kind, label) {
      const glow = c.createRadialGradient(x, y, 3, x, y, size*1.4);
      glow.addColorStop(0, "rgba(185, 219, 137, .16)");
      glow.addColorStop(1, "rgba(42, 85, 46, 0)");
      c.fillStyle = glow; c.fillRect(x-size*1.5, y-size*1.5, size*3, size*3);
      clump(c, x, y + 20, .48 * size/65, Math.round(x*10));
      const draw = kind === "banana" ? banana : kind === "apple" ? apple : berry;
      draw(c, x, y-13, Math.min(1.1, Math.max(.65, size/65)));
      c.textAlign = "center"; c.font = "600 12px system-ui, sans-serif";
      c.fillStyle = "rgba(242, 250, 217, 0.88)"; c.fillText(label, x, y + size*.95);
    }
    function paint(c, w, h) {
      c.clearRect(0, 0, w, h);
      const wash = c.createLinearGradient(0, 0, 0, h);
      wash.addColorStop(0, "rgba(39, 94, 71, .36)");
      wash.addColorStop(.55, "rgba(25, 78, 51, .48)");
      wash.addColorStop(1, "rgba(39, 86, 58, .53)");
      c.fillStyle = wash; c.fillRect(0, 0, w, h);
      const sunshine = c.createRadialGradient(w*.61, -h*.08, 0, w*.61, -h*.08, Math.max(w,h)*.56);
      sunshine.addColorStop(0, "rgba(254, 230, 144, .29)");
      sunshine.addColorStop(.65, "rgba(194, 205, 133, .07)");
      sunshine.addColorStop(1, "rgba(194, 205, 133, 0)");
      c.fillStyle = sunshine; c.fillRect(0, 0, w, h);
      // A gently winding path. Kept translucent so it never hides the fly.
      c.beginPath(); c.moveTo(w*.06, h*.73); c.bezierCurveTo(w*.32, h*.76, w*.42, h*.39, w*.73, h*.37);
      c.strokeStyle = "rgba(226, 210, 158, .10)"; c.lineWidth = Math.min(80,w*.075); c.stroke();
      c.strokeStyle = "rgba(247, 235, 189, .14)"; c.lineWidth = 1.5; c.stroke();
      // Soft foliage stays near the perimeter: this is still a simulation viewport.
      const k = Math.max(.6, Math.min(1.45, w/1300));
      clump(c, w*.03, h*.09, 1.7*k, 62);
      clump(c, w*.95, h*.04, 1.55*k, 82);
      clump(c, w*.02, h*.77, 1.5*k, 98);
      clump(c, w*.98, h*.77, 1.7*k, 141);
      clump(c, w*.4, h*.99, 1.35*k, 132);
      // A tiny pond, also decorative for now.
      c.save(); c.translate(w*.81, h*.78);
      c.beginPath(); c.ellipse(0, 0, 80*k, 29*k, -.13, 0, Math.PI*2);
      c.fillStyle = "rgba(98, 176, 177, .44)"; c.fill();
      c.strokeStyle = "rgba(167, 213, 174, .6)"; c.lineWidth = 3; c.stroke();
      c.beginPath(); c.ellipse(-9*k, -5*k, 34*k, 7*k, -.13, 0, Math.PI*2);
      c.strokeStyle = "rgba(212, 251, 216, .3)"; c.lineWidth = 2; c.stroke();
      c.restore();
      c.font = "600 12px system-ui, sans-serif"; c.fillStyle = "rgba(238, 249, 229, .8)";
      c.textAlign = "center"; c.fillText("Quiet pond (scenery)", w*.81, h*.78+48*k);
      // Fruit pictured here is art. Real food comes from the native Feed tool.
      patch(c, w*.18, h*.5, 65*k, "banana", "Banana grove");
      patch(c, w*.63, h*.22, 58*k, "apple", "Apple clearing");
      patch(c, w*.61, h*.83, 57*k, "berry", "Berry meadow");
      // A few fireflies / flowers, seeded for a reproducible scene.
      const random = rng(20261007);
      for (let i = 0; i < 65; i++) {
        const x = random()*w, y = random()*h;
        c.beginPath(); c.arc(x, y, 1+random()*2, 0, Math.PI*2);
        c.fillStyle = i%3 === 0 ? "rgba(253, 230, 156, .54)" : "rgba(175, 226, 159, .24)"; c.fill();
      }
    }
    window.addEventListener("resize", sync);
    window.addEventListener("scroll", sync, {passive: true});
    if ("ResizeObserver" in window) new ResizeObserver(sync).observe(original);
    document.addEventListener("click", function () { window.requestAnimationFrame(sync); }, true);
    window.requestAnimationFrame(sync);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, {once: true});
  } else start();
})();
