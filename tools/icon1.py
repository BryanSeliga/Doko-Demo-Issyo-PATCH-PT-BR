"""Videos de icone (ICON1.PMF) com o logotipo e a legenda em portugues.

Ha dois: o do disco (PSP_GAME/ICON1.PMF, no menu do PSP) e o do save (DATA.BPM, ICON/ICON1.PMF, copiado para
cada save). Os dois sao PSMF com H.264 Main 144x80, 300 quadros a 29,97, e mostram as mesmas cenas, montadas de
outro jeito. O original e decodificado com o ffmpeg do pacote imageio-ffmpeg; os quadros com o logotipo japones
viram o logotipo traduzido; a legenda rolante e coberta pela imagem logo acima dela, espelhada e escurecida, com o
texto em portugues por cima. O resultado e codificado com os parametros do original e montado de novo no mesmo
formato de pacotes (ver docs/FORMATOS.md).
"""
import io
import os
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from xmb import icon0, title_logo

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "fonts", "MPLUSRounded1c-ExtraBold.ttf")
W, H = 144, 80
TICKER = "A qualquer hora, em qualquer lugar. Que tal conversar com um Pokepi?"
# linha de cima da legenda japonesa (a mesma nos dois videos) e da linha do copyright no video do save
BAND_TOP = 52
COPYRIGHT_TOP = 62
PACK = 2048
FRAME_TICKS = 3003  # 90 kHz por quadro a 29,97

# Quadros de cada video. intro: ate onde vai o logotipo e quando termina a transicao para as cenas;
# ticker: quando a legenda japonesa entra pela direita e sai pela esquerda; outro: inicio do logotipo final.
DISC = {"intro": (27, 41), "ticker": (48, 286), "outro": 284, "card": False}
# no save, o logotipo e o copyright aparecem sobre o Toro desfocado do quadro 8 ao 72; nao ha logotipo no fim
SAVE = {"intro": (68, 80), "ticker": (82, 296), "outro": None, "card": True, "clean": 6, "copyright": 40}


def ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


# --- leitura do PSMF -------------------------------------------------------------------------------------

def demux(pmf):
    """Video H.264 (payload dos PES 0xE0) e indices de GOP (stream 0xBF): (cabecalho, numero de quadros)."""
    es = bytearray()
    gops = []
    for pos in range(0x800, len(pmf), PACK):
        p = pmf[pos:pos + PACK]
        if p[:4] != b"\x00\x00\x01\xba":
            break
        i = 14 + (p[13] & 7)
        while i + 6 <= len(p) and p[i:i + 3] == b"\x00\x00\x01":
            sid, ln = p[i + 3], int.from_bytes(p[i + 4:i + 6], "big")
            body = p[i + 6:i + 6 + ln]
            if sid == 0xE0:
                es += body[3 + body[2]:]
            elif sid == 0xBF:
                gops.append((body[:16], int.from_bytes(body[16:18], "big")))
            i += 6 + ln
    return bytes(es), gops


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


def text_layer(text, size, stroke):
    font = ImageFont.truetype(FONT, size)
    left, top, right, bottom = font.getbbox(text, stroke_width=stroke)
    im = Image.new("RGBA", (right - left + 4, bottom - top + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - left, 2 - top), text, font=font, fill=(255, 255, 255),
                            stroke_width=stroke, stroke_fill=(40, 28, 20))
    return im


def card(background, copyright_frame):
    """Logotipo sobre o Toro desfocado, como no video do save; a linha do copyright (em letras latinas) vem do
    quadro original, com uma passagem suave entre as duas imagens."""
    out = background.filter(ImageFilter.GaussianBlur(2.5))
    mask = Image.new("L", (W, H), 0)
    for y in range(COPYRIGHT_TOP, H):
        mask.paste(min(255, (y - COPYRIGHT_TOP) * 64), (0, y, W, y + 1))
    out = Image.composite(copyright_frame, out, mask).convert("RGBA")
    logo = title_logo(132, 28)
    out.alpha_composite(logo, ((W - logo.width) // 2, 22))
    return out.convert("RGB")


def compose(frames, layout, icon):
    first, last = layout["ticker"]
    intro_end, intro_fade = layout["intro"]
    text = text_layer(TICKER, 14, 2)
    y = BAND_TOP + (H - BAND_TOP - text.height) // 2 + 1
    if layout["card"]:
        clean = layout["clean"]
        logo = card(frames[clean], frames[layout["copyright"]])
    else:
        clean, logo = -1, icon
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
        if f <= clean:
            pass  # Toro sem logotipo, antes de o logotipo aparecer
        elif f < clean + 6:
            frame = Image.blend(frames[clean], logo, (f - clean) / 6)
        elif f <= intro_end:
            frame = logo
        elif f < intro_fade:
            a = (f - intro_end) / (intro_fade - intro_end)
            frame = Image.blend(logo.filter(ImageFilter.GaussianBlur(4 * a)), frames[intro_fade], a)
        elif layout["outro"] is not None and f >= layout["outro"]:
            a = (f - layout["outro"]) / (len(frames) - 1 - layout["outro"])
            frame = Image.blend(out[layout["outro"] - 1], icon, a)
        out.append(frame)
    return out


# --- codificacao -------------------------------------------------------------------------------------------

def encode(exe, frames, kbps, keyframes):
    """H.264 como o original: Main 2.1, CABAC, sem quadros B, 1 referencia, IDR nos mesmos quadros, AUD e SEI."""
    params = ("keyint=30:min-keyint=1:scenecut=0:bframes=0:ref=1:weightp=0:aud=1:nal-hrd=vbr:pic-struct=1:"
              "force-cfr=1:vbv-maxrate=600:vbv-bufsize=600:threads=1")  # uma thread: o mesmo resultado sempre
    force = "expr:" + "+".join(f"eq(n,{k})" for k in keyframes)
    raw = b"".join(f.tobytes() for f in frames)
    es = subprocess.run([exe, "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                         "-r", "30000/1001", "-i", "pipe:0", "-vf", "setsar=1", "-c:v", "libx264", "-profile:v", "main",
                         "-level", "2.1", "-pix_fmt", "yuv420p", "-b:v", f"{kbps}k", "-force_key_frames", force,
                         "-x264-params", params, "-f", "h264", "pipe:1"],
                        input=raw, capture_output=True, check=True).stdout
    return strip_x264_info(es)


def strip_x264_info(es):
    """Tira o SEI com a versao do x264 (user_data_unregistered), que o original nao tem."""
    out = bytearray()
    i = 0
    while True:
        j = es.find(b"\x00\x00\x01", i + 3)
        end = len(es) if j < 0 else (j - 1 if es[j - 1] == 0 else j)
        nal = es[i:end]
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


def padding_pack(scr):
    pack = pack_header(scr)
    return pack + b"\x00\x00\x01\xbe" + (PACK - len(pack) - 6).to_bytes(2, "big") + b"\xff" * (PACK - len(pack) - 6)


def mux(original, es, size=None):
    """PSMF com o cabecalho e os indices de GOP do original e o video novo, em pacotes de 2048 bytes.
    Com size, completa com pacotes de enchimento ate esse tamanho."""
    head = bytearray(original[:0x800])
    sys_header = original[0x800 + 14:0x800 + 14 + 18]
    _, gops = demux(original)
    aus = access_units(es)
    assert len(aus) == sum(n for _, n in gops), (len(aus), [n for _, n in gops])
    start_pts = int.from_bytes(original[0x54:0x5A], "big")
    out = bytearray()
    scr = 10147
    first_frame = 0
    for gop_head, n in gops:
        gop = aus[first_frame:first_frame + n]
        data = b"".join(gop)
        # posicao de inicio de cada quadro dentro do GOP, para PTS/DTS dos PES
        starts, pos = [], 0
        for au in gop:
            starts.append(pos)
            pos += len(au)
        index = b"\x00\x00\x01\xbf" + (16 + 2 + 4 * n).to_bytes(2, "big") + gop_head + n.to_bytes(2, "big") \
            + b"".join(b"\x00\x80" + len(au).to_bytes(2, "big") for au in gop)
        pos = 0
        first = True
        while pos < len(data):
            # relogio do pacote: um pouco antes do DTS do quadro que ele comeca, como no original
            at = max(k for k, s in enumerate(starts) if s <= pos)
            dts_first = start_pts - FRAME_TICKS + (first_frame + at) * FRAME_TICKS
            if out:
                scr = max(scr + 148, dts_first - 75000)
            pack = bytearray(pack_header(scr))
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
                dts = start_pts - FRAME_TICKS + (first_frame + k) * FRAME_TICKS
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
        first_frame += n
    while size is not None and 0x800 + len(out) < size:
        scr += 148
        out += padding_pack(scr)
    head[0x0C:0x10] = len(out).to_bytes(4, "big")
    return bytes(head) + bytes(out)


def build(original, layout=DISC, exact=False, kbps=110):
    """PMF traduzido, ou None sem o ffmpeg. Baixa a taxa ate caber no tamanho do original; com exact, completa
    com pacotes de enchimento ate ficar do mesmo tamanho (arquivo gravado no lugar dentro de um BPM)."""
    exe = ffmpeg()
    if exe is None:
        return None
    es, gops = demux(original)
    frames = decode(exe, es)
    keyframes, k = [], 0
    for _, n in gops:
        keyframes.append(k)
        k += n
    assert len(frames) == k, (len(frames), k)
    icon = Image.open(io.BytesIO(icon0())).convert("RGB")
    frames = compose(frames, layout, icon)
    while True:
        pmf = mux(original, encode(exe, frames, kbps, keyframes), len(original) if exact else None)
        if len(pmf) <= len(original):
            return pmf
        kbps -= 10
