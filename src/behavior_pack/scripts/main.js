// ============================================================================
//  Creative Squad - Itens Lendarios
//  Addon para Minecraft Bedrock 26.52 (1.26.52)
//  Ponto de entrada dos scripts (module @minecraft/server 2.0.0)
//
//  Estrutura:
//    config.js    -> identificadores, recargas e balanceamento
//    lore.js      -> tooltips (gerado por tools/gen_content.py)
//    util.js      -> helpers (equipamento, efeitos, raios, cooldowns)
//    passives.js  -> habilidades continuas (bota, capacete, lampiao, pena...)
//    abilities.js -> habilidades ativadas no uso
//    combat.js    -> repulsao, cansaco, raio, vida compartilhada, heranca
// ============================================================================

import { world, system } from "@minecraft/server";
import { CFG } from "./config.js";
import * as U from "./util.js";
import * as Passives from "./passives.js";
import * as Abilities from "./abilities.js";
import * as Combat from "./combat.js";

const TAG = "§8[§6CS§8] ";

function safe(name, fn) {
  try {
    fn();
    return true;
  } catch (e) {
    U.log(`falha ao registrar ${name}: ${e}`);
    return false;
  }
}

// ------------------------------------------------------------- loops
safe("loop de passivos", () => {
  system.runInterval(() => {
    Passives.runPassives();
  }, CFG.tickPassivo);
});

safe("loop de lore/encantamentos", () => {
  system.runInterval(() => {
    Passives.runItemSetup();
  }, CFG.tickLore);
});

// ------------------------------------------------------------- eventos
safe("itemUse", () => {
  world.afterEvents.itemUse.subscribe((ev) => {
    try {
      Abilities.handleItemUse(ev.source, ev.itemStack);
    } catch {}
  });
});

safe("itemCompleteUse", () => {
  world.afterEvents.itemCompleteUse.subscribe((ev) => {
    try {
      Abilities.handleItemCompleteUse(ev.source, ev.itemStack);
    } catch {}
  });
});

safe("entityHitEntity", () => {
  world.afterEvents.entityHitEntity.subscribe((ev) => Combat.onEntityHitEntity(ev));
});

safe("entityHurt", () => {
  world.afterEvents.entityHurt.subscribe((ev) => Combat.onEntityHurt(ev));
});

safe("entityDie", () => {
  world.afterEvents.entityDie.subscribe((ev) => Combat.onEntityDie(ev));
});

safe("playerSpawn", () => {
  world.afterEvents.playerSpawn.subscribe((ev) => {
    Combat.onPlayerSpawn(ev.player, ev.initialSpawn);
  });
});

safe("playerBreakBlock (before)", () => {
  world.beforeEvents.playerBreakBlock.subscribe((ev) => Combat.onBeforePlayerBreakBlock(ev));
});

// ------------------------------------------------------------- aviso no console
system.runTimeout(() => {
  U.log("Itens Lendarios da Creative Squad carregados (Bedrock 26.52).");
  try {
    world.sendMessage(TAG + "§aAddon §6Itens Lendários da Creative Squad §acarregado!");
    world.sendMessage(TAG + "§7Use §e/function cs/ajuda §7para ver os comandos.");
  } catch {}
}, 40);

export { TAG };
