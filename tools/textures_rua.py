"""Texturas 3D de placas, cartazes e letreiros da rua (obras, lojas, lixo, estacao, fazenda)."""

DK = (18, 18, 18)
R195 = lambda r, g, b, a: r < 195

SPECS = {
    # cartaz de obras "kouji-chuu" com colunas "gomeiwaku wo / okake shite imasu" dos lados do operario
    ("BG_CS.BPM", r"BG_CS\GIM\BGCS_KOUJICHU.GIM"): {
        "erase": [((2, 0, 126, 33), R195), ((4, 30, 34, 128), R195), ((90, 36, 126, 124), R195)], "fill": None,
        "texts": [{"lines": ["EM OBRAS"], "box": (8, 3, 120, 29), "color": DK},
                  {"lines": ["DESCULPE O"], "box": (8, 32, 30, 127), "color": DK, "vertical": True, "outline": DK},
                  {"lines": ["INCÔMODO"], "box": (94, 36, 122, 122), "color": DK, "vertical": True, "outline": DK}]},
    # mesmo cartaz em tamanho menor (poster do quarto)
    ("BG_ROOM.BPM", r"POSTER4\GIM\BGCS_KOUJICHU.GIM"): {
        "erase": [((1, 0, 63, 16), R195), ((1, 15, 17, 64), R195), ((45, 18, 64, 62), R195)], "fill": None,
        "texts": [{"lines": ["EM OBRAS"], "box": (4, 1, 60, 14), "color": DK},
                  {"lines": ["DESCULPE"], "box": (3, 15, 16, 62), "color": DK, "vertical": True, "outline": DK},
                  {"lines": ["INCÔMODO"], "box": (46, 18, 62, 61), "color": DK, "vertical": True, "outline": DK}]},
    # "anzen daiichi"
    ("BG_CS.BPM", r"BG_CS\GIM\BGTF_ANZEN.GIM"): {
        "erase": [((0, 0, 64, 64), lambda r, g, b, a: max(r, g, b) < 175)], "fill": None,
        "texts": [{"lines": ["SEGURANÇA", "PRIMEIRO"], "box": (2, 14, 62, 50), "color": (40, 36, 34)}]},
    # "Kamo semento" (cimento Pato); as faixas azuis ficam
    ("BG_CS.BPM", r"BG_CS\GIM\BGCS_CEMENT.GIM"): {
        "erase": [((4, 23, 63, 41), lambda r, g, b, a: max(r, g, b) < 140)], "fill": None,
        "texts": [{"lines": ["CIMENTO", "PATO"], "box": (6, 23, 62, 41), "color": (45, 40, 38)}]},
    # "shoukaki" em branco sobre vermelho, letras empilhadas
    ("BG_CV.BPM", r"BG_CV\GIM\BGCV_FIRE1.GIM"): {
        "erase": [((0, 8, 32, 62), lambda r, g, b, a: g > 100)], "fill": None,
        "texts": [{"lines": ["EXTINTOR"], "box": (8, 8, 30, 60), "color": (245, 245, 245), "vertical": True}]},
    # "honjitsu tokubai"
    ("BG_CV.BPM", r"BG_CV\GIM\BGCV_TOKUBAI.GIM"): {
        "erase": [((0, 0, 32, 64), lambda r, g, b, a: g > 125)], "fill": None,
        "texts": [{"lines": ["OFERTA", "DO", "DIA"], "box": (1, 4, 31, 60), "color": (252, 252, 252)}]},
    # "Chuuou jidousha gakkou" na placa do poste (a faixa azul de baixo, com o endereco, fica)
    ("BG_CV.BPM", r"BG_CV\GIM\BGSD_DENCHU2.GIM"): {
        "erase": [((0, 0, 32, 53), lambda r, g, b, a: r < 190)], "fill": None,
        "texts": [{"lines": ["AUTOESCOLA"], "box": (3, 1, 29, 53), "color": (85, 110, 135), "vertical": True}]},
    # "yuusenseki"
    ("BG_EL.BPM", r"BG_EL\GIM\BGEL_YUSEN.GIM"): {
        "erase": [((32, 0, 96, 32), lambda r, g, b, a: r > 135)], "fill": None,
        "texts": [{"lines": ["ASSENTO", "PREFERENCIAL"], "box": (33, 2, 95, 30), "color": (235, 235, 235)}]},
    # "funen gomi" e "kanen gomi"
    ("BG_KT.BPM", r"BG_KT\GIM\BGKT_FUNEN.GIM"): {
        "erase": [((4, 0, 28, 32), lambda r, g, b, a: max(r, g, b) < 150)], "fill": None,
        "texts": [{"lines": ["LIXO", "NÃO", "QUEIMA"], "box": (3, 2, 29, 30), "color": (45, 45, 45)}]},
    ("BG_KT.BPM", r"BG_KT\GIM\BGKT_KANEN.GIM"): {
        "erase": [((4, 0, 28, 32), lambda r, g, b, a: max(r, g, b) < 150)], "fill": None,
        "texts": [{"lines": ["LIXO", "QUEIMA"], "box": (3, 4, 29, 28), "color": (45, 45, 45)}]},
    # "shibutsu ni wa namae wo kakimashou" (era vertical): em portugues vai na horizontal
    ("BG_KT.BPM", r"BG_KT\GIM\BGKT_REIZOUKOHARIGAMI.GIM"): {
        "erase": [((20, 0, 64, 64), lambda r, g, b, a: max(r, g, b) < 150)], "fill": None,
        "texts": [{"lines": ["PONHA", "SEU NOME", "NAS SUAS", "COISAS"], "box": (4, 4, 60, 60), "color": (45, 45, 45)}]},
    # "shizen nouhou / yuuki saibai", tinta azulada
    ("BG_FM.BPM", r"BG_FM\GIM\BGFM_KANBAN1A.GIM"): {
        "erase": [((0, 0, 64, 32), lambda r, g, b, a: b - r > 8)], "fill": None,
        "texts": [{"lines": ["AGRICULTURA", "NATURAL", "ORGÂNICO"], "box": (2, 2, 62, 31), "color": (90, 90, 200)}]},
    # "Bisaido" (BeXide) no cartaozinho da porta
    ("BG_KT.BPM", r"BG_KT\GIM\BGKT_DOORR.GIM"): {
        "erase": [((20, 33, 44, 44), lambda r, g, b, a: max(r, g, b) < 150)], "fill": None,
        "texts": [{"lines": ["BEXIDE"], "box": (21, 34, 43, 43), "color": (50, 50, 50)}]},
}
