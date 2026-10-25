"""Rename / shift helpers used to clone an existing gun definition into a new one."""
import json
import re


def load(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def dump(path, doc, indent=None):
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=indent, ensure_ascii=False)
        f.write("\n")


def read_text(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def write_text(path, text):
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# --------------------------------------------------------------------------
# suffixes of the host weapon id that must be renamed when cloning.
# bone names of the rig (mk18tp, m870_classic, glock17rarm, ...) are absent
# from this list on purpose: the new geometry reuses the host skeleton, so
# every animation channel keeps pointing at the original bone names.
RENAME_TAILS = (
    "_fp_reload_empty_finish", "_fp_reload_finish", "_fp_reload_start", "_fp_reload_tac",
    "_fp_reload", "_fp_inspect", "_fp_sprint", "_fp_draw", "_fp_hold", "_fp_sight", "_fp",
    "_tp_crawl", "_tp",
    "_firest", "_fires", "_fire2", "_fire",
    "_emp", "_reload", "_inspect", "_draw", "_bolt",
    "reloading", "reloadtac", r"reload\d*",
    "shoot", "quantity",
    "muzzle2", "muzzle", "shell2", "shell", "locator2", "locator",
    "recipe",
    "b", "emp",
)

# properties are shared by every weapon and must never be renamed
PROPERTY_MASK = ("tac_guns:coltpythonreload", "tac_guns:gunreload", "tac_guns:itemtab",
                 "tac_guns:tab", "tac_guns:item")

_TAIL_RE = "|".join(RENAME_TAILS)
_BARE = r"(?![A-Za-z0-9_])"
_PRE = r"(?<![A-Za-z0-9_])"


def gun_text(text, old, new, bare=False):
    """Rename weapon tokens of `old` into `new` inside one string."""
    masked = {}
    for i, prop in enumerate(PROPERTY_MASK):
        if prop in text:
            key = f"\x00P{i}\x00"
            masked[key] = prop
            text = text.replace(prop, key)

    # explicit identifiers first (they embed the weapon name inside longer names)
    text = re.sub(r"geometry\." + re.escape(old) + r"root" + _BARE, f"geometry.{new}root", text)
    text = re.sub(r"Geometry\." + re.escape(old) + r"root" + _BARE, f"Geometry.{new}root", text)
    text = re.sub(r"geometry\." + re.escape(old) + _BARE, f"geometry.{new}", text)
    text = re.sub(r"Geometry\." + re.escape(old) + _BARE, f"Geometry.{new}", text)
    text = re.sub(r"controller\.render\.player\." + re.escape(old) + r"\.first_person",
                  f"controller.render.player.{new}.first_person", text)
    text = re.sub(r"controller\.render\." + re.escape(old) + _BARE, f"controller.render.{new}", text)
    text = re.sub(r"controller\.animation\." + re.escape(old) + _BARE,
                  f"controller.animation.{new}", text)
    text = re.sub(r"animation\." + re.escape(old) + r"\.", f"animation.{new}.", text)
    text = re.sub(r"texture\." + re.escape(old) + _BARE, f"texture.{new}", text)
    text = re.sub(r"tac_guns:" + re.escape(old) + _BARE, f"tac_guns:{new}", text)
    text = re.sub(r"bullet:" + re.escape(old) + _BARE, f"bullet:{new}", text)
    text = re.sub(_PRE + re.escape(old) + r":(nsight|sight)", rf"{new}:\1", text)
    text = re.sub(_PRE + re.escape(old) +
                  r"\.(shoot|draw|reload|reload_start|reload_finish|reload_empty_finish|"
                  r"tacreload|inspect|bolt|overheat|barrel)" + _BARE, rf"{new}.\1", text)
    # locators
    text = re.sub(_PRE + re.escape(old) + r"(locator2|locator|muzzle2|muzzle|shell2|shell)" + _BARE,
                  lambda m: f"{new}muzzle2" if m.group(1).endswith("locator2") or m.group(1) == "muzzle2"
                  else f"{new}muzzle" if m.group(1) in ("locator", "muzzle")
                  else f"{new}shell2" if m.group(1) == "shell2" else f"{new}shell", text)
    # weapon name with a known non-bone suffix
    text = re.sub(_PRE + re.escape(old) + r"(?:" + _TAIL_RE + r")" + _BARE, lambda m: new + m.group(0)[len(old):], text)
    if bare:
        text = re.sub(_PRE + re.escape(old) + _BARE, new, text)

    for key, prop in masked.items():
        text = text.replace(key, prop)
    return text


def gun_obj(obj, old, new, bare=True, command_strings_only=False):
    """Recursively rename keys and string values of a parsed JSON structure."""
    if isinstance(obj, dict):
        return {gun_obj(k, old, new, bare, command_strings_only):
                gun_obj(v, old, new, bare, command_strings_only) for k, v in obj.items()}
    if isinstance(obj, list):
        return [gun_obj(v, old, new, bare, command_strings_only) for v in obj]
    if isinstance(obj, str):
        use_bare = bare and (not command_strings_only or obj.startswith("/"))
        return gun_text(obj, old, new, bare=use_bare)
    return obj


def shift_property_values(obj, prop, lo, hi, delta):
    """Move every numeric comparison on `prop` inside [lo, hi] by `delta`."""
    if delta == 0:
        return obj
    if isinstance(obj, dict):
        return {k: shift_property_values(v, prop, lo, hi, delta) for k, v in obj.items()}
    if isinstance(obj, list):
        return [shift_property_values(v, prop, lo, hi, delta) for v in obj]
    if isinstance(obj, str) and prop in obj:
        def repl(m):
            value = int(m.group(2))
            return m.group(1) + str(value + delta) if lo <= value <= hi else m.group(0)
        return re.sub(r"(property\('" + re.escape(prop) + r"'\)\s*(?:==|>=|<=|>|<)\s*)(\d+)", repl, obj)
    return obj


def shift_property_text(text, prop, lo, hi, delta):
    if delta == 0:
        return text

    def repl(m):
        value = int(m.group(2))
        return m.group(1) + str(value + delta) if lo <= value <= hi else m.group(0)

    return re.sub(r"(property\('" + re.escape(prop) + r"'\)\s*(?:==|>=|<=|>|<)\s*)(\d+)", repl, text)


def clone_items(doc, old, new):
    return gun_obj(doc, old, new)
