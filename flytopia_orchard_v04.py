#!/usr/bin/env python3
"""Flytopia v0.4: make the three garden fruit patches use native FlyBrain food.

Place this script beside index.html and run `python3 flytopia_orchard_v04.py`.
Restore v0.3 using `python3 flytopia_orchard_v04.py --rollback`.
"""
from pathlib import Path
import shutil
import sys

FILES = ('index.html', 'js/main.js', 'js/flytopia-garden.js')
BACKUP = Path('.flytopia-backups/v04-before-orchard')
FOOD_HOOK = '''\t// Flytopia v0.4: add edible orchard fruit using FlyBrain's native food array.\n\tif (window.FlytopiaGarden && typeof window.FlytopiaGarden.updateFood === 'function') {\n\t\twindow.FlytopiaGarden.updateFood(food);\n\t}\n\n\t// Food proximity'''
BASE_ANCHOR = '\t// Food proximity'

ADDON = r'''

/* Flytopia v0.4 - Native food bridge. Decorative fruit patches now correspond
   to ordinary FlyBrain food objects. No network, motor, or neuron code changed.
   Note: the original model uses hard-coded behavioral biases alongside neural
   activity; its food sensor is a threshold, not a physically modeled odor plume. */
(function () {
  "use strict";
  const garden = window.FlytopiaGarden;
  if (!garden) return;
  const patches = [
    {name: "Banana", x: 0.18, y: 0.50, item: null, emptyAt: 0},
    {name: "Apple", x: 0.63, y: 0.22, item: null, emptyAt: 0},
    {name: "Berry", x: 0.61, y: 0.68, item: null, emptyAt: 0}
  ];
  let enabled = true;
  const regrowDelayMs = 30000;
  function foodPosition(p) {
    // Keep the native pellet close to the artwork on the same world canvas.
    // Its small offset makes it visible instead of hiding under the fruit icon.
    return {x: innerWidth * p.x + 44, y: innerHeight * p.y + 17};
  }
  garden.updateFood = function (items) {
    if (!Array.isArray(items)) return;
    const now = Date.now();
    for (const p of patches) {
      if (!enabled) {
        if (p.item) {
          const at = items.indexOf(p.item);
          if (at >= 0) items.splice(at, 1);
        }
        p.item = null;
        p.emptyAt = 0;
        continue;
      }
      if (p.item && !items.includes(p.item)) {
        // Native feeding has consumed the pellet, or Clear removed it.
        p.item = null;
        p.emptyAt = now;
      }
      if (!p.item && (p.emptyAt === 0 || now - p.emptyAt >= regrowDelayMs)) {
        const pos = foodPosition(p);
        p.item = {x: pos.x, y: pos.y, radius: 10, feedStart: 0,
                  feedDuration: 0, eaten: 0, flytopiaOrchard: p.name};
        items.push(p.item);
        p.emptyAt = 0;
      }
      if (p.item) {
        // Preserve amount eaten, but move with the artwork after resizing.
        const pos = foodPosition(p);
        p.item.x = pos.x;
        p.item.y = pos.y;
      }
    }
  };
  function setupOrchardControls() {
    const toolbar = document.querySelector('#toolbar .toolbar-left');
    if (!toolbar || document.getElementById('flytopia-orchard-toggle')) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.id = 'flytopia-orchard-toggle';
    button.className = 'tool-btn';
    button.textContent = 'Orchard Food: On';
    button.title = 'Places 3 native FlyBrain food objects. Food regrows after 30 seconds when eaten.';
    button.setAttribute('aria-pressed', 'true');
    const gardenToggle = document.getElementById('flytopia-garden-toggle');
    if (gardenToggle) gardenToggle.insertAdjacentElement('afterend', button);
    else toolbar.appendChild(button);
    button.addEventListener('click', () => {
      enabled = !enabled;
      button.textContent = enabled ? 'Orchard Food: On' : 'Orchard Food: Off';
      button.setAttribute('aria-pressed', String(enabled));
      const caption = document.getElementById('flytopia-garden-caption');
      if (caption) caption.textContent = enabled
        ? 'SANCTUARY GROVE / 3 EDIBLE FRUIT PATCHES / NATIVE FOOD SENSORS'
        : 'SANCTUARY GROVE / ORCHARD FOOD DISABLED / FEED STILL WORKS';
    });
    const caption = document.getElementById('flytopia-garden-caption');
    if (caption) caption.textContent = 'SANCTUARY GROVE / 3 EDIBLE FRUIT PATCHES / NATIVE FOOD SENSORS';
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupOrchardControls, {once: true});
  } else setupOrchardControls();
})();
'''


def abort(message):
    raise SystemExit('ERROR: ' + message)


def rollback(root):
    if not all((root / BACKUP / rel).is_file() for rel in FILES):
        abort('No complete v0.4 backup found. Nothing changed.')
    for rel in FILES:
        target = root / rel
        shutil.copy2(root / BACKUP / rel, target)
    print('RESTORED v0.3 files. Hard-refresh your browser.')


def main():
    root = Path.cwd()
    if sys.argv[1:] == ['--rollback']:
        rollback(root)
        return
    if sys.argv[1:]:
        abort('Usage: python3 flytopia_orchard_v04.py [--rollback]')
    if not all((root / rel).is_file() for rel in FILES):
        abort('Run in your Flytopia repository folder alongside index.html, after v0.3.')
    index = (root / FILES[0]).read_text(encoding='utf-8')
    main_js = (root / FILES[1]).read_text(encoding='utf-8')
    garden_js = (root / FILES[2]).read_text(encoding='utf-8')
    if FOOD_HOOK in main_js and 'Orchard Food: On' in garden_js and '?v=4' in index:
        print('Already installed; no changes necessary.')
        return
    if 'Flytopia v0.3: draw garden beneath native food and fly rendering' not in main_js:
        abort('Could not identify the v0.3 canvas hook in js/main.js. No changes made.')
    if main_js.count(BASE_ANCHOR) != 1 or 'Flytopia v0.4: add edible orchard fruit' in main_js:
        abort('Native food proximity hook is different than expected. No changes made.')
    if 'Flytopia v0.3 - draw orchard scenery' not in garden_js or 'Flytopia v0.4 - Native food bridge' in garden_js:
        abort('Expected unmodified v0.3 js/flytopia-garden.js. No changes made.')
    old_link = './js/flytopia-garden.js?v=3'
    if index.count(old_link) != 1:
        abort('Expected the v0.3 garden script link in index.html. No changes made.')
    # Make the berry meadow and pond accessible above the bottom neuron panel.
    # Coordinates are shared by drawn scenery and native food instances.
    new_garden = garden_js.replace('patch(c, w*.61, h*.83,', 'patch(c, w*.61, h*.68,')
    new_garden = new_garden.replace('c.translate(w*.81, h*.78)', 'c.translate(w*.81, h*.64)')
    new_garden = new_garden.replace('w*.81, h*.78+48*k', 'w*.81, h*.64+48*k')
    if new_garden == garden_js or 'patch(c, w*.61, h*.68,' not in new_garden:
        abort('Garden coordinates do not match the v0.3 scenery. No changes made.')
    new_garden += ADDON
    new_main = main_js.replace(BASE_ANCHOR, FOOD_HOOK, 1)
    new_index = index.replace(old_link, './js/flytopia-garden.js?v=4')
    if (root / BACKUP).exists():
        abort('A v0.4 backup already exists, but the installed files differ. No changes made.')
    for rel in FILES:
        dest = root / BACKUP / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / rel, dest)
    (root / FILES[0]).write_text(new_index, encoding='utf-8')
    (root / FILES[1]).write_text(new_main, encoding='utf-8')
    (root / FILES[2]).write_text(new_garden, encoding='utf-8')
    print('SUCCESS: Flytopia v0.4 edible orchard installed.')
    print('Native food patches: banana, apple, berry (regrow 30 seconds after consumption).')
    print('Toggle Orchard Food On/Off independently from the decorative Garden toggle.')
    print('Unchanged: connectome, brain workers, motor logic, CSS, and Feed controls.')
    print('Backup: .flytopia-backups/v04-before-orchard')
    print('Refresh http://localhost:8000 with Cmd+Shift+R.')


if __name__ == '__main__':
    main()
