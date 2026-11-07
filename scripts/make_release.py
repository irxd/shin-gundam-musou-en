"""Build the English patch and package it as xdelta files (no game data is distributed).

Usage (from the repo root):
    python -P scripts/make_release.py <version>          e.g.  python -P scripts/make_release.py 0.1.0

Needs xdelta3 (tools/bin/xdelta3.exe or on PATH) and these local inputs:
    decrypted/vita/LINKDATA_NGP/LINKDATA.B, LINKDATA.C    original decrypted Vita files (PCSG00278 v1.00)
    PCSG00278/eboot.bin.elf, self_auth.bin                FAGDec output for the same game
    decrypted/vita/param.sfo.orig                         original sce_sys/param.sfo
    decrypted/ps3/PS3_GAME/USRDIR/LINKDATA_PS3/LINKDATA.B, LINKDATA.C   PS3 EU source of the English text/images

Output: release/shin-gundam-musou-vita-english-<version>/  (+ .zip)
"""
import hashlib, os, shutil, subprocess, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VITA = ROOT / 'decrypted/vita/LINKDATA_NGP'
PS3 = ROOT / 'decrypted/ps3/PS3_GAME/USRDIR/LINKDATA_PS3'
FAGDEC = ROOT / 'PCSG00278'
BUILD = ROOT / 'build/rePatch/PCSG00278'
SFO = ROOT / 'decrypted/vita/param.sfo.orig'          # original sce_sys/param.sfo
SFO_OUT = ROOT / 'build/sce_sys/param.sfo'             # not a rePatch file: goes to ux0:app/.../sce_sys


def run(*args):
    print('>', ' '.join(str(a) for a in args))
    subprocess.run([str(a) for a in args], check=True)


def py(script, *args):
    run(sys.executable, '-P', ROOT / 'tools' / script, *args)


def sha1(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def find_xdelta():
    local = ROOT / 'tools/bin/xdelta3.exe'
    if local.exists():
        return local
    for name in ('xdelta3', 'xdelta'):
        p = shutil.which(name)
        if p:
            return Path(p)
    sys.exit('xdelta3 not found: put xdelta3.exe in tools/bin/ or on PATH')


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    version = sys.argv[1]
    xdelta = find_xdelta()

    # 1. build everything from the pristine inputs
    py('build_font.py', VITA / 'LINKDATA.C', FAGDEC / 'eboot.bin.elf', FAGDEC / 'self_auth.bin', BUILD)
    py('build_images.py', PS3 / 'LINKDATA.C', BUILD / 'LINKDATA_NGP/LINKDATA.C')
    py('build_text.py', VITA / 'LINKDATA.B', PS3 / 'LINKDATA.B', BUILD / 'LINKDATA_NGP/LINKDATA.B')
    py('build_sfo.py', SFO, SFO_OUT)

    # 2. xdelta: original -> patched
    out = ROOT / 'release' / f'shin-gundam-musou-vita-english-{version}'
    if out.exists():
        shutil.rmtree(out)
    (out / 'patches').mkdir(parents=True)
    pairs = [  # (source the player has, our output, patch name, where it goes)
        (FAGDEC / 'eboot.bin.elf', BUILD / 'eboot.bin', 'eboot.bin.xdelta', 'eboot.bin'),
        (VITA / 'LINKDATA.B', BUILD / 'LINKDATA_NGP/LINKDATA.B', 'LINKDATA.B.xdelta', 'LINKDATA_NGP/LINKDATA.B'),
        (VITA / 'LINKDATA.C', BUILD / 'LINKDATA_NGP/LINKDATA.C', 'LINKDATA.C.xdelta', 'LINKDATA_NGP/LINKDATA.C'),
        (SFO, SFO_OUT, 'param.sfo.xdelta', 'sce_sys/param.sfo (optional, see INSTALL.md)'),
    ]
    lines = []
    for src, dst, name, dest in pairs:
        run(xdelta, '-e', '-9', '-f', '-s', src, dst, out / 'patches' / name)
        check = out / 'verify.tmp'      # round trip: the patch must recreate our file exactly
        run(xdelta, '-d', '-f', '-s', src, out / 'patches' / name, check)
        ok = sha1(check) == sha1(dst)
        check.unlink()
        assert ok, f'{name}: applying the patch does not reproduce {dst}'
        target = dest if dest.startswith('sce_sys') else f'rePatch/PCSG00278/{dest}'
        lines.append(f'{name:20} {src.name:14} sha1 {sha1(src)}  ->  {target}  sha1 {sha1(dst)}')
    (out / 'checksums.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    shutil.copy(ROOT / 'docs/INSTALL.md', out / 'INSTALL.md')

    zpath = out.parent / (out.name + '.zip')
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file():
                z.write(p, p.relative_to(out.parent))
    print('\n'.join(lines))
    for p in sorted((out / 'patches').iterdir()):
        print(f'{p.name:20} {p.stat().st_size:>12,} bytes')
    print('wrote', zpath)


if __name__ == '__main__':
    main()
