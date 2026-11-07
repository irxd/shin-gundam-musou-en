"""Pre-wrap English text for Vita text boxes that do not wrap by themselves.

Widths are in "full-width units": one CJK glyph = 1.0, an ASCII glyph = width_px / 20 (the game draws
ASCII with the left-aligned full-width Latin glyphs; see build_font.py, which writes ascii_widths.json).
A box's width is estimated from the hand-placed line breaks of the Japanese text shown in it.
"""
import json, re

TAG = re.compile(r'(\[[a-z/]\]|\[\d+:[A-Za-z_0-9]+\])')
PLACEHOLDER_JA, PLACEHOLDER_EN = 5.0, 8.0     # estimated width of a [n:NAME] substitution
MIN_BOX = 14.0                                 # narrowest wrapping box seen (mission objective panel)
SCALE_BASE, SCALE_MIN, SCALE_FULL = 0x60, 16, 32  # must match build_font.py (marker ESC + chr(0x60 + s))
# characters the Vita font lacks -> closest glyph it has
FIXUPS = {'Ü': 'U', 'ü': 'u', 'ä': 'a', 'ö': 'o', 'é': 'e', '—': '―', '\xa0': ' '}


class Metrics:
    def __init__(self, path):
        self.w = {k: v / 20 for k, v in json.load(open(path)).items()}

    def width(self, s, ph=PLACEHOLDER_EN):
        w = 0.0
        for part in TAG.split(s):
            if not part:
                continue
            if TAG.fullmatch(part):
                w += ph if part[1].isdigit() else 0
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

    def wrap(self, s, lim, max_lines):
        """Return s with line breaks so every line fits lim. Keeps the original breaks when that still
        fits in max_lines, otherwise reflows the whole text (fewest lines)."""
        if self.line_width(s) <= lim:
            return s
        keep = [l for p in s.split('\n') for l in self._greedy(p, lim)]
        flow = self._greedy(s.replace('\n', ' '), lim)
        return '\n'.join(keep if len(keep) <= max_lines or len(keep) <= len(flow) else flow)

    def fit(self, s, lim, max_lines):
        """Wrap s for a box of lim units x max_lines lines. If it does not fit at full size, shrink:
        returns (text, scale out of 32) for the largest scale whose wrapped height fits; the text then
        starts with the ESC scale marker read by the eboot hook (build_font.py build_fit_code)."""
        w = self.wrap(s, lim, max_lines)
        if w.count('\n') + 1 <= max_lines:
            return w, SCALE_FULL
        for sc in range(SCALE_FULL - 1, SCALE_MIN - 1, -1):
            w = self.wrap(s, lim * SCALE_FULL / sc, max_lines)
            if (w.count('\n') + 1) * sc <= max_lines * SCALE_FULL:
                break
        return '\x1b' + chr(SCALE_BASE + sc) + w, sc


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
