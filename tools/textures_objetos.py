"""Texturas 3D com japones dos objetos (enfeites e cartazes do quarto, objetos da escola e do escritorio)."""

BLUE = lambda r, g, b, a: b - max(r, g) > 10
YELLOW = lambda r, g, b, a: r > 200 and g > 180 and b < 170 and r - b > 60


def _paper(name):
    # caligrafia de paz mundial, tracos escuros sobre papel bege; as variantes mudam so a posicao
    return (("BG_CL.BPM", "BG_CL\\GIM\\" + name + ".GIM"), {
        "erase": [((0, 0, 32, 32), ("dark", 198))], "fill": None,
        "texts": [{"lines": ["PAZ", "MUNDIAL"], "box": (2, 4, 30, 28), "color": (70, 64, 60)}]})


_DAYS = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB"]

SPECS = dict([_paper(n) for n in ("BGCL_PAPER2", "BG_SCHOOLPAPER2", "BG_SCHOOLPAPER3", "BG_SCHOOLPAPER3A",
                                  "BG_SCHOOLPAPER3B")])
SPECS.update({
    # quadro de horarios da escola: titulo e dias em azul/vermelho, materias em cinza (apagadas), numeros das aulas
    ("BG_CL.BPM", "BG_CL\\GIM\\BGCL_TIMETABLE.GIM"): {
        "erase": [((28, 0, 70, 7), BLUE), ((6, 16, 18, 61), BLUE), ((18, 8, 90, 15), ("redder", 25))]
                 + [((x, y0, x + 11, y1), ("all",)) for x in range(19, 90, 12)
                    for y0, y1 in ((16, 22), (24, 30), (32, 38), (40, 46), (48, 54), (56, 60))],
        "fill": (212, 209, 207),
        "texts": [{"lines": ["HORÁRIO"], "box": (30, 0, 68, 7), "color": (90, 80, 190)}]
                 + [{"lines": [d], "box": (19 + 12 * i, 9, 30 + 12 * i, 14), "color": (185, 74, 86)}
                    for i, d in enumerate(_DAYS)]
                 + [{"lines": [str(k + 1)], "box": (9, y, 16, y + 4), "color": (104, 91, 199)}
                    for k, y in enumerate((17, 25, 33, 41, 49, 57))]},
    # livro "daigaku juken" (vestibular): capa creme, titulo cinza escuro; o carimbo rosa fica
    ("BG_CL.BPM", "BG_CL\\GIM\\BGCL_BOOK1.GIM"): {
        "erase": [((0, 0, 32, 24), lambda r, g, b, a: max(r, g, b) < 200 and abs(r - g) < 30)], "fill": None,
        "texts": [{"lines": ["VESTI", "BULAR"], "box": (1, 2, 31, 22), "color": (78, 75, 72)}]},
    # diploma "hyoushoujou": titulo e corpo viram "CERTIFICADO" e tracinhos
    ("BG_CL.BPM", "BG_CL\\GIM\\BGCL_SYOUJYOU.GIM"): {
        "erase": [((12, 18, 52, 44), ("dark", 190))], "fill": None,
        "texts": [{"lines": ["CERTI", "FICADO"], "box": (14, 20, 51, 33), "color": (82, 58, 45)},
                  {"lines": ["- - - - - -", "- - - - - -"], "box": (16, 35, 49, 42), "color": (130, 100, 80)}]},
    # grafico de notas: titulo escuro no alto, rotulos vermelhos na esquerda e rotulos escuros embaixo
    ("BG_OF.BPM", "BG_OF\\GIM\\PBG_OFGRAPH1.GIM"): {
        "erase": [((6, 1, 63, 9), ("dark", 170)), ((0, 8, 8, 58), ("dark", 170)), ((12, 58, 63, 63), ("dark", 200))],
        "fill": None,
        "texts": [{"lines": ["RESULTADOS"], "box": (8, 1, 60, 8), "color": (60, 60, 60)}]},
    # galhardete "Himeji-jou"
    ("BG_ROOM.BPM", "PENNANT\\GIM\\BG_POSTER06.GIM"): {
        "erase": [((3, 5, 33, 26), lambda r, g, b, a: r - max(g, b) > 40 or max(r, g, b) < 140)], "fill": (135, 180, 214),
        "texts": [{"lines": ["CASTELO", "DE", "HIMEJI"], "box": (4, 6, 33, 26), "color": (50, 70, 80)}]},
    # placa de cafe: COFFEE (latino) fica, "jazu" verde escuro sobre branco
    ("BG_ROOM.BPM", "CAFEKANBAN\\GIM\\AC_COFFEEPLATE.GIM"): {
        "erase": [((7, 18, 60, 45), ("dark", 170))], "fill": None,
        "texts": [{"lines": ["JAZZ"], "box": (8, 22, 58, 44), "color": (40, 100, 70)}]},
    # cartaz "gozonji desu ka?"
    ("BG_ROOM.BPM", "POSTER2\\GIM\\BG_POSTER02.GIM"): {
        "erase": [((4, 1, 60, 10), ("dark", 175))], "fill": None,
        "texts": [{"lines": ["VOCÊ SABIA?"], "box": (4, 2, 60, 9), "color": (90, 110, 110)}]},
    # cartaz com titulo "...itawari gekkan"
    ("BG_ROOM.BPM", "POSTER1\\GIM\\BG_POSTER01.GIM"): {
        "erase": [((3, 2, 60, 11), ("dark", 200))], "fill": None,
        "texts": [{"lines": ["MÊS DO CUIDADO"], "box": (4, 3, 59, 10), "color": (120, 115, 70)}]},
    # placa de teatro "shibai-dou", em coluna, claro sobre verde
    ("BG_ROOM.BPM", "NEON1\\GIM\\SIBAIKANNBANN_TATE01.GIM"): {
        "erase": [((6, 3, 28, 61), ("light", 110))], "fill": None,
        "texts": [{"lines": ["TEATRO"], "box": (9, 5, 25, 59), "color": (225, 235, 225), "vertical": True}]},
    # livro "keizai nyuumon", marrom sobre faixa cinza
    ("BG_ROOM.BPM", "BOOKS\\GIM\\BOOK11.GIM"): {
        "erase": [((8, 2, 32, 10), ("all",))], "fill": (192, 192, 192),
        "texts": [{"lines": ["ECON."], "box": (9, 3, 31, 10), "color": (150, 100, 60)}]},
    # bandeirola "mainichi daihoushutsu", duas colunas vermelho escuro
    ("BG_ROOM.BPM", "NOBORI1\\GIM\\NOBORI3_02.GIM"): {
        "erase": [((17, 0, 32, 33), lambda r, g, b, a: r - g > 12 and r < 200),
                  ((17, 33, 28, 38), lambda r, g, b, a: r - g > 30 and r > 100),
                  ((0, 0, 16, 60), lambda r, g, b, a: r - g > 12 and r < 200)], "fill": None,
        "texts": [{"lines": ["TODO DIA"], "box": (19, 2, 31, 33), "color": (128, 58, 57), "turned": 90},
                  {"lines": ["LIQUIDAÇÃO"], "box": (2, 2, 15, 61), "color": (128, 58, 57), "turned": 90}]},
    # bandeirola "honjitsu saabisu dee", claro sobre roxo
    ("BG_ROOM.BPM", "NOBORI2\\GIM\\NOBORI1_02.GIM"): {
        "erase": [((14, 0, 32, 24), ("light", 140)), ((0, 0, 13, 64), ("light", 140))], "fill": None,
        "texts": [{"lines": ["HOJE"], "box": (16, 1, 30, 24), "color": (209, 209, 200), "turned": 90},
                  {"lines": ["PROMOÇÃO"], "box": (1, 1, 13, 63), "color": (209, 209, 200), "turned": 90}]},
    # bandeirola do hamburguer, amarelo sobre laranja
    ("BG_ROOM.BPM", "NOBORI3\\GIM\\NOBORI.GIM"): {
        "erase": [((18, 18, 32, 64), YELLOW), ((3, 50, 18, 64), YELLOW)], "fill": None,
        "texts": [{"lines": ["HAMBÚRGUER"], "box": (21, 18, 31, 62), "color": (255, 240, 110), "turned": 90},
                  {"lines": ["100"], "box": (3, 53, 17, 63), "color": (255, 240, 110)}]},
    # "ikiryou" vermelho escuro em coluna
    ("BG_ROOM.BPM", "POSTER5\\GIM\\KABE_B06.GIM"): {
        "erase": [((3, 3, 24, 60), lambda r, g, b, a: g < 60)], "fill": None,
        "texts": [{"lines": ["ESPÍRITO"], "box": (5, 5, 22, 58), "color": (140, 0, 0), "turned": 90}]},
    # "matsuri" grande, branco com contorno sobre vermelho escuro (happi)
    ("BG_ROOM.BPM", "HAPPI\\GIM\\KABE_U05.GIM"): {
        "erase": [((20, 5, 50, 31), lambda r, g, b, a: g > 35 or r < 100)], "fill": None,
        "texts": [{"lines": ["FESTA"], "box": (18, 8, 52, 28), "color": (250, 250, 250), "outline": (0, 0, 0)}]},
    # placa dourada dos premios
    ("BG_ROOM.BPM", "SHIRITORI01\\GIM\\S01_PLATE.GIM"): {
        "erase": [((1, 2, 31, 14), lambda r, g, b, a: r < 195)], "fill": None,
        "texts": [{"lines": ["PRÊMIO"], "box": (2, 3, 30, 13), "color": (110, 70, 30)}]},
    # capa de disco: titulo vermelho e letrinhas marrons na faixa amarela do alto
    ("BG_ROOM.BPM", "LPRECORD2\\GIM\\KABE_O07_1.GIM"): {
        "erase": [((1, 1, 31, 12), lambda r, g, b, a: r - g > 25 or g < 160)], "fill": None,
        "texts": [{"lines": ["A MÚSICA"], "box": (1, 1, 31, 10), "color": (170, 30, 20)}]},
})
