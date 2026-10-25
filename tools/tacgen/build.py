"""Build the expanded TacGuns addon: out/TacGuns(B) + out/TacGuns(R).

Every new weapon is produced by cloning one of the five original weapons that
already implements the full TacGuns behaviour (fire, reload, tactical reload,
inspect, draw, sprint, sway, recoil, third person, HUD counters) and swapping
in a freshly generated voxel model + atlas + inventory icon.
"""
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from PIL import Image, ImageDraw  # noqa: E402

from tacgen import preview, texture as texmod  # noqa: E402
from tacgen.analysis import load_template  # noqa: E402
from tacgen.clone import dump, gun_obj, load, write_text  # noqa: E402
from tacgen.designs import DESIGNS  # noqa: E402
from tacgen.designs_crime import DESIGNS_CRIME  # noqa: E402

ALL_DESIGNS = dict(DESIGNS)
ALL_DESIGNS.update(DESIGNS_CRIME)
from tacgen.geometry import build_geometry  # noqa: E402
from tacgen.specs import (BY_ID, FAMILIES, RECOLORS, RIGS, SPECS, recipe_items,
                         shop_entries,  # noqa: E402
                         recipe_pattern)

SRC_BP = os.path.join(ROOT, "src", "TacGuns(B)")
SRC_RP = os.path.join(ROOT, "src", "TacGuns(R)")
OUT = os.path.join(ROOT, "out")
OUT_BP = os.path.join(OUT, "TacGuns(B)")
OUT_RP = os.path.join(OUT, "TacGuns(R)")

TEMPLATE_AMMO = {"mk18": "556x45mm", "glock17": "9x19mm", "coltpython": "357magnum",
                 "awp": "338lapua", "m870": "12gauge"}
# score value that counts as "full magazine" for the inspect animation
ATTACH_PROPS = [("att_optic", "tac_guns:att_optic"),
                ("att_suppressor", "tac_guns:att_suppressor"),
                ("att_laser", "tac_guns:att_laser"),
                ("att_grip", "tac_guns:att_grip"),
                ("att_exmag", "tac_guns:att_exmag")]

CRIME_ATTACH_PROPS = [("att_tape_optic", "tac_guns:att_tape_optic"),
                      ("att_dualmag", "tac_guns:att_dualmag")]

ATTACHMENTS = [
    dict(id="att_optic", name="Red dot", prop="tac_guns:att_optic",
         craft={"minecraft:iron_ingot": 4, "minecraft:glass_pane": 2},
         desc="Mira de ponto vermelho com trilho universal."),
    dict(id="att_suppressor", name="Supressor", prop="tac_guns:att_suppressor",
         craft={"minecraft:iron_ingot": 6, "minecraft:wool": 3},
         desc="Moderador de som com rosca 1/2x28."),
    dict(id="att_laser", name="Lanterna/Laser", prop="tac_guns:att_laser",
         craft={"minecraft:iron_ingot": 3, "minecraft:glowstone_dust": 2,
                "minecraft:redstone": 2},
         desc="Modulo de lanterna com laser de mira."),
    dict(id="att_grip", name="Foregrip", prop="tac_guns:att_grip",
         craft={"minecraft:iron_ingot": 3, "minecraft:charcoal": 1},
         desc="Empunhadura dianteira vertical."),
    dict(id="att_exmag", name="Carregador estendido", prop="tac_guns:att_exmag",
         craft={"minecraft:iron_ingot": 5},
         desc="Extensor de carregador (+capacidade visual)."),
    # --- improvisados (linha de faccao)
    dict(id="att_tape_optic", name="Luneta amarrada", prop="tac_guns:att_tape_optic",
         craft={"minecraft:iron_ingot": 2, "minecraft:string": 2},
         desc="Luneta de caca presa com fita isolante no recebedor."),
    dict(id="att_dualmag", name="Carregador duplo fitado", prop="tac_guns:att_dualmag",
         craft={"minecraft:iron_ingot": 2, "minecraft:string": 1},
         desc="Dois carregadores presos com fita para recarga rapida."),
]

TEMPLATE_FULL = {"mk18": 31, "glock17": 18, "coltpython": 6, "awp": 6, "m870": 6}



def rename_geometry(doc, ident):
    """Renomeia o identificador da geometria nos dois formatos usados pelo pack.

    Formato novo: {"minecraft:geometry": [{"description": {"identifier": ...}}]}
    Formato antigo: {"geometry.nome": {"bones": [...]}}
    """
    geo = doc.get("minecraft:geometry")
    if geo is not None:
        items = geo if isinstance(geo, list) else [geo]
        for g in items:
            if isinstance(g, dict) and isinstance(g.get("description"), dict):
                g["description"]["identifier"] = ident
    for key in [k for k in doc if k.startswith("geometry.")]:
        valor = doc.pop(key)
        doc[ident] = valor
    return doc


def read(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def load_loose(path):
    text = read(path)
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return json.loads(text)


class Build:
    def __init__(self):
        self.geo = {}
        self.atlas = os.path.join(OUT, "_atlas.png")

    # ------------------------------------------------------------------ setup
    def reset(self):
        if os.path.isdir(OUT):
            shutil.rmtree(OUT)
        os.makedirs(OUT)
        shutil.copytree(SRC_BP, OUT_BP)
        shutil.copytree(SRC_RP, OUT_RP)
        texmod.save_atlas(self.atlas)
        self.tpl_cache = {t: load_template(t) for t in RIGS}

    # --------------------------------------------------------------- geometry
    def build_model(self, spec):
        fam = FAMILIES[spec["family"]]
        rig = RIGS[fam["template"]]
        tpl = self.tpl_cache[fam["template"]]
        design = ALL_DESIGNS[spec.get("design") or spec["id"]]()
        recolor = RECOLORS.get(spec["recolor"]) if spec.get("recolor") else None
        if recolor:
            for box in design.boxes:
                box.mat = recolor.get(box.mat, box.mat)
        cfg = dict(template=fam["template"], body_parent=rig["body_parent"],
                   part_bones=rig["part_bones"], locator_prefix=spec["id"],
                   scale=spec.get("scale", 1.0), faction=spec.get("faction"))
        doc = build_geometry(tpl, design, cfg)
        rename_geometry(doc, f"geometry.{spec['id']}")
        dump(os.path.join(OUT_RP, "models", "entity", "guns", f"{spec['id']}.json"), doc)
        self.geo[spec["id"]] = doc["minecraft:geometry"][0]

        # first person arms: same skeleton, own identifier
        root = load(os.path.join(SRC_RP, "models", "entity", "guns",
                                 f"{fam['template']}root.json"))
        rename_geometry(root, f"geometry.{spec['id']}root")
        dump(os.path.join(OUT_RP, "models", "entity", "guns", f"{spec['id']}root.json"), root)

    # ---------------------------------------------------------------- texture
    def build_textures(self, spec):
        gun_tex = os.path.join(OUT_RP, "textures", "gun", f"{spec['id']}.png")
        shutil.copyfile(self.atlas, gun_tex)

        tmp = os.path.join(OUT, f"_icon_{spec['id']}.png")
        preview.render(self.geo[spec["id"]], gun_tex, tmp, yaw=38, pitch=22,
                       size=(320, 320), bg=(0, 0, 0), quiet=True)
        img = Image.open(tmp).convert("RGBA")
        px = img.load()
        for y in range(img.height):
            for x in range(img.width):
                r, g, b, a = px[x, y]
                if r < 24 and g < 26 and b < 30:
                    px[x, y] = (0, 0, 0, 0)
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        scale = min(58 / img.width, 58 / img.height)
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.LANCZOS)
        icon = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        icon.paste(img, ((64 - img.width) // 2, (64 - img.height) // 2), img)
        icon.save(os.path.join(OUT_RP, "textures", "items", f"{spec['id']}.png"))
        os.remove(tmp)

    # -------------------------------------------------------------------- RP
    def rp_animation(self, spec):
        fam = FAMILIES[spec["family"]]
        tpl = fam["rp_anim"]
        doc = load(os.path.join(SRC_RP, "animations", "guns", f"{tpl}.animation.json"))
        anims = {}
        for name, anim in doc["animations"].items():
            anims[gun_obj(name, tpl, spec["id"])] = gun_obj(anim, tpl, spec["id"], bare=False) \
                if False else self._anims(anim, tpl, spec["id"])
        dump(os.path.join(OUT_RP, "animations", "guns", f"{spec['id']}.animation.json"),
             {"format_version": doc.get("format_version", "1.10.0"), "animations": anims})

    @staticmethod
    def _anims(anim, tpl, gid):
        return gun_obj(anim, tpl, gid, bare=False, command_strings_only=True)

    def rp_fp_controller(self, spec):
        fam = FAMILIES[spec["family"]]
        tpl = fam["rp_anim"]
        doc = load(os.path.join(SRC_RP, "animation_controllers", f"{tpl}.json"))
        out = {}
        for name, ctrl in doc["animation_controllers"].items():
            if tpl not in name:
                continue
            out[gun_obj(name, tpl, spec["id"])] = gun_obj(ctrl, tpl, spec["id"], bare=True)
        dump(os.path.join(OUT_RP, "animation_controllers", f"{spec['id']}.json"),
             {"format_version": doc.get("format_version", "1.10.0"), "animation_controllers": out})

    def rp_attachables(self, spec):
        fam = FAMILIES[spec["family"]]
        for suffix in ("", "emp"):
            src = os.path.join(SRC_RP, "attachables", "guns", f"{fam['template']}{suffix}.json")
            if not os.path.exists(src):
                # modelos sem variante "vazia" no pack original: reaproveita a cheia,
                # senao o item _emp aparece como sprite 2D na mao
                alt = os.path.join(SRC_RP, "attachables", "guns", f"{fam['template']}.json")
                if suffix and os.path.exists(alt):
                    src = alt
                else:
                    continue
            doc = load(src)
            desc = doc["minecraft:attachable"]["description"]
            desc["identifier"] = f"tac_guns:{spec['id']}{suffix}"
            dump(os.path.join(OUT_RP, "attachables", "guns", f"{spec['id']}{suffix}.json"), doc)

    def rp_render_controllers(self, spec):
        fam = FAMILIES[spec["family"]]
        tpl = fam["template"]
        found = {}
        for fn in os.listdir(os.path.join(SRC_RP, "render_controllers")):
            if not fn.endswith(".json"):
                continue
            try:
                doc = load_loose(os.path.join(SRC_RP, "render_controllers", fn))
            except Exception:
                continue
            found.update(doc.get("render_controllers", {}))
        out = {}
        for key in (f"controller.render.player.{tpl}.first_person", f"controller.render.{tpl}"):
            if key in found:
                rctrl = gun_obj(found[key], tpl, spec["id"])
                if key == f"controller.render.{tpl}":
                    vis = rctrl.setdefault("part_visibility", [])
                    props = list(ATTACH_PROPS)
                    if spec.get("faction") == "crime":
                        props += CRIME_ATTACH_PROPS
                    for bone, prop in props:
                        vis.append({bone: f"q.property('{prop}') == true"})
                out[gun_obj(key, tpl, spec["id"])] = rctrl
        dump(os.path.join(OUT_RP, "render_controllers", f"extra_{spec['id']}.json"),
             {"format_version": "1.8.0", "render_controllers": out})

    def rp_player(self):
        path = os.path.join(OUT_RP, "entity", "player.entity.json")
        doc = load(path)
        desc = doc["minecraft:client_entity"]["description"]
        scripts = desc["scripts"]
        templates = sorted({FAMILIES[s["family"]]["template"] for s in SPECS})

        # per gun variables + textures + geometry + animation map + animate list
        added_vars = []
        for spec in SPECS:
            tpl = FAMILIES[spec["family"]]["template"]
            gid = spec["id"]
            for line in list(scripts["pre_animation"]):
                if line.startswith("variable.holding_all_guns"):
                    continue
                new = gun_obj(line, tpl, gid)
                if new != line:
                    scripts["pre_animation"].append(new)
                    added_vars.append(new)
            for key, value in list(desc["textures"].items()):
                new = gun_obj(key, tpl, gid)
                if new != key:
                    desc["textures"][new] = gun_obj(value, tpl, gid)
            for key, value in list(desc["geometry"].items()):
                if key == f"{tpl}root":
                    desc["geometry"][f"{gid}root"] = f"geometry.{gid}root"
                    continue
                new = gun_obj(key, tpl, gid)
                if new != key:
                    desc["geometry"][new] = gun_obj(value, tpl, gid)
            for key, value in list(desc["animations"].items()):
                new = gun_obj(key, tpl, gid)
                if new != key:
                    desc["animations"][new] = gun_obj(value, tpl, gid)
            for entry in list(scripts["animate"]):
                if isinstance(entry, str):
                    new = gun_obj(entry, tpl, gid)
                    if new != entry:
                        scripts["animate"].append(new)
                elif isinstance(entry, dict):
                    new_entry, changed = {}, False
                    for key, value in entry.items():
                        new_key = gun_obj(key, tpl, gid)
                        if new_key != key:
                            changed = True
                        new_entry[new_key] = gun_obj(value, tpl, gid) if isinstance(value, str) else value
                    if changed:
                        scripts["animate"].append(new_entry)
            for entry in list(desc["render_controllers"]):
                if isinstance(entry, dict):
                    for key, value in entry.items():
                        if isinstance(value, str) and gun_obj(value, tpl, gid) != value:
                            desc["render_controllers"].append(gun_obj(entry, tpl, gid))
                            break

        # holding_all_guns must cover the new weapons
        for i, line in enumerate(scripts["pre_animation"]):
            if line.startswith("variable.holding_all_guns"):
                extra = "".join(
                    f" || query.get_equipped_item_name=='{s['id']}'"
                    f" || query.get_equipped_item_name=='{s['id']}_emp'" for s in SPECS)
                scripts["pre_animation"][i] = line.rstrip(";") + extra + ";"

        # recoil + first person animation hooks
        for entry in scripts["animate"]:
            if isinstance(entry, dict) and "gun_recoil_fp" in entry:
                value = entry["gun_recoil_fp"]
                inner = value[value.index("(") + 1:value.rindex(")")]
                flags = inner.split("||")
                for spec in SPECS:
                    flag = f"v.{spec['id']}b"
                    if flag not in flags:
                        flags.append(flag)
                entry["gun_recoil_fp"] = f"variable.is_first_person && ({'||'.join(flags)})"
        dump(path, doc)

    def rp_draw_controller(self):
        path = os.path.join(OUT_RP, "animation_controllers", "draw.json")
        doc = load(path)
        ctrl = doc["animation_controllers"]["controller.animation.draw"]
        order = ["m134", "mk18", "ak47", "awp", "coltpython", "deagle", "db", "glock17",
                 "m870", "dp28"] + [s["id"] for s in SPECS]
        variables = [f"v.{g}" for g in order]
        ctrl["states"]["setup"] = {"transitions": [{f"draw.{g}": f"v.{g}"} for g in order]}
        none_held = " && ".join(f"!{v}" for v in variables)
        for g in order:
            others = [{"setup": none_held}] + [{f"draw.{o}": f"v.{o}"} for o in order if o != g]
            ctrl["states"][f"draw.{g}"] = {"animations": [{f"{g}_fp_draw": f"v.{g}"}],
                                           "transitions": others}
        dump(path, doc)

    # -------------------------------------------------------------------- BP
    def bp_items(self, spec):
        fam = FAMILIES[spec["family"]]
        tpl = fam["template"]
        for suffix, src_name, movement, label in (("", "base", 0.85, spec["name"]),
                                                  ("_emp", "empty", 1.0, spec["name"] + " (vazio)")):
            doc = load(os.path.join(SRC_BP, "items", tpl, f"{src_name}.json"))
            item = doc["minecraft:item"]
            item["description"]["identifier"] = f"tac_guns:{spec['id']}{suffix}"
            item["components"]["minecraft:icon"] = {"texture": spec["id"]}
            item["components"]["minecraft:display_name"] = {"value": label}
            item["components"]["minecraft:chargeable"] = {"movement_modifier": movement}
            dump(os.path.join(OUT_BP, "items", spec["id"],
                              "base.json" if not suffix else "empty.json"), doc, indent=2)

    def bp_bullet(self, spec):
        fam = FAMILIES[spec["family"]]
        tpl = fam["bullet_from"]
        doc = load_loose(os.path.join(SRC_BP, "entities", "Bullet", f"{tpl}.json"))
        doc = gun_obj(doc, tpl, spec["id"])
        ent = doc["minecraft:entity"]
        ent["description"]["identifier"] = f"bullet:{spec['id']}"
        # keep the family's flight model, slightly tune power to the damage value
        base = {"mk18": 40.1, "glock17": 9.0, "coltpython": 14.0, "awp": 60.0, "m870": 6.0}[tpl]
        power = round(base * (spec["damage"] / {"mk18": 6.5, "glock17": 5, "coltpython": 14,
                                                "awp": 40.5, "m870": 4.125}[tpl]) ** 0.35, 2)
        for group in ent.get("component_groups", {}).values():
            proj = group.get("minecraft:projectile")
            if proj and "power" in proj:
                proj["power"] = power
        dump(os.path.join(OUT_BP, "entities", "Bullet", f"{spec['id']}.json"), doc, indent=2)

    def bp_functions(self, spec):
        fam = FAMILIES[spec["family"]]
        tpl = fam["template"]
        for kind in ("quantity", "reload"):
            src = os.path.join(SRC_BP, "functions", f"{tpl}{kind}.mcfunction")
            if not os.path.exists(src):
                continue
            text = read(src)
            text = gun_obj(text, tpl, spec["id"])
            text = text.replace(f"tac_guns:{TEMPLATE_AMMO[tpl]}", f"tac_guns:{spec['ammo']}")
            write_text(os.path.join(OUT_BP, "functions", f"{spec['id']}{kind}.mcfunction"), text)

    def bp_gun_controller(self, spec):
        fam = FAMILIES[spec["family"]]
        tpl = fam["bp_gun_ac"]
        doc = load_loose(os.path.join(SRC_BP, "animation_controllers", "gun", f"{tpl}.json"))
        out = {}
        for name, ctrl in doc["animation_controllers"].items():
            new_name = gun_obj(name, tpl, spec["id"])
            new_ctrl = gun_obj(ctrl, tpl, spec["id"])
            new_ctrl = self.shift(new_ctrl, spec)
            out[new_name] = new_ctrl
        dump(os.path.join(OUT_BP, "animation_controllers", "gun", f"{spec['id']}.json"),
             {"format_version": doc.get("format_version", "1.10.0"), "animation_controllers": out})

    # ------------------------------------------------------------- property band
    @staticmethod
    def shift(doc, spec):
        fam = FAMILIES[spec["family"]]
        prop = fam["prop"]
        if not prop:
            return doc
        delta = (spec.get("prop_new") or fam["prop_base"]) - fam["prop_base"]
        lo = fam["prop_base"]
        hi = fam["prop_base"] + fam["prop_span"]
        pattern = re.compile(r"(property\('" + re.escape(prop) + r"'\)\s*(?:==|>=|<=|>|<)\s*)(\d+)")

        def walk(node):
            if isinstance(node, dict):
                out = {}
                for k, v in node.items():
                    # event filters / set_property blocks carry the band as a raw number
                    if k == "domain" and v == prop:
                        out[k] = v
                        continue
                    if k in ("value",) and isinstance(v, int) and isinstance(node.get("domain"), str) \
                            and lo <= v <= hi:
                        out[k] = v + delta
                        continue
                    if k == "set_property" and isinstance(v, dict) and prop in v:
                        block = dict(v)
                        if lo <= block[prop] <= hi:
                            block[prop] = block[prop] + delta
                        out[k] = block
                        continue
                    out[k] = walk(v)
                return out
            if isinstance(node, list):
                return [walk(v) for v in node]
            if isinstance(node, str):
                return pattern.sub(lambda m: m.group(1) + str(int(m.group(2)) + delta)
                                   if lo <= int(m.group(2)) <= hi else m.group(0), node)
            return node

        return walk(doc)

    # ------------------------------------------------------------ shared patches
    def bp_player(self):
        path = os.path.join(OUT_BP, "entities", "player.json")
        doc = load(path)
        ent = doc["minecraft:entity"]
        events = ent["events"]
        groups = ent["component_groups"]
        anims = ent["description"]["animations"]
        animate = ent["description"]["scripts"]["animate"]

        for spec in SPECS:
            fam = FAMILIES[spec["family"]]
            tpl = fam["template"]
            gid = spec["id"]

            for suffix in ("_firest", "_fires", "_fire2"):
                key = f"tac_guns:{tpl}{suffix}"
                if key in groups:
                    groups[f"tac_guns:{gid}{suffix}"] = self.shift(gun_obj(groups[key], tpl, gid), spec)

            for key in list(events):
                if key == f"tac_guns:{tpl}_reload":
                    events[f"tac_guns:{gid}_reload"] = self.shift(gun_obj(events[key], tpl, gid), spec)
                elif re.fullmatch(re.escape(tpl) + r"reload\d*", key):
                    events[gun_obj(key, tpl, gid)] = self.shift(gun_obj(events[key], tpl, gid), spec)
                elif key.startswith(f"tac_guns:{tpl}_fire"):
                    events[gun_obj(key, tpl, gid)] = self.shift(gun_obj(events[key], tpl, gid), spec)

            for key, value in list(anims.items()):
                new = gun_obj(key, tpl, gid)
                if new != key:
                    anims[new] = gun_obj(value, tpl, gid)

            for entry in list(animate):
                if isinstance(entry, str):
                    new = gun_obj(entry, tpl, gid)
                    if new != entry:
                        animate.append(new)
                elif isinstance(entry, dict):
                    if any(gun_obj(k, tpl, gid) != k for k in entry.keys()):
                        animate.append(gun_obj(entry, tpl, gid))
        dump(path, doc)

    def bp_reload_controllers(self):
        path = os.path.join(OUT_BP, "animation_controllers", "556mm.json")
        doc = load(path)
        ctrls = doc["animation_controllers"]
        for spec in SPECS:
            fam = FAMILIES[spec["family"]]
            tpl = fam["bp_reload_ac"]
            key = f"controller.animation.{tpl}.reload"
            if key not in ctrls:
                continue
            ctrls[gun_obj(key, tpl, spec["id"])] = self.shift(
                gun_obj(ctrls[key], tpl, spec["id"]), spec)
        dump(path, doc)

    def bp_animations(self):
        path = os.path.join(OUT_BP, "animations", "guns.json")
        doc = load(path)
        anims = doc["animations"]
        for spec in SPECS:
            fam = FAMILIES[spec["family"]]
            tpl = fam["template"]
            for name, anim in list(anims.items()):
                if not name.startswith(f"animation.{tpl}."):
                    continue
                new = gun_obj(anim, tpl, spec["id"])
                text = json.dumps(new)
                text = text.replace(f"tac_guns:{TEMPLATE_AMMO[tpl]}", f"tac_guns:{spec['ammo']}")
                anims[gun_obj(name, tpl, spec["id"])] = json.loads(text)
        dump(path, doc)

    def bp_inspect_controller(self):
        path = os.path.join(OUT_BP, "animation_controllers", "inspect.json")
        doc = load(path)
        ctrl = doc["animation_controllers"]["controller.animation.inspect"]
        states = ctrl["states"]
        unequipped = states["unequipped"]
        for spec in SPECS:
            fam = FAMILIES[spec["family"]]
            tpl = fam["template"]
            gid = spec["id"]
            full = TEMPLATE_FULL[tpl]
            length = self.inspect_length(gid)
            unequipped["on_entry"].append(f"/stopsound @s {gid}.inspect")
            unequipped["transitions"].append({
                gid: (f"!q.is_sneaking && q.get_equipped_item_name=='{gid}' && "
                      f"q.scoreboard('{gid}') == {full} && q.mark_variant == 0 && v.attack_time")})
            states[gid] = {
                "on_entry": ["v.time = q.life_time;", "@s tac_guns:inspect", f"/playsound {gid}.inspect"],
                "transitions": [{"unequipped":
                                 f"q.get_equipped_item_name!='{gid}' || (q.life_time - v.time) >= "
                                 f"{length:.2f} || q.is_using_item"}],
            }
        dump(path, doc)

    def bp_scope_controller(self):
        path = os.path.join(OUT_BP, "animation_controllers", "scope.json")
        doc = load(path)
        states = doc["animation_controllers"]["controller.animation.scope"]["states"]

        def extend(expr, names, mode):
            if mode == "enter":
                extra = "".join(f" || q.get_equipped_item_name=='{n}'" for n in names)
            else:
                extra = "".join(f" || (q.is_sneaking && q.get_equipped_item_name=='{n}')" for n in names)
            return expr + extra

        names = []
        for spec in SPECS:
            names += [spec["id"], f"{spec['id']}_emp"]
        for transition in states["setup"]["transitions"]:
            for target, expr in transition.items():
                transition[target] = extend(expr, names, "enter")
        for transition in states["scope"]["transitions"]:
            for target, expr in transition.items():
                transition[target] = extend(expr, names, "stay")
        dump(path, doc)

    def inspect_length(self, gun_id):
        doc = load(os.path.join(OUT_RP, "animations", "guns", f"{gun_id}.animation.json"))
        anim = doc["animations"].get(f"animation.{gun_id}.fp.inspect") or {}
        return float(anim.get("animation_length", 4.0))

    def bp_recipes(self):
        out = os.path.join(OUT_BP, "recipes")
        os.makedirs(out, exist_ok=True)
        for spec in SPECS:
            counts = recipe_items(spec)
            pattern, key = recipe_pattern(counts)
            recipe = {
                "format_version": "1.20.10",
                "minecraft:recipe_shaped": {
                    "description": {"identifier": f"tac_guns:{spec['id']}_craft"},
                    "tags": ["crafting_table"],
                    "pattern": pattern,
                    "key": key,
                    "result": {"item": f"tac_guns:{spec['id']}_emp", "count": 1},
                },
            }
            dump(os.path.join(out, f"{spec['id']}.json"), recipe, indent=2)

    # ------------------------------------------------------------------- scripts
    def scripts(self):
        path = os.path.join(OUT_BP, "scripts", "main.js")
        text = read(path)
        anchor = '    "tac_guns:dp28": "tac_guns:762x54mmr"\n}'
        extra = "".join(f',\n    "tac_guns:{s["id"]}": "tac_guns:{s["ammo"]}"' for s in SPECS)
        if anchor in text and f'"tac_guns:{SPECS[0]["id"]}"' not in text:
            text = text.replace(anchor, anchor[:-1] + extra + "\n}")
        write_text(path, text)

        path = os.path.join(OUT_BP, "scripts", "global", "global.js")
        text = read(path)
        anchor = "            dp28: {\n                damage: 9.5\n            }"
        extra = "".join(f',\n            {s["id"]}: {{\n                damage: {s["damage"]}\n            }}'
                        for s in SPECS)
        if anchor in text and f"            {SPECS[0]['id']}: {{\n                damage:" not in text:
            text = text.replace(anchor, anchor + extra)
        else:
            raise SystemExit("global.js: ancora de dano nao encontrada")
        write_text(path, text)

    def bp_workbench(self):
        """Reescreve a navegacao da bancada para todas as abas (0-8) e paginas (1-11)."""
        path = os.path.join(OUT_BP, "animation_controllers", "workbench.json")
        doc = load(path)
        ctrl = doc["animation_controllers"]["controller.animation.workbench"]
        states = {}
        tabs = list(range(0, 9))
        pages = list(range(1, 12))
        for tab in tabs:
            transitions = []
            for page in pages:
                nxt = pages[page % len(pages)]
                prv = pages[(page - 2) % len(pages)]
                guard = (f"q.property('tac_guns:tab') == {tab} && "
                         f"q.property('tac_guns:itemtab') == {page} && q.mark_variant == 100")
                transitions.append({f"item{nxt}":
                                    guard + " && q.variant == 2 && (q.life_time - v.time) >= 0.15"})
                transitions.append({f"item{prv}":
                                    guard + " && q.variant == 1 && (q.life_time - v.time) >= 0.15"})
            for other in tabs:
                transitions.append({f"tab{other}": f"q.property('tac_guns:tab') == {other}"})
            states[f"tab{tab}"] = {"on_entry": ["v.time = q.life_time;"],
                                   "transitions": transitions}
        for page in pages:
            states[f"item{page}"] = {
                "on_entry": ["/playsound random.click @s", f"@s tac_guns:itemtab{page}"],
                "transitions": [{f"tab{t}": f"q.property('tac_guns:tab') == {t}"} for t in tabs],
            }
        ctrl["states"] = states
        dump(path, doc)

    # ------------------------------------------------------------ attachments
    def attach_items(self):
        """Itens de acessorio + receitas de bancada."""
        for att in ATTACHMENTS:
            item = {
                "format_version": "1.20.30",
                "minecraft:item": {
                    "description": {"identifier": f"tac_guns:{att['id']}",
                                    "menu_category": {"category": "equipment"}},
                    "components": {
                        "minecraft:max_stack_size": 16,
                        "minecraft:icon": {"texture": att["id"]},
                        "minecraft:display_name": {"value": att["name"]},
                        "minecraft:creative_category": {"parent": "equipment"},
                        "minecraft:hand_equipped": True,
                    },
                },
            }
            path = os.path.join(OUT_BP, "items", att["id"], "base.json")
            dump(path, item, indent=2)
            pattern, key = recipe_pattern(att["craft"])
            recipe = {
                "format_version": "1.20.10",
                "minecraft:recipe_shaped": {
                    "description": {"identifier": f"tac_guns:{att['id']}_craft"},
                    "tags": ["crafting_table"],
                    "pattern": pattern,
                    "key": key,
                    "result": {"item": f"tac_guns:{att['id']}", "count": 1},
                },
            }
            dump(os.path.join(OUT_BP, "recipes", f"{att['id']}.json"), recipe, indent=2)

            # icone 64x64 desenhado em PIL
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            drw = ImageDraw.Draw(img)
            colour = {"att_optic": (58, 62, 70), "att_suppressor": (44, 46, 50),
                      "att_laser": (38, 40, 46), "att_grip": (52, 54, 60),
                      "att_exmag": (64, 66, 72), "att_tape_optic": (70, 72, 78),
                      "att_dualmag": (58, 60, 66)}[att["id"]]
            if att["id"] == "att_optic":
                drw.rectangle([12, 22, 52, 42], fill=colour)
                drw.rectangle([18, 14, 46, 22], fill=(30, 32, 36))
                drw.rectangle([26, 16, 38, 21], fill=(150, 40, 40))
                drw.rectangle([10, 42, 54, 48], fill=(28, 30, 34))
            elif att["id"] == "att_suppressor":
                drw.rectangle([14, 24, 50, 40], fill=colour)
                for x in range(18, 50, 6):
                    drw.line([x, 24, x, 40], fill=(30, 32, 36))
                drw.rectangle([8, 28, 16, 36], fill=(26, 28, 32))
            elif att["id"] == "att_laser":
                drw.rectangle([12, 26, 48, 38], fill=colour)
                drw.rectangle([46, 28, 54, 36], fill=(140, 30, 30))
                drw.rectangle([16, 38, 24, 46], fill=(20, 22, 26))
            elif att["id"] == "att_tape_optic":
                drw.rectangle([10, 26, 54, 36], fill=colour)
                drw.rectangle([18, 22, 30, 40], fill=(36, 36, 40))
                drw.rectangle([34, 22, 46, 40], fill=(36, 36, 40))
                drw.rectangle([16, 28, 20, 34], fill=(60, 90, 130))
            elif att["id"] == "att_dualmag":
                drw.rectangle([18, 14, 30, 50], fill=colour)
                drw.rectangle([34, 14, 46, 50], fill=colour)
                drw.rectangle([16, 26, 48, 32], fill=(34, 34, 38))
                drw.rectangle([16, 38, 48, 43], fill=(34, 34, 38))
            elif att["id"] == "att_grip":
                drw.rectangle([26, 16, 40, 52], fill=colour)
                drw.rectangle([20, 10, 46, 18], fill=(28, 30, 34))
            else:
                drw.rectangle([22, 12, 44, 52], fill=colour)
                drw.rectangle([20, 46, 46, 54], fill=(30, 32, 36))
                drw.rectangle([26, 20, 40, 44], fill=(48, 50, 56))
            img.save(os.path.join(OUT_RP, "textures", "items", f"{att['id']}.png"))

    def attach_properties(self):
        """Propriedades sincronizadas que ligam/desligam cada peca no render controller."""
        path = os.path.join(OUT_BP, "entities", "player.json")
        doc = load(path)
        props = doc["minecraft:entity"]["description"].setdefault("properties", {})
        events = doc["minecraft:entity"]["events"]
        for att in ATTACHMENTS:
            props[att["prop"]] = {"type": "bool", "default": False, "client_sync": True}
            events[f"tac_guns:{att['id']}_on"] = {"set_property": {att["prop"]: True}}
            events[f"tac_guns:{att['id']}_off"] = {"set_property": {att["prop"]: False}}
        dump(path, doc)

    def attach_script(self):
        """Script que instala/remove o acessorio e o consome do inventario."""
        template = read(os.path.join(ROOT, "tools", "tacgen", "templates", "attachments.js"))
        table = "{\n" + "".join(
            f'    "tac_guns:{a["id"]}": {{ prop: "{a["prop"]}", name: "{a["name"]}" }},\n'
            for a in ATTACHMENTS) + "}"
        body = template.replace("__TABLE__", table)
        write_text(os.path.join(OUT_BP, "scripts", "events", "attachments.js"), body)

        main = os.path.join(OUT_BP, "scripts", "main.js")
        text = read(main)
        anchor = "import './global/global.js';"
        if "attachments.js" not in text:
            text = text.replace(anchor, anchor + "\nimport './events/attachments.js';")
        write_text(main, text)



    def faction_items(self):
        """Algemas (equipamento policial) + receita + ícone."""
        item = {
            "format_version": "1.20.30",
            "minecraft:item": {
                "description": {"identifier": "tac_guns:algemas",
                                "menu_category": {"category": "equipment"}},
                "components": {
                    "minecraft:max_stack_size": 1,
                    "minecraft:icon": {"texture": "algemas"},
                    "minecraft:display_name": {"value": "Algemas"},
                    "minecraft:creative_category": {"parent": "equipment"},
                    "minecraft:hand_equipped": True,
                },
            },
        }
        dump(os.path.join(OUT_BP, "items", "algemas", "base.json"), item, indent=2)

        recipe = {
            "format_version": "1.20.10",
            "minecraft:recipe_shaped": {
                "description": {"identifier": "tac_guns:algemas_craft"},
                "tags": ["crafting_table"],
                "pattern": ["i i", "ici", "i i"],
                "key": {"i": {"item": "minecraft:iron_ingot"},
                        "c": {"item": "minecraft:chain"}},
                "result": {"item": "tac_guns:algemas", "count": 1},
            },
        }
        dump(os.path.join(OUT_BP, "recipes", "algemas.json"), recipe, indent=2)

        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        aço = (150, 156, 168)
        escuro = (78, 84, 96)
        d.ellipse([6, 20, 26, 46], outline=aço, width=5)
        d.ellipse([36, 20, 56, 46], outline=aço, width=5)
        d.rectangle([24, 30, 38, 36], fill=escuro)
        for x in (27, 31, 35):
            d.line([x, 30, x, 36], fill=aço)
        d.rectangle([6, 28, 12, 38], fill=escuro)
        d.rectangle([50, 28, 56, 38], fill=escuro)
        img.save(os.path.join(OUT_RP, "textures", "items", "algemas.png"))

    def structures(self):
        """Bases construídas por /function (polícia e favela)."""
        from tacgen import structures
        relatorio = structures.escrever(OUT_BP)
        for nome, partes, comandos in relatorio:
            print(f"  /function {nome}: {partes} arquivos, {comandos} comandos")

    # ---------------------------------------------------------------- facções
    def faction_icons(self):
        """Ícones-botão da tela de escolha de lado: metades do card (azul/vermelho)."""
        import unicodedata
        from PIL import ImageFont

        _ttf = None
        for cand in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                     "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
                     "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
                     "/Library/Fonts/Arial Bold.ttf",
                     "C:/Windows/Fonts/arialbd.ttf"):
            if os.path.exists(cand):
                _ttf = cand
                break

        def fonte(tam):
            if _ttf:
                return ImageFont.truetype(_ttf, tam)
            try:
                return ImageFont.load_default(size=tam)
            except TypeError:
                return ImageFont.load_default()

        def legenda(d, cx, y, texto, tam, cor, esp=0):
            f = fonte(tam)
            if not _ttf:
                texto = "".join(c for c in unicodedata.normalize("NFD", texto)
                                if unicodedata.category(c) != "Mn")
            for dx in range(-esp, esp + 1):
                for dy in range(-esp, esp + 1):
                    d.text((cx + dx, y + dy), texto, font=f, fill=cor, anchor="ma")

        def card(nome, topo, sub, sub2, base, borda, claro, escuro, emblema):
            img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            d.rounded_rectangle([2, 2, 253, 253], radius=26, fill=base, outline=borda, width=5)
            d.rounded_rectangle([10, 10, 245, 245], radius=20, outline=claro, width=2)
            d.rectangle([12, 12, 243, 44], fill=escuro)
            legenda(d, 128, 20, topo, 22, (240, 246, 255, 255), 1)
            # faixa de destaque diagonal
            d.polygon([(10, 226), (245, 150), (245, 150), (245, 245), (10, 245)], fill=escuro)
            emblema(d, 128, 118)
            legenda(d, 128, 176, sub, 15, claro, 1)
            legenda(d, 128, 198, sub2, 15, claro, 1)
            d.rounded_rectangle([10, 10, 245, 245], radius=20, outline=claro, width=2)
            img.save(os.path.join(OUT_RP, "textures", "ui", nome + ".png"))

        def escudo(d, cx, cy):
            d.polygon([(cx, cy - 46), (cx + 42, cy - 30), (cx + 38, cy + 20),
                       (cx, cy + 52), (cx - 38, cy + 20), (cx - 42, cy - 30)],
                      fill=(22, 70, 150, 255), outline=(168, 214, 255, 255), width=3)
            d.polygon([(cx, cy - 30), (cx + 28, cy - 18), (cx + 25, cy + 14),
                       (cx, cy + 34), (cx - 25, cy + 14), (cx - 28, cy - 18)],
                      fill=(40, 112, 208, 255))
            import math as _m
            for i in range(5):
                a0 = -90 + i * 72
                a1 = a0 + 36
                cx0, cy0 = cx, cy - 4
                p0 = (cx0 + 18 * _m.cos(_m.radians(a0)), cy0 + 18 * _m.sin(_m.radians(a0)))
                p1 = (cx0 + 7 * _m.cos(_m.radians(a1)), cy0 + 7 * _m.sin(_m.radians(a1)))
                d.polygon([(cx0, cy0), p0, p1], fill=(238, 246, 255, 255))

        def mascara(d, cx, cy):
            d.ellipse([cx - 46, cy - 48, cx + 46, cy + 44], fill=(20, 20, 24, 255),
                      outline=(240, 96, 92, 255), width=3)
            d.polygon([(cx - 40, cy - 12), (cx - 6, cy - 18), (cx - 10, cy + 4), (cx - 40, cy + 4)],
                      fill=(246, 246, 246, 255))
            d.polygon([(cx + 40, cy - 12), (cx + 6, cy - 18), (cx + 10, cy + 4), (cx + 40, cy + 4)],
                      fill=(246, 246, 246, 255))
            d.ellipse([cx - 30, cy - 12, cx - 14, cy + 2], fill=(20, 20, 24, 255))
            d.ellipse([cx + 14, cy - 12, cx + 30, cy + 2], fill=(20, 20, 24, 255))
            d.rectangle([cx - 36, cy + 18, cx + 36, cy + 34], fill=(14, 14, 18, 255))
            d.line([cx - 36, cy + 18, cx + 36, cy + 18], fill=(214, 62, 58, 255), width=2)

        card("policial", "POLICIAL", "PROTEJA A CIDADE", "MANTENHA A ORDEM",
             (12, 26, 54, 255), (58, 138, 226, 255), (150, 205, 255, 255),
             (18, 52, 110, 235), escudo)
        card("ladrao", "LADRÃO", "FAÇA SEU DINHEIRO", "DESAFIE A LEI",
             (38, 8, 10, 255), (214, 62, 58, 255), (255, 176, 170, 255),
             (92, 20, 20, 235), mascara)

    def faction_script(self):
        """Script da camada de facções + tabelas geradas a partir do catálogo."""
        def shop(side):
            return "\n".join(
                f'        {{ nome: "{e["nome"]}", item: "{e["item"]}", ammo: "{e["ammo"]}", '
                f'preco: {e["preco"]}, municao: {e["municao"]}, icone: "{e["icone"]}" }},'
                for e in shop_entries(side))

        police = [s["id"] for s in SPECS if s.get("faction") != "crime"]
        crime = [s["id"] for s in SPECS if s.get("faction") == "crime"]
        # armas do pacote original (sem facção declarada) ficam liberadas para os dois lados
        legacy = ["ak47", "mk18", "awp", "m870", "glock17", "coltpython",
                  "deagle", "db", "dp28", "m134"]

        table = ("{\n    policia: [\n" + shop("policia") + "\n    ],\n"
                 "    ladrao: [\n" + shop("ladrao") + "\n    ],\n}")

        def js_set(ids):
            return "[" + ", ".join(f'"{i}"' for i in ids) + "]"

        police_js = js_set(police + legacy)
        crime_js = js_set(crime)

        template = read(os.path.join(ROOT, "tools", "tacgen", "templates", "factions.js"))
        body = (template
                .replace("__POLICE_WEAPONS__", police_js)
                .replace("__CRIME_WEAPONS__", crime_js)
                .replace("__SHOP__", table))
        write_text(os.path.join(OUT_BP, "scripts", "events", "factions.js"), body)

        hit = read(os.path.join(ROOT, "tools", "tacgen", "templates", "projectile_hit.js"))
        hit = (hit.replace("__POLICE_WEAPONS__", police_js)
                  .replace("__CRIME_WEAPONS__", crime_js))
        write_text(os.path.join(OUT_BP, "scripts", "events", "projectileHitEntity.js"), hit)

        main = os.path.join(OUT_BP, "scripts", "main.js")
        text = read(main)
        anchor = "import './global/global.js';"
        if "factions.js" not in text:
            text = text.replace(anchor, anchor + "\nimport './events/factions.js';")
        write_text(main, text)

    # ---------------------------------------------------------------- resources
    def item_texture(self):
        path = os.path.join(OUT_RP, "textures", "item_texture.json")
        text = read(path)
        marker = "  //////////ammo"
        extras = [{"id": "algemas"}]
        add = "".join(f'    "{s["id"]}": {{\n      "textures": "textures/items/{s["id"]}"\n    }},\n'
                      for s in SPECS + ATTACHMENTS + extras)
        if marker not in text:
            text = text.replace('  "texture_data": {\n',
                                '  "texture_data": {\n' + add)
        else:
            text = text.replace(marker, add + marker)
        write_text(path, text)

    def sounds(self):
        path = os.path.join(OUT_RP, "sounds", "sound_definitions.json")
        doc = load(path)
        for spec in SPECS:
            tpl = FAMILIES[spec["family"]]["template"]
            prefix = f"{tpl}."
            for key, value in list(doc.items()):
                if key.startswith(prefix):
                    doc[f"{spec['id']}." + key[len(prefix):]] = json.loads(json.dumps(value))
        dump(path, doc)

    def lang(self):
        path = os.path.join(OUT_RP, "texts", "en_US.lang")
        lines = [read(path).rstrip("\n")]
        for spec in SPECS:
            lines.append(f"item.tac_guns:{spec['id']}.name={spec['name']}")
            lines.append(f"item.tac_guns:{spec['id']}_emp.name={spec['name']} (vazio)")
        for att in ATTACHMENTS:
            lines.append(f"item.tac_guns:{att['id']}.name={att['name']}")
            lines.append(f"item.tac_guns:{att['id']}_emp.name={att['name']}")
        lines.append("item.tac_guns:algemas.name=Algemas")
        write_text(path, "\n".join(lines) + "\n")
        pt = os.path.join(OUT_RP, "texts", "pt_BR.lang")
        existing = read(pt) if os.path.exists(pt) else ""
        keep = [l for l in existing.splitlines() if l.strip()]
        for spec in SPECS:
            keep.append(f"item.tac_guns:{spec['id']}.name={spec['name']}")
            keep.append(f"item.tac_guns:{spec['id']}_emp.name={spec['name']} (vazio)")
        keep.append("item.tac_guns:algemas.name=Algemas")
        write_text(pt, "\n".join(keep) + "\n")

    VERSION = [1, 2, 0]

    def manifests(self):
        self.VERSION = getattr(Build, "VERSION", [1, 2, 0])
        note = ("\n+ 18 armas extras: MP5, MP5K, UMP45, Vector, P90, M4A1, SCAR-H, G36C, FAMAS, "
                "M82A1, Intervention, M24, Nova, SPAS-12, AA-12, Five-seveN, Model 29, Judge")
        bp = load(os.path.join(OUT_BP, "manifest.json"))
        rp = load(os.path.join(OUT_RP, "manifest.json"))
        for doc, extra in ((bp, ""), (rp, "")):
            doc["header"]["version"] = list(self.VERSION)
            if note not in doc["header"].get("description", ""):
                doc["header"]["description"] = doc["header"].get("description", "") + note
            for module in doc["modules"]:
                module["version"] = list(self.VERSION)
        rp["dependencies"] = [{"uuid": bp["header"]["uuid"],
                               "version": list(self.VERSION)}]
        # versoes de modulo explicitas: 2.0.0 e a primeira estavel da API 2.x
        # (Minecraft 1.21.90+) e continua disponivel nas versoes seguintes.
        bp["dependencies"] = [
            {"module_name": "@minecraft/server", "version": "2.0.0"},
            {"module_name": "@minecraft/server-ui", "version": "2.0.0"},
            {"uuid": rp["header"]["uuid"], "version": list(self.VERSION)},
        ]
        dump(os.path.join(OUT_BP, "manifest.json"), bp, indent=2)
        dump(os.path.join(OUT_RP, "manifest.json"), rp, indent=2)


def build():
    b = Build()
    b.reset()
    for spec in SPECS:
        b.build_model(spec)
        b.build_textures(spec)
        b.rp_animation(spec)
        b.rp_fp_controller(spec)
        b.rp_attachables(spec)
        b.rp_render_controllers(spec)
        b.bp_items(spec)
        b.bp_bullet(spec)
        b.bp_functions(spec)
        b.bp_gun_controller(spec)
    b.rp_player()
    b.rp_draw_controller()
    b.bp_player()
    b.bp_reload_controllers()
    b.bp_animations()
    b.bp_workbench()
    b.bp_inspect_controller()
    b.bp_scope_controller()
    b.bp_recipes()
    b.attach_items()
    b.attach_properties()
    b.attach_script()
    b.faction_icons()
    b.faction_items()
    b.faction_script()
    b.structures()
    b.scripts()
    b.item_texture()
    b.sounds()
    b.lang()
    b.manifests()
    print(f"ok: {len(SPECS)} armas -> {OUT}")


if __name__ == "__main__":
    build()
