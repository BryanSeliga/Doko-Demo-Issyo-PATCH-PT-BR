"""Texturas 3D com japones do cenario noturno e dos lugares (bar, loja de bolinhas, banho publico...)."""

# bordas e antialias: as regras pegam o miolo e as bordas suavizadas da tinta
# no papel cinza da inauguracao, tinta e tudo que tem cor ou e mais escuro que o papel
INK = lambda r, g, b, a: max(r, g, b) - min(r, g, b) > 15 or r + g + b < 560

SPECS = {
    # cortina "oden" (letras em coluna, escuro com realce rosado)
    ("BG_NM.BPM", "BG_NM\\GIM\\BGNM_ODEN.GIM"): {
        "erase": [((31, 4, 55, 61), lambda r, g, b, a: max(r, g, b) < 100 or min(r, g, b) > 125)], "fill": None,
        "texts": [{"lines": ["ODEN"], "box": (33, 6, 53, 58), "color": (52, 8, 8), "vertical": True}]},
    # "sunakku Akiko", branco sobre verde
    ("BG_NM.BPM", "BG_NM\\GIM\\BGNM_KANBANA02.GIM"): {
        "erase": [((0, 0, 32, 28), ("light", 95))], "fill": None,
        "texts": [{"lines": ["AKIKO"], "box": (3, 0, 29, 9), "color": (250, 250, 250)},
                  {"lines": ["SNACK"], "box": (2, 10, 30, 26), "color": (250, 250, 250)}]},
    # "akichi" (terreno vazio), escuro sobre amarelo; as duas barras escuras (y 5 e y 23) ficam
    ("BG_NM.BPM", "BG_NM\\GIM\\BGNM_KANBANA03.GIM"): {
        "erase": [((0, 7, 32, 22), lambda r, g, b, a: r < 135)], "fill": None,
        "texts": [{"lines": ["TERRENO"], "box": (1, 8, 31, 22), "color": (40, 40, 36)}]},
    # neon "ki ni suru na": traco escuro com brilho rosa no meio
    ("BG_NM.BPM", "BG_NM\\GIM\\BGNM_KANBANA04.GIM"): {
        "erase": [((0, 2, 32, 28), ("all",))], "fill": None,
        "texts": [{"lines": ["RELAXA"], "box": (1, 5, 31, 21), "color": (62, 26, 96), "outline": (226, 92, 236)}]},
    # "izakaya" em coluna, vermelho escuro sobre cinza
    ("BG_NM.BPM", "BG_NM\\GIM\\BGNM_KANBANB01.GIM"): {
        "erase": [((4, 0, 30, 62), ("redder", 18))], "fill": None,
        "texts": [{"lines": ["BOTECO"], "box": (8, 3, 25, 58), "color": (112, 36, 42), "vertical": True}]},
    # "pabu Kamo", branco sobre azul
    ("BG_NM.BPM", "BG_NM\\GIM\\BGNM_KANBANB04.GIM"): {
        "erase": [((6, 4, 28, 54), ("light", 130))], "fill": None,
        "texts": [{"lines": ["PUB"], "box": (9, 6, 26, 31), "color": (250, 250, 250), "vertical": True},
                  {"lines": ["PATO"], "box": (9, 35, 26, 54), "color": (250, 250, 250), "vertical": True}]},
    # "gekiyasu", vinho sobre placa clara
    ("BG_NM.BPM", "BG_NM\\GIM\\BGNM_KANBANB05.GIM"): {
        "erase": [((7, 11, 25, 54), ("redder", 25))], "fill": None,
        "texts": [{"lines": ["BARATO"], "box": (8, 12, 24, 53), "color": (140, 14, 36), "vertical": True}]},
    # cartaz com foto: coluna vermelha "nekomanma" e letrinhas verdes miudas
    ("BG_NM.BPM", "BG_NM\\GIM\\KABE_A01.GIM"): {
        "erase": [((44, 0, 59, 62), ("redder", 70)),
                  ((2, 26, 17, 62), lambda r, g, b, a: g - max(r, b) > 40)], "fill": None,
        "texts": [{"lines": ["RAÇÃO"], "box": (45, 3, 58, 58), "color": (150, 0, 0), "vertical": True}]},
    # barbearia: "moteru!" no topo e a plaquinha dourada
    ("BG_NM.BPM", "BG_NM\\GIM\\KABE_A03.GIM"): {
        "erase": [((5, 2, 43, 13), lambda r, g, b, a: max(r, g, b) < 120),
                  ((14, 41, 50, 44), ("light", 175)), ((10, 44, 54, 51), ("light", 175)),
                  ((14, 51, 50, 53), ("light", 175))], "fill": None,
        "texts": [{"lines": ["SUCESSO!"], "box": (5, 3, 43, 11), "color": (24, 22, 32)},
                  {"lines": ["BARBEARIA"], "box": (10, 43, 54, 52), "color": (248, 246, 238)}]},
    # placa do acougue "korokke" (croquete), vermelho sobre a faixa dourada; o dourado tem azul baixo
    ("BG_NM.BPM", "BG_NM\\GIM\\KABE_O06.GIM"): {
        "erase": [((0, 1, 32, 9), lambda r, g, b, a: b > 90 or r - g > 45)], "fill": None,
        "texts": [{"lines": ["CROQUETE"], "box": (0, 2, 32, 9), "color": (140, 8, 8)}]},
    # cortina do banho publico: "yu" branco
    ("BG_PB.BPM", "BG_PB\\GIM\\BGPB_GATENOREN2.GIM"): {
        "erase": [((19, 9, 45, 27), ("light", 125))], "fill": None,
        "texts": [{"lines": ["BANHO"], "box": (17, 10, 47, 26), "color": (250, 236, 236)}]},
    # "hari, kyuu, shiatsu", cinza escuro sobre cinza claro
    ("BG_PB.BPM", "BG_PB\\GIM\\BGPB_POSTER2.GIM"): {
        "erase": [((0, 19, 64, 32), ("dark", 168))], "fill": None,
        "texts": [{"lines": ["ACUPUNTURA"], "box": (1, 20, 63, 31), "color": (62, 66, 60)}]},
    # "muryou shindan-chuu", branco sobre magenta
    ("BG_PB.BPM", "BG_PB\\GIM\\BGPB_POSTER4.GIM"): {
        "erase": [((0, 19, 64, 32), ("light", 110))], "fill": None,
        "texts": [{"lines": ["CONSULTA", "GRÁTIS"], "box": (2, 14, 62, 31), "color": (244, 230, 236)}]},
    # "kakushu hoken atsukai", escuro sobre verde
    ("BG_PB.BPM", "BG_PB\\GIM\\BGPB_POSTER5.GIM"): {
        "erase": [((0, 0, 64, 14), ("dark", 150))], "fill": None,
        "texts": [{"lines": ["ACEITAMOS", "CONVÊNIOS"], "box": (2, 1, 62, 22), "color": (44, 56, 36)}]},
    # "denki seihin no goyoumei wa", claro sobre azul
    ("BG_PB.BPM", "BG_PB\\GIM\\BGPB_POSTER6.GIM"): {
        "erase": [((0, 0, 64, 12), ("light", 130))], "fill": None,
        "texts": [{"lines": ["ELETRÔNICOS"], "box": (1, 0, 63, 11), "color": (200, 208, 224)}]},
    # maquina de troca: "ryougae" branco no alto do painel azul (os numeros ficam)
    ("BG_PC.BPM", "BG_PC\\GIM\\BGPC_RYOUGAE.GIM"): {
        "erase": [((16, 1, 46, 15), ("light", 150))], "fill": None,
        "texts": [{"lines": ["TROCO"], "box": (16, 2, 46, 14), "color": (250, 250, 250)}]},
    # "tamakashiki", cinza claro sobre verde escuro
    ("BG_PC.BPM", "BG_PC\\GIM\\BGPC_TAMAKASI.GIM"): {
        "erase": [((0, 0, 32, 10), ("light", 125))], "fill": None,
        "texts": [{"lines": ["BOLAS"], "box": (1, 0, 31, 9), "color": (168, 170, 160)}]},
    # "shindai irekae!", amarelo em pinceladas sobre a foto
    ("BG_PC.BPM", "BG_PC\\GIM\\BGPC_POSTER01.GIM"): {
        "erase": [((0, 0, 40, 62), ("near", (232, 232, 32), 90))], "fill": None,
        "texts": [{"lines": ["NOVAS!"], "box": (3, 1, 29, 58), "color": (236, 232, 30), "vertical": True,
                   "outline": (20, 0, 50)}]},
    # "iwai shinsou kaiten" + "Bisaido"; em azul, vermelho e o nome miudo escuro
    ("BG_PC.BPM", "BG_PC\\GIM\\KABE_U03_02.GIM"): {
        "erase": [((7, 0, 57, 59), INK)], "fill": "rows",
        "texts": [{"lines": ["PARABÉNS"], "box": (8, 3, 56, 14), "color": (16, 40, 200)},
                  {"lines": ["INAUGURAÇÃO"], "box": (7, 17, 57, 33), "color": (226, 24, 56)},
                  {"lines": ["NOVA LOJA"], "box": (7, 40, 57, 58), "color": (226, 24, 56)}]},
    # versao do quarto: "iwai kaiten" + "akichi hiroba" a esquerda + "Bisaido" a direita
    ("BG_ROOM.BPM", "HANAWA\\GIM\\KABE_U03_02.GIM"): {
        "erase": [((7, 0, 57, 59), INK)], "fill": "rows",
        "texts": [{"lines": ["PARABÉNS"], "box": (8, 3, 56, 16), "color": (16, 40, 200)},
                  {"lines": ["INAUGURAÇÃO"], "box": (7, 19, 57, 35), "color": (226, 24, 56)},
                  {"lines": ["NOVA LOJA"], "box": (7, 40, 57, 58), "color": (226, 24, 56)}]},
}
