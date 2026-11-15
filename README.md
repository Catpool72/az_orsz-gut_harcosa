# Az országút harcosa – kalandkönyv Videoton TV-Computerre

Ian Livingstone *Az országút harcosa* (Freeway Fighter, Fighting Fantasy 13.) című lapozós kalandkönyvének
TVC-átirata Z80 gépi kódban, **A Sárkány szeme** motorjára építve
([Catpool72/sarkany_szeme-tvc](https://github.com/Catpool72/sarkany_szeme-tvc)), autós kiegészítésekkel.

- **Lemezes változat:** a teljes könyv (380 fejezet, 32 rajz, előzmények), 720 KB-os VT-DOS lemezkép
  (TVC 64K/64K+ + HBF). Indítás: `LOAD "KALAND"` (önindító). Mentés/visszatöltés a Kalandlapon (Fel/Le).
- **Címlap:** indításkor fekete-fehér, teljes képernyős plakát a játék 2 színű módjában (`cimlap/cimlap.png`,
  512×240 raszterrel, az alcím a játék fontjával; 3 részben a lemezről: `C01`–`C03.CAS`), Szóköz/Tűz után a
  szöveges címlap. A színes változatok (`cimlap/szines_*.png`) a 16 színű módhoz (`CVMODE=2`) maradtak meg.

> **Szerzői jog:** a könyv szövege és Kevin Bulmer illusztrációi a szerzők és a kiadó tulajdona
> (magyar fordítás: Forray Katalin). **Ebben a tárolóban nincsenek benne**: a `konyv/`, `ill/`, `lemez/`
> és `docs/` mappát a build a saját epub-példányodból készíti el (lásd lent), és a `.gitignore` kizárja.
> A motor, a fordító, a szabálykód, a font és a zene saját munka (Claude, Anthropic).

## Fordítás
Kell: Python 3 (Pillow, NumPy) és [sjasmplus](https://github.com/z00m128/sjasmplus).
```
python3 eszkozok/konyv.py Az_Orszagut_Harcosa.epub      # -> konyv/orszagut.json, konyv/orszagut.txt, ill/, img_sections.json
SJASMPLUS=/út/a/sjasmplus python3 build.py --disk       # -> build_disk/orszagut.dsk (+ build_disk/lemez/*.CAS)
python3 rules.py                                         # a szabályok ellenőrzése (minden cél valódi lapozási cél-e)
```

## A szabályok a TVC-n
- **Kalandlap:** ÜGYESSÉG 1d6+6, ÉLETERŐ 2d6+24, SZERENCSE 1d6+6; az Interceptor TŰZEREJE 1d6+6, PÁNCÉLZATA 2d6+24.
  Indulás: 200 Hitel, 10 gyógyszercsomag, 4 rakéta, 3 doboz vasszög, 2 olajtartály, 0 benzinkanna, 2 pótkerék.
- **Állapotsor:** `Ü 10 É 34 Sz 9 T 7 P 31 H 200`. A menüben mindig ott a **Lap** (Kalandlap: pontok, készletek,
  tárgyak) és, amíg van gyógyszer, a **Gyógy** (+4 ÉLETERŐ, legfeljebb a kezdeti értékig).
- **Harc**, három fajta:
  - *Kézitusa* (2d6+ÜGYESSÉG; a találat 1 vagy 2 pont; az Orgyilkosnál kiütés 6 elvesztett pontnál, 48),
  - *Tűzharc* (2d6+ÜGYESSÉG; a találat 1 kockányi ÉLETERŐ; a Magnummal +1),
  - *Autós Csata* (2d6+TŰZERŐ; a találat 1 kockányi PÁNCÉLZAT; kör előtt **Fel = rakéta**, ami biztosan
    megsemmisíti az ellenfelet – a Blitz-versenyen (63, 294) és a furgonnál (158) nem lehet).
  - Több ellenfél egyszerre lő rád (6, 102, 115, 184, 299), vagy egymás után (120, 284); módosítók
    (sebesülés, fedezék, mozdíthatatlan kocsi: 12, 17, 83, 116, 178, 193, 227, 352, 368); „egynél több találat
    után −1 ÜGYESSÉG”; túlélt körök (63, 294: 4, 158: 3, 291: 1); az Állat elleni ökölharc bokszerrel/anélkül (269).
- **Próbák:** Szerencsepróba (−1 SZERENCSE), dobás a Szerencsédre (77, 82: nem csökken), Ügyességpróba,
  egymás elleni dobás (30, 35, 164, 345), egy kocka (55, 127, 154, 165, 214, 245, 250, 254), kockás sebzés
  ÉLETERŐBEN és PÁNCÉLZATBAN, a Jaguár elleni gyorsulási verseny (358, a tuningolt motorral 210: +1 dobásonként).
- **Feltételes lapozás:** csak azok a célok választhatók, amelyekhez megvan a feltétel – benzinkanna (46, 96,
  118, 225, 272), rakéta, vasszög, olaj, pótkerék, gyógyszer, Hitel (15, 28, 259, 300), tárgyak (bokszer, tömlő,
  feszítővas, drótvágó, golyóálló mellény, tuningolt motor), ÉLETERŐ ≥ 10 (85, 339), ÜGYESSÉG ≥ 6 (40),
  patkányharapás (74, 132). A készletek fogynak (a benzinkannát a tankba öntöd, a pótkereket felteszed…).
- A PÁNCÉLZAT nullára csökkenése is halál. A győzelem a 380-as fejezet.

## Javítások a könyv szövegén (`eszkozok/konyv.py`, JAVITAS)
- 74: kimaradt a patkányharapás ága („…lapozz a 275-re”) – a 132-es fejezet párja alapján pótolva.
- 126, 130, 260, 324: elírások. 282: a könyvben az Oldalkocsis motor TŰZEREJE 2; a 220-as párja alapján 9.

## A motor változásai A Sárkány szemehez képest
`kaland.asm` (változók), `szabaly.asm`, `rules.py`, `build.py`:
- új pontok (TŰZERŐ, PÁNCÉLZAT, 16 bites Hitel), hat számolt készlet (`CNT` művelet, `C_CNT` feltétel),
  pontfeltétel (`C_STAT`), varázsital helyett gyógyszercsomag;
- harcmódok (`fight(HAND|GUN|CAR, …)`): kockás sebzés, rakéta, TŰZERŐ/PÁNCÉLZAT kijelzés, kiütés,
  „több találat: −1 ÜGYESSÉG”, első körös módosító, Magnum;
- új műveletek: `LUCK0`, `OPP` (egymás elleni dobás), `D6`, `ADMG` (páncélsebzés), `RACE` (verseny).
- Egyszerűsítés: ha többen lőnek rád egyszerre, mindig az első élő ellenfelet támadod.

## Teszt
```
gcc -O2 -I<z80-mappa> -o harness/tvcsim harness/tvcsim.c <z80-mappa>/z80.c     # superzazu/z80
CAS=build_disk/lemez/KALAND.CAS DISKDIR=build_disk/lemez BUILD=build_disk python3 t_one.py 49 'space,up,space'
CAS=build_disk/lemez/KALAND.CAS DISKDIR=build_disk/lemez BUILD=build_disk python3 fuzz.py 1 2500
```
`t_one.py <fejezet> <billentyűk> [változó=érték…]`: új játék, az előzmények után a fejezetre ugrik, és minden
billentyűcsoport után képet ment (`shots/`). `t_car.py`, `t_misc.py`: autós csata, rakéta, próbák, gyógyszer,
Kalandlap; `fuzz.py`: véletlen billentyűzés (négy kezdőértékkel, egyenként kb. 18 perc játék, hiba nélkül).
Valódi gépen / Ep128web-ben még nincs kipróbálva.
