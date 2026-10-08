#!/usr/bin/env python3
"""Safe Flytopia v0.5 installer. Run beside index.html, after v0.4.

Usage:
    python3 flytopia_senses_v05.py
    python3 flytopia_senses_v05.py --rollback
"""
from pathlib import Path
import shutil
import sys

BACKUP = Path('.flytopia-backups/v05-before-senses')
MAIN = Path('js/main.js')
INDEX = Path('index.html')
SENSES = Path('js/flytopia-senses.js')
MARKER = 'Flytopia v0.5: sensory cue after native food proximity'
DRAW_ANCHOR = '\n\tdrawFood();\n\tdrawRipples();'
DRAW_PATCH = '''
	// Flytopia v0.5: sensor overlay in WORLD coordinates behind native food and fly.
	if (window.FlytopiaSenses) window.FlytopiaSenses.draw(ctx, food, fly);
	drawFood();
	drawRipples();'''
UPDATE_ANCHOR = '\n\t// Reset touch stimulus after wall-clock expiry (2 seconds)'
UPDATE_PATCH = '''
	// Flytopia v0.5: sensory cue after native food proximity (opt-in only).
	if (window.FlytopiaSenses) window.FlytopiaSenses.update(food, fly, BRAIN);

	// Reset touch stimulus after wall-clock expiry (2 seconds)'''


def error(message):
    raise SystemExit('ERROR: ' + message)


def restore(root):
    backup = root / BACKUP
    if not all((backup / p).is_file() for p in (MAIN, INDEX)):
        error('No complete v0.5 backup. Nothing changed.')
    for p in (MAIN, INDEX):
        shutil.copy2(backup / p, root / p)
    addon = root / SENSES
    expected = Path(__file__).with_name('flytopia-senses.js')
    if addon.is_file():
        if expected.exists() and addon.read_bytes() == expected.read_bytes():
            addon.unlink()
        else:
            print('NOTE: Retained modified js/flytopia-senses.js; remove manually if desired.')
    print('RESTORED Flytopia v0.4 (main.js + index.html). Hard-refresh the browser.')


def main():
    root = Path.cwd()
    if sys.argv[1:] == ['--rollback']:
        restore(root)
        return
    if sys.argv[1:]:
        error('Usage: python3 flytopia_senses_v05.py [--rollback]')
    if not all((root / p).is_file() for p in (MAIN, INDEX)):
        error('Run this script from your Flytopia project root, beside index.html.')
    addon_source = Path(__file__).with_name('flytopia-senses.js')
    if not addon_source.is_file():
        error('Keep flytopia-senses.js next to this installer (both files from the ZIP).')
    old_main = (root / MAIN).read_text(encoding='utf-8')
    old_index = (root / INDEX).read_text(encoding='utf-8')
    addon_target = root / SENSES
    if MARKER in old_main and 'flytopia-senses.js?v=5' in old_index and addon_target.is_file():
        print('Already installed; no changes made.')
        return
    if (root / BACKUP).exists():
        error('A v0.5 backup already exists but the install is incomplete; no changes made.')
    if addon_target.exists():
        error('js/flytopia-senses.js already exists; no changes made.')
    if 'Flytopia v0.4: add edible orchard fruit' not in old_main:
        error('Expected Flytopia v0.4 main.js. Nothing changed.')
    if old_main.count(DRAW_ANCHOR) != 1 or old_main.count(UPDATE_ANCHOR) != 1:
        error('main.js drawing or food-proximity hooks differ from the uploaded version.')
    if 'flytopia-garden.js?v=4' not in old_index:
        error('Expected the v0.4 garden script in index.html. Nothing changed.')
    if old_index.lower().count('</body>') != 1:
        error('Expected one closing </body> tag in index.html. Nothing changed.')
    new_main = old_main.replace(DRAW_ANCHOR, DRAW_PATCH, 1).replace(UPDATE_ANCHOR, UPDATE_PATCH, 1)
    new_index = old_index.replace('</body>', '<script src="./js/flytopia-senses.js?v=5"></script>\n</body>', 1)
    for rel in (MAIN, INDEX):
        dest = root / BACKUP / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / rel, dest)
    try:
        (root / MAIN).write_text(new_main, encoding='utf-8')
        (root / INDEX).write_text(new_index, encoding='utf-8')
        shutil.copy2(addon_source, addon_target)
    except Exception:
        for rel in (MAIN, INDEX):
            shutil.copy2(root / BACKUP / rel, root / rel)
        if addon_target.is_file(): addon_target.unlink()
        raise
    print('SUCCESS: Flytopia v0.5 installed.')
    print('Fly Senses: On = illustration and data overlay; no change in neural behavior.')
    print('Odor Cue: Off (default) = original FlyBrain behavior.')
    print('Odor Cue: On = thresholded extension of native BRAIN.stimulate.foodNearby.')
    print('Original food contact, brain neuron code, and movement logic unchanged.')
    print('Backup: ' + str(BACKUP))
    print('Hard-refresh http://localhost:8000')


if __name__ == '__main__':
    main()
