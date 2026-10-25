"""
Tiny offline renderer for Bedrock geometry JSON (preview only, not shipped in the addon).
Renders cubes from a geometry file to a PNG using orthographic projection, painter's
algorithm and per-face texture sampling (or flat face shading when no texture is given).

Usage:
    python3 tools/mcpreview.py <geometry.json> <out.png> [--tex <texture.png>]
                               [--geo geometry.name] [--bones a,b,c] [--size 900]
"""
import json
import math
import sys
from PIL import Image, ImageDraw

FACE_DIRS = {
    "north": (0, 0, -1),
    "south": (0, 0, 1),
    "east": (1, 0, 0),
    "west": (-1, 0, 0),
    "up": (0, 1, 0),
    "down": (0, -1, 0),
}

# corner order per face: 4 corners given as (x,y,z) in 0/1 flags
FACE_CORNERS = {
    "north": [(0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)],
    "south": [(1, 1, 1), (0, 1, 1), (0, 0, 1), (1, 0, 1)],
    "east":  [(1, 1, 0), (1, 1, 1), (1, 0, 1), (1, 0, 0)],
    "west":  [(0, 1, 1), (0, 1, 0), (0, 0, 0), (0, 0, 1)],
    "up":    [(0, 1, 1), (1, 1, 1), (1, 1, 0), (0, 1, 0)],
    "down":  [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],
}


def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def mat_ident():
    return [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]


def mat_trans(t):
    m = mat_ident()
    m[0][3], m[1][3], m[2][3] = t
    return m


def mat_rot(rot):
    """Bedrock/Blockbench style: rotation in degrees around X, then Y, then Z (extrinsic)."""
    rx, ry, rz = [math.radians(v) for v in rot]
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    mx = [[1, 0, 0, 0], [0, cx, -sx, 0], [0, sx, cx, 0], [0, 0, 0, 1]]
    my = [[cy, 0, sy, 0], [0, 1, 0, 0], [-sy, 0, cy, 0], [0, 0, 0, 1]]
    mz = [[cz, -sz, 0, 0], [sz, cz, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    return mat_mul(mz, mat_mul(my, mx))


def xform(m, p):
    x, y, z = p
    return (
        m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3],
        m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3],
        m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3],
    )


def load_geometry(path, geo_name=None):
    with open(path) as f:
        data = json.load(f)
    geos = data["minecraft:geometry"]
    if geo_name:
        for g in geos:
            if g["description"]["identifier"] == geo_name:
                return g
        raise SystemExit(f"geometry {geo_name} not found in {path}")
    return geos[0]


def build_bone_transforms(geo):
    bones = {b["name"]: b for b in geo["bones"]}
    cache = {}

    def bone_matrix(name, depth=0):
        if name in cache:
            return cache[name]
        if depth > 64:
            raise SystemExit("bone hierarchy loop at " + name)
        b = bones[name]
        pivot = b.get("pivot", [0, 0, 0])
        rot = b.get("rotation", [0, 0, 0])
        local = mat_mul(mat_trans(pivot), mat_mul(mat_rot(rot), mat_trans([-p for p in pivot])))
        parent = b.get("parent")
        m = mat_mul(bone_matrix(parent, depth + 1), local) if parent else local
        cache[name] = m
        return m

    return bones, bone_matrix


def tex_sample(img, u, v, uw, uh):
    if img is None:
        return None
    w, h = img.size
    x0, x1 = sorted((int(u), int(u + uw)))
    y0, y1 = sorted((int(v), int(v + uh)))
    x0, x1 = max(0, min(w - 1, x0)), max(0, min(w - 1, x1))
    y0, y1 = max(0, min(h - 1, y0)), max(0, min(h - 1, y1))
    if x1 <= x0:
        x1 = min(w - 1, x0 + 1)
    if y1 <= y0:
        y1 = min(h - 1, y0 + 1)
    px = img.convert("RGBA")
    r = g = b = n = 0
    for yy in range(y0, y1 + 1, max(1, (y1 - y0) // 8 or 1)):
        for xx in range(x0, x1 + 1, max(1, (x1 - x0) // 8 or 1)):
            p = px.getpixel((xx, yy))
            if p[3] > 8:
                r += p[0]; g += p[1]; b += p[2]; n += 1
    if n == 0:
        return None
    return (r // n, g // n, b // n, 255)


CANVAS = (900, 560)
VIEW_YAW = math.radians(-35)
VIEW_PITCH = math.radians(22)


def project(p, center, scale):
    x, y, z = p
    x -= center[0]; y -= center[1]; z -= center[2]
    # rotate yaw around Y
    x, z = x * math.cos(VIEW_YAW) - z * math.sin(VIEW_YAW), x * math.sin(VIEW_YAW) + z * math.cos(VIEW_YAW)
    # rotate pitch around X
    y, z = y * math.cos(VIEW_PITCH) - z * math.sin(VIEW_PITCH), y * math.sin(VIEW_PITCH) + z * math.cos(VIEW_PITCH)
    # screen: +x right, -y down? model +y up => screen -y
    sx = CANVAS[0] / 2 + x * scale
    sy = CANVAS[1] / 2 - y * scale
    return sx, sy, z


def render(geo, tex_path=None, out_path="preview.png", hide_bones=(), only_bones=None):
    img_tex = Image.open(tex_path) if tex_path else None
    bones, bone_matrix = build_bone_transforms(geo)

    faces = []
    smin = [1e9, 1e9, 1e9]
    smax = [-1e9, -1e9, -1e9]
    prepped = []
    for bname, b in bones.items():
        if only_bones is not None and bname not in only_bones:
            continue
        if bname in hide_bones:
            continue
        m = bone_matrix(bname)
        for c in b.get("cubes", []):
            o = c["origin"]
            s = c["size"]
            infl = c.get("inflate", 0)
            cm = m
            if c.get("rotation"):
                pv = c.get("pivot", [0, 0, 0])
                cm = mat_mul(m, mat_mul(mat_trans(pv), mat_mul(mat_rot(c["rotation"]), mat_trans([-p for p in pv]))))
            for fname, flags in FACE_CORNERS.items():
                uvspec = c.get("uv")
                texel = None
                if isinstance(uvspec, dict) and fname in uvspec:
                    spec = uvspec[fname]
                    uv = spec["uv"]
                    uvs = spec.get("uv_size", [1, 1])
                    texel = tex_sample(img_tex, uv[0], uv[1], uvs[0], uvs[1])
                elif isinstance(uvspec, dict) and not isinstance(uvspec.get("uv"), (int, float)) and "uv" not in uvspec:
                    # box uv
                    texel = None
                pts = []
                for fx, fy, fz in flags:
                    p = (
                        o[0] - infl + (s[0] + 2 * infl) * fx,
                        o[1] - infl + (s[1] + 2 * infl) * fy,
                        o[2] - infl + (s[2] + 2 * infl) * fz,
                    )
                    p = xform(cm, p)
                    pts.append(p)
                for p in pts:
                    for i in range(3):
                        smin[i] = min(smin[i], p[i]); smax[i] = max(smax[i], p[i])
                prepped.append((fname, pts, texel, c.get("uv")))

    center = [(smin[i] + smax[i]) / 2 for i in range(3)]
    extent = max(smax[i] - smin[i] for i in range(3))
    scale = min(CANVAS[0], CANVAS[1]) * 0.8 / max(1e-6, extent)

    img = Image.new("RGBA", CANVAS, (26, 26, 30, 255))
    drw = ImageDraw.Draw(img)

    light = (-0.4, 0.85, -0.3)
    n = math.sqrt(sum(v * v for v in light))
    light = tuple(v / n for v in light)

    items = []
    for fname, pts, texel, uv in prepped:
        proj = [project(p, center, scale) for p in pts]
        d = sum(p[2] for p in proj) / len(proj)
        nrm = FACE_DIRS[fname]
        sh = 0.55 + 0.45 * max(0.0, nrm[0] * light[0] + nrm[1] * light[1] + nrm[2] * light[2])
        if texel:
            col = (int(min(255, texel[0] * sh)), int(min(255, texel[1] * sh)), int(min(255, texel[2] * sh)), 255)
        else:
            base = (168, 172, 178)
            col = (int(base[0] * sh), int(base[1] * sh), int(base[2] * sh), 255)
        items.append((d, [(p[0], p[1]) for p in proj], col))

    items.sort(key=lambda t: -t[0])
    for _, poly, col in items:
        drw.polygon(poly, fill=col, outline=(0, 0, 0, 40))

    img.save(out_path)
    print(f"rendered {len(items)} faces -> {out_path} (bounds {[round(v,1) for v in smin]} .. {[round(v,1) for v in smax]})")


if __name__ == "__main__":
    args = sys.argv[1:]
    geo_path = args[0]
    out_path = args[1]
    tex = None
    geo_name = None
    hide = ()
    only = None
    if "--tex" in args:
        tex = args[args.index("--tex") + 1]
    if "--geo" in args:
        geo_name = args[args.index("--geo") + 1]
    if "--hide" in args:
        hide = tuple(args[args.index("--hide") + 1].split(","))
    if "--only" in args:
        only = set(args[args.index("--only") + 1].split(","))
    g = load_geometry(geo_path, geo_name)
    render(g, tex, out_path, hide_bones=hide, only_bones=only)


# ---------------------------------------------------------------- animated view

def eval_expr(v, ctx):
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.strip()
        try:
            return float(s)
        except ValueError:
            pass
        expr = s
        for k, val in ctx.items():
            expr = expr.replace(k, str(val))
        expr = expr.replace('?', ' and ').replace(':', ' or ')
        try:
            return float(eval(expr, {"__builtins__": {}}, {}))
        except Exception:
            return 0.0
    return float(v)


def sample_channels(chan, t, ctx):
    """chan may be a list (static), a scalar, or dict of time->value."""
    if isinstance(chan, (int, float)):
        v = float(chan)
        return [v, v, v]
    if isinstance(chan, str):
        v = eval_expr(chan, ctx)
        return [v, v, v]
    if isinstance(chan, list):
        vals = [eval_expr(v, ctx) for v in chan]
        if len(vals) == 1:
            return [vals[0]] * 3
        return vals
    if isinstance(chan, dict):
        keys = sorted(float(k) for k in chan.keys())
        if not keys:
            return [0.0, 0.0, 0.0]
        if t <= keys[0]:
            v0 = chan[str(keys[0])] if str(keys[0]) in chan else chan[next(iter(chan))]
            return norm3([eval_expr(v, ctx) for v in (v0 if isinstance(v0, list) else [v0] * 3)])
        # find bracketing
        prev = keys[0]
        for k in keys:
            if k >= t:
                a = chan[str(k)] if str(k) in chan else chan[fmt_key(k)]
                b = chan[str(prev)] if str(prev) in chan else chan[fmt_key(prev)]
                f = 0.0 if k == prev else (t - prev) / (k - prev)
                a = norm3([eval_expr(v, ctx) for v in a])
                b = norm3([eval_expr(v, ctx) for v in b])
                return [b[i] + (a[i] - b[i]) * f for i in range(3)]
            prev = k
        last = chan[str(keys[-1])] if str(keys[-1]) in chan else chan[fmt_key(keys[-1])]
        return norm3([eval_expr(v, ctx) for v in (last if isinstance(last, list) else [last] * 3)])
    return [0.0, 0.0, 0.0]


def fmt_key(k):
    for cand in (f"{k}", f"{k:g}", f"{round(k,4)}"):
        pass
    return str(k)


def apply_anim(geo, anim, t=0.0, ctx=None):
    """Return dict bone -> {'rotation':..,'position':..,'scale':..} sampled at time t."""
    ctx = ctx or {}
    out = {}
    for bname, chans in anim.get("bones", {}).items():
        d = {}
        for key in ("rotation", "position", "scale"):
            if key in chans:
                d[key] = sample_channels(chans[key], t, ctx)
        out[bname] = d
    return out


def render_animated(geo, anim_state, out_path="apreview.png", tex_path=None,
                    eye=(0, 26, 0), yaw=0.0, pitch=0.0, fov=70.0, size=(900, 560),
                    hide_bones=()):
    from PIL import Image, ImageDraw
    img_tex = Image.open(tex_path) if tex_path else None
    bones = {b["name"]: b for b in geo["bones"]}
    cache = {}

    def bone_matrix(name, depth=0):
        if name in cache:
            return cache[name]
        if depth > 64:
            raise SystemExit("loop " + name)
        b = bones[name]
        pivot = b.get("pivot", [0, 0, 0])
        rot = b.get("rotation", [0, 0, 0])
        st = anim_state.get(name, {})
        pos = st.get("position", [0, 0, 0])
        r = st.get("rotation", rot)
        s = st.get("scale", [1, 1, 1])
        if isinstance(s, (int, float)):
            s = [s, s, s]
        local = mat_trans(pivot)
        local = mat_mul(local, mat_trans(pos))
        local = mat_mul(local, mat_rot(r))
        local = mat_mul(local, mat_scale(s))
        local = mat_mul(local, mat_trans([-p for p in pivot]))
        parent = b.get("parent")
        m = mat_mul(bone_matrix(parent, depth + 1), local) if parent else local
        cache[name] = m
        return m

    yw, pw = math.radians(yaw), math.radians(pitch)
    cy_, sy_ = math.cos(yw), math.sin(yw)
    cp_, sp_ = math.cos(pw), math.sin(pw)
    f = math.tan(math.radians(fov) / 2)
    W, H = size

    def cam(p):
        x = p[0] - eye[0]
        y = p[1] - eye[1]
        z = p[2] - eye[2]
        # yaw around Y then pitch around X: camera looks toward -z
        x, z = x * cy_ - z * sy_, x * sy_ + z * cy_
        y, z = y * cp_ - z * sp_, y * sp_ + z * cp_
        zc = -z
        if zc < 0.05:
            return None
        sx = W / 2 + (x / zc) * (W / 2) / f / (W / H) * (W / H) * (H / W) * (W / H)
        sx = W / 2 + (x / zc) * (H / 2) / f
        sy2 = H / 2 - (y / zc) * (H / 2) / f
        return sx, sy2, zc

    img = Image.new("RGBA", size, (30, 32, 38, 255))
    drw = ImageDraw.Draw(img)
    light = (-0.4, 0.8, -0.45)
    n = math.sqrt(sum(v * v for v in light))
    light = tuple(v / n for v in light)
    items = []
    for bname, b in bones.items():
        if bname in hide_bones:
            continue
        m = bone_matrix(bname)
        for c in b.get("cubes", []):
            o = c["origin"]; s = c["size"]; infl = c.get("inflate", 0)
            cm = m
            if c.get("rotation"):
                pv = c.get("pivot", [0, 0, 0])
                cm = mat_mul(m, mat_mul(mat_trans(pv), mat_mul(mat_rot(c["rotation"]), mat_trans([-p for p in pv]))))
            for fname, flags in FACE_CORNERS.items():
                texel = None
                uvs = c.get("uv")
                if isinstance(uvs, dict) and fname in uvs:
                    uvspec = uvs[fname]
                    texel = tex_sample(img_tex, uvspec["uv"][0], uvspec["uv"][1], *uvspec.get("uv_size", [1, 1]))
                pts = []
                for fx, fy, fz in flags:
                    p = (o[0] - infl + (s[0] + 2 * infl) * fx,
                         o[1] - infl + (s[1] + 2 * infl) * fy,
                         o[2] - infl + (s[2] + 2 * infl) * fz)
                    pts.append(cam(xform(cm, p)))
                if any(p is None for p in pts):
                    continue
                d = sum(p[2] for p in pts) / 4
                nrm = FACE_DIRS[fname]
                sh = 0.55 + 0.45 * max(0.0, nrm[0] * light[0] + nrm[1] * light[1] + nrm[2] * light[2])
                if texel:
                    col = (int(min(255, texel[0] * sh)), int(min(255, texel[1] * sh)), int(min(255, texel[2] * sh)), 255)
                else:
                    base = (150, 155, 160)
                    col = (int(base[0] * sh), int(base[1] * sh), int(base[2] * sh), 255)
                items.append((d, [(p[0], p[1]) for p in pts], col))
    items.sort(key=lambda x: -x[0])
    for _, poly, col in items:
        drw.polygon(poly, fill=col, outline=(0, 0, 0, 30))
    img.save(out_path)
    print("animated render ->", out_path, len(items), "faces")


def mat_scale(s):
    m = mat_ident()
    m[0][0], m[1][1], m[2][2] = s
    return m


def norm3(vals):
    vals = [float(v) for v in vals]
    if len(vals) == 1:
        return vals * 3
    while len(vals) < 3:
        vals.append(vals[-1])
    return vals[:3]
