"""Show the game's name in English on the home screen (optional).

Usage: rename_title.py <app.db | param.sfo> [--restore]

Real Vita: the home screen and LiveArea take the name from the system's app database, ur0:shell/db/app.db,
which is filled in when the game is installed (param.sfo is not read again, and rePatch does not apply to
the system software). Copy app.db to the PC, run this on it, copy it back and restart the Vita.
Changed: tbl_appinfo_icon.title (name under the icon) and the 4 tbl_appinfo rows holding the title /
short title (+ their _00 versions for a Japanese system), only for PCSG00278 and only where they still hold
the Japanese name. Nothing else in the database is touched.

Vita3K: it reads sce_sys/param.sfo of the installed game, so run this on
<Vita3K data>/ux0/app/PCSG00278/sce_sys/param.sfo (and ux0/patch/PCSG00278/sce_sys/param.sfo if the 1.02
update is installed there).

A copy of the original is kept next to the file (<name>.orig) on the first run; --restore puts it back.
"""
import argparse, shutil, sqlite3, sys
from pathlib import Path

TITLE_ID = 'PCSG00278'
JA = '真・ガンダム無双'
EN = 'Shin Gundam Musou'


def rename_db(path, new, old):
    db = sqlite3.connect(path)
    try:
        with db:
            n_info = db.execute('UPDATE tbl_appinfo SET val=? WHERE titleId=? AND val=?', (new, TITLE_ID, old)).rowcount
            n_icon = db.execute('UPDATE tbl_appinfo_icon SET title=? WHERE titleId=? AND title=?',
                                (new, TITLE_ID, old)).rowcount
        ok = db.execute('pragma integrity_check').fetchone()[0]
    finally:
        db.close()
    assert ok == 'ok', f'database check failed: {ok}'
    return n_info + n_icon


def rename_sfo(path, new):
    sys.path.insert(0, str(Path(__file__).parent))
    from build_sfo import set_strings, KEYS
    p = Path(path)
    old = p.read_bytes()
    out = set_strings(old, {k: new for k in KEYS})
    p.write_bytes(out)
    return int(out != old)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('file', help='app.db (real Vita) or param.sfo (Vita3K)')
    ap.add_argument('--restore', action='store_true', help='put back the original file saved on the first run')
    a = ap.parse_args()
    p = Path(a.file)
    orig = p.with_name(p.name + '.orig')
    if a.restore:
        if not orig.exists():
            sys.exit(f'no {orig.name} next to {p.name}: nothing to restore')
        shutil.copyfile(orig, p)
        print(f'restored {p} from {orig.name}')
        return
    is_db = p.read_bytes()[:16] == b'SQLite format 3\0'
    if not is_db and p.read_bytes()[:4] != b'\0PSF':
        sys.exit(f'{p.name} is neither app.db nor param.sfo')
    if not orig.exists():
        shutil.copyfile(p, orig)
        print(f'saved the original as {orig.name}')
    n = rename_db(p, EN, JA) if is_db else rename_sfo(p, EN)
    if n:
        print(f'{p.name}: game name set to "{EN}" ({n} {"entries" if is_db else "file"} changed)')
    else:
        print(f'{p.name}: nothing to change (already English, or {TITLE_ID} is not in this file)')


if __name__ == '__main__':
    main()
