"""Keskeny, 3 pont széles betűk a 16 színű címlaphoz (a font.py 5 pontos rajzolatából összevonva,
néhány kézzel javítva). 9 sor: 0-1. ékezet / felnyúlás, 2-7. betűtest, 8. lenyúlás."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import font

KEZI = {
    'm': ['...', '...', '...', '#.#', '###', '###', '#.#', '#.#', '...'],
    'n': ['...', '...', '...', '##.', '#.#', '#.#', '#.#', '#.#', '...'],
    'ő': ['#.#', '#.#', '...', '###', '#.#', '#.#', '#.#', '###', '...'],
    'á': ['..#', '.#.', '...', '###', '..#', '###', '#.#', '###', '...'],
    'é': ['..#', '.#.', '...', '###', '#.#', '###', '#..', '###', '...'],
    'ó': ['..#', '.#.', '...', '###', '#.#', '#.#', '#.#', '###', '...'],
    'Á': ['..#', '###', '#.#', '#.#', '###', '#.#', '#.#', '#.#', '...'],
    'É': ['..#', '###', '#..', '#..', '###', '#..', '#..', '###', '...'],
}

def glyph(ch):
    if ch in KEZI: return KEZI[ch]
    E = '.....'
    rows = [E] * 10
    if ch in font.UPPER_ACC:
        base, acc = font.UPPER_ACC[ch]; rows[2:10] = font.G[base]; rows[0:2] = acc
    elif ch in font.LOWER_ACC:
        base, acc = font.LOWER_ACC[ch]; rows[2:10] = font.G[base]; rows[2:4] = acc
    elif ch == 'í':
        rows[2:10] = font.G['i']; rows[2:4] = font.ACUTE
    else:
        rows[2:10] = font.G[ch]
    return [''.join('#' if any(r[c] == '#' for c in cols) else '.' for cols in ((0, 1), (2,), (3, 4)))
            for r in rows[1:]]

def write(scr, y0, s, color, x0=None, cell=4):
    w = len(s) * cell - 1
    if x0 is None: x0 = (scr.shape[1] - w) // 2
    for i, ch in enumerate(s):
        for dy, row in enumerate(glyph(ch)):
            for dx, c in enumerate(row):
                if c == '#': scr[y0 + dy, x0 + i * cell + dx] = color
    return x0, w
