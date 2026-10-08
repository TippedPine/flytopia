/* Flytopia v0.5 — Odor-field visualization and optional BOOLEAN foodNearby cue.
   This is a deliberately simplified scent model; it is not a fluid solver,
   left/right olfactory sensor array, or direct neural firing-rate stimulus.
   All real motion and feeding remain in FlyBrain's original main.js/brain code. */
(function () {
  'use strict';
  var display = true;
  var cueOn = false;
  var latest = {strength: 0, nativeNear: false, cueApplied: false, closest: null};
  var hud, overlayButton, cueButton;
  var lastHudAt = 0;
  var THRESHOLD = 0.29;
  var MAX_SOURCES = 16;

  // Wind always blows gently toward canvas right. IMPORTANT: illustrative
  // for orchard odor only; it does NOT trigger FlyBrain's wind stimulus.
  var windX = 1;
  function strengthAt(x, y, f) {
    var along = (x - f.x) * windX;
    var across = y - f.y;
    var alongSigma = along >= 0 ? 165 : 42;
    var crossSigma = 39 + Math.max(0, along) * 0.20;
    var s = Math.exp(-0.5 * (along * along / (alongSigma * alongSigma) +
                           across * across / (crossSigma * crossSigma)));
    return Math.max(0, Math.min(1, s));
  }
  function sample(x, y, items) {
    var maximum = 0;
    var nearest = null;
    if (!Array.isArray(items)) return {strength: 0, closest: null};
    for (var i = 0; i < items.length; i++) {
      var f = items[i];
      if (!f || !Number.isFinite(f.x) || !Number.isFinite(f.y)) continue;
      var value = strengthAt(x, y, f);
      if (value > maximum) { maximum = value; nearest = f; }
    }
    return {strength: maximum, closest: nearest};
  }
  function update(items, fly, brain) {
    if (!fly || !brain || !brain.stimulate) return;
    var sensor = sample(fly.x, fly.y, items);
    // Native FlyBrain proximity is computed earlier in main.js each frame.
    var nativeNear = Boolean(brain.stimulate.foodNearby);
    var isDetected = cueOn && sensor.strength >= THRESHOLD;
    // Never touch foodContact, drives, motor values, or neuron state.
    if (isDetected) brain.stimulate.foodNearby = true;
    latest = {strength: sensor.strength, nativeNear: nativeNear,
              cueApplied: isDetected && !nativeNear, closest: sensor.closest};
    var now = Date.now();
    if (hud && now - lastHudAt > 200) {
      lastHudAt = now;
      var percent = Math.round(sensor.strength * 100);
      hud.querySelector('[data-sense-strength]').textContent = percent + '%';
      hud.querySelector('[data-sense-near]').textContent = nativeNear ? 'YES (native)' :
        (latest.cueApplied ? 'YES (odor cue)' : 'NO');
      hud.querySelector('[data-sense-mode]').textContent = cueOn ? 'ON — simplified boolean input' : 'OFF — observation only';
      hud.querySelector('[data-sense-meter]').style.width = percent + '%';
    }
  }
  function draw(ctx, items, fly) {
    if (!display || !Array.isArray(items) || !ctx) return;
    ctx.save();
    // Overlay is in the original WORLD coordinate system, so it moves with
    // zoom and pan and never sits on top of the original fly artwork.
    var count = Math.min(items.length, MAX_SOURCES);
    for (var i = 0; i < count; i++) {
      var f = items[i];
      if (!f || !Number.isFinite(f.x) || !Number.isFinite(f.y)) continue;
      ctx.save();
      ctx.translate(f.x, f.y);
      // Anisotropic soft plume with a long downwind tail and short upwind reach.
      ctx.scale(1.0, 0.60);
      var plume = ctx.createRadialGradient(42, 0, 0, 42, 0, 198);
      plume.addColorStop(0, 'rgba(131, 248, 158, 0.19)');
      plume.addColorStop(0.33, 'rgba(116, 234, 158, 0.12)');
      plume.addColorStop(0.72, 'rgba(65, 195, 146, 0.045)');
      plume.addColorStop(1, 'rgba(49, 186, 130, 0)');
      ctx.fillStyle = plume;
      ctx.fillRect(-160, -210, 425, 420);
      ctx.restore();
      ctx.save();
      ctx.translate(f.x + 38, f.y);
      ctx.strokeStyle = 'rgba(164, 252, 183, .23)';
      ctx.lineWidth = 1;
      for (var k = 0; k < 3; k++) {
        ctx.beginPath();
        ctx.ellipse(0, 0, 62 + k * 52, 25 + k * 22, 0, -Math.PI * 0.75, Math.PI * 0.75);
        ctx.stroke();
      }
      ctx.restore();
    }
    if (fly && Number.isFinite(fly.x) && Number.isFinite(fly.y)) {
      var strength = latest.strength;
      ctx.beginPath();
      ctx.arc(fly.x, fly.y, 32, 0, Math.PI * 2);
      ctx.lineWidth = 2;
      ctx.strokeStyle = strength >= THRESHOLD ? 'rgba(190,255,133,.84)' : 'rgba(139,239,205,.42)';
      ctx.setLineDash([4, 5]);
      ctx.stroke();
      ctx.setLineDash([]);
    }
    ctx.restore();
  }
  function styleUI() {
    if (document.getElementById('flytopia-senses-style')) return;
    var style = document.createElement('style');
    style.id = 'flytopia-senses-style';
    style.textContent = '\n#flytopia-senses-hud{position:fixed;z-index:17;left:16px;top:59px;pointer-events:none;max-width:min(270px,46vw);padding:12px 14px;border:1px solid rgba(160,221,171,.4);border-radius:14px;color:#e8f7e5;background:rgba(11,41,32,.89);box-shadow:0 8px 25px rgba(0,0,0,.22);font:12px/1.5 system-ui,-apple-system,sans-serif;letter-spacing:0}#flytopia-senses-hud .sense-title{color:#c4edc2;font-size:10px;font-weight:800;letter-spacing:.12em}#flytopia-senses-hud .sense-row{display:flex;justify-content:space-between;gap:15px;margin-top:6px}#flytopia-senses-hud .sense-row strong{text-align:right}#flytopia-senses-hud .sense-track{height:6px;border-radius:5px;background:rgba(255,255,255,.13);overflow:hidden;margin:6px 0}#flytopia-senses-hud .sense-fill{height:100%;background:linear-gradient(90deg,#73bd89,#c6ed8e);width:0%;transition:width .2s}#flytopia-senses-hud .sense-note{color:#b5d2bc;font-size:10px;margin-top:8px}#flytopia-senses-hud[hidden]{display:none!important}@media(max-width:920px){#flytopia-senses-hud{top:56px;max-width:205px;padding:7px 9px;font-size:10px}#flytopia-senses-hud .sense-note{font-size:9px}}';
    document.head.appendChild(style);
  }
  function setupUI() {
    if (document.getElementById('flytopia-senses-toggle')) return;
    styleUI();
    var toolbar = document.querySelector('#toolbar .toolbar-left');
    if (!toolbar) return;
    overlayButton = document.createElement('button');
    overlayButton.id = 'flytopia-senses-toggle';
    overlayButton.className = 'tool-btn';
    overlayButton.type = 'button';
    overlayButton.textContent = 'Fly Senses: On';
    overlayButton.title = 'Toggle conceptual scent plume visualization without changing neural activity.';
    overlayButton.setAttribute('aria-pressed', 'true');
    cueButton = document.createElement('button');
    cueButton.id = 'flytopia-odor-cue-toggle';
    cueButton.className = 'tool-btn';
    cueButton.type = 'button';
    cueButton.textContent = 'Odor Cue: Off';
    cueButton.title = 'Opt in to extending FlyBrain foodNearby via a simple scent threshold; keeps original foodContact unchanged.';
    cueButton.setAttribute('aria-pressed', 'false');
    var after = document.getElementById('flytopia-orchard-toggle');
    if (after) { after.insertAdjacentElement('afterend', overlayButton); overlayButton.insertAdjacentElement('afterend', cueButton); }
    else { toolbar.appendChild(overlayButton); toolbar.appendChild(cueButton); }
    hud = document.createElement('section');
    hud.id = 'flytopia-senses-hud';
    hud.setAttribute('aria-label', 'Fly senses data');
    hud.innerHTML = '<div class="sense-title">FLY SENSES · V0.5</div>' +
      '<div class="sense-row"><span>Odor at fly</span><strong data-sense-strength>0%</strong></div>' +
      '<div class="sense-track"><div class="sense-fill" data-sense-meter></div></div>' +
      '<div class="sense-row"><span>Food nearby</span><strong data-sense-near>NO</strong></div>' +
      '<div class="sense-row"><span>Odor cue</span><strong data-sense-mode>OFF — observation only</strong></div>' +
      '<div class="sense-note">Gentle scent flows right → (illustrative). Visualization ≠ neural activity.</div>';
    document.body.appendChild(hud);
    overlayButton.addEventListener('click', function () {
      display = !display;
      overlayButton.textContent = display ? 'Fly Senses: On' : 'Fly Senses: Off';
      overlayButton.setAttribute('aria-pressed', String(display));
      hud.hidden = !display;
    });
    cueButton.addEventListener('click', function () {
      cueOn = !cueOn;
      cueButton.textContent = cueOn ? 'Odor Cue: On' : 'Odor Cue: Off';
      cueButton.setAttribute('aria-pressed', String(cueOn));
    });
  }
  window.FlytopiaSenses = {update: update, draw: draw, sample: sample,
                           strengthAt: strengthAt, getState: function () {return {display:display, cueOn:cueOn, latest:latest};}};
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupUI, {once: true});
  } else setupUI();
})();
