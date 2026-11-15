#!/usr/bin/env python3
"""
Az országút harcosa – játékszabályok fejezetenként (kézzel, a könyv szövegéből).

Minden fejezethez egy műveletlista tartozik; a build.py ebből bájtkódot fordít,
amit a kaland.asm/szabaly.asm értelmező futtat, miután a fejezet szövege megjelent.
A választható lapozási célok alapból a fejezet célpontjai (konyv/orszagut.json),
ezeket a GATE / ONLY / HIDE / ADD műveletek szűkítik vagy bővítik.

Feltételek (cond):  'bokszer' = van ilyen tárgy,  '!bokszer' = nincs,  'res' = az előző próba / harc eredménye,
                    ('gold', 200) = legalább 200 Hitel,  ('cnt', KA, 1) = legalább 1 benzinkanna,
                    ('stat', E, 10) = ÉLETERŐ legalább 10,  ('vis', 72) = jártunk már a 72-esen;
                    a '!' előtag (pl. ('!cnt', KA, 1)) tagad.
"""

# ---------------------------------------------------------------- tárgyak és készletek
ITEMS = [
    ('tomlo', 'Műanyag tömlő'), ('feszitovas', 'Feszítővas'), ('granat', 'Kézigránát'),
    ('bilincs', 'Bilincs'), ('terkep', 'Térkép'), ('bokszer', 'Bokszer'), ('dobokes', 'Dobókés'),
    ('lanc', 'Lánc'), ('drotvago', 'Drótvágó'), ('mellény', 'Golyóálló mellény'), ('magnum', 'Magnum'),
    ('tuning', 'Tuningolt motor'),
    ('harapas', ''), ('sinclair', ''),
]
ITEM_ID = {k: i for i, (k, _) in enumerate(ITEMS)}
assert len(ITEMS) <= 64
KEY_ITEMS = []
NO_RANDOM_LOSS = set()
START_ITEMS = []
START_GOLD = 200                                  # Hitel
POTIONS = []
# készletek (darabszám): gyógyszercsomag, rakéta, vasszög, olajtartály, benzinkanna, pótkerék
GY, RK, SZOG, OLAJ, KA, KE = range(6)
COUNTERS = ['Gyógyszer', 'Rakéta', 'Vasszög', 'Olajtartály', 'Benzinkanna', 'Pótkerék']
START_CNT = [10, 4, 3, 2, 0, 2]

# ---------------------------------------------------------------- műveletek
U, E, SZ, T, P = 0, 1, 2, 3, 4                    # ÜGYESSÉG, ÉLETERŐ, SZERENCSE, TŰZERŐ, PÁNCÉLZAT
def st(s, d):        return ('STAT', s, d)
def gold(d):         return ('GOLD', d)
def gain(*it):       return [('GAIN', i) for i in it]
def lose(i):         return ('LOSE', i)
def cnt(i, d):       return ('CNT', i, d)
def gate(t, c):      return ('GATE', t, c)
def only(t):         return ('ONLY', t)
def hide(t):         return ('HIDE', t)
def pick(a, b):      return ('PICK', a, b)
def luck(a=None, b=None):                         # Tedd próbára Szerencsédet! (utána -1)
    return [('LUCK',)] + ([pick(a, b)] if a else [])
def luck0(a, b):     return [('LUCK0',), pick(a, b)]   # "Dobj két kockával... mint szerencséd" (nem csökken)
def skill(a=None, b=None):
    return [('SKILL',)] + ([pick(a, b)] if a else [])
def opp(base, a, b, mod=0): return [('OPP', base, mod), pick(a, b)]   # 1d6+ÜGY+mod >= 1d6+base
def d6(k, a, b):     return [('D6', k), pick(a, b)]    # 1 kocka <= k -> a
def dmg(n, add=0):   return ('DMG', n, add)            # n kocka + add ÉLETERŐ-veszteség
def admg(n, add=0):  return ('ADMG', n, add)           # n kocka + add PÁNCÉLZAT-veszteség
def race(bonus, a, b): return [('RACE', bonus), pick(a, b)]
def iff(c, then, els=None): return ('IF', c, then, els or [])
def flat(*ops):
    out = []
    for o in ops: out += o if isinstance(o, list) else [o]
    return out

def M(name, sk, sta): return (name, sk, sta)
HAND, GUN, CAR = 1, 2, 3
def fight(kind, mons, win=None, hit2=False, norocket=False, sk1=False, ko=False, **kw):
    """kind: HAND (Kézitusa), GUN (Tűzharc, 1 kocka sebzés), CAR (Autós Csata: TŰZERŐ, PÁNCÉLZAT, rakéta);
    hit2: egynél több találat után -1 ÜGYESSÉG; norocket: nem lőhetsz rakétát; sk1: a skmod csak az
    1. körben; ko: kiütés 6 elvesztett pontnál (res=1, ha téged ütöttek ki).
    kw: all (egyszerre lőnek rád), pdmg/mdmg (rögzített sebzés), skmod, ev=(típus, param)"""
    kw['ext'] = 0x80 | kind | hit2 << 2 | norocket << 3 | sk1 << 4 | ko << 5
    ops = [('FIGHT', mons, kw)]
    if win is not None: ops.append(only(win))
    return ops

EV_LOSE_ROUND, EV_FIRST_ROUND, EV_WIN_N, EV_SURVIVE_N, EV_WIN_ROUND, EV_FLEE6 = 1, 2, 3, 4, 5, 6

R = {}
def r(n, *ops):
    R[n] = flat(*ops)

# --- pontok, készletek, tárgyak, Hitel
r(2, st(U, -1), st(E, -2), cnt(GY, -1), gain('tomlo'))
r(4, st(E, 2))
r(10, gain('feszitovas'))
r(11, cnt(RK, -127), cnt(SZOG, -127), cnt(OLAJ, -127), st(SZ, -2))
r(13, st(P, -1), gate(127, ('cnt', SZOG, 1)), gate(361, ('cnt', OLAJ, 1)))
r(14, st(E, 3))
r(16, st(E, 2))
r(19, cnt(KE, -1))
r(20, st(SZ, 1))
r(21, st(P, 2))
r(31, cnt(RK, -1))
r(33, st(E, -1))
r(38, cnt(GY, -1))
r(51, st(SZ, -1))
r(58, st(E, 2), gain('granat'))
r(65, st(E, -2))
r(75, st(SZ, -1))
r(80, st(SZ, -1))
r(90, st(U, 1), st(E, 4), skill(147, 18))
r(97, gain('dobokes'))
r(99, cnt(KA, -1))
r(101, st(SZ, 1))
r(110, st(E, 2))
r(111, cnt(KA, 1))
r(112, st(E, 2), cnt(KA, 2))
r(122, gold(200), gain('bilincs', 'terkep'))
r(131, gold(150), gain('bokszer'))
r(141, gold(-100), cnt(GY, -2), st(SZ, 1), gain('tuning'))
r(146, gain('lanc'))
r(152, st(P, -2))
r(155, st(SZ, -1))
r(166, cnt(KE, 1))
r(169, gold(-200), st(P, 10))
r(180, cnt(KA, -1))
r(185, gain('drotvago'), iff(('vis', 72), [hide(72)]))
r(197, cnt(KA, -1))
r(199, cnt(RK, -1))
r(206, gold(200), gain('bilincs', 'terkep'))
r(212, st(P, -2))
r(223, cnt(KE, -1))
r(233, st(SZ, -1), iff(('vis', 185), [hide(185)]))
r(239, st(SZ, -1))
r(241, st(E, -1), gain('harapas'))
r(246, iff(('vis', 112), [hide(112)]))
r(247, st(P, -2))
r(256, cnt(GY, -1))
r(258, cnt(GY, -1))
r(262, st(SZ, 1), gain('sinclair'))
r(276, st(E, 2))
r(277, st(SZ, 1), st(U, 1), gain('mellény'))
r(278, st(SZ, -1))
r(285, st(SZ, 1))
r(287, st(P, -2))
r(297, st(E, 2))
r(301, st(SZ, -1))
r(306, st(SZ, 1), cnt(KA, 1))
r(314, st(SZ, 1))
r(317, st(SZ, -1))
r(319, st(E, 4))
r(310, cnt(KA, -1))
r(323, cnt(KA, -1))
r(327, st(E, 1))
r(346, cnt(KE, -1))
r(348, st(E, 1))
r(359, st(SZ, 1), cnt(KA, 1))
r(361, cnt(OLAJ, -1))
r(369, gold(-200))
r(372, cnt(RK, -1))
r(375, gain('magnum'))
# --- feltételes lapozás
r(15, gate(169, ('gold', 200)))
r(28, gate(141, ('gold', 100)), gate(141, ('cnt', GY, 2)))
r(40, gate(81, ('stat', U, 6)), gate(296, ('!stat', U, 6)))
r(41, gate(165, ('cnt', OLAJ, 1)))
r(44, gate(273, 'bokszer'), gate(214, '!bokszer'))
r(228, gate(273, 'bokszer'), gate(214, '!bokszer'))
r(293, gate(56, 'bokszer'), gate(125, '!bokszer'))
for n, a, b in [(46, 310, 364), (96, 180, 364), (118, 99, 364), (225, 197, 364), (272, 323, 364)]:
    r(n, gate(a, ('cnt', KA, 1)), gate(b, ('!cnt', KA, 1)))      # benzin
r(74, gate(275, 'harapas'), gate(380, '!harapas'))
r(132, gate(275, 'harapas'), gate(380, '!harapas'))
r(78, gate(199, ('cnt', RK, 1)))
r(203, gate(372, ('cnt', RK, 1)))
r(292, gate(31, ('cnt', RK, 1)), gate(173, ('!cnt', RK, 1)))
r(320, gate(31, ('cnt', RK, 1)), gate(173, ('!cnt', RK, 1)))
r(85, gate(107, ('stat', E, 10)), gate(326, ('!stat', E, 10)))
r(339, gate(107, ('stat', E, 10)), gate(326, ('!stat', E, 10)))
# 94: vasszög VAGY olaj -> 328, egyik sem -> 284
r(94, iff(('cnt', SZOG, 1), [hide(284)], [iff(('cnt', OLAJ, 1), [hide(284)], [hide(328)])]))
r(104, gate(306, 'tomlo'), gate(187, '!tomlo'))
r(109, gate(277, 'feszitovas'))
r(128, gate(312, ('cnt', SZOG, 1)), gate(165, ('cnt', OLAJ, 1)))
r(198, gate(85, 'drotvago'), gate(255, '!drotvago'))
r(251, gate(223, ('cnt', KE, 1)), gate(343, ('!cnt', KE, 1)))
r(313, gate(19, ('cnt', KE, 1)), gate(336, ('!cnt', KE, 1)))
r(370, gate(19, ('cnt', KE, 1)), gate(336, ('!cnt', KE, 1)))
r(253, gate(2, ('cnt', GY, 1)), gate(357, ('!cnt', GY, 1)))
r(259, gate(369, ('gold', 200)))
r(296, gate(174, 'mellény'), gate(263, '!mellény'))
r(300, gate(240, ('gold', 200)))
# 340: ha csak az egyik van meg, a másik nem választható (ha egyik sincs, marad mindkettő)
r(340, iff(('cnt', SZOG, 1), [], [iff(('cnt', OLAJ, 1), [hide(318)])]),
       iff(('cnt', OLAJ, 1), [], [iff(('cnt', SZOG, 1), [hide(213)])]))
r(351, gate(210, 'tuning'), gate(358, '!tuning'))
# --- próbák
for n, a, b in [(3, 354, 247), (7, 319, 136), (32, 76, 160), (39, 171, 29), (43, 175, 201), (45, 304, 60),
                (59, 73, 121), (64, 242, 313), (71, 172, 37), (93, 268, 178), (142, 299, 25), (147, 235, 279),
                (157, 222, 315), (182, 227, 116), (190, 345, 30), (219, 288, 236), (221, 7, 331),
                (255, 339, 145), (273, 170, 250), (304, 238, 370), (332, 16, 84), (335, 5, 365),
                (338, 320, 105), (347, 204, 65), (355, 316, 184)]:
    r(n, luck(a, b))
r(148, st(SZ, -1), luck(354, 247))
r(312, cnt(SZOG, -1), luck(181, 41))
r(318, cnt(SZOG, -1), luck(63, 98))
r(295, st(P, -2), admg(1), luck(122, 329))
for n, a, b in [(23, 137, 342), (42, 161, 186), (67, 200, 248), (70, 62, 133), (125, 349, 202), (135, 193, 36),
                (144, 68, 168), (162, 94, 123), (170, 363, 87), (176, 108, 350), (217, 285, 50), (218, 52, 324),
                (270, 70, 231), (326, 113, 289), (333, 57, 86), (365, 308, 120), (377, 338, 191)]:
    r(n, skill(a, b))
r(139, st(P, -2), skill(8, 287))
r(240, gold(-200), skill(3, 148))
r(77, luck0(290, 352))
r(82, luck0(39, 244))
r(30, dmg(1), opp(7, 74, 226, -1))
r(345, opp(7, 74, 226))
r(35, opp(8, 379, 51))
r(164, opp(7, 132, 205))
r(55, d6(3, 110, 14))
r(127, cnt(SZOG, -1), d6(4, 373, 220))
r(154, st(E, -2), d6(2, 245, 376))
r(165, cnt(OLAJ, -1), d6(5, 234, 280))
r(214, d6(4, 192, 347))
r(250, d6(4, 192, 347))
r(245, st(E, -2), d6(2, 360, 376))
r(254, d6(3, 129, 101))
r(360, st(E, -2))
r(210, race(1, 54, 322))
r(358, race(0, 54, 322))
# --- sebzés kockával
for n in (29, 36, 72, 84, 279):
    r(n, dmg(1))
r(86, dmg(1, 2))
r(195, dmg(2))
for n in (37, 60, 98, 105, 121, 129, 133, 168, 186, 201, 315):
    r(n, admg(2))
r(342, admg(1))
r(191, admg(1), admg(2))
r(213, cnt(OLAJ, -1), st(SZ, -1), admg(2))

# --- harcok
r(6, fight(GUN, [M('Első motoros', 6, 15), M('Második motoros', 7, 15)], 307, hit2=True, all=1))
r(299, st(E, -2), fight(GUN, [M('Első motoros', 7, 13), M('Második motoros', 5, 14)], 97, hit2=True, all=1))
kutyak = [M('Pusztulás Kutyái I.', 7, 13), M('Pusztulás Kutyái II.', 8, 14)]
r(102, fight(GUN, kutyak, 154, hit2=True, all=1))
r(184, fight(GUN, kutyak, 69, hit2=True, all=1))
r(12, fight(GUN, [M('Útonálló', 8, 12)], 131, hit2=True, skmod=-1))
r(227, fight(GUN, [M('Útonálló', 8, 12)], 131, hit2=True, skmod=-1))
r(116, dmg(1), fight(GUN, [M('Útonálló', 8, 12)], 131, hit2=True, skmod=-2))
r(178, fight(GUN, [M('Törvényenkívüli', 9, 12)], 375, hit2=True, skmod=-2, sk1=True))
r(193, fight(GUN, [M('Bandita', 7, 11)], 64, hit2=True, skmod=1))
r(368, fight(GUN, [M('Bandita', 7, 11)], 64, hit2=True, skmod=1))
r(291, fight(GUN, [M('Párbajhős', 9, 9)], 208, ev=(EV_SURVIVE_N, 1)))
r(48, fight(HAND, [M('Orgyilkos', 7, 10)], ko=True), pick(100, 138))
r(120, fight(HAND, [M('Első Farkas', 8, 7), M('Második Farkas', 8, 8)], 286))
r(350, fight(HAND, [M('Vadkutya', 7, 5)], 89))
r(374, fight(HAND, [M('Vadkutya', 7, 5)], 89))
allat = [M('Állat', 11, 16)]
r(269, iff('bokszer', fight(HAND, allat, 355), fight(HAND, allat, 355, pdmg=1, mdmg=2)))
r(17, st(P, -2), fight(CAR, [M('Páncélmotor', 6, 9)], 103, skmod=-2))
r(49, fight(CAR, [M('Harci szekér', 9, 15)], 91))
ford = [M('Sárga Ford', 8, 16)]
r(63, fight(CAR, ford, 334, norocket=True, pdmg=2, mdmg=2, ev=(EV_SURVIVE_N, 4)))
r(294, fight(CAR, ford, 334, norocket=True, pdmg=2, mdmg=2, ev=(EV_SURVIVE_N, 4)))
r(83, fight(CAR, [M('Helikopter', 8, 11)], 305, skmod=-2))
r(95, fight(CAR, [M('Motorkerékpár', 6, 9)], 249))
r(115, fight(CAR, [M('Első Homokfutó', 7, 10), M('Második Homokfutó', 8, 11)], 194, all=1))
r(158, fight(CAR, [M('Furgon', 10, 19)], 67, norocket=True, ev=(EV_SURVIVE_N, 3)))
r(167, fight(CAR, [M('Vörös Chevrolet', 8, 15)], 188))
r(220, fight(CAR, [M('Oldalkocsis motor', 9, 8)], 143))
r(282, fight(CAR, [M('Oldalkocsis motor', 9, 8)], 143))      # a könyvben itt TŰZERŐ 2 áll (a 220-as párja 9)
r(284, fight(CAR, [M('Toyota', 9, 15), M('Jaguár E-típus', 10, 12), M('Commodore', 8, 13)], 265))
r(328, iff(('cnt', OLAJ, 1), [cnt(OLAJ, -1)], [cnt(SZOG, -1)]), fight(CAR, [M('Toyota', 9, 15)], 265))
r(290, fight(CAR, [M('Páncélkocsi', 9, 20)], 106))
r(352, fight(CAR, [M('Páncélautó', 9, 20)], 33, skmod=-2))
r(331, fight(CAR, [M('Dzsip', 9, 14)], 7))

# ---------------------------------------------------------------- fordítás
OP = {'END': 0, 'STAT': 1, 'GOLD': 2, 'GOLD0': 3, 'GAIN': 4, 'LOSE': 5, 'GATE': 6, 'IF': 7, 'SKIP': 8,
      'LUCK': 9, 'SKILL': 10, 'PICK': 11, 'ONLY': 12, 'DMG': 13, 'FIGHT': 14, 'LOSEITEMS': 15,
      'KEYS': 16, 'SWARM': 17, 'XSET': 18, 'XSUB': 19, 'DMGX': 20, 'ADD': 21, 'HIDE': 22, 'SHOP': 23,
      'ONCHOOSE': 24, 'PICKX': 25, 'DEATH': 26, 'CNT': 27, 'LUCK0': 28, 'OPP': 29, 'D6': 30,
      'ADMG': 31, 'RACE': 32}
C_KEY, C_RES, C_X, C_GOLD, C_VIS, C_REV, C_CNT, C_STAT = 64, 65, 66, 67, 68, 69, 70, 71

def cond(c):
    neg = 0
    if isinstance(c, tuple):
        k = c[0].lstrip('!'); neg = 0x80 if c[0].startswith('!') else 0
        if k == 'vis': return [C_VIS | neg] + w16(c[1])
        if k == 'gold': return [C_GOLD | neg] + w16(c[1])
        if k == 'cnt': return [C_CNT | neg, c[1], c[2]]
        if k == 'stat': return [C_STAT | neg, c[1], c[2]]
        raise ValueError(c)
    if c.startswith('!'):
        neg, c = 0x80, c[1:]
    v = {'key': C_KEY, 'res': C_RES, 'x': C_X, 'rev': C_REV}.get(c)
    if v is None: v = ITEM_ID[c]
    return [v | neg]

def w16(v): return [v & 255, v >> 8]

def compile_ops(ops, enc_str):
    """enc_str(s) -> font-index bájtok (0-val lezárva)"""
    out = []
    for o in ops:
        k = o[0]; out.append(OP[k])
        if k == 'STAT':   out += [o[1], o[2] & 255]
        elif k == 'GOLD': out += w16(o[1] & 0xFFFF)
        elif k == 'CNT':  out += [o[1], o[2] & 255]
        elif k == 'OPP':  out += [o[1], o[2] & 255]
        elif k == 'D6':   out += [o[1]]
        elif k == 'ADMG': out += [o[1], o[2]]
        elif k == 'RACE': out += [o[1]]
        elif k in ('GAIN', 'LOSE'): out += [ITEM_ID[o[1]]]
        elif k == 'GATE': out += w16(o[1]) + cond(o[2])
        elif k in ('PICK', 'PICKX'): out += w16(o[1]) + w16(o[2])
        elif k in ('ONLY', 'ADD', 'HIDE'): out += w16(o[1])
        elif k == 'DMG':  out += [o[1], o[2]]
        elif k == 'LOSEITEMS': out += [o[1]]
        elif k == 'SWARM': out += [o[1]]
        elif k == 'XSET': out += [o[1], o[2]]
        elif k == 'XSUB': out += [o[1]]
        elif k == 'SHOP':
            out += [len(o[1])]
            for it, price in o[1]: out += [ITEM_ID[it], price]
        elif k == 'IF':
            th = compile_ops(o[2], enc_str); el = compile_ops(o[3], enc_str)
            if el:
                th = th + [OP['SKIP'], len(el)]
            out += cond(o[1]) + [len(th)] + th + el
        elif k == 'ONCHOOSE':
            # a menüpont felirata: 0 = Harc, 1 = Próba; a törzs PICK/ONLY-ja felülírhatja a célt
            body = compile_ops(o[2], enc_str) + [0]
            out += w16(o[1]) + [o[3] if len(o) > 3 else 0, len(body)] + body
        elif k == 'FIGHT':
            mons, kw = o[1], o[2]
            flags = 0; extra = []
            if kw.get('all'): flags |= 1
            if kw.get('lb'): flags |= 2
            if kw.get('mdbl'): flags |= 4
            if 'hitlim' in kw: flags |= 8
            if 'pdmg' in kw or 'mdmg' in kw: flags |= 16
            if 'skmod' in kw: flags |= 32
            if 'ev' in kw: flags |= 64
            if 'ext' in kw: flags |= 128
            out += [len(mons), flags]
            if flags & 8: out += [kw['hitlim']]
            if flags & 16: out += [kw.get('pdmg', 2), kw.get('mdmg', 2)]
            if flags & 32: out += [kw['skmod'] & 255]
            if flags & 64: out += list(kw['ev'])
            if flags & 128: out += [kw['ext']]
            for name, sk, sta in mons:
                out += [sk, sta] + enc_str(name)
        assert all(0 <= b < 256 for b in out), (o, out)
    return out

def script(n, enc_str):
    """a fejezet bájtkódja (műveletek + 0), vagy None.
    Ismételt látogatáskor a nyereség (pozitív STAT/GOLD, GAIN) nem ismétlődik, a veszteség igen."""
    ops = R.get(n)
    if not ops: return None
    return compile_ops(ops, enc_str) + [0]

if __name__ == '__main__':
    import json, os
    here = os.path.dirname(os.path.abspath(__file__))
    doc = json.load(open(os.path.join(here, 'konyv', 'orszagut.json'), encoding='utf-8'))
    secs = {s['id']: s for s in doc['sections']}
    tot = 0
    for n, ops in sorted(R.items()):
        b = script(n, lambda s: [1] * len(s) + [0])
        tot += len(b)
        # minden ONLY/PICK/GATE cél szerepel-e a fejezet célpontjai között
        def targets(l):
            for o in l:
                if o[0] in ('ONLY', 'GATE', 'HIDE'): yield o[1]
                if o[0] in ('PICK', 'PICKX'): yield o[1]; yield o[2]
                if o[0] == 'IF': yield from targets(o[2]); yield from targets(o[3])
                if o[0] == 'ONCHOOSE': yield o[1]; yield from targets(o[2])
        bad = [t for t in targets(ops) if t not in secs[n]['jumps'] and t != n]
        if bad: print('HIBA', n, bad, secs[n]['jumps'])
    fights = sum(1 for o in R.values() for x in o if x[0] == 'FIGHT' or (x[0] == 'IF' and any(y[0] == 'FIGHT' for y in x[3])) or (x[0] == 'ONCHOOSE'))
    print(len(R), 'fejezet szabállyal,', tot, 'bájt;', 'harc:', fights)
    mons_json = {s['id'] for s in doc['sections'] if s.get('monsters')}
    have = {n for n, o in R.items() if any(x[0] in ('FIGHT', 'ONCHOOSE') or (x[0] == 'IF' and any(y[0] == 'FIGHT' for y in x[3])) for x in o)}
    print('hiányzó harc:', sorted(mons_json - have), 'extra:', sorted(have - mons_json))
