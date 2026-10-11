// ============================================================
//  Renderer Canvas 2D — cena top-down original, sem assets externos
// ============================================================
import { PERKS, getWeapon } from "./bo1data.js";
import { clamp, lerp, dist, angLerp, fmtNum } from "./util.js";

const FLOOR = {
  wood: ["#382e29", "#272320"], stage: ["#49363a", "#302a2d"], concrete: ["#31393a", "#22292a"],
  carpet: ["#45252e", "#30212b"], metal: ["#2a353b", "#1d292e"], marble: ["#3b3b39", "#272827"],
  tile: ["#304047", "#232f35"]
};
const MATERIAL = {
  wood: ["#735442", "#382b25"], seat: ["#754e50", "#372c34"], rubble: ["#625e54", "#393a37"],
  crate: ["#80613e", "#463828"], metal: ["#687779", "#303c40"], marble: ["#8a8070", "#494943"]
};

export class GameView {
  constructor(canvas, map) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d", { alpha: false });
    this.map = map;
    this.world = null;
    this.width = 1; this.height = 1; this.dpr = 1;
    this.scale = 0.65; this.offsetX = 0; this.offsetY = 0;
    this.camera = { x: 0, y: 0 };
    this.visual = new Map();
    this.lastFrame = performance.now();
    this.resizeObserver = new ResizeObserver(() => this.resize());
    this.resizeObserver.observe(canvas);
    this.resize();
  }

  resize() {
    const rect = this.canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    this.width = rect.width; this.height = rect.height;
    this.dpr = Math.min(2, window.devicePixelRatio || 1);
    this.canvas.width = Math.max(1, Math.round(this.width * this.dpr));
    this.canvas.height = Math.max(1, Math.round(this.height * this.dpr));
  }

  setWorld(world) { this.world = world; }

  screenToWorld(clientX, clientY) {
    const rect = this.canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return null;
    const sx = clientX - rect.left, sy = clientY - rect.top;
    return { x: (sx - this.offsetX) / this.scale, y: (sy - this.offsetY) / this.scale };
  }

  render(localUid) {
    const ctx = this.ctx, w = this.width, h = this.height, dpr = this.dpr;
    if (!ctx || !w || !h) return;
    const now = performance.now(), dt = Math.min(0.08, (now - this.lastFrame) / 1000 || 0.016);
    this.lastFrame = now;
    const world = this.world;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = "#080b10"; ctx.fillRect(0, 0, w, h);
    if (!world) return;
    const local = world.players?.[localUid] || Object.values(world.players || {})[0];
    const smoothLocal = local ? this.smooth("p:" + local.uid, local, dt) : null;
    this.updateCamera(smoothLocal || local);
    ctx.setTransform(dpr * this.scale, 0, 0, dpr * this.scale, dpr * this.offsetX, dpr * this.offsetY);
    this.drawMap(ctx, world);
    this.drawProps(ctx);
    this.drawWalls(ctx, world);
    this.drawDoors(ctx, world);
    this.drawMachines(ctx, world);
    this.drawWindowBoards(ctx, world);
    this.drawPowerups(ctx, world);
    this.drawZombies(ctx, world, dt);
    this.drawPlayers(ctx, world, dt);
    this.drawTraces(ctx, world);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.drawMiniMap(ctx, world, localUid);
    this.drawVignette(ctx);
  }

  updateCamera(player) {
    const w = this.width, h = this.height;
    const base = Math.min(w / 1220, h / 710);
    this.scale = clamp(base, 0.48, 0.83);
    const vw = w / this.scale, vh = h / this.scale;
    let cx = player?.x ?? 0, cy = player?.y ?? 0;
    const b = this.map.bounds;
    if (b.x1 - b.x0 <= vw) cx = (b.x0 + b.x1) / 2;
    else cx = clamp(cx, b.x0 + vw / 2, b.x1 - vw / 2);
    if (b.y1 - b.y0 <= vh) cy = (b.y0 + b.y1) / 2;
    else cy = clamp(cy, b.y0 + vh / 2, b.y1 - vh / 2);
    this.camera = { x: cx, y: cy };
    this.offsetX = w / 2 - cx * this.scale;
    this.offsetY = h / 2 - cy * this.scale;
  }

  smooth(key, entity, dt) {
    let p = this.visual.get(key);
    if (!p) { p = { x: entity.x, y: entity.y, angle: entity.angle || 0 }; this.visual.set(key, p); }
    const t = 1 - Math.exp(-dt * 18);
    p.x = lerp(p.x, Number(entity.x) || 0, t);
    p.y = lerp(p.y, Number(entity.y) || 0, t);
    if (Number.isFinite(entity.angle)) p.angle = angLerp(p.angle, entity.angle, t);
    return { ...entity, x: p.x, y: p.y, angle: p.angle };
  }

  drawMap(ctx, world) {
    const bg = ctx.createLinearGradient(this.map.bounds.x0, this.map.bounds.y0, this.map.bounds.x1, this.map.bounds.y1);
    bg.addColorStop(0, "#11151a"); bg.addColorStop(1, "#07090d");
    ctx.fillStyle = bg; ctx.fillRect(this.map.bounds.x0, this.map.bounds.y0, this.map.bounds.x1 - this.map.bounds.x0, this.map.bounds.y1 - this.map.bounds.y0);
    for (const room of this.map.rooms) {
      const palette = FLOOR[room.floorMaterial] || FLOOR.concrete;
      ctx.fillStyle = palette[1]; ctx.fillRect(room.x0, room.y0, room.x1 - room.x0, room.y1 - room.y0);
      const grad = ctx.createLinearGradient(room.x0, room.y0, room.x1, room.y1);
      grad.addColorStop(0, palette[0] + "8c"); grad.addColorStop(1, palette[1] + "10");
      ctx.fillStyle = grad; ctx.fillRect(room.x0, room.y0, room.x1 - room.x0, room.y1 - room.y0);
      ctx.save(); ctx.beginPath(); ctx.rect(room.x0, room.y0, room.x1 - room.x0, room.y1 - room.y0); ctx.clip();
      ctx.strokeStyle = "rgba(225,218,196,.045)"; ctx.lineWidth = 1;
      for (let x = Math.floor(room.x0 / 80) * 80; x < room.x1; x += 80) { ctx.beginPath(); ctx.moveTo(x, room.y0); ctx.lineTo(x, room.y1); ctx.stroke(); }
      for (let y = Math.floor(room.y0 / 80) * 80; y < room.y1; y += 80) { ctx.beginPath(); ctx.moveTo(room.x0, y); ctx.lineTo(room.x1, y); ctx.stroke(); }
      ctx.restore();
      ctx.strokeStyle = "rgba(207,194,166,.15)"; ctx.lineWidth = 5;
      ctx.strokeRect(room.x0, room.y0, room.x1 - room.x0, room.y1 - room.y0);
      const name = room.label || room.name.replaceAll("_", " ");
      ctx.save(); ctx.globalAlpha = 0.35; ctx.fillStyle = "#d4c8b5"; ctx.font = "600 24px Inter, sans-serif";
      ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(name.toUpperCase(), room.center.x, room.center.y - 185); ctx.restore();
      if (room.start) {
        const glow = ctx.createRadialGradient(room.center.x, room.center.y, 20, room.center.x, room.center.y, 280);
        glow.addColorStop(0, "rgba(195,135,79,.13)"); glow.addColorStop(1, "rgba(195,135,79,0)");
        ctx.fillStyle = glow; ctx.fillRect(room.x0, room.y0, room.x1 - room.x0, room.y1 - room.y0);
      }
    }
    // Sinaliza o caminho de saída da sala inicial sem marcar todos os caminhos.
    for (const door of this.map.doors) {
      const unlocked = !!world.unlocked?.[door.id];
      if (unlocked) {
        ctx.save(); ctx.strokeStyle = "rgba(129,225,187,.34)"; ctx.lineWidth = 4;
        ctx.beginPath(); ctx.arc(door.center.x, door.center.y, 45, 0, Math.PI * 2); ctx.stroke(); ctx.restore();
      }
    }
  }

  drawProps(ctx) {
    for (const p of this.map.props) {
      const colors = MATERIAL[p.material] || MATERIAL.crate;
      const ww = p.x1 - p.x0, hh = p.y1 - p.y0;
      ctx.save();
      ctx.fillStyle = "rgba(0,0,0,.44)"; ctx.fillRect(p.x0 + 16, p.y0 + 18, ww, hh);
      const grad = ctx.createLinearGradient(p.x0, p.y0, p.x1, p.y1);
      grad.addColorStop(0, colors[0]); grad.addColorStop(1, colors[1]);
      ctx.fillStyle = grad; ctx.fillRect(p.x0, p.y0, ww, hh);
      ctx.strokeStyle = "rgba(230,217,190,.27)"; ctx.lineWidth = 5; ctx.strokeRect(p.x0, p.y0, ww, hh);
      if (["wood", "crate", "seat", "rubble"].includes(p.material)) {
        ctx.strokeStyle = "rgba(20,15,13,.48)"; ctx.lineWidth = 3;
        if (ww > hh) { ctx.beginPath(); ctx.moveTo(p.x0, p.y0 + hh * .42); ctx.lineTo(p.x1, p.y0 + hh * .42); ctx.stroke(); }
        else { ctx.beginPath(); ctx.moveTo(p.x0 + ww * .5, p.y0); ctx.lineTo(p.x0 + ww * .5, p.y1); ctx.stroke(); }
      }
      if (p.material === "metal") {
        ctx.fillStyle = "rgba(224,233,226,.19)"; ctx.fillRect(p.x0 + 12, p.y0 + 12, Math.max(8, ww * .11), Math.max(6, hh * .08));
      }
      ctx.restore();
    }
  }

  drawWalls(ctx, world) {
    for (const c of this.map.wallSegments) {
      if (c.kind === "window" && (world.windows?.[c.windowId] ?? 6) === 0) {
        ctx.fillStyle = "rgba(7,9,12,.78)"; ctx.fillRect(c.x0, c.y0, c.x1 - c.x0, c.y1 - c.y0);
        continue;
      }
      const grad = ctx.createLinearGradient(c.x0, c.y0, c.x1, c.y1);
      grad.addColorStop(0, c.kind === "window" ? "#674a36" : "#3d4444");
      grad.addColorStop(1, c.kind === "window" ? "#2e2724" : "#191f20");
      ctx.fillStyle = grad; ctx.fillRect(c.x0, c.y0, c.x1 - c.x0, c.y1 - c.y0);
      ctx.strokeStyle = "rgba(224,213,186,.18)"; ctx.lineWidth = 3; ctx.strokeRect(c.x0, c.y0, c.x1 - c.x0, c.y1 - c.y0);
    }
  }

  drawDoors(ctx, world) {
    for (const d of this.map.doors) {
      const unlocked = !!world.unlocked?.[d.id];
      const ww = d.x1 - d.x0, hh = d.y1 - d.y0;
      if (unlocked) {
        ctx.save(); ctx.fillStyle = "rgba(111,218,177,.13)"; ctx.fillRect(d.x0, d.y0, ww, hh);
        ctx.strokeStyle = "rgba(135,242,196,.4)"; ctx.lineWidth = 3; ctx.strokeRect(d.x0 + 4, d.y0 + 4, ww - 8, hh - 8); ctx.restore();
        continue;
      }
      const electric = d.power;
      const g = ctx.createLinearGradient(d.x0, d.y0, d.x1, d.y1);
      g.addColorStop(0, electric ? "#52656a" : d.kind === "debris" ? "#63574b" : "#775236");
      g.addColorStop(1, "#262625");
      ctx.fillStyle = g; ctx.fillRect(d.x0 + 3, d.y0 + 3, ww - 6, hh - 6);
      ctx.strokeStyle = electric ? "rgba(113,207,221,.55)" : "rgba(223,177,102,.55)"; ctx.lineWidth = 4;
      ctx.strokeRect(d.x0 + 4, d.y0 + 4, ww - 8, hh - 8);
      if (ww < hh) {
        for (let y = d.y0 + 16; y < d.y1 - 8; y += 24) { ctx.strokeStyle = "rgba(10,12,13,.7)"; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(d.x0 + 7, y); ctx.lineTo(d.x1 - 7, y + 6); ctx.stroke(); }
      } else {
        for (let x = d.x0 + 16; x < d.x1 - 8; x += 24) { ctx.strokeStyle = "rgba(10,12,13,.7)"; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(x, d.y0 + 7); ctx.lineTo(x + 6, d.y1 - 7); ctx.stroke(); }
      }
      const text = d.power && !world.power ? "⚡" : String(d.cost || 0);
      ctx.save(); ctx.font = "900 19px Inter, sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.fillStyle = "#f5d58e"; ctx.shadowColor = "#17100a"; ctx.shadowBlur = 6; ctx.fillText(text, d.center.x, d.center.y); ctx.restore();
    }
  }

  drawMachines(ctx, world) {
    for (const w of this.map.wallbuys) {
      const spec = getWeapon(w.weapon); this.drawBuyIcon(ctx, w.x, w.y, spec?.kind === "shotgun" ? "SHOT" : "ARM", "#d1b873", spec?.name || "ARMA");
    }
    for (const p of this.map.perks) {
      const perk = PERKS[p.perk]; if (!perk) continue;
      const owned = Object.values(world.players || {}).some((player) => player.perks?.includes(p.perk));
      this.drawPerk(ctx, p.x, p.y, perk, owned);
    }
    for (let i = 0; i < this.map.boxes.length; i++) {
      const b = this.map.boxes[i], active = i === (world.activeBox || 0);
      this.drawBox(ctx, b.x, b.y, active, !!world.boxBusy);
    }
    for (const p of this.map.pap) {
      this.drawBuyIcon(ctx, p.x, p.y, "PAP", world.power ? "#dc82ff" : "#53606a", "PACK-A-PUNCH");
    }
    for (const s of this.map.switches) {
      ctx.save();
      const glow = ctx.createRadialGradient(s.x, s.y, 3, s.x, s.y, 95);
      glow.addColorStop(0, world.power ? "rgba(107,239,179,.34)" : "rgba(244,177,70,.16)"); glow.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(s.x, s.y, 95, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#3b4445"; ctx.fillRect(s.x - 24, s.y - 36, 48, 72);
      ctx.strokeStyle = world.power ? "#78efb5" : "#d4a35d"; ctx.lineWidth = 5; ctx.strokeRect(s.x - 24, s.y - 36, 48, 72);
      ctx.strokeStyle = world.power ? "#87ffbf" : "#ffbe59"; ctx.lineWidth = 8;
      ctx.beginPath(); ctx.moveTo(s.x, s.y + 14); ctx.lineTo(s.x + (world.power ? 14 : -12), s.y + (world.power ? -18 : -8)); ctx.stroke();
      ctx.fillStyle = "#e8d19c"; ctx.font = "700 16px Inter"; ctx.textAlign = "center"; ctx.fillText(world.power ? "ENERGIA" : "POWER", s.x, s.y + 57);
      ctx.restore();
    }
  }

  drawBuyIcon(ctx, x, y, short, color, label) {
    ctx.save();
    ctx.fillStyle = "rgba(0,0,0,.42)"; ctx.beginPath(); ctx.ellipse(x + 8, y + 22, 38, 20, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#283033"; ctx.fillRect(x - 28, y - 24, 56, 48);
    const g = ctx.createLinearGradient(x - 26, y - 24, x + 26, y + 22); g.addColorStop(0, color); g.addColorStop(1, "#202626");
    ctx.fillStyle = g; ctx.fillRect(x - 22, y - 19, 44, 37);
    ctx.strokeStyle = "rgba(227,234,225,.45)"; ctx.lineWidth = 3; ctx.strokeRect(x - 22, y - 19, 44, 37);
    ctx.fillStyle = "#111518"; ctx.font = "900 14px Inter"; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(short, x, y - 1);
    ctx.fillStyle = "#cabd9f"; ctx.font = "700 12px Inter"; ctx.fillText(label.toUpperCase().slice(0, 19), x, y + 42);
    ctx.restore();
  }

  drawPerk(ctx, x, y, perk, owned) {
    ctx.save();
    const glow = ctx.createRadialGradient(x, y, 8, x, y, 105);
    glow.addColorStop(0, perk.color + (owned ? "33" : "17")); glow.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(x, y, 105, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#252c2c"; ctx.beginPath(); ctx.roundRect(x - 33, y - 32, 66, 64, 8); ctx.fill();
    ctx.fillStyle = owned ? "#40504a" : "#3b3e39"; ctx.fillRect(x - 25, y - 24, 50, 22);
    ctx.fillStyle = perk.color; ctx.globalAlpha = owned ? 0.52 : 1; ctx.font = "900 15px Inter"; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(perk.short, x, y - 13);
    ctx.globalAlpha = 1; ctx.fillStyle = "#111618"; ctx.fillRect(x - 24, y + 4, 48, 15);
    ctx.fillStyle = "#d7cba9"; ctx.font = "700 11px Inter"; ctx.fillText(perk.name.toUpperCase().replace(" ROOT BEER", ""), x, y + 12);
    ctx.fillStyle = "#7e725e"; ctx.fillRect(x - 23, y + 21, 46, 8);
    ctx.fillStyle = "#d1a762"; ctx.font = "800 13px Inter"; ctx.fillText(String(perk.cost || perk.costCoop), x, y + 43);
    ctx.restore();
  }

  drawBox(ctx, x, y, active, busy) {
    ctx.save();
    const glow = ctx.createRadialGradient(x, y, 10, x, y, active ? 130 : 75);
    glow.addColorStop(0, active ? (busy ? "rgba(178,130,255,.34)" : "rgba(255,198,67,.28)") : "rgba(75,77,84,.08)"); glow.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(x, y, active ? 130 : 75, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = active ? "#725333" : "#3b3935"; ctx.fillRect(x - 48, y - 30, 96, 61);
    ctx.strokeStyle = active ? "#e1b75d" : "#6c675d"; ctx.lineWidth = 5; ctx.strokeRect(x - 48, y - 30, 96, 61);
    ctx.fillStyle = active ? "#b99754" : "#686153"; ctx.fillRect(x - 40, y - 24, 80, 10);
    ctx.strokeStyle = "rgba(24,22,18,.75)"; ctx.lineWidth = 4;
    for (let i = -1; i <= 1; i++) { ctx.beginPath(); ctx.moveTo(x + i * 25, y - 18); ctx.lineTo(x + i * 25, y + 26); ctx.stroke(); }
    ctx.fillStyle = active ? "#f5d177" : "#969081"; ctx.font = "900 15px Inter"; ctx.textAlign = "center"; ctx.fillText(active ? (busy ? "? ? ?" : "MYSTERY BOX") : "MYSTERY BOX", x, y + 48);
    ctx.restore();
  }

  drawWindowBoards(ctx, world) {
    for (const win of this.map.windows) {
      const boards = clamp(Number(world.windows?.[win.id] ?? 6), 0, 6);
      if (!boards) {
        ctx.save(); ctx.strokeStyle = "rgba(242,139,82,.43)"; ctx.lineWidth = 4;
        ctx.beginPath(); ctx.arc(win.x, win.y, 28, 0, Math.PI * 2); ctx.stroke(); ctx.restore();
        continue;
      }
      ctx.save();
      const horizontal = win.vertical;
      const color = ["#76543c", "#815d40", "#69462f", "#8a6340", "#60412e", "#76543c"];
      for (let i = 0; i < boards; i++) {
        const t = (i - (boards - 1) / 2) * 18;
        ctx.save(); ctx.translate(win.x, win.y); ctx.rotate(horizontal ? Math.PI / 2 : 0);
        ctx.fillStyle = color[i]; ctx.fillRect(-57, t - 6, 114, 13);
        ctx.strokeStyle = "rgba(26,17,13,.8)"; ctx.lineWidth = 2; ctx.strokeRect(-57, t - 6, 114, 13);
        ctx.fillStyle = "#c2a27a"; ctx.beginPath(); ctx.arc(-48, t, 2.5, 0, Math.PI * 2); ctx.arc(48, t, 2.5, 0, Math.PI * 2); ctx.fill();
        ctx.restore();
      }
      ctx.fillStyle = "#e0bd7e"; ctx.font = "800 14px Inter"; ctx.textAlign = "center"; ctx.fillText(`${boards}/6`, win.x, win.y - 54);
      ctx.restore();
    }
  }

  drawPowerups(ctx, world) {
    const icons = { maxammo: "M", instakill: "×1", doublepoints: "2×", nuke: "☢", carpenter: "⌂" };
    for (const p of world.powerups || []) {
      const pulse = 1 + Math.sin((world.time || 0) * 6) * 0.08;
      ctx.save(); ctx.translate(p.x, p.y); ctx.scale(pulse, pulse);
      const g = ctx.createRadialGradient(0, 0, 2, 0, 0, 52); g.addColorStop(0, p.color + "aa"); g.addColorStop(1, p.color + "00");
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, 52, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = p.color; ctx.beginPath(); ctx.arc(0, 0, 23, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = "#fff5d8"; ctx.lineWidth = 3; ctx.stroke();
      ctx.fillStyle = "#111"; ctx.font = "900 15px Inter"; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(icons[p.type] || "?", 0, 0);
      ctx.restore();
    }
  }

  drawZombies(ctx, world, dt) {
    const living = new Set();
    for (const source of world.zombies || []) {
      if (!source.alive) continue;
      living.add("z:" + source.id);
      const z = this.smooth("z:" + source.id, source, dt);
      const r = z.radius || 15;
      ctx.save(); ctx.translate(z.x, z.y); ctx.rotate(z.angle || 0);
      ctx.fillStyle = "rgba(0,0,0,.48)"; ctx.beginPath(); ctx.ellipse(5, r * .65, r * 1.25, r * .65, 0, 0, Math.PI * 2); ctx.fill();
      // Braços avançados e corpo em silhueta verde-cinza.
      ctx.strokeStyle = z.flash > 0 ? "#f0d6c2" : "#526053"; ctx.lineWidth = 7; ctx.lineCap = "round";
      ctx.beginPath(); ctx.moveTo(3, 0); ctx.lineTo(r + 14, -r * .74); ctx.moveTo(4, 2); ctx.lineTo(r + 16, r * .78); ctx.stroke();
      ctx.fillStyle = z.flash > 0 ? "#e7d6c7" : z.color || "#8c9a7d";
      ctx.beginPath(); ctx.ellipse(0, 2, r * .82, r * 1.05, 0, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = z.flash > 0 ? "#efe0cf" : (z.dog ? "#2b2a2d" : "#89927e");
      ctx.beginPath(); ctx.arc(r * .58, 0, r * .63, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#e6483f"; ctx.beginPath(); ctx.arc(r * .8, -r * .26, 2.2, 0, Math.PI * 2); ctx.arc(r * .8, r * .23, 2.2, 0, Math.PI * 2); ctx.fill();
      if (z.dog) { ctx.fillStyle = "#b64937"; ctx.beginPath(); ctx.moveTo(r + 5, 0); ctx.lineTo(r + 20, -5); ctx.lineTo(r + 20, 5); ctx.fill(); }
      ctx.restore();
      if (z.hp < z.maxHp) {
        const width = 38;
        ctx.fillStyle = "rgba(0,0,0,.7)"; ctx.fillRect(z.x - width / 2, z.y - r - 20, width, 5);
        ctx.fillStyle = "#cd554b"; ctx.fillRect(z.x - width / 2, z.y - r - 20, width * clamp(z.hp / z.maxHp, 0, 1), 5);
      }
    }
    this.pruneVisual(living, "z:");
  }

  drawPlayers(ctx, world, dt) {
    const living = new Set();
    for (const source of Object.values(world.players || {})) {
      living.add("p:" + source.uid);
      const p = this.smooth("p:" + source.uid, source, dt);
      if (!source.alive) {
        ctx.save(); ctx.globalAlpha = .24; ctx.fillStyle = source.color; ctx.beginPath(); ctx.arc(p.x, p.y, 17, 0, Math.PI * 2); ctx.fill(); ctx.restore();
        continue;
      }
      ctx.save(); ctx.translate(p.x, p.y);
      if (p.downed) { ctx.globalAlpha = .7; const pulse = 1 + Math.sin(performance.now() / 100) * .09; ctx.scale(pulse, pulse); }
      ctx.fillStyle = "rgba(0,0,0,.42)"; ctx.beginPath(); ctx.ellipse(1, 8, 24, 15, 0, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = source.color || "#7ec8ff"; ctx.beginPath(); ctx.arc(0, 0, 18, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = "#f4ebd0"; ctx.lineWidth = 3; ctx.stroke();
      ctx.rotate(p.angle || 0);
      ctx.fillStyle = "#202629"; ctx.fillRect(1, -5, 27, 10);
      ctx.fillStyle = "#9ba7a2"; ctx.fillRect(16, -2, 19, 4);
      ctx.fillStyle = "#e6d6b7"; ctx.fillRect(30, -2, 7, 4);
      ctx.restore();
      const nameY = p.y - 30;
      ctx.save(); ctx.font = "700 16px Inter, sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "bottom";
      ctx.fillStyle = "rgba(0,0,0,.65)"; ctx.fillText(source.downed ? "ABATIDO" : source.name, p.x + 1, nameY + 1);
      ctx.fillStyle = source.downed ? "#ff7e83" : source.color; ctx.fillText(source.downed ? "ABATIDO" : source.name, p.x, nameY);
      if (source.downed) {
        const progress = clamp(1 - source.downTimer / 32, 0, 1);
        ctx.fillStyle = "rgba(30,10,13,.8)"; ctx.fillRect(p.x - 20, p.y - 43, 40, 5);
        ctx.fillStyle = "#ef6374"; ctx.fillRect(p.x - 20, p.y - 43, 40 * progress, 5);
      }
      ctx.restore();
    }
    this.pruneVisual(living, "p:");
  }

  drawTraces(ctx, world) {
    for (const shot of world.traces || []) {
      const alpha = clamp((shot.until - world.time) / 0.11, 0, 1);
      ctx.save(); ctx.globalAlpha = alpha * .72; ctx.strokeStyle = shot.color || "#ffe5a5"; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.moveTo(shot.x, shot.y); ctx.lineTo(shot.x + Math.cos(shot.angle) * 195, shot.y + Math.sin(shot.angle) * 195); ctx.stroke(); ctx.restore();
    }
  }

  drawMiniMap(ctx, world, localUid) {
    const mobile = this.width < 650;
    const boxW = mobile ? 118 : 190, boxH = mobile ? 92 : 142;
    const x = this.width - boxW - 17, y = 64;
    const b = this.map.bounds, pad = 8;
    const scale = Math.min((boxW - pad * 2) / (b.x1 - b.x0), (boxH - pad * 2) / (b.y1 - b.y0));
    const ox = x + (boxW - (b.x1 - b.x0) * scale) / 2 - b.x0 * scale;
    const oy = y + (boxH - (b.y1 - b.y0) * scale) / 2 - b.y0 * scale;
    ctx.save();
    ctx.fillStyle = "rgba(7,10,13,.76)"; ctx.strokeStyle = "rgba(218,194,139,.32)"; ctx.lineWidth = 1.2;
    ctx.beginPath(); ctx.roundRect(x, y, boxW, boxH, 10); ctx.fill(); ctx.stroke();
    ctx.save(); ctx.beginPath(); ctx.roundRect(x + pad, y + pad, boxW - pad * 2, boxH - pad * 2, 4); ctx.clip();
    for (const room of this.map.rooms) {
      ctx.fillStyle = "rgba(128,136,139,.22)"; ctx.fillRect(ox + room.x0 * scale, oy + room.y0 * scale, (room.x1 - room.x0) * scale, (room.y1 - room.y0) * scale);
      ctx.strokeStyle = "rgba(230,220,193,.28)"; ctx.lineWidth = 1; ctx.strokeRect(ox + room.x0 * scale, oy + room.y0 * scale, (room.x1 - room.x0) * scale, (room.y1 - room.y0) * scale);
    }
    for (const d of this.map.doors) {
      ctx.fillStyle = world.unlocked?.[d.id] ? "#78dda9" : "#b77d56";
      ctx.beginPath(); ctx.arc(ox + d.center.x * scale, oy + d.center.y * scale, 2.4, 0, Math.PI * 2); ctx.fill();
    }
    for (const z of world.zombies || []) { if (!z.alive) continue; ctx.fillStyle = z.dog ? "#ff924f" : "#f1645d"; ctx.beginPath(); ctx.arc(ox + z.x * scale, oy + z.y * scale, 2.2, 0, Math.PI * 2); ctx.fill(); }
    for (const p of Object.values(world.players || {})) {
      if (!p.alive) continue; ctx.fillStyle = p.color; ctx.beginPath(); ctx.arc(ox + p.x * scale, oy + p.y * scale, p.uid === localUid ? 4 : 3, 0, Math.PI * 2); ctx.fill();
    }
    ctx.restore();
    ctx.fillStyle = "rgba(236,222,189,.68)"; ctx.font = "700 8px Inter, sans-serif"; ctx.textAlign = "left"; ctx.fillText("KINO • TACTICAL MAP", x + 9, y + boxH - 5);
    ctx.restore();
  }

  drawVignette(ctx) {
    const g = ctx.createRadialGradient(this.width * .5, this.height * .48, Math.min(this.width, this.height) * .25, this.width * .5, this.height * .48, Math.max(this.width, this.height) * .7);
    g.addColorStop(0, "rgba(0,0,0,0)"); g.addColorStop(1, "rgba(0,0,0,.38)");
    ctx.fillStyle = g; ctx.fillRect(0, 0, this.width, this.height);
  }

  pruneVisual(keep, prefix) {
    for (const key of this.visual.keys()) if (key.startsWith(prefix) && !keep.has(key)) this.visual.delete(key);
  }

  destroy() { this.resizeObserver?.disconnect(); }
}
