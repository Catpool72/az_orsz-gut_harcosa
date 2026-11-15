from play import Play
p = Play('demo'); p.wait(60); p.shot('cim'); p.key('space',gap=120); p.shot('lap'); p.key('space',gap=120); p.shot('e1')
p.key('space',6,gap=80); p.shot('e2'); p.key('space',3,gap=100); p.shot('x')
p.run()
