# Shin Gundam Musou (PS Vita) — English Patch

An English translation patch for **Shin Gundam Musou** (真・ガンダム無双, PS Vita, Japan only, `PCSG00278`).

The game was released in the West only on PS3, as *Dynasty Warriors: Gundam Reborn*. This project ports that
**official English localization** from the PS3 release onto the Japanese Vita release. Both versions run on the same
engine and use the same data layout.

> **Status: fully playable in English (v1.0.0; game versions 1.00 and 1.02).** Tested on a real
> PS Vita and in Vita3K.
>
> **Patch it in your browser with the [web patcher](https://irxd.github.io/shin-gundam-musou-en/)** or download the patch files
> from the [Releases](https://github.com/irxd/shin-gundam-musou-en/releases) page and use Delta Patcher. See [Installation](#installation).

<p align="center"><img src="docs/screenshots/05-story-dialogue.png" width="420" alt="Story scene with English dialogue, on a PS Vita"> <img src="docs/screenshots/08-battle-dialogue.png" width="420" alt="Battle with English dialogue and mission, on a PS Vita"></p>

More screenshots: [Screenshots](#screenshots).

## Installation

You patch files from **your own copy** of the game. No game data is included.

### What you need

- **The game:** Shin Gundam Musou, **PCSG00278**, version **1.00** or **1.02**.
  If the folder `ux0:patch/PCSG00278/` exists on your Vita, you have 1.02. Otherwise you have 1.00.
- **On the Vita:** HENkaku/Ensō, the **rePatch** plugin, **FAGDec** and **VitaShell**.
- **On the PC:** Chrome or Edge, for the [web patcher](https://irxd.github.io/shin-gundam-musou-en/).

Playing on Vita3K instead? See [Vita3K](#vita3k).

### Real PS Vita

**1. Get the eboot (with FAGDec)**

1. Open FAGDec, select **真・ガンダム無双** and press ✕.
2. Select the eboot for your version and press ✕:
   - **1.00:** `ux0:app/PCSG00278/eboot.bin`
   - **1.02:** `ux0:patch/PCSG00278/eboot.bin`
3. Press ○, then START, and choose **START DECRYPT (ELF)**.
4. Copy the `eboot.bin.elf` it made to your PC. It is in `ux0:FAGDec/app/PCSG00278/` (1.00) or
   `ux0:FAGDec/patch/PCSG00278/` (1.02).

**2. Get the game data (with VitaShell)**

1. Go to `ux0:app/PCSG00278/`, press △ and choose **Open decrypted**.
2. Copy `LINKDATA_NGP/LINKDATA.B` and `LINKDATA_NGP/LINKDATA.C` to your PC (`LINKDATA.C` is about 1 GB):
   - **FTP** (VitaShell: press SELECT): copy them from the folder you opened decrypted.
   - **USB:** USB mode gives the still-encrypted files. First copy both files in VitaShell (△ → Copy) and paste
     them into another folder, e.g. `ux0:data/`. Then copy them from that folder over USB.

**3. Optional: English DLC (advanced)**

Skip this if you like: DLC you have installed still works, just in Japanese.

For English DLC, the web patcher needs the DLC files **decrypted**. VitaShell can't decrypt DLC, so you decrypt
them on the PC. Skip to step 4 if your DLC files are already decrypted.

1. With VitaShell, copy these two folders to your PC:
   - `ux0:addcont/PCSG00278/` (the DLC)
   - `ux0:license/addcont/PCSG00278/` (its licenses)

   Have the DLC as a PKG dump (NoPayStation / pkg2zip) instead? Its `addcont/PCSG00278` folder works too, and you
   don't need the licenses folder.
2. Install [Python](https://www.python.org/downloads/). Unzip the
   [release zip](https://github.com/irxd/shin-gundam-musou-en/releases), then unzip
   [psvpfsparser](https://github.com/motoharu-gosuto/psvpfstools/releases) into that release folder.
3. Open a terminal in the release folder and run (with your own paths):

   ```
   python tools\decrypt_dlc.py "C:\path\to\addcont\PCSG00278" "C:\path\to\license\addcont\PCSG00278"
   ```

   Leave out the second path for a PKG dump. You need an internet connection: psvpfsparser asks an online key
   service once per DLC. The decrypted DLC goes into a new `PCSG00278_decrypted` folder next to the DLC folder.

> **Adding English DLC later?** You **must** re-patch your original `eboot.bin.elf` together with the DLC folder
> (and copy the new `eboot.bin` too). There are two separate eboot variants (one without DLC and one with DLC);
> if you only patch the DLC folder and keep your old `eboot.bin`, the game will ignore the patched DLC (see
> [Known issues](#known-issues) for why).

**4. Patch the files**

1. Open the **[web patcher](https://irxd.github.io/shin-gundam-musou-en/)** in Chrome or Edge.
2. Choose your `eboot.bin.elf`, `LINKDATA.B` and `LINKDATA.C`. For English DLC, also choose the folder with the
   decrypted DLC (`PCSG00278_decrypted` from step 3) under **DLC folder**.
3. Press **Patch**. You get a `rePatch` folder (or a zip with it).

Everything runs in your browser; nothing is uploaded.

**5. Copy to the Vita**

Copy the `rePatch` folder to `ux0:` on the Vita (unzip it first if you chose a zip). Start the game. Done!

Your game files in `ux0:app` and `ux0:patch` are not changed.

**6. Optional: English game name on the home screen**

The name under the game's icon stays Japanese unless you do this.

1. Don't install or delete apps on the Vita until you've finished these steps.
2. With VitaShell, copy `ur0:shell/db/app.db` to your PC. Keep this file as a backup.
3. In the [web patcher](https://irxd.github.io/shin-gundam-musou-en/), choose it under
   **Optional: English game name**. It saves a new `app.db`.
4. Copy the new `app.db` to `ur0:shell/db/app.db`, replacing it, and restart the Vita.

(Without the web patcher: `python tools/rename_title.py app.db`, from the `tools` folder in the release zip.)

### Updating to a new patch version

Do steps 1–5 again with your **original, unpatched** files, and replace the old files in `ux0:rePatch/PCSG00278/`.
Keep your original files somewhere safe for this. If the release notes say only some files changed, you can
patch just those.

### Manual patching (Delta Patcher)

Use this only if the web patcher doesn't work for you.

1. Download `shin-gundam-musou-en-<version>.zip` from [Releases](https://github.com/irxd/shin-gundam-musou-en/releases)
   and unzip it.
2. In [Delta Patcher](https://github.com/marco-calautti/DeltaPatcher/releases), apply each patch to its file and put
   the result here:

   | Your file | Patch | Put the result here |
   |---|---|---|
   | `eboot.bin.elf` (1.00) | `patches/eboot_v1.00.xdelta` (with English DLC: `eboot_v1.00_dlc.xdelta`) | `ux0:rePatch/PCSG00278/eboot.bin` |
   | `eboot.bin.elf` (1.02) | `patches/eboot_v1.02.xdelta` (with English DLC: `eboot_v1.02_dlc.xdelta`) | `ux0:rePatch/PCSG00278/eboot.bin` |
   | `LINKDATA.B` | `patches/LINKDATA.B.xdelta` | `ux0:rePatch/PCSG00278/LINKDATA_NGP/LINKDATA.B` |
   | `LINKDATA.C` | `patches/LINKDATA.C.xdelta` | `ux0:rePatch/PCSG00278/LINKDATA_NGP/LINKDATA.C` |
   | DLC: `<folder>/<file>.BIN` | `patches/DLC/<folder>/<file>.BIN.xdelta` | `ux0:rePatch/PCSG00278/DLC/<folder>/<file>.BIN` |

   Use only one eboot patch: the one for your version, and the `_dlc` one only if you also patch the DLC.
   Rename the patched eboot to `eboot.bin`.

Delta Patcher overwrites the file you patch unless you tick **Backup original file**, so keep a copy of your
original files. If a patch fails, check the game version and that the file is decrypted (`checksums.txt` in the
zip lists the expected files).

### Vita3K

1. Find the game in `<Vita3K data>/ux0/app/PCSG00278/`. Back up `eboot.bin`, `LINKDATA_NGP/LINKDATA.B` and
   `LINKDATA_NGP/LINKDATA.C` (with the 1.02 update: also `ux0/patch/PCSG00278/eboot.bin`).
2. Get an `eboot.bin.elf`: either from FAGDec on a Vita (step 1 above), or turn on **ELF dumping** in Vita3K
   (Settings → Debug), start the game once, and rename `elfdumps/PCSG00278/0x81000000-0x8137BCCC_app0.elf` to
   `eboot.bin.elf`.
3. Patch the files with the [web patcher](https://irxd.github.io/shin-gundam-musou-en/) (Vita3K's files are already
   decrypted).
4. From the patcher's `rePatch/PCSG00278/` folder, copy:
   - `LINKDATA_NGP/` into `ux0/app/PCSG00278/`, replacing the files there
   - `eboot.bin` into `ux0/app/PCSG00278/` (1.00) or `ux0/patch/PCSG00278/` (1.02)
   - `DLC/` (only if you patched the DLC) into `ux0/app/PCSG00278/`
5. Optional, English name in the game list: back up `ux0/app/PCSG00278/sce_sys/param.sfo`, choose it in the web
   patcher under **Optional: English game name**, put the new `param.sfo` in its place and restart Vita3K.
   With the 1.02 update, do the same for `ux0/patch/PCSG00278/sce_sys/param.sfo`.

### Removing the patch

Only if you want to go back to the Japanese game. You don't need this to install or update the patch.

- **Real Vita:** delete `ux0:rePatch/PCSG00278/`. If you did step 6, copy your backup `app.db` back to
  `ur0:shell/db/app.db` and restart the Vita.
- **Vita3K:** put back the files you backed up and delete `ux0/app/PCSG00278/DLC/`.

## Known issues

- **DLC not working or still in Japanese after patching:** Make sure your `eboot.bin` matches whether you use
  the patched `DLC/` folder. There are **two eboot variants** per game version (`without DLC` and `with DLC`):
  - **Why:** `rePatch`'s `reAddcont` folder did not work for this game on PS Vita hardware, so as a workaround
    the patched DLC is placed inside `ux0:rePatch/PCSG00278/DLC/` instead (`ux0/app/PCSG00278/DLC/` on Vita3K),
    and the patched eboot with DLC redirects DLC file reads from `addcont0:` to `app0:DLC/`.
  - **If you patched without DLC first and added DLC later:** Simply patching the DLC folder is not enough —
    you are still using the non-DLC `eboot.bin`, which reads from `addcont0:` and ignores `rePatch/PCSG00278/DLC/`.
    Re-patch your **original** `eboot.bin.elf` together with the DLC folder in the web patcher (or apply
    `eboot_v1.00_dlc.xdelta` / `eboot_v1.02_dlc.xdelta` manually) and replace `eboot.bin`.
  - **If you use the eboot with DLC without patched DLC files (or install new DLC later):** Because the eboot with DLC
    reads all DLC from `app0:DLC/`, any installed DLC missing from `ux0:rePatch/PCSG00278/DLC/` will not load.
    Include all installed DLCs when patching, or switch back to the non-DLC `eboot.bin` if you don't use patched DLC.
- Some images still have Japanese text, such as parts of menu screens and one tutorial picture (the network
  menu, which is Japanese on PS3 too). These stay as they are.
- English is longer than Japanese, so long lines in story and battle text boxes are drawn in a smaller font to
  fit, and some very long center-screen mission messages were shortened.

Found another problem? Please [open an issue](https://github.com/irxd/shin-gundam-musou-en/issues).

## What's translated

| Area | Status |
|---|---|
| Mission dialogue & messages | ✅ ~66k strings |
| Names, menus, items, tutorials, help texts | ✅ ~5k strings |
| Story scenes & narration | ✅ 5,461 lines |
| Video cutscene subtitles | ✅ 420 lines (42 cutscenes) |
| Font | ✅ Proportional English text with word wrap; long lines shrink to fit their box |
| Images: YES/NO/OK buttons, chapter title cards, boot notice & logo, title screen, tutorial pictures | ✅ |
| Game name on the home screen | ✅ Optional step (`tools/rename_title.py`) |
| Lines the PS3 release left blank or "......" (menu help, partner skills, battle messages, music titles…) | ✅ Official English from elsewhere in the game, the rest a new fan translation |
| Other images with Japanese text (e.g. parts of menu screens) | ➖ Not planned (see [Known issues](#known-issues)) |
| DLC (17 extra scenarios, 6 extra mobile suit packs) | ✅ Optional (needs decrypted DLC files): official English where the text matches the base game, the rest a new fan translation |

The English comes from the PS3 release, which has no English for some Vita lines: some are left empty and
some just say "......". These are mostly Vita-only content, such as partner skill descriptions, menu help lines,
some Ultimate Mode texts and battle messages, and music titles. For these lines the patch uses the official
English of the same Japanese line where it appears elsewhere in the game, and otherwise a new fan translation
(about 250 lines, in `text/base/`) that uses the official names and terms. The only Japanese left in the text is
developer placeholders the game never shows, such as ダミー ("dummy"). See [How it works](#how-it-works).

Tested on a real PS Vita (1.02, via rePatch), in Vita3K (1.00 and 1.02) and in Vita3K+ 1.4 (1.00).

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
  (and the update's → `decrypted/vita/param_102.sfo.orig`; not needed for the release)
- FAGDec output `eboot.bin.elf` + `self_auth.bin` → `PCSG00278_100/` (game 1.00) and `PCSG00278_102/`
  (update 1.02; `python -P tools/unfself.py eboot.bin eboot.bin.elf` turns FAGDec's decrypted SELF into the ELF)
- PS3 `LINKDATA_PS3/LINKDATA.B` and `.C` extracted from the ISO with 7-Zip → `decrypted/ps3/PS3_GAME/USRDIR/LINKDATA_PS3/`
- all 23 DLCs, decrypted (psvpfsparser with each DLC's NoNpDrm license) →
  `decrypted/vita/addcont/PCSG00278/<DLC folder>/`

Then:

```sh
python -P scripts/make_release.py 1.0.0
```

This builds the patched eboot (fself, one per game version), `LINKDATA.B` (text) and `LINKDATA.C` (font + images) into
`build/`, the English DLC files into `build/rePatch/PCSG00278/DLC/`, creates xdelta patches, verifies they round-trip,
and writes `release/…zip`. The individual steps are `tools/build_font.py`, `tools/build_images.py`,
`tools/build_movies.py`, `tools/build_text.py` and `tools/build_dlc.py`.

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

`tools/build_text.py` keeps every Vita structure and script byte as-is and swaps in only the PS3 strings, line by
line. Where the two versions don't line up:

- **A PS3 table has extra lines at the end** (blank, `......` or `DUMMY`): the extra lines are dropped and the
  rest is matched line by line (5 battle-message tables).
- **The PS3 line is blank, or `......` where the Vita has real text:** the build first looks for the official
  English of the same Japanese line elsewhere in the game (a first pass collects every Japanese → English pair
  the PS3 release has), then for a translation in `text/base/*.json`. If neither exists, the Japanese stays.
- **The PS3 line is itself Japanese:** it is never used. One PS3 table (table 18) holds a Japanese character
  list in the slot where the Vita has partner skill descriptions, so the Vita line is kept and translated.
- **The PS3 line has a mistake** (for example, a name in the wrong placeholder): `text/base/fixes.json`
  replaces it.

`text/base/*.json` and `text/dlc/*.json` map the first 10 hex digits of the SHA-1 of the Japanese line (UTF-8) to
the English, so no Japanese game text is stored in this repository. The build warns when a translation is no
longer used (the Japanese changed). Lines the game never shows (developer placeholders such as ダミー, "dummy")
stay as they are.

## Repository layout

```
tools/linkdata.py        LINKDATA reader / writer
tools/build_text.py      English LINKDATA.B (text port, story scenes, pre-wrapping)
tools/text_short.py      shorter English for lines that would otherwise shrink a lot (banners, story, dialogue)
text/base/               base-game lines with no PS3 English: sha1(Japanese)[:10] -> English
tools/build_dlc.py       English DLC files (scenarios + mobile suit packs), from text/dlc/*.json
text/dlc/                DLC translations: sha1(Japanese)[:10] -> English (no Japanese game text in the repo)
tools/story.py           story/event scene format (entry 171)
tools/textwrap_vita.py   line breaking + per-string text scale markers
tools/build_font.py      font atlas widths + eboot hooks (proportional text, word wrap, scale, DLC path,
                         wider center banners) -> fself
tools/build_images.py    English textures from the PS3 release (buttons, title cards, logos, notice)
tools/build_movies.py    English subtitles for the video cutscenes (LINKDATA.C, PS3 English slot -> Vita Japanese slot)
tools/build_sfo.py       English game name in param.sfo (used by rename_title.py)
tools/decrypt_dlc.py     players: decrypts the DLC with psvpfsparser + each DLC's license (rif / work.bin)
tools/rename_title.py    optional: English game name in app.db (real Vita) or param.sfo (Vita3K)
tools/unfself.py         decrypted SELF (FAGDec) -> ELF
tools/g1t*.py, dxt.py    G1T texture decoding / DXT5 encoding
tools/re/                reverse-engineering helpers for the eboot
scripts/make_release.py  full build + xdelta release package (+ the web patcher's patch files)
docs/index.html          web patcher (GitHub Pages); docs/patcher/ has its VCDIFF decoder, zip writer
                         and title.js (English game name in app.db via sql.js, or param.sfo)
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
