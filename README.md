# Shin Gundam Musou (PS Vita) — English Patch

An English translation patch for **Shin Gundam Musou** (真・ガンダム無双, PS Vita, Japan only, `PCSG00278`).

The game was released in the West only on PS3, as *Dynasty Warriors: Gundam Reborn*. This project ports that
**official English localization** from the PS3 release onto the Japanese Vita release. Both versions run on the same
engine and use the same data layout.

> **Status: work in progress, not playable in English yet.** No patch release is available. This repository
> contains only the tools used to build the patch.

## Progress

| Area | Status |
|---|---|
| Archive format (`LINKDATA`) | ✅ Read / write, byte-exact round trip |
| Mission dialogue & messages | ✅ Ported (~66k strings) |
| Names, menus, items, tutorials | ✅ Ported (~5k strings) |
| Story narration (`LINKDATA.B` entry 171) | ⏳ Format not decoded yet |
| Lines blank on PS3 (~780) / 5 tables with differing line counts | ⏳ Needs manual review |
| Font (English text renders monospace / overly wide) | ⏳ To do |
| Images containing Japanese text | ⏳ To do |
| Patch distribution (xdelta + rePatch) | ⏳ To do |

Tested in [Vita3K](https://vita3k.org/) so far.

## No game data here

This repository does **not** contain and will **not** distribute any game files, ISOs, keys or copyrighted assets.
To build the patch, you need your own copies of both games:

| Game | Platform | ID | Notes |
|---|---|---|---|
| Shin Gundam Musou | PS Vita (JP) | `PCSG00278` v1.00 | Decrypted dump |
| Dynasty Warriors: Gundam Reborn | PS3 (EU) | `BLES02057` | Decrypted ISO |

The `.gitignore` uses an allow-list, so it ignores everything except source files.

## Building

Requirements: Python 3.10+ (standard library only) and 7-Zip.

### 1. Decrypt the Vita dump

Use one of these options:

- **Vita3K:** zip the `app/PCSG00278` folder and install it with *File → Install .zip, .vpk*. The decrypted files
  end up in `%APPDATA%\Vita3K\Vita3K\ux0\app\PCSG00278\`.
- **VitaShell** on a modded Vita: open the game folder, press Triangle, choose *Open decrypted* and copy the files.
- **psvpfsparser** (NoNpDRM dumps):
  `powershell -ExecutionPolicy Bypass -File scripts\decrypt_vita.ps1 -Parser C:\path\to\psvpfsparser.exe`

Copy the decrypted `LINKDATA_NGP/LINKDATA.B` to `decrypted/vita/LINKDATA_NGP/LINKDATA.B`.

### 2. Extract the PS3 text archive

```sh
7z x -o"decrypted/ps3" "Dynasty Warriors - Gundam Reborn (Europe).iso" "PS3_GAME/USRDIR/LINKDATA_PS3/LINKDATA.B"
```

The ISO must be decrypted. Redump-style images may need PS3Dec and the disc key first.

### 3. Build the English text archive

```sh
python tools/build_text.py \
  decrypted/vita/LINKDATA_NGP/LINKDATA.B \
  decrypted/ps3/PS3_GAME/USRDIR/LINKDATA_PS3/LINKDATA.B \
  build/rePatch/PCSG00278/LINKDATA_NGP/LINKDATA.B
```

### 4. Test

- **Vita3K:** copy the built `LINKDATA.B` over the one in `ux0/app/PCSG00278/LINKDATA_NGP/`. Keep a backup.
- **Vita:** copy `build/rePatch/PCSG00278/` to `ux0:rePatch/PCSG00278/`. This requires the rePatch plugin.

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
