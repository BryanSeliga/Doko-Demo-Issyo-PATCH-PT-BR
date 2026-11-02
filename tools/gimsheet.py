"""Gera paineis PNG com as imagens GIM de interface para identificar as que contem texto."""
import re
import sys

from PIL import Image, ImageDraw

from gim import to_rgba
from iso_common import Iso, bpm_files, inner_files

SKIP = re.compile(r"KADO|LINE|SQARE|SQUARE|CIRCLE|HOLE|WAKU|ARROW|YAJ|EDGE|DECO|BLOOD|LIGHT|FRAME|TEXT_BOX|NML_BUTTOM|SYS_BUTTOM|BASE[0-9]|_BASE|MARK_|R[0-9][0-9][.]GIM|I_[A-Z0-9_]+[.]GIM|PIC_|PSP_")


def sheet(iso, bpm_off, out, cols_w=960):
    items = []
    for name, o, s in inner_files(iso, bpm_off):
        if not name.endswith(".GIM") or SKIP.search(name):
            continue
        w, h, rgba, _ = to_rgba(iso.bp(o, s))
        im = Image.frombytes("RGBA", (w, h), rgba)
        if w > 256 or h > 128:
            im.thumbnail((256, 128))
        items.append((name.split("\\")[-1][:-4], im))
    x = y = rowh = 0
    pos = []
    for name, im in items:
        cw = max(im.width, 6 * len(name)) + 8
        if x + cw > cols_w:
            x = 0
            y += rowh + 14
            rowh = 0
        pos.append((x, y))
        x += cw
        rowh = max(rowh, im.height)
    H = y + rowh + 16
    canvas = Image.new("RGB", (cols_w, max(H, 16)), (70, 90, 110))
    d = ImageDraw.Draw(canvas)
    for (name, im), (px, py) in zip(items, pos):
        d.text((px, py), name, fill=(255, 255, 0))
        canvas.paste(im, (px, py + 11), im)
    canvas.save(out)
    return len(items), canvas.size


iso = Iso(sys.argv[1])
b = {n: (o, s) for n, o, s in bpm_files(iso)}
for n in sys.argv[3:]:
    print(n, sheet(iso, b[n][0], f"{sys.argv[2]}/{n[:-4]}.png"))
