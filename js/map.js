// ============================================================
//  Mapa 2D derivado do formato de layouts BO1/mapkit
// ============================================================
import { resolveCircleRect, clamp, dist2 } from "./util.js";

const mapRect = (mins, maxs) => ({ x0: mins[0], y0: mins[1], x1: maxs[0], y1: maxs[1] });
const center = (r) => ({ x: (r.x0 + r.x1) / 2, y: (r.y0 + r.y1) / 2 });

function rectForEdge(side, at, a, b, thick = 22) {
  if (side === "left" || side === "right") return { x0: at - thick / 2, y0: a, x1: at + thick / 2, y1: b };
  return { x0: a, y0: at - thick / 2, x1: b, y1: at + thick / 2 };
}

/** Converte o JSON-authored (formato familiar ao mapkit) para geometria runtime. */
export function prepareMap(raw) {
  const map = {
    ...raw,
    rooms: [], doors: [], windows: [], perks: [], wallbuys: [], boxes: [],
    pap: [], switches: [], props: [], spawns: [], colliders: [], wallSegments: [],
    byId: new Map(), bounds: { x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity }
  };

  for (const edit of raw.edits || []) {
    if (edit.kind === "room") {
      const r = { ...edit, ...mapRect(edit.mins, edit.maxs), center: null };
      r.center = center(r);
      map.rooms.push(r); map.byId.set(r.name, r);
      map.bounds.x0 = Math.min(map.bounds.x0, r.x0 - (r.wall || 0));
      map.bounds.y0 = Math.min(map.bounds.y0, r.y0 - (r.wall || 0));
      map.bounds.x1 = Math.max(map.bounds.x1, r.x1 + (r.wall || 0));
      map.bounds.y1 = Math.max(map.bounds.y1, r.y1 + (r.wall || 0));
    }
  }

  const roomNames = new Set(map.rooms.map((r) => r.name));
  for (const edit of raw.edits || []) {
    if (edit.kind === "door" || edit.kind === "debris") {
      const e = { ...edit, ...mapRect(edit.mins, edit.maxs), center: null };
      e.center = center(e); e.id = edit.name || `barrier_${map.doors.length}`;
      e.kind = edit.kind;
      e.from = roomNames.has(edit.from) ? edit.from : map.rooms[0]?.name;
      e.to = roomNames.has(edit.to) ? edit.to : map.rooms[0]?.name;
      map.doors.push(e);
    } else if (edit.kind === "window") {
      const room = map.byId.get(edit.room) || map.rooms.find((r) => {
        const x = edit.origin?.[0] || 0, y = edit.origin?.[1] || 0;
        return x >= r.x0 - 5 && x <= r.x1 + 5 && y >= r.y0 - 5 && y <= r.y1 + 5;
      });
      if (!room) continue;
      const w = { ...edit, id: edit.name || `window_${map.windows.length}`, x: edit.origin[0], y: edit.origin[1], room: room.name, boards: 6, maxBoards: 6 };
      const distances = [
        [Math.abs(w.x - room.x0), "left"], [Math.abs(w.x - room.x1), "right"],
        [Math.abs(w.y - room.y0), "top"], [Math.abs(w.y - room.y1), "bottom"]
      ].sort((a, b) => a[0] - b[0]);
      w.side = distances[0][1];
      w.vertical = w.side === "left" || w.side === "right";
      w.edge = w.vertical ? (w.side === "left" ? room.x0 : room.x1) : (w.side === "top" ? room.y0 : room.y1);
      w.axis = w.vertical ? w.y : w.x;
      w.inner = w.vertical
        ? { x: w.edge + (w.side === "left" ? 1 : -1) * 46, y: w.axis }
        : { x: w.axis, y: w.edge + (w.side === "top" ? 1 : -1) * 46 };
      w.outer = w.vertical
        ? { x: w.edge + (w.side === "left" ? -1 : 1) * 58, y: w.axis }
        : { x: w.axis, y: w.edge + (w.side === "top" ? -1 : 1) * 58 };
      map.windows.push(w);
    } else if (edit.kind === "perk") {
      const data = { ...edit, id: edit.name || edit.perk, x: edit.origin[0], y: edit.origin[1], room: edit.room };
      map.perks.push(data);
    } else if (edit.kind === "wallbuy") {
      map.wallbuys.push({ ...edit, id: edit.name, x: edit.origin[0], y: edit.origin[1], room: edit.room });
    } else if (edit.kind === "mysterybox") {
      map.boxes.push({ ...edit, id: edit.name, x: edit.origin[0], y: edit.origin[1], room: edit.room });
    } else if (edit.kind === "pap") {
      map.pap.push({ ...edit, id: edit.name, x: edit.origin[0], y: edit.origin[1], room: edit.room });
    } else if (edit.kind === "powerswitch") {
      map.switches.push({ ...edit, id: edit.name, x: edit.origin[0], y: edit.origin[1], room: edit.room });
    } else if (edit.kind === "box") {
      const p = { ...edit, ...mapRect(edit.mins, edit.maxs), id: edit.name };
      map.props.push(p);
    } else if (edit.kind === "spawn") {
      map.spawns.push({ id: `spawn_${map.spawns.length}`, x: edit.origin[0], y: edit.origin[1], yaw: edit.yaw || 0, room: edit.zone || "palco" });
    }
  }

  // Gera paredes perimetrais com aberturas para as portas e vãos das janelas.
  for (const room of map.rooms) {
    const sides = [
      { name: "left", at: room.x0, a: room.y0, b: room.y1, vertical: true },
      { name: "right", at: room.x1, a: room.y0, b: room.y1, vertical: true },
      { name: "top", at: room.y0, a: room.x0, b: room.x1, vertical: false },
      { name: "bottom", at: room.y1, a: room.x0, b: room.x1, vertical: false }
    ];
    for (const side of sides) {
      const doorCuts = [];
      for (const d of map.doors) {
        const dw = d.x1 - d.x0, dh = d.y1 - d.y0;
        if (side.vertical && dw <= dh * 1.15 && Math.abs(d.center.x - side.at) <= 105) {
          const lo = Math.max(side.a, d.y0), hi = Math.min(side.b, d.y1);
          if (hi > lo) doorCuts.push([lo, hi]);
        } else if (!side.vertical && dh <= dw * 1.15 && Math.abs(d.center.y - side.at) <= 105) {
          const lo = Math.max(side.a, d.x0), hi = Math.min(side.b, d.x1);
          if (hi > lo) doorCuts.push([lo, hi]);
        }
      }
      const windowCuts = map.windows.filter((w) => w.room === room.name && w.vertical === side.vertical && w.side === side.name)
        .map((w) => ({ lo: Math.max(side.a, w.axis - 72), hi: Math.min(side.b, w.axis + 72), id: w.id }))
        .filter((w) => w.hi > w.lo);
      const points = new Set([side.a, side.b]);
      for (const [lo, hi] of doorCuts) { points.add(lo); points.add(hi); }
      for (const w of windowCuts) { points.add(w.lo); points.add(w.hi); }
      const ordered = [...points].sort((a, b) => a - b);
      for (let i = 0; i < ordered.length - 1; i++) {
        const a = ordered[i], b = ordered[i + 1], mid = (a + b) / 2;
        if (doorCuts.some(([lo, hi]) => mid > lo - 0.01 && mid < hi + 0.01)) continue;
        const win = windowCuts.find((w) => mid >= w.lo - 0.01 && mid <= w.hi + 0.01);
        const rect = rectForEdge(side.name, side.at, a, b, 24);
        const coll = { ...rect, kind: win ? "window" : "wall", room: room.name, side: side.name, windowId: win?.id || null, material: room.wallMaterial || "wall" };
        map.colliders.push(coll); map.wallSegments.push(coll);
      }
    }
  }

  for (const prop of map.props) {
    map.colliders.push({ x0: prop.x0, y0: prop.y0, x1: prop.x1, y1: prop.y1, kind: "prop", id: prop.id, material: prop.material });
  }

  // Bounds for draw/camera/spawn safety.
  map.bounds.x0 -= 42; map.bounds.y0 -= 42; map.bounds.x1 += 42; map.bounds.y1 += 42;
  return map;
}

export function roomAt(map, x, y, margin = 0) {
  let best = null, score = Infinity;
  for (const r of map.rooms) {
    if (x >= r.x0 - margin && x <= r.x1 + margin && y >= r.y0 - margin && y <= r.y1 + margin) {
      const d = dist2(x, y, r.center.x, r.center.y);
      if (d < score) { score = d; best = r; }
    }
  }
  if (best) return best;
  for (const r of map.rooms) {
    const px = clamp(x, r.x0, r.x1), py = clamp(y, r.y0, r.y1);
    const d = dist2(x, y, px, py);
    if (d < score) { score = d; best = r; }
  }
  return best;
}

export function roomGraphPath(map, world, fromRoom, toRoom, ignoreLocked = false) {
  if (!fromRoom || !toRoom) return [];
  if (fromRoom === toRoom) return [];
  const queue = [fromRoom], prev = new Map([[fromRoom, null]]), via = new Map();
  while (queue.length) {
    const current = queue.shift();
    if (current === toRoom) break;
    for (const door of map.doors) {
      const unlocked = !!world.unlocked?.[door.id];
      if (!ignoreLocked && !unlocked) continue;
      let next = null;
      if (door.from === current) next = door.to;
      else if (door.to === current) next = door.from;
      if (!next || prev.has(next)) continue;
      prev.set(next, current); via.set(next, door); queue.push(next);
    }
  }
  if (!prev.has(toRoom) && !ignoreLocked) return roomGraphPath(map, world, fromRoom, toRoom, true);
  if (!prev.has(toRoom)) return [];
  const path = [];
  let node = toRoom;
  while (node !== fromRoom) { path.unshift(via.get(node)); node = prev.get(node); }
  return path;
}

export function accessibleRooms(map, world, startRoom) {
  const seen = new Set([startRoom]);
  const q = [startRoom];
  while (q.length) {
    const current = q.shift();
    for (const d of map.doors) {
      if (!world.unlocked?.[d.id]) continue;
      const next = d.from === current ? d.to : d.to === current ? d.from : null;
      if (next && !seen.has(next)) { seen.add(next); q.push(next); }
    }
  }
  return seen;
}

/** Move a circle while sliding along walls. `isPlayer` controls broken-window collision. */
export function moveWithCollision(map, world, entity, dx, dy, radius, isPlayer = false) {
  let x = entity.x, y = entity.y;
  const tryStep = (nx, ny) => {
    let tx = nx, ty = ny;
    for (let pass = 0; pass < 3; pass++) {
      let moved = false;
      for (const c of map.colliders) {
        if (c.kind === "window" && !isPlayer && (world.windows?.[c.windowId] ?? 6) <= 0) continue;
        const hit = resolveCircleRect(tx, ty, radius, c);
        if (hit) { tx = hit.x; ty = hit.y; moved = true; }
      }
      if (!moved) break;
    }
    for (const d of map.doors) {
      if (world.unlocked?.[d.id]) continue;
      const barrier = { x0: d.x0 + 3, y0: d.y0 + 3, x1: d.x1 - 3, y1: d.y1 - 3 };
      const hit = resolveCircleRect(tx, ty, radius, barrier);
      if (hit) { tx = hit.x; ty = hit.y; }
    }
    const b = map.bounds;
    tx = clamp(tx, b.x0, b.x1); ty = clamp(ty, b.y0, b.y1);
    return { x: tx, y: ty };
  };
  const all = tryStep(x + dx, y + dy);
  if (Math.hypot(all.x - x, all.y - y) > 0.01) return all;
  const xx = tryStep(x + dx, y);
  if (Math.hypot(xx.x - x, xx.y - y) > 0.01) return xx;
  return tryStep(x, y + dy);
}

export function windowPosition(w, inside = false) {
  return inside ? w.inner : w.outer;
}
