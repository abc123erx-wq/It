"""Author-time check: build a design against its template and render previews."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tacgen.analysis import load_template      # noqa: E402
from tacgen.geometry import build_geometry     # noqa: E402
from tacgen import texture as texmod           # noqa: E402
from tacgen import preview                     # noqa: E402
from tacgen.designs import DESIGNS             # noqa: E402

CONFIGS = {
    "mp5": dict(template="mk18", body_parent="mk18",
                part_bones={"mag": "magazine"}, locator_prefix="mp5"),
}


def main(gun_id, outdir="/tmp/gunpreview"):
    os.makedirs(outdir, exist_ok=True)
    cfg = dict(CONFIGS[gun_id])
    tpl = load_template(cfg["template"])
    design = DESIGNS[gun_id]()
    doc = build_geometry(tpl, design, cfg)
    geo = doc["minecraft:geometry"][0]
    gpath = os.path.join(outdir, f"{gun_id}.geo.json")
    with open(gpath, "w") as f:
        f.write(__import__("json").dumps(doc, indent=1))
    atlas = os.path.join(outdir, f"{gun_id}.png")
    texmod.save_atlas(atlas)
    outs = []
    for yaw, pitch, tag in ((35, 16, "34"), (90, 0, "side"), (0, 0, "front")):
        p = os.path.join(outdir, f"{gun_id}_{tag}.png")
        preview.render(geo, atlas, p, yaw=yaw, pitch=pitch, size=(760, 460))
        outs.append(p)
    # reference: the host template at the same scale, for proportion comparison
    ref = preview.load_geo(tpl.geo_path, f"geometry.{cfg['template']}")
    p = os.path.join(outdir, f"{gun_id}_ref.png")
    preview.render(ref, os.path.join("src", "TacGuns(R)", "textures", "gun", cfg["template"] + ".png"),
                   p, yaw=35, pitch=16, size=(760, 460))
    outs.append(p)
    preview.contact_sheet(outs, os.path.join(outdir, f"{gun_id}_sheet.png"), cols=2)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "mp5")
