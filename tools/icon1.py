"""ICON1.PMF: video do icone no menu do PSP, com o logotipo e a legenda em portugues.

O original (PSMF, H.264 Main 144x80, 300 quadros a 29,97) e decodificado com o ffmpeg do pacote imageio-ffmpeg.
Os quadros com o logotipo japones viram o ICON0 traduzido; a legenda rolante e coberta pela imagem logo acima
dela, espelhada e escurecida, com o texto em portugues por cima. O resultado e codificado com os parametros do
original e montado de novo no mesmo formato de pacotes (ver docs/FORMATOS.md).
"""
import io
import os
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from xmb import icon0

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "fonts", "MPLUSRounded1c-ExtraBold.ttf")
W, H = 144, 80
FRAMES = 300
TICKER = "A qualquer hora, em qualquer lugar. Que tal conversar com um Pokepi?"
# quadros da legenda japonesa (entra pela direita no 50 e sai no 284) e linhas que ela ocupa
TICKER_FRAMES = (48, 286)
BAND_TOP = 52
# logotipo japones: inicio ate o 27 (some desfocando ate o 40) e fim a partir do 285
INTRO_END, INTRO_FADE = 27, 41
OUTRO_START = 284
PACK = 2048
FRAME_TICKS = 3003  # 90 kHz por quadro a 29,97


def ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


# --- leitura do PSMF -------------------------------------------------------------------------------------

def demux(pmf):
    """Video H.264 (payload dos PES 0xE0) e cabecalhos dos indices de GOP (stream 0xBF)."""
    es = bytearray()
    gop_heads = []
    for pos in range(0x800, len(pmf), PACK):
        p = pmf[pos:pos + PACK]
        i = 14 + (p[13] & 7)
        while i + 6 <= len(p) and p[i:i + 3] == b"\x00\x00\x01":
            sid, ln = p[i + 3], int.from_bytes(p[i + 4:i + 6], "big")
            body = p[i + 6:i + 6 + ln]
            if sid == 0xE0:
                es += body[3 + body[2]:]
            elif sid == 0xBF:
                gop_heads.append(body[:16])
            i += 6 + ln
    return bytes(es), gop_heads


def access_units(es):
    """Quadros do video, cada um comecando no delimitador (NAL 9, codigo de 4 bytes)."""
    starts = []
    i = es.find(b"\x00\x00\x00\x01\x09")
    while i >= 0:
        starts.append(i)
        i = es.find(b"\x00\x00\x00\x01\x09", i + 5)
    return [es[a:b] for a, b in zip(starts, starts[1:] + [len(es)])]


# --- quadros -----------------------------------------------------------------------------------------------

def decode(exe, es):
    raw = subprocess.run([exe, "-v", "error", "-f", "h264", "-i", "pipe:0", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "pipe:1"], input=es, capture_output=True, check=True).stdout
    size = W * H * 3
    return [Image.frombytes("RGB", (W, H), raw[k:k + size]) for k in range(0, len(raw), size)]


def cover_ticker(frame):
    """Esconde a legenda japonesa: a faixa de baixo recebe a imagem de cima dela, espelhada e escurecida."""
    h = H - BAND_TOP
    band = frame.crop((0, BAND_TOP - h, W, BAND_TOP)).transpose(Image.FLIP_TOP_BOTTOM)
    band = band.filter(ImageFilter.GaussianBlur(1.5))
    band = Image.blend(band, Image.new("RGB", band.size, (24, 16, 8)), 0.45)
    out = frame.copy()
    out.paste(band, (0, BAND_TOP))
    return out


def ticker_layer(text):
    font = ImageFont.truetype(FONT, 14)
    left, top, right, bottom = font.getbbox(text, stroke_width=2)
    im = Image.new("RGBA", (right - left + 4, bottom - top + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - left, 2 - top), text, font=font, fill=(255, 255, 255),
                            stroke_width=2, stroke_fill=(40, 28, 20))
    return im


def compose(frames, icon):
    first, last = TICKER_FRAMES
    text = ticker_layer(TICKER)
    y = BAND_TOP + (H - BAND_TOP - text.height) // 2 + 1
    out = []
    for f, frame in enumerate(frames):
        if first <= f < last:
            frame = cover_ticker(frame)
            # da borda direita ate sumir pela esquerda no mesmo intervalo da legenda original
            x = round(W - (W + text.width) * (f - first) / (last - first - 1))
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            if x > -text.width:
                layer.alpha_composite(text, (max(x, 0), y), (max(-x, 0), 0))
            frame = Image.alpha_composite(frame.convert("RGBA"), layer).convert("RGB")
        if f <= INTRO_END:
            frame = icon
        elif f < INTRO_FADE:
            a = (f - INTRO_END) / (INTRO_FADE - INTRO_END)
            frame = Image.blend(icon.filter(ImageFilter.GaussianBlur(4 * a)), frames[INTRO_FADE], a)
        elif f >= OUTRO_START:
            a = (f - OUTRO_START) / (FRAMES - 1 - OUTRO_START)
            frame = Image.blend(out[OUTRO_START - 1], icon, a)
        out.append(frame)
    return out


# --- codificacao -------------------------------------------------------------------------------------------

def encode(exe, frames, kbps):
    """H.264 como o original: Main 2.1, CABAC, sem quadros B, 1 referencia, IDR a cada 30, AUD e SEI de tempo."""
    params = ("keyint=30:min-keyint=30:scenecut=0:bframes=0:ref=1:weightp=0:aud=1:nal-hrd=vbr:pic-struct=1:"
              "force-cfr=1:vbv-maxrate=600:vbv-bufsize=600:threads=1")  # uma thread: o mesmo resultado sempre
    raw = b"".join(f.tobytes() for f in frames)
    es = subprocess.run([exe, "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                         "-r", "30000/1001", "-i", "pipe:0", "-vf", "setsar=1", "-c:v", "libx264", "-profile:v", "main",
                         "-level", "2.1",
                         "-pix_fmt", "yuv420p", "-b:v", f"{kbps}k", "-x264-params", params, "-f", "h264", "pipe:1"],
                        input=raw, capture_output=True, check=True).stdout
    return strip_x264_info(es)


def strip_x264_info(es):
    """Tira o SEI com a versao do x264 (user_data_unregistered), que o original nao tem."""
    out = bytearray()
    i = 0
    while True:
        j = es.find(b"\x00\x00\x01", i + 3)
        start = i
        end = len(es) if j < 0 else (j - 1 if es[j - 1] == 0 else j)
        nal = es[start:end]
        k = nal.find(b"\x00\x00\x01") + 3
        if not (nal[k] & 0x1F == 6 and nal[k + 1] == 5):
            out += nal
        if j < 0:
            return bytes(out)
        i = end


# --- montagem do PSMF -----------------------------------------------------------------------------------

def ts_bytes(prefix, t):
    return bytes([prefix << 4 | (t >> 29 & 0x0E) | 1, t >> 22 & 0xFF, (t >> 14 & 0xFE) | 1, t >> 7 & 0xFF,
                  (t << 1 & 0xFE) | 1])


def pack_header(scr):
    return b"\x00\x00\x01\xba" + bytes([
        0x44 | (scr >> 27 & 0x38) | (scr >> 28 & 3), scr >> 20 & 0xFF, (scr >> 12 & 0xF8) | 4 | (scr >> 13 & 3),
        scr >> 5 & 0xFF, (scr << 3 & 0xF8) | 4, 1]) + b"\x01\x86\xa3\xf8"


def pes(data, header_data, flags):
    head = bytes([0x81, flags, len(header_data)]) + header_data
    return b"\x00\x00\x01\xe0" + (len(head) + len(data)).to_bytes(2, "big") + head + data


def mux(original, es):
    """PSMF com o cabecalho e os indices de GOP do original e o video novo, em pacotes de 2048 bytes."""
    head = bytearray(original[:0x800])
    sys_header = original[0x800 + 14:0x800 + 14 + 18]
    _, gop_heads = demux(original)
    aus = access_units(es)
    assert len(aus) == FRAMES and len(gop_heads) == FRAMES // 30, (len(aus), len(gop_heads))
    start_pts = int.from_bytes(original[0x54:0x5A], "big")
    out = bytearray()
    scr = 10147
    for g in range(FRAMES // 30):
        gop = aus[g * 30:(g + 1) * 30]
        data = b"".join(gop)
        # posicao de inicio de cada quadro dentro do GOP, para PTS/DTS dos PES
        starts, pos = [], 0
        for au in gop:
            starts.append(pos)
            pos += len(au)
        index = b"\x00\x00\x01\xbf" + (16 + 2 + 4 * 30).to_bytes(2, "big") + gop_heads[g] + (30).to_bytes(2, "big") \
            + b"".join(b"\x00\x80" + len(au).to_bytes(2, "big") for au in gop)
        pos = 0
        first = True
        while pos < len(data):
            # relogio do pacote: um pouco antes do DTS do quadro que ele comeca, como no original
            dts_first = start_pts - FRAME_TICKS + (g * 30 + max(k for k, s in enumerate(starts) if s <= pos)) * FRAME_TICKS
            if out:
                scr = max(scr + 148, dts_first - 75000)
            pack = bytearray(pack_header(max(scr, 0)))
            if first:
                pack += sys_header + index
            room = PACK - len(pack) - 9 - (13 if first else 10)
            k = next((k for k, s in enumerate(starts) if pos <= s < pos + room), None)
            if k is None:
                room = PACK - len(pack) - 9
            chunk = data[pos:pos + room]
            if k is None:
                hdr, flags = b"", 0
            else:
                dts = start_pts - FRAME_TICKS + (g * 30 + k) * FRAME_TICKS
                hdr = ts_bytes(3, dts + FRAME_TICKS) + ts_bytes(1, dts)
                flags = 0xC0
                if first:
                    hdr += b"\x1e\x61\xef"  # extensao do PES com o buffer P-STD, como no original
                    flags = 0xC1
            left = PACK - len(pack) - 9 - len(hdr) - len(chunk)
            if 0 < left < 6:
                hdr += b"\xff" * left  # bytes de enchimento no cabecalho do PES
                left = 0
            pack += pes(chunk, hdr, flags)
            if left:
                pack += b"\x00\x00\x01\xbe" + (left - 6).to_bytes(2, "big") + b"\xff" * (left - 6)
            assert len(pack) == PACK, len(pack)
            out += pack
            pos += len(chunk)
            first = False
    head[0x0C:0x10] = len(out).to_bytes(4, "big")
    return bytes(head) + bytes(out)


def build(original, kbps=110):
    """PMF traduzido, ou None se o ffmpeg nao estiver instalado. Baixa a taxa ate caber nos setores do original."""
    max_size = len(original)
    exe = ffmpeg()
    if exe is None:
        return None
    es, _ = demux(original)
    frames = decode(exe, es)
    assert len(frames) == FRAMES, len(frames)
    icon = Image.open(io.BytesIO(icon0())).convert("RGB")
    frames = compose(frames, icon)
    while True:
        pmf = mux(original, encode(exe, frames, kbps))
        if len(pmf) <= max_size:
            return pmf
        kbps -= 10
