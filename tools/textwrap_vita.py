"""Pre-wrap English text for Vita text boxes that do not wrap by themselves.

Widths are in "full-width units": one CJK glyph = 1.0, an ASCII glyph = width_px / 20 (the game draws
ASCII with the left-aligned full-width Latin glyphs; see build_font.py, which writes ascii_widths.json).
A box's width is estimated from the hand-placed line breaks of the Japanese text shown in it.
"""
import json, re

TAG = re.compile(r'(\[[a-z/]\]|\[\d+:[A-Za-z_0-9]+\])')
PLACEHOLDER_JA, PLACEHOLDER_EN = 5.0, 11.0    # estimated width of a [n:NAME] substitution (long names, e.g. 'Defense Commander')
PLACEHOLDER_CHARA = 7.0                       # [n:CHARA...]: pilot names are short ('Char' 2.7, 'Lunamaria' 5.7)
# battle message type tag ('（吉味）' ...) at the start of a string: the game strips it (it only picks the banner
# style), so it takes no room, and nothing may come before it (a scale marker there makes the game show it)
BATTLE_TAG = re.compile(r'^（[^）\n]{2}）')
MIN_BOX = 14.0                                 # narrowest wrapping box seen (mission objective panel)
SCALE_BASE, SCALE_MIN, SCALE_FULL = 0x60, 16, 32  # must match build_font.py (marker ESC + chr(0x60 + s))
SCALE_BASE_PITCH = 0x50                        # ESC + chr(0x50 + s): same scale, line pitch kept
# characters the Vita font lacks -> closest glyph it has
FIXUPS = {'Ü': 'U', 'ü': 'u', 'ä': 'a', 'ö': 'o', 'é': 'e', '—': '―', '\xa0': ' ', '℠': ''}


class Metrics:
    def __init__(self, path):
        self.w = {k: v / 20 for k, v in json.load(open(path)).items()}

    def width(self, s, ph=PLACEHOLDER_EN):
        w = 0.0
        for part in TAG.split(BATTLE_TAG.sub('', s)):
            if not part:
                continue
            if TAG.fullmatch(part):
                if part[1].isdigit():
                    w += min(ph, PLACEHOLDER_CHARA) if ':CHARA' in part else ph
            else:
                w += sum(self.w.get(c, 1.0) for c in part)
        return w

    def line_width(self, s, ph=PLACEHOLDER_EN):
        return max(self.width(l, ph) for l in s.split('\n'))

    def _greedy(self, para, lim):
        out, cur = [], ''
        for word in para.split(' '):
            if not word:
                continue
            t = cur + ' ' + word if cur else word
            if cur and self.width(t) > lim:
                out.append(cur); cur = word
            else:
                cur = t
        out.append(cur)
        return out

    def wrap(self, s, lim, max_lines, reflow=True):
        """Return s with line breaks so every line fits lim. Keeps the original breaks when that still
        fits in max_lines (or always, without reflow), otherwise reflows the whole text (fewest lines)."""
        if self.line_width(s) <= lim and s.count('\n') < max_lines:
            return s
        keep = [l for p in s.split('\n') for l in self._greedy(p, lim)]
        if not reflow:
            return '\n'.join(keep)
        flow = self._greedy(s.replace('\n', ' '), lim)
        return '\n'.join(keep if len(keep) <= max_lines or len(keep) <= len(flow) else flow)

    def fit(self, s, lim, max_lines, grow=True, reflow=True, fixed=False):
        """Wrap s for a box of lim units x max_lines lines. If it does not fit at full size, shrink:
        returns (text, scale out of 32) for the largest scale whose wrapped text fits. grow: a shrunk
        text may use more lines, as long as their total (scaled) height fits; without it, the line
        count stays within max_lines and the marker keeps the full line pitch (for boxes that also
        draw line by line at full pitch, e.g. story text while it types out). A shrunk text gets the ESC scale marker read by the eboot hook
        (build_font.py, per-string text scale) at its start and after every line break: the hook only
        looks at the start of the string it draws, and some screens draw each line on its own.
        fixed: lines keep the full-size width limit (for widgets that break the text before scaling)."""
        tag = BATTLE_TAG.match(s)
        if tag:     # the marker goes after the tag (see BATTLE_TAG)
            w, sc = self.fit(s[tag.end():], lim, max_lines, grow, reflow, fixed)
            return tag.group() + w, sc
        w = self.wrap(s, lim, max_lines, reflow)
        if w.count('\n') + 1 <= max_lines:
            return w, SCALE_FULL
        for sc in range(SCALE_FULL - 1, SCALE_MIN - 1, -1):
            w = self.wrap(s, lim if fixed else lim * SCALE_FULL / sc, max_lines, reflow)
            n = w.count('\n') + 1
            if (n * sc <= max_lines * SCALE_FULL) if grow else n <= max_lines:
                break
        mark = '\x1b' + chr((SCALE_BASE if grow else SCALE_BASE_PITCH) + sc)
        return mark + w.replace('\n', '\n' + mark), sc


def fixup(s):
    return ''.join(FIXUPS.get(c, c) for c in s)


def box_of(metrics, japanese):
    """Estimate (width limit, max lines) of the box a group of Japanese strings is shown in, or None
    when none of them is multi-line (= no evidence of a wrapping box)."""
    multi = [s for s in japanese if '\n' in s]
    if not multi:
        return None
    ws = sorted(metrics.width(l, PLACEHOLDER_JA) for s in multi for l in s.split('\n'))
    # big groups: 99th percentile (ignores a few overflowing lines); small groups: the widest line.
    # Japanese is often broken at a phrase well before the edge, so never go below MIN_BOX.
    w = ws[int(0.99 * (len(ws) - 1))] if len(ws) >= 200 else ws[-1]
    return max(MIN_BOX, w), max(s.count('\n') + 1 for s in japanese)
