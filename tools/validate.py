#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador do addon (roda sem o Minecraft).

Checa:
  * todos os JSONs parseiam e os manifests (UUIDs unicos, dependencias);
  * cada item tem textura, chave de idioma e componentes conhecidos;
  * receitas usam apenas itens/vanilla ids validos;
  * blocos da Picareta existem de verdade;
  * efeitos, encantamentos, particulas e entidades usados nos scripts existem;
  * PNGs existem, sao 32x32 e estao no atlas item_texture.json;
  * funcoes .mcfunction referenciam itens existentes.

Uso:  python3 tools/validate.py
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, "src", "behavior_pack")
RP = os.path.join(ROOT, "src", "resource_pack")
DATA = os.path.join(ROOT, "tools", "data")

erros = []
avisos = []


def erro(msg):
    erros.append(msg)


def aviso(msg):
    avisos.append(msg)


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_list(name):
    path = os.path.join(DATA, name + ".json")
    if not os.path.exists(path):
        aviso("lista %s.json ausente - validacao dessa parte ignorada" % name)
        return None
    return set(load(path))


def rel(path):
    return os.path.relpath(path, ROOT)


# ------------------------------------------------------------------ JSON geral
json_files = []
for base in (BP, RP):
    for root, _dirs, files in os.walk(base):
        for f in files:
            if f.endswith(".json"):
                json_files.append(os.path.join(root, f))

parsed = {}
for path in json_files:
    try:
        parsed[path] = load(path)
    except Exception as exc:  # noqa: BLE001
        erro("JSON invalido em %s: %s" % (rel(path), exc))

# ------------------------------------------------------------------ manifests
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
uuids = {}
for pack, label in ((BP, "BP"), (RP, "RP")):
    path = os.path.join(pack, "manifest.json")
    if not os.path.exists(path):
        erro("manifest.json ausente em %s" % label)
        continue
    man = load(path)
    ids = [man["header"]["uuid"]] + [m["uuid"] for m in man.get("modules", [])]
    for u in ids:
        if not UUID_RE.match(u):
            erro("%s: UUID invalido %s" % (label, u))
        if u in uuids:
            erro("%s: UUID duplicado %s (tambem em %s)" % (label, u, uuids[u]))
        uuids[u] = label
    eng = man["header"].get("min_engine_version")
    if eng != [1, 26, 52]:
        aviso("%s: min_engine_version = %s (esperado [1, 26, 52])" % (label, eng))

bp_man = load(os.path.join(BP, "manifest.json"))
rp_man = load(os.path.join(RP, "manifest.json"))
rp_uuid = rp_man["header"]["uuid"]
deps = [d for d in bp_man.get("dependencies", []) if "uuid" in d]
if not any(d["uuid"] == rp_uuid for d in deps):
    erro("BP: dependencia do resource pack ausente (o addon nao acha as texturas)")
script_mods = [m for m in bp_man["modules"] if m.get("type") == "script"]
if not script_mods:
    erro("BP: modulo de script ausente")
else:
    entry = os.path.join(BP, script_mods[0]["entry"])
    if not os.path.exists(entry):
        erro("BP: entry de script nao existe (%s)" % rel(entry))

# ------------------------------------------------------------------ itens
COMPONENTES_OK = {
    "minecraft:allow_off_hand",
    "minecraft:block_placer",
    "minecraft:can_destroy_in_creative",
    "minecraft:cooldown",
    "minecraft:damage",
    "minecraft:digger",
    "minecraft:display_name",
    "minecraft:durability",
    "minecraft:enchantable",
    "minecraft:entity_placer",
    "minecraft:food",
    "minecraft:fuel",
    "minecraft:glint",
    "minecraft:hand_equipped",
    "minecraft:hover_text_color",
    "minecraft:icon",
    "minecraft:interact_button",
    "minecraft:liquid_clipped",
    "minecraft:max_stack_size",
    "minecraft:projectile",
    "minecraft:record",
    "minecraft:repairable",
    "minecraft:shooter",
    "minecraft:should_despawn",
    "minecraft:stacked_by_data",
    "minecraft:tags",
    "minecraft:throwable",
    "minecraft:use_animation",
    "minecraft:use_modifiers",
    "minecraft:wearable",
}
MENU_CATEGORIES = {"construction", "equipment", "items", "nature", "none"}

atlas = load(os.path.join(RP, "textures", "item_texture.json"))["texture_data"]
lang_pt = open(os.path.join(RP, "texts", "pt_BR.lang"), encoding="utf-8").read()
lang_en = open(os.path.join(RP, "texts", "en_US.lang"), encoding="utf-8").read()

vanilla_items = load_list("vanilla_items")
vanilla_blocks = load_list("vanilla_blocks")

itens = {}
for path in sorted(glob.glob(os.path.join(BP, "items", "*.json"))):
    doc = load(path)
    if "minecraft:item" not in doc:
        erro("%s: falta a chave minecraft:item" % rel(path))
        continue
    desc = doc["minecraft:item"]["description"]
    ident = desc["identifier"]
    itens[ident] = doc
    if not ident.startswith("cs:"):
        erro("%s: identificador fora do namespace cs: (%s)" % (rel(path), ident))
    if os.path.basename(path) != ident.split(":")[1] + ".json":
        erro("%s: nome do arquivo nao bate com o identificador %s" % (rel(path), ident))

    cat = desc.get("menu_category", {}).get("category")
    if cat not in MENU_CATEGORIES:
        erro("%s: menu_category invalida (%s)" % (rel(path), cat))

    comps = doc["minecraft:item"]["components"]
    for cname in comps:
        if cname not in COMPONENTES_OK:
            erro("%s: componente desconhecida %s" % (rel(path), cname))

    icon = comps.get("minecraft:icon", {}).get("textures", {}).get("default")
    if not icon:
        erro("%s: sem minecraft:icon" % rel(path))
    else:
        if icon not in atlas:
            erro("%s: textura %s nao esta no item_texture.json" % (rel(path), icon))
        png = os.path.join(RP, "textures", "items", icon + ".png")
        if not os.path.exists(png):
            erro("%s: PNG ausente %s" % (rel(path), rel(png)))
        if atlas.get(icon, {}).get("textures") != "textures/items/" + icon:
            erro("%s: item_texture.json aponta para o caminho errado em %s" % (rel(path), icon))

    nome_key = comps.get("minecraft:display_name", {}).get("value")
    if not nome_key:
        erro("%s: sem display_name" % rel(path))
    else:
        if nome_key not in lang_pt:
            erro("%s: chave %s ausente no pt_BR.lang" % (rel(path), nome_key))
        if nome_key not in lang_en:
            erro("%s: chave %s ausente no en_US.lang" % (rel(path), nome_key))

    # blocos usados pela picareta
    for entry in comps.get("minecraft:digger", {}).get("destroy_speeds", []):
        if vanilla_blocks and entry["block"] not in vanilla_blocks:
            erro("%s: bloco inexistente em destroy_speeds: %s" % (rel(path), entry["block"]))

    # slots de armadura
    wear = comps.get("minecraft:wearable")
    if wear:
        if wear.get("slot") not in {
            "slot.armor.head", "slot.armor.chest", "slot.armor.legs",
            "slot.armor.feet", "slot.armor.body", "slot.weapon.offhand",
        }:
            erro("%s: slot de wearable invalido (%s)" % (rel(path), wear.get("slot")))
        max_stack = comps.get("minecraft:max_stack_size", 1)
        if isinstance(max_stack, dict):
            max_stack = max_stack.get("value", 1)
        if max_stack != 1:
            erro("%s: item vestivel precisa de max_stack_size 1" % rel(path))

if len(itens) != 14:
    aviso("esperados 14 itens lendarios, encontrados %d" % len(itens))

# ------------------------------------------------------------------ receitas
for path in sorted(glob.glob(os.path.join(BP, "recipes", "*.json"))):
    doc = load(path)
    kind = "minecraft:recipe_shaped" if "minecraft:recipe_shaped" in doc else "minecraft:recipe_shapeless"
    body = doc.get(kind)
    if not body:
        erro("%s: tipo de receita desconhecido" % rel(path))
        continue
    result = body["result"]["item"]
    if result not in itens:
        erro("%s: resultado %s nao e um item do addon" % (rel(path), result))
    if kind == "minecraft:recipe_shaped":
        for chave, val in body["key"].items():
            if vanilla_items and val["item"] not in vanilla_items and val["item"] not in itens:
                erro("%s: ingrediente inexistente %s" % (rel(path), val["item"]))
        for linha in body["pattern"]:
            for ch in linha:
                if ch != " " and ch not in body["key"]:
                    erro("%s: padrao usa '%s' sem chave" % (rel(path), ch))
    else:
        for ing in body["ingredients"]:
            if vanilla_items and ing["item"] not in vanilla_items and ing["item"] not in itens:
                erro("%s: ingrediente inexistente %s" % (rel(path), ing["item"]))

# ------------------------------------------------------------------ texturas
for png in glob.glob(os.path.join(RP, "textures", "**", "*.png"), recursive=True):
    try:
        from PIL import Image
        with Image.open(png) as im:
            if "items" in png.split(os.sep) and im.size != (32, 32):
                erro("%s: icone deveria ser 32x32 (e %s)" % (rel(png), im.size))
    except ImportError:
        break
    except Exception as exc:  # noqa: BLE001
        erro("%s: PNG invalido (%s)" % (rel(png), exc))

# ------------------------------------------------------------------ attachables
for path in glob.glob(os.path.join(RP, "attachables", "*.json")):
    doc = load(path)
    desc = doc.get("minecraft:attachable", {}).get("description", {})
    ident = desc.get("identifier")
    if ident not in itens:
        erro("%s: attachable para item inexistente %s" % (rel(path), ident))
    tex = desc.get("textures", {}).get("default")
    if tex and not os.path.exists(os.path.join(RP, tex + ".png")):
        erro("%s: textura de armadura ausente %s" % (rel(path), tex))

# ------------------------------------------------------------------ funcoes
for path in glob.glob(os.path.join(BP, "functions", "**", "*.mcfunction"), recursive=True):
    for linha in open(path, encoding="utf-8"):
        linha = linha.strip()
        if linha.startswith("#") or not linha:
            continue
        m = re.match(r"^give @s (cs:[a-z_]+)", linha)
        if m and m.group(1) not in itens:
            erro("%s: give de item inexistente %s" % (rel(path), m.group(1)))
        m = re.match(r"^tellraw @s (\{.*\})$", linha)
        if m:
            try:
                json.loads(m.group(1))
            except Exception:  # noqa: BLE001
                erro("%s: tellraw com JSON invalido" % rel(path))

# funcoes citadas na ajuda existem?
ajuda = os.path.join(BP, "functions", "cs", "ajuda.mcfunction")
if os.path.exists(ajuda):
    txt = open(ajuda, encoding="utf-8").read()
    for nome in re.findall(r"/function (cs/[\w/]+)", txt):
        if not os.path.exists(os.path.join(BP, "functions", nome + ".mcfunction")):
            erro("ajuda.mcfunction cita /function %s que nao existe" % nome)

# ------------------------------------------------------------------ scripts
vanilla_effects = load_list("vanilla_effects")
vanilla_ench = load_list("vanilla_enchantments")
vanilla_particles = load_list("vanilla_particles")
vanilla_entities = load_list("vanilla_entities")

script_src = ""
for path in glob.glob(os.path.join(BP, "scripts", "*.js")):
    script_src += open(path, encoding="utf-8").read()

conhecidos = set()
for grupo in (vanilla_effects, vanilla_ench, vanilla_particles, vanilla_entities, vanilla_blocks):
    if grupo:
        conhecidos |= grupo
# componentes da API e tipos internos nao sao ids de conteudo
conhecidos |= {
    "minecraft:enchantable", "minecraft:equippable", "minecraft:inventory",
    "minecraft:item", "minecraft:xp_orb", "minecraft:arrow",
}
for p in set(re.findall(r'"(minecraft:[a-z_]+)"', script_src)):
    if p not in conhecidos:
        aviso("script usa id nao catalogado: %s" % p)

# ids de item usados nos scripts precisam existir
for ident in set(re.findall(r'"(cs:[a-z_]+)"', script_src)):
    if ident not in itens:
        # chaves de dynamic property (cs:fakename, cs:herdou_espada_...) nao sao itens
        if ident.split(":")[1].startswith(("fake", "herdou")):
            continue
        erro("script referencia item inexistente: %s" % ident)

# ------------------------------------------------------------------ relatorio
print("JSONs analisados: %d" % len(json_files))
print("Itens: %d | Receitas: %d | Attachables: %d | Funcoes: %d" % (
    len(itens),
    len(glob.glob(os.path.join(BP, "recipes", "*.json"))),
    len(glob.glob(os.path.join(RP, "attachables", "*.json"))),
    len(glob.glob(os.path.join(BP, "functions", "**", "*.mcfunction"), recursive=True)),
))
if avisos:
    print("\nAvisos (%d):" % len(avisos))
    for a in avisos:
        print("  ~ " + a)
if erros:
    print("\nERROS (%d):" % len(erros))
    for e in erros:
        print("  x " + e)
    sys.exit(1)
print("\nTudo certo! Nenhum erro encontrado.")
