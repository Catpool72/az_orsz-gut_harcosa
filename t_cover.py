from play import Play
p = Play('cover'); p.wait(30); p.shot('tolt'); p.wait(60); p.shot('cimlap')
p.key('space', gap=100); p.shot('cim'); p.key('space', gap=120); p.shot('lap')
p.run()
