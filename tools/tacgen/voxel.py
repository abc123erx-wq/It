"""Voxel-ish gun design DSL.

Authoring space (all guns):
    x : left(-) / right(+) of the shooter, gun is centred on 0
    y : up(+), bore axis at y = 0
    z : 0 = muzzle tip, increasing towards the stock (rear)

A design is a list of Box entries. Each box is mapped into the template rig by a
uniform scale so the finished weapon matches the host weapon's silhouette.
"""

MATERIALS = {
    # name: (base rgb, border rgb)
    "black":    ((52, 54, 60), (30, 31, 35)),
    "polymer":  ((74, 76, 82), (44, 45, 49)),
    "gunmetal": ((96, 101, 109), (58, 61, 66)),
    "steel":    ((140, 145, 152), (88, 92, 98)),
    "silver":   ((186, 190, 196), (124, 128, 134)),
    "tan":      ((186, 158, 110), (124, 104, 70)),
    "sand":     ((156, 136, 96), (104, 90, 62)),
    "olive":    ((116, 124, 84), (74, 80, 52)),
    "wood":     ((134, 88, 50), (86, 54, 28)),
    "wood2":    ((104, 64, 34), (66, 38, 20)),
    "brass":    ((214, 176, 88), (146, 116, 50)),
    "red":      ((166, 54, 46), (104, 30, 26)),
    "lume":     ((186, 236, 146), (118, 168, 90)),
    "darkred":  ((104, 38, 34), (64, 20, 18)),
    "blue":     ((72, 96, 138), (44, 60, 88)),
}


class Box:
    __slots__ = ("mat", "x0", "y0", "z0", "x1", "y1", "z1", "bone", "name")

    def __init__(self, mat, x0, y0, z0, x1, y1, z1, bone="body", name=None):
        self.mat = mat
        self.x0, self.x1 = min(x0, x1), max(x0, x1) + 1e-9
        self.y0, self.y1 = min(y0, y1), max(y0, y1) + 1e-9
        self.z0, self.z1 = min(z0, z1), max(z0, z1) + 1e-9
        self.bone = bone
        self.name = name

    def as_dict(self):
        return dict(mat=self.mat, x0=self.x0, y0=self.y0, z0=self.z0,
                    x1=self.x1, y1=self.y1, z1=self.z1, bone=self.bone, name=self.name)


class Design:
    def __init__(self, gun_id, length, display_name):
        self.gun_id = gun_id
        self.length = length
        self.display_name = display_name
        self.boxes = []
        self.locators = {}

    # ---------------------------------------------------------------- basics
    def box(self, mat, x0, y0, z0, x1, y1, z1, bone="body", name=None):
        b = Box(mat, x0, y0, z0, x1, y1, z1, bone=bone, name=name)
        self.boxes.append(b)
        return b

    def sym(self, mat, half_w, y0, z0, y1, z1, bone="body", name=None, x_off=0.0):
        """Box centred on the x axis (or offset by x_off)."""
        return self.box(mat, x_off - half_w, y0, z0, x_off + half_w, y1, z1, bone=bone, name=name)

    # ------------------------------------------------------- part shortcuts
    def tube(self, mat, cx, cy, z0, z1, r, bone="body", name=None, sides=8):
        """Octagonal prism along z (barrel / suppressor look)."""
        rr = r
        c = rr * 0.4142
        self.box(mat, cx - rr, cy - rr + c, z0, cx + rr, cy + rr - c, z1, bone=bone, name=name)
        self.box(mat, cx - rr + c, cy - rr, z0, cx + rr - c, cy + rr, z1, bone=bone, name=name)
        self.box(mat, cx - rr, cy - rr + c, z0, cx + rr - c, cy + rr - c, z1, bone=bone, name=name)
        self.box(mat, cx + rr - c, cy - rr + c, z0, cx + rr, cy + rr - c, z1, bone=bone, name=name)
        return self

    def step(self, mat, x0, y0, z0, x1, y1, z1, bone="body", steps=1, axis="y", name=None):
        """Stair-stepped box (for angled grips/stocks). axis is the direction of the 'slope'."""
        dx = x1 - x0
        for i in range(steps):
            f0 = i / steps
            f1 = (i + 1) / steps
            if axis == "y":
                self.box(mat, x0, y0 + (y1 - y0) * f0, z0 + (z1 - z0) * f0,
                         x1, y0 + (y1 - y0) * f1, z0 + (z1 - z0) * f1, bone=bone, name=name)
            elif axis == "z":
                self.box(mat, x0, y0 + (y1 - y0) * f0, z0 + (z1 - z0) * f0,
                         x1, y0 + (y1 - y0) * f1, z0 + (z1 - z0) * f1, bone=bone, name=name)
        return self

    def slanted(self, mat, x0, x1, y0, y1, z0, z1, rise=0.0, steps=4, bone="body", name=None):
        """Vertical slab whose top edge is slanted by `rise` over the z span."""
        for i in range(steps):
            f0, f1 = i / steps, (i + 1) / steps
            zz0 = z0 + (z1 - z0) * f0
            zz1 = z0 + (z1 - z0) * f1
            yy = y0 + rise * (f0 + f1) / 2
            self.box(mat, x0, y0 - yy, zz0, x1, y1 - yy * 0 + (-yy) * 0 + (y1 - y0) * 0 + (yy - yy), zz1, bone=bone, name=name)
        return self

    def locator(self, name, x, y, z):
        self.locators[name] = (x, y, z)

    # ------------------------------------------------------------ reporting
    @property
    def z_max(self):
        return max(b.z1 for b in self.boxes)

    def bounds(self):
        mn = [min(getattr(b, k + "0") for b in self.boxes) for k in "xyz"]
        mx = [max(getattr(b, k + "1") for b in self.boxes) for k in "xyz"]
        return mn, mx
