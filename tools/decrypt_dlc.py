"""Decrypt the Shin Gundam Musou DLC with psvpfsparser, so the web patcher can translate it.

Usage:
    python tools/decrypt_dlc.py <addcont folder> [<license folder>] [-o <output folder>] [--psvpfsparser <exe>]

  <addcont folder>   the DLC as copied from the Vita: ux0:addcont/PCSG00278 (one subfolder per DLC),
                     or the addcont/PCSG00278 folder of a PKG dump (NoPayStation / pkg2zip)
  <license folder>   ux0:license/addcont/PCSG00278 (NoNpDrm licenses). Not needed when every DLC folder
                     already has its license inside (a .rif file or sce_sys/package/work.bin, as in PKG dumps)
  -o                 where the decrypted files go (default: PCSG00278_decrypted next to the addcont folder)
  --psvpfsparser     path to psvpfsparser(.exe) (default: found in the release folder, its tools folder, a
                     folder inside either, or on PATH)

psvpfsparser (https://github.com/motoharu-gosuto/psvpfstools/releases) asks the public F00D service
cma.henkaku.xyz once per DLC, so an internet connection is needed. This script only finds each DLC's
key in its license and runs psvpfsparser for every DLC folder.
"""
import argparse, os, shutil, subprocess, sys
from pathlib import Path

RIF_MAGIC = bytes.fromhex('efcdab8967452301')   # NoNpDrm fake license; klicensee at 0x50..0x5f


def klicensee(rif):
    data = rif.read_bytes()
    if len(data) < 0x60:
        return None
    return data[0x50:0x60].hex()


def find_license(dlc, licenses):
    """The license of one DLC folder: inside it (PKG dump) or in the license folder (from the Vita)."""
    cands = [dlc / 'sce_sys/package/work.bin', *sorted(dlc.glob('*.rif'))]
    if licenses:
        cands += sorted((licenses / dlc.name).glob('*.rif'))
    for c in cands:
        if c.is_file() and (k := klicensee(c)):
            return c, k
    return None, None


def find_parser(arg):
    if arg:
        return arg
    here = Path(__file__).resolve().parent
    for name in ('psvpfsparser.exe', 'psvpfsparser'):
        # next to this script, in the release folder above it, or in an unzipped folder in either
        for d in (here, here.parent):
            if (d / name).is_file():
                return str(d / name)
            if found := sorted(d.glob(f'*/{name}')):
                return str(found[0])
        if p := shutil.which(name):
            return p
    sys.exit('psvpfsparser not found. Download it from https://github.com/motoharu-gosuto/psvpfstools/releases '
             'and put it next to this script (or pass --psvpfsparser <path>).')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('addcont', type=Path)
    ap.add_argument('licenses', type=Path, nargs='?')
    ap.add_argument('-o', '--out', type=Path)
    ap.add_argument('--psvpfsparser')
    a = ap.parse_args()

    parser = find_parser(a.psvpfsparser)
    src = a.addcont.resolve()
    dlcs = sorted(d for d in src.iterdir() if d.is_dir() and (d / 'sce_pfs').is_dir() and any(d.glob('*.BIN')))
    if not dlcs:
        sys.exit(f'No DLC folders (DMS... / DSC... with a .BIN file) found in {src}')
    out = (a.out or src.parent / 'PCSG00278_decrypted').resolve()
    out.mkdir(parents=True, exist_ok=True)

    failed = []
    for i, dlc in enumerate(dlcs, 1):
        lic, key = find_license(dlc, a.licenses and a.licenses.resolve())
        print(f'[{i}/{len(dlcs)}] {dlc.name}', end=' ', flush=True)
        if not key:
            print('- no license found, skipped')
            failed.append(dlc.name)
            continue
        dst = out / dlc.name
        if dst.exists():
            shutil.rmtree(dst)
        r = subprocess.run([parser, '-i', str(dlc), '-o', str(dst), '-k', key, '-f', 'cma.henkaku.xyz'],
                           capture_output=True, text=True, errors='replace')
        bins = list(dst.glob('*.BIN')) if dst.exists() else []
        if r.returncode == 0 and bins:
            print('- ok')
        else:
            print('- FAILED')
            print('    ' + '\n    '.join((r.stdout + r.stderr).strip().splitlines()[-6:]))
            failed.append(dlc.name)

    print()
    if failed:
        print(f'{len(failed)} DLC could not be decrypted: {", ".join(failed)}')
        print('Check the internet connection (psvpfsparser needs cma.henkaku.xyz) and that each DLC has its license.')
    print(f'Decrypted DLC: {out}')
    print('Choose this folder in the web patcher\'s "DLC folder" row.')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
