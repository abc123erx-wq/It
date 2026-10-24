#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera docs/preview-itens.png: uma imagem de divulgacao com os 14 itens do addon.
Uso: python3 tools/gen_preview.py
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, "src", "resource_pack")
ITEMS_DIR = os.path.join(RP, "textures", "items")
DOCS = os.path.join(ROOT, "docs")

ORDEM = [
    ("espada_do_cacador", "Espada do Caçador", "NaitPlayer"),
    ("tridente_lendario", "Tridente Lendário", "NaitPlayer"),
    ("batata_do_bobo", "Batata do Bobo", "Caduxinn"),
    ("dragao_lendario", "Dragão Lendário", "Caduxinn"),
    ("bota_lendaria", "Bota Lendária", "0nerb"),
    ("capacete_gemeo_bern", "Capacete dos Gêmeos · Bern", "Bern"),
    ("capacete_gemeo_chip", "Capacete dos Gêmeos · Chip", "Chip"),
    ("escapamento", "", ""),
    ("escudo_lendario", "Escudo Lendário", "MucaHD"),
    ("bussola_lendaria", "Bússola Lendária", "GeleiaPlays"),
    ("lampiao_lendario", "Lampião Lendário", "Tonigonn"),
    ("pena_lendaria", "Pena Lendária", "Feuripe"),
    ("picareta_lendaria", "Picareta Lendária", "Pedrux"),
    ("pocao_lendaria", "Poção Lendária", "Fixz"),
    ("relogio_lendario", "Relógio Lendário", "Ligonz"),
]

COLS = 5
CELL_W = 250
CELL_H = 196
PAD = 34
HEADER = 128
FOOTER = 54


def main():
    os.makedirs(DOCS, exist_ok=True)
    linhas = (len(ORDEM) + COLS - 1) // COLS
    w = COLS * CELL_W + PAD * 2
    h = HEADER + linhas * CELL_H + FOOTER

    img = Image.new("RGBA", (w, h), (16, 13, 20, 255))
    d = ImageDraw.Draw(img)

    # fundo em degrade + brilho central
    for y in range(h):
        t = y / max(h - 1, 1)
        d.line([(0, y), (w, y)], fill=(int(22 + 46 * t), int(14 + 12 * t), int(26 + 26 * t), 255))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([w * 0.18, HEADER * 0.1, w * 0.82, h * 0.95], fill=(255, 150, 40, 26))
    img.alpha_composite(glow.filter(__import__("PIL.ImageFilter", fromlist=["ImageFilter"]).GaussianBlur(70)))

    f_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
    f_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    f_nome = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
    f_dono = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    f_rodape = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)

    d.text((PAD, 30), "ITENS LENDÁRIOS", font=f_titulo, fill=(255, 205, 96, 255))
    d.text((PAD + 2, 86), "Creative Squad · addon para Minecraft Bedrock 26.52",
           font=f_sub, fill=(206, 196, 214, 255))

    def wrap(texto, fonte, largura):
        palavras = texto.split(" ")
        linhas_txt, atual = [], ""
        for palavra in palavras:
            teste = (atual + " " + palavra).strip()
            if d.textlength(teste, font=fonte) <= largura:
                atual = teste
            else:
                if atual:
                    linhas_txt.append(atual)
                atual = palavra
        if atual:
            linhas_txt.append(atual)
        return linhas_txt

    for i, (tex, nome, dono) in enumerate(ORDEM):
        if not nome:
            continue
        cx = PAD + (i % COLS) * CELL_W
        cy = HEADER + (i // COLS) * CELL_H

        d.rounded_rectangle([cx, cy, cx + CELL_W - 18, cy + CELL_H - 16], radius=10,
                            fill=(30, 24, 36, 235), outline=(96, 78, 112, 255), width=2)

        icon = Image.open(os.path.join(ITEMS_DIR, tex + ".png")).convert("RGBA")
        icon = icon.resize((72, 72), Image.NEAREST)
        icone_x = cx + (CELL_W - 18 - 80) // 2
        d.rounded_rectangle([icone_x, cy + 10, icone_x + 80, cy + 90], radius=6,
                            fill=(12, 9, 16, 255), outline=(236, 199, 96, 255), width=2)
        img.alpha_composite(icon, (icone_x + 4, cy + 14))

        fontes = wrap(nome, f_nome, CELL_W - 46)
        y = cy + 100
        for linha in fontes[:2]:
            largura_txt = d.textlength(linha, font=f_nome)
            d.text((cx + (CELL_W - 18 - largura_txt) / 2, y), linha,
                   font=f_nome, fill=(246, 240, 250, 255))
            y += 22

        dono_txt = "portador: " + dono
        largura_dono = d.textlength(dono_txt, font=f_dono)
        d.text((cx + (CELL_W - 18 - largura_dono) / 2, cy + CELL_H - 40), dono_txt,
               font=f_dono, fill=(170, 154, 188, 255))

    d.text((PAD, h - FOOTER + 12),
           "14 itens · habilidades reais · inquebráveis · receitas próprias",
           font=f_rodape, fill=(172, 158, 188, 255))

    out = os.path.join(DOCS, "preview-itens.png")
    img.convert("RGB").save(out, quality=92)
    print("preview ->", os.path.relpath(out, ROOT))


if __name__ == "__main__":
    main()
