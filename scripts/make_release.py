"""Build the English patch and package it as xdelta files (no game data is distributed).

Usage (from the repo root):
    python -P scripts/make_release.py <version>          e.g.  python -P scripts/make_release.py 0.1.0

Needs xdelta3 (tools/bin/xdelta3.exe or on PATH) and these local inputs:
    decrypted/vita/LINKDATA_NGP/LINKDATA.B, LINKDATA.C    original decrypted Vita files (PCSG00278 v1.00)
    PCSG00278_100/eboot.bin.elf, self_auth.bin            FAGDec output, game version 1.00
    PCSG00278_102/eboot.bin.elf, self_auth.bin            FAGDec output, update 1.02 (tools/unfself.py makes
                                                          the .elf from FAGDec's decrypted SELF)
    decrypted/vita/param.sfo.orig, param_102.sfo.orig     original sce_sys/param.sfo of the game / of the update
    decrypted/ps3/PS3_GAME/USRDIR/LINKDATA_PS3/LINKDATA.B, LINKDATA.C   PS3 EU source of the English text/images

Output: release/shin-gundam-musou-vita-english-<version>/  (+ .zip)
"""
import hashlib, os, shutil, subprocess, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VITA = ROOT / 'decrypted/vita/LINKDATA_NGP'
PS3 = ROOT / 'decrypted/ps3/PS3_GAME/USRDIR/LINKDATA_PS3'
BUILD = ROOT / 'build/rePatch/PCSG00278'                # LINKDATA (same for every game version)
# game versions: (FAGDec dir, eboot build dir, original param.sfo, patched param.sfo, where it goes)
GAME = {
    '1.00': (ROOT / 'PCSG00278_100', ROOT / 'build/v100', ROOT / 'decrypted/vita/param.sfo.orig',
             ROOT / 'build/sce_sys/param.sfo', 'ux0:app/PCSG00278/sce_sys/param.sfo'),
    '1.02': (ROOT / 'PCSG00278_102', ROOT / 'build/v102', ROOT / 'decrypted/vita/param_102.sfo.orig',
             ROOT / 'build/sce_sys_102/param.sfo', 'ux0:patch/PCSG00278/sce_sys/param.sfo'),
}


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


def install_text(version):
    """INSTALL.md for the zip: the README's installation section (between the install markers)."""
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    start = readme.index('<!-- install:start')
    body = readme[readme.index('-->', start) + 3:readme.index('<!-- install:end -->')].strip()
    return (f'# Shin Gundam Musou (PS Vita) – English Patch v{version}\n\n'
            'English translation of Shin Gundam Musou (PCSG00278), using the official English script and graphics '
            'from Dynasty Warriors: Gundam Reborn (PS3, Europe).\n'
            'Project page: https://github.com/irxd/shin-musou-gundam-vita-english\n\n'
            + body + '\n')


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    version = sys.argv[1]
    xdelta = find_xdelta()

    # 1. build everything from the pristine inputs
    for v, (fag, out_v, sfo, sfo_out, _) in GAME.items():   # eboot per version (+ font atlas, same for all)
        py('build_font.py', VITA / 'LINKDATA.C', fag / 'eboot.bin.elf', fag / 'self_auth.bin', out_v)
    BUILD.joinpath('LINKDATA_NGP').mkdir(parents=True, exist_ok=True)
    shutil.copy(GAME['1.00'][1] / 'LINKDATA_NGP/LINKDATA.C', BUILD / 'LINKDATA_NGP/LINKDATA.C')
    for v, (_, out_v, *_r) in GAME.items():
        shutil.copy(out_v / 'eboot.bin', BUILD.parent / f'eboot_v{v}.bin')
    py('build_images.py', PS3 / 'LINKDATA.C', BUILD / 'LINKDATA_NGP/LINKDATA.C')
    py('build_text.py', VITA / 'LINKDATA.B', PS3 / 'LINKDATA.B', BUILD / 'LINKDATA_NGP/LINKDATA.B')

    # 2. xdelta: original -> patched
    out = ROOT / 'release' / f'shin-gundam-musou-vita-english-{version}'
    if out.exists():
        shutil.rmtree(out)
    (out / 'patches').mkdir(parents=True)
    pairs = [  # (source the player has, our output, patch name, where it goes)
        (VITA / 'LINKDATA.B', BUILD / 'LINKDATA_NGP/LINKDATA.B', 'LINKDATA.B.xdelta',
         'ux0:rePatch/PCSG00278/LINKDATA_NGP/LINKDATA.B'),
        (VITA / 'LINKDATA.C', BUILD / 'LINKDATA_NGP/LINKDATA.C', 'LINKDATA.C.xdelta',
         'ux0:rePatch/PCSG00278/LINKDATA_NGP/LINKDATA.C'),
    ]
    for v, (fag, out_v, sfo, sfo_out, sfo_dest) in GAME.items():
        pairs += [(fag / 'eboot.bin.elf', out_v / 'eboot.bin', f'eboot_v{v}.xdelta', 'ux0:rePatch/PCSG00278/eboot.bin')]
        # (param.sfo / home-screen name: tools/build_sfo.py works, but the LiveArea didn't pick it up on
        #  hardware, so it is not shipped yet)
    lines = []
    for src, dst, name, dest in pairs:
        run(xdelta, '-e', '-9', '-f', '-s', src, dst, out / 'patches' / name)
        check = out / 'verify.tmp'      # round trip: the patch must recreate our file exactly
        run(xdelta, '-d', '-f', '-s', src, out / 'patches' / name, check)
        ok = sha1(check) == sha1(dst)
        check.unlink()
        assert ok, f'{name}: applying the patch does not reproduce {dst}'
        lines.append(f'{name:24} source sha1 {sha1(src)}  ->  {dest}  sha1 {sha1(dst)}')
    (out / 'checksums.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (out / 'INSTALL.md').write_text(install_text(version), encoding='utf-8')

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
