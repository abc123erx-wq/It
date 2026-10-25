"""Gera a documentacao tecnica do arsenal brasileiro a partir do catalogo e do
modelo realmente produzido pelo pipeline (contagem de cubos, bones, textura)."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from tacgen.specs import BY_ID, FAMILIES, SPECS, recipe_items  # noqa: E402

TEMPLATE_AMMO = {"mk18": "556x45mm", "glock17": "9x19mm", "coltpython": "357magnum",
                 "awp": "338lapua", "m870": "12gauge"}

OUT_RP = os.path.join(ROOT, "out", "TacGuns(R)")
DOCS = os.path.join(ROOT, "docs")

GROUPS = [
    ("Fuzis de assalto e batalha", "rifle", ["ia2_556", "ia2_762", "md97l", "md97lm",
                                             "m964_fal", "md2", "t4", "t4_cqc"]),
    ("Submetralhadoras", "rifle", ["saf_9mm", "mini_saf", "mt9_g2", "smt9", "uru", "mt12"]),
    ("Pistolas", "pistol", ["pt92", "pt24_7", "ts9", "th9", "g3c", "gx4"]),
    ("Revólveres", "revolver", ["rt85", "rt608", "raging_bull"]),
    ("Precisão e escopetas", "sniper", ["aglc"]),
    ("Precisão e escopetas", "shotgun", ["st12", "cbc_military"]),
]

ATTACH_MOUNTS = {
    "rifle": [("Óptica", "trilho superior (Picatinny), sobre o receptor"),
              ("Supressor", "boca do cano, rosca 1/2x28"),
              ("Foregrip / bipé", "trilho inferior do guarda-mão"),
              ("Lanterna / laser", "trilho lateral 3h ou 9h"),
              ("Carregador estendido", "poço do carregador"),
              ("Coronha", "tubo do receptor traseiro")],
    "pistol": [("Red dot", "placa óptica / trilho curto no ferrolho"),
               ("Supressor", "boca do cano roscada"),
               ("Lanterna", "trilho inferior curto"),
               ("Carregador estendido", "base do punho")],
    "revolver": [("Mira", "trilho do cano (substitui a mira fixa)"),
                 ("Cilindro extra", "conjunto do tambor")],
    "sniper": [("Luneta 3-12x", "trilho superior, sobre a culatra"),
               ("Supressor", "boca do cano roscada"),
               ("Bipé", "trilho inferior / swivel"),
               ("Carregador", "poço do carregador")],
    "shotgun": [("Red dot", "trilho superior do receptor"),
                ("Lanterna / laser", "trilho lateral do guarda-mão"),
                ("Tube extensor", "tubo carregador sob o cano"),
                ("Coronha", "traseira do receptor")],
}

ATTACHMENTS_DOC = [
    dict(id="att_optic", name="Red dot", prop="tac_guns:att_optic", bone="att_optic",
         mount="trilho superior do receptor"),
    dict(id="att_suppressor", name="Supressor", prop="tac_guns:att_suppressor",
         bone="att_suppressor", mount="boca do cano"),
    dict(id="att_laser", name="Lanterna/Laser", prop="tac_guns:att_laser",
         bone="att_laser", mount="trilho inferior/lateral"),
    dict(id="att_grip", name="Foregrip", prop="tac_guns:att_grip", bone="att_grip",
         mount="trilho inferior do guarda-mão"),
    dict(id="att_exmag", name="Carregador estendido", prop="tac_guns:att_exmag",
         bone="att_exmag", mount="poço do carregador"),
]

ANIM_KEYS = [("fp.draw", "Equipar / saque"),
             ("fp.inspect", "Inspecionar"),
             ("shoot.nsight / shoot.sight", "Disparo (quadril / mira)"),
             ("fp.tac", "Recarga tática"),
             ("fp.reload", "Recarga vazia / seca"),
             ("fp.sprint", "Corrida com a arma baixa"),
             ("tp.hold / tp.crawl", "Pose de terceira pessoa")]


def geometry_stats(gid):
    path = os.path.join(OUT_RP, "models", "entity", "guns", f"{gid}.json")
    doc = json.load(open(path))
    geo = doc["minecraft:geometry"][0]
    cubes = 0
    bones = []
    for bone in geo["bones"]:
        n = len(bone.get("cubes", []))
        if n:
            cubes += n
            bones.append((bone["name"], n))
    return dict(cubes=cubes, faces=cubes * 6, bones=bones,
                tex=(geo["description"]["texture_width"], geo["description"]["texture_height"]))


def render():
    lines = []
    add = lines.append
    add("# Arsenal Brasileiro — documentação técnica e integração no TacGuns")
    add("")
    add("Este documento cobre as armas brasileiras **já implementadas no addon** "
        f"(packs `out/TacGuns(B)` e `out/TacGuns(R)`): {len(SPECS)} armas distribuídas em "
        "cinco categorias, todas herdando o comportamento completo das armas originais do "
        "TacGuns (disparo, munição, recarga, recarga tática, inspeção, saque, sprint, sway, "
        "recuo, pose em terceira pessoa, bancada e contador de munição no HUD).")
    add("")
    add("## Como a herança funciona")
    add("")
    add("Cada arma brasileira foi gerada a partir de uma das cinco plataformas originais. "
        "O pipeline copia controladores, animações, eventos, funções e faixa de propriedade "
        "e troca apenas o identificador, o modelo voxel, o atlas 128x128 e o ícone:")
    add("")
    add("| Plataforma | Herda de | Pente no jogo | Munição base | Propriedade de recarga |")
    add("|---|---|---|---|---|")
    for key, fam in FAMILIES.items():
        add(f"| {key} | `{fam['template']}` | {fam['mag']} (+1 na câmara) | "
            f"`tac_guns:{TEMPLATE_AMMO[fam['template']]}` | "
            f"`{fam['prop'] or 'mark_variant (escopeta)'}` |")
    add("")
    add("### Sistemas ativos em todas as armas")
    add("")
    for key, desc in ANIM_KEYS:
        add(f"- **{desc}** — `animation.<arma>.{key}`")
    add("- **HUD**: `xv<munição no pente>b<munição no inventário>` via `/title @s actionbar`.")
    add("- **Troca pente vazio/cheio**: ao zerar o pente o item vira `<arma>_emp` e volta "
        "ao atirar com recarga concluída.")
    add("- **Bancada**: cada arma tem página própria na aba correspondente do workbench.")
    add("- **Sons**: `<arma>.shoot`, `.draw`, `.reload`, `.tacreload`, `.inspect` "
        "(gerados a partir da plataforma, prontos para receber gravações próprias).")
    add("- **Dano**: script `global.js` (`tacg.bullets`) + entidade `bullet:<arma>`.")
    add("")

    add("### Attachments modulares (implementado)")
    add("")
    add("Cinco acessórios universais são craftáveis na mesa de trabalho e equipáveis em "
        "**qualquer** arma brasileira:")
    add("")
    add("| Item | Propriedade sincronizada | Bone no modelo | Encaixe |")
    add("|---|---|---|---|")
    for att in ATTACHMENTS_DOC:
        add(f"| `tac_guns:{att['id']}` ({att['name']}) | `{att['prop']}` | `{att['bone']}` | "
            f"{att['mount']} |")
    add("")
    add("**Como instalar:** segure o acessório, agache e use (botão de usar). O script "
        "`scripts/events/attachments.js` liga a propriedade do jogador, consome 1 item do "
        "inventário e o render controller passa a desenhar o bone correspondente. Repetir o "
        "gesto remove a peça. Como o estado vive no jogador (propriedade com `client_sync`), "
        "a peça aparece em primeira e terceira pessoa e sobrevive à troca de arma.")
    add("")
    add("Os bones de encaixe existem em todas as 26 armas e são filhos do bone do corpo, "
        "portanto acompanham o recuo, o sway, a recarga e a animação de inspeção sem nenhum "
        "trabalho extra.")
    add("")
    for title, fam_key, ids in GROUPS:
        if not ids:
            continue
        add(f"## {title}")
        add("")
        for gid in ids:
            spec = BY_ID[gid]
            fam = FAMILIES[spec["family"]]
            st = geometry_stats(gid)
            lore = spec["lore"]
            add(f"### {spec['name']}  (`tac_guns:{gid}`)")
            add("")
            add("**1. Identificação e lore**")
            add("")
            add(f"- Fabricante: {lore['maker']}")
            add(f"- Calibre: {lore['caliber']} — no mod usa `tac_guns:{spec['ammo']}`")
            add(f"- Uso: {lore['users']}")
            add(f"- Época: {lore['era']}")
            add(f"- Contexto: {lore['note']}")
            add(f"- Dano no addon: **{spec['damage']}** por projétil · pente **{fam['mag']}** "
                f"· plataforma `{fam['template']}`")
            add("")
            add("**2. Sistema de attachments**")
            add("")
            add("| Acessório | Ponto de encaixe |")
            add("|---|---|")
            for acc in spec["attach"]:
                mount = "trilho/rosca padrão"
                for key, where in ATTACH_MOUNTS[spec["family"]]:
                    if key.split()[0].lower() in acc.lower():
                        mount = where
                        break
                add(f"| {acc} | {mount} |")
            add("")
            add("No modelo, cada ponto de encaixe é um bone próprio "
                "(`att_optic`, `att_suppressor`, `att_grip`, `att_laser`, `att_exmag`) "
                "para que a peça possa ser trocada sem editar o corpo da arma.")
            add("")
            add("**3. Diretrizes do modelo 3D**")
            add("")
            add(f"- Malha voxel: **{st['cubes']} cubos / {st['faces']} faces** "
                f"(atlas único {st['tex'][0]}x{st['tex'][1]}, 1 material `material.guns`).")
            add(f"- Bones com geometria: {', '.join(f'`{n}` ({c})' for n, c in st['bones'])}.")
            add("- Estilo: voxel com blocos de 1 unidade, sem chanfros; silhueta legível a "
                "3 blocos de distância e mira alinhada ao ponto de visada da câmera.")
            add(f"- Texturização: {spec['finish']}")
            add("- Separação de malha (peças móveis em bones independentes): "
                + ", ".join(f"`{m}`" for m in spec["mesh"]) + ".")
            add("")
            add("**4. Animações nativas**")
            add("")
            anim = spec["anim"]
            add(f"- **Equipar (Draw)**: {anim['draw']} — `animation.{gid}.fp.draw` "
                "(reproduzida também no controller `draw` global).")
            add(f"- **Inspecionar (Inspect)**: {anim['inspect']} — "
                f"`animation.{gid}.fp.inspect`, disparada com a arma cheia + agachado.")
            add(f"- **Atirar (Fire)**: {anim['fire']} — `animation.{gid}.shoot.nsight` "
                f"(quadril) e `.shoot.sight` (mira), com partículas de boca e de "
                "ejeção no locator `<arma>shell`.")
            add(f"- **Recarga tática**: {anim['tactical']} — `animation.{gid}.fp.tac` "
                "(não descarta o pente, mantém a mira).")
            add(f"- **Recarga vazia**: {anim['empty']} — `animation.{gid}.fp.reload`, "
                "termina com `/replaceitem` devolvendo a arma carregada.")
            add("")
            recipe = ", ".join(f"{v}x `{k}`" for k, v in recipe_items(spec).items())
            add(f"*Receita na bancada de trabalho (aba {spec['tab']}, item {spec['itemtab']}):* "
                f"{recipe} → `tac_guns:{gid}_emp` (arma vazia, pronta para municiar).")
            add("")
    add("## Cobertura da lista solicitada")
    add("")
    add("| Categoria da lista | Armas implementadas |")
    add("|---|---|")
    add("| Fuzis 1-25 | IA2 5.56, IA2 7.62, MD97L, MD97LM, M964 FAL, MD2, T4, T4 CQC |")
    add("| SMGs 26-50 | SAF 9mm, Mini-SAF, MT9 G2, SMT9, Uru 9mm, MT12 |")
    add("| Pistolas 51-80 | PT92, PT24/7, TS9, TH9, G3c, GX4 |")
    add("| Revólveres 81-95 | RT85, RT608, Raging Bull .454 |")
    add("| Precisão / escopetas 96-105 | AGLC, ST12, CBC Military 3.0 |")
    add("")
    add("As demais armas da lista usam as mesmas cinco plataformas: para incluí-las basta "
        "adicionar uma entrada em `tools/tacgen/specs.py` (id, família, design voxel, calibre, "
        "faixa de propriedade livre, receita e textos) e rodar "
        "`python3 tools/tacgen/build.py && python3 tools/validate.py`.")
    add("")
    return "\n".join(lines)


def main():
    os.makedirs(DOCS, exist_ok=True)
    text = render()
    path = os.path.join(DOCS, "ARSENAL_BRASIL.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(f"doc -> {path} ({len(text.splitlines())} linhas)")


if __name__ == "__main__":
    main()
