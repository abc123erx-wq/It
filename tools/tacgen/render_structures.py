"""Pré-visualização das estruturas de /function (mapa de topo + corte).

Lê os `.mcfunction` gerados em `out/TacGuns(B)/functions/<nome>/` na ordem em que
o master chama as partes, aplica os `/fill` e desenha:
  - mapa visto de cima (bloco de maior y em cada coluna)
  - corte vertical na linha z escolhida

Salva `docs/estrutura_policial.png` e `docs/estrutura_favela.png`.
"""
import os
import re
import sys
from collections import OrderedDict

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tacgen import structures as st  # noqa: E402

FUNCOES = os.path.join(ROOT, "out", "TacGuns(B)", "functions")
DOCS = os.path.join(ROOT, "docs")

CORES = {
    "gray_concrete": (86, 90, 96), "white_concrete": (206, 208, 206),
    "light_blue_concrete": (88, 166, 216), "blue_concrete": (46, 82, 168),
    "black_concrete": (24, 26, 30), "red_concrete": (168, 48, 44),
    "lime_concrete": (104, 176, 46), "yellow_concrete": (238, 196, 62),
    "orange_concrete": (222, 128, 34), "brown_concrete": (114, 72, 44),
    "purple_concrete": (110, 60, 168), "cyan_concrete": (32, 134, 148),
    "polished_andesite": (138, 138, 136), "smooth_stone": (166, 166, 164),
    "stone": (128, 128, 128), "stone_bricks": (124, 124, 124),
    "quartz_block": (236, 230, 226), "chiseled_quartz_block": (230, 226, 220),
    "bricks": (150, 84, 68), "mud_bricks": (132, 102, 74),
    "terracotta": (152, 94, 68), "white_terracotta": (210, 178, 162),
    "orange_terracotta": (162, 84, 38), "red_terracotta": (142, 62, 46),
    "gray_terracotta": (58, 58, 60),
    "oak_planks": (168, 132, 80), "dark_oak_planks": (66, 44, 22),
    "jungle_planks": (160, 116, 82),
    "glass": (190, 216, 226), "glass_pane": (190, 216, 226),
    "iron_bars": (120, 124, 130), "iron_block": (200, 200, 204),
    "gold_block": (246, 208, 62), "sea_lantern": (222, 236, 232),
    "lantern": (206, 168, 96), "torch": (232, 190, 96),
    "coarse_dirt": (122, 92, 62), "dirt": (116, 86, 58),
    "dirt_path": (150, 118, 74), "gravel": (136, 130, 128),
    "sand": (222, 208, 158), "water": (52, 96, 200),
    "white_wool": (232, 232, 232), "red_wool": (162, 44, 44),
    "blue_wool": (54, 62, 152), "green_wool": (86, 116, 44),
    "black_wool": (28, 28, 32), "light_gray_wool": (160, 160, 158),
    "pink_wool": (232, 156, 172),
    "barrel": (140, 108, 66), "chest": (150, 116, 56), "crafting_table": (128, 88, 52),
    "furnace": (110, 110, 112), "blast_furnace": (96, 96, 98),
    "smithing_table": (62, 68, 82), "grindstone": (128, 118, 104),
    "anvil": (74, 74, 78), "cauldron": (66, 66, 70),
    "scaffolding": (188, 166, 96), "oak_fence": (166, 130, 78),
    "spruce_fence": (108, 78, 48), "campfire": (176, 106, 48),
    "jukebox": (128, 88, 56), "noteblock": (140, 104, 68), "magma": (156, 84, 36),
    "brown_terracotta": (76, 50, 36), "yellow_wool": (250, 200, 62),
}

VAZIO = (12, 14, 18)


def cor(bloco):
    return CORES.get(bloco, (150, 40, 150))


def coord(token):
    token = token.strip()
    if token in ("~", "~0", ""):
        return 0
    if token.startswith("~"):
        return int(token[1:])
    return int(token)


def ler_parte(path):
    """Aplica os comandos de uma parte numa grade esparsa."""
    grade = {}
    for linha in open(path, encoding="utf-8").read().splitlines():
        linha = linha.strip()
        if linha.startswith("fill "):
            campos = linha.split(" ")
            x0, y0, z0 = (coord(c) for c in campos[1:4])
            x1, y1, z1 = (coord(c) for c in campos[4:7])
            bloco = campos[7]
            if len(campos) == 9:
                continue          # hollow/outline não usados no render
            for x in range(min(x0, x1), max(x0, x1) + 1):
                for y in range(min(y0, y1), max(y0, y1) + 1):
                    for z in range(min(z0, z1), max(z0, z1) + 1):
                        if bloco == "air":
                            grade.pop((x, y, z), None)
                        else:
                            grade[(x, y, z)] = bloco
        elif linha.startswith("setblock "):
            campos = linha.split(" ")
            x, y, z = (coord(c) for c in campos[1:4])
            bloco = campos[4]
            if bloco == "air":
                grade.pop((x, y, z), None)
            else:
                grade[(x, y, z)] = bloco
    return grade


def desenhar(nome, partes, z_corte=0, escala=6):
    grade = {}
    for parte in sorted(partes):
        grade.update(ler_parte(os.path.join(FUNCOES, nome, parte + ".mcfunction")))

    xs = [p[0] for p in grade]
    zs = [p[2] for p in grade]
    ys = [p[1] for p in grade]
    x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)
    y0, y1 = min(ys), max(ys)
    largura = (x1 - x0 + 1) * escala
    altura_topo = (z1 - z0 + 1) * escala
    altura_corte = (y1 - y0 + 1) * escala
    margem = 26
    img = Image.new("RGBA", (largura + 2 * margem,
                             altura_topo + altura_corte + 3 * margem + 8),
                    (14, 16, 20, 255))
    d = ImageDraw.Draw(img)

    try:
        fonte = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        fonte_p = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    except OSError:
        fonte = fonte_p = ImageFont.load_default()

    d.text((margem, 8), f"/function {nome} — vista de cima", font=fonte,
           fill=(236, 238, 244))

    # topo
    for (x, y, z), bloco in grade.items():
        base = cor(bloco)
        topo_atual = grade.get((x, y + 1, z))
        if topo_atual is not None and topo_atual != "air":
            continue
        px = margem + (x - x0) * escala
        py = margem + (z - z0) * escala
        brilho = 1.0 + (y - y0) * 0.02
        c = tuple(min(255, int(min(255, v) * brilho)) for v in base)
        d.rectangle([px, py, px + escala - 1, py + escala - 1], fill=c)

    # corte
    topo_corte = margem + altura_topo + margem
    d.text((margem, topo_corte - 20), f"corte em z = {z_corte}", font=fonte_p,
           fill=(170, 174, 186))
    for (x, y, z), bloco in grade.items():
        if z != z_corte:
            continue
        px = margem + (x - x0) * escala
        py = topo_corte + (y1 - y) * escala
        d.rectangle([px, py, px + escala - 1, py + escala - 1], fill=cor(bloco))

    d.text((margem, topo_corte + altura_corte + 8),
           f"{len(grade)} blocos · {nome}", font=fonte_p, fill=(150, 154, 166))

    destino = os.path.join(DOCS, f"estrutura_{nome}.png")
    os.makedirs(DOCS, exist_ok=True)
    img.convert("RGB").save(destino)
    print("->", destino, img.size)


def main():
    pol = st.base_policial()
    fav = st.favela()
    desenhar("policial", pol, z_corte=8)
    desenhar("favela", fav, z_corte=0)


if __name__ == "__main__":
    main()
