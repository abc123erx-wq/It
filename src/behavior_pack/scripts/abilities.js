// ============================================================================
//  Creative Squad - Itens Lendarios  |  abilities.js
//  Habilidades ativadas no uso (botao de usar / clique direito).
// ============================================================================

import { world, system, EquipmentSlot } from "@minecraft/server";
import { CFG, ITEM, DP } from "./config.js";
import * as U from "./util.js";

export function handleItemUse(player, item) {
  if (!player?.isValid || !item) return;
  switch (item.typeId) {
    case ITEM.dragao:
      bafoDoDragao(player);
      break;
    case ITEM.escudo:
      rajadaSonica(player);
      break;
    case ITEM.pocao:
      arremessarPocao(player);
      break;
    case ITEM.bussola:
      localizarJogador(player);
      break;
    case ITEM.relogio:
      disfarcar(player);
      break;
    default:
      break;
  }
}

// ---------------------------------------------------------------- Dragao
function bafoDoDragao(player) {
  if (U.onCooldown(player, "dragao", CFG.cdDragao)) {
    U.actionbar(
      player,
      `§5Dragão Lendário§8: §c${U.cooldownLeft(player, "dragao", CFG.cdDragao).toFixed(1)}s`
    );
    return;
  }
  U.startCooldown(player, "dragao");

  const dim = player.dimension;
  const head = player.getHeadLocation();
  const dir = U.normalize(player.getViewDirection());

  for (let i = 1; i <= 10; i++) {
    const pos = U.add(head, U.scale(dir, i * 0.9));
    U.particle(dim, "minecraft:dragon_breath_trail", pos);
    if (i % 3 === 0) U.particle(dim, "minecraft:dragon_breath_lingering", pos);
  }
  U.sound(dim, "mob.enderdragon.growl", head, 1.2, 0.9);

  for (const alvo of U.entitiesInCone(player, 10, 32)) {
    U.hurt(alvo, 8, player);
    U.keepEffect(alvo, "minecraft:poison", 120, 1, true);
  }
  U.actionbar(player, "§5§lBAFO DO DRAGÃO");
}

// ---------------------------------------------------------------- Escudo
function rajadaSonica(player) {
  if (U.onCooldown(player, "escudo", CFG.cdEscudo)) {
    U.actionbar(
      player,
      `§bEscudo Lendário§8: §c${U.cooldownLeft(player, "escudo", CFG.cdEscudo).toFixed(1)}s`
    );
    return;
  }
  U.startCooldown(player, "escudo");

  const dim = player.dimension;
  const head = player.getHeadLocation();
  const dir = U.normalize(player.getViewDirection());

  for (let i = 1; i <= 16; i++) {
    U.particle(dim, "minecraft:sonic_explosion", U.add(head, U.scale(dir, i)));
  }
  U.sound(dim, "mob.warden.sonic_boom", head, 1.5, 1);

  for (const alvo of U.entitiesInCone(player, 16, 20)) {
    U.hurt(alvo, 12, player);
    const loc = alvo.location;
    U.knockback(alvo, loc.x - player.location.x, loc.z - player.location.z, 2.6, 0.6);
    U.keepEffect(alvo, "minecraft:blindness", 100, 0, true);
  }
  U.actionbar(player, "§3§lRAJADA SÔNICA");
}

// ---------------------------------------------------------------- Pocao
function arremessarPocao(player) {
  if (U.onCooldown(player, "pocao", CFG.cdPocao)) return;
  U.startCooldown(player, "pocao");

  const dim = player.dimension;
  const raio = U.rayBlock(player, 22);
  let impacto = raio.hit
    ? { x: raio.location.x + 0.5, y: raio.location.y + 0.5, z: raio.location.z + 0.5 }
    : raio.location;

  // trajetoria da pocao
  const head = player.getHeadLocation();
  const dir = U.normalize(player.getViewDirection());
  const dist = U.distance(head, impacto);
  for (let i = 1; i <= Math.max(2, Math.floor(dist)); i++) {
    U.particle(dim, "minecraft:splashpotionspell", U.add(head, U.scale(dir, i)));
  }

  U.particle(dim, "minecraft:splashpotionspell", impacto);
  U.particle(dim, "minecraft:witchspell", impacto);
  U.sound(dim, "random.glass", impacto, 1, 1);

  let atingidos = 0;
  try {
    for (const alvo of dim.getEntities({ location: impacto, maxDistance: 5 })) {
      if (!alvo || alvo.id === player.id) continue;
      if (alvo.typeId === "minecraft:item" || alvo.typeId === "minecraft:xp_orb") continue;
      U.keepEffect(alvo, "minecraft:blindness", 300, 1, true);
      U.hurt(alvo, 1, player, "magic");
      atingidos++;
    }
  } catch {}

  U.actionbar(
    player,
    atingidos > 0
      ? `§dPoção Lendária§8: §a${atingidos} alvo(s) cegado(s)`
      : "§dPoção Lendária§8: §7ninguém foi atingido"
  );
}

// ---------------------------------------------------------------- Bussola
function localizarJogador(player) {
  if (U.onCooldown(player, "bussola", CFG.cdBussola)) {
    U.actionbar(player, "§cAguarde para usar a Bússola Lendária novamente.");
    return;
  }
  U.startCooldown(player, "bussola");

  const near = U.nearestPlayer(player, 512);
  if (!near) {
    U.tell(player, "§8[§6CS§8] §7A bússola não encontrou ninguém online.");
    return;
  }
  const alvo = near.player;
  const dist = Math.round(near.distance);
  const dir = U.directionName(player.location, alvo.location);

  U.tell(
    player,
    `§8[§6CS§8] §b${alvo.name}§7 está a §e${dist} blocos§7 ao §e${dir}§7 ` +
      `§8(${Math.round(alvo.location.x)}, ${Math.round(alvo.location.y)}, ${Math.round(alvo.location.z)})`
  );
  U.actionbar(player, `§b${alvo.name} §8• §e${dist}m §8• §e${dir}`);

  // rastro de particulas: revela o alvo mesmo invisivel (o efeito "glowing"
  // nao existe no Bedrock, entao usamos um marcador visual de 8 segundos)
  U.sound(player.dimension, "random.orb", player.location, 0.6, 1.6);
  const alvoId = alvo.id;
  for (let i = 0; i < 20; i++) {
    system.runTimeout(() => {
      try {
        const alvoAtual = world.getEntity(alvoId);
        if (!alvoAtual || !alvoAtual.isValid) return;
        const p = alvoAtual.location;
        U.particle(alvoAtual.dimension, "minecraft:endrod", { x: p.x, y: p.y + 2.2, z: p.z });
        U.particle(alvoAtual.dimension, "minecraft:sculk_soul", { x: p.x, y: p.y + 1.4, z: p.z });
      } catch {}
    }, i * 8);
  }
}

// ---------------------------------------------------------------- Relogio
function disfarcar(player) {
  if (U.onCooldown(player, "relogio", CFG.cdRelogio)) {
    U.actionbar(
      player,
      `§6Relógio Lendário§8: §c${Math.ceil(U.cooldownLeft(player, "relogio", CFG.cdRelogio))}s`
    );
    return;
  }
  const near = U.nearestPlayer(player, 256);
  if (!near) {
    U.tell(player, "§8[§6CS§8] §7Não há outro jogador online para copiar.");
    return;
  }
  U.startCooldown(player, "relogio");

  const alvo = near.player;
  player.setDynamicProperty(DP.fakeName, alvo.name);
  player.setDynamicProperty(DP.fakeUntil, system.currentTick + CFG.relogioDuracao);
  player.nameTag = alvo.name;

  U.sound(player.dimension, "random.orb", player.location, 1, 0.7);
  U.tell(
    player,
    `§8[§6CS§8] §6Você agora é §f${alvo.name}§6 por 60 segundos. §8(Nick copiado — a skin não muda no Bedrock)`
  );
  U.actionbar(player, `§6Disfarçado de §f${alvo.name}`);
}

// ---------------------------------------------------------------- Batata (comer)
export function handleItemCompleteUse(player, item) {
  if (item?.typeId !== ITEM.batata) return;
  U.keepEffect(player, "minecraft:poison", 120, 1, true);
  U.keepEffect(player, "minecraft:slowness", 240, CFG.batataSlowAmp, false);
  U.keepEffect(player, "minecraft:nausea", 200, 0, true);
  U.tell(player, "§8[§6CS§8] §2Você comeu a Batata do Bobo... §7que nojo. §8(ela voltou para o seu inventário)");
  // a batata e' "indestrutivel" no servidor: volta para o inventario
  system.runTimeout(() => {
    try {
      U.give(player, ITEM.batata, 1);
    } catch {}
  }, 3);
}
