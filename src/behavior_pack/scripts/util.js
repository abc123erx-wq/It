// ============================================================================
//  Creative Squad - Itens Lendarios  |  util.js
//  Helpers defensivos: tudo aqui e' escrito com try/catch porque a API de
//  scripts do Bedrock varia um pouco entre versoes (26.52 / 1.26.52).
// ============================================================================

import { world, system, EquipmentSlot, EntityComponentTypes, ItemStack } from "@minecraft/server";

export const log = (...args) => {
  try {
    console.warn("[CS] " + args.join(" "));
  } catch {}
};

// ---------------------------------------------------------------- equipamento
export function equippable(entity) {
  try {
    return entity.getComponent(EntityComponentTypes.Equippable);
  } catch {
    return undefined;
  }
}

export function slotItem(entity, slot) {
  try {
    const eq = equippable(entity);
    return eq ? eq.getEquipment(slot) : undefined;
  } catch {
    return undefined;
  }
}

export function setSlotItem(entity, slot, item) {
  try {
    const eq = equippable(entity);
    if (eq) eq.setEquipment(slot, item);
    return true;
  } catch {
    return false;
  }
}

export const HAND_SLOTS = [EquipmentSlot.Mainhand, EquipmentSlot.Offhand];

export const ALL_ARMOR_SLOTS = [
  EquipmentSlot.Head,
  EquipmentSlot.Chest,
  EquipmentSlot.Legs,
  EquipmentSlot.Feet,
];

export function heldItem(player) {
  return slotItem(player, EquipmentSlot.Mainhand);
}

export function isHolding(player, typeId) {
  return (
    slotItem(player, EquipmentSlot.Mainhand)?.typeId === typeId ||
    slotItem(player, EquipmentSlot.Offhand)?.typeId === typeId
  );
}

export function wearing(player, slot, typeId) {
  return slotItem(player, slot)?.typeId === typeId;
}

export function playerContainer(player) {
  try {
    return player.getComponent(EntityComponentTypes.Inventory)?.container;
  } catch {
    return undefined;
  }
}

/** Conjunto com o typeId de tudo que o jogador tem (inventario + equipamento). */
export function ownedIds(player) {
  const ids = new Set();
  for (const slot of [...ALL_ARMOR_SLOTS, ...HAND_SLOTS]) {
    const it = slotItem(player, slot);
    if (it) ids.add(it.typeId);
  }
  const c = playerContainer(player);
  if (c) {
    try {
      for (let i = 0; i < c.size; i++) {
        const it = c.getItem(i);
        if (it) ids.add(it.typeId);
      }
    } catch {}
  }
  return ids;
}

/** Lista de {slot, index, item} de todos os lugares onde um item pode estar. */
export function allItemRefs(player) {
  const refs = [];
  for (const slot of [...ALL_ARMOR_SLOTS, ...HAND_SLOTS]) {
    const it = slotItem(player, slot);
    if (it) refs.push({ kind: "equip", slot, item: it });
  }
  const c = playerContainer(player);
  if (c) {
    try {
      for (let i = 0; i < c.size; i++) {
        const it = c.getItem(i);
        if (it) refs.push({ kind: "inv", slot: i, item: it });
      }
    } catch {}
  }
  return refs;
}

/** Remove uma unidade do item indicado do inventario/equipamento. */
export function removeOne(player, typeId) {
  for (const slot of [...ALL_ARMOR_SLOTS, ...HAND_SLOTS]) {
    const it = slotItem(player, slot);
    if (it?.typeId === typeId) {
      setSlotItem(player, slot, undefined);
      return true;
    }
  }
  const c = playerContainer(player);
  if (!c) return false;
  try {
    for (let i = 0; i < c.size; i++) {
      const it = c.getItem(i);
      if (it?.typeId !== typeId) continue;
      if (it.amount > 1) {
        it.amount -= 1;
        c.setItem(i, it);
      } else {
        c.setItem(i, undefined);
      }
      return true;
    }
  } catch {}
  return false;
}

export function give(player, typeId, amount = 1) {
  try {
    const c = playerContainer(player);
    if (c) {
      const left = c.addItem(new ItemStack(typeId, amount));
      if (!left) return true;
    }
    player.runCommand(`give @s ${typeId} ${amount}`);
    return true;
  } catch {
    try {
      player.runCommand(`give @s ${typeId} ${amount}`);
      return true;
    } catch {
      return false;
    }
  }
}

// ---------------------------------------------------------------- efeitos
/** Aplica o efeito mantendo-o sempre ativo sem "piscar". */
export function keepEffect(entity, id, ticks, amplifier = 0, particles = false) {
  try {
    const cur = entity.getEffect(id);
    if (cur && cur.amplifier === amplifier && cur.duration > ticks - 20) return;
    entity.addEffect(id, ticks, { amplifier, showParticles: particles });
  } catch {}
}

export function clearEffect(entity, id) {
  try {
    if (entity.getEffect(id)) entity.removeEffect(id);
  } catch {}
}

// ---------------------------------------------------------------- movimento
/** applyKnockback funciona diferente em 2.0.0 e em versoes anteriores. */
export function knockback(entity, dirX, dirZ, strength, vertical = 0.45) {
  const len = Math.hypot(dirX, dirZ) || 1;
  const nx = dirX / len;
  const nz = dirZ / len;
  try {
    entity.applyKnockback({ x: nx * strength, z: nz * strength }, vertical);
    return;
  } catch {}
  try {
    entity.applyKnockback(nx, nz, strength, vertical);
  } catch {}
}

// ---------------------------------------------------------------- geometria
export function add(a, b) {
  return { x: a.x + b.x, y: a.y + b.y, z: a.z + b.z };
}

export function scale(v, k) {
  return { x: v.x * k, y: v.y * k, z: v.z * k };
}

export function normalize(v) {
  const len = Math.hypot(v.x, v.y, v.z) || 1;
  return { x: v.x / len, y: v.y / len, z: v.z / len };
}

export function distance(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
}

/** Entidades dentro de um cone na frente do jogador. */
export function entitiesInCone(player, range, halfAngleDeg, extra = {}) {
  const out = [];
  const origin = player.getHeadLocation();
  const dir = normalize(player.getViewDirection());
  const cosLimit = Math.cos((halfAngleDeg * Math.PI) / 180);
  try {
    const list = player.dimension.getEntities({
      location: origin,
      maxDistance: range,
      excludeTypes: ["minecraft:item", "minecraft:xp_orb", "minecraft:arrow"],
      excludeNames: [player.name],
      ...extra,
    });
    for (const e of list) {
      try {
        if (!e || e.id === player.id) continue;
        const head = e.getHeadLocation();
        const to = normalize({
          x: head.x - origin.x,
          y: head.y - origin.y,
          z: head.z - origin.z,
        });
        const dot = to.x * dir.x + to.y * dir.y + to.z * dir.z;
        if (dot >= cosLimit) out.push(e);
      } catch {}
    }
  } catch {}
  return out;
}

/** Primeiro bloco atingido pelo raio de visao. */
export function rayBlock(player, range) {
  try {
    const hit = player.dimension.getBlockFromRay(
      player.getHeadLocation(),
      player.getViewDirection(),
      { maxDistance: range, includeLiquidBlocks: false, includePassableBlocks: false }
    );
    if (hit) return { block: hit.block, location: hit.block.location, hit: true };
  } catch {}
  const end = add(player.getHeadLocation(), scale(normalize(player.getViewDirection()), range));
  return { block: undefined, location: end, hit: false };
}

export function particle(dimension, name, location) {
  try {
    dimension.spawnParticle(name, location);
  } catch {}
}

export function sound(dimension, id, location, volume = 1, pitch = 1) {
  try {
    dimension.playSound(id, location, { volume, pitch });
  } catch {}
}

// ---------------------------------------------------------------- cooldowns
const cooldowns = new Map();

export function onCooldown(player, key, ticks) {
  const now = system.currentTick;
  const last = cooldowns.get(player.id + ":" + key);
  if (last === undefined) return false;
  return now - last < ticks;
}

export function startCooldown(player, key) {
  cooldowns.set(player.id + ":" + key, system.currentTick);
}

/** Retorna o tempo restante em segundos (para mostrar na actionbar). */
export function cooldownLeft(player, key, ticks) {
  const last = cooldowns.get(player.id + ":" + key);
  if (last === undefined) return 0;
  const left = ticks - (system.currentTick - last);
  return left > 0 ? left / 20 : 0;
}

// ---------------------------------------------------------------- mensagens
export function actionbar(player, text) {
  try {
    player.onScreenDisplay.setActionBar(text);
  } catch {}
}

export function tell(player, text) {
  try {
    player.sendMessage(text);
  } catch {}
}

export function broadcast(text) {
  try {
    world.sendMessage(text);
  } catch {}
}

export function nearestPlayer(player, maxDistance = 512) {
  let best;
  let bestDist = Infinity;
  try {
    for (const other of world.getAllPlayers()) {
      if (other.id === player.id) continue;
      if (other.dimension.id !== player.dimension.id) continue;
      const d = distance(other.location, player.location);
      if (d < bestDist && d <= maxDistance) {
        best = other;
        bestDist = d;
      }
    }
  } catch {}
  return best ? { player: best, distance: bestDist } : undefined;
}

/** Direcao em texto (N, NE, L, ...) do ponto de vista do jogador. */
export function directionName(from, to) {
  const dx = to.x - from.x;
  const dz = to.z - from.z;
  const angle = (Math.atan2(dz, dx) * 180) / Math.PI;
  const dirs = [
    "Leste", "Sudeste", "Sul", "Sudoeste",
    "Oeste", "Noroeste", "Norte", "Nordeste",
  ];
  const idx = Math.round((angle + 360) % 360 / 45) % 8;
  return dirs[idx];
}

// ---------------------------------------------------------------- dano
/** Aplica dano de ataque creditando o jogador (funciona em 2.x e versoes antigas). */
export function hurt(target, amount, attacker, cause = "entityAttack") {
  try {
    const opts = { cause };
    if (attacker) opts.damagingEntity = attacker;
    target.applyDamage(amount, opts);
    return true;
  } catch {}
  try {
    target.applyDamage(amount);
    return true;
  } catch {
    return false;
  }
}

export function lightning(dimension, location) {
  try {
    dimension.spawnEntity("minecraft:lightning_bolt", location);
  } catch {}
}

/** true se estiver trovejando na dimensao do jogador. */
export function isThundering(player) {
  try {
    return player.dimension.getWeather?.() === "Thunder";
  } catch {
    return false;
  }
}
