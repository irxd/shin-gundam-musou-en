# Shin Gundam Musou (PS Vita) — English Patch

An English translation patch for **Shin Gundam Musou** (真・ガンダム無双, PS Vita, Japan only, `PCSG00278`).

The game was released in the West only on PS3, as *Dynasty Warriors: Gundam Reborn*. This project ports that
**official English localization** from the PS3 release onto the Japanese Vita release. Both versions run on the same
engine and use the same data layout.

> **Status: playable in English (v0.1.0, early test release).** Tested in Vita3K; real-hardware testing in
> progress. The release is a set of xdelta patches — see [docs/INSTALL.md](docs/INSTALL.md).

## Progress

| Area | Status |
|---|---|
| Archive format (`LINKDATA`) | ✅ Read / write |
| Mission dialogue & messages | ✅ Ported (~66k strings) |
| Names, menus, items, tutorials, help | ✅ Ported (~5k strings) |
| Story scenes & narration (`LINKDATA.B` entry 171) | ✅ Ported (5,461 lines) |
| Font | ✅ Proportional Latin glyphs, word wrap, per-string shrink for long text (eboot patch) |
| Line breaking | ✅ Pre-wrapped to the Vita box sizes |
| Images: YES/NO/OK buttons, chapter title cards, boot notice & logo, title screen | ✅ Done |
| Game name in the home screen (`param.sfo`) | ✅ Optional patch |
| Lines blank on PS3 (~780) / 5 tables with differing line counts | ⏳ Still Japanese |
| Other images with Japanese text (tutorial pictures, …) | ⏳ To do |
| Release packaging (xdelta + rePatch) | ✅ `scripts/make_release.py` |

## No game data here

This repository does **not** contain and will **not** distribute any game files, ISOs, keys or copyrighted assets.
To build the patch, you need your own copies of both games:

| Game | Platform | ID | Notes |
|---|---|---|---|
| Shin Gundam Musou | PS Vita (JP) | `PCSG00278` v1.00 | Decrypted dump |
| Dynasty Warriors: Gundam Reborn | PS3 (EU) | `BLES02057` | Decrypted ISO |

The `.gitignore` uses an allow-list, so it ignores everything except source files.

## Building

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
tools/linkdata.py      LINKDATA reader / writer
tools/build_text.py    builds the English LINKDATA.B
tools/*.py             research / probing scripts used to map the formats
scripts/               helper scripts (Vita decryption)
```

## Credits

- English localization: Bandai Namco / Koei Tecmo (*Dynasty Warriors: Gundam Reborn*, PS3)
- Tools used: Vita3K, VitaShell, rePatch, psvpfstools

This is an unofficial fan project and is not affiliated with Bandai Namco, Koei Tecmo or Sunrise.
