"""Gera a documentacao tecnica do arsenal brasileiro a partir do catalogo e do
modelo realmente produzido pelo pipeline (contagem de cubos, bones, textura)."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from tacgen.specs import (BY_ID, FAMILIES, SPECS, recipe_items,  # noqa: E402
                         shop_entries)

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
    ("Fuzil de precisão", "sniper", ["aglc"]),
    ("Escopetas táticas", "shotgun", ["st12", "cbc_military"]),
    ("Facção — fuzis", "rifle", ["ak47_crime", "akm_crime", "ak_curta", "ar15_ghost",
                                 "m16_crime", "g3_crime", "fal_crime", "sks_crime",
                                 "mini14_crime", "mosin_crime"]),
    ("Facção — submetralhadoras, pistolas e escopeta serrada", "pistol",
     ["tec9", "tec_dc9", "mac10", "mac11", "uzi_crime", "kit_roni", "glock18_crime",
      "sawed_shotgun", "fgc9", "pt24_7_raspada"]),
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

CRIME_ATTACHMENTS_DOC = [
    dict(id="att_tape_optic", name="Luneta amarrada", mount="recebedor (fita isolante)"),
    dict(id="att_dualmag", name="Carregador duplo fitado", mount="poço do carregador"),
]

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
    # ------------------------------------------------ linha de faccao
    crime = [w for w in SPECS if w.get("faction") == "crime"]
    police = [w for w in SPECS if w.get("faction") != "crime"]
    add("## Linha de facção — armas de crime organizado")
    add("")
    add(f"{len(crime)} armas inspiradas em apreensões reais, na mesma plataforma de "
        "comportamento das demais (disparo, recarga, inspeção, bancada, HUD). O que muda é "
        "a linguagem visual e o kit de acessórios:")
    add("")
    add("- **Estética**: metal estampado oxidado, madeira riscada, fita isolante nas "
        "junções, numeração raspada e sigla da facção gravada (material `engrave`).")
    add("- **Acessórios improvisados** exclusivos: luneta de caça amarrada com fita "
        "(`att_tape_optic`) e carregador duplo fitado (`att_dualmag`), além dos cinco "
        "acessórios padrão.")
    add("- **Bancada**: aba 7 (fuzis de facção) e aba 8 (SMGs, pistolas e escopeta "
        "serrada), páginas 1 a 10.")
    add("")
    add("| Arma | Base real | Calibre no mod | Aba/página |")
    add("|---|---|---|---|")
    for w in crime:
        add(f"| {w['name']} (`tac_guns:{w['id']}`) | {w['lore']['maker']} | "
            f"`tac_guns:{w['ammo']}` | {w['tab']}/{w['itemtab']} |")
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
            bones_att = ("`att_optic`, `att_suppressor`, `att_grip`, `att_laser`, "
                         "`att_exmag`")
            if spec.get("faction") == "crime":
                bones_att += ", `att_tape_optic`, `att_dualmag` (improvisados)"
            add("No modelo, cada ponto de encaixe é um bone próprio "
                f"({bones_att}) para que a peça possa ser trocada sem editar o corpo "
                "da arma.")
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
    # ------------------------------------------------- camada policia x ladrao
    add("## Facções: policial x ladrão (camada de jogo)")
    add("")
    add("A camada de facção é implementada por script (`scripts/events/factions.js`) e não "
        "duplica itens: as 46 armas continuam as mesmas, mas passam a responder ao lado do "
        "jogador. O lado é guardado na tag `policia` / `ladrao` (compatível com `/tag`) e "
        "espelhado no scoreboard `faccao` (1 = policial, 2 = ladrão).")
    add("")
    add("### Tela de escolha de lado")
    add("")
    add("Ao entrar no mundo sem facção, o script abre um formulário "
        "(`ActionFormData`) com o layout do card de referência: título "
        "**ESCOLHA SEU LADO**, subtítulo *LEI OU LIBERDADE?* e dois botões-imagem de "
        "256x256 — metade azul **POLICIAL** (escudo, *PROTEJA A CIDADE / MANTENHA A ORDEM*) "
        "e metade vermelha **LADRÃO** (máscara, *FAÇA SEU DINHEIRO / DESAFIE A LEI*).")
    add("")
    add("| Arquivo | Papel |")
    add("|---|---|")
    add("| `out/TacGuns(R)/textures/ui/policial.png` | card azul do botão POLICIAL |")
    add("| `out/TacGuns(R)/textures/ui/ladrao.png` | card vermelho do botão LADRÃO |")
    add("| `out/TacGuns(B)/scripts/events/factions.js` | tela, economia, loja, abates |")
    add("| `tools/tacgen/templates/factions.js` | fonte do script (tabelas geradas no build) |")
    add("| `docs/faccao_tela.png` | mock da tela (gerado por `tools/tacgen/render_faction_screen.py`) |")
    add("")
    add("![Tela de escolha de lado](faccao_tela.png)")
    add("")
    add("Ao confirmar, o jogador recebe o título do lado (azul ou vermelho), som próprio, "
        "kit inicial (pistola + 60 munições, uma vez por lado) e o placar lateral "
        "*FACÇÃO BRASIL* com dinheiro, abates, reputação, lado e contagem de jogadores.")
    add("")
    add("### Arsenais separados")
    add("")
    add("Cada arma pertence a um lado. **Usar arma do lado oposto é bloqueado** "
        "(`beforeEvents.itemUse` cancelado, som de erro e aviso na action bar). As armas do "
        "pacote original (AK-47, MK18, AWP, M870, Glock 17, Colt Python, Desert Eagle, DB, "
        "DP-28, M134) ficam **neutras** — as duas facções podem usar.")
    add("")
    add(f"- **POLICIAL** — {len(police)} armas de dotação/forças especiais: IA2 5.56 e 7.62, "
        "MD97L/LM, M964 FAL, MD2, T4/T4 CQC, SAF 9mm, Mini-SAF, MT9 G2, SMT9, Uru, MT12, "
        "PT92, PT24/7, TS9, TH9, G3c, GX4, RT85, RT608, Raging Bull, AGLC, ST12 e CBC Military.")
    add(f"- **LADRÃO** — as {len(crime)} armas de facção (abas 7 e 8), com os acessórios "
        "improvisados (`att_tape_optic`, `att_dualmag`) que a polícia **não** pode usar.")
    add("")
    add("### Recompensas, recuo e apreensão")
    add("")
    add("| Ação | POLICIAL | LADRÃO |")
    add("|---|---|---|")
    add("| Abater jogador do lado oposto | +R$ 400, +1 abate, +1 reputação | idem |")
    add("| Abater monstro | +R$ 40 | +R$ 25 |")
    add("| Matar aldeão | -R$ 100 (conduta imprópria) | +R$ 120 (assalto) |")
    add("| Recuo da câmera por disparo | 0,022 (treinamento) | 0,058 (arma sem manutenção) |")
    add("| Arma do lado oposto | não dispara | não dispara |")
    add("| Dano de arma própria | x1,05 | x1,10 |")
    add("| Dano de arma alheia | x0,75 | x0,70 |")
    add("")
    add("**Apreensão:** ao abater um jogador do lado oposto, a arma na mão dele cai no chão "
        "(o pente é zerado) e o matador recebe o dinheiro. **Reputação** sobe com abates e "
        "define a patente mostrada no `/scriptevent tac_guns:info` "
        "(*Recruta → Coronel* na polícia, *Verme → Dono* na facção).")
    add("")
    add("### Loja de campanha")
    add("")
    add("`/scriptevent tac_guns:loja` abre a loja do lado com 6 itens (pistola, escopeta, "
        "dois fuzis, revólver e precisão), preço calculado a partir do dano real da arma e "
        "munição inclusa:")
    add("")
    for lado, rotulo in (("policia", "POLICIAL"), ("ladrao", "LADRÃO")):
        add(f"**{rotulo}**")
        add("")
        add("| Item | Preço | Munição inclusa |")
        add("|---|---|---|")
        for e in shop_entries(lado):
            add(f"| {e['nome']} (`{e['item']}`) | R$ {e['preco']} | "
                f"{e['municao']}x `{e['ammo']}` |")
        add("")
    add("A tabela completa é gerada em `factions.js` e validada por `tools/validate.py` "
        "(garante que a loja da polícia nunca vende arma de facção).")
    add("")
    add("### Comandos")
    add("")
    add("| Comando | Efeito |")
    add("|---|---|")
    add("| `/scriptevent tac_guns:faccao` | abre a tela de escolha (troca de lado) |")
    add("| `/scriptevent tac_guns:loja` | abre a loja do lado atual |")
    add("| `/scriptevent tac_guns:info` | lado, dinheiro, abates, patente, procurado |")
    add("| `/scriptevent tac_guns:marcar_cela` | polícia marca a cela onde está (usada na prisão) |")
    add("| `/scriptevent tac_guns:soltar` | libera um jogador algemado |")
    add("| `/tag @s add policia` / `add ladrao` | define o lado por comando |")
    add("| `/scoreboard players set <jogador> dinheiro 5000` | define o dinheiro |")
    add("")
    add("Trocar de lado zera dinheiro, abates e reputação (o kit inicial de cada lado é "
        "entregue uma única vez, controlado pelas tags `kit_policia` / `kit_ladrao`).")
    add("")

    # ------------------------------------------------ bases e prisão
    add("### Bases construídas por `/function`")
    add("")
    add("Duas estruturas completas são geradas como funções de comando (sem `.mcstructure`), "
        "montadas **ao redor do jogador** e relativas à sua posição — funcionam em qualquer "
        "mundo e não dependem de pack de estrutura:")
    add("")
    add("| Comando | Conteúdo | Arquivos |")
    add("|---|---|---|")
    add("| `/function policial` | pátio asfaltado com faixas e viatura, muro com portão e "
        "grades, prédio de 2 andares com recepção e escada, 2 celas com cama e banheiro, "
        "arsenal com bancada/rebolo/forno, heliponto com \"H\", torre de vigilância, postes "
        "e mastro com bandeira | `functions/policial.mcfunction` + 8 partes |")
    add("| `/function favela` | morro em três patamares com paredões de contenção, "
        "escadarias, 26 casas com laje, puxadinho, caixa d'água, antena e pichação, becos "
        "iluminados, varais, barracas de lona, postes de energia, **boca de fumo** com "
        "balcão, estoque, mesa de dinheiro, som, fogueira e sacos de areia, e **mirador** "
        "de 16 blocos | `functions/favela.mcfunction` + 7 partes |")
    add("| `/function faccao` | ajuda no chat com todos os comandos | — |")
    add("")
    add("![Base policial](estrutura_policial.png)")
    add("")
    add("![Favela](estrutura_favela.png)")
    add("")
    add("Imagens geradas por `tools/tacgen/render_structures.py`, que aplica os próprios "
        "`.mcfunction` gerados e desenha a vista de cima + um corte vertical.")
    add("")
    add("**Como usar:** ative cheats no mundo, fique em área aberta e carregada (a "
        "estrutura ocupa ~3 chunks de raio) e rode `/function policial` ou `/function favela` "
        "no ponto onde quer a construção. O master só encadeia as partes; cada parte pode ser "
        "chamada sozinha (ex.: `/function favela/04_boca`).")
    add("")
    add("### Prisão, algemas e nível de procurado")
    add("")
    add("| Item/efeito | Como funciona |")
    add("|---|---|")
    add("| `tac_guns:algemas` | receita 3x3: 4 `iron_ingot` nos cantos + 1 `chain` no centro. "
        "Só a **polícia** pode usar; clicar com elas em um jogador do lado oposto prende |")
    add("| Prisão | vítima recebe a tag `algemado`, lentidão III + fadiga, perde o direito de "
        "usar armas e é teleportada para a cela marcada; o policial ganha +R$ 250 e +1 de "
        "reputação |")
    add("| Cela | a polícia marca o ponto com `/scriptevent tac_guns:marcar_cela` (fica salvo "
        "no mundo, funciona em qualquer dimensão) |")
    add("| Soltura | clicar de novo com as algemas, `/scriptevent tac_guns:soltar` ou 60 s de "
        "prazo automático |")
    add("| Nível de procurado | sobe +2 por assalto a aldeão e +4 por abate entre facções; "
        "cai 1 ponto a cada 20 s |")
    add("| Alerta policial | ao chegar em 3, o procurado recebe o título **PROCURADO**, ganha "
        "brilho e a polícia recebe no chat o nome e as coordenadas dele |")
    add("")
    add("## Cobertura da lista solicitada")
    add("")
    add("| Categoria | Armas implementadas |")
    add("|---|---|")
    add("| Fuzis 1-25 | IA2 5.56, IA2 7.62, MD97L, MD97LM, M964 FAL, MD2, T4, T4 CQC |")
    add("| SMGs 26-50 | SAF 9mm, Mini-SAF, MT9 G2, SMT9, Uru 9mm, MT12 |")
    add("| Pistolas 51-80 | PT92, PT24/7, TS9, TH9, G3c, GX4 |")
    add("| Revólveres 81-95 | RT85, RT608, Raging Bull .454 |")
    add("| Precisão / escopetas 96-105 | AGLC, ST12, CBC Military 3.0 |")
    add("| Crime organizado | AK-47, AKM, AK curta, AR fantasma 3D, M16A1, G3A3, "
        "FAL internacional, SKS, Mini-14, Mosin serrado, TEC-9, TEC-DC9, MAC-10, M11, "
        "Uzi, Kit Roni, Glock 18, espingarda serrada, FGC-9, PT24/7 raspada |")
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
