"""Atlas texture generation for the generated weapons.

The atlas is a grid of 16x16 cells; each material owns three cells (top / side /
bottom shading) so a flat voxel model still reads with depth in game, and every
cell has a darker inner frame which becomes a visible panel seam.
"""
import random

from PIL import Image, ImageDraw

from .voxel import MATERIALS

CELL = 16
COLS = 8
ROWS = 8
SHADES = ("top", "side", "bottom")


def material_index(mat):
    return list(MATERIALS).index(mat)


def cell_of(mat, shade):
    idx = material_index(mat) * 3 + SHADES.index(shade)
    return idx % COLS, idx // COLS


def cell_uv_region(mat, shade, inset=0.5):
    """UV rect (u, v, w, h) of the inner area of a material cell."""
    col, row = cell_of(mat, shade)
    return (col * CELL + inset, row * CELL + inset, CELL - inset * 2, CELL - inset * 2)


def face_shade(face):
    if face == "up":
        return "top"
    if face == "down":
        return "bottom"
    return "side"


def build_atlas(seed=7, extra_materials=None):
    rnd = random.Random(seed)
    mats = dict(MATERIALS)
    if extra_materials:
        mats.update(extra_materials)
    size = CELL * COLS, CELL * ROWS
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    drw = ImageDraw.Draw(img)
    for mi, (name, (base, border)) in enumerate(mats.items()):
        for si, shade in enumerate(SHADES):
            idx = mi * 3 + si
            col, row = idx % COLS, idx // COLS
            ox, oy = col * CELL, row * CELL
            factor = (1.16, 1.0, 0.78)[si]
            for y in range(CELL):
                for x in range(CELL):
                    # gentle vertical gradient + fine noise so faces are not flat
                    g = 1.0 + (0.10 * (1 - y / (CELL - 1)) - 0.05)
                    n = rnd.uniform(-0.045, 0.045)
                    rgb = tuple(max(0, min(255, int(c * factor * g * (1 + n)))) for c in base)
                    drw.point((ox + x, oy + y), fill=rgb + (255,))
            # inner frame (panel seam)
            fr = tuple(max(0, min(255, int(c * 0.72))) for c in border)
            drw.rectangle([ox, oy, ox + CELL - 1, oy + CELL - 1], outline=fr + (255,))
            # a couple of bright pixels on the top edge for a bevel highlight
            hi = tuple(max(0, min(255, int(c * 1.35))) for c in base)
            drw.line([ox + 2, oy + 1, ox + CELL - 3, oy + 1], fill=hi + (255,))
    return img


def save_atlas(path, **kw):
    img = build_atlas(**kw)
    img.save(path)
    return img
