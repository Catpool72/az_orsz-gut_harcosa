#!/usr/bin/env python3
"""
Az országút harcosa – zene a TVC hanggenerátorára (saját szerzemények).

A TVC egyszólamú: négyszögjel, f = 195312,5 / (4096 - n) Hz (n: 12 bites osztó, $04/$05 port),
hangerő 4 bit ($06 port 2-5. bit). A lejátszó képkockánként lép (50 Hz), a hangok rövid
lecsengést kapnak (pengetett hangzás).

Kimenet: build/zene.inc – NOTETAB (osztók), és a dalok: db hang, hossz (képkocka) ... ;
hang 0 = szünet, $FF = vissza az elejére (ismétlés), $FE = vége.
"""
import os, re, sys

NAMES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

def freq(note):
    m = re.fullmatch(r'([A-G])(#|b)?(\d)', note)
    n = NAMES[m.group(1)] + {'#': 1, 'b': -1, None: 0}[m.group(2)] + 12 * (int(m.group(3)) + 1)
    return 440.0 * 2 ** ((n - 69) / 12)

def divisor(f):
    n = round(4096 - 195312.5 / f)
    assert 0 <= n < 4095, f
    return n

# --- a dalok: "hang:ütés" párok; a 'ütés' a dal alapegységének többszöröse (lehet tört)
SONGS = {
    # Címzene: országúti rock, E moll, 4/4, nyolcadok (9 képkocka). A riff az alaphangot
    # (orgonapont) váltogatja a dallammal – az egyszólamú gépen ettől hallatszik "akkordnak".
    'MUS_TITLE': (9, True, '''
        E3:1 E3:1 G3:1 E3:1 A3:1 E3:1 B3:1 A3:1 | E3:1 E3:1 G3:1 E3:1 D4:1 B3:1 A3:1 G3:1 |
        C3:1 C3:1 E3:1 C3:1 G3:1 C3:1 A3:1 G3:1 | D3:1 D3:1 F#3:1 D3:1 A3:1 D3:1 B3:1 A3:1 |
        E3:1 E3:1 G3:1 E3:1 A3:1 E3:1 B3:1 A3:1 | E3:1 E3:1 G3:1 E3:1 D4:1 B3:1 A3:1 G3:1 |
        C3:1 C3:1 E3:1 C3:1 G3:1 A3:1 B3:1 C4:1 | D4:1 D3:1 F#3:1 A3:1 D4:1 C4:1 B3:1 A3:1 |
        E4:2 G4:2 B4:3 A4:1 | G4:2 F#4:2 E4:4 | C5:2 B4:2 A4:3 G4:1 | F#4:2 G4:2 A4:4 |
        E4:2 G4:2 B4:3 D5:1 | C5:2 B4:2 A4:2 G4:2 | F#4:2 D4:2 E4:2 F#4:2 | E4:6 R:2 |
    '''),
    # Kézitusa és tűzharc: feszes, kromatikus A moll ostinato (6 képkocka)
    'MUS_FIGHT': (6, True, '''
        A2:1 A2:1 A3:1 A2:1 G3:1 A2:1 F3:1 E3:1 | A2:1 A2:1 A3:1 A2:1 Bb3:1 A3:1 G3:1 F3:1 |
        D3:1 D3:1 D4:1 D3:1 C4:1 D3:1 Bb3:1 A3:1 | E3:1 E3:1 E4:1 E3:1 F4:1 E4:1 D4:1 C#4:1 |
        A2:1 A2:1 A3:1 A2:1 G3:1 A2:1 F3:1 E3:1 | F3:1 F3:1 F4:1 F3:1 E4:1 D4:1 C4:1 Bb3:1 |
        E3:1 F3:1 E3:1 D#3:1 E3:1 G#3:1 B3:1 D4:1 | C4:1 B3:1 A3:1 G#3:1 A3:2 R:2 |
    '''),
    # Autós csata: gyors, motorzúgásszerű oktávugrások E mollban, közte sziréna (5 képkocka)
    'MUS_CAR': (5, True, '''
        E2:1 E3:1 E2:1 E3:1 G2:1 G3:1 A2:1 A3:1 | E2:1 E3:1 E2:1 E3:1 Bb2:1 Bb3:1 A2:1 A3:1 |
        E2:1 E3:1 E2:1 E3:1 G2:1 G3:1 A2:1 A3:1 | B2:1 B3:1 A2:1 A3:1 G2:1 G3:1 F#2:1 F#3:1 |
        B4:2 E5:2 B4:2 E5:2 | B4:2 E5:2 G5:2 F#5:2 |
        C3:1 C4:1 C3:1 C4:1 D3:1 D4:1 E3:1 E4:1 | B2:1 B3:1 B2:1 B3:1 E3:2 R:2 |
    '''),
    # Megnyert harc: rövid, felfelé futó szignál
    'MUS_WON': (6, False, 'E4:1 G4:1 B4:1 E5:3 R:1'),
    # Halál: lassú, lefelé lépő, mint a kifulladó motor
    'MUS_DEATH': (16, False, 'E4:2 D4:1 B3:1 | C4:2 A3:1 R:1 | F#3:2 E3:4 | R:1'),
    # Győzelem (380: hazaérsz Új Reménybe): G-dúr fanfár
    'MUS_WIN': (8, False, 'G4:1 G4:1 G4:1 D5:3 | B4:1 C5:1 D5:2 E5:2 | D5:1 C5:1 B4:1 A4:1 G4:2 B4:1 D5:1 G5:4 R:2'),
}

def parse(spec):
    out = []
    for tok in spec.replace('|', ' ').split():
        n, d = tok.split(':')
        out.append((n, float(d)))
    return out

def build(path):
    notes = sorted({n for _, _, s in SONGS.values() for n, _ in parse(s) if n != 'R'}, key=freq)
    idx = {n: i + 1 for i, n in enumerate(notes)}
    o = ['; generálta a zene.py – saját szerzemények (Az országút harcosa TVC)',
         'NOTETAB:                  ; hang -> 12 bites osztó (f = 195312,5 / (4096 - n))']
    for n in notes:
        o.append(f'        dw {divisor(freq(n))}   ; {n} {freq(n):.1f} Hz')
    for name, (unit, loop, spec) in SONGS.items():
        o.append(f'{name}:')
        b = []
        for n, d in parse(spec):
            fr = round(unit * d)
            while fr > 255: b += [0 if n == 'R' else idx[n], 255]; fr -= 255
            b += [0 if n == 'R' else idx[n], fr]
        b.append(0xFF if loop else 0xFE)
        for i in range(0, len(b), 16):
            o.append('        db ' + ','.join(map(str, b[i:i + 16])))
    open(path, 'w', encoding='utf-8').write('\n'.join(o) + '\n')

def wav(path, rate=22050):
    """előhallgatás: a TVC négyszögjelét és a lecsengést utánozza"""
    import wave, struct
    data = []
    for name, (unit, loop, spec) in SONGS.items():
        for n, d in parse(spec) * (2 if loop else 1):
            frames = round(unit * d)
            f = None if n == 'R' else 195312.5 / (4096 - divisor(freq(n)))
            amp = 11
            for fr in range(frames):
                if fr and fr % 2 == 0 and amp > 3: amp -= 1
                for k in range(rate // 50):
                    t = (len(data)) / rate
                    v = 0 if f is None else (amp if (t * f) % 1 < 0.5 else 0)
                    data.append(v)
        data += [0] * (rate // 2)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        mean = 3
        w.writeframes(b''.join(struct.pack('<h', int((v - mean) * 1800)) for v in data))

if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    build(os.path.join(here, 'build', 'zene.inc'))
    if len(sys.argv) > 1: wav(sys.argv[1])
