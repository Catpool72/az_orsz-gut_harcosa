"""a docs/ képernyőképei (lemezes változat)"""
import os, shutil
from play import Play
p = Play('doc'); p.wait(60); p.shot('cim'); p.key('space', gap=120); p.shot('kalandlap')
p.key('space', gap=120); p.key('space', 2, gap=80)
p.sec(381, 0, 'x'); p.sec(1, 0, 'fejezet1')
p.sec(115, 0, 'x'); p.key('space', gap=100)
for i in range(3): p.key('space', gap=70)
p.shot('autos_csata')
p.sec(49, 0, 'x'); p.key('space', gap=100); p.key('up', gap=100); p.shot('raketa'); p.key('space', gap=100)
p.sec(358, 0, 'x'); p.key('space', gap=250); p.shot('verseny'); p.key('space', gap=100)
p.sec(6, 0, 'x'); p.key('space', gap=100)
for i in range(3): p.key('space', gap=70)
p.shot('tuzharc')
p.run()
for f in sorted(os.listdir('shots')):
    if f.startswith('doc_') and not f.endswith('_x.png'):
        shutil.copy(os.path.join('shots', f), os.path.join('docs', f[4:]))
