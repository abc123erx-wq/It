// ============================================================================
//  Creative Squad - Itens Lendarios  |  passives.js
//  Habilidades que ficam "ligadas" enquanto o item esta no inventario,
//  equipado ou na mao.
// ============================================================================

import { world, system, EquipmentSlot } from "@minecraft/server";
import { CFG, ITEM, ENCHANTS, DP, NAMESPACE } from "./config.js";
import { LORE } from "./lore.js";
import * as U from "./util.js";

const BAD_OMEN_TICKS = 400;
const PASSIVE_TICKS = 100;

/** Roda a cada CFG.tickPassivo ticks: efeitos passivos de todos os jogadores. */
export function runPassives() {
  let players;
  try {
    players = world.getAllPlayers();
  } catch {
    return;
  }
  for (const player of players) {
    try {
      applyPassives(player);
    } catch {
      // um erro em um jogador nunca derruba o loop inteiro
    }
  }
}

function applyPassives(player) {
  if (!player?.isValid) return;

  const owned = U.ownedIds(player);
  const batata = owned.has(ITEM.batata);

  const cabeca = U.slotItem(player, EquipmentSlot.Head);
  const pes = U.slotItem(player, EquipmentSlot.Feet);
  const mao = U.heldItem(player);
  const off = U.slotItem(player, EquipmentSlot.Offhand);

  // ---- Batata do Bobo: Lentidao V permanente (mesmo sem estar na mao)
  if (batata) {
    U.keepEffect(player, "minecraft:slowness", PASSIVE_TICKS, CFG.batataSlowAmp, false);
  }

  // ---- Bota Lendaria: Velocidade III (anulada pela Batata do Bobo)
  if (pes?.typeId === ITEM.bota && !batata) {
    // duracao curta: se a bota sair (ou a batata entrar), o efeito cai rapido
    U.keepEffect(player, "minecraft:speed", 40, CFG.botaSpeedAmp, false);
  } else if (batata) {
    // a Batata do Bobo anula a velocidade da Bota Lendaria
    const atual = player.getEffect("minecraft:speed");
    if (atual && atual.amplifier === CFG.botaSpeedAmp) {
      U.clearEffect(player, "minecraft:speed");
    }
  }

  // ---- Capacetes dos Gemeos: vida extra + respiracao aquatica
  if (cabeca?.typeId === ITEM.capaceteBern || cabeca?.typeId === ITEM.capaceteChip) {
    U.keepEffect(player, "minecraft:health_boost", PASSIVE_TICKS * 2, CFG.capaceteVidaAmp, false);
    U.keepEffect(player, "minecraft:water_breathing", PASSIVE_TICKS * 2, 0, false);
  }

  // ---- Lampiao Lendario: invisibilidade infinita
  const lampiao = mao?.typeId === ITEM.lampiao || off?.typeId === ITEM.lampiao;
  if (lampiao) {
    U.keepEffect(player, "minecraft:invisibility", PASSIVE_TICKS, 0, false);
  }

  // ---- Pena Lendaria: levitacao enquanto segurar
  if (mao?.typeId === ITEM.pena || off?.typeId === ITEM.pena) {
    U.keepEffect(player, "minecraft:levitation", 60, CFG.penaLevAmp, false);
  }

  // ---- Espada do Cacador: mal pressagio permanente no portador
  if (mao?.typeId === ITEM.espada || off?.typeId === ITEM.espada) {
    U.keepEffect(player, "minecraft:bad_omen", BAD_OMEN_TICKS, 0, true);
  }

  // ---- Relogio Lendario: hora de voltar ao normal
  const fakeUntil = player.getDynamicProperty(DP.fakeUntil);
  if (typeof fakeUntil === "number" && fakeUntil > 0 && system.currentTick >= fakeUntil) {
    player.nameTag = player.name;
    player.setDynamicProperty(DP.fakeUntil, 0);
    player.setDynamicProperty(DP.fakeName, "");
    U.actionbar(player, "§8[§6CS§8] §7O disfarce do §6Relógio Lendário§7 acabou.");
  }
}

/**
 * Roda a cada CFG.tickLore ticks.
 * Aplica o lore (tooltip) e os encantamentos "de fabrica" nos itens lendarios
 * que ainda nao foram preparados.
 */
export function runItemSetup() {
  for (const player of world.getAllPlayers()) {
    try {
      setupPlayerItems(player);
    } catch {}
  }
}

function setupPlayerItems(player) {
  const container = U.playerContainer(player);
  for (const ref of U.allItemRefs(player)) {
    const item = ref.item;
    if (!item || !item.typeId.startsWith(NAMESPACE)) continue;

    let changed = false;

    // lore / tooltip
    try {
      const linhas = LORE[item.typeId];
      if (linhas && item.getLore().length === 0) {
        item.setLore(linhas);
        changed = true;
      }
    } catch {}

    // encantamentos fixos (ex.: Repulsao X da espada, Eficiencia/Fortuna da picareta)
    const enchList = ENCHANTS[item.typeId];
    if (enchList) {
      try {
        const comp = item.getComponent("minecraft:enchantable");
        if (comp) {
          for (const e of enchList) {
            if (applyEnchant(comp, e.type, e.level)) changed = true;
          }
        }
      } catch {}
    }

    if (!changed) continue;
    if (ref.kind === "inv") {
      try {
        container?.setItem(ref.slot, item);
      } catch {}
    } else {
      U.setSlotItem(player, ref.slot, item);
    }
  }
}

/**
 * Alguns nomes podem chegar com ou sem o namespace "minecraft:". Tentamos as
 * duas formas para funcionar em qualquer build do jogo.
 * Retorna true se o encantamento foi aplicado agora.
 */
function applyEnchant(comp, nome, nivel) {
  const variantes = nome.startsWith("minecraft:")
    ? [nome, nome.slice("minecraft:".length)]
    : [nome, "minecraft:" + nome];

  for (const v of variantes) {
    try {
      if (comp.hasEnchantment(v)) return false;
    } catch {}
  }
  for (const v of variantes) {
    try {
      comp.addEnchantment({ type: v, level: nivel });
      return true;
    } catch {}
  }
  return false;
}
