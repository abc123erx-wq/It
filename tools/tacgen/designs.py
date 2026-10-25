"""Weapon designs. Authoring space: muzzle at z=0, bore at y=0, x centred."""
import math

from .voxel import Design


# --------------------------------------------------------------- shared parts
def rail(d, z0, z1, y, half_w=1.15, teeth=8, mat="polymer", z_len=None):
    """Picatinny-ish rail: base + raised teeth."""
    d.box("gunmetal", -half_w, y, z0, half_w, y + 0.45, z1)
    span = z1 - z0
    n = teeth
    for i in range(n):
        a = z0 + span * i / n + 0.12
        b = a + span / n * 0.55
        d.box(mat, -half_w - 0.05, y + 0.45, a, half_w + 0.05, y + 0.85, b)


def trigger_guard(d, z0, z1, y_top, y_bot, half_w=1.4, mat="gunmetal"):
    d.box(mat, -half_w, y_top - 0.9, z0, half_w, y_top, z1)          # under the receiver
    d.box(mat, -half_w, y_bot, z1 - 0.9, half_w, y_top, z1)          # rear post
    d.box(mat, -half_w, y_bot, z0, half_w, y_bot + 0.8, z1)          # bottom bar
    d.box("steel", -0.35, y_top - 2.1, z0 + 1.5, 0.35, y_top - 0.9, z0 + 2.6)  # trigger


def curved_mag(d, z_top, y_top, length, half_w, curve=2.2, mat="gunmetal", bone="mag",
               segs=4, seg_h=2.2, taper=0.9, seg_z=6.2):
    for i in range(segs):
        zc = curve * (i / segs) ** 1.5
        w = half_w * (1 - (1 - taper) * i / segs)
        y1 = y_top - seg_h * i
        y0 = y_top - seg_h * (i + 1)
        d.box(mat, -w, y0, z_top + zc, w, y1, z_top + zc + (seg_z if i == 0 else seg_z - 1.0), bone=bone)
    # floor plate
    zc = curve
    d.box("black", -half_w * taper - 0.15, y_top - seg_h * segs - 0.9, z_top + zc - 0.3,
          half_w * taper + 0.15, y_top - seg_h * segs + 0.2, z_top + zc + 5.6, bone=bone)


def slanted_grip(d, z_front, z_back, y_top, y_bot, half_w=1.55, mat="polymer", lean=2.2, steps=6):
    """Pistol grip leaning backwards (z grows as y drops)."""
    for i in range(steps):
        f0, f1 = i / steps, (i + 1) / steps
        y1 = y_top + (y_bot - y_top) * f0
        y0 = y_top + (y_bot - y_top) * f1
        off = lean * f0
        d.box(mat, -half_w, y0, z_front + off, half_w, y1, z_back + off)
    d.box("black", -half_w - 0.1, y_bot - 0.9, z_front + lean, half_w + 0.1, y_bot + 0.4, z_back + lean)


def butt_stock(d, z0, z1, y0, y1, half_w=2.0, mat="black", cheek=True):
    d.box(mat, -half_w, y0, z1 - 1.5, half_w, y1, z1)          # butt plate
    d.box(mat, -half_w + 0.2, y0 + 0.4, z1 - 2.6, half_w - 0.2, y1 - 0.4, z1 - 1.4)
    if cheek:
        d.box(mat, -half_w + 0.35, y1 - 0.8, z0, half_w - 0.35, y1 - 0.1, z1 - 1.4)


# ------------------------------------------------------------------ SMG / rifle
def mp5():
    """HK MP5A3 - 9x19mm SMG (unit ~= 20 mm)."""
    d = Design("mp5", 33.0, "MP5")
    # ---- barrel + flash hider
    d.tube("gunmetal", 0, 0, 0.0, 1.6, 0.95)
    d.tube("black", 0, 0, 1.4, 8.2, 0.62)
    d.box("steel", -0.72, -0.72, 0.15, 0.72, 0.72, 0.9)
    # ---- front sight (hooded)
    d.box("black", -0.9, 0.55, 2.2, 0.9, 2.5, 3.5)
    d.box("black", -0.9, 2.1, 2.2, -0.32, 3.35, 3.5)
    d.box("black", 0.32, 2.1, 2.2, 0.9, 3.35, 3.5)
    d.box("black", -0.9, 2.85, 2.2, 0.9, 3.35, 3.5)
    d.box("lume", -0.13, 2.15, 2.3, 0.13, 2.7, 2.55)
    # ---- cocking tube + charging handle
    d.tube("gunmetal", 0, 1.62, 3.2, 12.6, 0.55)
    d.box("steel", 1.5, 1.2, 4.6, 2.8, 2.1, 5.8)
    d.box("black", 2.6, 1.35, 4.9, 2.95, 1.95, 5.5)
    # ---- handguard
    d.box("polymer", -1.45, -1.95, 3.6, 1.45, 1.35, 12.5)
    d.box("black", -1.5, -1.55, 4.1, 1.5, 1.0, 12.2)
    for i in range(5):
        z = 4.8 + i * 1.45
        d.box("polymer", -1.56, -1.35, z, 1.56, 0.8, z + 0.8)
    d.box("steel", -1.5, 1.35, 11.4, 1.5, 1.55, 12.5)
    d.box("polymer", -1.2, -2.15, 8.6, 1.2, -1.85, 11.6)   # hand stop
    # ---- receiver
    d.box("black", -1.45, -2.65, 12.1, 1.45, 1.9, 21.6)
    d.box("gunmetal", -1.52, -2.2, 12.4, 1.52, 1.35, 21.0)
    d.box("steel", 0.95, -1.1, 14.2, 1.55, 0.35, 18.4)      # ejection port
    d.box("gunmetal", 1.32, -1.35, 13.7, 1.62, 0.65, 19.0)
    d.box("black", -1.5, -3.0, 12.1, 1.5, -2.35, 21.6)      # lower lip
    d.box("gunmetal", -1.2, -2.9, 19.6, 1.2, -2.2, 21.4)    # magwell
    # ---- top rail + rear sight drum
    rail(d, 11.9, 20.4, 1.9, half_w=0.95, teeth=7)
    d.box("black", -0.95, 1.9, 19.9, 0.95, 3.3, 21.9)
    d.box("polymer", -0.75, 3.15, 20.2, 0.75, 3.55, 21.6)
    d.box("lume", -0.13, 2.6, 19.95, 0.13, 3.1, 20.2)
    # ---- trigger group
    trigger_guard(d, 18.4, 22.8, -2.65, -4.5, half_w=1.1)
    # ---- pistol grip (leaning back)
    slanted_grip(d, 20.9, 24.2, -2.9, -8.1, half_w=1.2, lean=1.7, steps=5)
    d.box("polymer", -1.3, -8.6, 22.4, 1.3, -7.6, 26.2)
    # ---- curved magazine (bottom swings forward)
    curved_mag(d, 14.3, -2.6, 12.0, 1.05, curve=-2.6, segs=5, seg_h=1.95, taper=0.94, seg_z=5.4)
    # ---- stock
    d.box("steel", -1.45, 0.15, 21.0, -0.5, 1.45, 31.2)
    d.box("steel", 0.5, 0.15, 21.0, 1.45, 1.45, 31.2)
    d.box("gunmetal", -0.45, 0.35, 21.2, 0.45, 1.25, 30.6)
    d.box("black", -1.55, -1.6, 21.0, 1.55, 1.9, 22.8)
    butt_stock(d, 27.4, 33.0, -2.9, 2.2, half_w=1.5)
    d.box("polymer", -1.55, -0.9, 26.6, 1.55, 1.5, 31.6)
    d.box("gunmetal", -1.6, 1.4, 27.2, 1.6, 1.9, 31.5)
    d.locator("shell", 1.7, 0.0, 16.4)
    return d


def mp5k():
    """HK MP5K - compact 9x19mm (unit ~= 20 mm)."""
    d = Design("mp5k", 18.6, "MP5K")
    # ---- barrel + front sight
    d.tube("gunmetal", 0, 0, 0.0, 1.1, 0.8)
    d.tube("black", 0, 0, 0.9, 3.4, 0.5)
    d.box("black", -0.8, 0.45, 1.2, 0.8, 2.15, 2.4)
    d.box("black", -0.8, 1.85, 1.2, -0.28, 3.0, 2.4)
    d.box("black", 0.28, 1.85, 1.2, 0.8, 3.0, 2.4)
    d.box("black", -0.8, 2.5, 1.2, 0.8, 3.0, 2.4)
    d.box("lume", -0.12, 1.9, 1.3, 0.12, 2.4, 1.55)
    # ---- shroud + cocking tube
    d.box("black", -1.15, -1.6, 2.2, 1.15, 1.15, 7.4)
    d.box("polymer", -1.2, -0.85, 2.7, 1.2, 0.85, 7.2)
    d.tube("gunmetal", 0, 1.45, 2.4, 7.6, 0.45)
    d.box("steel", 1.15, 1.05, 3.0, 2.2, 1.85, 4.0)
    # ---- receiver
    d.box("black", -1.3, -2.45, 7.2, 1.3, 1.75, 15.2)
    d.box("gunmetal", -1.37, -2.0, 7.5, 1.37, 1.3, 14.6)
    d.box("steel", 0.85, -1.0, 8.6, 1.4, 0.3, 12.0)
    rail(d, 7.1, 14.2, 1.75, half_w=0.85, teeth=6)
    d.box("black", -0.85, 1.75, 14.4, 0.85, 3.0, 15.9)
    d.box("lume", -0.12, 2.35, 14.45, 0.12, 2.85, 14.7)
    # ---- vertical foregrip
    d.box("polymer", -0.8, -5.9, 3.2, 0.8, -1.4, 5.2)
    d.box("black", -0.9, -6.5, 3.1, 0.9, -5.8, 5.3)
    d.box("polymer", -0.9, -2.1, 3.1, 0.9, -1.4, 5.3)
    # ---- trigger group
    trigger_guard(d, 12.4, 14.8, -2.45, -4.0, half_w=0.95)
    # ---- magazine (short, slight forward curve), front of the trigger guard
    curved_mag(d, 9.4, -2.4, 10.0, 0.95, curve=-1.1, segs=3, seg_h=1.8, taper=0.96, seg_z=4.8)
    # ---- pistol grip behind it
    slanted_grip(d, 14.9, 17.3, -2.6, -8.0, half_w=1.1, lean=1.2, steps=5)
    d.box("polymer", -1.2, -8.5, 15.9, 1.2, -7.5, 19.2)
    # ---- end cap + sling loop
    d.box("black", -1.25, -2.35, 15.2, 1.25, 1.7, 16.9)
    d.box("steel", -0.3, -0.1, 16.9, 0.3, 0.55, 17.7)
    d.locator("shell", 1.45, 0.15, 10.6)
    return d





# ------------------------------------------------------------- more utilities
def drum_mag(d, cx, cy, z0, r, mat="gunmetal", bone="mag", segs=10):
    for i in range(segs):
        a0 = 3.1416 * 2 * i / segs
        a1 = 3.1416 * 2 * (i + 1) / segs
        x0 = cx + r * math.cos(a0) * 0.55
        x1 = cx + r * math.cos(a1) * 0.55
        y0 = cy + r * math.sin(a0)
        y1 = cy + r * math.sin(a1)
        pad = r * 0.42
        d.box(mat, min(x0, x1) - pad, min(y0, y1) - pad * 0.55,
              z0, max(x0, x1) + pad, max(y0, y1) + pad * 0.55, z0 + 4.6, bone=bone)
    d.box("black", cx - r * 0.45, cy - r * 0.45, z0 - 0.4, cx + r * 0.45, cy + r * 0.45, z0 + 4.8, bone=bone)


def revolver_cylinder(d, z0, half_w, cy=0.0, r=1.7, mat="steel"):
    d.tube(mat, 0, cy, z0, z0 + 4.4, r)
    for i in range(6):
        a = 3.1416 * 2 * i / 6
        d.box("black", -0.28 + r * 0.55 * math.cos(a), cy - 0.28 + r * 0.55 * math.sin(a), z0 - 0.1,
              0.28 + r * 0.55 * math.cos(a), cy + 0.28 + r * 0.55 * math.sin(a), z0 + 4.5)


def optic(d, z0, z1, y, half_w=1.0, mat="black", len_glass=True):
    d.box(mat, -half_w, y, z0, half_w, y + 2.4, z1)
    d.box("gunmetal", -half_w - 0.18, y - 0.15, z0 - 0.2, half_w + 0.18, y + 0.5, z1 + 0.2)
    if len_glass:
        d.box("blue", -half_w + 0.25, y + 0.55, z1 - 0.25, half_w - 0.25, y + 2.0, z1 - 0.05)
        d.box("blue", -half_w + 0.25, y + 0.55, z0 + 0.05, half_w - 0.25, y + 2.0, z0 + 0.25)
    d.box("steel", -0.4, y + 2.4, z0 + 0.6, 0.4, y + 2.9, z1 - 0.6)


# --------------------------------------------------------------------- SMG / PDW
def ump45():
    d = Design("ump45", 32.0, "UMP45")
    d.tube("gunmetal", 0, 0, 0.0, 1.2, 1.0)
    d.tube("black", 0, 0, 1.1, 6.0, 0.7)
    d.box("black", -1.0, 0.8, 1.4, 1.0, 3.0, 2.8)            # front sight
    d.box("lume", -0.14, 2.2, 1.5, 0.14, 2.8, 1.75)
    d.box("polymer", -1.9, -2.1, 5.0, 1.9, 1.9, 12.4)        # handguard
    d.box("black", -1.98, -1.7, 5.4, 1.98, 1.4, 12.0)
    for i in range(4):
        z = 6.0 + i * 1.5
        d.box("gunmetal", -2.02, -1.5, z, 2.02, 1.2, z + 0.7)
    d.box("black", -1.95, 1.9, 11.8, 1.95, 2.35, 12.6)
    d.box("black", -2.1, -2.6, 12.2, 2.1, 2.3, 21.6)         # receiver
    d.box("polymer", -2.18, -2.2, 12.6, 2.18, 1.9, 21.0)
    d.box("steel", 1.4, -1.2, 14.6, 2.2, 0.6, 19.0)          # ejection port
    d.box("black", -2.15, -3.1, 12.2, 2.15, -2.5, 21.6)
    rail(d, 11.9, 20.6, 2.3, half_w=1.0, teeth=7)
    d.box("black", -1.0, 2.3, 20.0, 1.0, 3.7, 21.9)          # rear sight
    d.box("lume", -0.14, 2.9, 20.05, 0.14, 3.4, 20.3)
    trigger_guard(d, 18.0, 22.6, -3.1, -5.0, half_w=1.2)
    slanted_grip(d, 20.0, 23.6, -3.0, -9.0, half_w=1.35, lean=1.8, steps=5)
    d.box("polymer", -1.45, -9.5, 21.8, 1.45, -8.4, 25.4)
    curved_mag(d, 14.2, -3.0, 12.0, 1.3, curve=-1.4, segs=4, seg_h=2.4, taper=0.92, seg_z=6.0)
    # folding stock (skeleton)
    d.box("steel", -1.5, 0.2, 21.2, -0.7, 1.4, 30.6)
    d.box("steel", 0.7, 0.2, 21.2, 1.5, 1.4, 30.6)
    d.box("black", -1.7, -1.4, 21.2, 1.7, 1.9, 23.0)
    butt_stock(d, 27.0, 32.0, -3.2, 2.4, half_w=1.7)
    d.box("polymer", -1.65, -0.8, 26.4, 1.65, 1.4, 31.0)
    d.locator("shell", 1.9, 0.2, 16.4)
    return d


def vector():
    d = Design("vector", 21.0, "Vector")
    d.tube("gunmetal", 0, 0, 0.0, 1.0, 0.9)
    d.tube("black", 0, 0, 0.9, 3.4, 0.62)
    d.box("black", -1.6, -2.0, 2.6, 1.6, 1.7, 12.0)          # shroud
    d.box("polymer", -1.68, -1.6, 3.0, 1.68, 1.3, 11.6)
    for i in range(4):
        z = 3.6 + i * 1.9
        d.box("black", -1.72, -1.4, z, 1.72, 1.1, z + 0.8)
    d.box("black", -1.35, 1.7, 2.4, 1.35, 3.1, 3.8)
    d.box("lume", -0.13, 2.2, 2.5, 0.13, 2.7, 2.75)
    # angled receiver (Krueger style) - upper block slopes down to the rear
    for i in range(6):
        f = i / 6
        d.box("black", -1.6, -0.4 - 0.55 * f, 12.0 + 1.9 * i, 1.6, 2.0 - 0.35 * f, 14.0 + 1.9 * i)
    d.box("gunmetal", -1.68, 1.4, 12.4, 1.68, 1.95, 22.4)
    rail(d, 11.9, 23.0, 1.35, half_w=0.95, teeth=6)
    d.box("black", -0.95, 1.35, 22.4, 0.95, 2.7, 23.6)
    d.box("lume", -0.13, 1.85, 22.45, 0.13, 2.35, 22.7)
    d.box("steel", 1.1, -0.6, 14.4, 1.75, 0.7, 18.0)
    # trigger + grip
    trigger_guard(d, 19.4, 23.2, -3.6, -5.2, half_w=1.05)
    slanted_grip(d, 21.8, 25.4, -3.6, -10.2, half_w=1.2, lean=1.4, steps=5)
    d.box("polymer", -1.3, -10.6, 23.4, 1.3, -9.6, 26.8)
    # long slim magazine in front of the grip
    d.box("gunmetal", -0.95, -9.6, 14.4, 0.95, -1.2, 17.6, bone="mag")
    d.box("black", -1.05, -10.2, 14.2, 1.05, -9.2, 17.8, bone="mag")
    # stock
    d.box("black", -1.45, 0.0, 23.6, 1.45, 1.6, 26.0)
    d.box("steel", -1.0, -0.2, 25.0, 1.0, 1.2, 27.0)
    butt_stock(d, 24.6, 27.4, -3.0, 2.0, half_w=1.5)
    d.locator("shell", 1.5, 0.3, 16.4)
    return d


def p90():
    d = Design("p90", 23.0, "P90")
    # bullpup shell
    d.box("polymer", -1.9, -2.6, 1.6, 1.9, 1.9, 17.0)
    d.box("olive", -1.98, -2.2, 2.0, 1.98, 1.5, 16.6)
    d.box("black", -1.9, -2.9, 9.0, 1.9, -2.4, 15.0)
    d.tube("gunmetal", 0, 0, 0.0, 1.8, 0.8)
    d.box("black", -1.0, -1.6, 0.6, 1.0, 1.6, 2.2)
    d.box("polymer", -1.6, 1.9, 2.2, 1.6, 3.0, 10.4)          # top rail block
    rail(d, 2.2, 10.2, 3.0, half_w=0.85, teeth=5)
    optic(d, 3.0, 7.2, 3.0, half_w=1.0)
    # integrated front grip loop
    d.box("polymer", -1.5, -6.2, 3.0, 1.5, -2.6, 5.0)
    d.box("black", -1.6, -6.8, 2.8, 1.6, -6.0, 5.2)
    trigger_guard(d, 13.0, 16.4, -2.9, -4.6, half_w=1.0)
    # magazine on top (horizontal, along the top of the shell)
    d.box("black", -0.9, 1.9, 10.6, 0.9, 3.4, 17.4, bone="mag")
    d.box("polymer", -1.0, 2.0, 11.0, 1.0, 3.3, 17.0, bone="mag")
    # pistol grip
    slanted_grip(d, 15.2, 18.4, -2.8, -8.2, half_w=1.2, lean=1.0, steps=4)
    d.box("polymer", -1.3, -8.7, 16.4, 1.3, -7.6, 19.4)
    d.box("polymer", -1.7, -1.0, 17.0, 1.7, 1.6, 20.6)        # rear of the shell
    d.box("steel", 1.5, -0.8, 12.0, 2.1, 0.2, 14.4)           # ejection
    d.locator("shell", 1.7, -1.6, 13.0)
    return d


def famas():
    d = Design("famas", 27.0, "FAMAS")
    d.tube("gunmetal", 0, 0, 0.0, 2.0, 0.75)
    d.box("black", -1.1, -0.6, 1.6, 1.1, 1.4, 5.0)            # front block
    d.box("polymer", -1.7, -2.4, 4.0, 1.7, 1.9, 15.6)         # bullpup body
    d.box("black", -1.78, -2.0, 4.4, 1.78, 1.4, 15.2)
    for i in range(4):
        z = 5.0 + i * 1.6
        d.box("gunmetal", -1.82, -1.8, z, 1.82, 1.2, z + 0.75)
    # tall carry handle
    d.box("black", -1.0, 1.9, 5.4, 1.0, 2.4, 14.0)
    d.box("black", -0.9, 2.4, 5.4, -0.5, 4.4, 14.0)
    d.box("black", 0.5, 2.4, 5.4, 0.9, 4.4, 14.0)
    d.box("black", -0.9, 3.9, 5.4, 0.9, 4.4, 14.0)
    d.box("lume", -0.13, 2.6, 5.5, 0.13, 3.2, 5.8)
    # trigger guard (big FAMAS loop)
    d.box("polymer", -1.2, -4.4, 15.4, 1.2, -2.4, 16.6)
    for i in range(4):
        f = i / 4
        d.box("polymer", -1.15, -4.4 - 2.6 * (1 - f), 16.5 + 1.6 * i, 1.15, -4.2 - 2.6 * (1 - f) + 0.9, 18.1 + 1.6 * i)
    slanted_grip(d, 19.0, 22.6, -4.4, -9.6, half_w=1.2, lean=1.2, steps=4)
    # magazine behind the grip
    d.box("gunmetal", -1.1, -8.6, 19.6, 1.1, -3.4, 23.4, bone="mag")
    d.box("black", -1.2, -9.2, 19.4, 1.2, -8.2, 23.6, bone="mag")
    d.box("polymer", -1.5, -1.2, 22.0, 1.5, 1.4, 27.0)        # butt
    d.box("black", -1.55, -1.5, 25.8, 1.55, 1.8, 27.2)
    d.locator("shell", 1.7, 0.2, 12.0)
    return d


# ------------------------------------------------------------------ assault rifles
def m4a1():
    d = Design("m4a1", 34.0, "M4A1")
    d.tube("gunmetal", 0, 0, 0.0, 1.6, 0.75)                 # flash hider
    d.box("black", -0.55, -0.55, 0.2, 0.55, 0.55, 0.5)
    d.tube("steel", 0, 0, 1.4, 4.6, 0.6)
    d.box("steel", 0, 1.5, 1.4, 1.0, 2.3, 2.2)               # gas tube
    # handguard
    d.box("polymer", -1.75, -1.85, 4.2, 1.75, 1.7, 12.4)
    d.box("black", -1.85, -1.5, 4.6, 1.85, 1.35, 12.0)
    for i in range(5):
        z = 5.2 + i * 1.4
        d.box("polymer", -1.9, -1.3, z, 1.9, 1.15, z + 0.75)
    rail(d, 4.0, 21.0, 1.7, half_w=1.05, teeth=10)
    # front sight
    d.box("black", -1.0, 2.5, 2.6, 1.0, 4.6, 4.2)
    d.box("black", -0.32, 4.2, 3.0, 0.32, 5.4, 3.9)
    d.box("black", -1.0, 4.6, 2.6, -0.36, 5.4, 3.9)
    d.box("black", 0.36, 4.6, 2.6, 1.0, 5.4, 3.9)
    # receiver
    d.box("black", -1.6, -2.6, 12.2, 1.6, 1.9, 21.4)
    d.box("gunmetal", -1.68, -2.2, 12.5, 1.68, 1.6, 20.8)
    d.box("steel", 1.0, -1.0, 14.4, 1.66, 0.4, 18.6)
    d.box("gunmetal", 1.5, -1.3, 14.0, 1.82, 0.8, 19.2)
    d.box("steel", -0.5, 0.2, 21.2, 0.5, 1.1, 22.2)          # charging handle
    d.box("steel", 0.5, 1.4, 21.3, 1.6, 2.1, 22.0)           # forward assist
    # rear sight
    d.box("black", -0.95, 1.9, 20.6, 0.95, 3.3, 22.0)
    d.box("lume", -0.13, 2.4, 20.65, 0.13, 2.9, 20.9)
    # trigger group + grip
    trigger_guard(d, 18.6, 23.4, -2.6, -4.6, half_w=1.15)
    slanted_grip(d, 21.4, 24.8, -2.6, -8.6, half_w=1.25, lean=1.8, steps=5)
    d.box("polymer", -1.35, -8.9, 23.0, 1.35, -7.9, 26.6)
    # STANAG magazine
    curved_mag(d, 14.4, -2.6, 12.0, 1.15, curve=-1.2, segs=4, seg_h=2.3, taper=0.95, seg_z=6.4)
    # buffer tube + collapsible stock
    d.tube("gunmetal", 0, 0.9, 21.6, 30.0, 1.05)
    d.box("black", -1.4, -0.6, 25.0, 1.4, 2.3, 33.2)
    d.box("polymer", -1.5, -0.9, 28.6, 1.5, 1.4, 32.4)
    d.box("black", -1.55, -1.8, 32.6, 1.55, 2.6, 34.0)
    d.locator("shell", 1.9, 0.2, 16.4)
    return d


def scar_h():
    d = Design("scar_h", 36.0, "SCAR-H")
    d.tube("gunmetal", 0, 0, 0.0, 2.2, 0.85)
    d.tube("black", 0, 0, 2.0, 6.0, 0.6)
    d.box("tan", -2.0, -2.0, 5.6, 2.0, 1.8, 13.6)            # handguard
    d.box("sand", -2.1, -1.6, 6.0, 2.1, 1.45, 13.2)
    for i in range(4):
        z = 6.6 + i * 1.6
        d.box("black", -2.14, -1.45, z, 2.14, 1.3, z + 0.75)
    rail(d, 5.2, 22.6, 1.8, half_w=1.1, teeth=11)
    d.box("black", -0.95, 2.6, 3.0, 0.95, 4.2, 4.4)          # front sight
    d.box("lume", -0.12, 3.1, 3.1, 0.12, 3.6, 3.35)
    d.box("black", -2.0, -2.5, 13.4, 2.0, 2.1, 22.8)         # receiver
    d.box("tan", -2.1, -2.1, 13.8, 2.1, 1.8, 22.2)
    d.box("steel", 1.3, -1.2, 15.6, 2.15, 0.6, 19.8)
    d.box("gunmetal", 1.95, -1.5, 15.2, 2.3, 1.0, 20.4)
    d.box("steel", 0.4, 2.1, 22.4, 1.4, 2.9, 23.6)           # charging handle
    d.box("black", -1.1, 2.1, 21.6, 1.1, 3.5, 23.2)          # rear sight
    d.box("lume", -0.13, 2.6, 21.65, 0.13, 3.1, 21.9)
    trigger_guard(d, 19.4, 24.2, -2.5, -4.8, half_w=1.2)
    slanted_grip(d, 22.0, 25.6, -2.5, -8.8, half_w=1.3, lean=1.6, steps=5)
    d.box("tan", -1.4, -9.1, 23.6, 1.4, -8.0, 27.0)
    curved_mag(d, 14.8, -2.5, 12.0, 1.2, curve=-1.5, segs=4, seg_h=2.5, taper=0.94, seg_z=6.6)
    # fixed side-folder stock (tan)
    d.box("tan", -1.7, -1.0, 22.8, -0.75, 1.9, 35.2)
    d.box("tan", 0.75, -1.0, 22.8, 1.7, 1.9, 35.2)
    butt_stock(d, 32.6, 36.0, -3.0, 2.4, half_w=1.75, mat="tan")
    d.box("black", -1.75, 0.0, 30.0, 1.75, 1.8, 32.8)
    d.locator("shell", 2.1, 0.3, 17.6)
    return d


def g36c():
    d = Design("g36c", 30.0, "G36C")
    d.tube("gunmetal", 0, 0, 0.0, 1.8, 0.75)
    d.box("black", -1.4, -1.7, 1.6, 1.4, 1.5, 3.0)
    d.box("polymer", -1.85, -2.1, 2.6, 1.85, 1.9, 12.0)      # wide polymer handguard
    for i in range(4):
        z = 3.2 + i * 1.6
        d.box("black", -1.95, -1.9, z, 1.95, 1.7, z + 0.8)
    d.box("polymer", -1.95, -2.5, 2.8, 1.95, -2.1, 11.8)     # lower handguard rail
    d.box("black", -1.9, -2.6, 12.0, 1.9, 2.1, 21.6)         # receiver
    d.box("polymer", -1.98, -2.2, 12.4, 1.98, 1.8, 21.0)
    rail(d, 4.0, 21.0, 1.9, half_w=1.0, teeth=11)
    # carry handle + integrated 3x optic
    d.box("black", -0.95, 2.4, 8.0, 0.95, 3.0, 17.6)
    optic(d, 9.0, 15.0, 3.0, half_w=1.05)
    d.box("black", -0.9, 2.4, 17.6, 0.9, 3.4, 19.4)          # rear sight
    d.box("steel", 1.2, -1.0, 14.0, 2.0, 0.5, 18.2)
    trigger_guard(d, 18.0, 22.8, -2.6, -4.6, half_w=1.2)
    # distinctive straight magazine well + mag
    d.box("black", -1.3, -4.4, 13.6, 1.3, -2.4, 20.2, bone="mag")
    d.box("black", -1.0, -10.0, 13.8, 1.0, -4.2, 20.0, bone="mag")
    d.box("polymer", -1.1, -10.6, 13.6, 1.1, -9.6, 20.2, bone="mag")
    slanted_grip(d, 21.6, 25.2, -2.6, -8.6, half_w=1.25, lean=1.7, steps=5)
    d.box("polymer", -1.35, -8.9, 23.2, 1.35, -7.8, 26.8)
    # folding stock
    d.box("polymer", -1.5, -0.6, 21.4, 1.5, 1.6, 24.2)
    d.box("black", -1.4, -1.8, 24.0, 1.4, 2.0, 30.0)
    d.box("polymer", -1.5, -1.4, 26.0, 1.5, 1.4, 29.4)
    d.box("black", -1.55, -2.0, 29.4, 1.55, 2.3, 30.2)
    d.locator("shell", 2.0, 0.2, 16.0)
    return d


# ------------------------------------------------------------------ sniper rifles
def barrett():
    d = Design("barrett", 56.0, "M82A1")
    d.tube("gunmetal", 0, 0, 0.0, 5.0, 1.0)                  # huge muzzle brake
    for i in range(3):
        d.box("black", -1.05, -0.85, 1.0 + i * 1.2, 1.05, 0.85, 1.0 + i * 1.2 + 0.4)
    d.box("steel", -0.9, -0.9, 5.0, 0.9, 0.9, 9.4)
    d.box("black", -2.1, -2.3, 9.0, 2.1, 1.6, 12.0)          # barrel shroud
    # receiver
    d.box("black", -2.2, -2.6, 11.6, 2.2, 2.4, 34.0)
    d.box("gunmetal", -2.3, -2.2, 12.0, 2.3, 2.0, 33.4)
    d.box("steel", 1.4, -1.4, 15.0, 2.3, 0.9, 25.0)
    d.box("black", -2.3, -3.0, 11.8, 2.3, -2.4, 30.0)
    # long top rail + scope
    rail(d, 12.0, 33.0, 2.4, half_w=1.1, teeth=12)
    optic(d, 15.0, 23.0, 3.0, half_w=1.25)
    d.box("black", -1.3, 3.0, 23.6, 1.3, 4.6, 25.4)
    d.box("lume", -0.13, 3.5, 23.65, 0.13, 4.1, 23.9)
    # bipod (folded)
    d.box("steel", -1.0, -4.4, 6.0, -0.5, -2.0, 7.2)
    d.box("steel", 0.5, -4.4, 6.0, 1.0, -2.0, 7.2)
    # pistol grip + trigger
    trigger_guard(d, 20.6, 26.4, -3.0, -5.6, half_w=1.3)
    slanted_grip(d, 25.0, 28.8, -3.0, -10.4, half_w=1.4, lean=2.0, steps=6)
    d.box("polymer", -1.5, -10.8, 26.6, 1.5, -9.6, 30.6)
    # magazine in front of the grip
    d.box("gunmetal", -1.5, -11.0, 15.6, 1.5, -2.6, 20.0, bone="mag")
    d.box("black", -1.6, -11.8, 15.4, 1.6, -10.6, 20.2, bone="mag")
    # big skeleton stock with recoil pad
    d.box("black", -1.6, -2.2, 30.0, 1.6, 2.0, 34.4)
    d.box("steel", -1.5, -1.6, 33.0, -0.8, 0.6, 52.0)
    d.box("steel", 0.8, -1.6, 33.0, 1.5, 0.6, 52.0)
    d.box("black", -1.9, -3.6, 50.6, 1.9, 2.2, 53.4)
    d.box("polymer", -1.9, -3.4, 53.0, 1.9, 2.0, 56.0)
    d.box("steel", -1.2, 1.9, 34.4, 1.2, 2.6, 44.0)          # cheek rail
    d.locator("shell", 2.3, 0.4, 20.0)
    return d


def intervention():
    d = Design("intervention", 48.0, "Intervention")
    d.tube("gunmetal", 0, 0, 0.0, 3.2, 0.9)
    d.box("steel", -0.7, -0.7, 3.0, 0.7, 0.7, 10.0)
    d.box("olive", -1.9, -2.2, 9.6, 1.9, 1.6, 22.6)          # chassis
    d.box("black", -2.0, -1.8, 10.0, 2.0, 1.2, 22.2)
    for i in range(5):
        z = 10.4 + i * 2.2
        d.box("black", -2.05, -2.4, z, 2.05, 1.5, z + 0.7)
    d.box("black", -2.0, -2.7, 9.8, 2.0, -2.2, 24.0)
    d.box("olive", -2.1, -2.6, 22.4, 2.1, 2.2, 32.0)         # receiver
    d.box("black", -2.2, -2.2, 22.8, 2.2, 1.8, 31.4)
    d.box("steel", 1.2, -1.2, 24.0, 2.1, 0.8, 28.6)
    rail(d, 10.0, 31.0, 2.2, half_w=1.15, teeth=12)
    optic(d, 13.0, 24.0, 2.8, half_w=1.3)
    d.box("black", -1.2, 2.8, 25.0, 1.2, 4.0, 26.8)
    d.box("lume", -0.13, 3.2, 25.05, 0.13, 3.7, 25.3)
    # bolt handle
    d.box("steel", 2.2, -0.6, 28.0, 3.9, 0.5, 29.4, bone="bolt")
    d.box("black", 3.6, -0.9, 27.8, 4.3, 0.8, 29.6, bone="bolt")
    # grip / trigger
    trigger_guard(d, 19.0, 24.0, -2.6, -5.0, half_w=1.25)
    slanted_grip(d, 24.8, 28.4, -2.6, -9.8, half_w=1.3, lean=1.9, steps=6)
    d.box("olive", -1.4, -10.2, 26.4, 1.4, -9.2, 30.0)
    d.box("gunmetal", -1.4, -8.6, 26.0, 1.4, -4.0, 29.4, bone="mag")
    d.box("black", -1.5, -9.2, 25.8, 1.5, -8.4, 29.6, bone="mag")
    # thumbhole stock
    d.box("olive", -1.8, -1.8, 31.8, 1.8, 2.0, 36.0)
    d.box("olive", -1.6, -3.4, 33.0, -0.7, 1.8, 44.0)
    d.box("olive", 0.7, -3.4, 33.0, 1.6, 1.8, 44.0)
    d.box("olive", -1.6, -3.4, 33.0, 1.6, -2.4, 36.0)
    d.box("black", -1.9, -3.8, 44.0, 1.9, 2.4, 46.6)
    d.box("polymer", -1.9, -3.6, 46.6, 1.9, 2.2, 48.4)
    d.box("olive", -1.5, 1.6, 36.0, 1.5, 2.6, 43.0)
    d.locator("shell", 2.1, 0.2, 26.0)
    return d


def remington700():
    d = Design("remington700", 49.0, "M24")
    d.tube("steel", 0, 0, 0.0, 8.0, 0.62)
    d.box("black", -0.75, -0.75, 7.8, 0.75, 0.75, 9.0)
    d.box("wood", -1.7, -2.0, 6.0, 1.7, 1.5, 22.0)           # wooden stock fore-end
    d.box("wood2", -1.8, -1.6, 6.4, 1.8, 1.1, 21.6)
    d.box("black", -0.5, 1.5, 8.0, 0.5, 2.4, 8.8)            # front sight
    d.box("black", -1.8, -2.4, 22.0, 1.8, 2.0, 31.0)         # receiver
    d.box("gunmetal", -1.9, -2.0, 22.4, 1.9, 1.6, 30.4)
    d.box("steel", 1.1, -1.1, 24.0, 1.85, 0.7, 28.4)
    # bolt handle
    d.box("steel", 1.9, -0.5, 28.4, 3.6, 0.7, 30.0, bone="bolt")
    d.box("black", 3.4, -0.9, 28.2, 4.1, 1.0, 30.2, bone="bolt")
    # scope on rings
    d.box("black", -0.6, 2.0, 23.0, 0.6, 2.8, 24.4)
    d.box("black", -0.6, 2.0, 28.0, 0.6, 2.8, 29.4)
    optic(d, 21.0, 30.6, 2.8, half_w=1.1)
    # trigger + grip
    trigger_guard(d, 19.0, 23.6, -2.4, -4.6, half_w=1.15)
    slanted_grip(d, 24.4, 27.8, -2.4, -8.8, half_w=1.25, lean=1.8, steps=5)
    d.box("wood", -1.35, -9.2, 26.0, 1.35, -8.2, 29.4)
    d.box("gunmetal", -1.2, -8.2, 25.0, 1.2, -3.8, 28.6, bone="mag")
    # wooden butt stock
    d.box("wood", -1.75, -1.6, 30.6, 1.75, 2.2, 46.0)
    d.box("wood2", -1.85, -2.2, 40.0, 1.85, 2.6, 48.4)
    d.box("black", -1.85, -2.4, 48.4, 1.85, 2.8, 49.4)
    d.box("wood", -1.6, 1.8, 33.0, 1.6, 2.8, 40.0)
    d.locator("shell", 2.0, 0.2, 26.0)
    return d


# ---------------------------------------------------------------------- shotguns
def nova():
    d = Design("nova", 41.0, "Nova")
    d.tube("gunmetal", 0, 0, 0.0, 26.0, 0.72)                # long barrel
    d.box("black", -0.8, 0.5, 0.4, 0.8, 1.6, 1.4)            # front sight
    d.box("lume", -0.13, 1.0, 0.5, 0.13, 1.5, 0.75)
    # magazine tube below the barrel
    d.tube("gunmetal", 0, -1.7, 2.0, 22.0, 0.62)
    d.box("black", -0.75, -2.5, 2.0, 0.75, -2.2, 22.0)
    # pump handguard
    d.box("polymer", -1.5, -3.0, 8.0, 1.5, 1.1, 17.6, bone="pump")
    d.box("black", -1.6, -2.6, 8.4, 1.6, 0.8, 17.2, bone="pump")
    for i in range(5):
        z = 8.8 + i * 1.7
        d.box("polymer", -1.65, -2.4, z, 1.65, 0.6, z + 0.8, bone="pump")
    d.box("steel", -0.4, -0.5, 17.6, 0.4, 0.5, 18.6, bone="pump")
    # receiver
    d.box("black", -1.6, -2.9, 18.0, 1.6, 1.7, 28.6)
    d.box("gunmetal", -1.7, -2.5, 18.4, 1.7, 1.3, 28.0)
    d.box("steel", 1.0, -1.4, 20.0, 1.72, 0.4, 26.0)
    d.box("gunmetal", 1.55, -1.7, 19.6, 1.9, 0.8, 26.4)
    d.box("black", -1.7, -3.6, 18.2, 1.7, -2.7, 28.6)        # loading port housing
    trigger_guard(d, 24.4, 29.0, -3.6, -5.4, half_w=1.2)
    slanted_grip(d, 26.2, 30.0, -3.6, -9.4, half_w=1.3, lean=1.7, steps=5)
    d.box("polymer", -1.4, -9.8, 27.8, 1.4, -8.8, 31.4)
    # stock
    d.box("polymer", -1.6, -2.0, 28.6, 1.6, 1.9, 33.0)
    butt_stock(d, 32.4, 41.0, -3.6, 2.4, half_w=1.7)
    d.box("polymer", -1.5, -1.2, 32.6, 1.5, 1.8, 39.4)
    d.locator("shell", 1.9, 0.0, 22.0)
    return d


def spas12():
    d = Design("spas12", 40.0, "SPAS-12")
    d.tube("gunmetal", 0, 0, 0.0, 3.2, 0.78)                 # muzzle + brake
    d.box("black", -0.95, -0.7, 2.0, 0.95, 0.7, 3.2)
    d.tube("steel", 0, 0, 3.0, 22.0, 0.68)
    d.tube("gunmetal", 0, -1.7, 3.0, 20.0, 0.6)
    # heat shield
    d.box("black", -1.3, -2.6, 5.0, 1.3, 1.4, 18.0)
    for i in range(6):
        z = 5.4 + i * 2.1
        d.box("polymer", -1.4, -2.3, z, 1.4, 1.1, z + 0.9)
    d.box("black", -0.9, 1.4, 3.4, 0.9, 2.6, 4.6)            # front sight
    d.box("lume", -0.12, 1.9, 3.5, 0.12, 2.4, 3.75)
    # receiver
    d.box("black", -1.6, -3.0, 17.6, 1.6, 2.0, 29.6)
    d.box("gunmetal", -1.7, -2.6, 18.0, 1.7, 1.6, 29.0)
    d.box("steel", 1.0, -1.5, 19.6, 1.72, 0.5, 26.4)
    d.box("black", -1.7, -3.8, 18.0, 1.7, -2.8, 29.6)
    rail(d, 18.0, 27.0, 2.0, half_w=1.0, teeth=6)
    d.box("black", -0.95, 2.0, 27.4, 0.95, 3.4, 29.2)        # rear sight
    trigger_guard(d, 23.0, 28.0, -3.8, -5.6, half_w=1.2)
    slanted_grip(d, 26.6, 30.0, -3.8, -9.6, half_w=1.3, lean=1.5, steps=5)
    d.box("polymer", -1.4, -10.0, 28.0, 1.4, -9.0, 31.6)
    # folding stock (over the top)
    d.box("steel", -0.9, 2.0, 26.6, 0.9, 2.8, 34.0)
    d.box("steel", -0.9, 2.0, 34.0, 0.9, 4.6, 35.2)
    d.box("black", -1.7, 3.6, 33.4, 1.7, 5.2, 34.6)
    d.box("polymer", -1.5, -1.4, 29.4, 1.5, 1.8, 33.6)
    d.box("black", -1.6, -2.4, 33.4, 1.6, 3.0, 40.0)
    d.box("polymer", -1.6, -2.2, 38.8, 1.6, 2.8, 40.2)
    d.locator("shell", 1.9, 0.0, 22.0)
    return d


def aa12():
    d = Design("aa12", 38.0, "AA-12")
    d.tube("gunmetal", 0, 0, 0.0, 3.4, 0.95)
    d.box("black", -1.0, -0.8, 2.8, 1.0, 0.8, 3.6)
    d.tube("steel", 0, 0, 3.2, 12.0, 0.7)
    d.box("polymer", -1.9, -2.3, 11.0, 1.9, 1.8, 30.0)       # big boxy receiver
    d.box("black", -2.0, -1.9, 11.4, 2.0, 1.4, 29.4)
    d.box("black", -1.6, -2.7, 3.0, 1.6, 1.5, 11.4)          # barrel shroud
    for i in range(4):
        z = 3.6 + i * 1.9
        d.box("gunmetal", -1.7, -2.4, z, 1.7, 1.2, z + 0.8)
    rail(d, 11.0, 28.6, 1.8, half_w=1.05, teeth=9)
    d.box("black", -0.9, 1.8, 3.4, 0.9, 3.0, 4.6)
    d.box("lume", -0.12, 2.3, 3.5, 0.12, 2.8, 3.75)
    d.box("steel", 1.5, -1.4, 14.0, 2.1, 0.4, 22.0)
    trigger_guard(d, 22.4, 27.0, -2.9, -4.8, half_w=1.2)
    slanted_grip(d, 25.0, 28.6, -2.9, -8.6, half_w=1.3, lean=1.6, steps=5)
    d.box("polymer", -1.4, -9.0, 26.6, 1.4, -8.0, 30.0)
    # drum magazine
    drum_mag(d, 0.0, -6.4, 13.4, 4.6)
    d.box("polymer", -1.8, -1.6, 29.6, 1.8, 1.9, 37.0)       # solid stock
    d.box("black", -1.9, -2.0, 36.4, 1.9, 2.3, 38.2)
    d.locator("shell", 2.1, 0.2, 18.0)
    return d


# ------------------------------------------------------------------------ pistols
def model29():
    d = Design("model29", 16.0, "Model 29")
    d.tube("steel", 0, 0, 0.0, 8.4, 0.72)
    d.box("steel", -0.55, 0.7, 0.3, 0.55, 1.35, 1.4)         # front sight
    d.box("silver", -1.0, -1.6, 7.6, 1.0, 1.6, 12.0)         # frame
    d.box("steel", -1.05, -1.2, 8.0, 1.05, 1.2, 11.6)
    revolver_cylinder(d, 6.6, 1.05, cy=0.0, r=1.55)          # swing-out cylinder
    d.box("black", -0.35, -0.4, 5.6, 0.35, 0.4, 6.8)         # ejector rod housing
    d.box("steel", -0.28, -0.28, 1.0, 0.28, -0.1, 6.8)
    d.box("steel", -1.1, 0.9, 9.4, 1.1, 1.9, 11.6)           # rear sight
    # hammer
    d.box("black", -0.4, 1.6, 11.2, 0.4, 2.6, 12.2, bone="hammer")
    # trigger guard
    d.box("steel", -0.6, -2.2, 9.6, 0.6, -1.5, 11.6)
    d.box("steel", -0.6, -3.4, 10.4, 0.6, -2.0, 11.6)
    d.box("black", -0.22, -2.6, 10.0, 0.22, -1.4, 10.9)
    # wooden grip (leaning back)
    for i in range(4):
        f = i / 4
        d.box("wood", -1.05, -3.2 - 3.2 * (1 - f) * 0 - 2.9 * (1 - f), 12.0 + 0.9 * (1 - f) * 0 + 1.1 * (1 - f),
              1.05, -2.4 - 2.9 * (1 - f) + 1.0, 13.6 + 1.1 * (1 - f))
    d.box("wood", -1.1, -6.0, 12.6, 1.1, -3.0, 15.5)
    d.box("wood2", -1.15, -6.6, 12.4, 1.15, -5.4, 15.7)
    d.box("steel", -1.0, -1.9, 11.9, 1.0, -0.6, 12.4)        # backstrap
    d.locator("shell", 1.1, 0.3, 9.0)
    return d


def judge():
    d = Design("judge", 17.5, "Judge")
    d.tube("gunmetal", 0, 0, 0.0, 7.4, 0.8)
    d.box("black", -0.6, 0.75, 0.2, 0.6, 1.5, 1.5)            # front sight
    d.box("lume", -0.12, 1.1, 0.3, 0.12, 1.45, 0.55)
    d.box("black", -1.05, -1.9, 6.6, 1.05, 1.7, 12.6)         # polymer frame
    d.box("polymer", -1.12, -1.5, 7.0, 1.12, 1.3, 12.2)
    revolver_cylinder(d, 6.0, 1.05, cy=0.0, r=1.7, mat="gunmetal")
    d.box("black", -0.35, -0.4, 4.6, 0.35, 0.4, 6.2)          # underlug
    d.box("steel", -1.1, 1.3, 10.4, 1.1, 2.2, 12.4)           # rear sight
    d.box("black", -0.42, 1.4, 12.0, 0.42, 2.4, 13.0, bone="hammer")
    d.box("black", -0.65, -2.6, 10.2, 0.65, -1.8, 12.4)       # trigger guard
    d.box("black", -0.65, -3.8, 10.2, 0.65, -2.4, 12.4)
    d.box("steel", -0.24, -2.4, 10.6, 0.24, -1.6, 11.4)
    # rubber grip
    for i in range(3):
        f = i / 3
        d.box("polymer", -1.0, -4.2 - 2.2 * (1 - f), 12.6 + 1.0 * (1 - f), 1.0, -3.0 - 2.2 * (1 - f) + 1.0, 14.6 + 1.0 * (1 - f))
    d.box("black", -1.05, -6.8, 13.2, 1.05, -3.4, 16.6)
    d.box("black", -1.1, -7.4, 13.0, 1.1, -6.2, 16.8)
    d.locator("shell", 1.0, 0.2, 9.4)
    return d


def five_seven():
    d = Design("five_seven", 19.0, "Five-seveN")
    d.tube("gunmetal", 0, 0, 0.0, 2.6, 0.62)
    d.box("black", -0.95, -1.55, 2.0, 0.95, 1.5, 11.6)        # slide
    d.box("polymer", -1.02, -1.2, 2.4, 1.02, 1.2, 11.2)
    d.box("steel", 0.85, -0.9, 3.4, 1.0, 0.4, 8.0)
    d.box("polymer", -1.05, -2.4, 5.6, 1.05, -1.4, 11.8)      # frame
    d.box("black", -1.0, -2.8, 9.8, 1.0, -2.2, 12.0)
    d.box("black", -0.5, 1.5, 0.5, 0.5, 2.0, 1.2)             # front sight
    d.box("lume", -0.12, 1.6, 0.55, 0.12, 1.9, 0.8)
    d.box("black", -0.95, 1.5, 10.6, 0.95, 2.1, 11.9)         # rear sight
    d.box("lume", -0.4, 1.7, 10.65, -0.15, 2.0, 10.9)
    d.box("lume", 0.15, 1.7, 10.65, 0.4, 2.0, 10.9)
    d.box("steel", -0.4, -1.6, 10.0, 0.4, -0.9, 11.0)         # hammer
    d.box("polymer", -1.05, -8.0, 11.4, 1.05, -2.4, 15.4)     # grip
    d.box("black", -1.1, -8.6, 11.2, 1.1, -7.6, 15.6)
    for i in range(4):
        f = i / 4
        d.box("polymer", -1.1, -7.4 + 1.2 * f, 11.6 + 1.0 * f, 1.1, -6.6 + 1.2 * f, 15.4 + 1.0 * f)
    # trigger + guard
    d.box("polymer", -0.7, -3.2, 9.0, 0.7, -2.3, 11.4)
    d.box("black", -0.22, -2.9, 9.6, 0.22, -1.9, 10.3)
    d.box("gunmetal", -0.75, -11.0, 11.8, 0.75, -9.6, 12.2, bone="mag")   # mag floor
    d.box("gunmetal", -0.8, -9.9, 11.6, 0.8, -8.2, 15.2, bone="mag")
    d.locator("shell", 1.0, 0.2, 7.4)
    return d


DESIGNS = {}


def _register():
    for fn in (mp5, mp5k, ump45, vector, p90, famas, m4a1, scar_h, g36c,
               barrett, intervention, remington700, nova, spas12, aa12,
               model29, judge, five_seven):
        DESIGNS[fn.__name__] = fn


_register()
