# Shin Gundam Musou (PS Vita) — English Patch

An English translation patch for **Shin Gundam Musou** (真・ガンダム無双, PS Vita, Japan only, `PCSG00278`).

The game was released in the West only on PS3, as *Dynasty Warriors: Gundam Reborn*. This project ports that
**official English localization** from the PS3 release onto the Japanese Vita release. Both versions run on the same
engine and use the same data layout.

> **Status: playable in English (v0.2.0, early test release; game versions 1.00 and 1.02).** Tested on a real
> PS Vita and in Vita3K. Download the patch from the [Releases](https://github.com/irxd/shin-musou-gundam-vita-english/releases) page.

<p align="center"><img src="docs/screenshots/05-story-dialogue.png" width="420" alt="Story scene with English dialogue, on a PS Vita"> <img src="docs/screenshots/08-battle-dialogue.png" width="420" alt="Battle with English dialogue and mission, on a PS Vita"></p>

More screenshots: [Screenshots](#screenshots).

## Installation

The patch is a set of small **xdelta** files that you apply to files from **your own copy** of the game. No game
data is included.

> **New: [web patcher](https://irxd.github.io/shin-musou-gundam-vita-english/) (experimental).** Instead of
> Delta Patcher, you can apply the patch in your browser: choose your decrypted `eboot.bin.elf`, `LINKDATA.B` and
> `LINKDATA.C`, and it gives you the finished `rePatch` folder. Everything runs on your computer and nothing is
> uploaded. You still need to get those three files from your Vita (steps 1 and 2 below). Desktop Chrome or Edge
> is recommended. If it doesn't work for you, use the manual steps below.

### You need

- **The game:** Shin Gundam Musou, Japanese release **PCSG00278**, version **1.00** or **1.02** (the latest
  update). Check the version in the game's LiveArea or in `sce_sys/param.sfo`.
- **For a real Vita:**
  - A PS Vita on HENkaku/Ensō.
  - The **rePatch** plugin, installed under `*KERNEL` in `ux0:tai/config.txt` (or `ur0:tai/config.txt`).
  - **FAGDec**, to decrypt the game's `eboot.bin`.
  - **VitaShell**, to copy files between the Vita and your PC.
- **For [Vita3K](https://vita3k.org/):** the game installed in Vita3K. Its files are already decrypted.
- **[Delta Patcher](https://github.com/marco-calautti/DeltaPatcher/releases)** (recommended), to apply the
  patches on your PC. It's the tool the patch was tested with; other xdelta3 tools should also work.

### The patch files

Download the latest `shin-gundam-musou-vita-english-<version>.zip` from the
[Releases](https://github.com/irxd/shin-musou-gundam-vita-english/releases) page and unzip it.

First check which version you have: **1.00** (no update) or **1.02** (the update is installed, so
`ux0:patch/PCSG00278/` exists). The version decides where the `eboot.bin` comes from and which eboot patch to
use. Everything else is the same.

`checksums.txt` in the zip lists the SHA-1 of each expected source file and of each patched result. If a source
file doesn't match, the patch will fail: check that you used the patch for your game version and that the file
is decrypted.

### Real PS Vita (rePatch)

1. **Decrypt the eboot with FAGDec:**
   1. Open FAGDec.
   2. Select the game **真・ガンダム無双** and press ✕.
   3. Select the `eboot.bin` for your version and press ✕:
      - **1.00:** `ux0:app/PCSG00278/eboot.bin`
      - **1.02:** `ux0:patch/PCSG00278/eboot.bin`

      It now appears on the right, under *Modules to be decrypted*.
   4. Press ○ to go back to the main menu.
   5. Press START and choose **START DECRYPT (ELF)**.
   6. The decrypted file is written to `ux0:FAGDec/app/PCSG00278/` (1.00) or `ux0:FAGDec/patch/PCSG00278/`
      (1.02). Copy the `eboot.bin.elf` from there to your PC.
2. **Copy the decrypted data files** (both versions): in VitaShell, go to `ux0:app/PCSG00278/`, open the
   folder with *Open decrypted* (△ menu), and copy `LINKDATA_NGP/LINKDATA.B` and `LINKDATA_NGP/LINKDATA.C` to
   your PC. `LINKDATA.C` is about 1 GB.
3. **Apply the patches** on your PC: each `.xdelta` file plus its source file gives a patched file. For the
   eboot use `eboot_v1.00.xdelta` **or** `eboot_v1.02.xdelta` to match the eboot you decrypted, and name the
   result `eboot.bin`.

   | Source file (from step 1 or 2) | Patch | Result goes to |
   |---|---|---|
   | `eboot.bin.elf`, version 1.00 | `patches/eboot_v1.00.xdelta` | `ux0:rePatch/PCSG00278/eboot.bin` |
   | `eboot.bin.elf`, version 1.02 | `patches/eboot_v1.02.xdelta` | `ux0:rePatch/PCSG00278/eboot.bin` |
   | `LINKDATA.B` | `patches/LINKDATA.B.xdelta` | `ux0:rePatch/PCSG00278/LINKDATA_NGP/LINKDATA.B` |
   | `LINKDATA.C` | `patches/LINKDATA.C.xdelta` | `ux0:rePatch/PCSG00278/LINKDATA_NGP/LINKDATA.C` |

   > **Note:** *Delta Patcher* overwrites the file you select unless *Backup original file* is ticked; *xdelta
   > UI* and the `xdelta3` command line write a new file. Keep an unpatched copy of each file (or tick the
   > backup option) in case you need it again, for example for a future patch version. You can check every
   > result against the patched SHA-1 in `checksums.txt`.
4. **Copy the patched files** to the Vita:
   ```
   ux0:rePatch/PCSG00278/eboot.bin
   ux0:rePatch/PCSG00278/LINKDATA_NGP/LINKDATA.B
   ux0:rePatch/PCSG00278/LINKDATA_NGP/LINKDATA.C
   ```

Nothing in `ux0:app` or `ux0:patch` is changed. **Uninstall:** delete `ux0:rePatch/PCSG00278/`.

### Vita3K

1. Find the installed game at `<Vita3K data>/ux0/app/PCSG00278/`. Back up `eboot.bin` and
   `LINKDATA_NGP/LINKDATA.B` and `LINKDATA.C`.
2. Apply the LINKDATA patches to the files from that folder.
3. Apply the eboot patch for your version to a decrypted `eboot.bin.elf`. You can get one from FAGDec on a
   Vita, or from Vita3K's *ELF dumping* option (Settings → Debug), which writes
   `elfdumps/PCSG00278/0x81000000-0x8137BCCC_app0.elf`. Rename it to `eboot.bin.elf` and check its SHA-1
   against `checksums.txt`.
4. Put the patched LINKDATA files into `ux0/app/PCSG00278/LINKDATA_NGP/`, replacing the originals. Put the
   patched `eboot.bin` into `ux0/app/PCSG00278/` (1.00), or into `ux0/patch/PCSG00278/` if the 1.02 update
   is installed in Vita3K.

## Known issues

- Some menu and table lines are still in Japanese: about 780 lines the PS3 release left blank, and 5 tables
  whose line counts differ between the two versions.
- Some images with Japanese text remain, such as tutorial pictures.
- DLC (the extra scenarios and mobile suits) is not translated yet and hasn't been tested with the patch.
  The patch doesn't change any DLC files; DLC scenario text will most likely show in Japanese. Planned for a
  later version.
- Long lines in story and battle text boxes are drawn in a smaller font so that they fit.
- The game's name on the home screen stays 真・ガンダム無双. Changing it via `param.sfo` did not update the
  LiveArea in testing; a fix is planned for a later version.
- Tested on a real PS Vita (1.02, via rePatch) and in Vita3K (1.00 and 1.02). Please report problems.

## What's translated

| Area | Status |
|---|---|
| Mission dialogue & messages | ✅ ~66k strings |
| Names, menus, items, tutorials, help texts | ✅ ~5k strings |
| Story scenes & narration | ✅ 5,461 lines |
| Font | ✅ Proportional English text with word wrap; long lines shrink to fit their box |
| Images: YES/NO/OK buttons, chapter title cards, boot notice & logo, title screen | ✅ |
| Game name on the home screen | ⏳ Still Japanese (planned) |
| ~780 lines the PS3 release left blank, 5 tables with different line counts | ⏳ Still Japanese |
| Other images with Japanese text (e.g. tutorial pictures) | ⏳ To do |
| DLC (16 extra scenarios, 4 extra mobile suits) | ⏳ Planned for a later version |

## Screenshots

Taken on a real PS Vita (game version 1.02).

<table>
<tr><td><img src="docs/screenshots/04-narration.png" alt="Story narration"><br><sub>Story narration</sub></td><td><img src="docs/screenshots/06-chapter-card.png" alt="Chapter title card"><br><sub>Chapter title card</sub></td><td><img src="docs/screenshots/03-title-select.png" alt="Title select menu"><br><sub>Title select menu</sub></td></tr>
<tr><td><img src="docs/screenshots/08-battle-dialogue.png" alt="Battle dialogue and mission"><br><sub>Battle dialogue and mission</sub></td><td><img src="docs/screenshots/09-battle-message.png" alt="Battle message"><br><sub>Battle message</sub></td><td><img src="docs/screenshots/07-tutorial.png" alt="Tutorial"><br><sub>Tutorial</sub></td></tr>
<tr><td><img src="docs/screenshots/02-options.png" alt="Options"><br><sub>Options</sub></td><td><img src="docs/screenshots/01-save-prompt.png" alt="Save data prompt with YES/NO"><br><sub>Save data prompt with YES/NO</sub></td><td><img src="docs/screenshots/05-story-dialogue.png" alt="Story dialogue"><br><sub>Story dialogue</sub></td></tr>
</table>

---

# For developers

## No game data here

This repository does **not** contain and will **not** distribute any game files, ISOs, keys or copyrighted assets.
To build the patch, you need your own copies of both games:

| Game | Platform | ID | Notes |
|---|---|---|---|
| Shin Gundam Musou | PS Vita (JP) | `PCSG00278` v1.00 | Decrypted dump |
| Dynasty Warriors: Gundam Reborn | PS3 (EU) | `BLES02057` | Decrypted ISO |

The `.gitignore` uses an allow-list, so it ignores everything except source files.

## Building the patch

Requirements: Windows, Python 3.10+ with Pillow and keystone-engine, 7-Zip and xdelta3
(`tools/bin/xdelta3.exe`). Inputs (all from your own copies, see `scripts/make_release.py` for paths):

- decrypted Vita `LINKDATA_NGP/LINKDATA.B` and `.C` → `decrypted/vita/LINKDATA_NGP/`
  (Vita3K install, or VitaShell *Open decrypted*), original `sce_sys/param.sfo` → `decrypted/vita/param.sfo.orig`
  (and the update's → `decrypted/vita/param_102.sfo.orig`; only for the experimental `tools/build_sfo.py`)
- FAGDec output `eboot.bin.elf` + `self_auth.bin` → `PCSG00278_100/` (game 1.00) and `PCSG00278_102/`
  (update 1.02; `python -P tools/unfself.py eboot.bin eboot.bin.elf` turns FAGDec's decrypted SELF into the ELF)
- PS3 `LINKDATA_PS3/LINKDATA.B` and `.C` extracted from the ISO with 7-Zip → `decrypted/ps3/PS3_GAME/USRDIR/LINKDATA_PS3/`

Then:

```sh
python -P scripts/make_release.py 0.2.0
```

This builds the patched eboot (fself, one per game version), `LINKDATA.B` (text) and `LINKDATA.C` (font + images) into
`build/`, creates xdelta patches, verifies they round-trip, and writes `release/…zip`. The individual steps are
`tools/build_font.py`, `tools/build_images.py` and `tools/build_text.py`.

## How it works

### `LINKDATA` archives

`LINKDATA.A`–`D` are uncompressed. They use little-endian byte order on Vita and big-endian on PS3.

```
u32 magic (0x77df9), u32 count, u32 align (0x800), u32 0
count × { u64 offset_in_blocks, u32 size, u32 0 }
data, each entry aligned to 0x800
```

All text is UTF-8 and lives in `LINKDATA.B`. Text entries on Vita at index ≥ 112 correspond to the PS3 entry at
**index + 2**.

**String tables** (mission dialogue):

```
u32 count, count × { u32 offset, u32 length_incl_nul }, strings…
```

**Section containers** can be nested, with sections aligned to 4 bytes:

```
u32 count, count × { u32 offset, u32 size }, sections…
```

**Table entries** (names, menus, tutorials):

```
u16 table_id, u16 count, u32 offsets[count]  (offsets[0] = 0, relative to 4 + 4·count)
records: u16 length, bytes, NUL, zero-pad to 4
entry is zero-padded to a 16-byte boundary and ends with 0x1A
```

`tools/build_text.py` keeps every Vita structure and script byte as-is and swaps in only the PS3 strings. Where the
PS3 line is blank or the counts differ, it keeps the Japanese original.

## Repository layout

```
tools/linkdata.py        LINKDATA reader / writer
tools/build_text.py      English LINKDATA.B (text port, story scenes, pre-wrapping)
tools/story.py           story/event scene format (entry 171)
tools/textwrap_vita.py   line breaking + per-string text scale markers
tools/build_font.py      font atlas widths + eboot hooks (proportional text, word wrap, scale) -> fself
tools/build_images.py    English textures from the PS3 release (buttons, title cards, logos, notice)
tools/build_sfo.py       English game name in param.sfo (experimental, not in the release yet)
tools/unfself.py         decrypted SELF (FAGDec) -> ELF
tools/g1t*.py, dxt.py    G1T texture decoding / DXT5 encoding
tools/re/                reverse-engineering helpers for the eboot
scripts/make_release.py  full build + xdelta release package (+ the web patcher's patch files)
docs/index.html          web patcher (GitHub Pages); docs/patcher/ has its VCDIFF decoder and zip writer
```

## Credits

- English localization: Bandai Namco / Koei Tecmo (*Dynasty Warriors: Gundam Reborn*, PS3)
- Tools used: Vita3K, VitaShell, rePatch, FAGDec, xdelta3, capstone, keystone, Pillow

This is an unofficial fan project and is not affiliated with Bandai Namco, Koei Tecmo or Sunrise.

## License

The code in this repository (tools and scripts) is released under the [MIT License](LICENSE).

The license does not cover the games or anything taken from them. *Shin Gundam Musou* and *Dynasty Warriors:
Gundam Reborn*, including their text, graphics and code, belong to their respective owners (©SOTSU・SUNRISE,
Bandai Namco, Koei Tecmo). The release patches contain English text and images from the PS3 release and are
meant only for use with a copy of the game you own.
