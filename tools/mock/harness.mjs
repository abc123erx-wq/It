// ============================================================================
//  Teste de fumaca dos scripts do addon usando o mock da API.
//  Roda com: bash tools/mock_test.sh
// ============================================================================

import { world, system, testkit, log, EquipmentSlot } from "@minecraft/server";
import "./scripts/main.mjs";

const R = { ok: 0, falhas: [] };
function check(nome, cond, extra = "") {
  if (cond) {
    R.ok++;
  } else {
    R.falhas.push(nome + (extra ? " -> " + extra : ""));
  }
}

function novoJogador(nome, loc) {
  const p = testkit.newPlayer(nome, loc);
  world.afterEvents.playerSpawn.trigger({ player: p, initialSpawn: true });
  return p;
}

const IDS = {
  espada: "cs:espada_do_cacador",
  batata: "cs:batata_do_bobo",
  bota: "cs:bota_lendaria",
  bern: "cs:capacete_gemeo_bern",
  chip: "cs:capacete_gemeo_chip",
  dragao: "cs:dragao_lendario",
  escudo: "cs:escudo_lendario",
  bussola: "cs:bussola_lendaria",
  lampiao: "cs:lampiao_lendario",
  pena: "cs:pena_lendaria",
  picareta: "cs:picareta_lendaria",
  pocao: "cs:pocao_lendaria",
  relogio: "cs:relogio_lendario",
  tridente: "cs:tridente_lendario",
};

function equipar(p, slot, typeId) {
  p.getComponent("minecraft:equippable").setEquipment(slot, testkit.item(typeId));
}

// ---------------------------------------------------------------- 1. carregou
{
  testkit.reset();
  system.advance(60);
  check("addon anunciou no chat", world.messages.some((m) => m.includes("carregado")), world.messages.join(" | "));
}

// ---------------------------------------------------------------- 2. passivos
{
  testkit.reset();
  const p = novoJogador("Mendrake");
  equipar(p, EquipmentSlot.Head, IDS.bern);
  equipar(p, EquipmentSlot.Feet, IDS.bota);
  system.advance(20);

  check("capacete da vida extra", !!p.getEffect("minecraft:health_boost"));
  check("capacete da respiracao aquatica", !!p.getEffect("minecraft:water_breathing"));
  check("bota da velocidade III", p.getEffect("minecraft:speed")?.amplifier === 2);

  // batata anula a bota
  p.container.addItem(testkit.item(IDS.batata));
  system.advance(20);
  const speed = p.getEffect("minecraft:speed");
  check("batata aplica lentidao V", p.getEffect("minecraft:slowness")?.amplifier === 4);
  check("batata anula a bota", !speed, JSON.stringify(speed));

  // lampiao / pena / espada na mao
  equipar(p, EquipmentSlot.Mainhand, IDS.lampiao);
  system.advance(20);
  check("lampiao da invisibilidade", !!p.getEffect("minecraft:invisibility"));

  equipar(p, EquipmentSlot.Mainhand, IDS.pena);
  system.advance(60);
  check("pena da levitacao", !!p.getEffect("minecraft:levitation"));

  equipar(p, EquipmentSlot.Mainhand, IDS.espada);
  system.advance(60);
  check("espada da mau pressagio", !!p.getEffect("minecraft:bad_omen"));
  check("espada recebeu lore", p.equipment[EquipmentSlot.Mainhand].getLore().length > 0);
  check(
    "espada recebeu repulsao X",
    p.equipment[EquipmentSlot.Mainhand].enchantments.get("knockback") === 10,
    JSON.stringify([...p.equipment[EquipmentSlot.Mainhand].enchantments])
  );

  // picareta recebe eficiencia e fortuna
  equipar(p, EquipmentSlot.Mainhand, IDS.picareta);
  system.advance(120);
  const ench = p.equipment[EquipmentSlot.Mainhand].enchantments;
  check("picareta recebeu eficiencia V", ench.get("efficiency") === 5, JSON.stringify([...ench]));
  check("picareta recebeu fortuna III", ench.get("fortune") === 3, JSON.stringify([...ench]));
}

// ---------------------------------------------------------------- 3. dragao
{
  testkit.reset();
  const p = novoJogador("Caduxinn");
  const alvo = testkit.newEntity("minecraft:pig", { x: 0, y: 64, z: 4 });
  equipar(p, EquipmentSlot.Mainhand, IDS.dragao);
  system.advance(2);

  world.afterEvents.itemUse.trigger({
    source: p,
    itemStack: p.equipment[EquipmentSlot.Mainhand],
  });
  check("bafo do dragao causou dano", alvo.damages.length > 0);
  check("bafo do dragao envenenou", !!alvo.getEffect("minecraft:poison"));
  check("bafo do dragao soltou particulas", testkit.dimension.particles.length > 0);

  // cooldown: segundo uso nao deve causar mais dano
  const antes = alvo.damages.length;
  world.afterEvents.itemUse.trigger({ source: p, itemStack: p.equipment[EquipmentSlot.Mainhand] });
  check("bafo do dragao respeita recarga", alvo.damages.length === antes);
}

// ---------------------------------------------------------------- 4. escudo
{
  testkit.reset();
  const p = novoJogador("MucaHD");
  const alvo = testkit.newEntity("minecraft:zombie", { x: 0, y: 64, z: 6 });
  equipar(p, EquipmentSlot.Mainhand, IDS.escudo);

  world.afterEvents.itemUse.trigger({ source: p, itemStack: p.equipment[EquipmentSlot.Mainhand] });
  check("rajada sonica causou dano", alvo.damages.length === 1);
  check("rajada sonica cegou", !!alvo.getEffect("minecraft:blindness"));
  check("rajada sonica empurrou", alvo.knockbacks.length > 0);
}

// ---------------------------------------------------------------- 5. pocao
{
  testkit.reset();
  const p = novoJogador("Fixz");
  const alvo = testkit.newEntity("minecraft:cow", { x: 0, y: 64, z: 3 });
  equipar(p, EquipmentSlot.Mainhand, IDS.pocao);

  world.afterEvents.itemUse.trigger({ source: p, itemStack: p.equipment[EquipmentSlot.Mainhand] });
  check("pocao cegou o alvo", !!alvo.getEffect("minecraft:blindness"));
  check("pocao nao foi consumida", p.equipment[EquipmentSlot.Mainhand]?.amount === 1);
}

// ---------------------------------------------------------------- 6. bussola
{
  testkit.reset();
  const p = novoJogador("Geleia");
  const outro = novoJogador("Tonigon", { x: 30, y: 64, z: 0 });
  equipar(p, EquipmentSlot.Mainhand, IDS.bussola);

  world.afterEvents.itemUse.trigger({ source: p, itemStack: p.equipment[EquipmentSlot.Mainhand] });
  check(
    "bussola aponta o jogador mais proximo",
    p.messages.some((m) => m.includes("Tonigon")),
    p.messages.join(" | ")
  );
  system.advance(40);
  check("bussola solta rastro de particulas", testkit.dimension.particles.length > 0);
  check("bussola nao altera a vida do alvo", outro.damages.length === 0);
}

// ---------------------------------------------------------------- 7. relogio
{
  testkit.reset();
  const p = novoJogador("Ligonz");
  novoJogador("Pedrux", { x: 10, y: 64, z: 0 });
  equipar(p, EquipmentSlot.Mainhand, IDS.relogio);

  world.afterEvents.itemUse.trigger({ source: p, itemStack: p.equipment[EquipmentSlot.Mainhand] });
  check("relogio copia o nick", p.nameTag === "Pedrux", p.nameTag);

  system.advance(1250);
  check("disfarce expira", p.nameTag === "Ligonz", p.nameTag);
}

// ---------------------------------------------------------------- 8. espada
{
  testkit.reset();
  const killer = novoJogador("Nait");
  const vitima = novoJogador("Mendrake", { x: 0, y: 64, z: 2 });
  equipar(killer, EquipmentSlot.Mainhand, IDS.espada);

  world.afterEvents.entityHitEntity.trigger({ damagingEntity: killer, hitEntity: vitima });
  check("espada empurra o alvo", vitima.knockbacks.length > 0);

  world.afterEvents.entityDie.trigger({
    deadEntity: vitima,
    damageSource: { cause: "entityAttack", damagingEntity: killer },
  });
  check("espada sai do matador", !killer.equipment[EquipmentSlot.Mainhand]);

  world.afterEvents.playerSpawn.trigger({ player: vitima, initialSpawn: false });
  const herdou =
    vitima.equipment[EquipmentSlot.Mainhand]?.typeId === IDS.espada ||
    vitima.container.find(IDS.espada) !== undefined ||
    vitima.commands?.some((c) => c.includes(IDS.espada));
  check("vitima herda a espada", herdou, JSON.stringify(vitima.commands || []));
}

// ---------------------------------------------------------------- 9. tridente
{
  testkit.reset();
  const p = novoJogador("Nait");
  const alvo = testkit.newEntity("minecraft:husk", { x: 0, y: 64, z: 2 });
  equipar(p, EquipmentSlot.Mainhand, IDS.tridente);
  world.afterEvents.entityHitEntity.trigger({ damagingEntity: p, hitEntity: alvo });
  check("tridente aplica cansaco", !!alvo.getEffect("minecraft:mining_fatigue"));
}

// ---------------------------------------------------------------- 10. gemeos
{
  testkit.reset();
  const bern = novoJogador("Bern");
  const chip = novoJogador("Chip");
  equipar(bern, EquipmentSlot.Head, IDS.bern);
  equipar(chip, EquipmentSlot.Head, IDS.chip);
  chip.applyDamage(6, { cause: "entityAttack" });
  check("vida compartilhada machuca o gemeo", bern.damages.length > 0, JSON.stringify(bern.damages));
  check("vida compartilhada nao entra em eco", bern.damages.length === 1 && chip.damages.length === 1,
    JSON.stringify([bern.damages.length, chip.damages.length]));
}

// ---------------------------------------------------------------- 11. picareta
{
  testkit.reset();
  const p = novoJogador("Pedrux");
  equipar(p, EquipmentSlot.Mainhand, IDS.picareta);
  const ev = {
    player: p,
    block: { typeId: "minecraft:obsidian" },
    cancel: false,
  };
  world.beforeEvents.playerBreakBlock.trigger(ev);
  check("picareta nao quebra obsidiana", ev.cancel === true);

  const ev2 = { player: p, block: { typeId: "minecraft:stone" }, cancel: false };
  world.beforeEvents.playerBreakBlock.trigger(ev2);
  check("picareta quebra pedra normalmente", ev2.cancel === false);
}

// ---------------------------------------------------------------- 12. batata
{
  testkit.reset();
  const p = novoJogador("Caduxinn");
  world.afterEvents.itemCompleteUse.trigger({ source: p, itemStack: testkit.item(IDS.batata) });
  check("comer a batata da veneno", !!p.getEffect("minecraft:poison"));
  system.advance(10);
  check(
    "batata volta para o inventario",
    !!p.container.find(IDS.batata) || p.commands?.some((c) => c.includes(IDS.batata))
  );
}

// ---------------------------------------------------------------- 13. sem erros
check("nenhum erro interno nos scripts", log.erros.length === 0, log.erros.slice(0, 3).join("\n---\n"));

// ---------------------------------------------------------------- relatorio
console.log(`\nTestes OK: ${R.ok}`);
if (R.falhas.length) {
  console.log(`FALHAS (${R.falhas.length}):`);
  for (const f of R.falhas) console.log("  x " + f);
  process.exit(1);
}
console.log("Todos os testes de fumaca passaram.");
