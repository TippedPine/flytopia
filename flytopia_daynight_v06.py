#!/usr/bin/env python3
"""Install or roll back Flytopia v0.6 in an existing v0.5 repository."""
from pathlib import Path
import sys, hashlib, json, shutil

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / 'js' / 'main.js'
INDEX = ROOT / 'index.html'
ASSET_FILES = {
    'js/flytopia-daynight.js': ROOT / 'flytopia-daynight.js',
    'css/flytopia-daynight.css': ROOT / 'flytopia-daynight.css',
}
BACKUP = ROOT / '.flytopia-backup-v06'
MARK = '// Flytopia v0.6: automated ambient light and local grove shade.'


def hash_file(f):
    return hashlib.sha256(f.read_bytes()).hexdigest()


def rollback():
    meta_path = BACKUP / 'manifest.json'
    if not meta_path.exists():
        print('No v0.6 backup found; no changes made.')
        return 1
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    for file in [MAIN, INDEX]:
        rel = str(file.relative_to(ROOT))
        if not file.exists() or hash_file(file) != meta['installed_hashes'][rel]:
            print('STOP: ' + rel + ' was edited since v0.6 installation. Rollback would overwrite those edits.')
            print('Please back up the changes, then restore manually from ' + str(BACKUP))
            return 1
    for rel, obj in meta['new_files'].items():
        path = ROOT / rel
        if path.exists() and hash_file(path) != obj['hash']:
            print('STOP: ' + rel + ' was edited since installation. Back it up before rolling back.')
            return 1
    for rel in ['js/main.js', 'index.html']:
        shutil.copy2(BACKUP / rel, ROOT / rel)
    for rel, obj in meta['new_files'].items():
        p = ROOT / rel
        if obj['existed']:
            shutil.copy2(BACKUP / rel, p)
        elif p.exists():
            p.unlink()
    print('Rolled back Flytopia v0.6. v0.5 code has been restored.')
    return 0


def main():
    if '--rollback' in sys.argv:
        return rollback()
    if not MAIN.is_file() or not INDEX.is_file():
        print('ERROR: Put this installer in the Flytopia project root, alongside index.html.')
        return 1
    if not all(path.is_file() for path in ASSET_FILES.values()):
        print('ERROR: Keep the JS and CSS files from the ZIP alongside the Python installer.')
        return 1
    if BACKUP.exists():
        print('v0.6 backup already exists. To avoid overwriting it, installation stopped.')
        print('If you already installed v0.6, no further action is needed.')
        return 1
    main_text = MAIN.read_text(encoding='utf-8')
    index_text = INDEX.read_text(encoding='utf-8')
    if MARK in main_text or 'flytopia-daynight.js' in index_text:
        print('v0.6 is already installed (or partially installed). Nothing modified.')
        return 1
    if 'window.FlytopiaSenses.update(food, fly, BRAIN)' not in main_text or 'flytopia-senses.js' not in index_text:
        print('ERROR: v0.5 sensory hooks are missing. Install and test v0.5 first.')
        return 1
    updates = [
        ('// --- Draw ---\nfunction draw() {',
         '// --- Draw ---\nfunction draw() {\n'
         '\t' + MARK + '\n'
         '\tif (window.FlytopiaDayNight) {\n'
         '\t\twindow.FlytopiaDayNight.update(BRAIN, fly, window.innerWidth, window.innerHeight, performance.now());\n'
         '\t}\n'),
        ('\t// Flytopia v0.5: sensor overlay in WORLD coordinates behind native food and fly.',
         '\t// Flytopia v0.6: canopy drawn below all original simulation objects.\n'
         '\tif (window.FlytopiaDayNight) {\n'
         '\t\twindow.FlytopiaDayNight.drawGrove(ctx, window.innerWidth, window.innerHeight);\n'
         '\t}\n\n'
         '\t// Flytopia v0.5: sensor overlay in WORLD coordinates behind native food and fly.'),
        ('\tctx.restore(); // end zoom/pan transform',
         '\tctx.restore(); // end zoom/pan transform\n'
         '\t// v0.6: screen-space light tint after the fly, before browser UI layers.\n'
         '\tif (window.FlytopiaDayNight) {\n'
         '\t\twindow.FlytopiaDayNight.drawAtmosphere(ctx, window.innerWidth, window.innerHeight);\n'
         '\t}'),
    ]
    for a, b in updates:
        if main_text.count(a) != 1:
            print('ERROR: Expected integration point missing or ambiguous in js/main.js:', repr(a[:95]))
            print('No files were changed. Please upload the latest main.js if this happens.')
            return 1
        main_text = main_text.replace(a, b, 1)
    if index_text.count('</head>') != 1 or index_text.count('</body>') != 1:
        print('ERROR: Unexpected HTML structure; no files changed.')
        return 1
    index_text = index_text.replace('</head>',
        '  <!-- Flytopia v0.6: day/night clock -->\n'
        '  <link rel="stylesheet" href="./css/flytopia-daynight.css?v=6">\n'
        '</head>', 1)
    index_text = index_text.replace('</body>',
        '  <script src="./js/flytopia-daynight.js?v=6"></script>\n'
        '</body>', 1)
    BACKUP.mkdir(parents=True)
    original_files = ['js/main.js', 'index.html']
    new_files = {}
    for rel, source in ASSET_FILES.items():
        target = ROOT / rel
        existed = target.exists()
        if existed:
            backup_target = BACKUP / rel
            backup_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup_target)
        new_files[rel] = {'existed': existed, 'hash': hash_file(source)}
    for rel in original_files:
        destination = BACKUP / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, destination)
    try:
        MAIN.write_text(main_text, encoding='utf-8')
        INDEX.write_text(index_text, encoding='utf-8')
        for rel, src in ASSET_FILES.items():
            dest = ROOT / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        metadata = {
            'installed_hashes': {rel: hash_file(ROOT / rel) for rel in original_files},
            'new_files': new_files,
        }
        (BACKUP / 'manifest.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        # Keep the local backup out of git without modifying tracked .gitignore.
        exclude = ROOT / '.git' / 'info' / 'exclude'
        if exclude.exists():
            old = exclude.read_text(encoding='utf-8')
            if '.flytopia-backup-v06/' not in old:
                with exclude.open('a', encoding='utf-8') as f:
                    f.write('\n.flytopia-backup-v06/\n')
    except Exception:
        for rel in original_files:
            shutil.copy2(BACKUP / rel, ROOT / rel)
        for rel, info in new_files.items():
            target = ROOT / rel
            if info['existed']:
                shutil.copy2(BACKUP / rel, target)
            elif target.exists():
                target.unlink()
        raise
    print('SUCCESS: Flytopia v0.6 installed.')
    print('- Added a 24-minute day, real lightLevel input, and local grove shade.')
    print('- Added Day/Night, Pause, and +6 hours controls.')
    print('- Preserved original food, connectome, behavior, and movement systems.')
    print('Hard-refresh http://localhost:8000 in your browser.')
    print('To undo: python3 flytopia_daynight_v06.py --rollback')
    return 0


if __name__ == '__main__':
    sys.exit(main())
