// ============================================================================
//  Creative Squad - Itens Lendarios  |  combat.js
//  Combate: Repulsao X da espada, cansaco do tridente, raio na tempestade,
//  vida compartilhada dos capacetes e heranca da espada.
// ============================================================================

import { world, system, EquipmentSlot } from "@minecraft/server";
import { CFG, ITEM, DP, PICARETA_PROIBIDOS, PREFIX } from "./config.js";
import * as U from "./util.js";

// ------------------------------------------------------------------ ataques
export function onEntityHitEntity(ev) {
  try {
    const atacante = ev.damagingEntity;
    const alvo = ev.hitEntity;
    if (!atacante || !alvo || atacante.typeId !== "minecraft:player") return;

    const mao = U.heldItem(atacante);

    // ---- Espada do Cacador: Repulsao X
    if (mao?.typeId === ITEM.espada) {
      const dx = alvo.location.x - atacante.location.x;
      const dz = alvo.location.z - atacante.location.z;
      U.knockback(alvo, dx, dz, 3.2, 0.5);
      U.particle(alvo.dimension, "minecraft:critical_hit", alvo.getHeadLocation());
      U.sound(alvo.dimension, "random.anvil_land", alvo.location, 0.5, 2);
    }

    // ---- Tridente Lendario: cansaco + raio na tempestade
    if (mao?.typeId === ITEM.tridente) {
      U.keepEffect(alvo, "minecraft:mining_fatigue", 200, 1, true);
      if (U.isThundering(atacante) && !U.onCooldown(atacante, "raio", CFG.cdTridenteRaio)) {
        U.startCooldown(atacante, "raio");
        U.lightning(alvo.dimension, alvo.location);
        U.tell(atacante, PREFIX + "§bO tridente invocou um raio!");
      }
    }
  } catch {}
}

// -------------------------------------------------------- vida compartilhada
let transferindo = false;

export function onEntityHurt(ev) {
  if (transferindo) return; // evita eco infinito entre os dois gemeos
  try {
    const vitima = ev.hurtEntity;
    if (!vitima || vitima.typeId !== "minecraft:player") return;
    if (ev.damageSource?.cause === "magic") return; // dano vindo da propria divisao

    const cabeca = U.slotItem(vitima, EquipmentSlot.Head);
    let outroId;
    if (cabeca?.typeId === ITEM.capaceteBern) outroId = ITEM.capaceteChip;
    else if (cabeca?.typeId === ITEM.capaceteChip) outroId = ITEM.capaceteBern;
    else return;

    // procura o outro portador do capacete (o "gemeo")
    for (const p of world.getAllPlayers()) {
      if (p.id === vitima.id) continue;
      if (U.slotItem(p, EquipmentSlot.Head)?.typeId !== outroId) continue;

      const transferido = Math.max(1, Math.round(ev.damage * 0.5));
      transferindo = true;
      try {
        U.hurt(p, transferido, undefined, "magic");
      } finally {
        transferindo = false;
      }
      U.particle(p.dimension, "minecraft:critical_hit", p.getHeadLocation());
      U.actionbar(
        p,
        `§dVida compartilhada§8: §c-${transferido} §8(${vitima.name})`
      );
      break;
    }
  } catch {}
}

// ------------------------------------------------------------ heranca da espada
export function onEntityDie(ev) {
  try {
    const vitima = ev.deadEntity;
    const matador = ev.damageSource?.damagingEntity;
    if (!vitima || vitima.typeId !== "minecraft:player") return;
    if (!matador || matador.typeId !== "minecraft:player") return;
    if (!U.isHolding(matador, ITEM.espada)) return;

    if (!U.removeOne(matador, ITEM.espada)) return;

    // guarda a heranca para entregar quando a vitima renascer
    try {
      world.setDynamicProperty(DP.herdouEspada + vitima.id, true);
    } catch {}

    U.tell(matador, PREFIX + `§cA espada foi selada em §f${vitima.name}§c...`);
    U.tell(vitima, PREFIX + "§cVocê foi morto pela Espada do Caçador. §fA espada agora é sua herança...");
    U.broadcast(
      PREFIX + `§c${vitima.name}§7 herdou a §6Espada do Caçador§7 de §f${matador.name}§7!`
    );
  } catch {}
}

/** Chamado no evento de renascimento. */
export function onPlayerSpawn(player, initialSpawn) {
  try {
    const key = DP.herdouEspada + player.id;
    if (!world.getDynamicProperty(key)) return;
    world.setDynamicProperty(key, false);
    U.give(player, ITEM.espada, 1);
    U.tell(player, PREFIX + "§6A Espada do Caçador voltou para as suas mãos.");
    U.sound(player.dimension, "random.levelup", player.location, 1, 1);
  } catch {}
  if (initialSpawn) {
    system.runTimeout(() => {
      U.tell(player, "§8§m                                        ");
      U.tell(player, "§6§lITENS LENDÁRIOS §8| §fCREATIVE SQUAD §7(26.52)");
      U.tell(player, "§7Digite §e/function cs/ajuda §7para ver todos os comandos.");
      U.tell(player, "§7Ou use §e/function cs/dar_todos §7para pegar tudo.");
      U.tell(player, "§8§m                                        ");
    }, 60);
  }
}

// ------------------------------------------------------- picareta lendaria
export function onBeforePlayerBreakBlock(ev) {
  try {
    const player = ev.player;
    if (!player) return;
    if (U.heldItem(player)?.typeId !== ITEM.picareta) return;
    const id = ev.block?.typeId;
    if (!id || !PICARETA_PROIBIDOS.includes(id)) return;

    ev.cancel = true;
    system.run(() => {
      U.actionbar(player, "§cA Picareta Lendária não consegue minerar " + id.replace("minecraft:", "") + "!");
      U.sound(player.dimension, "note.bass", player.location, 0.7, 0.8);
    });
  } catch {}
}
