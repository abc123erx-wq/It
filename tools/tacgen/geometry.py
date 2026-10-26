"""Turn a voxel Design into a Bedrock geometry that plugs into a TacGuns rig."""
import copy

from . import texture as tex
from .analysis import is_identity_rot, xform

FACES = ("north", "south", "east", "west", "up", "down")
ATLAS = tex.CELL * tex.COLS  # square atlas size


def _face_uv(mat, face):
    u, v, w, h = tex.cell_uv_region(mat, tex.face_shade(face))
    return {face: {"uv": [u, v], "uv_size": [w, h]}}


def cube_json(box, bone_space_offset=(0, 0, 0), scale=1.0):
    """Cube in bone local space. box coordinates are already in that space."""
    ox, oy, oz = bone_space_offset
    origin = [round(box.x0 + ox, 4), round(box.y0 + oy, 4), round(box.z0 + oz, 4)]
    size = [round(box.x1 - box.x0, 4), round(box.y1 - box.y0, 4), round(box.z1 - box.z0, 4)]
    uv = {}
    for face in FACES:
        uv.update(_face_uv(box.mat, face))
    return {"origin": origin, "size": size, "uv": uv}


class Placement:
    """Maps design space -> host template world space."""

    def __init__(self, template, design, extra_scale=1.0):
        self.t = template
        self.d = design
        bmin, bmax = template.full_bbox
        # muzzle / bore from the template's locator, rear from the assembled bbox
        self.muzzle = template.muzzle_pos
        self.rear_z = bmax[2]
        dz = self.rear_z - self.muzzle[2]
        self.scale = (dz / design.length) * extra_scale
        self.x_center = self.muzzle[0]
        self.bore_y = self.muzzle[1]

    def to_world(self, box):
        s = self.scale
        return dict(mat=box.mat, bone=box.bone,
                    x0=self.x_center + box.x0 * s, x1=self.x_center + box.x1 * s,
                    y0=self.bore_y + box.y0 * s, y1=self.bore_y + box.y1 * s,
                    z0=self.muzzle[2] + box.z0 * s, z1=self.muzzle[2] + box.z1 * s)

    def point(self, p):
        s = self.scale
        return (self.x_center + p[0] * s, self.bore_y + p[1] * s, self.muzzle[2] + p[2] * s)


def _to_local(cubes, template, bone_name):
    """Shift world space boxes into a bone's local space (chains are translation only)."""
    inv = template.inv_rest[bone_name]
    if not is_identity_rot(inv):
        raise ValueError(f"cannot host cubes on rotated chain bone {bone_name}")
    dx, dy, dz = inv[0][3], inv[1][3], inv[2][3]

    class S:
        pass

    out = []
    for c in cubes:
        s = S()
        s.mat = c["mat"]
        s.x0, s.x1 = c["x0"] + dx, c["x1"] + dx
        s.y0, s.y1 = c["y0"] + dy, c["y1"] + dy
        s.z0, s.z1 = c["z0"] + dz, c["z1"] + dz
        out.append(s)
    return out


class _Box:
    __slots__ = ("mat", "x0", "y0", "z0", "x1", "y1", "z1")

    def __init__(self, d):
        if isinstance(d, dict):
            for k in ("mat", "x0", "y0", "z0", "x1", "y1", "z1"):
                setattr(self, k, d[k])
        else:
            for k in ("mat", "x0", "y0", "z0", "x1", "y1", "z1"):
                setattr(self, k, getattr(d, k))


def _as_boxes(items):
    return [_Box(i) for i in items]



# ---------------------------------------------------------------------------
# pontos de encaixe modulares (attachments)
# ---------------------------------------------------------------------------
ATTACHMENTS = ("att_optic", "att_suppressor", "att_grip", "att_laser", "att_exmag")
CRIME_ATTACHMENTS = ("att_tape_optic", "att_dualmag")


def _att_boxes(design):
    """Pecas de attachment no espaco de autoria (boca do cano em z=0, alma em y=0)."""
    L = design.length
    x0, x1 = -1.1, 1.1          # largura das pecas
    boxes = {}

    # optica: bloco sobre o receptor com "lente" azulada
    z0, z1 = 0.20 * L, 0.34 * L
    boxes["att_optic"] = [
        dict(mat="black", x0=x0, x1=x1, y0=1.5, y1=2.1, z0=z0, z1=z1),
        dict(mat="gunmetal", x0=x0 - 0.2, x1=x1 + 0.2, y0=2.1, y1=3.3, z0=z0 + 0.6, z1=z1 - 0.6),
        dict(mat="blue", x0=x0 - 0.1, x1=x1 + 0.1, y0=2.3, y1=3.1, z0=z0 + 0.4, z1=z0 + 0.6),
        dict(mat="lume", x0=-0.3, x1=0.3, y0=2.6, y1=2.9, z0=z1 - 0.8, z1=z1 - 0.5),
    ]
    # supressor: cilindro voxel na frente da boca
    boxes["att_suppressor"] = [
        dict(mat="polymer", x0=-1.2, x1=1.2, y0=-1.2, y1=1.2, z0=-0.30 * L, z1=-0.02 * L),
        dict(mat="gunmetal", x0=-1.35, x1=1.35, y0=-1.35, y1=1.35, z0=-0.31 * L, z1=-0.26 * L),
    ]
    # foregrip vertical
    boxes["att_grip"] = [
        dict(mat="polymer", x0=-0.9, x1=0.9, y0=-3.4, y1=-1.2, z0=0.30 * L, z1=0.37 * L),
    ]
    # lanterna / laser
    boxes["att_laser"] = [
        dict(mat="black", x0=-1.0, x1=1.0, y0=-2.2, y1=-1.2, z0=0.34 * L, z1=0.44 * L),
        dict(mat="darkred", x0=-0.4, x1=0.4, y0=-2.0, y1=-1.4, z0=0.44 * L, z1=0.46 * L),
    ]
    # carregador estendido (saliencia abaixo do poco)
    boxes["att_exmag"] = [
        dict(mat="gunmetal", x0=-1.0, x1=1.0, y0=-6.4, y1=-3.6, z0=0.42 * L, z1=0.50 * L),
        dict(mat="black", x0=-1.2, x1=1.2, y0=-6.8, y1=-6.2, z0=0.42 * L, z1=0.50 * L),
    ]
    return boxes


def _crime_att_boxes(design):
    """Acessorios improvisados: luneta amarrada com fita e carregador duplo fitado."""
    L = design.length
    return {
        # luneta de caca presa com fita sobre o recebedor
        "att_tape_optic": [
            dict(mat="steel", x0=-0.5, x1=0.5, y0=2.2, y1=2.9, z0=0.28 * L, z1=0.46 * L),
            dict(mat="blue", x0=-0.35, x1=0.35, y0=2.35, y1=2.75, z0=0.26 * L, z1=0.28 * L),
            dict(mat="tape", x0=-0.75, x1=0.75, y0=1.7, y1=3.0, z0=0.30 * L, z1=0.32 * L),
            dict(mat="tape", x0=-0.75, x1=0.75, y0=1.7, y1=3.0, z0=0.42 * L, z1=0.44 * L),
        ],
        # dois carregadores presos com fita isolante
        "att_dualmag": [
            dict(mat="gunmetal", x0=-1.05, x1=1.05, y0=-6.6, y1=-4.4, z0=0.46 * L, z1=0.54 * L),
            dict(mat="tape", x0=-1.2, x1=1.2, y0=-6.2, y1=-4.8, z0=0.46 * L, z1=0.54 * L),
        ],
    }


def build_attachments(template, design, placement, body_name, crime=False):
    """Bones extras (filhos do corpo) que ficam ocultos ate o jogador instalar a peca."""
    boxes_sets = _att_boxes(design)
    if crime:
        boxes_sets.update(_crime_att_boxes(design))
    bones = []
    for name, boxes in boxes_sets.items():
        world = [placement.to_world(_B(b)) for b in boxes]
        local = _to_local(world, template, body_name)
        bone = {"name": name, "parent": body_name,
                "cubes": [cube_json(c) for c in _as_boxes(local)]}
        bones.append(bone)
    return bones


class _B:
    """Converte dict de attachment para o formato esperado por Placement.to_world."""

    __slots__ = ("mat", "bone", "x0", "y0", "z0", "x1", "y1", "z1")

    def __init__(self, d):
        self.mat = d["mat"]
        self.bone = "body"
        for k in ("x0", "y0", "z0", "x1", "y1", "z1"):
            setattr(self, k, d[k])


def build_geometry(template, design, cfg):
    """cfg keys:
        body_parent : bone the new body bone hangs from (the weapon root bone)
        part_bones  : dict design-bone -> template bone name
        strip_bones : extra template bones to empty
    """
    geo_doc = copy.deepcopy(template.geo_doc)
    geo = geo_doc["minecraft:geometry"][0]
    geo["description"]["texture_width"] = ATLAS
    geo["description"]["texture_height"] = ATLAS
    base_w = geo["description"].get("visible_bounds_width", 200)
    base_h = geo["description"].get("visible_bounds_height", 100)
    geo["description"]["visible_bounds_width"] = max(base_w, 200)
    geo["description"]["visible_bounds_height"] = max(base_h, 100)
    bones = {b["name"]: b for b in geo["bones"]}

    # 1. strip every cube that belonged to the host weapon (the rig keeps only its skeleton)
    for b in geo["bones"]:
        b["cubes"] = []
        b.pop("locators", None)

    pl = Placement(template, design, extra_scale=cfg.get("scale", 1.0))
    world = [pl.to_world(b) for b in design.boxes]

    body_name = f"{design.gun_id}_body"
    # 2. new body bone hanging from the weapon root, in world-rest coordinates
    template.register_virtual_bone(body_name, cfg["body_parent"])
    root = bones[cfg["body_parent"]]
    new_bone = template.bones[body_name]
    # PIVOT: usa o mesmo centro de rotacao da arma original. Sem isso o corpo novo
    # gira em torno de (0,0,0) nas animacoes (saque, recarga, sprint) e "flutua"
    # longe da mao. Em repouso o pivo nao desloca nada: T(p)*R(0)*T(-p) = I.
    pivo_da_arma = cfg.get("pivot")
    if not pivo_da_arma:
        mesh = cfg.get("mesh_bone")
        if mesh and mesh in template.bones:
            pivo_da_arma = template.bones[mesh].get("pivot")
    if pivo_da_arma:
        new_bone["pivot"] = [round(v, 4) for v in pivo_da_arma]
    geo["bones"].insert(geo["bones"].index(root) + 1, new_bone)
    bones[body_name] = new_bone

    groups = {}
    for c in world:
        groups.setdefault(c["bone"], []).append(c)

    # 3. place cubes
    body_cubes = groups.pop("body", [])
    bones[body_name]["cubes"] = [cube_json(c) for c in _as_boxes(_to_local(body_cubes, template, body_name))]
    loc = {}
    muzzle_local = _to_local([dict(mat="black", x0=pl.muzzle[0], x1=pl.muzzle[0], y0=pl.muzzle[1],
                                    y1=pl.muzzle[1], z0=pl.muzzle[2], z1=pl.muzzle[2])], template, body_name)[0]
    loc["muzzle"] = [round(muzzle_local.x0, 3), round(muzzle_local.y0, 3), round(muzzle_local.z0, 3)]
    if "shell" in design.locators:
        sp = pl.point(design.locators["shell"])
        sl = _to_local([dict(mat="black", x0=sp[0], x1=sp[0], y0=sp[1], y1=sp[1], z0=sp[2], z1=sp[2])],
                       template, body_name)[0]
        loc["shell"] = [round(sl.x0, 3), round(sl.y0, 3), round(sl.z0, 3)]
    bones[body_name]["locators"] = {cfg["locator_prefix"] + k: v for k, v in loc.items()}

    for design_bone, cubes in groups.items():
        target = cfg["part_bones"].get(design_bone)
        if not target or target not in bones:
            target = body_name
        local = cubes if target == body_name else _to_local(cubes, template, target)
        bones[target].setdefault("cubes", []).extend(
            cube_json(c) for c in _as_boxes(local))

    # 4. third person copy: the whole weapon, static
    tp = template.tp_bone
    if tp in bones:
        tp_cubes = _to_local(world, template, tp)
        bones[tp]["cubes"] = [cube_json(c) for c in _as_boxes(tp_cubes)]
        tl = _to_local([dict(mat="black", x0=pl.muzzle[0], x1=pl.muzzle[0], y0=pl.muzzle[1],
                             y1=pl.muzzle[1], z0=pl.muzzle[2], z1=pl.muzzle[2])], template, tp)[0]
        lbs = {cfg["locator_prefix"] + "muzzle2": [round(tl.x0, 3), round(tl.y0, 3), round(tl.z0, 3)]}
        if "shell" in design.locators:
            sp = pl.point(design.locators["shell"])
            sl = _to_local([dict(mat="black", x0=sp[0], x1=sp[0], y0=sp[1], y1=sp[1], z0=sp[2], z1=sp[2])],
                           template, tp)[0]
            lbs[cfg["locator_prefix"] + "shell2"] = [round(sl.x0, 3), round(sl.y0, 3), round(sl.z0, 3)]
        bones[tp]["locators"] = lbs

    # 5. pontos de encaixe de attachments (ocultos por padrao)
    geo["bones"].extend(build_attachments(template, design, pl, body_name,
                                           crime=cfg.get("faction") == "crime"))

    return geo_doc
