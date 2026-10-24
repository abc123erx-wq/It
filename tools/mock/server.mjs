// ============================================================================
//  Mock minimo da API @minecraft/server (somente para testes offline)
//  Simula o suficiente para exercitar os scripts do addon fora do jogo.
// ============================================================================

export const log = { erros: [] };

function track(fn) {
  return (...args) => {
    try {
      return fn(...args);
    } catch (e) {
      log.erros.push(String(e && e.stack ? e.stack : e));
      throw e;
    }
  };
}

// --------------------------------------------------------------- enums
export const EquipmentSlot = {
  Head: "slot.armor.head",
  Chest: "slot.armor.chest",
  Legs: "slot.armor.legs",
  Feet: "slot.armor.feet",
  Mainhand: "slot.weapon.mainhand",
  Offhand: "slot.weapon.offhand",
  Body: "slot.armor.body",
};

export const EntityComponentTypes = {
  Equippable: "minecraft:equippable",
  Inventory: "minecraft:inventory",
  Health: "minecraft:health",
};

// --------------------------------------------------------------- ItemStack
let itemId = 0;
export class ItemStack {
  constructor(typeId, amount = 1) {
    this.typeId = typeId;
    this.amount = amount;
    this.lore = [];
    this.enchantments = new Map();
    this._id = ++itemId;
  }
  clone() {
    const c = new ItemStack(this.typeId, this.amount);
    c.lore = [...this.lore];
    c.enchantments = new Map(this.enchantments);
    return c;
  }
  getLore() {
    return [...this.lore];
  }
  setLore(lines) {
    this.lore = [...lines];
  }
  getComponent(id) {
    if (id === "minecraft:enchantable" || id === "enchantable") {
      const self = this;
      return {
        hasEnchantment: (t) => self.enchantments.has(String(t)),
        addEnchantment: (e) => {
          if (!e || typeof e !== "object") throw new Error("addEnchantment precisa de objeto");
          self.enchantments.set(String(e.type), e.level);
        },
        getEnchantment: (t) => self.enchantments.get(String(t)),
      };
    }
    return undefined;
  }
}

// --------------------------------------------------------------- Container
export class Container {
  constructor(size) {
    this.size = size;
    this.slots = new Array(size).fill(undefined);
  }
  getItem(i) {
    return this.slots[i];
  }
  setItem(i, it) {
    if (i < 0 || i >= this.size) throw new Error("slot invalido " + i);
    this.slots[i] = it;
  }
  addItem(it) {
    const livre = this.slots.findIndex((s) => s === undefined);
    if (livre === -1) return it;
    this.slots[livre] = it;
    return undefined;
  }
  find(typeId) {
    return this.slots.find((s) => s && s.typeId === typeId);
  }
}

// --------------------------------------------------------------- Entity
let entityId = 0;
export class Entity {
  constructor(typeId, dimension, location = { x: 0, y: 64, z: 0 }) {
    this.typeId = typeId;
    this.id = "e" + ++entityId;
    this.dimension = dimension;
    this.location = { ...location };
    this.isValid = true;
    this.effects = new Map();
    this.knockbacks = [];
    this.damages = [];
    this.nameTag = "";
  }
  getHeadLocation() {
    return { x: this.location.x, y: this.location.y + 1.6, z: this.location.z };
  }
  getViewDirection() {
    return { x: 0, y: 0, z: 1 };
  }
  getComponent() {
    return undefined;
  }
  addEffect(id, ticks, opts = {}) {
    if (!/^[a-z_]+$/.test(String(id).replace("minecraft:", ""))) {
      throw new Error("efeito invalido: " + id);
    }
    this.effects.set(String(id), { amplifier: opts.amplifier ?? 0, duration: ticks });
  }
  getEffect(id) {
    return this.effects.get(String(id));
  }
  removeEffect(id) {
    this.effects.delete(String(id));
  }
  applyDamage(amount, opts = {}) {
    if (typeof amount !== "number") throw new Error("dano invalido");
    this.damages.push({ amount, opts });
    world.afterEvents.entityHurt.trigger({
      hurtEntity: this,
      damage: amount,
      damageSource: { cause: opts?.cause ?? "none", damagingEntity: opts?.damagingEntity },
    });
    return true;
  }
  applyKnockback(a, b) {
    this.knockbacks.push([a, b]);
  }
  applyImpulse(v) {
    this.knockbacks.push(["impulse", v]);
  }
  teleport() {}
  runCommand() {
    return { successCount: 1 };
  }
  sendMessage() {}
}

// --------------------------------------------------------------- Player
export class Player extends Entity {
  constructor(name, dimension, location) {
    super("minecraft:player", dimension, location);
    this.name = name;
    this.nameTag = name;
    this.container = new Container(36);
    this.equipment = {
      [EquipmentSlot.Head]: undefined,
      [EquipmentSlot.Chest]: undefined,
      [EquipmentSlot.Legs]: undefined,
      [EquipmentSlot.Feet]: undefined,
      [EquipmentSlot.Mainhand]: undefined,
      [EquipmentSlot.Offhand]: undefined,
      [EquipmentSlot.Body]: undefined,
    };
    this.props = new Map();
    this.messages = [];
    this.actionbars = [];
    this.onScreenDisplay = {
      setActionBar: (t) => this.actionbars.push(t),
    };
  }
  getComponent(id) {
    if (id === EntityComponentTypes.Equippable || id === "equippable") {
      return {
        getEquipment: (slot) => this.equipment[slot],
        setEquipment: (slot, item) => {
          if (!(slot in this.equipment)) throw new Error("slot invalido " + slot);
          this.equipment[slot] = item;
        },
      };
    }
    if (id === EntityComponentTypes.Inventory || id === "inventory") {
      return { container: this.container };
    }
    return undefined;
  }
  sendMessage(t) {
    this.messages.push(t);
  }
  getDynamicProperty(k) {
    return this.props.get(k);
  }
  setDynamicProperty(k, v) {
    this.props.set(k, v);
  }
  runCommand(cmd) {
    this.commands = this.commands || [];
    this.commands.push(cmd);
    return { successCount: 1 };
  }
  runCommandAsync(cmd) {
    return Promise.resolve(this.runCommand(cmd));
  }
}

// --------------------------------------------------------------- Dimension
export class Dimension {
  constructor(id) {
    this.id = id;
    this.entities = [];
    this.particles = [];
    this.sounds = [];
    this.spawned = [];
  }
  getEntities(opts = {}) {
    let list = this.entities.filter((e) => e.isValid);
    if (opts.location) {
      list = list.filter(
        (e) =>
          Math.hypot(
            e.location.x - opts.location.x,
            e.location.y - opts.location.y,
            e.location.z - opts.location.z
          ) <= (opts.maxDistance ?? 100)
      );
    }
    if (opts.excludeNames) list = list.filter((e) => !opts.excludeNames.includes(e.name));
    if (opts.excludeTypes) list = list.filter((e) => !opts.excludeTypes.includes(e.typeId));
    return list;
  }
  getEntitiesFromRay() {
    return [];
  }
  getBlockFromRay(location, direction, opts = {}) {
    // simula um bloco a 5 blocos de distancia na direcao olhada
    const alcance = Math.min(5, opts.maxDistance ?? 5);
    return {
      block: { typeId: "minecraft:stone", location: { x: 0, y: 64, z: alcance } },
      face: "North",
      faceLocation: { x: 0, y: 64, z: alcance },
    };
  }
  spawnParticle(name, location) {
    if (!/^minecraft:[a-z_]+$/.test(name)) throw new Error("particula invalida " + name);
    this.particles.push({ name, location });
  }
  playSound(id, location, opts) {
    this.sounds.push({ id, location, opts });
  }
  spawnEntity(type, location) {
    if (!/^minecraft:[a-z_]+$/.test(type)) throw new Error("entidade invalida " + type);
    this.spawned.push({ type, location });
    return new Entity(type, this, location);
  }
  getWeather() {
    return "Clear";
  }
}

// --------------------------------------------------------------- events
class Signal {
  constructor(name) {
    this.name = name;
    this.handlers = [];
  }
  subscribe(fn) {
    this.handlers.push(fn);
    return fn;
  }
  unsubscribe(fn) {
    this.handlers = this.handlers.filter((h) => h !== fn);
  }
  trigger(ev) {
    for (const h of this.handlers) h(ev);
  }
}

const overworld = new Dimension("minecraft:overworld");
const players = [];
const props = new Map();

export const world = {
  afterEvents: {
    itemUse: new Signal("itemUse"),
    itemCompleteUse: new Signal("itemCompleteUse"),
    entityHitEntity: new Signal("entityHitEntity"),
    entityHurt: new Signal("entityHurt"),
    entityDie: new Signal("entityDie"),
    playerSpawn: new Signal("playerSpawn"),
    entitySpawn: new Signal("entitySpawn"),
  },
  beforeEvents: {
    playerBreakBlock: new Signal("playerBreakBlock"),
  },
  getAllPlayers: () => players,
  getPlayers: () => players,
  getDimension: () => overworld,
  getEntity: (id) => {
    const all = [...players, ...overworld.entities];
    return all.find((e) => e.id === id);
  },
  sendMessage: (t) => {
    world.messages.push(t);
  },
  messages: [],
  setDynamicProperty: (k, v) => props.set(k, v),
  getDynamicProperty: (k) => props.get(k),
};

// --------------------------------------------------------------- system
const intervals = [];
const timeouts = [];
export const system = {
  currentTick: 0,
  runInterval: (fn, ticks) => {
    const h = { fn, ticks, last: 0, id: intervals.length };
    intervals.push(h);
    return h.id;
  },
  clearRun: (id) => {
    const h = intervals[id];
    if (h) h.fn = () => {};
  },
  runTimeout: (fn, ticks) => {
    timeouts.push({ fn, at: system.currentTick + (ticks ?? 1) });
    return timeouts.length;
  },
  clearTimeout: () => {},
  run: (fn) => {
    fn();
    return 0;
  },
  /** Avanca o tempo simulado, disparando intervals e timeouts. */
  advance(ticks) {
    for (let i = 0; i < ticks; i++) {
      system.currentTick++;
      for (const h of intervals) {
        if (system.currentTick - h.last >= h.ticks) {
          h.last = system.currentTick;
          h.fn();
        }
      }
      for (let j = timeouts.length - 1; j >= 0; j--) {
        if (timeouts[j].at <= system.currentTick) {
          const t = timeouts.splice(j, 1)[0];
          t.fn();
        }
      }
    }
  },
  intervals,
};

// --------------------------------------------------------------- helpers de teste
export const testkit = {
  reset() {
    players.length = 0;
    overworld.entities.length = 0;
    overworld.particles.length = 0;
    overworld.sounds.length = 0;
    overworld.spawned.length = 0;
    props.clear();
    world.messages.length = 0;
    log.erros.length = 0;
  },
  dimension: overworld,
  newPlayer(name, loc = { x: 0, y: 64, z: 0 }) {
    const p = new Player(name, overworld, loc);
    players.push(p);
    return p;
  },
  newEntity(typeId, loc = { x: 0, y: 64, z: 5 }) {
    const e = new Entity(typeId, overworld, loc);
    overworld.entities.push(e);
    return e;
  },
  item(typeId, amount = 1) {
    return new ItemStack(typeId, amount);
  },
};
