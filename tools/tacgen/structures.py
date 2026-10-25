"""Estruturas de facção: base policial e favela, geradas como /function.

Cada estrutura é escrita em `out/TacGuns(B)/functions/` como vários `.mcfunction`
(coordenadas relativas ao jogador) e um arquivo mestre chamado pelo jogador:

    /function policial   -> base da Polícia
    /function favela     -> favela completa com a boca de fumo
    /function faccao     -> ajuda / lista de comandos

Só são usados blocos vanilla do Bedrock 1.21 sem estados, para que cada linha
`fill`/`setblock` funcione em qualquer versão recente.
"""
import os
import random

# ------------------------------------------------------------------ blocos
ASFALTO = "gray_concrete"
FAIXA = "white_concrete"
CONCRETO_AZUL = "light_blue_concrete"
AZUL = "blue_concrete"
PISO_POLIDO = "polished_andesite"
QUARTZO = "quartz_block"
QUARTZO_LISO = "chiseled_quartz_block"
PEDRA = "stone"
PEDRA_LISA = "smooth_stone"
PEDRA_LAVADA = "stone_bricks"
SAIBRO = "coarse_dirt"
TERRA = "dirt"
CAMINHO = "dirt_path"
BRITA = "gravel"
TIJOLO = "bricks"
TIJOLO_BARRO = "mud_bricks"
TERRACOTA = "terracotta"
TERRACOTA_BRANCA = "white_terracotta"
TERRACOTA_LARANJA = "orange_terracotta"
TERRACOTA_VERMELHA = "red_terracotta"
TERRACOTA_CINZA = "gray_terracotta"
TERRACOTA_MARROM = "brown_terracotta"
MADEIRA = "oak_planks"
MADEIRA_ESCURA = "dark_oak_planks"
MADEIRA_JUNGLE = "jungle_planks"
VIDRO = "glass"
VIDRO_FINO = "glass_pane"
GRADE = "iron_bars"
FERRO = "iron_block"
OURO = "gold_block"
LUZ = "sea_lantern"
LANTERNA = "lantern"
TOCHA = "torch"
CONCRETO_CINZA = "gray_concrete"
CONCRETO_BRANCO = "white_concrete"
CONCRETO_PRETO = "black_concrete"
CONCRETO_VERMELHO = "red_concrete"
CONCRETO_VERDE = "lime_concrete"
CONCRETO_AMARELO = "yellow_concrete"
CONCRETO_LARANJA = "orange_concrete"
CONCRETO_MARROM = "brown_concrete"
CONCRETO_VERDE = "lime_concrete"
CONCRETO_ROXO = "purple_concrete"
CONCRETO_CIANO = "cyan_concrete"
LA_ROSA = "pink_wool"
LA_BRANCA = "white_wool"
LA_VERMELHA = "red_wool"
LA_AZUL = "blue_wool"
LA_VERDE = "green_wool"
LA_PRETA = "black_wool"
LA_CINZA = "light_gray_wool"
LA_AMARELA = "yellow_wool"
BARRIL = "barrel"
BAU = "chest"
BANCADA = "crafting_table"
FORNALHA = "furnace"
ALTO_FORNO = "blast_furnace"
BIGORNA = "smithing_table"
REBOLO = "grindstone"
BIGORNA_ANTIGA = "anvil"
CALDEIRAO = "cauldron"
ANDAIME = "scaffolding"
CERCA = "oak_fence"
CERCA_ESCURA = "spruce_fence"
AGUA = "water"
FOGUEIRA = "campfire"
JUKEBOX = "jukebox"
NOTA = "noteblock"
AREIA = "sand"
MAGMA = "magma"

# letras 3x5 para placas no chão/telhado
LETRAS = {
    "H": ["101", "101", "111", "101", "101"],
    "P": ["111", "101", "111", "100", "100"],
    "M": ["101", "111", "111", "101", "101"],
    "S": ["111", "100", "111", "001", "111"],
    "O": ["111", "101", "101", "101", "111"],
    "L": ["100", "100", "100", "100", "111"],
}


def rel(n):
    return "~" if n == 0 else f"~{n}"


class Cmds:
    """Acumula comandos de uma function."""

    def __init__(self):
        self.lines = []

    def fill(self, x0, y0, z0, x1, y1, z1, bloco, modo=""):
        self.lines.append(
            f"fill {rel(x0)} {rel(y0)} {rel(z0)} {rel(x1)} {rel(y1)} {rel(z1)} "
            f"{bloco}{(' ' + modo) if modo else ''}")

    def set(self, x, y, z, bloco):
        self.lines.append(f"setblock {rel(x)} {rel(y)} {rel(z)} {bloco}")

    def caixa(self, x0, y0, z0, x1, y1, z1, bloco):
        """Casca oca (paredes + piso + teto)."""
        self.fill(x0, y0, z0, x1, y1, z1, bloco, "hollow")

    def ar(self, x0, y0, z0, x1, y1, z1):
        self.fill(x0, y0, z0, x1, y1, z1, "air")

    def tell(self, texto):
        self.lines.append(
            'tellraw @s {"rawtext":[{"text":"' + texto.replace('"', "'") + '"}]}')

    def estrela(self, cx, y, cz, bloco=QUARTZO):
        """Estrela simples de 5 blocos (emblema)."""
        self.set(cx, y, cz, bloco)
        self.set(cx - 1, y, cz, bloco)
        self.set(cx + 1, y, cz, bloco)
        self.set(cx, y, cz - 1, bloco)
        self.set(cx, y, cz + 1, bloco)

    def letras(self, texto, x, y, z, bloco=QUARTZO, eixo="z"):
        """Escreve `texto` com letras 3x5 no plano horizontal (y fixo)."""
        pos = x
        for ch in texto:
            padrao = LETRAS.get(ch)
            if not padrao:
                pos += 4
                continue
            for linha, bits in enumerate(padrao):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        if eixo == "z":
                            self.set(pos + col, y, z + linha, bloco)
                        else:
                            self.set(x + linha, y, pos + col, bloco)
            pos += 4


# ==================================================================== POLÍCIA
def base_policial():
    """Base da Polícia Militar: pátio, muro, prédio de 2 andares, celas,
    arsenal, heliponto, torre de vigilância e iluminação."""
    partes = {}

    # ---------------------------------------------------------- pátio
    p = partes["00_patio"] = Cmds()
    p.fill(-16, -1, -16, 16, -1, 16, ASFALTO)
    p.fill(-16, -1, -16, 16, -1, -16, FAIXA)
    p.fill(-16, -1, 16, 16, -1, 16, FAIXA)
    p.fill(-16, -1, -16, -16, -1, 16, FAIXA)
    p.fill(-16, -1, 16, 16, -1, 16, FAIXA)
    p.fill(-16, -1, 0, 16, -1, 0, FAIXA)
    # faixas de estacionamento + viatura
    for x in (-12, -8, 4, 8, 12):
        p.fill(x, -1, 5, x, -1, 9, FAIXA)
    p.fill(-11, 0, 6, -7, 0, 7, CONCRETO_BRANCO)
    p.fill(-11, 1, 6, -7, 1, 7, AZUL)
    p.fill(-10, 1, 6, -8, 1, 6, CONCRETO_PRETO)
    p.fill(-11, 0, 9, -7, 0, 9, CONCRETO_PRETO)
    p.set(-11, 0, 6, CONCRETO_PRETO)
    p.set(-7, 0, 6, CONCRETO_PRETO)
    # praça de entrada
    p.fill(-2, -1, 16, 2, -1, 24, ASFALTO)
    p.fill(-2, -1, 16, -2, -1, 24, FAIXA)
    p.fill(2, -1, 16, 2, -1, 24, FAIXA)
    p.tell("§9Base Policial: §7pátio pronto")

    # ---------------------------------------------------------- muro
    m = partes["01_muro"] = Cmds()
    # norte / oeste / leste
    m.fill(-16, 0, -16, 16, 2, -16, CONCRETO_BRANCO)
    m.fill(-16, 3, -16, 16, 3, -16, CONCRETO_AZUL)
    m.fill(-16, 4, -16, 16, 4, -16, GRADE)
    m.fill(-16, 0, -16, -16, 2, 16, CONCRETO_BRANCO)
    m.fill(-16, 3, -16, -16, 3, 16, CONCRETO_AZUL)
    m.fill(-16, 4, -16, -16, 4, 16, GRADE)
    m.fill(16, 0, -16, 16, 2, 16, CONCRETO_BRANCO)
    m.fill(16, 3, -16, 16, 3, 16, CONCRETO_AZUL)
    m.fill(16, 4, -16, 16, 4, 16, GRADE)
    # sul com portão de 5 blocos
    for x0, x1 in ((-16, -4), (4, 16)):
        m.fill(x0, 0, 16, x1, 2, 16, CONCRETO_BRANCO)
        m.fill(x0, 3, 16, x1, 3, 16, CONCRETO_AZUL)
        m.fill(x0, 4, 16, x1, 4, 16, GRADE)
    # pilares do portão
    for x in (-4, 4):
        m.fill(x, 0, 16, x, 5, 16, CONCRETO_AZUL)
        m.set(x, 5, 16, LUZ)
    m.fill(-3, 5, 16, 3, 5, 16, CONCRETO_AZUL)
    m.fill(-3, 4, 16, 3, 4, 16, GRADE)
    # cantos
    for cx, cz in ((-16, -16), (16, -16), (-16, 16), (16, 16)):
        m.fill(cx, 0, cz, cx, 4, cz, CONCRETO_AZUL)
        m.set(cx, 5, cz, LUZ)
    m.tell("§9Base Policial: §7muro e portão prontos")

    # ---------------------------------------------------------- prédio
    b = partes["02_predio"] = Cmds()
    b.fill(-8, -1, -15, 8, -1, -4, PISO_POLIDO)
    # térreo (casca de 4 de altura)
    b.caixa(-8, 0, -15, 8, 3, -4, CONCRETO_BRANCO)
    b.fill(-7, 0, -14, 7, 0, -5, PISO_POLIDO)
    b.fill(-7, 3, -14, 7, 3, -5, CONCRETO_BRANCO)
    # primeiro andar
    b.caixa(-8, 4, -15, 8, 7, -4, CONCRETO_BRANCO)
    b.fill(-7, 4, -14, 7, 4, -5, PEDRA_LISA)
    b.fill(-7, 7, -14, 7, 7, -5, CONCRETO_BRANCO)
    # telhado + parapeito
    b.fill(-8, 8, -15, 8, 8, -4, CONCRETO_CINZA)
    b.fill(-8, 9, -15, 8, 9, -15, CONCRETO_AZUL)
    b.fill(-8, 9, -4, 8, 9, -4, CONCRETO_AZUL)
    b.fill(-8, 9, -15, -8, 9, -4, CONCRETO_AZUL)
    b.fill(8, 9, -15, 8, 9, -4, CONCRETO_AZUL)
    # porta de entrada (3x3) + degraus + toldo
    b.ar(-1, 0, -4, 1, 2, -4)
    b.fill(-2, -1, -3, 2, -1, -2, QUARTZO)
    b.fill(-2, 3, -4, 2, 3, -3, CONCRETO_AZUL)
    b.fill(-2, 0, -4, -2, 2, -4, QUARTZO)
    b.fill(2, 0, -4, 2, 2, -4, QUARTZO)
    # janelas (vidro) nas duas fachadas
    for x in (-6, -4, 4, 6):
        for y in (1, 2):
            b.set(x, y, -4, VIDRO)
            b.set(x, y + 4, -4, VIDRO)
    for z in (-12, -10, -7):
        for y in (1, 2):
            b.set(-8, y, z, VIDRO)
            b.set(8, y, z, VIDRO)
            b.set(-8, y + 4, z, VIDRO)
            b.set(8, y + 4, z, VIDRO)
    # emblema (escudo) na fachada
    b.fill(-3, 5, -4, 3, 5, -4, AZUL)
    b.fill(-2, 6, -4, 2, 6, -4, AZUL)
    b.fill(-1, 7, -4, 1, 7, -4, AZUL)
    b.set(0, 8, -4, AZUL)
    b.estrela(0, 6, -4, QUARTZO)
    b.set(0, 5, -4, QUARTZO)
    # interior: balcão de atendimento e cadeiras
    b.fill(-6, 0, -10, -3, 0, -9, PEDRA_LISA)
    b.fill(-6, 1, -10, -3, 1, -9, PEDRA_LISA)
    b.set(-7, 0, -11, BAU)
    b.set(-7, 0, -12, BAU)
    b.set(-7, 1, -11, LANTERNA)
    # escada interna para o 2º andar
    for i in range(4):
        b.fill(5, i, -9 - i, 7, i, -9 - i, PISO_POLIDO)
    b.ar(5, 4, -13, 7, 5, -13)
    b.tell("§9Base Policial: §7prédio, recepção e escada prontos")

    # ---------------------------------------------------------- celas
    c = partes["03_celas"] = Cmds()
    c.fill(-8, 0, -15, -3, 3, -15, FERRO)
    c.fill(-8, 0, -10, -8, 3, -15, FERRO)
    # duas celas de 2x3
    c.fill(-7, 0, -14, -6, 3, -11, GRADE, "outline")
    c.fill(-5, 0, -14, -4, 3, -11, GRADE, "outline")
    c.ar(-7, 0, -11, -6, 2, -11)
    c.ar(-5, 0, -11, -4, 2, -11)
    c.set(-7, 0, -11, GRADE)
    c.set(-4, 0, -11, GRADE)
    # camas, banheiro e marcador de cela
    for x in (-7, -5):
        c.fill(x, 0, -14, x, 0, -13, LA_BRANCA)
        c.set(x, 1, -14, LA_BRANCA)
        c.set(x, 0, -12, CALDEIRAO)
    c.set(-6, 0, -13, QUARTZO_LISO)   # marque aqui: /scriptevent tac_guns:marcar_cela
    c.fill(-6, 3, -13, -6, 3, -13, LUZ)
    c.tell("§9Base Policial: §7celas prontas (marque com /scriptevent tac_guns:marcar_cela)")

    # ---------------------------------------------------------- arsenal
    a = partes["04_arsenal"] = Cmds()
    a.fill(3, 0, -15, 7, 3, -15, FERRO)
    a.fill(7, 0, -15, 7, 3, -10, FERRO)
    a.ar(3, 0, -11, 5, 2, -11)
    a.set(6, 0, -11, GRADE)
    a.set(6, 1, -11, GRADE)
    a.fill(3, 0, -14, 6, 0, -12, PEDRA_LISA)
    a.set(4, 0, -14, BARRIL)
    a.set(5, 0, -14, BARRIL)
    a.set(4, 1, -14, BARRIL)
    a.set(5, 1, -14, BAU)
    a.set(3, 0, -13, BAU)
    a.set(6, 0, -13, BIGORNA)
    a.set(6, 0, -12, REBOLO)
    a.set(3, 0, -12, ALTO_FORNO)
    a.set(6, 1, -12, LANTERNA)
    a.tell("§9Base Policial: §7arsenal pronto")

    # ---------------------------------------------------------- cobertura
    t = partes["05_cobertura"] = Cmds()
    # heliponto 7x7 com "H"
    t.fill(-3, 8, -13, 3, 8, -7, CONCRETO_CINZA)
    t.fill(-3, 8, -13, 3, 8, -13, CONCRETO_BRANCO)
    t.fill(-3, 8, -7, 3, 8, -7, CONCRETO_BRANCO)
    t.fill(-3, 8, -13, -3, 8, -7, CONCRETO_BRANCO)
    t.fill(3, 8, -13, 3, 8, -7, CONCRETO_BRANCO)
    t.letras("H", -2, 8, -12, QUARTZO)
    # antena e luzes de teto
    t.fill(6, 9, -14, 6, 12, -14, FERRO)
    t.set(6, 13, -14, LUZ)
    for x, z in ((-6, -13), (6, -6), (-6, -6)):
        t.set(x, 9, z, LUZ)
    # segundo piso visível pela cobertura: claraboia
    t.fill(-4, 7, -10, -1, 7, -6, VIDRO)
    t.tell("§9Base Policial: §7cobertura e heliponto prontos")

    # ---------------------------------------------------------- torre
    v = partes["06_torre"] = Cmds()
    v.fill(-15, 0, 8, -11, 0, 12, PEDRA_LISA)
    v.fill(-15, 1, 8, -15, 6, 12, PEDRA_LAVADA)
    v.fill(-11, 1, 8, -11, 6, 12, PEDRA_LAVADA)
    v.fill(-15, 1, 8, -11, 6, 8, PEDRA_LAVADA)
    v.fill(-15, 1, 12, -11, 6, 12, PEDRA_LAVADA)
    v.fill(-13, 1, 10, -13, 6, 10, ANDAIME)
    v.fill(-15, 7, 8, -11, 7, 12, CONCRETO_CINZA)
    v.fill(-15, 8, 8, -15, 8, 12, GRADE)
    v.fill(-11, 8, 8, -11, 8, 12, GRADE)
    v.fill(-15, 8, 8, -11, 8, 8, GRADE)
    v.fill(-15, 8, 12, -11, 8, 12, GRADE)
    v.fill(-15, 9, 8, -11, 9, 12, CONCRETO_AZUL)
    v.set(-13, 8, 10, LUZ)
    v.set(-13, 9, 8, LUZ)
    v.tell("§9Base Policial: §7torre de vigilância pronta")

    # ---------------------------------------------------------- detalhes
    d = partes["07_detalhes"] = Cmds()
    # postes de luz no pátio
    for x, z in ((-13, 3), (13, 3), (-13, 13), (13, 13)):
        d.fill(x, 0, z, x, 2, z, PISO_POLIDO)
        d.set(x, 3, z, LUZ)
    # mastro da bandeira (azul, com detalhe dourado)
    d.fill(-6, 0, 12, -6, 6, 12, FERRO)
    d.set(-6, 7, 12, OURO)
    d.fill(-5, 5, 12, -3, 6, 12, AZUL)
    # banco e mesa no pátio
    d.fill(8, 0, 10, 10, 0, 10, MADEIRA)
    d.set(8, 1, 10, CERCA)
    d.set(10, 1, 10, CERCA)
    # caixa d'água
    d.fill(12, 0, -6, 14, 1, -4, PEDRA_LAVADA)
    d.fill(12, 2, -6, 14, 2, -4, AGUA)
    d.tell("§aBase Policial construída! §7Celas: marque com /scriptevent tac_guns:marcar_cela")
    return partes


# ===================================================================== FAVELA
PALETAS = [
    TIJOLO, TIJOLO, TIJOLO, TIJOLO_BARRO, TIJOLO_BARRO,
    TERRACOTA_LARANJA, TERRACOTA_LARANJA, TERRACOTA_VERMELHA, TERRACOTA,
]
ESTILOS = ["telha"] * 70 + ["laje"] * 25 + ["lona"] * 5
TELHAS = (["red_terracotta"] * 7 + ["orange_terracotta"] * 2 + ["bricks"] * 1)
TOLDOS = [LA_VERMELHA, LA_AZUL, LA_VERDE, LA_PRETA, LA_CINZA, LA_AMARELA]
GRAFFITI = [CONCRETO_ROXO, CONCRETO_CIANO, CONCRETO_VERDE, CONCRETO_AMARELO,
            CONCRETO_LARANJA, CONCRETO_VERMELHO, CONCRETO_MARROM]


def casa(c, rnd, x, z, y, w, d, h, parede, estilo, porta_lado):
    """Barraco de favela: laje de concreto, paredes de tijolo, telhado de telha,
    laje com parapeito ou lona, caixa d'água, antena, puxadinho e pichação."""
    c.fill(x, y - 1, z, x + w, y - 1, z + d, PEDRA_LAVADA)
    c.caixa(x, y, z, x + w, y + h, z + d, parede)
    c.fill(x + 1, y, z + 1, x + w - 1, y, z + d - 1, MADEIRA)
    # porta
    if porta_lado == 0:
        c.ar(x + 1, y, z, x + 2, y + 2, z)
    elif porta_lado == 1:
        c.ar(x + w, y, z + 1, x + w, y + 2, z + 2)
    elif porta_lado == 2:
        c.ar(x + 1, y, z + d, x + 2, y + 2, z + d)
    else:
        c.ar(x, y, z + 1, x, y + 2, z + 2)
    # janelas pequenas e grades (cara de favela)
    for i in range(2):
        if rnd.random() < 0.8:
            c.set(x + 1 + i * 2, y + 2, z, VIDRO_FINO)
        if rnd.random() < 0.65:
            c.set(x + w, y + 2, z + 1 + i * 2, VIDRO_FINO)
        if rnd.random() < 0.35:
            c.set(x + 1 + i * 2, y + 1, z, GRADE)
    # telhado
    telha = rnd.choice(TELHAS)
    if estilo == "telha":
        c.fill(x, y + h, z, x + w, y + h, z + d, telha)
        if rnd.random() < 0.55:
            c.fill(x, y + h + 1, z, x + w, y + h + 1, z + d // 2, telha)
            c.fill(x, y + h + 1, z + d // 2, x + w, y + h + 1, z + d // 2, LA_PRETA)
    elif estilo == "laje":
        c.fill(x, y + h, z, x + w, y + h, z + d, PEDRA_LISA)
        c.fill(x, y + h + 1, z, x + w, y + h + 1, z, parede)
        c.fill(x, y + h + 1, z + d, x + w, y + h + 1, z + d, parede)
        c.fill(x, y + h + 1, z, x, y + h + 1, z + d, parede)
        c.fill(x + w, y + h + 1, z, x + w, y + h + 1, z + d, parede)
    else:
        cor = rnd.choice(TOLDOS)
        c.fill(x, y + h, z, x + w, y + h, z + d, cor)
        c.fill(x, y + h + 1, z, x + w, y + h + 1, z + 1, cor)
        c.set(x + w, y + h + 1, z + 1, LA_PRETA)
    # puxadinho em cima da laje
    if rnd.random() < 0.45:
        cor = rnd.choice(TOLDOS)
        c.caixa(x + 1, y + h + 1, z + 1, x + 3, y + h + 2, z + 3, TIJOLO)
        c.fill(x + 1, y + h + 3, z + 1, x + 3, y + h + 3, z + 3, cor)
        c.ar(x + 2, y + h + 1, z + 1, x + 2, y + h + 2, z + 1)
        c.set(x + 3, y + h + 2, z + 2, VIDRO_FINO)
    # caixa d'água / antena de TV
    if rnd.random() < 0.75:
        c.set(x + w - 1, y + h + (2 if estilo == "laje" else 1), z + 1, CALDEIRAO)
        if rnd.random() < 0.5:
            c.set(x + w - 1, y + h + (3 if estilo == "laje" else 2), z + 1, CALDEIRAO)
    if rnd.random() < 0.7:
        base = y + h + (2 if estilo == "laje" else 1)
        c.fill(x + 1, base, z + d - 1, x + 1, base + 1, z + d - 1, CERCA)
        c.set(x + 1, base + 2, z + d - 1, GRADE)
    # interior simples
    c.fill(x + w - 1, y, z + d - 1, x + w - 1, y, z + d - 2, LA_BRANCA)
    c.set(x + w - 1, y + 1, z + d - 1, LA_BRANCA)
    c.set(x + 1, y, z + d - 1, BANCADA)
    c.set(x + w - 1, y, z + 1, FORNALHA)
    if rnd.random() < 0.6:
        c.set(x + 1, y, z + 1, BARRIL)
    c.set(x + 2, y + h - 1, z + d // 2, TOCHA)
    # pichação na fachada (só em parte dos barracos)
    if rnd.random() < 0.3:
        return
    cor = rnd.choice(GRAFFITI)
    if porta_lado in (0, 2):
        zz = z if porta_lado == 0 else z + d
        c.fill(x + w - 3, y + 1, zz, x + w - 1, y + 1, zz, cor)
        if rnd.random() < 0.5:
            c.set(x + w - 2, y + 2, zz, cor)
    else:
        xx = x if porta_lado == 3 else x + w
        c.fill(xx, y + 1, z + d - 3, xx, y + 1, z + d - 1, cor)


def favela():
    """Favela densa em quatro patamares, 50 barracos colados, becos de 1 bloco,
    escadões, lajes com parapeito, telhados de telha, varais, fios, quadra e
    galpão de laje embaixo, boca de fumo no meio e mirador no alto."""
    rnd = random.Random(20240607)
    partes = {}
    # 4 patamares: cada coluna sobe 2 blocos (0, 2, 4, 6)
    NIVEIS = (0, 0, 2, 2, 4, 4, 6, 6)
    XS = [-26, -19, -12, -5, 2, 9, 16, 23]
    ZS = [-26, -19, -12, -5, 2, 9, 16, 23]

    # ---------------------------------------------------------- terreno
    t = partes["00_terreno"] = Cmds()
    t.fill(-30, -2, -30, 30, -2, 30, TERRA)
    for i, x in enumerate(XS):
        nivel = NIVEIS[i]
        prox = NIVEIS[i + 1] if i + 1 < len(NIVEIS) else nivel
        topo = max(nivel, prox)
        t.fill(x - 1, -1, -28, x + 6, topo - 1, 28, SAIBRO)
        t.fill(x - 1, topo - 1, -28, x + 6, topo - 1, 28, CAMINHO)
        if nivel > 0:
            t.fill(x - 1, -1, -28, x - 1, nivel, 28, PEDRA_LAVADA)
    t.fill(XS[-1] + 6, -1, -28, XS[-1] + 6, 6, 28, PEDRA_LAVADA)
    t.fill(XS[0] - 2, -1, -28, XS[0] - 2, 0, 28, PEDRA_LAVADA)
    t.tell("§6Favela: §7morro em 4 patamares pronto")

    # ---------------------------------------------------------- becos e escadões
    b = partes["01_becos"] = Cmds()
    for i, x in enumerate(XS):
        nivel = NIVEIS[i]
        b.fill(x, nivel - 1, -28, x, nivel - 1, 28, CAMINHO)
    # escadões nas divisas de patamar (3 larguras diferentes)
    for i in range(1, len(XS)):
        nivel_novo, nivel_velho = NIVEIS[i], NIVEIS[i - 1]
        if nivel_novo == nivel_velho:
            continue
        for z0 in (-24, -10, 4, 18):
            for passo in range(nivel_novo - nivel_velho):
                altura = nivel_velho + passo
                b.fill(XS[i] - 1, altura - 1, z0, XS[i] - 1, altura - 1, z0 + 2, PEDRA)
    # vielas transversais
    for z in (-27, -13, 1, 15):
        for i, x in enumerate(XS):
            b.fill(x, NIVEIS[i] - 1, z, x + 6, NIVEIS[i] - 1, z, CAMINHO)
    b.set(-15, 1, -3, AGUA)
    b.set(6, 5, 9, AGUA)
    b.tell("§6Favela: §7becos e escadões prontos")

    # ---------------------------------------------------------- casas
    casas = partes["02_casas"] = Cmds()
    total = 0
    for ci, x in enumerate(XS):
        for ri, z in enumerate(ZS):
            # praça da boca de fumo (centro-baixo) e mirador (canto alto)
            if ci in (1, 2) and ri in (3, 4):
                continue
            if ci >= 6 and ri >= 6:
                continue
            # galpão/quadra no pé do morro
            if ci <= 1 and ri >= 6:
                continue
            y = NIVEIS[ci]
            w = 6 if rnd.random() < 0.7 else 5
            d = 6 if rnd.random() < 0.7 else 5
            h = 2 if rnd.random() < 0.25 else (3 if rnd.random() < 0.6 else 4)
            parede = rnd.choice(PALETAS)
            estilo = rnd.choice(ESTILOS)
            casa(casas, rnd, x, z, y, w, d, h, parede, estilo, rnd.randrange(4))
            total += 1
    casas.tell(f"§6Favela: §7{total} barracos construídos")

    # ---------------------------------------------------------- detalhes
    d = partes["03_detalhes"] = Cmds()
    # varais e fios entre os barracos
    for x, z, y in ((-22, -20, 4), (-9, -6, 6), (4, 3, 8), (17, 10, 10),
                    (-23, 12, 4), (11, -22, 8)):
        d.fill(x, y, z, x + 8, y, z, CERCA)
        d.fill(x + 1, y - 1, z, x + 4, y - 1, z, LA_BRANCA)
        d.fill(x + 5, y - 1, z, x + 7, y - 1, z, LA_VERMELHA)
    # postes de luz e fios nos becos
    for x, z, y in ((-26, 1, 0), (-12, 1, 2), (-5, 3, 2), (2, 5, 4), (9, 7, 6),
                    (16, 9, 6), (23, 11, 8), (-19, 15, 2), (5, -13, 4)):
        d.fill(x, y, z, x, y + 3, z, MADEIRA_ESCURA)
        d.set(x, y + 4, z, LANTERNA)
    # barracas de lona e bancas
    for x, z, y, cor in ((-24, -6, 1, LA_AZUL), (-3, 4, 3, LA_VERMELHA),
                         (13, -4, 5, LA_VERDE), (-17, 9, 1, LA_AMARELA)):
        d.fill(x, y, z, x + 3, y, z + 3, cor)
        d.fill(x, y + 1, z, x + 3, y + 1, z, cor)
        d.set(x + 1, y, z + 1, BANCADA)
        d.set(x + 2, y, z + 1, BARRIL)
    # pichações no arrimo
    for x, y, z in ((-13, 1, -8), (-6, 3, 6), (3, 5, -6), (10, 7, 8), (17, 9, -10)):
        d.fill(x, y, z, x, y + 1, z + 2, rnd.choice(GRAFFITI))
    d.tell("§6Favela: §7fios, varais e barracas prontos")

    # ---------------------------------------------------------- boca de fumo
    o = partes["04_boca"] = Cmds()
    o.fill(-18, 1, -4, -6, 1, 8, CAMINHO)
    o.fill(-18, 1, -4, -6, 1, -4, PEDRA_LAVADA)
    o.fill(-18, 1, 8, -6, 1, 8, PEDRA_LAVADA)
    o.fill(-17, 4, -3, -7, 4, 7, CONCRETO_CINZA)
    o.fill(-17, 5, -3, -7, 5, 7, LA_VERMELHA)
    o.fill(-17, 5, 1, -7, 5, 2, LA_PRETA)
    for x in (-17, -12, -7):
        o.fill(x, 2, -3, x, 4, -3, CONCRETO_BRANCO)
        o.fill(x, 2, 7, x, 4, 7, CONCRETO_BRANCO)
    o.fill(-15, 2, 1, -9, 2, 2, PEDRA_LISA)
    o.fill(-15, 3, 1, -9, 3, 2, PEDRA_LISA)
    o.set(-16, 2, 0, BARRIL)
    o.set(-16, 2, -1, BARRIL)
    o.set(-16, 3, 0, BARRIL)
    o.set(-16, 2, 3, BAU)
    o.set(-16, 2, 4, BAU)
    o.fill(-13, 2, -2, -11, 2, -2, MADEIRA)
    o.set(-12, 3, -2, OURO)
    o.set(-15, 2, 5, JUKEBOX)
    o.set(-9, 2, 5, NOTA)
    o.set(-9, 2, 6, NOTA)
    o.set(-12, 2, 6, FOGUEIRA)
    o.fill(-14, 2, 7, -10, 2, 7, MADEIRA)
    for x in (-16, -14, -12, -10):
        o.fill(x, 2, 8, x, 3, 8, LA_BRANCA)
    o.fill(-18, 3, -6, -18, 4, -2, CONCRETO_VERMELHO)
    o.fill(-17, 3, -6, -14, 3, -6, CONCRETO_AMARELO)
    o.set(-15, 4, -6, CONCRETO_ROXO)
    o.set(-13, 4, -6, CONCRETO_AMARELO)
    o.tell("§4Boca de fumo pronta")

    # ---------------------------------------------------------- mirador
    mi = partes["05_mirador"] = Cmds()
    mi.fill(21, 6, 20, 28, 6, 27, PEDRA_LAVADA)
    mi.fill(21, 7, 20, 28, 7, 20, PEDRA_LAVADA)
    mi.fill(21, 7, 27, 28, 7, 27, PEDRA_LAVADA)
    mi.fill(21, 7, 20, 21, 7, 27, PEDRA_LAVADA)
    mi.fill(28, 7, 20, 28, 7, 27, PEDRA_LAVADA)
    mi.fill(24, 7, 23, 24, 14, 23, ANDAIME)
    mi.fill(22, 15, 21, 26, 15, 25, CONCRETO_CINZA)
    mi.fill(22, 16, 21, 22, 16, 25, GRADE)
    mi.fill(26, 16, 21, 26, 16, 25, GRADE)
    mi.fill(22, 16, 21, 26, 16, 21, GRADE)
    mi.fill(22, 16, 25, 26, 16, 25, GRADE)
    mi.set(24, 17, 23, LA_VERMELHA)
    mi.set(24, 16, 23, LUZ)
    mi.tell("§4Mirador da favela pronto")

    # ---------------------------------------------------------- quadra e galpão
    q = partes["06_quadra"] = Cmds()
    # galpão de laje (o bloco de concreto da frente da foto)
    q.fill(-28, -1, 18, -14, -1, 28, PEDRA_LISA)
    q.fill(-28, 0, 18, -28, 2, 28, CONCRETO_BRANCO)
    q.fill(-14, 0, 18, -14, 2, 28, CONCRETO_BRANCO)
    q.fill(-28, 0, 28, -14, 2, 28, CONCRETO_BRANCO)
    q.fill(-28, 3, 17, -14, 3, 29, CONCRETO_CINZA)
    q.fill(-28, 4, 17, -14, 4, 17, CONCRETO_BRANCO)
    q.fill(-28, 4, 29, -14, 4, 29, CONCRETO_BRANCO)
    q.fill(-28, 4, 17, -28, 4, 29, CONCRETO_BRANCO)
    q.fill(-14, 4, 17, -14, 4, 29, CONCRETO_BRANCO)
    q.ar(-24, 0, 28, -18, 2, 28)
    q.fill(-26, 0, 20, -25, 1, 26, LA_BRANCA)
    q.fill(-23, 0, 20, -22, 1, 26, LA_BRANCA)
    q.set(-27, 0, 27, BAU)
    q.set(-15, 0, 27, BARRIL)
    q.fill(-25, 2, 23, -24, 2, 23, LUZ)
    # quadra descoberta com alambrado
    q.fill(-12, -1, 18, 2, -1, 28, CONCRETO_VERDE)
    q.fill(-12, -1, 18, 2, -1, 18, FAIXA)
    q.fill(-12, -1, 28, 2, -1, 28, FAIXA)
    for x in (-12, 2):
        q.fill(x, 0, 18, x, 2, 18, GRADE)
        q.fill(x, 0, 28, x, 2, 28, GRADE)
        q.fill(x, 0, 18, x, 2, 28, GRADE)
    q.fill(-12, 0, 18, 2, 2, 18, GRADE)
    q.fill(-12, 0, 28, 2, 2, 28, GRADE)
    q.fill(-6, 0, 22, -4, 2, 24, GRADE)
    q.set(-11, 0, 27, LANTERNA)
    q.set(1, 0, 27, LANTERNA)
    q.tell("§6Favela completa! §7Galpão e quadra prontos")

    # ---------------------------------------------------------- saída
    s = partes["07_saida"] = Cmds()
    s.fill(-30, -1, 29, 30, -1, 30, CAMINHO)
    s.fill(3, -1, 18, 20, -1, 18, CAMINHO)
    s.fill(-30, 0, 29, -30, 2, 29, CONCRETO_PRETO)
    s.set(-30, 1, 29, CONCRETO_AMARELO)
    s.tell("§6Use /scriptevent tac_guns:loja para o arsenal da facção")
    return partes


# ================================================================== escrita
def _write_part(caminho, c):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(c.lines) + "\n")


def ajuda():
    c = Cmds()
    c.tell("§6§l=== TACGUNS: FACÇÕES E BASES ===")
    c.tell("§e/function policial §7- constrói a base da Polícia ao seu redor")
    c.tell("§e/function favela §7- constrói a favela inteira com a boca de fumo")
    c.tell("§e/function lado_policial §7- entrar/trocar para a Polícia (sem menu)")
    c.tell("§e/function lado_ladrao §7- entrar/trocar para o Ladrão (sem menu)")
    c.tell("§e/scriptevent tac_guns:faccao §7- abrir a tela de escolha de lado")
    c.tell("§e/scriptevent tac_guns:loja §7- comprar armas do seu lado")
    c.tell("§e/scriptevent tac_guns:info §7- sua ficha (dinheiro, patente, procurado)")
    c.tell("§e/scriptevent tac_guns:marcar_cela §7- marcar a cela (polícia, dentro dela)")
    return c


KITS = {
    "policial": ("POLICIAL", "§9", "1", "policia", "ladrao", "tac_guns:pt92_emp",
                 "tac_guns:9x19mm", "tac_guns:algemas"),
    "ladrao": ("LADRÃO", "§4", "2", "ladrao", "policia", "tac_guns:tec9_emp",
               "tac_guns:9x19mm", ""),
}


def lado(nome):
    """Escolha de lado por comando: funciona mesmo sem os scripts."""
    rotulo, cor, valor, tag, outra, arma, municao, extra = KITS[nome]
    c = Cmds()
    c.tell(f"{cor}§l{rotulo}§r §7- entrando no lado...")
    for obj in ("dinheiro", "abates", "reputacao", "procurado", "faccao"):
        c.lines.append(f"scoreboard objectives add {obj} dummy {obj}")
    c.lines.append(f"tag @s remove {outra}")
    c.lines.append(f"tag @s add {tag}")
    c.lines.append(f"scoreboard players set @s faccao {valor}")
    c.lines.append(f"scoreboard players add @s dinheiro 0")
    c.lines.append(f"give @s {arma} 1")
    c.lines.append(f"give @s {municao} 60")
    if extra:
        c.lines.append(f"give @s {extra} 1")
    c.lines.append(f"tag @s add kit_{tag}")
    c.tell(f"§aVocê agora é {cor}{rotulo}§a. Kit entregue (pistola + 60 munições).")
    c.tell("§7Loja: §f/scriptevent tac_guns:loja §7· Ficha: §f/scriptevent tac_guns:info")
    return c


def escrever(bp_dir):
    """Escreve as functions em `bp_dir/functions` e devolve o relatório."""
    rel_ = []
    for nome_mestre, partes, titulo in (
            ("policial", base_policial(), "Base Policial"),
            ("favela", favela(), "Favela")):
        master = Cmds()
        master.tell(f"§6§l{titulo}§r §7- construindo ao seu redor...")
        for parte in sorted(partes):
            master.lines.append(f"function {nome_mestre}/{parte}")
        _write_part(os.path.join(bp_dir, "functions", f"{nome_mestre}.mcfunction"), master)
        comandos = len(master.lines)
        for parte, c in partes.items():
            _write_part(os.path.join(bp_dir, "functions", nome_mestre,
                                     f"{parte}.mcfunction"), c)
            comandos += len(c.lines)
        rel_.append((nome_mestre, len(partes) + 1, comandos))
    _write_part(os.path.join(bp_dir, "functions", "faccao.mcfunction"), ajuda())
    for nome in ("policial", "ladrao"):
        _write_part(os.path.join(bp_dir, "functions", f"lado_{nome}.mcfunction"),
                    lado(nome))
    return rel_
