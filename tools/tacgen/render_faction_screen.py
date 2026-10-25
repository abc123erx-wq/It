"""Gera docs/faccao_tela.png — mock da tela de escolha de lado mostrada no jogo.

A tela real é um ActionFormData do Bedrock com dois botões-imagem; este render
reproduz o mesmo layout (card escuro dividido, azul POLICIAL / vermelho LADRÃO,
título ESCOLHA SEU LADO e subtítulo LEI OU LIBERDADE?) para documentação.
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UI = os.path.join(ROOT, "out", "TacGuns(R)", "textures", "ui")
OUT = os.path.join(ROOT, "docs", "faccao_tela.png")

FONTES = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
          "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
          "C:/Windows/Fonts/arialbd.ttf")


def fonte(tam):
    for caminho in FONTES:
        if os.path.exists(caminho):
            return ImageFont.truetype(caminho, tam)
    return ImageFont.load_default()


def texto_centro(d, cx, y, txt, tam, cor, esp=0):
    f = fonte(tam)
    for dx in range(-esp, esp + 1):
        for dy in range(-esp, esp + 1):
            d.text((cx + dx, y + dy), txt, font=f, fill=cor, anchor="ma")


def main():
    largura, altura = 960, 560
    img = Image.new("RGBA", (largura, altura), (10, 12, 16, 255))
    d = ImageDraw.Draw(img)

    # fundo: gradiente escuro + linhas de "madeira/metal"
    for y in range(altura):
        tom = 10 + int(8 * (y / altura))
        d.line([(0, y), (largura, y)], fill=(tom, tom + 2, tom + 6, 255))
    for x in range(0, largura, 48):
        d.line([(x, 0), (x, altura)], fill=(18, 20, 26, 255))

    # painel
    d.rounded_rectangle([38, 26, largura - 38, altura - 26], radius=22,
                        fill=(16, 18, 24, 250), outline=(58, 62, 74, 255), width=3)

    # cabeçalho
    d.rectangle([40, 28, largura - 40, 108], fill=(24, 26, 34, 255))
    texto_centro(d, largura // 2, 34, "ESCOLHA SEU LADO", 40, (240, 242, 248, 255), 2)
    texto_centro(d, largura // 2, 80, "LEI OU LIBERDADE?", 20, (150, 154, 168, 255), 1)
    d.line([(70, 110), (largura - 70, 110)], fill=(58, 62, 74, 255), width=2)

    # cards
    policial = Image.open(os.path.join(UI, "policial.png")).resize((330, 330))
    ladrao = Image.open(os.path.join(UI, "ladrao.png")).resize((330, 330))
    esq, topo = 96, 132
    dir_ = largura - 96 - 330
    for card, x, cor in ((policial, esq, (58, 138, 226, 255)),
                         (ladrao, dir_, (214, 62, 58, 255))):
        d.rounded_rectangle([x - 8, topo - 8, x + 338, topo + 338], radius=26,
                            fill=(8, 10, 14, 255), outline=cor, width=3)
        img.paste(card, (x, topo), card)

    # divisor + "vs"
    meio = largura // 2
    d.line([(meio, 132), (meio, 470)], fill=(70, 74, 86, 255), width=2)
    d.ellipse([meio - 26, 292, meio + 26, 344], fill=(16, 18, 24, 255),
              outline=(120, 124, 136, 255), width=2)
    texto_centro(d, meio, 300, "VS", 22, (220, 222, 230, 255))

    # rodapé
    texto_centro(d, largura // 2, 486,
                 "Cada lado tem arsenal, economia e táticas próprias — "
                 "armas do lado oposto não disparam", 15, (150, 154, 168, 255))
    texto_centro(d, largura // 2, 510,
                 "/scriptevent tac_guns:faccao  ·  /scriptevent tac_guns:loja  ·  "
                 "/scriptevent tac_guns:info", 14, (110, 114, 126, 255))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.convert("RGB").save(OUT)
    print("mock ->", OUT)


if __name__ == "__main__":
    main()
