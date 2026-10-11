// ============================================================
//  ZOMBIES: co-op browser simulation (host-authoritative)
//  World units correspond to the inches used by BO1/mapkit JSON.
// ============================================================
import { getWeapon, START_WEAPON, PERKS, ZOMBIE, DOG, SCORE, COST, rollBox } from "./bo1data.js";
import { clamp, dist, dist2, angleTo, makeRng, resolveCircleRect } from "./util.js";
import { roomAt, roomGraphPath, accessibleRooms, moveWithCollision, windowPosition } from "./map.js";

const PLAYER_RADIUS = 19;
const INTERACT_RADIUS = 142;
const DOWN_TIME = 32;
const RELOAD_FAST = 0.55;

function freshGun(id) {
  const spec = getWeapon(id);
  return spec ? { id, clip: spec.mag === Infinity ? 0 : spec.mag, reserve: spec.res === Infinity ? 0 : spec.res } : null;
}

function slotsFor(player) {
  const slots = ["primary", "secondary"];
  if (player.perks?.includes("specialty_twoprimaries")) slots.push("tertiary");
  return slots;
}

function playerGun(player) { return player.weapons?.[player.selected] || null; }

function perkCost(id, coop) {
  const perk = PERKS[id];
  if (!perk) return 0;
  return perk.costSolo ? (coop ? perk.costCoop : perk.costSolo) : perk.cost;
}

function firstBlockingProp(map, world, x, y, radius) {
  for (const c of map.colliders) {
    if (c.kind !== "prop") continue;
    if (resolveCircleRect(x, y, radius, c)) return c;
  }
  return null;
}

function routeAroundProp(z, target, prop, radius) {
  const margin = radius + 19;
  const left = prop.x0 - margin, right = prop.x1 + margin;
  const top = prop.y0 - margin, bottom = prop.y1 + margin;
  const towardY = target.y > prop.y1 ? bottom : target.y < prop.y0 ? top : clamp(target.y, top, bottom);
  const towardX = target.x > prop.x1 ? right : target.x < prop.x0 ? left : clamp(target.x, left, right);
  const crossesVertical = (z.y < prop.y0 && target.y > prop.y1) || (z.y > prop.y1 && target.y < prop.y0);
  const crossesHorizontal = (z.x < prop.x0 && target.x > prop.x1) || (z.x > prop.x1 && target.x < prop.x0);
  const options = [
    { side: "left", axis: "vertical", points: [{ x: left, y: z.y }, { x: left, y: towardY }] },
    { side: "right", axis: "vertical", points: [{ x: right, y: z.y }, { x: right, y: towardY }] },
    { side: "top", axis: "horizontal", points: [{ x: z.x, y: top }, { x: towardX, y: top }] },
    { side: "bottom", axis: "horizontal", points: [{ x: z.x, y: bottom }, { x: towardX, y: bottom }] }
  ].filter((option) => crossesVertical ? option.axis === "vertical" : crossesHorizontal ? option.axis === "horizontal" : true);
  for (const option of options) {
    const [a, b] = option.points;
    option.cost = dist(z.x, z.y, a.x, a.y) + dist(a.x, a.y, b.x, b.y) + dist(b.x, b.y, target.x, target.y);
  }
  options.sort((a, b) => a.cost - b.cost);
  return options[0].points;
}

function makePlayer(info, spawn, index) {
  return {
    uid: String(info.uid),
    name: String(info.name || `Jogador ${index + 1}`).slice(0, 18),
    color: String(info.color || ["#7ec8ff", "#ffcf5c", "#7dffa8", "#ff7d9c"][index % 4]),
    x: spawn.x + (index % 2 ? 26 : -26), y: spawn.y + (index > 1 ? 26 : -26), angle: spawn.yaw * Math.PI / 180,
    score: SCORE.START, kills: 0, downs: 0, revives: 0,
    hp: 100, maxHp: 100, alive: true, downed: false, downTimer: 0, reviveProgress: 0,
    perks: [], weapons: { primary: freshGun(START_WEAPON), secondary: null, tertiary: null }, selected: "primary",
    reloading: 0, fireCooldown: 0, meleeCooldown: 0, hurtFlash: 0, invuln: 0,
    quickRevives: 0, quickReviveUsed: false,
    lastHit: 0, moveX: 0, moveY: 0,
    connected: true
  };
}

export class Simulation {
  constructor(map, roster, seed = (Date.now() ^ Math.floor(Math.random() * 0xffffffff)) >>> 0) {
    this.map = map;
    this.rng = makeRng(seed);
    this.seed = seed >>> 0;
    this.commandSeen = {};
    this.counter = { zombie: 0, powerup: 0, event: 0 };
    const spawnList = map.spawns.length ? map.spawns : [{ x: 0, y: 0, yaw: 0, room: "palco" }];
    const players = {};
    roster.slice(0, 4).forEach((info, i) => {
      const spawn = spawnList[i % spawnList.length];
      players[String(info.uid)] = makePlayer(info, spawn, i);
      this.commandSeen[String(info.uid)] = { interact: 0, reload: 0, melee: 0, swap: 0 };
    });
    const unlocked = {};
    const doorDamage = {};
    for (const d of map.doors) { unlocked[d.id] = d.cost === 0 && !d.power; doorDamage[d.id] = 0; }
    const windows = {};
    for (const w of map.windows) windows[w.id] = 6;
    const firstDog = 10 + this.rng.int(6);
    this.world = {
      schema: 3,
      status: "playing",
      seed: this.seed,
      time: 0,
      round: 0,
      roundTotal: 0,
      roundKilled: 0,
      spawnLeft: 0,
      spawnTimer: 0,
      roundDelay: 0,
      dogRound: false,
      firstDogRound: firstDog,
      nextDogRound: firstDog,
      power: false,
      unlocked,
      doorDamage,
      windows,
      activeBox: 0,
      boxUses: 0,
      boxCooldown: 0,
      boxBusy: null,
      effects: { instaUntil: 0, doubleUntil: 0, firesaleUntil: 0 },
      players,
      zombies: [],
      powerups: [],
      traces: [],
      notices: [],
      noticeKey: 0,
      waveStartedAt: 0,
      elapsed: 0
    };
    this.world.activeBox = this.rng.int(Math.max(1, map.boxes.length));
    if (this.world.players && Object.keys(this.world.players).length === 0) this.world.status = "waiting";
    this.addEvent("A noite começa. Sobrevivam juntos.", null, "#9eabbc");
    this.beginRound();
  }

  beginRound() {
    const w = this.world;
    if (w.status !== "playing") return;
    const living = Object.values(w.players).filter((p) => p.alive).length || 1;
    w.round += 1;
    w.dogRound = w.round === w.nextDogRound;
    if (w.dogRound) w.nextDogRound += 5;
    if (w.round % 3 === 0) {
      for (const p of Object.values(w.players)) if (p.perks.includes("specialty_quickrevive")) p.quickRevives = 1;
    }
    w.roundTotal = w.dogRound ? Math.max(6, 6 + living * 2) : ZOMBIE.total(w.round, living);
    w.roundKilled = 0;
    w.spawnLeft = w.roundTotal;
    w.spawnTimer = 1.2;
    w.roundDelay = 0;
    w.waveStartedAt = w.time;
    this.addEvent(w.dogRound ? `RODADA ${w.round} • CÃES DO INFERNO` : `RODADA ${w.round}`, null, w.dogRound ? "#ff6b3d" : "#f3cf72");
  }

  step(dt, inputs = {}, localUid = null) {
    const w = this.world;
    if (w.status !== "playing") return w;
    dt = clamp(dt, 0, 0.05);
    w.time += dt;
    w.elapsed += dt;
    w.traces = w.traces.filter((t) => t.until > w.time);
    w.notices = w.notices.filter((n) => n.until > w.time);
    w.effects.instaUntil = Math.max(w.time, Number(w.effects.instaUntil || 0));
    w.effects.doubleUntil = Math.max(w.time, Number(w.effects.doubleUntil || 0));
    w.effects.firesaleUntil = Math.max(w.time, Number(w.effects.firesaleUntil || 0));
    w.boxCooldown = Math.max(0, w.boxCooldown - dt);
    if (w.boxBusy && w.boxBusy.until <= w.time) this.resolveBox();

    const inputByUid = {};
    for (const p of Object.values(w.players)) {
      inputByUid[p.uid] = this.getInput(p, inputs[p.uid], p.uid === localUid ? inputs.__local : null);
    }
    for (const p of Object.values(w.players)) this.updatePlayer(p, inputByUid[p.uid], dt, inputByUid);
    this.updateZombies(dt);
    this.updatePowerups(dt);
    this.updateSpawning(dt);
    this.checkRound(dt);
    this.checkGameOver();
    return w;
  }

  getInput(player, remote, local) {
    const raw = local || remote;
    if (!raw || (raw.at && Date.now() - Number(raw.at) > 1800)) {
      return { x: 0, y: 0, aim: player.angle || 0, fire: false, sprint: false, interactHeld: false, slot: player.selected, seq: {} };
    }
    return {
      x: clamp(Number(raw.x) || 0, -1, 1), y: clamp(Number(raw.y) || 0, -1, 1),
      aim: Number.isFinite(Number(raw.aim)) ? Number(raw.aim) : (player.angle || 0),
      fire: !!raw.fire, sprint: !!raw.sprint, interactHeld: !!raw.interactHeld,
      slot: raw.slot || player.selected, seq: raw.seq || {}
    };
  }

  updatePlayer(p, input, dt, inputByUid) {
    if (!p.alive) return;
    p.angle = input.aim;
    p.fireCooldown = Math.max(0, p.fireCooldown - dt);
    p.meleeCooldown = Math.max(0, p.meleeCooldown - dt);
    p.hurtFlash = Math.max(0, p.hurtFlash - dt);
    p.invuln = Math.max(0, p.invuln - dt);
    p.reloading = Math.max(0, p.reloading - dt);
    if (p.reloading === 0 && p._reloadFinish) {
      const gun = playerGun(p), spec = gun && getWeapon(gun.id);
      if (gun && spec) {
        const want = Math.max(0, spec.mag - gun.clip);
        const take = Math.min(want, gun.reserve);
        gun.clip += take; gun.reserve -= take;
      }
      p._reloadFinish = false;
    }
    if (p.downed) {
      p.downTimer -= dt;
      p.moveX = 0; p.moveY = 0;
      this.updateRevive(p, inputByUid, dt);
      if (!p.downed) return;
      if (p.downTimer <= 0) {
        if (p.quickReviveUsed && p.perks.includes("specialty_quickrevive")) {
          p.downed = false; p.hp = Math.max(35, Math.round(p.maxHp * 0.4)); p.invuln = 2.5; p.downTimer = 0; p.quickReviveUsed = false;
          this.addEvent(`${p.name} voltou à luta • QUICK REVIVE`, p.uid, "#63d8ff");
        } else this.eliminate(p);
      }
      return;
    }

    const seq = input.seq || {};
    const seen = this.commandSeen[p.uid] || (this.commandSeen[p.uid] = { interact: 0, reload: 0, melee: 0, swap: 0 });
    if (Number(seq.reload || 0) !== seen.reload) { seen.reload = Number(seq.reload || 0); this.startReload(p); }
    if (Number(seq.swap || 0) !== seen.swap) {
      seen.swap = Number(seq.swap || 0);
      if (input.slot && slotsFor(p).includes(input.slot) && p.weapons[input.slot]) p.selected = input.slot;
    }
    if (Number(seq.melee || 0) !== seen.melee) { seen.melee = Number(seq.melee || 0); this.melee(p); }
    if (Number(seq.interact || 0) !== seen.interact) { seen.interact = Number(seq.interact || 0); this.interact(p); }

    let mx = input.x, my = input.y;
    const ml = Math.hypot(mx, my);
    if (ml > 1) { mx /= ml; my /= ml; }
    const moving = Math.hypot(mx, my) > 0.05;
    const speed = (input.sprint ? 275 : 220) * (p.perks.includes("specialty_longersprint") ? 1.23 : 1) * (getWeapon(playerGun(p)?.id)?.speed || 1);
    if (moving) {
      const next = moveWithCollision(this.map, this.world, p, mx * speed * dt, my * speed * dt, PLAYER_RADIUS, true);
      p.x = next.x; p.y = next.y;
    }
    p.moveX = mx; p.moveY = my;
    if (input.fire && p.fireCooldown <= 0 && !p.reloading) this.shoot(p);
  }

  startReload(p) {
    const gun = playerGun(p), spec = gun && getWeapon(gun.id);
    if (!gun || !spec || spec.melee || p.reloading || gun.clip >= spec.mag || gun.reserve <= 0) return;
    const fast = p.perks.includes("specialty_fastreload") ? RELOAD_FAST : 1;
    p.reloading = spec.reload * fast;
    p._reloadFinish = true;
    this.addNotice(p.uid, "RECARREGANDO", "#e7d6a1");
  }

  shoot(p) {
    const gun = playerGun(p), spec = gun && getWeapon(gun.id);
    if (!gun || !spec || spec.melee) return;
    if (gun.clip <= 0) { this.startReload(p); return; }
    gun.clip -= 1;
    const doubleTap = p.perks.includes("specialty_rof") ? 1.33 : 1;
    const insta = this.world.effects.instaUntil > this.world.time;
    p.fireCooldown = 60 / (spec.rpm * doubleTap);
    const spread = (spec.spread || 0) * Math.PI / 180;
    const pellets = Math.max(1, spec.pellets || 1);
    const range = spec.range || (spec.kind === "sniper" ? 1250 : 1000);
    let anyHit = false;
    this.world.traces.push({ id: `t${++this.counter.event}`, x: p.x, y: p.y, angle: p.angle, until: this.world.time + 0.11, color: spec.kind === "special" ? "#66d6ff" : "#ffdf9b" });

    if (spec.cone || spec.knockback) {
      const victims = this.world.zombies.filter((z) => z.alive && dist(p.x, p.y, z.x, z.y) <= (spec.coneRange || 850) && this.angleDiff(p.angle, angleTo(p.x, p.y, z.x, z.y)) < ((spec.cone || 30) * Math.PI / 180) / 2);
      for (const z of victims) {
        if (spec.freeze) { z.frozen = 2.8; z.hp = Math.max(1, z.hp); }
        else this.damageZombie(z, p, insta || spec.knockback ? z.hp + 1 : Math.max(220, ZOMBIE.health(this.world.round) * 1.2), false, "gun");
        if (spec.knockback && z.alive) { z.stunned = 1.5; }
      }
      anyHit = victims.length > 0;
    } else {
      for (let pellet = 0; pellet < pellets; pellet++) {
        const offset = (this.rng() - 0.5) * spread;
        const angle = p.angle + offset;
        let best = null, bestT = Infinity, head = false;
        const ex = p.x + Math.cos(angle) * range, ey = p.y + Math.sin(angle) * range;
        for (const z of this.world.zombies) {
          if (!z.alive) continue;
          const d = this.pointToSegment(z.x, z.y, p.x, p.y, ex, ey);
          if (d.dist <= (z.radius || 15) && d.t < bestT) {
            best = z; bestT = d.t;
            head = d.dist <= (z.radius || 15) * (p.perks.includes("specialty_bulletaccuracy") ? 0.42 : 0.3) && this.angleDiff(p.angle, angleTo(p.x, p.y, z.x, z.y)) < 0.08;
          }
        }
        if (!best) continue;
        anyHit = true;
        const hs = head ? (spec.hs || 1) * (p.perks.includes("specialty_bulletaccuracy") ? 1.7 : 1) : 1;
        const damage = insta ? best.hp + 10 : Math.round((spec.dmg || 0) * hs);
        if (spec.proj === "rocket" || spec.proj === "bolt") this.explosion(p, best.x, best.y, insta ? best.hp + 100 : Math.max(spec.splash || 0, damage), spec.splashRadius || 150);
        else this.damageZombie(best, p, damage, head, "gun");
      }
    }
    if (anyHit && spec.kind === "special") this.addNotice(p.uid, "ACERTO!", "#79dcff");
    if (gun.clip === 0 && gun.reserve > 0) this.addNotice(p.uid, "SEM MUNIÇÃO NO PENTE", "#ffc66d");
  }

  melee(p) {
    if (p.meleeCooldown > 0 || p.downed) return;
    p.meleeCooldown = 0.56;
    const range = p.perks.includes("specialty_bulletaccuracy") ? 105 : 96;
    let best = null, bestD = Infinity;
    for (const z of this.world.zombies) {
      if (!z.alive) continue;
      const d = dist(p.x, p.y, z.x, z.y);
      if (d < range && this.angleDiff(p.angle, angleTo(p.x, p.y, z.x, z.y)) < 0.9 && d < bestD) { best = z; bestD = d; }
    }
    if (best) this.damageZombie(best, p, this.world.effects.instaUntil > this.world.time ? best.hp + 1 : this.mapTimeKnifeDamage(p), true, "melee");
  }

  mapTimeKnifeDamage(p) {
    const round = this.world.round;
    const base = round <= 4 ? 150 : round <= 9 ? 100 : 50;
    return p.perks.includes("specialty_bulletaccuracy") ? Math.round(base * 1.15) : base;
  }

  explosion(owner, x, y, damage, radius) {
    for (const z of this.world.zombies) {
      if (!z.alive) continue;
      const d = dist(x, y, z.x, z.y);
      if (d > radius) continue;
      this.damageZombie(z, owner, Math.round(damage * (1 - d / (radius * 1.25))), false, "explosion");
    }
  }

  damageZombie(z, p, amount, headshot, source) {
    if (!z.alive) return;
    z.hp -= Math.max(1, amount);
    z.flash = 0.12;
    const mult = this.world.effects.doubleUntil > this.world.time ? 2 : 1;
    if (source === "gun") p.score += SCORE.BULLET_HIT * mult;
    if (z.hp > 0) return;
    z.hp = 0; z.alive = false; this.world.roundKilled += 1; p.kills += 1;
    const points = source === "melee" ? SCORE.MELEE_KILL : (headshot ? SCORE.HEADSHOT_KILL : SCORE.KILL);
    p.score += points * mult;
    this.addEvent(`${p.name} eliminou um ${z.dog ? "cão" : "zumbi"}${headshot ? " • HEADSHOT" : ""}`, p.uid, headshot ? "#ffd36f" : p.color);
    if (this.rng() < 0.035 && this.world.powerups.length < 3) this.dropPowerup(z.x, z.y);
  }

  updateZombies(dt) {
    const w = this.world;
    for (let i = w.zombies.length - 1; i >= 0; i--) {
      const z = w.zombies[i];
      if (!z.alive) { w.zombies.splice(i, 1); continue; }
      z.flash = Math.max(0, (z.flash || 0) - dt);
      z.attackCooldown = Math.max(0, (z.attackCooldown || 0) - dt);
      z.hitWindow = Math.max(0, (z.hitWindow || 0) - dt);
      z.stunned = Math.max(0, (z.stunned || 0) - dt);
      z.frozen = Math.max(0, (z.frozen || 0) - dt);
      if (z.stunned || z.frozen) continue;
      const targets = Object.values(w.players).filter((p) => p.alive);
      if (!targets.length) continue;
      targets.sort((a, b) => dist2(z.x, z.y, a.x, a.y) - dist2(z.x, z.y, b.x, b.y));
      const target = targets[0];
      const targetRoom = roomAt(this.map, target.x, target.y, 35);
      const speed = z.dog ? DOG.speed : (z.speed || ZOMBIE.speed(w.round));
      let moveTarget = { x: target.x, y: target.y };
      let banging = false;

      if (z.windowId) {
        const win = this.map.windows.find((q) => q.id === z.windowId);
        const boards = w.windows[z.windowId] ?? 0;
        if (win) {
          const room = this.map.byId.get(win.room);
          const insideRoom = room && z.x >= room.x0 && z.x <= room.x1 && z.y >= room.y0 && z.y <= room.y1;
          if (boards > 0) {
            moveTarget = { x: win.x, y: win.y };
            if (dist(z.x, z.y, win.x, win.y) < 82) {
              banging = true;
              z.hitWindow = (z.hitWindow || 0) - dt;
              if (z.hitWindow <= 0) {
                z.hitWindow = 0.82;
                w.windows[win.id] = Math.max(0, boards - 1);
                if (w.windows[win.id] === 0) this.addEvent("Uma janela foi arrombada", null, "#ff9b63");
              }
            }
          } else {
            moveTarget = win.inner;
            if (insideRoom) z.windowId = null;
          }
        } else z.windowId = null;
      }

      if (!z.windowId && targetRoom) {
        const zRoom = roomAt(this.map, z.x, z.y, 45);
        if (zRoom && zRoom.name !== targetRoom.name) {
          const route = roomGraphPath(this.map, w, zRoom.name, targetRoom.name, true);
          const nextDoor = route[0];
          if (nextDoor) {
            if (!w.unlocked[nextDoor.id]) {
              moveTarget = nextDoor.center;
              if (dist(z.x, z.y, nextDoor.center.x, nextDoor.center.y) < 62) {
                banging = true;
                z.hitWindow = (z.hitWindow || 0) - dt;
                if (z.hitWindow <= 0) {
                  z.hitWindow = 1.0;
                  w.doorDamage[nextDoor.id] = (w.doorDamage[nextDoor.id] || 0) + 1;
                  if (w.doorDamage[nextDoor.id] >= 7) {
                    w.unlocked[nextDoor.id] = true;
                    this.addEvent(`Zumbis derrubaram a barreira: ${nextDoor.name}`, null, "#ff956b");
                  }
                }
              }
            } else {
              let nextRoomName = nextDoor.from === zRoom.name ? nextDoor.to : nextDoor.from;
              const nextRoom = this.map.byId.get(nextRoomName);
              const c = nextRoom?.center || target;
              const dx = c.x - nextDoor.center.x, dy = c.y - nextDoor.center.y, len = Math.hypot(dx, dy) || 1;
              moveTarget = { x: nextDoor.center.x + dx / len * 100, y: nextDoor.center.y + dy / len * 100 };
              if (dist(z.x, z.y, moveTarget.x, moveTarget.y) < 58) moveTarget = { x: target.x, y: target.y };
            }
          }
        }
      }

      const dTarget = dist(z.x, z.y, target.x, target.y);
      if (!banging && !z.windowId && dTarget <= (z.dog ? DOG.attackRange : ZOMBIE.attackRange) + PLAYER_RADIUS) {
        if (z.attackCooldown <= 0) {
          z.attackCooldown = z.dog ? DOG.attackCooldown : ZOMBIE.attackCooldown;
          this.hurtPlayer(target, z.dog ? DOG.attackDamage : ZOMBIE.attackDamage);
        }
        continue;
      }
      if (banging) continue;
      if (z.detourUid && z.detourUid !== target.uid) z.detour = null;
      z.detourUid = target.uid;
      while (z.detour?.length && dist(z.x, z.y, z.detour[0].x, z.detour[0].y) < 23) z.detour.shift();
      if (z.detour?.length) moveTarget = z.detour[0];
      const a = angleTo(z.x, z.y, moveTarget.x, moveTarget.y);
      z.angle = a;
      const dx = Math.cos(a) * speed * dt, dy = Math.sin(a) * speed * dt;
      const next = moveWithCollision(this.map, w, z, dx, dy, z.radius || 15, false);
      const progress = (next.x - z.x) * Math.cos(a) + (next.y - z.y) * Math.sin(a);
      if (!z.detour?.length && progress < Math.hypot(dx, dy) * 0.42) {
        const blocker = firstBlockingProp(this.map, w, z.x + dx, z.y + dy, z.radius || 15);
        if (blocker) z.detour = routeAroundProp(z, target, blocker, z.radius || 15);
      }
      z.x = next.x; z.y = next.y;
    }
  }

  hurtPlayer(p, damage) {
    if (!p.alive || p.downed || p.invuln > 0) return;
    const actual = p.perks.includes("specialty_armorvest") ? Math.max(1, Math.round(damage * 0.42)) : damage;
    p.hp -= actual;
    p.hurtFlash = 0.35; p.invuln = 0.32; p.lastHit = this.world.time;
    this.addNotice(p.uid, "DANO RECEBIDO", "#ff6678");
    if (p.hp <= 0) this.downPlayer(p);
  }

  downPlayer(p) {
    p.hp = 0; p.downed = true; p.downTimer = DOWN_TIME; p.reviveProgress = 0; p.downs += 1;
    const solo = Object.values(this.world.players).filter((q) => q.alive).length <= 1;
    if (solo && p.perks.includes("specialty_quickrevive") && p.quickRevives > 0) {
      p.quickRevives -= 1; p.quickReviveUsed = true; p.downTimer = 1.8;
      this.addEvent(`${p.name} se autorreanimará • Quick Revive`, p.uid, "#63d8ff");
    } else this.addEvent(`${p.name} está abatido — reanime!`, p.uid, "#ff6678");
  }

  updateRevive(downed, inputByUid, dt) {
    const helper = Object.values(this.world.players).find((p) => p.alive && !p.downed && p.uid !== downed.uid && dist(p.x, p.y, downed.x, downed.y) < 92 && inputByUid[p.uid]?.interactHeld);
    if (helper) {
      downed.reviveProgress += dt * (helper.perks.includes("specialty_quickrevive") ? 1.65 : 1);
      if (downed.reviveProgress >= 3) {
        downed.downed = false; downed.hp = downed.maxHp * 0.4; downed.invuln = 2.5; downed.downTimer = 0;
        helper.revives += 1; helper.score += 200;
        this.addEvent(`${helper.name} reanimou ${downed.name}`, helper.uid, "#8effbb");
      }
    } else downed.reviveProgress = Math.max(0, downed.reviveProgress - dt * 0.65);
  }

  eliminate(p) {
    if (!p.alive) return;
    p.alive = false; p.downed = false; p.hp = 0;
    this.addEvent(`${p.name} foi eliminado`, p.uid, "#ff586f");
  }

  checkGameOver() {
    const players = Object.values(this.world.players);
    if (players.length && players.every((p) => !p.alive)) {
      this.world.status = "gameover";
      this.world.endedAt = this.world.time;
      this.addEvent(`FIM DE JOGO • RODADA ${this.world.round}`, null, "#ff586f");
    }
  }

  checkRound(dt) {
    const w = this.world;
    if (w.spawnLeft === 0 && w.zombies.length === 0) {
      w.roundDelay += dt;
      if (w.roundDelay > 4) this.beginRound();
    }
  }

  updateSpawning(dt) {
    const w = this.world;
    if (w.spawnLeft <= 0) return;
    const players = Object.values(w.players).filter((p) => p.alive);
    const cap = ZOMBIE.maxAlive(Math.max(1, players.length));
    if (w.zombies.length >= cap) return;
    w.spawnTimer -= dt;
    if (w.spawnTimer > 0) return;
    w.spawnTimer = w.dogRound ? 0.9 : Math.max(0.44, 1.65 - w.round * 0.055) + this.rng.range(0.1, 0.5);
    this.spawnZombie();
    w.spawnLeft -= 1;
  }

  spawnZombie() {
    const w = this.world;
    const startRoom = this.map.spawns[0]?.room || "palco";
    const accessible = accessibleRooms(this.map, w, startRoom);
    const spawnWindows = this.map.windows.filter((win) => accessible.has(win.room));
    let x, y, windowId = null;
    if (spawnWindows.length) {
      const win = this.rng.pick(spawnWindows);
      x = win.outer.x; y = win.outer.y; windowId = win.id;
    } else {
      const rooms = this.map.rooms.filter((r) => accessible.has(r.name));
      const r = this.rng.pick(rooms.length ? rooms : this.map.rooms);
      x = this.rng.range(r.x0 + 35, r.x1 - 35); y = this.rng.range(r.y0 + 35, r.y1 - 35);
    }
    const round = w.round;
    const dog = w.dogRound;
    const typeRoll = this.rng();
    let type = "normal", hpMul = 1, speedMul = 1, color = "#99a88c";
    if (dog) { type = "dog"; color = "#434348"; }
    else if (round >= 5 && typeRoll < 0.10) { type = "sprinter"; hpMul = 0.75; speedMul = 1.42; color = "#c09077"; }
    else if (round >= 7 && typeRoll > 0.94) { type = "armored"; hpMul = 1.55; speedMul = 0.88; color = "#8594a7"; }
    const baseHp = dog ? DOG.health(round) : ZOMBIE.health(round);
    const speed = dog ? DOG.speed : Math.min(ZOMBIE.maxSpeed, 100 + (round - 1) * 4.5) * speedMul;
    const z = {
      id: `z${++this.counter.zombie}`,
      x, y, angle: 0,
      hp: Math.round(baseHp * hpMul), maxHp: Math.round(baseHp * hpMul),
      alive: true, dog, type, color,
      speed, radius: dog ? DOG.RADIUS : ZOMBIE.RADIUS,
      attackCooldown: this.rng.range(0, 0.8), hitWindow: 0, hitFlash: 0, flash: 0, stunned: 0, frozen: 0,
      windowId
    };
    w.zombies.push(z);
  }

  updatePowerups(dt) {
    const w = this.world;
    for (let i = w.powerups.length - 1; i >= 0; i--) {
      const drop = w.powerups[i];
      drop.life -= dt;
      if (drop.life <= 0) { w.powerups.splice(i, 1); continue; }
      const player = Object.values(w.players).find((p) => p.alive && !p.downed && dist(p.x, p.y, drop.x, drop.y) < 38);
      if (!player) continue;
      this.collectPowerup(player, drop);
      w.powerups.splice(i, 1);
    }
  }

  dropPowerup(x, y) {
    const types = ["maxammo", "instakill", "doublepoints", "nuke", "carpenter"];
    const type = this.rng.pick(types);
    const colors = { maxammo: "#76e8ff", instakill: "#ff4c4c", doublepoints: "#ffd44e", nuke: "#fb973a", carpenter: "#65e69a" };
    this.world.powerups.push({ id: `p${++this.counter.powerup}`, type, x, y, color: colors[type], life: 18 });
  }

  collectPowerup(player, drop) {
    const w = this.world;
    switch (drop.type) {
      case "maxammo":
        for (const slot of Object.values(player.weapons)) {
          if (!slot) continue;
          const spec = getWeapon(slot.id);
          if (spec && spec.res !== Infinity) { slot.reserve = spec.res; slot.clip = spec.mag; }
        }
        this.addEvent(`${player.name} pegou MAX AMMO`, player.uid, "#76e8ff"); break;
      case "instakill": w.effects.instaUntil = w.time + 25; this.addEvent("INSTA-KILL", null, "#ff6868"); break;
      case "doublepoints": w.effects.doubleUntil = w.time + 30; this.addEvent("DOUBLE POINTS", null, "#ffd44e"); break;
      case "nuke": {
        const alive = [...w.zombies];
        for (const z of alive) if (z.alive) this.damageZombie(z, player, z.hp + 1, false, "nuke");
        for (const p of Object.values(w.players)) if (p.alive) p.score += 400;
        this.addEvent("NUKE! +400 pontos para todos", null, "#fb973a"); break;
      }
      case "carpenter":
        for (const win of this.map.windows) w.windows[win.id] = win.maxBoards;
        for (const p of Object.values(w.players)) if (p.alive) p.score += 200;
        this.addEvent("CARPENTER • barricadas reparadas", null, "#65e69a"); break;
    }
  }

  interact(p) {
    if (!p.alive || p.downed) return;
    if (Object.values(this.world.players).some((q) => q.uid !== p.uid && q.alive && q.downed && dist(p.x, p.y, q.x, q.y) < 92)) return;
    const target = this.nearestInteractable(p);
    if (!target) { this.addNotice(p.uid, "NADA PARA USAR AQUI", "#bdc6d3"); return; }
    const w = this.world;
    if (target.kind === "door") {
      const d = target.item;
      if (d.power && !w.power) { this.addNotice(p.uid, "PRECISA LIGAR A ENERGIA", "#ff9f64"); return; }
      if (p.score < d.cost) { this.addNotice(p.uid, `FALTAM ${d.cost - p.score} PONTOS`, "#ff7d88"); return; }
      p.score -= d.cost; w.unlocked[d.id] = true; w.doorDamage[d.id] = 0;
      this.addEvent(`${p.name} abriu ${d.name} • ${d.cost} pts`, p.uid, "#ffe194"); return;
    }
    if (target.kind === "switch") {
      if (w.power) { this.addNotice(p.uid, "ENERGIA JÁ ESTÁ LIGADA", "#ffe194"); return; }
      w.power = true;
      for (const d of this.map.doors) if (d.cost === 0 && d.power) w.unlocked[d.id] = true;
      this.addEvent(`${p.name} ligou a energia`, p.uid, "#8effbb"); return;
    }
    if (target.kind === "perk") {
      const perkId = target.item.perk, perk = PERKS[perkId];
      if (!perk) return;
      if (p.perks.includes(perkId)) { this.addNotice(p.uid, "VOCÊ JÁ TEM ESSE PERK", perk.color); return; }
      if (p.perks.length >= 4) { this.addNotice(p.uid, "LIMITE DE 4 PERKS", "#ff9f64"); return; }
      const cost = perkCost(perkId, Object.keys(w.players).length > 1);
      if (p.score < cost) { this.addNotice(p.uid, `PRECISA DE ${cost} PONTOS`, "#ff7d88"); return; }
      p.score -= cost; p.perks.push(perkId);
      if (perkId === "specialty_armorvest") { p.maxHp = 250; p.hp = Math.min(250, Math.max(100, p.hp)); }
      if (perkId === "specialty_quickrevive") p.quickRevives = 1;
      if (perkId === "specialty_twoprimaries") p.weapons.tertiary = null;
      this.addEvent(`${p.name} comprou ${perk.name}`, p.uid, perk.color); return;
    }
    if (target.kind === "wallbuy") {
      const item = target.item, spec = getWeapon(item.weapon);
      if (!spec) return;
      const cost = spec.cost ?? 1000;
      if (p.score < cost) { this.addNotice(p.uid, `PRECISA DE ${cost} PONTOS`, "#ff7d88"); return; }
      this.buyWeapon(p, item.weapon, cost, item.name);
      return;
    }
    if (target.kind === "box") {
      if (w.boxCooldown > 0 || w.boxBusy) { this.addNotice(p.uid, "A CAIXA ESTÁ OCUPADA", "#e2ca82"); return; }
      if (p.score < COST.BOX) { this.addNotice(p.uid, `A CAIXA CUSTA ${COST.BOX}`, "#ff7d88"); return; }
      p.score -= COST.BOX;
      const weapon = rollBox(this.rng);
      w.boxBusy = { uid: p.uid, weapon, until: w.time + 1.9 };
      this.addEvent(`${p.name} abriu a Mystery Box…`, p.uid, "#b8a0ff"); return;
    }
    if (target.kind === "pap") {
      if (!w.power) { this.addNotice(p.uid, "LIGUE A ENERGIA PRIMEIRO", "#ff9f64"); return; }
      const gun = playerGun(p), spec = gun && getWeapon(gun.id);
      if (!gun || !spec?.pap) { this.addNotice(p.uid, "ARMA SEM MELHORIA DISPONÍVEL", "#e2ca82"); return; }
      if (p.score < COST.PAP) { this.addNotice(p.uid, `PACK-A-PUNCH: ${COST.PAP} PONTOS`, "#ff7d88"); return; }
      p.score -= COST.PAP;
      const oldSpec = spec, upgraded = spec.pap;
      gun.id = upgraded.id; gun.clip = upgraded.mag ?? oldSpec.mag; gun.reserve = upgraded.res ?? oldSpec.res;
      this.addEvent(`${p.name} melhorou ${oldSpec.name} • ${upgraded.name}`, p.uid, "#ff9ade"); return;
    }
    if (target.kind === "window") {
      const win = target.item;
      const boards = w.windows[win.id] ?? 0;
      if (boards >= win.maxBoards) { this.addNotice(p.uid, "BARRICADA COMPLETA", "#e2ca82"); return; }
      w.windows[win.id] = boards + 1;
      p.score += SCORE.BOARD;
      this.addEvent(`${p.name} consertou a janela +10`, p.uid, "#8effbb"); return;
    }
  }

  nearestInteractable(p) {
    const w = this.world, choices = [];
    const add = (kind, item, x, y, priority = 0) => {
      const d = dist(p.x, p.y, x, y);
      if (d <= INTERACT_RADIUS) choices.push({ kind, item, x, y, d: d - priority });
    };
    for (const d of this.map.doors) if (!w.unlocked[d.id]) add("door", d, d.center.x, d.center.y, 15);
    for (const item of this.map.perks) add("perk", item, item.x, item.y, 4);
    for (const item of this.map.wallbuys) add("wallbuy", item, item.x, item.y, 3);
    for (const item of this.map.pap) add("pap", item, item.x, item.y, 3);
    for (const item of this.map.switches) if (!w.power) add("switch", item, item.x, item.y, 6);
    const box = this.map.boxes[w.activeBox % Math.max(1, this.map.boxes.length)];
    if (box) add("box", box, box.x, box.y, 5);
    for (const item of this.map.windows) if ((w.windows[item.id] ?? 6) < item.maxBoards) add("window", item, item.inner.x, item.inner.y, 8);
    choices.sort((a, b) => a.d - b.d);
    return choices[0] || null;
  }

  buyWeapon(p, weaponId, cost, label = "") {
    const existingSlot = slotsFor(p).find((key) => p.weapons[key]?.id === weaponId);
    if (existingSlot) {
      const gun = p.weapons[existingSlot], spec = getWeapon(weaponId);
      const refill = Math.ceil(cost * 0.5);
      if (p.score < refill) { this.addNotice(p.uid, `MUNIÇÃO CUSTA ${refill}`, "#ff7d88"); return; }
      p.score -= refill; gun.clip = spec.mag; gun.reserve = spec.res;
      this.addEvent(`${p.name} comprou munição • ${spec.name}`, p.uid, "#8effbb"); return;
    }
    if (p.score < cost) { this.addNotice(p.uid, `PRECISA DE ${cost} PONTOS`, "#ff7d88"); return; }
    p.score -= cost;
    let slot = slotsFor(p).find((key) => !p.weapons[key]);
    if (!slot) slot = p.selected;
    p.weapons[slot] = freshGun(weaponId); p.selected = slot;
    this.addEvent(`${p.name} comprou ${getWeapon(weaponId).name || label}`, p.uid, p.color);
  }

  resolveBox() {
    const busy = this.world.boxBusy;
    if (!busy) return;
    const player = this.world.players[busy.uid];
    if (player?.alive) {
      const slots = slotsFor(player);
      let slot = slots.find((key) => !player.weapons[key]);
      if (!slot) slot = player.selected;
      player.weapons[slot] = freshGun(busy.weapon); player.selected = slot;
      const spec = getWeapon(busy.weapon);
      this.addEvent(`${player.name} recebeu ${spec?.name || busy.weapon}!`, player.uid, "#c7a7ff");
    }
    this.world.boxBusy = null;
    this.world.boxUses += 1;
    this.world.boxCooldown = 2.5;
    if (this.world.boxUses >= 4 && this.map.boxes.length > 1) {
      let next = this.world.activeBox;
      while (next === this.world.activeBox) next = this.rng.int(this.map.boxes.length);
      this.world.activeBox = next; this.world.boxUses = 0;
      this.addEvent("A Mystery Box mudou de lugar", null, "#c7a7ff");
    }
  }

  getPrompt(p) {
    if (!p || !p.alive) return "";
    if (p.downed) return "VOCÊ ESTÁ ABATIDO • AGUARDE UM COMPANHEIRO";
    const teammate = Object.values(this.world.players).find((q) => q.uid !== p.uid && q.alive && q.downed && dist(p.x, p.y, q.x, q.y) < 92);
    if (teammate) return `SEGURE E  REANIMAR ${teammate.name.toUpperCase()}`;
    const target = this.nearestInteractable(p);
    if (!target) return "";
    const w = this.world;
    switch (target.kind) {
      case "door": {
        const d = target.item;
        return d.power && !w.power ? "ENERGIA NECESSÁRIA" : `E  ABRIR ${d.name.replaceAll("_", " ").toUpperCase()}  •  ${d.cost} PTS`;
      }
      case "switch": return "E  LIGAR ENERGIA";
      case "perk": {
        const perk = PERKS[target.item.perk];
        if (!perk) return "";
        const cost = perkCost(perk.id, Object.keys(w.players).length > 1);
        return `${p.perks.includes(perk.id) ? "✓ " : "E  "}${perk.name.toUpperCase()}  •  ${cost} PTS`;
      }
      case "wallbuy": {
        const spec = getWeapon(target.item.weapon);
        return `E  ${spec?.name?.toUpperCase() || "ARMA"}  •  ${spec?.cost ?? 1000} PTS`;
      }
      case "box": return w.boxBusy ? "MYSTERY BOX • OCUPADA" : `E  MYSTERY BOX  •  ${COST.BOX} PTS`;
      case "pap": return `E  PACK-A-PUNCH  •  ${COST.PAP} PTS`;
      case "window": return "E  RECONSTRUIR BARRICADA  •  +10 PTS";
      default: return "";
    }
  }

  reloadAll() {
    for (const p of Object.values(this.world.players)) {
      for (const gun of Object.values(p.weapons)) {
        if (!gun) continue;
        const spec = getWeapon(gun.id);
        if (spec && spec.res !== Infinity) { gun.clip = spec.mag; gun.reserve = spec.res; }
      }
    }
  }

  addEvent(text, playerUid = null, color = "#e6edf7") {
    const event = { id: ++this.counter.event, text: String(text).slice(0, 120), uid: playerUid, color, time: this.world.time, until: this.world.time + 4.4 };
    this.world.notices.push(event);
    if (this.world.notices.length > 18) this.world.notices.shift();
  }

  addNotice(playerUid, text, color = "#fff") {
    const notice = { id: ++this.counter.event, text, uid: playerUid, color, time: this.world.time, until: this.world.time + 1.8 };
    this.world.notices.push(notice);
    if (this.world.notices.length > 18) this.world.notices.shift();
  }

  pointToSegment(px, py, ax, ay, bx, by) {
    const dx = bx - ax, dy = by - ay, ll = dx * dx + dy * dy;
    const t = ll ? clamp(((px - ax) * dx + (py - ay) * dy) / ll, 0, 1) : 0;
    return { t, dist: Math.hypot(px - (ax + t * dx), py - (ay + t * dy)) };
  }

  angleDiff(a, b) { return Math.abs(((a - b + Math.PI * 3) % (Math.PI * 2)) - Math.PI); }
}

/** Inputs sem propriedades opcionais (JSON-friendly), usados pela rede. */
export function neutralInput(player) {
  return { x: 0, y: 0, aim: player?.angle || 0, fire: false, sprint: false, interactHeld: false, slot: player?.selected || "primary", seq: { interact: 0, reload: 0, melee: 0, swap: 0 } };
}

export function promptFor(map, world, player) {
  if (!world || !player) return "";
  const helper = { map, world, nearestInteractable: Simulation.prototype.nearestInteractable };
  return Simulation.prototype.getPrompt.call(helper, player);
}
