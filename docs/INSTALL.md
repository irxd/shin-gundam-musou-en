# Shin Gundam Musou (PS Vita) – English Patch: Installation

This patch translates the Japanese PS Vita release of **Shin Gundam Musou** (PCSG00278) into English, using
the official English script and graphics from *Dynasty Warriors: Gundam Reborn* (PS3, Europe).

The patch contains **no game data**. It is a set of xdelta files that you apply to files from your own copy
of the game.

## What you need

- **The game:** Shin Gundam Musou, Japanese release **PCSG00278, version 1.00**.
- **For a real Vita:**
  - A PS Vita on HENkaku/Ensō.
  - The **rePatch** plugin, installed under `*KERNEL` in `ux0:tai/config.txt` (or `ur0:tai/config.txt`).
  - **FAGDec**, to decrypt the game's `eboot.bin`.
  - **VitaShell**, to copy files between the Vita and your PC.
- **For Vita3K:** the game installed in Vita3K. Its files are already decrypted.
- **xdelta**, to apply the patches on your PC. Any xdelta3 tool works, such as *xdelta UI* or *Delta Patcher*.

## The patch files

| Patch | Apply it to | Result goes to |
|---|---|---|
| `patches/eboot.bin.xdelta` | `eboot.bin.elf` (decrypted with FAGDec) | `ux0:rePatch/PCSG00278/eboot.bin` |
| `patches/LINKDATA.B.xdelta` | `LINKDATA_NGP/LINKDATA.B` (decrypted) | `ux0:rePatch/PCSG00278/LINKDATA_NGP/LINKDATA.B` |
| `patches/LINKDATA.C.xdelta` | `LINKDATA_NGP/LINKDATA.C` (decrypted) | `ux0:rePatch/PCSG00278/LINKDATA_NGP/LINKDATA.C` |
| `patches/param.sfo.xdelta` (optional) | `sce_sys/param.sfo` | `ux0:app/PCSG00278/sce_sys/param.sfo` |

The optional `param.sfo` patch changes the game's name in the home screen from 真・ガンダム無双 to
*Shin Gundam Musou*. It is the only file that goes into `ux0:app` rather than `ux0:rePatch`.

`checksums.txt` lists the SHA-1 of each expected source file and of each patched result. If a source file
doesn't match, the patch will fail: check that you have version 1.00 and that the file is decrypted.

## Real PS Vita (rePatch)

1. **Decrypt the eboot.** In FAGDec, select Shin Gundam Musou (PCSG00278), choose `eboot.bin` and decrypt it
   to ELF. Copy the resulting `eboot.bin.elf` to your PC.
2. **Copy the decrypted data files.** In VitaShell, go to `ux0:app/PCSG00278/`, open the folder with
   *Open decrypted* (triangle menu), and copy `LINKDATA_NGP/LINKDATA.B` and `LINKDATA_NGP/LINKDATA.C` to your
   PC. `LINKDATA.C` is about 1 GB.
3. **Apply the patches** on your PC: each `.xdelta` file plus its source file gives a patched file (see the
   table above). Name the patched eboot `eboot.bin`.
4. **Copy the patched files** to the Vita:
   ```
   ux0:rePatch/PCSG00278/eboot.bin
   ux0:rePatch/PCSG00278/LINKDATA_NGP/LINKDATA.B
   ux0:rePatch/PCSG00278/LINKDATA_NGP/LINKDATA.C
   ```
5. Reboot the Vita and start the game.
6. *Optional: English name on the home screen.* Copy `ux0:app/PCSG00278/sce_sys/param.sfo` to your PC, keep a
   backup, and apply `param.sfo.xdelta`. Copy the result back over the original. Then, in VitaShell, press
   △ and choose *Refresh LiveArea*.

Without step 6, nothing in `ux0:app` is changed. To uninstall, delete `ux0:rePatch/PCSG00278/`. If you did
step 6, also put your backup `param.sfo` back and refresh the LiveArea again.

## Vita3K

1. Find the installed game at `<Vita3K data>/ux0/app/PCSG00278/`. Back up `eboot.bin` and
   `LINKDATA_NGP/LINKDATA.B` and `LINKDATA.C`.
2. Apply the LINKDATA patches to the files from that folder.
3. Apply the eboot patch to a decrypted `eboot.bin.elf`. You can get one from FAGDec on a Vita, or from
   Vita3K's *ELF dumping* option (Settings → Debug), which writes
   `elfdumps/PCSG00278/0x81000000-0x8137BCCC_app0.elf`. Rename it to `eboot.bin.elf` and check its SHA-1
   against `checksums.txt`.
4. Put the three patched files into `ux0/app/PCSG00278/`, replacing the originals.
5. *Optional:* apply `param.sfo.xdelta` to `ux0/app/PCSG00278/sce_sys/param.sfo` for the English name in the
   game list. You may need to restart Vita3K or refresh the game list.

## Known issues

- Some menu and table lines are still in Japanese, because the PS3 release left them blank or arranged them
  differently.
- Some images with Japanese text remain, such as tutorial pictures.
- Long lines in story and battle text boxes are drawn in a smaller font so that they fit.
- Real-hardware testing is still in progress. Vita3K has been tested.

## Credits

- English script and graphics: the official *Dynasty Warriors: Gundam Reborn* EU release (Koei Tecmo).
- Patch, tools and reverse engineering: see the project repository.
