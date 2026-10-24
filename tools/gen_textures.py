#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera todas as texturas do addon Creative Squad - Itens Lendarios.

Saida:
  src/resource_pack/textures/items/*.png              (icones 32x32)
  src/resource_pack/textures/models/armor/*_1.png     (camada de armadura 64x32)
  src/resource_pack/pack_icon.png                     (128x128)
  src/behavior_pack/pack_icon.png                     (128x128)

Uso:  python3 tools/gen_textures.py
"""
import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, "src", "resource_pack")
BP = os.path.join(ROOT, "src", "behavior_pack")
ITEMS_DIR = os.path.join(RP, "textures", "items")
ARMOR_DIR = os.path.join(RP, "textures", "models", "armor")

S = 32  # tamanho do icone
OUTLINE = (22, 18, 26, 255)

# ---------------------------------------------------------------- paleta
GOLD = (242, 201, 76, 255)
GOLD_L = (255, 232, 140, 255)
GOLD_D = (176, 122, 24, 255)
PURPLE = (160, 92, 214, 255)
PURPLE_L = (198, 143, 240, 255)
PURPLE_D = (92, 43, 134, 255)
IRON = (198, 204, 214, 255)
IRON_L = (232, 236, 242, 255)
IRON_D = (116, 124, 138, 255)
WOOD = (138, 94, 46, 255)
WOOD_D = (86, 56, 26, 255)
GREEN = (88, 196, 92, 255)
GREEN_L = (150, 226, 140, 255)
GREEN_D = (42, 116, 48, 255)
TEAL = (66, 219, 210, 255)
TEAL_L = (160, 246, 240, 255)
TEAL_D = (20, 128, 142, 255)
RED = (224, 74, 74, 255)
RED_D = (150, 32, 40, 255)
BLUE = (86, 190, 245, 255)
BLUE_L = (160, 225, 255, 255)
BLUE_D = (32, 110, 168, 255)
WHITE = (244, 244, 246, 255)
GRAY = (196, 200, 206, 255)
BLACK = (54, 50, 60, 255)
GLASS = (206, 236, 240, 255)
POTATO = (196, 158, 74, 255)
POTATO_D = (140, 104, 44, 255)
TOXIC = (150, 214, 74, 255)
FIRE = (255, 206, 92, 255)


def canvas():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def outline(img, color=OUTLINE):
    """Contorno de 1px em volta de todos os pixels opacos."""
    alpha = img.split()[3]
    grown = alpha.filter(ImageFilter.MaxFilter(3))
    ring = ImageChops.subtract(grown, alpha)
    ring = ring.point(lambda v: 255 if v > 8 else 0)
    layer = Image.new("RGBA", img.size, color)
    out = img.copy()
    out.paste(layer, (0, 0), ring)
    return out


def save(img, name, folder=ITEMS_DIR, do_outline=True):
    os.makedirs(folder, exist_ok=True)
    if do_outline:
        img = outline(img)
    img.save(os.path.join(folder, name + ".png"))


def line(d, p0, p1, color, width=1):
    d.line([p0, p1], fill=color, width=width)
    # pontas arredondadas
    r = width / 2.0
    for p in (p0, p1):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=color)


# ---------------------------------------------------------------- iconess
def icon_espada():
    img, d = canvas()
    axis_a, axis_b = (11, 21), (24, 8)
    # lamina
    d.polygon([(9, 20), (23, 6), (26, 9), (12, 23)], fill=GOLD)
    d.polygon([(11, 20), (24, 7), (25, 8), (12, 21)], fill=GOLD_L)
    # ponta
    d.polygon([(23, 6), (27, 4), (26, 9)], fill=GOLD_L)
    # guarda
    d.line([(6, 17), (15, 26)], fill=PURPLE_D, width=4)
    d.line([(6, 17), (15, 26)], fill=PURPLE, width=2)
    # cabo
    d.line([(11, 22), (6, 27)], fill=PURPLE_D, width=4)
    d.line([(11, 22), (7, 26)], fill=PURPLE_L, width=1)
    # pomo
    d.ellipse([3, 24, 8, 29], fill=GOLD_D)
    return img


def icon_batata():
    img, d = canvas()
    d.ellipse([8, 10, 25, 27], fill=POTATO)
    d.ellipse([10, 12, 21, 21], fill=(216, 178, 92, 255))
    # manchas
    for cx, cy, r in ((12, 19, 2.2), (19, 22, 1.8), (20, 14, 1.6), (15, 24, 1.4)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=POTATO_D)
    # gosma toxica
    for cx, cy, r in ((11, 14, 1.6), (22, 17, 1.3), (17, 12, 1.1)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=TOXIC)
    # folha
    d.polygon([(16, 11), (21, 6), (24, 7), (19, 12)], fill=GREEN)
    return img


def icon_bota():
    img, d = canvas()
    # cano da bota
    d.rectangle([10, 5, 21, 20], fill=BLUE)
    d.rectangle([10, 5, 21, 8], fill=BLUE_D)
    d.rectangle([12, 8, 14, 20], fill=BLUE_L)
    # peito do pe
    d.rectangle([10, 18, 26, 24], fill=BLUE)
    d.rectangle([11, 19, 15, 21], fill=BLUE_L)
    # bico arredondado
    d.ellipse([21, 16, 28, 25], fill=BLUE)
    d.ellipse([22, 18, 26, 23], fill=BLUE_L)
    # sola
    d.rectangle([9, 24, 28, 27], fill=BLUE_D)
    d.rectangle([9, 6, 10, 27], fill=BLUE_D)
    # detalhe lateral
    d.rectangle([17, 11, 20, 14], fill=BLUE_D)
    d.rectangle([17, 12, 19, 13], fill=BLUE_L)
    return img


def _helmet(base, light, dark, face=None, crest=None):
    img, d = canvas()
    # cupula (semi circulo)
    d.pieslice([6, 6, 26, 26], start=180, end=360, fill=base)
    d.rectangle([6, 15, 26, 18], fill=base)
    # topo iluminado
    d.pieslice([9, 9, 23, 23], start=180, end=360, fill=light)
    d.rectangle([9, 14, 23, 16], fill=light)
    # aba / borda
    d.rectangle([6, 16, 26, 19], fill=dark)
    d.rectangle([9, 19, 23, 26], fill=base)
    d.rectangle([9, 24, 23, 26], fill=dark)
    # abertura do rosto
    d.rectangle([11, 19, 21, 25], fill=(34, 40, 44, 255))
    if crest:
        d.rectangle([15, 7, 17, 17], fill=crest)
    if face == "creeper":
        d.rectangle([12, 20, 14, 22], fill=GREEN_L)
        d.rectangle([18, 20, 20, 22], fill=GREEN_L)
        d.rectangle([15, 22, 17, 25], fill=GREEN_L)
        d.rectangle([13, 23, 15, 25], fill=GREEN_L)
        d.rectangle([17, 23, 19, 25], fill=GREEN_L)
    if face == "gem":
        d.rectangle([12, 20, 14, 23], fill=(255, 246, 214, 255))
        d.rectangle([18, 20, 20, 23], fill=(255, 246, 214, 255))
        d.polygon([(16, 20), (18, 23), (16, 25), (14, 23)], fill=(255, 214, 92, 255))
    return img


def icon_capacete_a():
    return _helmet(GREEN, GREEN_L, GREEN_D, face="creeper", crest=GREEN_D)


def icon_capacete_b():
    return _helmet(GOLD, GOLD_L, GOLD_D, face="gem", crest=GOLD_D)


def icon_dragao():
    img, d = canvas()
    # chifres
    d.polygon([(11, 12), (8, 4), (14, 9)], fill=PURPLE_D)
    d.polygon([(21, 12), (25, 4), (18, 9)], fill=PURPLE_D)
    # cranio
    d.polygon([(9, 10), (23, 10), (26, 17), (22, 21), (18, 25), (14, 25), (10, 21), (7, 17)], fill=PURPLE)
    d.polygon([(11, 11), (16, 10), (14, 20), (11, 17)], fill=PURPLE_L)
    # focinho
    d.polygon([(14, 22), (20, 22), (18, 28), (15, 28)], fill=PURPLE_D)
    # olhos
    d.rectangle([11, 15, 14, 18], fill=(255, 214, 64, 255))
    d.rectangle([19, 15, 22, 18], fill=(255, 214, 64, 255))
    d.rectangle([12, 16, 13, 17], fill=(40, 20, 50, 255))
    d.rectangle([20, 16, 21, 17], fill=(40, 20, 50, 255))
    # dentes
    d.polygon([(15, 26), (16, 29), (17, 26)], fill=WHITE)
    d.polygon([(18, 26), (19, 29), (20, 26)], fill=WHITE)
    return img


def icon_escudo():
    img, d = canvas()
    d.polygon([(7, 6), (25, 6), (25, 19), (16, 28), (7, 19)], fill=IRON)
    d.polygon([(9, 8), (23, 8), (23, 18), (16, 25), (9, 18)], fill=IRON_L)
    # borda
    d.line([(7, 6), (25, 6)], fill=IRON_D, width=3)
    d.line([(25, 6), (25, 19)], fill=IRON_D, width=2)
    # emblema
    d.polygon([(16, 10), (21, 15), (16, 22), (11, 15)], fill=GREEN_D)
    d.polygon([(16, 11), (19, 15), (16, 20), (13, 15)], fill=GREEN_L)
    # runas
    d.line([(10, 12), (10, 16)], fill=IRON_D, width=1)
    d.line([(22, 12), (22, 16)], fill=IRON_D, width=1)
    return img


def icon_bussola():
    img, d = canvas()
    d.ellipse([4, 4, 28, 28], fill=IRON_D)
    d.ellipse([6, 6, 26, 26], fill=GOLD_D)
    d.ellipse([8, 8, 24, 24], fill=(240, 240, 232, 255))
    # agulha grande vermelha/branca
    d.polygon([(16, 5), (21, 16), (16, 14), (11, 16)], fill=RED)
    d.polygon([(16, 27), (21, 16), (16, 18), (11, 16)], fill=WHITE)
    d.ellipse([14, 14, 18, 18], fill=GOLD_D)
    # anel externo
    d.ellipse([4, 4, 28, 28], outline=IRON_D)
    # argola
    d.rectangle([14, 0, 18, 5], fill=IRON_D)
    d.ellipse([13, 1, 19, 4], fill=IRON)
    return img


def icon_lampiao():
    img, d = canvas()
    # alca
    d.arc([11, 2, 21, 12], start=180, end=360, fill=IRON_D, width=2)
    # topo
    d.rectangle([10, 6, 22, 10], fill=IRON_D)
    d.rectangle([12, 4, 20, 7], fill=IRON)
    # corpo
    d.rectangle([10, 10, 22, 25], fill=TEAL_D)
    d.rectangle([12, 11, 20, 24], fill=TEAL)
    d.rectangle([13, 12, 16, 23], fill=TEAL_L)
    # chama
    d.ellipse([14, 16, 19, 23], fill=FIRE)
    d.ellipse([15, 18, 18, 22], fill=WHITE)
    # estrutura
    d.rectangle([15, 10, 17, 25], fill=IRON_D)
    d.rectangle([10, 14, 22, 15], fill=IRON_D)
    # base
    d.rectangle([9, 25, 23, 29], fill=IRON_D)
    d.rectangle([11, 25, 21, 27], fill=IRON)
    return img


def icon_pena():
    img, d = canvas()
    d.polygon([(24, 4), (28, 8), (14, 24), (8, 27), (10, 21)], fill=WHITE)
    d.polygon([(23, 7), (26, 9), (15, 22), (12, 24)], fill=(214, 216, 224, 255))
    # calamo
    d.line([(25, 7), (9, 26)], fill=(176, 180, 190, 255), width=2)
    # barbas
    for i in range(6):
        x = 22 - i * 2.6
        y = 9 + i * 2.6
        d.line([(x, y), (x - 3.2, y + 0.6)], fill=(226, 228, 236, 255), width=1)
        d.line([(x, y), (x - 0.4, y + 3.0)], fill=(200, 204, 214, 255), width=1)
    return img


def icon_picareta():
    img, d = canvas()
    # cabo
    d.line([(9, 26), (21, 12)], fill=WOOD_D, width=4)
    d.line([(9, 26), (21, 12)], fill=WOOD, width=2)
    # cabeca
    d.polygon([(7, 12), (12, 6), (21, 5), (27, 11), (22, 11), (16, 10), (11, 17), (9, 15)], fill=IRON)
    d.polygon([(9, 12), (13, 8), (20, 7), (24, 10), (17, 9), (12, 15)], fill=IRON_L)
    d.polygon([(7, 12), (9, 15), (10, 12)], fill=IRON_D)
    d.polygon([(27, 11), (24, 14), (24, 10)], fill=IRON_D)
    # amarra
    d.rectangle([14, 12, 17, 15], fill=WOOD_D)
    return img


def icon_pocao():
    img, d = canvas()
    # corpo
    d.polygon([(13, 10), (19, 10), (24, 16), (24, 26), (8, 26), (8, 16)], fill=GLASS)
    # liquido
    d.polygon([(9, 17), (23, 17), (23, 25), (9, 25)], fill=PURPLE)
    d.ellipse([9, 15, 23, 22], fill=PURPLE)
    d.ellipse([11, 20, 16, 25], fill=PURPLE_L)
    # gargalo
    d.rectangle([13, 8, 19, 12], fill=GLASS)
    # rolha
    d.rectangle([13, 4, 19, 9], fill=WOOD)
    d.rectangle([14, 5, 18, 7], fill=WOOD_D)
    # brilho do vidro
    d.line([(21, 12), (21, 20)], fill=WHITE, width=1)
    # bolhas
    d.ellipse([17, 21, 19, 23], fill=PURPLE_L)
    d.ellipse([19, 18, 21, 20], fill=PURPLE_L)
    return img


def icon_relogio():
    img, d = canvas()
    d.ellipse([5, 3, 27, 27], fill=GOLD_D)
    d.ellipse([7, 5, 25, 25], fill=GOLD)
    d.ellipse([9, 7, 23, 23], fill=(242, 244, 240, 255))
    # marcas
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        x0 = 16 + math.cos(a) * 6.0
        y0 = 16 + math.sin(a) * 6.0
        x1 = 16 + math.cos(a) * 7.2
        y1 = 16 + math.sin(a) * 7.2
        d.line([(x0, y0), (x1, y1)], fill=IRON_D, width=1)
    # ponteiros
    d.line([(16, 16), (16, 9)], fill=BLACK, width=2)
    d.line([(16, 16), (21, 20)], fill=BLACK, width=2)
    d.ellipse([14.5, 14.5, 17.5, 17.5], fill=GOLD_D)
    # botao de corda
    d.rectangle([14, 1, 18, 5], fill=GOLD_D)
    return img


def icon_tridente():
    img, d = canvas()
    # haste
    d.line([(16, 28), (16, 9)], fill=TEAL_D, width=4)
    d.line([(16, 28), (16, 9)], fill=TEAL, width=2)
    # ponta central
    d.polygon([(16, 2), (19, 10), (16, 13), (13, 10)], fill=TEAL_L)
    # pontas laterais
    d.polygon([(8, 6), (11, 6), (11, 14), (8, 13)], fill=TEAL)
    d.polygon([(21, 6), (24, 6), (24, 13), (21, 14)], fill=TEAL)
    d.polygon([(8, 6), (11, 2), (11, 7)], fill=TEAL_L)
    d.polygon([(24, 6), (21, 2), (21, 7)], fill=TEAL_L)
    # travessa
    d.rectangle([8, 14, 24, 17], fill=TEAL_D)
    d.rectangle([9, 14, 23, 15], fill=TEAL)
    # detalhe
    d.rectangle([15, 18, 17, 27], fill=TEAL_L)
    return img


ICONS = {
    "espada_do_cacador": icon_espada,
    "batata_do_bobo": icon_batata,
    "bota_lendaria": icon_bota,
    "capacete_gemeo_bern": icon_capacete_a,
    "capacete_gemeo_chip": icon_capacete_b,
    "dragao_lendario": icon_dragao,
    "escudo_lendario": icon_escudo,
    "bussola_lendaria": icon_bussola,
    "lampiao_lendario": icon_lampiao,
    "pena_lendaria": icon_pena,
    "picareta_lendaria": icon_picareta,
    "pocao_lendaria": icon_pocao,
    "relogio_lendario": icon_relogio,
    "tridente_lendario": icon_tridente,
}


# ---------------------------------------------------------------- armadura
def armor_layer(base, light, dark, pattern="shell"):
    """Camada 1 de armadura (64x32). Cabeca ocupa a regiao 0,0 - 32,16."""
    img = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 31, 15], fill=base)
    if pattern == "shell":
        # placas de casco
        for y in range(0, 16, 4):
            for x in range(0, 32, 8):
                d.rectangle([x, y, x + 6, y + 2], fill=dark)
                d.rectangle([x + 1, y + 1, x + 5, y + 2], fill=light)
        for y in range(0, 16, 4):
            d.rectangle([0, y, 31, y], fill=dark)
        d.rectangle([0, 0, 31, 1], fill=dark)
    else:
        d.rectangle([0, 0, 31, 1], fill=dark)
        d.rectangle([0, 0, 1, 15], fill=dark)
        d.rectangle([30, 0, 31, 15], fill=dark)
        d.rectangle([0, 14, 31, 15], fill=dark)
        for x in range(4, 32, 8):
            d.rectangle([x, 2, x + 3, 13], fill=dark)
            d.rectangle([x + 1, 3, x + 2, 12], fill=light)
    # face frontal (8..16) com detalhe diferente para nao ficar chapado
    d.rectangle([8, 8, 15, 15], fill=light)
    d.rectangle([8, 8, 15, 9], fill=dark)
    return img


def pack_icon():
    size = 128
    img = Image.new("RGBA", (size, size), (18, 14, 22, 255))
    d = ImageDraw.Draw(img)
    for y in range(size):
        t = y / (size - 1)
        c = (int(38 + 60 * t), int(20 + 10 * t), int(40 + 20 * t), 255)
        d.line([(0, y), (size, y)], fill=c)
    # brilho diagonal
    d.polygon([(0, 96), (128, 20), (128, 44), (0, 120)], fill=(255, 190, 90, 28))
    tiles = [
        ("espada_do_cacador", 12, 12),
        ("dragao_lendario", 68, 12),
        ("lampiao_lendario", 12, 68),
        ("relogio_lendario", 68, 68),
    ]
    for name, x, y in tiles:
        icon = Image.open(os.path.join(ITEMS_DIR, name + ".png")).convert("RGBA")
        icon = icon.resize((48, 48), Image.NEAREST)
        d.rectangle([x - 4, y - 4, x + 51, y + 51], fill=(10, 8, 12, 200),
                    outline=(240, 200, 90, 255), width=2)
        img.alpha_composite(icon, (x, y))
    return img


def main():
    os.makedirs(ITEMS_DIR, exist_ok=True)
    for name, fn in ICONS.items():
        save(fn(), name)
        print("item  ->", name + ".png")

    os.makedirs(ARMOR_DIR, exist_ok=True)
    a = armor_layer(GREEN, GREEN_L, GREEN_D, "shell")
    b = armor_layer(GOLD, GOLD_L, GOLD_D, "gem")
    c = armor_layer(BLUE, BLUE_L, BLUE_D, "gem")
    a.save(os.path.join(ARMOR_DIR, "capacete_bern_layer_1.png"))
    b.save(os.path.join(ARMOR_DIR, "capacete_chip_layer_1.png"))
    c.save(os.path.join(ARMOR_DIR, "bota_layer_1.png"))
    print("armor -> capacete_bern_layer_1.png, capacete_chip_layer_1.png, bota_layer_1.png")

    icon = pack_icon()
    icon.save(os.path.join(RP, "pack_icon.png"))
    icon.save(os.path.join(BP, "pack_icon.png"))
    print("pack  -> pack_icon.png")


if __name__ == "__main__":
    main()
