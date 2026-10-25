"""Template analysis: read an existing TacGuns weapon rig so new guns can reuse it."""
import json
import math
import os

RP = os.path.join(os.path.dirname(__file__), "..", "..", "src", "TacGuns(R)")
BP = os.path.join(os.path.dirname(__file__), "..", "..", "src", "TacGuns(B)")

SKELETON_HINTS = (
    "rootforweapons", "fakewaist", "bodyforweapons", "bone3", "node", "bone", "bone2",
    "root", "waist", "body", "head", "leftarm", "rightarm", "leftitem", "rightitem",
    "leftleg", "rightleg", "r", "l", "righthand", "lefthand",
)


# ------------------------------------------------------------------ matrix help
def mat_ident():
    return [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]


def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def mat_trans(t):
    m = mat_ident()
    m[0][3], m[1][3], m[2][3] = t
    return m


def mat_rot(rot):
    rx, ry, rz = [math.radians(v) for v in rot]
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    mx = [[1, 0, 0, 0], [0, cx, -sx, 0], [0, sx, cx, 0], [0, 0, 0, 1]]
    my = [[cy, 0, sy, 0], [0, 1, 0, 0], [-sy, 0, cy, 0], [0, 0, 0, 1]]
    mz = [[cz, -sz, 0, 0], [sz, cz, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    return mat_mul(mz, mat_mul(my, mx))


def mat_inv(m):
    """Inverse of an affine matrix."""
    a = [row[:] for row in m]
    inv = mat_ident()
    # gauss-jordan on 4x4 affine
    for i in range(4):
        piv = max(range(i, 4), key=lambda r: abs(a[r][i]))
        if abs(a[piv][i]) < 1e-12:
            raise ValueError("singular matrix")
        a[i], a[piv] = a[piv], a[i]
        inv[i], inv[piv] = inv[piv], inv[i]
        d = a[i][i]
        a[i] = [v / d for v in a[i]]
        inv[i] = [v / d for v in inv[i]]
        for r in range(4):
            if r == i:
                continue
            f = a[r][i]
            if f:
                a[r] = [a[r][c] - f * a[i][c] for c in range(4)]
                inv[r] = [inv[r][c] - f * inv[i][c] for c in range(4)]
    return inv


def xform(m, p):
    x, y, z = p
    return (m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3],
            m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3],
            m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3])


def rot_of(m):
    return [[round(m[i][j], 6) for j in range(3)] for i in range(3)]


def is_identity_rot(m):
    r = rot_of(m)
    ident = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    return all(abs(r[i][j] - ident[i][j]) < 1e-3 for i in range(3) for j in range(3))


# ------------------------------------------------------------------- template
class Template:
    def __init__(self, gun_id):
        self.id = gun_id
        self.geo_path = os.path.join(RP, "models", "entity", "guns", f"{gun_id}.json")
        with open(self.geo_path) as f:
            self.geo_doc = json.load(f)
        self.geo = self.geo_doc["minecraft:geometry"][0]
        self.bones = {b["name"]: b for b in self.geo["bones"]}
        self.tp_bone = next((n for n in self.bones if n.lower().endswith("tp")), None)
        # rest transforms
        self.rest = {}
        for name in self.bones:
            self.rest[name] = self._rest_matrix(name)
        self.inv_rest = {n: mat_inv(self.rest[n]) for n in self.bones}

        # locators (muzzle / shell) from the first-person bones
        self.locators = {}
        for b in self.geo["bones"]:
            for k, v in (b.get("locators") or {}).items():
                self.locators[k] = (v, b["name"])

        # bone roles
        self.mesh_bone = max((b for b in self.geo["bones"]
                              if b["name"] != self.tp_bone and self._is_gun_bone(b["name"])),
                             key=lambda b: len(b.get("cubes", [])))["name"]
        self.part_bones = [b["name"] for b in self.geo["bones"]
                           if b["name"] not in (self.mesh_bone, self.tp_bone)
                           and b.get("cubes") and self._is_gun_bone(b["name"])]

        self.body_bbox = self._cube_bbox([self.mesh_bone])
        self.full_bbox = self._cube_bbox([self.mesh_bone] + self.part_bones)

        # muzzle reference
        muzzle = next(((n, v) for n, (v, b) in self.locators.items() if "muzzle" in n or "locator" in n), None)
        self.muzzle_locator_name = muzzle[0] if muzzle else None
        self.muzzle_pos = muzzle[1] if muzzle else [self.full_bbox[0][0], 8, self.full_bbox[0][2]]
        self.shell_locator_name = next((n for n in self.locators if "shell" in n), None)

    # -- helpers
    def _rest_matrix(self, name, depth=0):
        if name in self.rest:
            return self.rest[name]
        if depth > 64:
            raise RuntimeError("bone loop " + name)
        b = self.bones[name]
        pv = b.get("pivot", [0, 0, 0])
        rot = b.get("rotation", [0, 0, 0])
        local = mat_mul(mat_trans(pv), mat_mul(mat_rot(rot), mat_trans([-p for p in pv])))
        parent = b.get("parent")
        pre = self._rest_matrix(parent, depth + 1) if parent else mat_ident()
        return mat_mul(pre, local)

    def _is_gun_bone(self, name):
        n = name.lower()
        if "tp" in n:
            return False
        if n in ("r", "l"):
            return False
        if "arm" in n or "hand" in n:
            return False
        if n.startswith(("node", "bone", "root", "waist", "body", "head", "left", "right", "fake")):
            return False
        return True

    def _cube_bbox(self, bone_names):
        mn = [1e9] * 3
        mx = [-1e9] * 3
        for bn in bone_names:
            b = self.bones[bn]
            m = self.rest[bn]
            for c in b.get("cubes", []):
                o, s, infl = c["origin"], c["size"], c.get("inflate", 0)
                cm = m
                if c.get("rotation"):
                    pv = c.get("pivot", [0, 0, 0])
                    cm = mat_mul(m, mat_mul(mat_trans(pv), mat_mul(mat_rot(c["rotation"]), mat_trans([-p for p in pv]))))
                for fx in (0, 1):
                    for fy in (0, 1):
                        for fz in (0, 1):
                            p = xform(cm, (o[0] - infl + (s[0] + 2 * infl) * fx,
                                           o[1] - infl + (s[1] + 2 * infl) * fy,
                                           o[2] - infl + (s[2] + 2 * infl) * fz))
                            for i in range(3):
                                mn[i] = min(mn[i], p[i])
                                mx[i] = max(mx[i], p[i])
        return mn, mx

    def register_virtual_bone(self, name, parent):
        """A bone with pivot 0 / no rotation shares its parent's rest transform."""
        self.rest[name] = self.rest[parent]
        self.inv_rest[name] = self.inv_rest[parent]
        self.bones[name] = {"name": name, "parent": parent, "pivot": [0, 0, 0], "cubes": []}

    # -- conversion of world-space cubes into a bone's local space
    def to_bone_space(self, boxes, bone_name):
        """boxes: list of dicts with x0..z1 in rest/world space. Returns cubes in bone-local space.
        Chains in these rigs are translation only, so this is an exact re-placement."""
        inv = self.inv_rest[bone_name]
        if not is_identity_rot(inv):
            raise ValueError(f"bone {bone_name} has a rotated chain; cannot host unrotated cubes")
        dx, dy, dz = inv[0][3], inv[1][3], inv[2][3]
        out = []
        for b in boxes:
            out.append(dict(b, x0=b["x0"] + dx, x1=b["x1"] + dx,
                            y0=b["y0"] + dy, y1=b["y1"] + dy,
                            z0=b["z0"] + dz, z1=b["z1"] + dz))
        return out


def load_template(gun_id):
    return Template(gun_id)
