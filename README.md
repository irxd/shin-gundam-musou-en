# Shin Gundam Musou (PS Vita) — English Patch

An English translation patch for **Shin Gundam Musou** (真・ガンダム無双, PS Vita, Japan only, `PCSG00278`).

The game was released in the West only on PS3, as *Dynasty Warriors: Gundam Reborn*. This project ports that
**official English localization** from the PS3 release onto the Japanese Vita release. Both versions run on the same
engine and use the same data layout.

> **Status: playable in English (v0.1.0, early test release).** Tested in Vita3K; real-hardware testing in
> progress. Download the patch from the [Releases](../../releases) page.

## Installation

The patch is a set of small **xdelta** files that you apply to files from **your own copy** of the game. No game
data is included. The full step-by-step guide is in [docs/INSTALL.md](docs/INSTALL.md).

**You need**

- Shin Gundam Musou, Japanese release **PCSG00278, version 1.00**
- A PS Vita on HENkaku/Ensō with the **rePatch** plugin, **FAGDec** and **VitaShell**, or the game installed in
  [Vita3K](https://vita3k.org/)
- An xdelta tool on your PC, such as *xdelta UI* or *Delta Patcher*

**Steps (real Vita)**

1. Download the latest `shin-gundam-musou-vita-english-<version>.zip` from [Releases](../../releases) and unzip it.
2. Decrypt the game's `eboot.bin` with **FAGDec** (to `eboot.bin.elf`). Copy the decrypted
   `LINKDATA_NGP/LINKDATA.B` and `LINKDATA.C` with VitaShell (*Open decrypted*).
3. Apply the patches on your PC:

   | Patch | Apply to | Copy the result to |
   |---|---|---|
   | `eboot.bin.xdelta` | `eboot.bin.elf` | `ux0:rePatch/PCSG00278/eboot.bin` |
   | `LINKDATA.B.xdelta` | `LINKDATA.B` | `ux0:rePatch/PCSG00278/LINKDATA_NGP/LINKDATA.B` |
   | `LINKDATA.C.xdelta` | `LINKDATA.C` | `ux0:rePatch/PCSG00278/LINKDATA_NGP/LINKDATA.C` |
   | `param.sfo.xdelta` *(optional, English name on the home screen)* | `sce_sys/param.sfo` | `ux0:app/PCSG00278/sce_sys/param.sfo` |

4. Reboot the Vita and start the game. To uninstall, delete `ux0:rePatch/PCSG00278/`.

`checksums.txt` in the zip lists the expected SHA-1 of every file. If a patch fails, check that your game is
v1.00 and that the source file is decrypted. For **Vita3K**, see [docs/INSTALL.md](docs/INSTALL.md#vita3k).

## What's translated

| Area | Status |
|---|---|
| Mission dialogue & messages | ✅ ~66k strings |
| Names, menus, items, tutorials, help texts | ✅ ~5k strings |
| Story scenes & narration | ✅ 5,461 lines |
| Font | ✅ Proportional English text with word wrap; long lines shrink to fit their box |
| Images: YES/NO/OK buttons, chapter title cards, boot notice & logo, title screen | ✅ |
| Game name on the home screen | ✅ Optional |
| ~780 lines the PS3 release left blank, 5 tables with different line counts | ⏳ Still Japanese |
| Other images with Japanese text (e.g. tutorial pictures) | ⏳ To do |

## Known issues

- Some menu and table lines are still in Japanese (see the table above).
- Some images with Japanese text remain.
- Long lines in story and battle boxes use a smaller font so they fit.
- Real-hardware testing is still in progress.

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
- FAGDec output `eboot.bin.elf` + `self_auth.bin` → `PCSG00278/`
- PS3 `LINKDATA_PS3/LINKDATA.B` and `.C` extracted from the ISO with 7-Zip → `decrypted/ps3/PS3_GAME/USRDIR/LINKDATA_PS3/`

Then:

```sh
python -P scripts/make_release.py 0.1.0
```

This builds the patched eboot (fself), `LINKDATA.B` (text), `LINKDATA.C` (font + images) and `param.sfo` into
`build/`, creates xdelta patches, verifies they round-trip, and writes `release/…zip`. The individual steps are
`tools/build_font.py`, `tools/build_images.py`, `tools/build_text.py` and `tools/build_sfo.py`.

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
tools/build_sfo.py       English game name in param.sfo
tools/g1t*.py, dxt.py    G1T texture decoding / DXT5 encoding
tools/re/                reverse-engineering helpers for the eboot
scripts/make_release.py  full build + xdelta release package
docs/INSTALL.md          player install guide (shipped in the release zip)
```

## Credits

- English localization: Bandai Namco / Koei Tecmo (*Dynasty Warriors: Gundam Reborn*, PS3)
- Tools used: Vita3K, VitaShell, rePatch, FAGDec, xdelta3, capstone, keystone, Pillow

This is an unofficial fan project and is not affiliated with Bandai Namco, Koei Tecmo or Sunrise.
