#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera os arquivos de conteudo do addon (itens, receitas, idiomas, item_texture e
funcoes de comando) a partir de uma unica tabela de dados.

Uso:  python3 tools/gen_content.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, "src", "behavior_pack")
RP = os.path.join(ROOT, "src", "resource_pack")
FMT = "1.26.30"          # formato dos JSONs de item (aceito pelo 26.52)
RECIPE_FMT = "1.21.30"   # formato dos JSONs de receita

PICK_SPEED = 60
FAST_BLOCKS = [
    "stone", "cobblestone", "mossy_cobblestone", "smooth_stone", "granite",
    "diorite", "andesite", "polished_granite", "polished_diorite",
    "polished_andesite", "deepslate", "cobbled_deepslate", "tuff", "calcite",
    "dripstone_block", "netherrack", "basalt", "smooth_basalt", "blackstone",
    "end_stone", "sandstone", "red_sandstone", "dirt", "grass_block", "sand",
    "red_sand", "gravel", "clay", "coal_ore", "iron_ore", "copper_ore",
    "gold_ore", "redstone_ore", "lapis_ore", "diamond_ore", "emerald_ore",
    "nether_gold_ore", "quartz_ore", "deepslate_coal_ore",
    "deepslate_iron_ore", "deepslate_copper_ore", "deepslate_gold_ore",
    "deepslate_redstone_ore", "deepslate_lapis_ore", "deepslate_diamond_ore",
    "deepslate_emerald_ore",
]


def item(identifier, key, pt, en, components, category="equipment",
         hidden=False, recipe=None, lore_pt=None, lore_en=None):
    return {
        "id": identifier,
        "key": key,
        "pt": pt,
        "en": en,
        "components": components,
        "category": category,
        "hidden": hidden,
        "recipe": recipe,
        "lore_pt": lore_pt or [],
        "lore_en": lore_en or [],
    }


def base(name, glint=True, stack=1, hand=True, tags=None):
    c = {
        "minecraft:icon": {"textures": {"default": name}},
        "minecraft:display_name": {"value": "item.cs.%s.name" % name},
        "minecraft:max_stack_size": stack,
        "minecraft:glint": {"value": glint},
    }
    if hand:
        c["minecraft:hand_equipped"] = {"value": True}
    if tags:
        c["minecraft:tags"] = {"tags": tags}
    return c


LEG = ["cs:lendario"]

ITEMS = [
    item(
        "cs:espada_do_cacador", "espada_do_cacador",
        "Espada do Caçador", "Hunter's Sword",
        {
            **base("espada_do_cacador", tags=LEG + ["cs:espada", "minecraft:is_sword"]),
            "minecraft:damage": {"value": 9},
            "minecraft:enchantable": {"slot": "sword", "value": 15},
        },
        recipe={
            "type": "shaped",
            "pattern": [" G ", " G ", " S "],
            "key": {"G": "minecraft:gold_ingot", "S": "minecraft:stick"},
            "unlock": [{"item": "minecraft:gold_ingot"}],
        },
        lore_pt=[
            "§7Item Lendário de §fNaitPlayer",
            "§8§m                         ",
            "§6+9§r de dano (ouro maciço)",
            "§bRepulsão X§r: arremessa o alvo",
            "§cMaldição:§r Mau Presságio permanente",
            "§eAo matar alguém, a vítima herda a espada",
            "§7Inquebrável",
        ],
        lore_en=[
            "§7Legendary item of §fNaitPlayer",
            "§8§m                         ",
            "§6+9§r damage",
            "§bKnockback X§r",
            "§cCurse:§r permanent Bad Omen",
            "§eWhoever you kill inherits the sword",
            "§7Unbreakable",
        ],
    ),
    item(
        "cs:batata_do_bobo", "batata_do_bobo",
        "Batata do Bobo", "Fool's Potato",
        {
            **base("batata_do_bobo", tags=LEG + ["cs:batata"]),
            "minecraft:max_stack_size": 1,
            "minecraft:food": {
                "nutrition": 1,
                "saturation_modifier": 0.1,
                "can_always_eat": True,
            },
            "minecraft:use_modifiers": {
                "use_duration": 1.6,
                "movement_modifier": 1.0,
            },
        },
        category="items",
        recipe={
            "type": "shapeless",
            "ingredients": [
                "minecraft:poisonous_potato",
                "minecraft:spider_eye",
                "minecraft:slime_ball",
            ],
            "unlock": [{"item": "minecraft:poisonous_potato"}],
        },
        lore_pt=[
            "§7Item Lendário de §fCaduxinn",
            "§8§m                         ",
            "§2Lentidão V§r enquanto estiver no inventário",
            "§8(e mesmo sem estar na mão)",
            "§aAnula a Bota Lendária",
            "§7Comer dá Veneno + Lentidão",
        ],
        lore_en=[
            "§7Legendary item of §fCaduxinn",
            "§8§m                         ",
            "§2Slowness V§r while in your inventory",
            "§aNegates the Legendary Boots",
        ],
    ),
    item(
        "cs:bota_lendaria", "bota_lendaria",
        "Bota Lendária", "Legendary Boots",
        {
            **base("bota_lendaria", tags=LEG + ["cs:bota"]),
            "minecraft:wearable": {"slot": "slot.armor.feet", "protection": 3},
            "minecraft:enchantable": {"slot": "armor_feet", "value": 12},
        },
        recipe={
            "type": "shaped",
            "pattern": ["D D", "D D", "F F"],
            "key": {"D": "minecraft:diamond", "F": "minecraft:feather"},
            "unlock": [{"item": "minecraft:diamond"}],
        },
        lore_pt=[
            "§7Item Lendário de §f0nerb",
            "§8§m                         ",
            "§bVelocidade III§r enquanto estiver calçada",
            "§aProteção 3§r · Inquebrável",
            "§cAnulada pela Batata do Bobo",
        ],
        lore_en=[
            "§7Legendary item of §f0nerb",
            "§8§m                         ",
            "§bSpeed III§r while worn",
            "§aProtection 3§r · Unbreakable",
        ],
    ),
    item(
        "cs:capacete_gemeo_bern", "capacete_gemeo_bern",
        "Capacete dos Gêmeos · Bern", "Twin Helmet · Bern",
        {
            **base("capacete_gemeo_bern", tags=LEG + ["cs:capacete", "cs:gemeo_bern"]),
            "minecraft:wearable": {"slot": "slot.armor.head", "protection": 4},
            "minecraft:enchantable": {"slot": "armor_head", "value": 12},
        },
        recipe={
            "type": "shaped",
            "pattern": ["SSS", "SHS"],
            "key": {"S": "minecraft:turtle_scute", "H": "minecraft:heart_of_the_sea"},
            "unlock": [{"item": "minecraft:turtle_scute"}],
        },
        lore_pt=[
            "§7Item Lendário de §fBern",
            "§8§m                         ",
            "§c+4 corações§r de vida extra",
            "§bRespiração aquática infinita",
            "§dVida compartilhada§r com o capacete do Chip",
            "§7Inquebrável",
        ],
        lore_en=[
            "§7Legendary item of §fBern",
            "§8§m                         ",
            "§c+4 hearts§r of extra health",
            "§bInfinite water breathing",
            "§dShared life§r with Chip's helmet",
        ],
    ),
    item(
        "cs:capacete_gemeo_chip", "capacete_gemeo_chip",
        "Capacete dos Gêmeos · Chip", "Twin Helmet · Chip",
        {
            **base("capacete_gemeo_chip", tags=LEG + ["cs:capacete", "cs:gemeo_chip"]),
            "minecraft:wearable": {"slot": "slot.armor.head", "protection": 4},
            "minecraft:enchantable": {"slot": "armor_head", "value": 12},
        },
        recipe={
            "type": "shaped",
            "pattern": ["SSS", "SNS"],
            "key": {"S": "minecraft:turtle_scute", "N": "minecraft:nautilus_shell"},
            "unlock": [{"item": "minecraft:turtle_scute"}],
        },
        lore_pt=[
            "§7Item Lendário de §fChip Naughter",
            "§8§m                         ",
            "§c+4 corações§r de vida extra",
            "§bRespiração aquática infinita",
            "§dVida compartilhada§r com o capacete do Bern",
            "§7Inquebrável",
        ],
        lore_en=[
            "§7Legendary item of §fChip Naughter",
            "§8§m                         ",
            "§c+4 hearts§r of extra health",
            "§bInfinite water breathing",
            "§dShared life§r with Bern's helmet",
        ],
    ),
    item(
        "cs:dragao_lendario", "dragao_lendario",
        "Dragão Lendário", "Legendary Dragon",
        {
            **base("dragao_lendario", tags=LEG + ["cs:dragao"]),
        },
        recipe={
            "type": "shaped",
            "pattern": [" E ", "EDE", " E "],
            "key": {"E": "minecraft:ender_pearl", "D": "minecraft:dragon_breath"},
            "unlock": [{"item": "minecraft:dragon_breath"}],
        },
        lore_pt=[
            "§7Item Lendário de §fCaduxinn",
            "§8§m                         ",
            "§5Use§r para soltar o Bafo do Dragão",
            "§cDano em cone§r + Veneno",
            "§7Recarga: 4s · Inquebrável",
        ],
        lore_en=[
            "§7Legendary item of §fCaduxinn",
            "§8§m                         ",
            "§5Use§r to unleash Dragon's Breath",
            "§cCone damage§r + Poison",
        ],
    ),
    item(
        "cs:escudo_lendario", "escudo_lendario",
        "Escudo Lendário", "Legendary Shield",
        {
            **base("escudo_lendario", tags=LEG + ["cs:escudo"]),
            "minecraft:allow_off_hand": {"value": True},
        },
        recipe={
            "type": "shaped",
            "pattern": ["IEI", "ISI", " I "],
            "key": {
                "I": "minecraft:iron_ingot",
                "E": "minecraft:echo_shard",
                "S": "minecraft:shield",
            },
            "unlock": [{"item": "minecraft:shield"}],
        },
        lore_pt=[
            "§7Item Lendário de §fMucaHD",
            "§8§m                         ",
            "§3Use§r para disparar a §bRajada Sônica",
            "§c12 de dano§r + empurrão forte",
            "§8Não bloqueia ataques (como no servidor)",
            "§7Recarga: 8s · Inquebrável",
        ],
        lore_en=[
            "§7Legendary item of §fMucaHD",
            "§8§m                         ",
            "§3Use§r to fire a §bSonic Boom",
            "§c12 damage§r + heavy knockback",
        ],
    ),
    item(
        "cs:bussola_lendaria", "bussola_lendaria",
        "Bússola Lendária", "Legendary Compass",
        {
            **base("bussola_lendaria", tags=LEG + ["cs:bussola"]),
        },
        recipe={
            "type": "shapeless",
            "ingredients": [
                "minecraft:compass",
                "minecraft:ender_eye",
                "minecraft:amethyst_shard",
            ],
            "unlock": [{"item": "minecraft:compass"}],
        },
        lore_pt=[
            "§7Item Lendário de §fGeleiaPlays",
            "§8§m                         ",
            "§3Use§r para localizar o jogador mais próximo",
            "§eMostra nome, distância e direção",
            "§cRevela jogadores invisíveis§r (rastro de partículas)",
            "§7Inquebrável",
        ],
        lore_en=[
            "§7Legendary item of §fGeleiaPlays",
            "§8§m                         ",
            "§3Use§r to track the nearest player",
            "§cReveals invisible players",
        ],
    ),
    item(
        "cs:lampiao_lendario", "lampiao_lendario",
        "Lampião Lendário", "Legendary Lantern",
        {
            **base("lampiao_lendario", tags=LEG + ["cs:lampiao"]),
            "minecraft:allow_off_hand": {"value": True},
        },
        recipe={
            "type": "shapeless",
            "ingredients": [
                "minecraft:lantern",
                "minecraft:glow_ink_sac",
                "minecraft:amethyst_shard",
            ],
            "unlock": [{"item": "minecraft:lantern"}],
        },
        lore_pt=[
            "§7Item Lendário de §fTonigonn",
            "§8§m                         ",
            "§bInvisibilidade infinita§r enquanto segurar",
            "§7Sem partículas de efeito",
            "§cPode ser revelado pela Bússola Lendária",
        ],
        lore_en=[
            "§7Legendary item of §fTonigonn",
            "§8§m                         ",
            "§bInfinite invisibility§r while held",
            "§7No effect particles",
        ],
    ),
    item(
        "cs:pena_lendaria", "pena_lendaria",
        "Pena Lendária", "Legendary Feather",
        {
            **base("pena_lendaria", tags=LEG + ["cs:pena"]),
        },
        recipe={
            "type": "shapeless",
            "ingredients": [
                "minecraft:feather",
                "minecraft:phantom_membrane",
                "minecraft:wind_charge",
            ],
            "unlock": [{"item": "minecraft:feather"}],
        },
        lore_pt=[
            "§7Item Lendário de §fFeuripe",
            "§8§m                         ",
            "§fLevitação infinita§r enquanto segurar",
            "§cNão protege contra dano de queda",
        ],
        lore_en=[
            "§7Legendary item of §fFeuripe",
            "§8§m                         ",
            "§fInfinite levitation§r while held",
            "§cNo fall damage protection",
        ],
    ),
    item(
        "cs:picareta_lendaria", "picareta_lendaria",
        "Picareta Lendária", "Legendary Pickaxe",
        {
            **base("picareta_lendaria", tags=LEG + ["cs:picareta"]),
            "minecraft:damage": {"value": 3},
            "minecraft:enchantable": {"slot": "pickaxe", "value": 15},
            "minecraft:digger": {
                "use_efficiency": True,
                "destroy_speeds": [
                    {"block": "minecraft:" + b, "speed": PICK_SPEED}
                    for b in FAST_BLOCKS
                ],
            },
        },
        recipe={
            "type": "shaped",
            "pattern": ["III", "ISI", " S "],
            "key": {"I": "minecraft:iron_ingot", "S": "minecraft:stick"},
            "unlock": [{"item": "minecraft:iron_ingot"}],
        },
        lore_pt=[
            "§7Item Lendário de §fPedrux",
            "§8§m                         ",
            "§fEficiência V§r + §bFortuna III",
            "§aQuebra blocos quase instantaneamente",
            "§cNão consegue minerar obsidiana/netherita",
            "§7Inquebrável",
        ],
        lore_en=[
            "§7Legendary item of §fPedrux",
            "§8§m                         ",
            "§fEfficiency V§r + §bFortune III",
            "§cCannot mine obsidian/netherite",
        ],
    ),
    item(
        "cs:pocao_lendaria", "pocao_lendaria",
        "Poção Lendária", "Legendary Potion",
        {
            **base("pocao_lendaria", stack=16, tags=LEG + ["cs:pocao"]),
        },
        category="items",
        recipe={
            "type": "shapeless",
            "ingredients": [
                "minecraft:glass_bottle",
                "minecraft:ink_sac",
                "minecraft:gunpowder",
            ],
            "unlock": [{"item": "minecraft:glass_bottle"}],
        },
        lore_pt=[
            "§7Item Lendário de §fFixz",
            "§8§m                         ",
            "§dUse§r para arremessar (não gasta o item)",
            "§8Cegueira§r em quem for atingido",
            "§7Recarga: 1,5s · Inquebrável",
        ],
        lore_en=[
            "§7Legendary item of §fFixz",
            "§8§m                         ",
            "§dUse§r to throw it (not consumed)",
            "§8Blindness§r on hit",
        ],
    ),
    item(
        "cs:relogio_lendario", "relogio_lendario",
        "Relógio Lendário", "Legendary Clock",
        {
            **base("relogio_lendario", tags=LEG + ["cs:relogio"]),
        },
        recipe={
            "type": "shapeless",
            "ingredients": [
                "minecraft:clock",
                "minecraft:ender_pearl",
                "minecraft:gold_ingot",
                "minecraft:name_tag",
            ],
            "unlock": [{"item": "minecraft:clock"}],
        },
        lore_pt=[
            "§7Item Lendário de §fLigonz",
            "§8§m                         ",
            "§6Use§r para se disfarçar de outro jogador",
            "§7Copia o nick de quem estiver online por 60s",
            "§8(No Bedrock a skin não pode ser trocada em jogo)",
            "§7Inquebrável",
        ],
        lore_en=[
            "§7Legendary item of §fLigonz",
            "§8§m                         ",
            "§6Use§r to disguise as another player",
            "§7Copies their name tag for 60s",
        ],
    ),
    item(
        "cs:tridente_lendario", "tridente_lendario",
        "Tridente Lendário", "Legendary Trident",
        {
            **base("tridente_lendario", tags=LEG + ["cs:tridente"]),
            "minecraft:damage": {"value": 9},
            "minecraft:enchantable": {"slot": "sword", "value": 15},
        },
        recipe={
            "type": "shapeless",
            "ingredients": [
                "minecraft:trident",
                "minecraft:prismarine_shard",
                "minecraft:nautilus_shell",
            ],
            "unlock": [{"item": "minecraft:trident"}],
        },
        lore_pt=[
            "§7Item Lendário de §fNaitPlayer",
            "§8§m                         ",
            "§6+9§r de dano",
            "§8Cansaço II§r em quem for atingido",
            "§bEm tempestade§r: invoca um raio no alvo",
            "§7Inquebrável",
        ],
        lore_en=[
            "§7Legendary item of §fNaitPlayer",
            "§8§m                         ",
            "§8Mining Fatigue II§r on hit",
            "§bDuring storms§r: strikes lightning",
        ],
    ),
]


# ----------------------------------------------------------------- itens
def gen_items():
    out = os.path.join(BP, "items")
    os.makedirs(out, exist_ok=True)
    for it in ITEMS:
        name = it["id"].split(":", 1)[1]
        comps = dict(it["components"])
        doc = {
            "format_version": FMT,
            "minecraft:item": {
                "description": {
                    "identifier": it["id"],
                    "menu_category": {
                        "category": it["category"],
                        "is_hidden_in_commands": False,
                    },
                },
                "components": comps,
            },
        }
        with open(os.path.join(out, name + ".json"), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print("item    ->", name + ".json")


# ----------------------------------------------------------------- receitas
def gen_recipes():
    out = os.path.join(BP, "recipes")
    os.makedirs(out, exist_ok=True)
    for it in ITEMS:
        rec = it["recipe"]
        if not rec:
            continue
        name = it["id"].split(":", 1)[1]
        body = {
            "description": {"identifier": "cs:%s_recipe" % name},
            "tags": ["crafting_table"],
            "result": {"item": it["id"]},
            "unlock": rec["unlock"],
        }
        if rec["type"] == "shaped":
            key = {
                k: {"item": v} for k, v in rec["key"].items()
            }
            body["pattern"] = rec["pattern"]
            body["key"] = key
            doc = {
                "format_version": RECIPE_FMT,
                "minecraft:recipe_shaped": body,
            }
        else:
            body["ingredients"] = [{"item": i} for i in rec["ingredients"]]
            doc = {
                "format_version": RECIPE_FMT,
                "minecraft:recipe_shapeless": body,
            }
        with open(os.path.join(out, name + "_recipe.json"), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print("recipe  ->", name + "_recipe.json")


# ------------------------------------------------------- item_texture.json
def gen_item_texture():
    data = {}
    for it in ITEMS:
        name = it["id"].split(":", 1)[1]
        data[name] = {"textures": "textures/items/" + name}
    doc = {
        "resource_pack_name": "creative_squad_itens_lendarios",
        "texture_name": "atlas.items",
        "texture_data": data,
    }
    path = os.path.join(RP, "textures", "item_texture.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("atlas   -> item_texture.json (%d itens)" % len(data))
    return data


# ------------------------------------------------------------- idiomas
def lang_lines(lang):
    lines = []
    lines.append("pack.name=§6§lItens Lendários §8| §fCreative Squad"
                 if lang == "pt" else
                 "pack.name=§6§lLegendary Items §8| §fCreative Squad")
    lines.append(
        "pack.description=§7Os 14 itens lendários da Creative Squad 4 com "
        "suas habilidades reais. §8Feito para Minecraft Bedrock 26.52."
        if lang == "pt" else
        "pack.description=§7All 14 legendary items from Creative Squad 4 with "
        "their real abilities. §8Built for Minecraft Bedrock 26.52."
    )
    for it in ITEMS:
        name = it["id"].split(":", 1)[1]
        lines.append("item.cs.%s.name=%s" % (name, it["pt"] if lang == "pt" else it["en"]))
    return lines


def gen_lang():
    for pack, folder in ((BP, "behavior_pack"), (RP, "resource_pack")):
        out = os.path.join(pack, "texts")
        os.makedirs(out, exist_ok=True)
        for code, lang in (("pt_BR", "pt"), ("en_US", "en")):
            with open(os.path.join(out, code + ".lang"), "w", encoding="utf-8") as fh:
                fh.write("\n".join(lang_lines(lang)) + "\n")
        # languages.json declarando os idiomas suportados
        with open(os.path.join(out, "languages.json"), "w", encoding="utf-8") as fh:
            json.dump(["en_US", "pt_BR"], fh, indent=2)
            fh.write("\n")
        print("lang    ->", folder + "/texts/{pt_BR,en_US}.lang")


# ------------------------------------------------------------- funcoes
def gen_functions():
    out = os.path.join(BP, "functions", "cs")
    itens_dir = os.path.join(out, "itens")
    os.makedirs(itens_dir, exist_ok=True)

    for it in ITEMS:
        name = it["id"].split(":", 1)[1]
        pt = it["pt"]
        with open(os.path.join(itens_dir, name + ".mcfunction"), "w", encoding="utf-8") as fh:
            fh.write("# Da o item lendario: %s\n" % pt)
            fh.write("give @s %s\n" % it["id"])
            fh.write('tellraw @s {"rawtext":[{"text":"§8[§6CS§8] §aVocê recebeu §r%s§a!"}]}\n' % pt)
            fh.write("playsound random.orb @s\n")

    with open(os.path.join(out, "dar_todos.mcfunction"), "w", encoding="utf-8") as fh:
        fh.write("# Da todos os itens lendarios para quem executar\n")
        for it in ITEMS:
            fh.write("give @s %s\n" % it["id"])
        fh.write('tellraw @s {"rawtext":[{"text":"§8[§6CS§8] §aVocê recebeu os §e14 itens lendários§a!"}]}\n')
        fh.write("playsound random.levelup @s\n")

    with open(os.path.join(out, "ajuda.mcfunction"), "w", encoding="utf-8") as fh:
        linhas = [
            "§8§m                                              ",
            "§6§lITENS LENDÁRIOS §8- §fCREATIVE SQUAD §7(26.52)",
            "§8§m                                              ",
            "§e/function cs/dar_todos §7- recebe os 14 itens",
            "§e/function cs/ajuda §7- mostra esta lista",
        ]
        for it in ITEMS:
            name = it["id"].split(":", 1)[1]
            linhas.append("§7/function cs/itens/%s §8- §r%s" % (name, it["pt"]))
        linhas.append("§8§m                                              ")
        linhas.append("§7Também é possível pegar direto: §f/give @s cs:<item>")
        for l in linhas:
            fh.write('tellraw @s {"rawtext":[{"text":"%s"}]}\n' % l.replace('"', '\\"'))
    print("funcion -> cs/ajuda, cs/dar_todos + cs/itens/*")


# ------------------------------------------------- lore usado pelos scripts
def gen_script_data():
    """Gera scripts/lore.js com o texto de lore de cada item (fonte unica)."""
    out = os.path.join(BP, "scripts")
    os.makedirs(out, exist_ok=True)
    data = {}
    for it in ITEMS:
        data[it["id"]] = it["lore_pt"]
    txt = ["// GERADO AUTOMATICAMENTE por tools/gen_content.py - nao editar a mao.",
           "// Texto de lore (tooltip) de cada item lendario.", "",
           "export const LORE = {"]
    for k, v in data.items():
        txt.append('  "%s": [' % k)
        for l in v:
            txt.append('    %s,' % json.dumps(l, ensure_ascii=False))
        txt.append("  ],")
    txt.append("};")
    with open(os.path.join(out, "lore.js"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(txt) + "\n")
    print("script  -> lore.js (%d itens)" % len(data))


# ------------------------------------------------------------- attachables
ATTACHABLES = {
    "capacete_gemeo_bern": ("capacete_bern_layer_1", "helmet"),
    "capacete_gemeo_chip": ("capacete_chip_layer_1", "helmet"),
    "bota_lendaria": ("bota_layer_1", "boots"),
}


def gen_attachables():
    out = os.path.join(RP, "attachables")
    os.makedirs(out, exist_ok=True)
    for name, (tex, kind) in ATTACHABLES.items():
        if kind == "helmet":
            geometry = "geometry.humanoid.armor.helmet"
            script = "variable.helmet_layer_visible = 0.0;"
        else:
            geometry = "geometry.humanoid.armor.boots"
            script = "variable.boot_layer_visible = 0.0;"
        doc = {
            "format_version": "1.10.0",
            "minecraft:attachable": {
                "description": {
                    "identifier": "cs:" + name,
                    "materials": {
                        "default": "armor",
                        "enchanted": "armor_enchanted",
                    },
                    "textures": {
                        "default": "textures/models/armor/" + tex,
                        "enchanted": "textures/misc/enchanted_item_glint",
                    },
                    "geometry": {"default": geometry},
                    "scripts": {"parent_setup": script},
                    "render_controllers": ["controller.render.armor"],
                }
            },
        }
        with open(os.path.join(out, name + ".attachable.json"), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print("attachi ->", name + ".attachable.json")


def main():
    gen_items()
    gen_recipes()
    gen_item_texture()
    gen_lang()
    gen_functions()
    gen_script_data()
    gen_attachables()


if __name__ == "__main__":
    main()
