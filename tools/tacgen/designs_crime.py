"""Desenhos voxel das armas de faccao / crime organizado.

Mesmo espaco de autoria das demais armas: boca do cano em z=0, alma em y=0,
z crescendo em direcao a coronha. A estetica e proposital: metal oxidado,
fita isolante, marcas de faccao e pecas improvisadas.
"""
from .designs import (butt_stock, curved_mag, optic, rail, slanted_grip,
                      trigger_guard)
from .voxel import Design


def ak47():
    """AK-47 / AKM / Tipo 56 - 7,62x39mm, madeira e ferrugem."""
    d = Design("ak47", 36.0, "AK-47")
    # cano + massa de mira
    d.tube("gunmetal", 0, 0, 0.6, 11.0, 0.78)
    d.box("rust", -0.95, -0.95, 0.0, 0.95, 0.95, 1.1)      # boca oxidada
    d.box("gunmetal", -0.95, -1.0, 9.4, 0.95, 1.0, 11.2)
    d.box("gunmetal", -0.4, 1.0, 9.6, 0.4, 2.6, 10.3)
    d.box("black", -0.25, 2.2, 9.7, 0.25, 2.8, 10.1)
    # tubo de gas + bloco
    d.tube("black", 0, 1.75, 5.0, 11.4, 0.5)
    d.box("gunmetal", -0.8, 1.0, 11.0, 0.8, 2.2, 12.2)
    # guarda-mao de madeira
    d.box("wood2", -1.55, -2.1, 3.2, 1.55, 1.1, 11.4)
    d.box("wood", -1.35, 1.1, 3.6, 1.35, 1.9, 10.8)
    # fita isolante prendendo o guarda-mao
    d.box("tape", -1.65, -2.2, 6.4, 1.65, 1.2, 7.3)
    d.box("tape", -1.65, -2.2, 9.8, 1.65, 1.2, 10.4)
    # receptor + tampa de ferrolho
    d.box("gunmetal", -1.5, -1.9, 11.0, 1.5, 1.7, 24.0)
    d.box("rust", -1.52, -1.4, 12.2, 1.52, 1.2, 13.0)        # mancha de ferrugem
    d.box("rust", -1.52, -1.8, 20.0, 1.52, 1.0, 21.0)
    d.box("black", -1.35, 1.7, 11.4, 1.35, 2.35, 23.4)
    d.box("gunmetal", -0.5, 2.35, 12.0, 0.5, 2.7, 14.0)          # alca de mira
    # alavanca de manejo (lado direito) + seletor
    d.box("steel", 1.5, 0.2, 16.2, 2.6, 1.1, 17.4)
    d.box("black", 1.5, -1.2, 13.4, 2.1, 0.2, 15.4)
    # gatilho + guarda-mato
    trigger_guard(d, 15.0, 19.0, -1.9, -3.6, half_w=1.25, mat="black")
    # empunhadura e coronha de madeira
    slanted_grip(d, 19.2, 22.4, -1.9, -6.0, half_w=1.3, mat="wood2", lean=2.0)
    butt_stock(d, 24.0, 35.0, -2.2, 1.4, half_w=1.55, mat="wood2")
    d.box("wood", -1.2, -1.0, 25.0, 1.2, 0.9, 33.6)
    # marcas de faccao gravadas na coronha
    d.box("engrave", -0.55, -0.4, 29.0, 0.55, 0.35, 31.4)
    # carregador curvo grande
    curved_mag(d, 17.6, -1.9, 9.5, 1.15, curve=3.4, mat="gunmetal", segs=4,
               seg_h=2.3, taper=0.92, seg_z=6.0)
    d.box("tape", -1.3, -4.0, 18.4, 1.3, -1.9, 19.2, bone="mag")
    d.locator("shell", 1.0, 0.4, 15.0)
    return d


def ak_short():
    """AK curta (AK-74U / Hellpup / M92) - sem coronha, cano serrado."""
    d = Design("ak_short", 27.0, "AK curta")
    d.tube("gunmetal", 0, 0, 0.4, 6.0, 0.8)
    d.box("black", -1.0, -1.0, 0.0, 1.0, 1.0, 1.2)
    d.box("gunmetal", -0.9, -0.9, 4.6, 0.9, 1.2, 6.2)
    d.box("gunmetal", -0.4, 1.2, 4.8, 0.4, 2.6, 5.4)
    d.tube("black", 0, 1.8, 3.0, 7.0, 0.45)
    d.box("wood2", -1.5, -2.0, 1.8, 1.5, 1.1, 7.4)
    d.box("tape", -1.6, -2.1, 2.4, 1.6, 1.2, 3.2)
    d.box("gunmetal", -1.45, -1.9, 7.0, 1.45, 1.7, 17.6)
    d.box("black", -1.3, 1.7, 7.2, 1.3, 2.3, 17.0)
    d.box("steel", 1.45, 0.2, 10.6, 2.4, 1.0, 11.6)
    trigger_guard(d, 10.0, 13.6, -1.9, -3.5, half_w=1.2, mat="black")
    slanted_grip(d, 13.8, 16.8, -1.9, -5.8, half_w=1.25, mat="tape", lean=1.8)
    # coronha de arame dobrada sobre o receptor
    d.box("black", -0.35, 1.4, 17.6, 0.35, 2.1, 24.6)
    d.box("black", -1.3, 0.9, 23.8, 1.3, 2.1, 25.0)
    d.box("engrave", -0.5, -0.6, 13.4, 0.5, 0.3, 14.6)
    curved_mag(d, 11.8, -1.9, 8.0, 1.1, curve=2.8, mat="gunmetal", segs=3,
               seg_h=2.3, taper=0.92, seg_z=5.4)
    d.locator("shell", 1.0, 0.4, 9.0)
    return d


def sks():
    """Carabina SKS - madeira clara, ferrolho exposto, sem carregador destacavel."""
    d = Design("sks", 35.0, "SKS")
    d.tube("gunmetal", 0, 0, 0.6, 16.0, 0.7)
    d.box("black", -0.9, -0.8, 14.2, 0.9, 1.0, 16.4)
    d.box("gunmetal", -0.35, 1.0, 14.4, 0.35, 2.4, 15.2)
    d.box("wood2", -1.5, -2.2, 2.0, 1.5, 1.0, 17.0)
    d.box("wood", -1.25, 1.0, 4.0, 1.25, 1.8, 16.0)
    d.box("tape", -1.6, -2.3, 8.0, 1.6, 1.1, 8.8)
    d.box("gunmetal", -1.35, -1.8, 16.6, 1.35, 1.6, 25.0)
    d.box("black", -0.55, 1.6, 17.2, 0.55, 2.2, 19.0)
    trigger_guard(d, 18.6, 22.0, -1.8, -3.4, half_w=1.15, mat="black")
    slanted_grip(d, 21.6, 24.6, -1.8, -5.4, half_w=1.2, mat="wood2", lean=1.8)
    butt_stock(d, 25.0, 34.6, -2.1, 1.2, half_w=1.5, mat="wood2")
    # ferrolho exposto + pente fixo
    d.box("steel", 1.35, 0.4, 18.0, 2.3, 1.2, 19.6)
    d.box("gunmetal", -1.1, -4.6, 19.4, 1.1, -1.8, 23.0, bone="mag")
    d.box("engrave", -0.5, -0.5, 28.6, 0.5, 0.4, 30.6)
    d.locator("shell", 1.2, 0.4, 21.0)
    return d


def tec9():
    """Intratec TEC-9 / DC-9 - tubo ventilado, carregador a frente do gatilho."""
    d = Design("tec9", 25.0, "TEC-9")
    # tubo ventilado (shroud perfurado)
    d.tube("tape", 0, 0.2, 0.0, 7.6, 0.95)
    for i in range(4):
        z = 1.4 + i * 1.5
        d.box("black", -1.0, 0.9, z, 1.0, 1.15, z + 0.55)
    d.box("gunmetal", -1.05, -1.0, 7.0, 1.05, 1.2, 8.2)
    # receptor quadrado
    d.box("gunmetal", -1.15, -1.3, 7.6, 1.15, 1.4, 19.2)
    d.box("black", -1.0, 1.4, 8.0, 1.0, 1.9, 18.4)
    d.box("tape", -1.25, -1.4, 12.4, 1.25, 1.5, 13.4)
    # mira traseira improvisada
    d.box("black", -0.8, 1.9, 15.6, 0.8, 2.6, 16.4)
    d.box("engrave", -0.25, 2.1, 15.8, 0.25, 2.4, 16.2)
    # gatilho + guarda-mato
    trigger_guard(d, 10.4, 14.2, -1.3, -3.2, half_w=1.0, mat="black")
    # empunhadura
    slanted_grip(d, 16.4, 19.4, -1.3, -5.6, half_w=1.15, mat="tape", lean=1.6)
    # carregador a frente do guarda-mato
    d.box("gunmetal", -0.95, -7.6, 9.0, 0.95, -1.2, 12.2, bone="mag")
    d.box("tape", -1.1, -6.8, 8.9, 1.1, -1.3, 9.4, bone="mag")
    d.box("black", -1.1, -8.0, 9.0, 1.1, -7.3, 12.4, bone="mag")
    # alca de manejo superior
    d.box("steel", -0.3, 1.9, 9.0, 0.3, 2.7, 12.6)
    d.locator("shell", 1.0, 0.6, 11.0)
    return d


def mac10():
    """MAC-10 / MAC-11 - caixa compacta, carregador no punho, coronha de arame."""
    d = Design("mac10", 19.0, "MAC-10")
    d.tube("gunmetal", 0, 0.3, 0.0, 3.0, 0.72)
    d.box("black", -0.9, -0.9, 2.4, 0.9, 1.0, 3.6)
    # corpo em U estampado
    d.box("gunmetal", -1.3, -2.0, 3.0, 1.3, 2.0, 13.4)
    d.box("black", -1.15, 2.0, 3.4, 1.15, 2.5, 12.6)
    d.box("tape", -1.4, -2.1, 5.0, 1.4, 2.1, 6.2)
    d.box("tape", -1.4, -2.1, 9.0, 1.4, 2.1, 9.8)
    # alca de manejo no topo
    d.box("steel", -0.35, 2.5, 4.2, 0.35, 3.4, 8.6)
    d.box("black", -0.6, 3.4, 4.4, 0.6, 3.9, 8.4)
    d.box("engrave", -0.4, -0.8, 10.6, 0.4, 0.2, 12.2)
    # punho + carregador dentro dele
    slanted_grip(d, 10.4, 13.6, -2.0, -6.4, half_w=1.15, mat="tape", lean=1.2)
    d.box("black", -0.85, -9.4, 10.2, 0.85, -6.2, 13.2, bone="mag")
    # coronha de arame recolhida
    d.box("black", -1.2, -1.0, 13.4, 1.2, -0.4, 14.4)
    d.box("black", -0.3, -1.2, 13.6, 0.3, 1.4, 17.6)
    d.box("black", -1.2, 0.6, 17.2, 1.2, 2.2, 18.2)
    d.locator("shell", 1.0, 1.0, 7.0)
    return d


def uzi():
    """UZI - receptor quadrado, carregador no punho, coronha dobrável."""
    d = Design("uzi", 22.0, "UZI")
    d.tube("gunmetal", 0, 0.2, 0.0, 5.0, 0.7)
    d.box("black", -0.85, -0.85, 4.2, 0.85, 1.0, 5.4)
    d.box("gunmetal", -1.3, -2.2, 4.6, 1.3, 2.2, 15.0)
    d.box("black", -1.15, 2.2, 5.0, 1.15, 2.7, 14.2)
    d.box("tape", -1.4, -2.3, 6.4, 1.4, 2.3, 7.3)
    d.box("black", -0.35, 2.7, 6.0, 0.35, 3.3, 8.6)      # alca de mira
    d.box("steel", 1.3, 0.4, 9.0, 2.2, 1.2, 10.4)         # alavanca
    trigger_guard(d, 11.2, 14.0, -2.2, -3.8, half_w=1.1, mat="black")
    slanted_grip(d, 14.0, 16.8, -2.2, -6.6, half_w=1.2, mat="tape", lean=1.4)
    d.box("black", -0.9, -10.0, 13.6, 0.9, -6.4, 16.8, bone="mag")
    d.box("engrave", -0.5, -1.0, 11.0, 0.5, 0.0, 12.6)
    # coronha de arame
    d.box("black", -0.3, -1.6, 15.0, 0.3, 0.6, 20.6)
    d.box("black", -1.2, -1.8, 19.8, 1.2, 1.0, 21.0)
    d.locator("shell", 1.1, 1.0, 9.0)
    return d


def kit_roni():
    """Pistola dentro do kit Roni: chassi com coronha e trilhos."""
    d = Design("kit_roni", 29.0, "Glock + Kit Roni")
    # pistola interna
    d.box("tape", -0.85, -0.2, 4.0, 0.85, 1.5, 15.4)      # ferrolho
    d.box("black", -0.55, -1.0, 4.2, 0.55, -0.1, 13.0)    # cano visivel
    d.box("gunmetal", -0.9, 1.5, 5.0, 0.9, 1.8, 14.4)         # plano de mira
    # chassi do kit
    d.box("tape", -1.35, -2.6, 3.0, 1.35, 2.2, 20.6)
    d.box("black", -1.2, -3.0, 4.0, 1.2, -2.4, 19.0)
    d.box("tape", -1.45, -2.7, 8.0, 1.45, 2.3, 9.0)
    # trilho superior + alca
    rail(d, 9.5, 16.5, 2.2, half_w=1.0, teeth=5, mat="black")
    d.box("engrave", -0.5, -1.2, 16.4, 0.5, -0.2, 18.0)
    # empunhadura da pistola + carregador
    slanted_grip(d, 15.4, 18.6, -2.6, -7.0, half_w=1.1, mat="tape", lean=1.4)
    d.box("black", -0.85, -8.0, 15.2, 0.85, -6.6, 18.4, bone="mag")
    # coronha dobrável do kit
    d.box("black", -0.35, -1.0, 20.4, 0.35, 0.4, 27.6)
    d.box("tape", -1.4, -2.4, 26.8, 1.4, 1.2, 28.4)
    # carregador extra preso com fita
    d.box("gunmetal", -0.8, -6.4, 20.8, 0.8, -2.0, 23.6, bone="mag")
    d.locator("shell", 1.2, 0.8, 12.0)
    return d


def ghost_ar():
    """AR-15 'fantasma' / FGC-9: receptor impresso, juncoes com fita, sem trilho."""
    d = Design("ghost_ar", 31.0, "AR fantasma")
    d.tube("tape", 0, 0.2, 0.0, 12.0, 0.72)
    d.box("black", -0.85, -0.85, 11.4, 0.85, 1.0, 12.8)
    # guarda-mao impresso (bloco reto, sem ventilacao)
    d.box("tape", -1.45, -1.7, 3.0, 1.45, 1.3, 12.2)
    d.box("black", -1.55, -1.8, 6.6, 1.55, 1.4, 7.6)
    d.box("black", -1.55, -1.8, 10.0, 1.55, 1.4, 10.8)
    # receptor superior/inferior retos
    d.box("tape", -1.3, -1.7, 12.0, 1.3, 1.7, 23.4)
    d.box("black", -1.15, 1.7, 12.4, 1.15, 2.2, 22.6)
    d.box("black", -0.9, 2.2, 12.8, 0.9, 2.9, 14.4)
    # parafusos e fita na juncao
    d.box("engrave", -1.4, -1.0, 14.0, 1.4, 0.6, 14.8)
    d.box("tape", -1.4, -1.8, 17.6, 1.4, 1.8, 18.4)
    trigger_guard(d, 17.0, 20.6, -1.7, -3.4, half_w=1.15, mat="black")
    slanted_grip(d, 20.4, 23.4, -1.7, -5.8, half_w=1.2, mat="tape", lean=1.8)
    # coronha impressa macica
    d.box("tape", -1.15, -1.6, 23.2, 1.15, 1.4, 28.0)
    d.box("black", -1.4, -2.2, 27.4, 1.4, 1.6, 29.4)
    # carregador reto
    d.box("gunmetal", -1.0, -7.2, 18.4, 1.0, -1.7, 21.6, bone="mag")
    d.box("tape", -1.1, -4.0, 18.3, 1.1, -1.8, 18.9, bone="mag")
    d.box("engrave", -0.5, -5.6, 18.4, 0.5, -4.4, 21.6, bone="mag")
    d.locator("shell", 1.1, 0.6, 16.0)
    return d


def sawedoff():
    """Espingarda serrada de dois canos - 12 gauge, coronha removida."""
    d = Design("sawedoff", 20.0, "Espingarda serrada")
    # dois canos
    d.tube("gunmetal", -0.78, 0.1, 0.0, 10.4, 0.62)
    d.tube("gunmetal", 0.78, 0.1, 0.0, 10.4, 0.62)
    d.box("black", -1.9, -0.9, 9.6, 1.9, 1.0, 10.8)
    # bascula (break action)
    d.box("black", -1.5, -1.6, 10.2, 1.5, 1.2, 13.2)
    d.box("steel", 1.4, -0.6, 11.0, 2.0, 0.2, 12.4)
    # guarda-mato + gatilho duplo
    trigger_guard(d, 12.0, 14.6, -1.6, -3.2, half_w=1.0, mat="black")
    d.box("tape", -1.6, -1.7, 10.6, 1.6, 1.3, 11.4)
    # punho de madeira serrado
    slanted_grip(d, 13.6, 16.4, -1.6, -5.4, half_w=1.15, mat="wood2", lean=1.6)
    d.box("tape", -1.25, -4.6, 15.4, 1.25, -3.4, 16.6)
    d.box("engrave", -0.5, -0.9, 12.0, 0.5, 0.1, 13.0)
    d.locator("shell", 1.4, 0.4, 12.0)
    return d


DESIGNS_CRIME = {}

for fn in (ak47, ak_short, sks, tec9, mac10, uzi, kit_roni, ghost_ar, sawedoff):
    DESIGNS_CRIME[fn.__name__] = fn
