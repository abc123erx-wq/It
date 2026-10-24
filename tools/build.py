#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Empacota o addon em um arquivo .mcaddon (zip com os dois pacotes).

Uso:
    python3 tools/build.py            # valida + gera release/*.mcaddon
    python3 tools/build.py --no-check # gera sem rodar o validador
"""
import os
import shutil
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, "src", "behavior_pack")
RP = os.path.join(ROOT, "src", "resource_pack")
RELEASE = os.path.join(ROOT, "release")

NOME = "CreativeSquad_ItensLendarios_26.52"
BP_DIR = "CreativeSquad_ItensLendarios_BP"
RP_DIR = "CreativeSquad_ItensLendarios_RP"


def rodar_validador():
    print("==> validando conteudo")
    res = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "validate.py")])
    if res.returncode != 0:
        print("\nBuild abortado: o validador encontrou erros.")
        sys.exit(1)


def adicionar_pacote(zf, origem, destino):
    for base, _dirs, files in os.walk(origem):
        for f in files:
            full = os.path.join(base, f)
            rel = os.path.relpath(full, origem)
            zf.write(full, os.path.join(destino, rel))


def main():
    if "--no-check" not in sys.argv:
        rodar_validador()

    os.makedirs(RELEASE, exist_ok=True)

    # .mcpack individuais (uteis para quem quer instalar so um lado)
    for origem, destino, sufixo in (
        (BP, BP_DIR, "BP"),
        (RP, RP_DIR, "RP"),
    ):
        mcpack = os.path.join(RELEASE, "%s_%s.mcpack" % (NOME, sufixo))
        with zipfile.ZipFile(mcpack, "w", zipfile.ZIP_DEFLATED) as zf:
            adicionar_pacote(zf, origem, "")
        print("==> %s (%.1f KB)" % (os.path.basename(mcpack), os.path.getsize(mcpack) / 1024))

    # .mcaddon com os dois pacotes
    mcaddon = os.path.join(RELEASE, NOME + ".mcaddon")
    with zipfile.ZipFile(mcaddon, "w", zipfile.ZIP_DEFLATED) as zf:
        adicionar_pacote(zf, BP, BP_DIR)
        adicionar_pacote(zf, RP, RP_DIR)
    print("==> %s (%.1f KB)" % (os.path.basename(mcaddon), os.path.getsize(mcaddon) / 1024))

    # copia os documentos para o release
    for doc in ("README.md",):
        src = os.path.join(ROOT, doc)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(RELEASE, doc))

    with zipfile.ZipFile(mcaddon) as zf:
        nomes = zf.namelist()
    print("\nConteudo do .mcaddon: %d arquivos" % len(nomes))
    print("  itens:      %d" % len([n for n in nomes if "/items/" in n]))
    print("  receitas:   %d" % len([n for n in nomes if "/recipes/" in n]))
    print("  scripts:    %d" % len([n for n in nomes if "/scripts/" in n]))
    print("  texturas:   %d" % len([n for n in nomes if n.endswith(".png")]))
    print("  funcoes:    %d" % len([n for n in nomes if n.endswith(".mcfunction")]))


if __name__ == "__main__":
    main()
