import sys
from play import Play
n = int(sys.argv[1]); keys = sys.argv[2] if len(sys.argv) > 2 else ''
p = Play(f'one{n}'); p.start()
for k, v in [x.split('=') for x in sys.argv[3:]]:
    p.poke(k, *[int(t) for t in v.split(',')])
p.sec(n, 0, 's')
for i, k in enumerate(keys.split(',') if keys else []):
    k, _, c = k.partition('*')
    p.key(k, int(c or 1), gap=70)
    p.shot(f'k{i}')
p.run()
