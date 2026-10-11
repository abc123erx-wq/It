import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { prepareMap } from "../js/map.js";
import { Simulation } from "../js/simulation.js";
import { getWeapon } from "../js/bo1data.js";

const rawMap = JSON.parse(await readFile(new URL("../data/map_theater.json", import.meta.url), "utf8"));
const map = prepareMap(rawMap);
const input = (seq = {}) => ({
  at: Date.now(), x: 0, y: 0, aim: 0, fire: false, sprint: false,
  interactHeld: false, slot: "primary",
  seq: { interact: 0, reload: 0, melee: 0, swap: 0, ...seq }
});

test("mapkit-style map compiles to rooms, doors, windows and collision geometry", () => {
  assert.equal(map.rooms.length, 12);
  assert.equal(map.doors.length, 17);
  assert.equal(map.windows.length, 14);
  assert.ok(map.colliders.length > 100);
  assert.ok(map.byId.has("palco"));
});

test("a run starts in round one with valid host-serializable state", () => {
  const sim = new Simulation(map, [{ uid: "solo-test", name: "Tester", color: "#7ec8ff" }], 1234);
  assert.equal(sim.world.status, "playing");
  assert.equal(sim.world.round, 1);
  assert.ok(sim.world.spawnLeft > 0);
  assert.equal(sim.world.players["solo-test"].weapons.primary.id, "m1911_zm");
  assert.doesNotThrow(() => JSON.stringify(sim.world));
});

test("a precise M1911 headshot can eliminate a round-one zombie and score points", () => {
  const sim = new Simulation(map, [{ uid: "shooter", name: "Shooter" }], 44);
  const p = sim.world.players.shooter;
  p.x = 0; p.y = 0; p.angle = 0; p.score = 500;
  const z = { id: "target", x: 100, y: 0, angle: Math.PI, hp: 70, maxHp: 70, radius: 15, alive: true, dog: false };
  sim.world.zombies = [z];
  sim.shoot(p);
  assert.equal(z.alive, false);
  assert.equal(p.kills, 1);
  assert.ok(p.score > 500);
});

test("interacting with a nearby door charges points and opens its barrier", () => {
  const sim = new Simulation(map, [{ uid: "buyer", name: "Buyer" }], 17);
  const p = sim.world.players.buyer;
  const door = map.doors.find((d) => d.id === "d_palco_plateia");
  p.x = door.center.x; p.y = door.center.y; p.score = 2000;
  sim.step(1 / 60, { buyer: input({ interact: 1 }), __local: input({ interact: 1 }) }, "buyer");
  assert.equal(sim.world.unlocked[door.id], true);
  assert.equal(p.score, 2000 - door.cost);
});

test("zombies breach the window, path around stage props and reach a stationary survivor", () => {
  const sim = new Simulation(map, [{ uid: "target", name: "Target" }], 23);
  const idle = input();
  for (let i = 0; i < 1800; i++) sim.step(1 / 60, { target: idle, __local: idle }, "target");
  assert.equal(sim.world.windows.w_palco_n, 0);
  assert.ok(sim.world.players.target.hp < 100);
});

test("an alive teammate holding interact can revive a downed player", () => {
  const sim = new Simulation(map, [
    { uid: "downed", name: "Downed" }, { uid: "helper", name: "Helper" }
  ], 21);
  const w = sim.world, downed = w.players.downed, helper = w.players.helper;
  downed.x = 0; downed.y = 0; downed.downed = true; downed.hp = 0; downed.downTimer = 20;
  helper.x = 24; helper.y = 0;
  w.spawnLeft = 0; w.zombies = [];
  const helpInput = input(); helpInput.interactHeld = true;
  for (let i = 0; i < 200; i++) sim.step(1 / 60, { downed: input(), helper: helpInput }, "helper");
  assert.equal(downed.downed, false);
  assert.ok(downed.hp > 0);
  assert.equal(helper.revives, 1);
});

test("Pack-a-Punch weapon IDs resolve to their upgraded stats", () => {
  const pap = getWeapon("m1911_upgraded_zm");
  assert.equal(pap?.name, "⚡ M1911");
  assert.equal(pap?.dmg, 90);
  assert.equal(pap?.pap, null);
});
