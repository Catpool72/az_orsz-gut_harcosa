import sys, glob
from PIL import Image
pat, out = sys.argv[1], sys.argv[2]
fs = sorted(glob.glob(pat))
ims = [Image.open(f).crop((240, 0, 512, 480)) for f in fs]; w, h = ims[0].size
cols = 4
sh = Image.new('RGB', (w * cols, h * ((len(ims) + cols - 1) // cols)), 'gray')
for i, im in enumerate(ims): sh.paste(im, ((i % cols) * w, (i // cols) * h))
sh.save(out); print(len(ims), [f.split('_', 2)[-1] for f in fs])
