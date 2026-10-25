"""Render a gun in first-person hold pose, mimicking the in-game camera (preview only)."""
import sys, json, math
sys.path.insert(0, '/home/user/It/tools')
import mcpreview as mp
from PIL import Image, ImageDraw


def pose_bbox(geo, state, skip_tp=True):
    bones = {b['name']: b for b in geo['bones']}
    cache = {}

    def bm(name, d=0):
        if name in cache:
            return cache[name]
        b = bones[name]
        pv = b.get('pivot', [0, 0, 0]); rot = b.get('rotation', [0, 0, 0])
        s = state.get(name, {})
        pos = s.get('position', [0, 0, 0]); r = s.get('rotation', rot); sc = s.get('scale', [1, 1, 1])
        if isinstance(sc, (int, float)):
            sc = [sc] * 3
        m = mp.mat_trans(pv)
        m = mp.mat_mul(m, mp.mat_trans(pos))
        m = mp.mat_mul(m, mp.mat_rot(r))
        m = mp.mat_mul(m, mp.mat_scale(sc))
        m = mp.mat_mul(m, mp.mat_trans([-v for v in pv]))
        par = b.get('parent')
        if par:
            m = mp.mat_mul(bm(par, d + 1), m)
        cache[name] = m
        return m

    mn = [1e9] * 3; mx = [-1e9] * 3
    for name, b in bones.items():
        if skip_tp and 'tp' in name:
            continue
        for c in b.get('cubes', []):
            o = c['origin']; s = c['size']; infl = c.get('inflate', 0)
            cm = bm(name)
            if c.get('rotation'):
                pv = c.get('pivot', [0, 0, 0])
                cm = mp.mat_mul(cm, mp.mat_mul(mp.mat_trans(pv), mp.mat_mul(mp.mat_rot(c['rotation']), mp.mat_trans([-p for p in pv]))))
            for fx in (0, 1):
                for fy in (0, 1):
                    for fz in (0, 1):
                        p = mp.xform(cm, (o[0] - infl + (s[0] + 2 * infl) * fx,
                                          o[1] - infl + (s[1] + 2 * infl) * fy,
                                          o[2] - infl + (s[2] + 2 * infl) * fz))
                        if abs(p[1]) > 1e6:
                            continue
                        for i in range(3):
                            mn[i] = min(mn[i], p[i]); mx[i] = max(mx[i], p[i])
    return mn, mx


def render_orbit(geo, state, out, tex=None, center=None, dist=60, yaw=40, pitch=12,
                 size=(700, 460), hide_tp=True, extra_bones=None):
    """Simple orbit camera; yaw rotates around Y, pitch up/down."""
    img_tex = Image.open(tex) if tex else None
    bones = {b['name']: b for b in geo['bones']}
    cache = {}

    def bm(name, d=0):
        if name in cache:
            return cache[name]
        b = bones[name]
        pv = b.get('pivot', [0, 0, 0]); rot = b.get('rotation', [0, 0, 0])
        s = state.get(name, {})
        pos = s.get('position', [0, 0, 0]); r = s.get('rotation', rot); sc = s.get('scale', [1, 1, 1])
        if isinstance(sc, (int, float)):
            sc = [sc] * 3
        m = mp.mat_trans(pv)
        m = mp.mat_mul(m, mp.mat_trans(pos))
        m = mp.mat_mul(m, mp.mat_rot(r))
        m = mp.mat_mul(m, mp.mat_scale(sc))
        m = mp.mat_mul(m, mp.mat_trans([-v for v in pv]))
        par = b.get('parent')
        if par:
            m = mp.mat_mul(bm(par, d + 1), m)
        cache[name] = m
        return m

    yw, pw = math.radians(yaw), math.radians(pitch)
    cy_, sy_ = math.cos(yw), math.sin(yw)
    cp_, sp_ = math.cos(pw), math.sin(pw)
    W, H = size
    f = 1.0
    scale = min(W, H) * 0.45

    def cam(p):
        x = p[0] - center[0]; y = p[1] - center[1]; z = p[2] - center[2]
        x, z = x * cy_ + z * sy_, -x * sy_ + z * cy_
        y, z = y * cp_ - z * sp_, y * sp_ + z * cp_
        d = dist + z
        if d < 1:
            return None
        return W / 2 + x * scale / d, H / 2 - y * scale / d, d

    img = Image.new('RGBA', size, (28, 30, 36, 255))
    drw = ImageDraw.Draw(img)
    light = (-0.35, 0.8, -0.5)
    n = math.sqrt(sum(v * v for v in light)); light = tuple(v / n for v in light)
    items = []
    for name, b in bones.items():
        if hide_tp and 'tp' in name:
            continue
        m = bm(name)
        for c in b.get('cubes', []):
            o = c['origin']; s = c['size']; infl = c.get('inflate', 0)
            cm = m
            if c.get('rotation'):
                pv = c.get('pivot', [0, 0, 0])
                cm = mp.mat_mul(m, mp.mat_mul(mp.mat_trans(pv), mp.mat_mul(mp.mat_rot(c['rotation']), mp.mat_trans([-p for p in pv]))))
            for fname, flags in mp.FACE_CORNERS.items():
                texel = None
                uvs = c.get('uv')
                if isinstance(uvs, dict) and fname in uvs:
                    face_uv = uvs[fname]
                    texel = mp.tex_sample(img_tex, face_uv['uv'][0], face_uv['uv'][1], *face_uv.get('uv_size', [1, 1]))
                pts = []
                for fx, fy, fz in flags:
                    p = (o[0] - infl + (s[0] + 2 * infl) * fx,
                         o[1] - infl + (s[1] + 2 * infl) * fy,
                         o[2] - infl + (s[2] + 2 * infl) * fz)
                    pts.append(cam(mp.xform(cm, p)))
                if any(p is None for p in pts):
                    continue
                d = sum(p[2] for p in pts) / 4
                nrm = mp.FACE_DIRS[fname]
                sh = 0.5 + 0.5 * max(0.0, nrm[0] * light[0] + nrm[1] * light[1] + nrm[2] * light[2])
                if texel:
                    col = (int(min(255, texel[0] * sh)), int(min(255, texel[1] * sh)), int(min(255, texel[2] * sh)), 255)
                else:
                    base = (150, 150, 155)
                    col = (int(base[0] * sh), int(base[1] * sh), int(base[2] * sh), 255)
                items.append((d, [(p[0], p[1]) for p in pts], col))
    items.sort(key=lambda t: -t[0])
    for _, poly, col in items:
        drw.polygon(poly, fill=col, outline=(0, 0, 0, 30))
    img.save(out)
    print('->', out)


if __name__ == '__main__':
    geo_path, anim_path, anim_name, out, tex = sys.argv[1:6]
    geo = mp.load_geometry(geo_path)
    anim = json.load(open(anim_path))['animations'][anim_name]
    state = mp.apply_anim(geo, anim, t=0.0)
    mn, mx = pose_bbox(geo, state)
    center = [(mn[i] + mx[i]) / 2 for i in range(3)]
    extent = max(mx[i] - mn[i] for i in range(3))
    yaw = float(sys.argv[6]) if len(sys.argv) > 6 else 40
    pitch = float(sys.argv[7]) if len(sys.argv) > 7 else 10
    render_orbit(geo, state, out, tex=tex, center=center, dist=extent * 2.2, yaw=yaw, pitch=pitch)
    print('bbox', [round(v, 1) for v in mn], [round(v, 1) for v in mx])
