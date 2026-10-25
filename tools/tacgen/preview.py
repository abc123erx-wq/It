"""Preview renders used while authoring the weapon models (not shipped)."""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
import mcpreview as mp  # noqa: E402

FACE_CORNERS = mp.FACE_CORNERS
FACE_DIRS = mp.FACE_DIRS


def load_geo(path, identifier=None):
    with open(path) as f:
        doc = json.load(f)
    for g in doc["minecraft:geometry"]:
        if identifier is None or g["description"]["identifier"] == identifier:
            return g
    raise SystemExit("geometry not found")


def bone_matrices(geo, state=None):
    state = state or {}
    bones = {b["name"]: b for b in geo["bones"]}
    cache = {}

    def bm(name, d=0):
        if name in cache:
            return cache[name]
        b = bones[name]
        pv = b.get("pivot", [0, 0, 0])
        rot = b.get("rotation", [0, 0, 0])
        s = state.get(name, {})
        pos = s.get("position", [0, 0, 0])
        r = s.get("rotation", rot)
        sc = s.get("scale", [1, 1, 1])
        if isinstance(sc, (int, float)):
            sc = [sc] * 3
        m = mp.mat_trans(pv)
        m = mp.mat_mul(m, mp.mat_trans(pos))
        m = mp.mat_mul(m, mp.mat_rot(r))
        m = mp.mat_mul(m, mp.mat_scale(sc))
        m = mp.mat_mul(m, mp.mat_trans([-v for v in pv]))
        if b.get("parent"):
            m = mp.mat_mul(bm(b["parent"], d + 1), m)
        cache[name] = m
        return m

    return bones, bm


def render(geo, tex_path, out, yaw=35, pitch=18, size=(900, 600), hide_contains=("tp",),
           only_bones=None, bg=(38, 41, 48), quiet=False):
    img_tex = Image.open(tex_path).convert("RGBA") if tex_path and os.path.exists(tex_path) else None
    bones, bm = bone_matrices(geo)
    yw, pw = math.radians(yaw), math.radians(pitch)
    cyw, syw = math.cos(yw), math.sin(yw)
    cpw, spw = math.cos(pw), math.sin(pw)

    faces = []
    mn = [1e9] * 3
    mx = [-1e9] * 3
    for name, b in bones.items():
        if only_bones is not None and name not in only_bones:
            continue
        if any(h in name for h in hide_contains):
            continue
        m = bm(name)
        for c in b.get("cubes", []):
            o, sz = c["origin"], c["size"]
            infl = c.get("inflate", 0)
            cm = m
            if c.get("rotation"):
                pv = c.get("pivot", [0, 0, 0])
                cm = mp.mat_mul(m, mp.mat_mul(mp.mat_trans(pv), mp.mat_mul(mp.mat_rot(c["rotation"]), mp.mat_trans([-p for p in pv]))))
            for fname, flags in FACE_CORNERS.items():
                pts = []
                for fx, fy, fz in flags:
                    p = (o[0] - infl + (sz[0] + 2 * infl) * fx,
                         o[1] - infl + (sz[1] + 2 * infl) * fy,
                         o[2] - infl + (sz[2] + 2 * infl) * fz)
                    pts.append(mp.xform(cm, p))
                texel = None
                uvs = c.get("uv")
                if isinstance(uvs, dict) and fname in uvs:
                    uv = uvs[fname]
                    texel = mp.tex_sample(img_tex, uv["uv"][0], uv["uv"][1], *uv.get("uv_size", [1, 1]))
                for p in pts:
                    for i in range(3):
                        mn[i] = min(mn[i], p[i]); mx[i] = max(mx[i], p[i])
                faces.append((fname, pts, texel))

    center = [(mn[i] + mx[i]) / 2 for i in range(3)]
    extent = max(mx[i] - mn[i] for i in range(3)) or 1
    scale = min(size) * 0.95 / extent

    def proj(p):
        x, y, z = p[0] - center[0], p[1] - center[1], p[2] - center[2]
        x, z = x * cyw - z * syw, x * syw + z * cyw
        y, z = y * cpw - z * spw, y * spw + z * cpw
        return (size[0] / 2 + x * scale, size[1] / 2 - y * scale, z)

    img = Image.new("RGBA", size, bg + (255,))
    drw = ImageDraw.Draw(img)
    light = (-0.35, 0.82, -0.45)
    n = math.sqrt(sum(v * v for v in light))
    light = tuple(v / n for v in light)
    items = []
    for fname, pts, texel in faces:
        pr = [proj(p) for p in pts]
        d = sum(p[2] for p in pr) / 4
        nrm = FACE_DIRS[fname]
        sh = 0.66 + 0.44 * max(0.0, nrm[0] * light[0] + nrm[1] * light[1] + nrm[2] * light[2])
        if texel:
            col = tuple(min(255, int(ch * sh)) for ch in texel[:3]) + (255,)
        else:
            col = (int(120 * sh), int(124 * sh), int(130 * sh), 255)
        items.append((d, [(p[0], p[1]) for p in pr], col))
    items.sort(key=lambda t: -t[0])
    for _, poly, col in items:
        drw.polygon(poly, fill=col, outline=tuple(max(0,c-14) for c in col))
    img.convert("RGB").save(out)
    if not quiet:
        print("->", out, f"({len(items)} faces, bounds {[round(v,1) for v in mn]}..{[round(v,1) for v in mx]})")
    return img


def contact_sheet(paths, out, cols=3, label=True):
    ims = [Image.open(p).convert("RGB") for p in paths]
    w = max(i.width for i in ims)
    h = max(i.height for i in ims)
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (w * cols, h * rows), (18, 19, 23))
    drw = ImageDraw.Draw(sheet)
    for i, im in enumerate(ims):
        x, y = (i % cols) * w, (i // cols) * h
        sheet.paste(im, (x, y))
        if label:
            drw.text((x + 8, y + 6), os.path.basename(paths[i]), fill=(230, 230, 230))
    sheet.save(out)
    print("sheet ->", out)
