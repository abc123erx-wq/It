// ============================================================
//  Utilitários: matemática, RNG determinístico, pooling
// ============================================================

export const TAU = Math.PI * 2;

export const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
export const lerp = (a, b, t) => a + (b - a) * t;
export const dist2 = (ax, ay, bx, by) => { const dx = bx - ax, dy = by - ay; return dx * dx + dy * dy; };
export const dist = (ax, ay, bx, by) => Math.hypot(bx - ax, by - ay);

export function angLerp(a, b, t) {
  let d = ((b - a + Math.PI) % TAU + TAU) % TAU - Math.PI;
  return a + d * t;
}

export function angleTo(ax, ay, bx, by) { return Math.atan2(by - ay, bx - ax); }

/** Distância ponto -> segmento (usada para colisão com paredes finas). */
export function distToSeg(px, py, ax, ay, bx, by) {
  const dx = bx - ax, dy = by - ay;
  const l2 = dx * dx + dy * dy;
  if (l2 === 0) return Math.hypot(px - ax, py - ay);
  let t = ((px - ax) * dx + (py - ay) * dy) / l2;
  t = clamp(t, 0, 1);
  return Math.hypot(px - (ax + t * dx), py - (ay + t * dy));
}

// ---------- RNG determinístico (mulberry32) ----------
export function makeRng(seed) {
  let a = seed >>> 0;
  const f = () => {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  f.int = (n) => Math.floor(f() * n);
  f.range = (lo, hi) => lo + f() * (hi - lo);
  f.pick = (arr) => arr[Math.floor(f() * arr.length)];
  f.chance = (p) => f() < p;
  f.seed = () => a;
  return f;
}

export function hashStr(s) {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}

// ---------- IDs / códigos ----------
const CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"; // sem chars ambíguos
export function makeRoomCode(len = 5) {
  const c = new Uint32Array(len);
  (globalThis.crypto || { getRandomValues: (a) => a.forEach((_, i) => (a[i] = Math.random() * 4294967296)) }).getRandomValues(c);
  let s = "";
  for (let i = 0; i < len; i++) s += CODE_ALPHABET[c[i] % CODE_ALPHABET.length];
  return s;
}

export function makeId() {
  const c = new Uint32Array(2);
  globalThis.crypto.getRandomValues(c);
  return (c[0].toString(36) + c[1].toString(36)).slice(0, 11);
}

export const uid = () => makeId() + makeId();

// ---------- Geometria: retângulos ----------
export function rectsOverlap(a, b) {
  return a.x0 < b.x1 && a.x1 > b.x0 && a.y0 < b.y1 && a.y1 > b.y0;
}
export function pointInRect(px, py, r) {
  return px >= r.x0 && px <= r.x1 && py >= r.y0 && py <= r.y1;
}
/** Empurra um círculo (px,py,r) para fora do retângulo r. Retorna novo {x,y} ou null. */
export function resolveCircleRect(px, py, rad, r) {
  const cx = clamp(px, r.x0, r.x1);
  const cy = clamp(py, r.y0, r.y1);
  const dx = px - cx, dy = py - cy;
  const d2 = dx * dx + dy * dy;
  if (d2 >= rad * rad - 1e-6) return null;
  if (d2 > 1e-9) {
    const d = Math.sqrt(d2);
    return { x: cx + (dx / d) * rad, y: cy + (dy / d) * rad };
  }
  // centro dentro do rect: empurra pela borda mais próxima
  const l = px - r.x0, rr = r.x1 - px, t = py - r.y0, b = r.y1 - py;
  const m = Math.min(l, rr, t, b);
  if (m === l) return { x: r.x0 - rad, y: py };
  if (m === rr) return { x: r.x1 + rad, y: py };
  if (m === t) return { x: px, y: r.y0 - rad };
  return { x: px, y: r.y1 + rad };
}

// ---------- Serialização compacta ----------
export const pack = (arr) => arr.map((x) => (Number.isFinite(x) ? +x.toFixed(1) : 0)).join(",");
export const packList = (list) => list.join(";");
export function unpackList(str, n) {
  if (!str) return [];
  const out = [];
  const rows = str.split(";");
  for (let i = 0; i < rows.length; i++) {
    if (!rows[i]) continue;
    const p = rows[i].split(",");
    out.push(p);
  }
  return out;
}

export const r1 = (v) => Math.round(v * 10) / 10;
export const r0 = (v) => Math.round(v);

export function fmtTime(ms) {
  const s = Math.max(0, Math.floor(ms / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

export function fmtNum(n) {
  return n >= 10000 ? (n / 1000).toFixed(1) + "k" : String(n);
}

// ---------- DOM ----------
export const $ = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
export function el(tag, cls, html) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  return e;
}
export function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// ---------- Persistência local ----------
export const store = {
  get(k, d) { try { const v = localStorage.getItem("bo1z." + k); return v == null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem("bo1z." + k, JSON.stringify(v)); } catch {} }
};

// ---------- Cores de jogador ----------
export const PLAYER_COLORS = ["#7ec8ff", "#ffcf5c", "#7dffa8", "#ff7d9c", "#c79bff", "#ffb27d"];
