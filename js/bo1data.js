// ============================================================
//  BO1 ZOMBIES: WEB  —  Dados fiéis ao Black Ops 1
//
//  Nomes internos (`*_zm`, `specialty_*`) extraídos do repositório
//  decompilado  MisaDev4/bo1-zombies-decompiled  (mods/mapkit + src).
//  Valores de dano/cadência/custo seguem o modo Zombies do BO1.
// ============================================================

// -------------------- ARMAS --------------------
// dmg      : dano por bala no corpo
// hs       : multiplicador de dano na cabeça
// rpm      : disparos por minuto
// mag      : tamanho do pente
// res      : reserva máxima
// reload   : segundos
// auto     : segur o botão dispara continuamente
// pellets  : projéteis por disparo (shotguns)
// spread   : graus de dispersão
// cost     : preço na parede (null = só Mystery Box)
// papDmg   : dano após Pack-a-Punch
//
// kind: 'pistol'|'smg'|'ar'|'lmg'|'sniper'|'shotgun'|'special'|'melee'
export const WEAPONS = {
  // ---- Pistolas ----
  m1911_zm: {
    id: "m1911_zm", name: "M1911", kind: "pistol", dmg: 40, hs: 2.0, rpm: 240, mag: 8, res: 80,
    reload: 1.5, auto: false, pellets: 1, spread: 1.6, cost: null, speed: 1.0,
    pap: { id: "m1911_upgraded_zm", name: "⚡ M1911", dmg: 90, mag: 12, res: 120, rpm: 300 }
  },
  python_zm: {
    id: "python_zm", name: "Python", kind: "pistol", dmg: 100, hs: 2.0, rpm: 180, mag: 6, res: 60,
    reload: 2.4, auto: false, pellets: 1, spread: 1.2, cost: 1500, speed: 1.0,
    pap: { id: "python_upgraded_zm", name: "⚡ Python", dmg: 220, mag: 8, res: 80, rpm: 220 }
  },
  cz75_zm: {
    id: "cz75_zm", name: "CZ75", kind: "pistol", dmg: 45, hs: 2.0, rpm: 400, mag: 12, res: 120,
    reload: 2.0, auto: true, pellets: 1, spread: 2.2, cost: null, speed: 1.0,
    pap: { id: "cz75_upgraded_zm", name: "⚡ CZ75", dmg: 100, mag: 20, res: 200, rpm: 600 }
  },

  // ---- SMGs ----
  mp5k_zm: {
    id: "mp5k_zm", name: "MP5K", kind: "smg", dmg: 30, hs: 1.6, rpm: 800, mag: 30, res: 180,
    reload: 2.2, auto: true, pellets: 1, spread: 2.6, cost: 1000, speed: 1.0,
    pap: { id: "mp5k_upgraded_zm", name: "⚡ MP5K", dmg: 70, mag: 40, res: 240, rpm: 900 }
  },
  ak74u_zm: {
    id: "ak74u_zm", name: "AK74u", kind: "smg", dmg: 40, hs: 1.6, rpm: 800, mag: 30, res: 210,
    reload: 2.4, auto: true, pellets: 1, spread: 2.9, cost: 1200, speed: 0.98,
    pap: { id: "ak74u_upgraded_zm", name: "⚡ AK74u", dmg: 90, mag: 40, res: 280, rpm: 850 }
  },
  pm63_zm: {
    id: "pm63_zm", name: "PM63", kind: "smg", dmg: 30, hs: 1.5, rpm: 750, mag: 20, res: 160,
    reload: 2.0, auto: true, pellets: 1, spread: 3.1, cost: 1000, speed: 1.02,
    pap: { id: "pm63_upgraded_zm", name: "⚡ PM63", dmg: 70, mag: 30, res: 240, rpm: 850 }
  },
  mpl_zm: {
    id: "mpl_zm", name: "MPL", kind: "smg", dmg: 30, hs: 1.6, rpm: 850, mag: 20, res: 160,
    reload: 2.1, auto: true, pellets: 1, spread: 3.0, cost: 1000, speed: 1.02,
    pap: { id: "mpl_upgraded_zm", name: "⚡ MPL", dmg: 70, mag: 32, res: 240, rpm: 950 }
  },
  spectre_zm: {
    id: "spectre_zm", name: "Spectre", kind: "smg", dmg: 35, hs: 1.6, rpm: 800, mag: 30, res: 210,
    reload: 2.3, auto: true, pellets: 1, spread: 2.5, cost: null, speed: 1.0,
    pap: { id: "spectre_upgraded_zm", name: "⚡ Spectre", dmg: 80, mag: 40, res: 280, rpm: 900 }
  },
  mp40_zm: {
    id: "mp40_zm", name: "MP40", kind: "smg", dmg: 40, hs: 1.5, rpm: 600, mag: 32, res: 192,
    reload: 2.5, auto: true, pellets: 1, spread: 2.8, cost: 1000, speed: 0.99,
    pap: { id: "mp40_upgraded_zm", name: "⚡ MP40", dmg: 90, mag: 40, res: 240, rpm: 650 }
  },

  // ---- Rifles de assalto ----
  m14_zm: {
    id: "m14_zm", name: "M14", kind: "ar", dmg: 70, hs: 1.8, rpm: 360, mag: 8, res: 96,
    reload: 2.3, auto: false, pellets: 1, spread: 1.0, cost: 500, speed: 0.98,
    pap: { id: "m14_upgraded_zm", name: "⚡ M14", dmg: 150, mag: 15, res: 150, rpm: 480 }
  },
  m16_zm: {
    id: "m16_zm", name: "M16", kind: "ar", dmg: 45, hs: 1.7, rpm: 540, mag: 30, res: 180,
    reload: 2.4, auto: false, burst: 3, pellets: 1, spread: 1.4, cost: 1200, speed: 0.97,
    pap: { id: "m16_gl_upgraded_zm", name: "⚡ M16 + GL", dmg: 100, mag: 30, res: 210, rpm: 600 }
  },
  famas_zm: {
    id: "famas_zm", name: "FAMAS", kind: "ar", dmg: 45, hs: 1.7, rpm: 580, mag: 25, res: 200,
    reload: 2.5, auto: false, burst: 3, pellets: 1, spread: 1.3, cost: 1400, speed: 0.97,
    pap: { id: "famas_upgraded_zm", name: "⚡ FAMAS", dmg: 100, mag: 35, res: 245, rpm: 900 }
  },
  galil_zm: {
    id: "galil_zm", name: "Galil", kind: "ar", dmg: 45, hs: 1.7, rpm: 700, mag: 35, res: 245,
    reload: 2.8, auto: true, pellets: 1, spread: 2.0, cost: 1800, speed: 0.95,
    pap: { id: "galil_upgraded_zm", name: "⚡ Galil", dmg: 100, mag: 45, res: 315, rpm: 750 }
  },
  fnfal_zm: {
    id: "fnfal_zm", name: "FN FAL", kind: "ar", dmg: 75, hs: 1.8, rpm: 400, mag: 20, res: 160,
    reload: 2.5, auto: false, pellets: 1, spread: 1.0, cost: 1600, speed: 0.96,
    pap: { id: "fnfal_upgraded_zm", name: "⚡ FN FAL", dmg: 160, mag: 30, res: 210, rpm: 600 }
  },
  commando_zm: {
    id: "commando_zm", name: "Commando", kind: "ar", dmg: 45, hs: 1.7, rpm: 700, mag: 30, res: 210,
    reload: 2.6, auto: true, pellets: 1, spread: 2.2, cost: 1500, speed: 0.96,
    pap: { id: "commando_upgraded_zm", name: "⚡ Commando", dmg: 100, mag: 40, res: 280, rpm: 750 }
  },
  ak47_zm: {
    id: "ak47_zm", name: "AK-47", kind: "ar", dmg: 60, hs: 1.7, rpm: 600, mag: 30, res: 210,
    reload: 2.7, auto: true, pellets: 1, spread: 2.4, cost: null, speed: 0.94,
    pap: { id: "ak47_upgraded_zm", name: "⚡ AK-47", dmg: 130, mag: 40, res: 280, rpm: 650 }
  },
  aug_acog_zm: {
    id: "aug_acog_zm", name: "AUG", kind: "ar", dmg: 50, hs: 1.8, rpm: 650, mag: 30, res: 210,
    reload: 2.6, auto: true, pellets: 1, spread: 1.5, cost: null, speed: 0.96,
    pap: { id: "aug_acog_upgraded_zm", name: "⚡ AUG", dmg: 110, mag: 42, res: 294, rpm: 700 }
  },
  g11_lps_zm: {
    id: "g11_lps_zm", name: "G11", kind: "ar", dmg: 40, hs: 1.6, rpm: 480, mag: 45, res: 180,
    reload: 3.0, auto: false, burst: 3, pellets: 1, spread: 1.1, cost: 2000, speed: 0.97,
    pap: { id: "g11_lps_upgraded_zm", name: "⚡ G11", dmg: 90, mag: 45, res: 270, rpm: 1500 }
  },

  // ---- LMGs ----
  hk21_zm: {
    id: "hk21_zm", name: "HK21", kind: "lmg", dmg: 55, hs: 1.7, rpm: 700, mag: 40, res: 240,
    reload: 4.0, auto: true, pellets: 1, spread: 2.6, cost: 2000, speed: 0.9,
    pap: { id: "hk21_upgraded_zm", name: "⚡ HK21", dmg: 120, mag: 60, res: 360, rpm: 750 }
  },
  rpk_zm: {
    id: "rpk_zm", name: "RPK", kind: "lmg", dmg: 50, hs: 1.7, rpm: 700, mag: 40, res: 240,
    reload: 3.8, auto: true, pellets: 1, spread: 2.8, cost: 1800, speed: 0.9,
    pap: { id: "rpk_upgraded_zm", name: "⚡ RPK", dmg: 110, mag: 60, res: 360, rpm: 750 }
  },
  minigun_zm: {
    id: "minigun_zm", name: "Minigun", kind: "lmg", dmg: 40, hs: 1.5, rpm: 1500, mag: 400, res: 400,
    reload: 6.0, auto: true, pellets: 1, spread: 3.4, cost: null, speed: 0.85,
    pap: null
  },

  // ---- Snipers ----
  l96a1_zm: {
    id: "l96a1_zm", name: "L96A1", kind: "sniper", dmg: 200, hs: 2.5, rpm: 55, mag: 5, res: 40,
    reload: 3.2, auto: false, pellets: 1, spread: 0.2, cost: 2000, speed: 0.92,
    pap: { id: "l96a1_upgraded_zm", name: "⚡ L96A1", dmg: 450, mag: 8, res: 64, rpm: 70 }
  },
  dragunov_zm: {
    id: "dragunov_zm", name: "Dragunov", kind: "sniper", dmg: 110, hs: 2.2, rpm: 240, mag: 10, res: 80,
    reload: 2.8, auto: false, pellets: 1, spread: 0.5, cost: 1600, speed: 0.94,
    pap: { id: "dragunov_upgraded_zm", name: "⚡ Dragunov", dmg: 240, mag: 20, res: 140, rpm: 300 }
  },

  // ---- Shotguns ----
  rottweil72_zm: {
    id: "rottweil72_zm", name: "Olympia", kind: "shotgun", dmg: 40, hs: 1.5, rpm: 90, mag: 2, res: 24,
    reload: 2.6, auto: false, pellets: 8, spread: 8.0, cost: 500, speed: 0.98, range: 620,
    pap: { id: "rottweil72_upgraded_zm", name: "⚡ Olympia", dmg: 90, mag: 4, res: 36, rpm: 110 }
  },
  ithaca_zm: {
    id: "ithaca_zm", name: "Stakeout", kind: "shotgun", dmg: 35, hs: 1.5, rpm: 70, mag: 6, res: 48,
    reload: 3.4, auto: false, pellets: 8, spread: 9.0, cost: 1000, speed: 0.96, range: 700,
    pap: { id: "ithaca_upgraded_zm", name: "⚡ Stakeout", dmg: 80, mag: 8, res: 64, rpm: 90 }
  },
  spas_zm: {
    id: "spas_zm", name: "SPAS-12", kind: "shotgun", dmg: 32, hs: 1.5, rpm: 130, mag: 8, res: 64,
    reload: 4.0, auto: false, pellets: 8, spread: 9.5, cost: 1400, speed: 0.95, range: 700,
    pap: { id: "spas_upgraded_zm", name: "⚡ SPAS-12", dmg: 72, mag: 12, res: 96, rpm: 160 }
  },
  hs10_zm: {
    id: "hs10_zm", name: "HS10", kind: "shotgun", dmg: 45, hs: 1.5, rpm: 100, mag: 2, res: 20,
    reload: 2.4, auto: false, pellets: 10, spread: 10.0, cost: null, speed: 0.97, range: 620,
    pap: { id: "hs10_upgraded_zm", name: "⚡ HS10", dmg: 100, mag: 4, res: 32, rpm: 120 }
  },

  // ---- Especiais (Mystery Box) ----
  ray_gun_zm: {
    id: "ray_gun_zm", name: "Ray Gun", kind: "special", dmg: 350, hs: 1.5, rpm: 200, mag: 20, res: 160,
    reload: 2.6, auto: false, pellets: 1, spread: 0.4, cost: null, speed: 0.98,
    proj: "rocket", splash: 90, splashRadius: 190, boxOnly: true,
    pap: { id: "ray_gun_upgraded_zm", name: "⚡ Porter's X2 Ray Gun", dmg: 700, mag: 40, res: 320, splash: 180 }
  },
  thundergun_zm: {
    id: "thundergun_zm", name: "Thundergun", kind: "special", dmg: 0, hs: 1, rpm: 40, mag: 2, res: 12,
    reload: 3.0, auto: false, pellets: 1, spread: 0, cost: null, speed: 0.95,
    knockback: 1, cone: 34, coneRange: 900, boxOnly: true,
    pap: null
  },
  freezegun_zm: {
    id: "freezegun_zm", name: "Winter's Howl", kind: "special", dmg: 0, hs: 1, rpm: 45, mag: 3, res: 24,
    reload: 3.0, auto: false, pellets: 1, spread: 0, cost: null, speed: 0.96,
    freeze: 1, cone: 30, coneRange: 700, boxOnly: true,
    pap: { id: "freezegun_upgraded_zm", name: "⚡ Winter's Howl", mag: 6, res: 48 }
  },
  crossbow_explosive_zm: {
    id: "crossbow_explosive_zm", name: "Crossbow Explosivo", kind: "special", dmg: 150, hs: 2, rpm: 45, mag: 1, res: 20,
    reload: 2.2, auto: false, pellets: 1, spread: 0.3, cost: null, speed: 1.0,
    proj: "bolt", splash: 250, splashRadius: 170, boxOnly: true,
    pap: { id: "crossbow_explosive_upgraded_zm", name: "⚡ Crossbow", dmg: 300, splash: 500, splashRadius: 230 }
  },
  china_lake_zm: {
    id: "china_lake_zm", name: "China Lake", kind: "special", dmg: 200, hs: 1.5, rpm: 60, mag: 3, res: 24,
    reload: 3.4, auto: false, pellets: 1, spread: 1.2, cost: null, speed: 0.93,
    proj: "rocket", splash: 300, splashRadius: 220, boxOnly: true,
    pap: { id: "china_lake_upgraded_zm", name: "⚡ China Lake", dmg: 400, mag: 6, res: 48, splashRadius: 280 }
  },
  m72_law_zm: {
    id: "m72_law_zm", name: "M72 LAW", kind: "special", dmg: 300, hs: 1.5, rpm: 30, mag: 1, res: 10,
    reload: 3.2, auto: false, pellets: 1, spread: 0.5, cost: null, speed: 0.92,
    proj: "rocket", splash: 350, splashRadius: 240, boxOnly: true,
    pap: { id: "m72_law_upgraded_zm", name: "⚡ M72 LAW", dmg: 600, splashRadius: 300 }
  },

  // ---- Corpo a corpo ----
  knife_zm: {
    id: "knife_zm", name: "Faca", kind: "melee", dmg: 150, hs: 1.5, rpm: 120, mag: Infinity, res: Infinity,
    reload: 0, auto: false, pellets: 1, spread: 0, cost: null, speed: 1.0, melee: true, meleeRange: 90,
    pap: null
  },
  bowie_knife_zm: {
    id: "bowie_knife_zm", name: "Bowie Knife", kind: "melee", dmg: 300, hs: 2, rpm: 120, mag: Infinity, res: Infinity,
    reload: 0, auto: false, pellets: 1, spread: 0, cost: 3000, speed: 1.0, melee: true, meleeRange: 95,
    pap: null
  }
};

const PAP_WEAPONS = new Map();
for (const base of Object.values(WEAPONS)) {
  if (base.pap?.id) PAP_WEAPONS.set(base.pap.id, { ...base, ...base.pap, pap: null });
}
export function getWeapon(id) { return WEAPONS[id] || PAP_WEAPONS.get(id) || null; }

export const START_WEAPON = "m1911_zm";
export const MELEE_WEAPON = "knife_zm";

/** Peso relativo no Mystery Box (raridade). */
export const BOX_WEIGHTS = {
  common: ["m14_zm", "mp5k_zm", "ithaca_zm", "ak74u_zm", "pm63_zm", "mpl_zm", "mp40_zm", "m16_zm", "famas_zm", "rottweil72_zm"],
  uncommon: ["galil_zm", "fnfal_zm", "commando_zm", "spectre_zm", "aug_acog_zm", "dragunov_zm", "spas_zm", "python_zm", "cz75_zm", "ak47_zm"],
  rare: ["hk21_zm", "rpk_zm", "l96a1_zm", "g11_lps_zm", "hs10_zm", "crossbow_explosive_zm", "china_lake_zm", "m72_law_zm"],
  wonder: ["ray_gun_zm", "thundergun_zm", "freezegun_zm", "minigun_zm"]
};

export function rollBox(rng) {
  const r = rng();
  const tier = r < 0.02 ? "wonder" : r < 0.16 ? "rare" : r < 0.52 ? "uncommon" : "common";
  return rng.pick(BOX_WEIGHTS[tier]);
}

// -------------------- PERKS --------------------
// specialty_* = nomes internos reais do BO1 (grep em mods/mapkit + src)
export const PERKS = {
  specialty_quickrevive: {
    id: "specialty_quickrevive", name: "Quick Revive", color: "#4fd0ff", short: "QR",
    costSolo: 500, costCoop: 1500,
    desc: "Revive sozinho uma vez (a cada 3 rodadas) / revive aliados mais rápido."
  },
  specialty_armorvest: {
    id: "specialty_armorvest", name: "Juggernog", color: "#ff4d4d", short: "JUG",
    cost: 2500,
    desc: "Aguenta muito mais dano. Essencial em rodadas altas."
  },
  specialty_fastreload: {
    id: "specialty_fastreload", name: "Speed Cola", color: "#3ddc84", short: "SPD",
    cost: 3000,
    desc: "Recarrega muito mais rápido e constrói barricadas em dobro."
  },
  specialty_rof: {
    id: "specialty_rof", name: "Double Tap Root Beer", color: "#ffd23d", short: "DT",
    cost: 2000,
    desc: "Aumenta a cadência de tiro em ~33%."
  },
  specialty_longersprint: {
    id: "specialty_longersprint", name: "Stamin-Up", color: "#ffe066", short: "STA",
    cost: 2000,
    desc: "Corre mais rápido e por mais tempo."
  },
  specialty_bulletaccuracy: {
    id: "specialty_bulletaccuracy", name: "Deadshot Daiquiri", color: "#7dffcf", short: "DS",
    cost: 1500,
    desc: "Mira automática na cabeça e dano de headshot aumentado."
  },
  specialty_flakjacket: {
    id: "specialty_flakjacket", name: "PhD Flopper", color: "#ff9b3d", short: "PHD",
    cost: 2000,
    desc: "Imune a dano explosivo próprio; queda vira explosão (Nuke)."
  },
  specialty_twoprimaries: {
    id: "specialty_twoprimaries", name: "Mule Kick", color: "#c8ff5c", short: "MK",
    cost: 4000,
    desc: "Carrega uma terceira arma."
  }
};

export const PERK_ORDER = Object.keys(PERKS);

// -------------------- ZUMBIS / RODADAS --------------------
// Fórmulas do modo Zombies do BO1.
export const ZOMBIE = {
  RADIUS: 15,
  baseSpeed: 88,          // world units/s, calibrado à escala do mapa web
  speedPerRound: 4.5,
  maxSpeed: 180,          // sprint acelera progressivamente nas rodadas altas
  maxAliveBase: 8,
  maxAlivePerPlayer: 6,
  maxAliveCap: 24,
  attackDamage: 34,       // sem Juggernog; Jugg = /4 aprox.
  attackRange: 44,
  attackCooldown: 1.0,
  windowDamageInterval: 0.85,
  health(round) {
    if (round <= 9) return 150 + (round - 1) * 100;
    return Math.round(950 * Math.pow(1.1, round - 9));
  },
  speed(round) {
    return Math.min(this.maxSpeed, this.baseSpeed + (round - 1) * this.speedPerRound);
  },
  /** Total de zumbis da rodada (aprox. BO1). */
  total(round, players) {
    const p = Math.max(1, players);
    const base = Math.floor(round * 6.0 + Math.pow(round, 0.72) * 1.6);
    return Math.max(6, Math.round(base * (1 + (p - 1) * 0.55)));
  },
  maxAlive(players) {
    return Math.min(this.maxAliveCap, this.maxAliveBase + (Math.max(1, players) - 1) * this.maxAlivePerPlayer);
  }
};

export const DOG = {
  RADIUS: 13,
  health(round) { return Math.round(70 * Math.pow(1.17, Math.max(0, round - 1)) + round * 10); },
  speed: 190,
  attackDamage: 40,
  attackRange: 40,
  attackCooldown: 1.2
};

/** Rodadas de cachorro: primeira entre 10-15, depois a cada ~5. */
export function isDogRound(round, rng) {
  if (round < 10) return false;
  const first = 10 + Math.floor(rng() * 6);
  if (round === first) return true;
  return (round - first) % 5 === 0 && round > first;
}

// -------------------- ECONOMIA --------------------
export const SCORE = {
  START: 500,
  BULLET_HIT: 10,
  KILL: 100,
  HEADSHOT_KILL: 120,
  MELEE_KILL: 130,
  BOARD: 10,
  MAX_BOARDS: 6
};

export const COST = {
  BOX: 950,
  PAP: 5000,
  REVIVE_SELF: 0
};

// -------------------- TIPOS DE ZUMBI --------------------
export const Z_TYPES = {
  normal: { color: "#8fa07a", scale: 1.0, name: "Zumbi" },
  armored: { color: "#6f7f9a", scale: 1.1, name: "Zumbi Blindado", hpMul: 1.6, dmgMul: 1.2 },
  sprinter: { color: "#a8856a", scale: 0.95, name: "Corredor", speedMul: 1.45, hpMul: 0.75 },
  dog: { color: "#3a3a3a", scale: 0.8, name: "Cachorro do Inferno" }
};
