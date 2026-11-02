"""Caminho automatico do titulo ate a sala do Toro, tirando prints em work/shots/w*.png."""
import ppdbg
from PIL import Image

STEPS = "circle:3 circle:4 square:3 circle:5 circle:2 wait:5 square:2 circle:3 circle:1.5 circle:1.5 circle:1.5 circle:1.5 circle:2 circle:1.5 wait:5 square:2 circle:3 circle:6 wait:10 shot circle:4 shot wait:3 shot wait:3 shot wait:3 shot wait:3 shot".split()
d = ppdbg.Debugger()
import time
n = 0
files = []
for s in STEPS:
    name, _, arg = s.partition(":")
    if name == "shot":
        p = f"../work/shots/w{n}.png"
        d.shot(p)
        files.append(p)
        n += 1
    elif name == "wait":
        time.sleep(float(arg))
    else:
        d.press(name)
        time.sleep(float(arg or 0.5))
ims = [Image.open(f) for f in files]
w, h = ims[0].size
cols = 4
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w // 2, rows * h // 2))
for i, m in enumerate(ims):
    sheet.paste(m.resize((w // 2, h // 2)), ((i % cols) * w // 2, (i // cols) * h // 2))
sheet.save("../work/shots/walk.png")
print(sheet.size)
