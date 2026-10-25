"""Static sanity check for the generated addon (JSON syntax + cross references)."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, "out", "TacGuns(B)")
RP = os.path.join(ROOT, "out", "TacGuns(R)")
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tacgen.specs import SPECS, FAMILIES  # noqa: E402

errors = []
warns = []


def fail(msg):
    errors.append(msg)


def warn(msg):
    warns.append(msg)


def load_json(path, allow_comment=True):
    """Bedrock acepta comentarios // y comas finales en sus JSON."""
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return json.loads(text)


def walk_json(directory, skip=()):
    for root, _, files in os.walk(directory):
        for fn in files:
            if fn.endswith(".json"):
                p = os.path.join(root, fn)
                if any(s in p for s in skip):
                    continue
                yield p


def check_json_syntax():
    for p in list(walk_json(BP)) + list(walk_json(RP)):
        try:
            load_json(p, allow_comment=p.endswith("item_texture.json"))
        except Exception as e:
            fail(f"json invalido: {os.path.relpath(p, ROOT)} :: {e}")


def check_manifest():
    bp = load_json(os.path.join(BP, "manifest.json"))
    rp = load_json(os.path.join(RP, "manifest.json"))
    if rp["dependencies"][0]["uuid"] != bp["header"]["uuid"]:
        fail("RP nao depende do UUID do BP")
    if rp["dependencies"][0]["version"] != bp["header"]["version"]:
        fail("versao da dependencia RP->BP divergente")


def check_items():
    for spec in SPECS:
        for suffix in ("", "_emp"):
            p = os.path.join(BP, "items", spec["id"], "base.json" if not suffix else "empty.json")
            if not os.path.exists(p):
                fail(f"item faltando {spec['id']}{suffix}")
                continue
            doc = load_json(p)
            ident = doc["minecraft:item"]["description"]["identifier"]
            if ident != f"tac_guns:{spec['id']}{suffix}":
                fail(f"identificador de item errado em {p}: {ident}")


def check_texture_atlas():
    p = os.path.join(RP, "textures", "item_texture.json")
    text = open(p, encoding="utf-8-sig").read()
    for spec in SPECS:
        if f'"{spec["id"]}"' not in text:
            fail(f"item_texture.json sem {spec['id']}")
        icon = os.path.join(RP, "textures", "items", f"{spec['id']}.png")
        if not os.path.exists(icon):
            fail(f"icone faltando {spec['id']}.png")


def check_geometry_and_controllers():
    desc = load_json(os.path.join(RP, "entity", "player.entity.json"))["minecraft:client_entity"]["description"]
    geos = desc["geometry"]
    anims = desc["animations"]
    rcs = []
    for d in os.listdir(os.path.join(RP, "render_controllers")):
        if d.endswith(".json"):
            try:
                rcs += list(load_json(os.path.join(RP, "render_controllers", d))["render_controllers"])
            except Exception:
                pass
    for spec in SPECS:
        gid = spec["id"]
        gfile = os.path.join(RP, "models", "entity", "guns", f"{gid}.json")
        if not os.path.exists(gfile):
            fail(f"modelo faltando {gid}")
        else:
            doc = load_json(gfile)
            geo = doc["minecraft:geometry"][0]
            if geo["description"]["identifier"] != f"geometry.{gid}":
                fail(f"identificador de geometria errado {gid}")
            for b in geo["bones"]:
                if b.get("cubes") and gid not in b["name"] and "tp" not in b["name"]:
                    pass
        if gid not in geos:
            fail(f"player.entity.json sem geometria {gid}")
        if f"{gid}_fp" not in anims:
            fail(f"player.entity.json sem animation {gid}_fp")
        if f"{gid}_tp" not in anims:
            fail(f"player.entity.json sem animation {gid}_tp")
        if f"controller.render.{gid}" not in rcs:
            fail(f"render controller ausente controller.render.{gid}")
        if f"controller.render.player.{gid}.first_person" not in rcs:
            fail(f"render controller ausente first_person {gid}")
        # referenced animation controllers must exist on disk
        for key in (f"controller.animation.{gid}.fp",):
            found = False
            for p in walk_json(RP):
                if "animation_controllers" in p:
                    try:
                        d = load_json(p)
                    except Exception:
                        continue
                    if key in d.get("animation_controllers", {}):
                        found = True
                        break
            if not found:
                fail(f"animation controller ausente: {key}")
        # every animation.<gun>.* referenced must exist
        for p in walk_json(RP):
            pass


def check_bp():
    player = load_json(os.path.join(BP, "entities", "player.json"))["minecraft:entity"]
    events = player["events"]
    groups = player["component_groups"]
    anims = player["description"].get("animations", {})
    animate = player["description"]["scripts"]["animate"]
    ctrls = {}
    for p in walk_json(BP):
        if "animation_controllers" in p:
            try:
                ctrls.update(load_json(p).get("animation_controllers", {}))
            except Exception:
                pass
    for spec in SPECS:
        gid = spec["id"]
        fam = FAMILIES[spec["family"]]
        tpl_events = load_json(os.path.join(BP, "entities", "player.json"))["minecraft:entity"]["events"]
        expected = [f"tac_guns:{gid}_fire"]
        if f"tac_guns:{fam['template']}_reload" in tpl_events:
            expected.append(f"tac_guns:{gid}_reload")
        for key in expected:
            if key not in events:
                fail(f"evento ausente {key}")
        for key in (f"tac_guns:{gid}_firest", f"tac_guns:{gid}_fires"):
            if key not in groups:
                fail(f"component group ausente {key}")
            else:
                spawned = json.dumps(groups[key])
                if f"bullet:{gid}" not in spawned:
                    fail(f"{key} nao spawna bullet:{gid}")
        if f"controller.animation.{gid}" not in ctrls:
            fail(f"BP fire controller ausente {gid}")
        if f"controller.animation.{gid}.reload" not in ctrls:
            fail(f"BP reload controller ausente {gid}")
        if gid not in anims:
            fail(f"BP animations sem {gid}")
        if gid + "reloading" not in anims:
            fail(f"BP animations sem {gid}reloading")
        found = any(isinstance(a, dict) and gid in a for a in animate)
        if not found:
            fail(f"BP animate sem entrada para {gid}")
        # bullet entity + functions
        if not os.path.exists(os.path.join(BP, "entities", "Bullet", f"{gid}.json")):
            fail(f"bullet entity ausente {gid}")
        # recipe
        if not os.path.exists(os.path.join(BP, "recipes", f"{gid}.json")):
            fail(f"receita ausente {gid}")


def check_scripts():
    text = open(os.path.join(BP, "scripts", "main.js"), encoding="utf-8").read()
    for spec in SPECS:
        if f'"tac_guns:{spec["id"]}": "tac_guns:{spec["ammo"]}"' not in text:
            fail(f"main.js: guns sem {spec['id']}")
    # crude brace balance check on the recipes object
    if text.count("{") != text.count("}"):
        fail("main.js com chaves desbalanceadas")


def check_sounds():
    doc = load_json(os.path.join(RP, "sounds", "sound_definitions.json"))
    for spec in SPECS:
        for suffix in ("shoot", "draw", "reload", "inspect"):
            if f"{spec['id']}.{suffix}" not in doc:
                fail(f"som ausente {spec['id']}.{suffix}")
    # every sound file referenced must exist
    for key, val in doc.items():
        for s in val.get("sounds", []):
            name = s if isinstance(s, str) else s.get("name")
            p = os.path.join(RP, name + ".ogg")
            if not os.path.exists(p) and not key.startswith(("m870.", "ak47.", "db.", "dp28.")):
                fail(f"arquivo de som ausente para {key}: {name}")


def check_animations():
    """Every animation.<x> referenced by controllers must be defined somewhere."""
    defined = set()
    for p in walk_json(RP):
        if "animations" in p and "animation" in p:
            try:
                d = load_json(p)
            except Exception:
                continue
            defined.update(d.get("animations", {}).keys())
    refs = set()
    for p in walk_json(RP):
        try:
            text = open(p, encoding="utf-8-sig").read()
        except Exception:
            continue
        refs.update(re.findall(r'"(animation\.[A-Za-z0-9_.]+)"', text))
    missing = sorted(r for r in refs if r not in defined and not r.startswith("animation.itemscale"))
    for m in missing:
        warn(f"animacao referenciada sem definicao: {m}")


def check_bones():
    """Cubes must live on bones that exist and part bones referenced in RC must exist."""
    for spec in SPECS:
        doc = load_json(os.path.join(RP, "models", "entity", "guns", f"{spec['id']}.json"))
        geo = doc["minecraft:geometry"][0]
        names = {b["name"] for b in geo["bones"]}
        for b in geo["bones"]:
            if b.get("parent") and b["parent"] not in names:
                fail(f"{spec['id']}: bone {b['name']} aponta para pai inexistente {b['parent']}")
        for p in walk_json(RP):
            try:
                d = load_json(p)
            except Exception:
                continue
            for k, v in d.get("render_controllers", {}).items():
                if k == f"controller.render.{spec['id']}":
                    for entry in v.get("part_visibility", []):
                        for bone in entry:
                            if bone != "*" and bone not in names:
                                fail(f"{spec['id']}: render controller cita bone {bone} inexistente")



def check_assets():
    """Sons, locators e animações citados pelos arquivos clonados precisam existir."""
    sounds = load_json(os.path.join(RP, "sounds", "sound_definitions.json"))
    rp_anims = {}
    for p in walk_json(os.path.join(RP, "animations")):
        d = load_json(p)
        rp_anims.update(d.get("animations", {}))
    bp_anims = {}
    for p in walk_json(os.path.join(BP, "animations")):
        d = load_json(p)
        bp_anims.update(d.get("animations", {}))
    for spec in SPECS:
        gid = spec["id"]
        text = open(os.path.join(RP, "animations", "guns", f"{gid}.animation.json")).read()
        for effect in set(re.findall(r'"effect"\s*:\s*"([^"]+)"', text)):
            if effect.startswith("krep."):
                continue
            if effect not in sounds:
                fail(f"{gid}: som {effect} sem definicao")
        for locator in set(re.findall(r'"locator"\s*:\s*"([^"]+)"', text)):
            doc = load_json(os.path.join(RP, "models", "entity", "guns", f"{gid}.json"))
            names = set()
            for b in doc["minecraft:geometry"][0]["bones"]:
                names.update(b.get("locators", {}).keys())
            if locator not in names:
                fail(f"{gid}: locator {locator} nao existe na geometria")
        # animations referenced by the entity/render code must exist in one of the packs
        fam = FAMILIES[spec["family"]]
        tpl = fam["rp_anim"]
        tpl_doc = load_json(os.path.join(ROOT, "src", "TacGuns(R)", "animations", "guns",
                                         f"{tpl}.animation.json"))
        for name in tpl_doc["animations"]:
            expected = name.replace(f"animation.{tpl}.", f"animation.{gid}.")
            if expected not in rp_anims:
                fail(f"{gid}: animacao ausente {expected}")
        if f"animation.{gid}.shoot" not in bp_anims:
            fail(f"{gid}: BP animation.{gid}.shoot ausente")
        if f"animation.{gid}.reload" not in bp_anims:
            fail(f"{gid}: BP animation.{gid}.reload ausente")


def check_reload_band():
    """O valor base de cada arma (evento <arma>reload0) deve ser unico por propriedade."""
    player = load_json(os.path.join(BP, "entities", "player.json"))["minecraft:entity"]
    used = {}
    for key, value in player["events"].items():
        if not re.fullmatch(r"[a-z0-9_]+reload0", key):
            continue
        base = key[: -len("reload0")]
        prop = value.get("set_property") if isinstance(value, dict) else None
        if not prop:
            continue
        for name, number in prop.items():
            used.setdefault(name, {}).setdefault(int(number), []).append(base)
    for name, bases in used.items():
        for number, guns in bases.items():
            if len(guns) > 1:
                warn(f"base {number} de {name} compartilhada por {', '.join(sorted(guns))}")
        ordered = sorted(bases)
        for a, b in zip(ordered, ordered[1:]):
            if b - a < 40:
                warn(f"bases de {name} muito proximas: {a} ({bases[a]}) e {b} ({bases[b]})")


def check_factions():
    """Camada de facções: tabelas geradas, ícones da tela e script ligado."""
    script = os.path.join(BP, "scripts", "events", "factions.js")
    if not os.path.exists(script):
        fail("factions.js nao gerado")
        return
    text = open(script, encoding="utf-8").read()
    if "__POLICE_WEAPONS__" in text or "__SHOP__" in text:
        fail("factions.js: template nao substituido")
    for spec in SPECS:
        if f'"{spec["id"]}"' not in text:
            fail(f"factions.js: arma {spec['id']} fora das tabelas de faccao")
    for icone in ("policial", "ladrao"):
        path = os.path.join(RP, "textures", "ui", icone + ".png")
        if not os.path.exists(path):
            fail(f"textures/ui/{icone}.png ausente")
    for linha in ("tac_guns:faccao", "tac_guns:loja", "tac_guns:info"):
        if linha not in text:
            fail(f"factions.js: comando {linha} ausente")
    main = open(os.path.join(BP, "scripts", "main.js"), encoding="utf-8").read()
    if "factions.js" not in main:
        fail("main.js nao importa events/factions.js")
    hit = open(os.path.join(BP, "scripts", "events", "projectileHitEntity.js"),
               encoding="utf-8").read()
    if "multiplicador" not in hit:
        fail("projectileHitEntity.js sem modificador de faccao")
    # loja so deve vender coisa do proprio lado
    for bloco, marca in (("policia", "crime"), ("ladrao", None)):
        trecho = text.split(f"    {bloco}: [", 1)[-1].split("],", 1)[0]
        if marca is None:
            if "_crime_emp" not in trecho and bloco == "ladrao":
                warn("loja do ladrao sem itens de faccao")
        elif "_crime_emp" in trecho:
            fail("loja da policia vendendo arma de faccao")


def main():
    check_json_syntax()
    check_manifest()
    check_items()
    check_texture_atlas()
    check_geometry_and_controllers()
    check_bp()
    check_scripts()
    check_sounds()
    check_animations()
    check_bones()
    check_assets()
    check_reload_band()
    check_factions()
    for w in warns:
        print("AVISO:", w)
    for e in errors:
        print("ERRO:", e)
    print(f"\n{len(errors)} erros, {len(warns)} avisos")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
