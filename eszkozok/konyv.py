#!/usr/bin/env python3
"""Az országút harcosa – a könyv adatbázisa (konyv/orszagut.json) az epubból.

  python3 eszkozok/konyv.py <Az_Orszagut_Harcosa.epub>

- a fejezetek szövege (a fejezetszám nélkül), a lapozási célok a szöveg sorrendjében
  ("lapozz a N-re"), a fejezet rajza (auhNNN.jpg; a kis díszítő vignetták nem),
- az előzmények: a könyv háttértörténete + a TVC-változat szabályainak rövid leírása,
- néhány szövegjavítás (JAVITAS), a rajzok kivágása az ill/ mappába (pNNN.png).
"""
import html, json, os, re, sys, zipfile, io
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# szövegjavítások: (fejezet, régi, új)
JAVITAS = [
    # a 74-es fejezetből kimaradt a patkányharapás ága (a 132-es fejezet párja alapján)
    (74, 'Ha megúsztad harapás nélkül, lapozz a 380-ra.',
     'Ha útközben megharapott egy patkány, lapozz a 275-re. Ha megúsztad harapás nélkül, lapozz a 380-ra.'),
    (126, 'alapozz a 274-re', 'lapozz a 274-re'),
    (324, 'közeledik…', 'közeledik...'),
    (130, 'Ha inkább gyorsítasz és úgy próbálsz megmenekülni. Lapozz a 71-re.',
     'Ha inkább gyorsítasz, és úgy próbálsz megmenekülni, lapozz a 71-re.'),
    (260, 'Ügyes sem vet rád', 'Ügyet sem vet rád'),
]

SZABALYOK = (
    'A JÁTÉK SZABÁLYAI A TVC-N. A program mindent kiszámol és feljegyez helyetted. '
    'Kezdéskor kockadobással dől el ÜGYESSÉGED (1 kocka + 6), ÉLETERŐD (2 kocka + 24) és SZERENCSÉD (1 kocka + 6), '
    'az Interceptor TŰZEREJE (1 kocka + 6) és PÁNCÉLZATA (2 kocka + 24). '
    'Indulásodkor 200 Hitel, 10 gyógyszercsomag, 4 rakéta, 3 doboz vasszög, 2 olajtartály és 2 pótkerék van nálad. '
    'Az állapotsor: Ü ÜGYESSÉG, É ÉLETERŐ, Sz SZERENCSE, T TŰZERŐ, P PÁNCÉLZAT, H Hitel. '
    'A menüben a Lap a Kalandlapot mutatja; a Gyógy egy gyógyszercsomagot használ el, és 4 ÉLETERŐT ad vissza. '
    'Harc: Kézitusában és Tűzharcban a 2 kocka + ÜGYESSÉG, Autós Csatában a 2 kocka + TŰZERŐ a Támadóerő. '
    'Tűzharcban a találat 1 kockányi ÉLETERŐT, Autós Csatában 1 kockányi PÁNCÉLZATOT visz el. '
    'Autós Csatában a kör előtt a Fel billentyűvel rakétát lőhetsz ki: ez biztosan elpusztítja az ellenfelet. '
    'Ha ÉLETERŐD vagy a PÁNCÉLZATOD nullára csökken, kalandod véget ér. '
    'A lapozási célok közül csak azok választhatók, amelyekhez megvan a szükséges tárgy, Hitel vagy benzin. '
    'Ha végig akarsz jutni, szerezz benzint: a tartalék kannák nélkül a sivatagban kifogysz az üzemanyagból. '
    'Jó utat, országúti harcos!')

def clean(t):
    t = re.sub(r'<br\s*/?>', ' ', t)
    t = re.sub(r'</(p|div|h\d)>', '\n', t)
    t = re.sub(r'<[^>]+>', '', t)
    return html.unescape(t).replace('\xa0', ' ')

def main(src):
    z = zipfile.ZipFile(src)
    secs = {}
    for name in z.namelist():
        m = re.match(r'OEBPS/Text/(\d+)\.xhtml$', name)
        if not m: continue
        n = int(m.group(1))
        body = z.read(name).decode('utf-8')
        body = body[body.index('<body'):]
        imgs = [i for i in re.findall(r'src="\.\./Images/([^"]+)"', body) if i.startswith('auh')]
        body = re.sub(r'<h3[^>]*>.*?</h3>', '', body, flags=re.S)
        secs[n] = {'id': n, 'text': ' '.join(clean(body).split()), 'img': imgs}
    for n, old, new in JAVITAS:
        assert old in secs[n]['text'], (n, old)
        secs[n]['text'] = secs[n]['text'].replace(old, new)
    for s in secs.values():
        s['text'] = s['text'].replace('…', '...').replace('„', '"').replace('”', '"')
        js = []
        for j in re.findall(r'[Ll]apozz\D{0,20}?(\d+)', s['text']):
            if int(j) not in js: js.append(int(j))
        s['jumps'] = js
    t = z.read('OEBPS/Text/Section0004.xhtml').decode('utf-8')
    hatter = ' '.join(clean(t[t.index('<body'):]).split())
    hatter = hatter.replace('Videóhírek, 2022. Július 21.', 'HÁTTÉRTÖRTÉNET. Videóhírek, 2022. július 21.')
    doc = {
        'meta': {
            'title': 'AZ ORSZÁGÚT HARCOSA', 'win': 380,
            'paper': 15, 'ink': 0, 'fixed_palette': True, 'border': 0xAA, 'text_gap': True,
        },
        'intro_parts': [hatter, SZABALYOK],
        'sections': [secs[n] for n in sorted(secs)],
    }
    os.makedirs(os.path.join(ROOT, 'konyv'), exist_ok=True)
    json.dump(doc, open(os.path.join(ROOT, 'konyv', 'orszagut.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, 'konyv', 'orszagut.txt'), 'w', encoding='utf-8') as f:
        f.write('AZ ORSZÁGÚT HARCOSA\n\nELŐZMÉNYEK\n\n' + hatter + '\n\n' + SZABALYOK + '\n\n')
        for n in sorted(secs):
            f.write(f'{n}.\n{secs[n]["text"]}\n\n')
    # rajzok: a fejezet saját rajza (auhNNN.jpg) -> ill/pNNN.png, img_sections.json: NNN -> fejezet
    ill = os.path.join(ROOT, 'ill'); os.makedirs(ill, exist_ok=True)
    m = {}
    for n in sorted(secs):
        for i in secs[n]['img']:
            k = int(i[3:6])
            m[k] = n
            Image.open(io.BytesIO(z.read('OEBPS/Images/' + i))).convert('L').save(os.path.join(ill, f'p{k}.png'))
    json.dump({str(k): v for k, v in sorted(m.items())}, open(os.path.join(ROOT, 'img_sections.json'), 'w'))
    print(len(secs), 'fejezet,', len(m), 'rajz; leghosszabb:', max(len(s['text']) for s in secs.values()),
          'előzmények:', len(hatter), len(SZABALYOK))

if __name__ == '__main__':
    main(sys.argv[1])
