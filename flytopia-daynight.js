/* Flytopia v0.6: Day/night cycle and shaded resting grove.
   Uses FlyBrain's real scalar BRAIN.stimulate.lightLevel sensory input.
   It does not force behavior, simulate circadian neurons, or create sleep states. */
(function () {
  'use strict';
  var TOTAL_SECONDS = 24 * 60;           // one simulated day = 24 real minutes
  var hour = 8;                          // start at 08:00 in Flytopia
  var enabled = true;
  var paused = false;
  var lastFrame = null;
  var currentAmbient = 1;
  var currentSensor = 1;
  var inGrove = false;
  var shadeStrength = 0;
  var lastHudUpdate = 0;
  var ui = {};
  var TWO_PI = Math.PI * 2;

  function clamp(n, lo, hi) { return Math.max(lo, Math.min(hi, n)); }
  function smoothstep(x) { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); }
  function ambientForHour(t) {
    // Solar altitude is zero at 06:00 and 18:00, with smooth twilight.
    var altitude = Math.sin((t - 6) * TWO_PI / 24);
    return smoothstep((altitude + 0.25) / 0.5);
  }
  function groveGeometry(w, h) {
    return { x: w * 0.40, y: h * 0.64, radius: clamp(Math.min(w, h) * 0.145, 75, 135) };
  }
  function getGroveShade(fly, w, h) {
    if (!fly || !Number.isFinite(fly.x) || !Number.isFinite(fly.y)) return 0;
    var grove = groveGeometry(w, h);
    var distance = Math.hypot(fly.x - grove.x, fly.y - grove.y);
    // Smooth transition from open sunlight to the shaded grove.
    return 1 - smoothstep((distance - grove.radius * 0.55) / (grove.radius * 0.45));
  }
  function labelForHour(t) {
    if (t >= 5.5 && t < 8) return 'Sunrise';
    if (t >= 8 && t < 17) return 'Daytime';
    if (t >= 17 && t < 19.5) return 'Sunset';
    return 'Nighttime';
  }
  function hhmm(t) {
    var minutes = Math.floor((t * 60 + 0.00001) % 1440);
    var hh = String(Math.floor(minutes / 60)).padStart(2, '0');
    var mm = String(minutes % 60).padStart(2, '0');
    return hh + ':' + mm;
  }
  function updateLightButton() {
    var light = document.getElementById('lightBtn');
    if (!light) return;
    if (enabled) {
      light.textContent = 'Light: Auto';
      light.title = 'Using Flytopia daylight. Click to return to manual light settings.';
    } else {
      if (typeof lightLabels !== 'undefined' && typeof lightStateIndex !== 'undefined') {
        light.textContent = 'Light: ' + lightLabels[lightStateIndex];
      }
      light.title = 'Manual light setting';
    }
  }
  function syncControls() {
    if (ui.toggle) {
      ui.toggle.textContent = 'Day/Night: ' + (enabled ? 'On' : 'Off');
      ui.toggle.setAttribute('aria-pressed', String(enabled));
    }
    if (ui.pause) {
      ui.pause.textContent = paused ? 'Resume clock' : 'Pause clock';
      ui.pause.disabled = !enabled;
    }
    if (ui.skip) ui.skip.disabled = !enabled;
    if (ui.panel) ui.panel.hidden = !enabled;
    updateLightButton();
  }
  function startOrStop(on) {
    enabled = Boolean(on);
    lastFrame = null; // No catch-up jump after a pause or tab switch.
    if (!enabled && typeof BRAIN !== 'undefined' && BRAIN.stimulate &&
        typeof lightStates !== 'undefined' && typeof lightStateIndex !== 'undefined') {
      BRAIN.stimulate.lightLevel = lightStates[lightStateIndex];
    }
    syncControls();
  }
  function renderHud() {
    if (!ui.panel || !enabled) return;
    ui.time.textContent = hhmm(hour);
    ui.phase.textContent = labelForHour(hour);
    ui.light.textContent = Math.round(currentSensor * 100) + '%';
    ui.grove.textContent = shadeStrength > 0.5 ? 'Under the canopy' : 'Open garden';
    ui.grove.title = 'Grove shade reduces sensed light only; no rest is forced.';
    ui.meter.style.width = (hour / 24 * 100).toFixed(2) + '%';
    ui.status.textContent = paused ? 'Clock paused' : '1 real minute = 1 Flytopia hour';
  }
  function update(brain, fly, w, h, now) {
    if (!brain || !brain.stimulate) return;
    if (!Number.isFinite(now)) now = performance.now();
    if (lastFrame === null) lastFrame = now;
    // Time advances only while the tab is visible, enabled and unpaused.
    var elapsed = clamp((now - lastFrame) / 1000, 0, 0.25);
    lastFrame = now;
    if (document.hidden) elapsed = 0;
    if (enabled && !paused) hour = (hour + elapsed * 24 / TOTAL_SECONDS) % 24;
    if (!enabled) return;
    currentAmbient = ambientForHour(hour);
    shadeStrength = getGroveShade(fly, w, h);
    inGrove = shadeStrength > 0.5;
    // Single existing scalar light input: not a full retinal/visual model.
    currentSensor = currentAmbient * (1 - 0.58 * shadeStrength);
    brain.stimulate.lightLevel = currentSensor;
    // 'Light: Auto' is intentional; don't pretend it is a discrete Bright/Dim state.
    if (now - lastHudUpdate > 200) { lastHudUpdate = now; renderHud(); }
  }

  function drawGrove(ctx, w, h) {
    if (!enabled) return;
    var g = groveGeometry(w, h);
    ctx.save();
    var glow = ctx.createRadialGradient(g.x, g.y, 8, g.x, g.y, g.radius * 1.33);
    glow.addColorStop(0, 'rgba(7, 37, 28, 0.42)');
    glow.addColorStop(0.6, 'rgba(8, 48, 35, 0.22)');
    glow.addColorStop(1, 'rgba(9, 43, 31, 0)');
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(g.x, g.y, g.radius * 1.33, 0, TWO_PI);
    ctx.fill();
    // Layered leaf canopy; all geometry remains beneath the fly artwork.
    for (var j = 0; j < 11; j++) {
      var a = TWO_PI * j / 11;
      var leafX = g.x + Math.cos(a) * g.radius * 0.78;
      var leafY = g.y + Math.sin(a) * g.radius * 0.48;
      ctx.save();
      ctx.translate(leafX, leafY);
      ctx.rotate(a);
      ctx.beginPath();
      ctx.ellipse(0, 0, g.radius * 0.28, g.radius * 0.145, 0, 0, TWO_PI);
      ctx.fillStyle = j % 3 === 0 ? 'rgba(89,151,99,.55)' :
                      j % 2 === 0 ? 'rgba(65,121,77,.60)' : 'rgba(40,102,67,.68)';
      ctx.fill();
      ctx.restore();
    }
    ctx.fillStyle = 'rgba(220,251,206,.93)';
    ctx.font = '600 13px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Shaded resting grove', g.x, g.y + g.radius * 0.67);
    ctx.fillStyle = 'rgba(211,237,209,.76)';
    ctx.font = '11px system-ui, sans-serif';
    ctx.fillText('Cool shade, no forced sleep', g.x, g.y + g.radius * 0.67 + 17);
    ctx.restore();
  }

  function drawAtmosphere(ctx, w, h) {
    if (!enabled) return;
    ctx.save();
    // The lighting filter covers the original canvas, including the fly.
    var dark = 0.47 * (1 - currentAmbient);
    if (dark > 0.001) {
      ctx.fillStyle = 'rgba(3,12,37,' + dark.toFixed(3) + ')';
      ctx.fillRect(0, 0, w, h);
      var moon = ctx.createRadialGradient(w * .84, h * .22, 5, w * .84, h * .22, w * .49);
      moon.addColorStop(0, 'rgba(136,178,246,' + (.12 * (1 - currentAmbient)).toFixed(3) + ')');
      moon.addColorStop(1, 'rgba(75,112,202,0)');
      ctx.fillStyle = moon;
      ctx.fillRect(0, 0, w, h);
    }
    if (hour >= 5 && hour < 8 || hour >= 17 && hour < 20) {
      var tint = (.08 * (1 - Math.abs(Math.sin((hour-6)*TWO_PI/24)))).toFixed(3);
      ctx.fillStyle = 'rgba(241,153,82,' + tint + ')';
      ctx.fillRect(0, 0, w, h);
    }
    ctx.restore();
  }

  function buildUI() {
    var toolbar = document.querySelector('#toolbar .toolbar-left');
    var light = document.getElementById('lightBtn');
    if (!toolbar || !light || document.getElementById('flytopia-daynight-toggle')) return;
    var toggle = document.createElement('button');
    toggle.className = 'tool-btn';
    toggle.id = 'flytopia-daynight-toggle';
    toggle.type = 'button';
    toggle.addEventListener('click', function () { startOrStop(!enabled); });
    toolbar.insertBefore(toggle, light);
    ui.toggle = toggle;

    var panel = document.createElement('section');
    panel.id = 'flytopia-daynight-panel';
    panel.className = 'flytopia-daynight-panel';
    panel.setAttribute('aria-label', 'Flytopia day and night clock');
    panel.innerHTML =
      '<div class="ftdn-heading">DAY / NIGHT <span class="ftdn-version">v0.6</span></div>' +
      '<div class="ftdn-clockrow"><span class="ftdn-time" data-ftdn-time>08:00</span>' +
      '<span class="ftdn-phase" data-ftdn-phase>Daytime</span></div>' +
      '<div class="ftdn-timeline"><span data-ftdn-meter></span></div>' +
      '<div class="ftdn-labelrow"><span>00:00</span><span>06:00 sunrise</span><span>18:00 sunset</span></div>' +
      '<div class="ftdn-readout"><span>Light reaching fly</span><strong data-ftdn-light>100%</strong></div>' +
      '<div class="ftdn-readout"><span>Location</span><strong data-ftdn-grove>Open garden</strong></div>' +
      '<div class="ftdn-actions"><button type="button" data-ftdn-pause>Pause clock</button>' +
      '<button type="button" data-ftdn-skip>+6 hours</button></div>' +
      '<div class="ftdn-hint" data-ftdn-status>1 real minute = 1 Flytopia hour</div>';
    document.body.appendChild(panel);
    ui.panel = panel;
    ui.time = panel.querySelector('[data-ftdn-time]');
    ui.phase = panel.querySelector('[data-ftdn-phase]');
    ui.meter = panel.querySelector('[data-ftdn-meter]');
    ui.light = panel.querySelector('[data-ftdn-light]');
    ui.grove = panel.querySelector('[data-ftdn-grove]');
    ui.status = panel.querySelector('[data-ftdn-status]');
    ui.pause = panel.querySelector('[data-ftdn-pause]');
    ui.skip = panel.querySelector('[data-ftdn-skip]');
    ui.pause.addEventListener('click', function () { paused = !paused; syncControls(); renderHud(); });
    ui.skip.addEventListener('click', function () {
      hour = (hour + 6) % 24;
      lastFrame = null;
      // Apply immediately on next draw frame; this is a world-clock control,
      // never a command to the fly's behavioral state machine.
      renderHud();
    });
    // Manual Light control overrides automatic daylight deliberately.
    light.addEventListener('click', function () {
      if (enabled) startOrStop(false);
      // FlyBrain's original click handler then cycles its manual light mode.
    }, true);
    document.addEventListener('visibilitychange', function () { lastFrame = null; });
    syncControls();
    renderHud();
  }

  window.FlytopiaDayNight = {
    update: update,
    drawGrove: drawGrove,
    drawAtmosphere: drawAtmosphere,
    ambientForHour: ambientForHour,
    getState: function () {
      return {hour: hour, enabled: enabled, paused: paused, ambient: currentAmbient,
              lightAtFly: currentSensor, inGrove: inGrove};
    }
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildUI);
  } else {
    buildUI();
  }
})();
