// ============================================================
//  KINO // ZOMBIES — aplicação, lobby online e loop do jogo
// ============================================================
import { Simulation, promptFor, neutralInput } from "./simulation.js";
import { GameView } from "./view.js";
import { InputController } from "./input.js";
import { createRoom, joinRoom, setRoomState, firebaseErrorMessage } from "./firebase.js";
import { getWeapon, PERKS } from "./bo1data.js";
import { PLAYER_COLORS, store, makeId, fmtNum, esc } from "./util.js";
import { prepareMap } from "./map.js";

const $ = (sel) => document.querySelector(sel);
const app = {
  map: null, mode: "home", session: null, sim: null, view: null, input: null,
  localUid: null, remoteWorld: null, inputCache: {}, latestPresence: {}, roomData: null,
  raf: 0, lastFrame: 0, lastHud: 0, lastHostSend: 0, lastPresenceSweep: 0,
  lastNoticeId: 0, lastRound: 0, lastWorldStatus: "", pauseOpen: false,
  roomUnsub: null, presenceUnsub: null, worldUnsub: null, inputUnsub: null,
  starting: false, gameEndedUI: false, toastTimer: 0,
  ui: {}
};

function cacheDom() {
  const ids = [
    "home-screen", "game-screen", "play-solo", "create-room", "join-room", "player-name", "room-code-input",
    "lobby-panel", "lobby-code", "lobby-count", "lobby-roster", "lobby-status", "ready-toggle", "start-online",
    "copy-code", "lobby-leave", "firebase-note", "game-canvas", "touch-controls", "game-mode-label",
    "room-online-badge", "room-code-badge", "round-number", "round-subtitle", "pause-open", "resume-game",
    "leave-game", "pause-overlay", "pause-round", "pause-kills", "pause-message", "scoreboard-open",
    "scoreboard-overlay", "scoreboard-list", "gameover-overlay", "final-round", "final-scoreboard",
    "play-again", "exit-home", "hud-player-dot", "hud-player-name", "hud-player-state", "hud-kills",
    "health-value", "health-fill", "score-value", "revive-indicator", "zombie-count", "effects-row",
    "game-squad", "game-notices", "round-banner", "interaction-prompt", "weapon-slot-label", "weapon-class",
    "weapon-name", "weapon-ammo", "weapon-reserve", "weapon-one", "weapon-two", "weapon-three", "perk-row", "ammo-dots",
    "help-open", "help-overlay", "help-close", "help-ok", "toast", "loading-overlay", "loading-title", "loading-text"
  ];
  for (const id of ids) app.ui[id] = document.getElementById(id);
}

function toast(message, type = "") {
  const node = app.ui.toast;
  node.textContent = String(message || "Algo deu errado.");
  node.className = `toast show${type ? ` ${type}` : ""}`;
  clearTimeout(app.toastTimer);
  app.toastTimer = setTimeout(() => node.classList.remove("show"), 4100);
}

function setLoading(show, title = "CONECTANDO", text = "Preparando o esquadrão…") {
  app.ui["loading-title"].textContent = title;
  app.ui["loading-text"].textContent = text;
  app.ui["loading-overlay"].classList.toggle("hidden", !show);
}

function savedName() { return store.get("name", "") || ""; }
function getOperatorName() {
  const input = app.ui["player-name"];
  const entered = (input.value || "").trim().replace(/[<>]/g, "").slice(0, 18);
  const name = entered || `Operador-${Math.floor(10 + Math.random() * 90)}`;
  input.value = name;
  store.set("name", name);
  return name;
}
function getColor() {
  let color = store.get("color", null);
  if (!PLAYER_COLORS.includes(color)) {
    color = PLAYER_COLORS[Math.floor(Math.random() * PLAYER_COLORS.length)]; store.set("color", color);
  }
  return color;
}

function normalizeList(value) {
  if (Array.isArray(value)) return value;
  if (!value || typeof value !== "object") return [];
  return Object.keys(value).sort((a, b) => Number(a) - Number(b)).map((key) => value[key]).filter((x) => x != null);
}
function normalizeWorld(world) {
  if (!world || typeof world !== "object") return null;
  world.zombies = normalizeList(world.zombies);
  world.powerups = normalizeList(world.powerups);
  world.traces = normalizeList(world.traces);
  world.notices = normalizeList(world.notices);
  world.players = world.players || {};
  for (const p of Object.values(world.players)) {
    if (p && !Array.isArray(p.perks)) p.perks = p.perks && typeof p.perks === "object" ? Object.values(p.perks) : [];
  }
  return world;
}

function setHomeVisible() {
  app.ui["home-screen"].classList.remove("hidden");
  app.ui["game-screen"].classList.add("hidden");
  document.body.classList.remove("in-game");
  app.ui["lobby-panel"].classList.add("hidden");
  app.ui["pause-overlay"].classList.add("hidden");
  app.ui["scoreboard-overlay"].classList.add("hidden");
  app.ui["gameover-overlay"].classList.add("hidden");
  app.ui["room-online-badge"].classList.add("hidden");
  app.mode = "home";
}

function startSolo() {
  if (!app.map) return toast("O mapa ainda está carregando.", "error");
  teardownGame();
  const localUid = store.get("solo-uid", null) || `solo-${makeId()}`;
  store.set("solo-uid", localUid);
  app.localUid = localUid;
  const roster = [{ uid: localUid, name: getOperatorName(), color: getColor() }];
  app.sim = new Simulation(app.map, roster);
  app.remoteWorld = null; app.mode = "solo"; app.session = null;
  enterGame(app.sim.world);
}

async function createOnlineRoom() {
  if (app.starting) return;
  app.starting = true; setLoading(true, "CRIANDO SALA", "Conectando ao Firebase Realtime Database…");
  try {
    const session = await createRoom(getOperatorName(), getColor());
    app.session = session; app.localUid = session.uid; app.mode = "lobby"; app.sim = null; app.remoteWorld = null;
    app.latestPresence = { [session.uid]: { uid: session.uid, name: session.name, color: session.color, ready: true, seen: Date.now() } };
    app.roomData = { owner: session.uid, state: "waiting", maxPlayers: 4, name: "Kino der Toten" };
    openLobby();
    toast("Sala criada. Compartilhe o código com seu esquadrão.");
  } catch (error) {
    console.error(error); toast(firebaseErrorMessage(error), "error");
  } finally { app.starting = false; setLoading(false); }
}

async function joinOnlineRoom() {
  if (app.starting) return;
  app.starting = true; setLoading(true, "ENTRANDO NA SALA", "Verificando o código e sincronizando…");
  try {
    const session = await joinRoom(app.ui["room-code-input"].value, getOperatorName(), getColor());
    app.session = session; app.localUid = session.uid; app.mode = "lobby"; app.sim = null; app.remoteWorld = null;
    app.latestPresence = { [session.uid]: { uid: session.uid, name: session.name, color: session.color, ready: false, seen: Date.now() } };
    app.roomData = { owner: null, state: "waiting", maxPlayers: 4, name: "Kino der Toten" };
    openLobby();
    toast(`Conectado à sala ${session.code}.`);
  } catch (error) {
    console.error(error); toast(firebaseErrorMessage(error), "error");
  } finally { app.starting = false; setLoading(false); }
}

function openLobby() {
  app.ui["lobby-panel"].classList.remove("hidden");
  app.ui["lobby-code"].textContent = app.session.code;
  app.ui["room-code-input"].value = "";
  app.ui["lobby-status"].textContent = app.session.isHost ? "Compartilhe o código. O host inicia quando todos estiverem prontos." : "Marque-se como pronto e aguarde o host.";
  app.ui["start-online"].classList.toggle("hidden", !app.session.isHost);
  app.ui["ready-toggle"].classList.toggle("hidden", app.session.isHost);
  app.roomUnsub = app.session.observeRoom((room) => onRoomChange(room), (error) => toast(firebaseErrorMessage(error), "error"));
  app.presenceUnsub = app.session.observePresence((presence) => onPresenceChange(presence), (error) => toast(firebaseErrorMessage(error), "error"));
  renderLobby();
  app.ui["lobby-panel"].scrollIntoView({ behavior: "smooth", block: "center" });
}

function onPresenceChange(presence) {
  app.latestPresence = presence || {};
  if (app.mode === "lobby") renderLobby();
  if (app.mode === "online-host" && app.sim) checkConnectedPlayers();
}

function onRoomChange(room) {
  app.roomData = room;
  if (!room) {
    if ((app.mode === "lobby" || app.mode === "online-client") && !app.starting) {
      toast("O host encerrou a sala.", "error");
      if (app.mode === "online-client") returnHome();
      else leaveLobby(false);
    }
    return;
  }
  if (app.mode === "lobby") {
    if (room.state === "closed") { toast("O host desconectou. A sala foi encerrada.", "error"); leaveLobby(false); return; }
    if (room.presence) app.latestPresence = room.presence;
    renderLobby();
    if (room.state === "playing" && !app.session.isHost && !app.starting) {
      const initial = normalizeWorld(room.world);
      if (initial) enterOnlineClient(initial);
    }
  }
}

function renderLobby() {
  if (!app.session || app.mode !== "lobby") return;
  const now = Date.now();
  const members = Object.entries(app.latestPresence || {})
    .filter(([, p]) => p && now - Number(p.seen || now) < 14000)
    .sort((a, b) => (a[0] === app.roomData?.owner ? -1 : b[0] === app.roomData?.owner ? 1 : String(a[1].name).localeCompare(String(b[1].name))));
  const readyCount = members.filter(([, p]) => p.ready).length;
  const allReady = members.length > 0 && readyCount === members.length;
  app.ui["lobby-count"].textContent = `${members.length} / 4`;
  app.ui["lobby-roster"].innerHTML = "";
  for (let i = 0; i < 4; i++) {
    const slot = document.createElement("div");
    if (members[i]) {
      const [uid, player] = members[i];
      const isHost = uid === app.roomData?.owner;
      slot.className = "roster-slot";
      const dot = document.createElement("span"); dot.className = "operator-dot"; dot.style.background = player.color || "#8cbad0";
      const name = document.createElement("b"); name.textContent = String(player.name || "Operador").slice(0, 18);
      const status = document.createElement("small"); status.textContent = isHost ? "HOST" : player.ready ? "PRONTO" : "AGUARDANDO";
      if (!isHost && !player.ready) status.style.color = "#9a8a68";
      slot.append(dot, name, status);
    } else {
      slot.className = "roster-slot empty"; slot.textContent = `+ AGUARDANDO OPERADOR ${String(i + 1).padStart(2, "0")}`;
    }
    app.ui["lobby-roster"].append(slot);
  }
  const mine = app.latestPresence?.[app.session.uid];
  const ready = !!mine?.ready;
  const readyButton = app.ui["ready-toggle"];
  readyButton.classList.toggle("is-ready", ready);
  readyButton.querySelector("span").textContent = ready ? "PRONTO ✓" : "MARCAR PRONTO";
  app.ui["start-online"].disabled = !app.session.isHost || !allReady || members.length > 4;
  app.ui["start-online"].querySelector("span").textContent = allReady ? "INICIAR PARTIDA" : `AGUARDANDO ${members.length - readyCount} OPERADOR${members.length - readyCount === 1 ? "" : "ES"}`;
  app.ui["lobby-status"].textContent = allReady
    ? "Esquadrão pronto. O host pode iniciar a partida."
    : `${readyCount} de ${members.length} operadores prontos • compartilhe o código para convidar.`;
}

async function toggleReady() {
  if (!app.session || app.session.isHost) return;
  const current = !!app.latestPresence?.[app.session.uid]?.ready;
  try { await app.session.setReady(!current); }
  catch (error) { toast(firebaseErrorMessage(error), "error"); }
}

async function startOnlineGame() {
  if (!app.session?.isHost || app.starting) return;
  const members = Object.entries(app.latestPresence || {}).filter(([, p]) => p && Date.now() - Number(p.seen || 0) < 14000);
  if (!members.length || members.some(([, p]) => !p.ready)) return toast("Todos os operadores precisam marcar PRONTO.", "error");
  app.starting = true; setLoading(true, "INICIANDO OPERAÇÃO", "Distribuindo munição e sincronizando a horda…");
  try {
    const roster = members.slice(0, 4).map(([uid, p]) => ({ uid, name: p.name, color: p.color }));
    const sim = new Simulation(app.map, roster);
    app.sim = sim; app.localUid = app.session.uid; app.remoteWorld = null; app.mode = "online-host";
    const world = JSON.parse(JSON.stringify(sim.world));
    await setRoomState(app.session, "playing", { world, startedAt: Date.now() });
    app.roomUnsub?.(); app.roomUnsub = null;
    enterGame(world);
    installHostListeners();
  } catch (error) {
    console.error(error); app.mode = "lobby"; toast(firebaseErrorMessage(error), "error");
  } finally { app.starting = false; setLoading(false); }
}

function installHostListeners() {
  if (!app.session) return;
  app.inputUnsub?.(); app.presenceUnsub?.();
  app.inputUnsub = app.session.observeInputs((inputs) => { app.inputCache = inputs || {}; }, (error) => toast(firebaseErrorMessage(error), "error"));
  app.presenceUnsub = app.session.observePresence((presence) => { app.latestPresence = presence || {}; checkConnectedPlayers(); }, (error) => toast(firebaseErrorMessage(error), "error"));
  app.session.unsubs.push(app.inputUnsub, app.presenceUnsub);
}

function checkConnectedPlayers() {
  if (!app.sim || app.mode !== "online-host") return;
  const now = Date.now();
  for (const p of Object.values(app.sim.world.players)) {
    const presence = app.latestPresence?.[p.uid];
    const connected = !!presence && now - Number(presence.seen || 0) < 14000;
    if (p.uid === app.localUid) { p.connected = true; continue; }
    if (p.connected && !connected) {
      p.connected = false; p.alive = false; p.downed = false; p.hp = 0;
      app.sim.addEvent(`${p.name} perdeu a conexão`, p.uid, "#f08c79");
    } else if (connected) p.connected = true;
  }
}

function enterOnlineClient(initialWorld) {
  if (!app.session || app.starting || app.mode !== "lobby") return;
  app.starting = true;
  app.mode = "online-client"; app.localUid = app.session.uid; app.remoteWorld = normalizeWorld(initialWorld); app.sim = null;
  app.roomUnsub?.(); app.roomUnsub = null;
  app.presenceUnsub?.(); app.presenceUnsub = null;
  enterGame(app.remoteWorld);
  app.worldUnsub?.();
  app.worldUnsub = app.session.observeWorld((world) => {
    const next = normalizeWorld(world);
    if (!next) {
      if (app.mode === "online-client") { toast("O host encerrou a operação.", "error"); returnHome(); }
      return;
    }
    app.remoteWorld = next;
    app.view?.setWorld(next);
  }, (error) => toast(firebaseErrorMessage(error), "error"));
  app.starting = false;
}

function enterGame(initialWorld) {
  app.ui["home-screen"].classList.add("hidden");
  app.ui["game-screen"].classList.remove("hidden");
  app.ui["lobby-panel"].classList.add("hidden");
  app.ui["pause-overlay"].classList.add("hidden");
  app.ui["scoreboard-overlay"].classList.add("hidden");
  app.ui["gameover-overlay"].classList.add("hidden");
  document.body.classList.add("in-game");
  app.pauseOpen = false; app.gameEndedUI = false; app.lastRound = 0; app.lastNoticeId = 0;
  const world = normalizeWorld(initialWorld);
  app.remoteWorld = world;
  app.view?.destroy();
  app.view = new GameView(app.ui["game-canvas"], app.map);
  app.view.setWorld(world);
  app.input?.destroy();
  app.input = new InputController(app.ui["game-canvas"], app.ui["touch-controls"], { onPause: togglePause });
  app.ui["game-mode-label"].textContent = app.mode === "solo" ? "SOLO • SOBREVIDA" : app.mode === "online-host" ? "CO-OP • HOST DA SALA" : "CO-OP • ONLINE";
  app.ui["room-online-badge"].classList.toggle("hidden", !app.session);
  app.ui["room-code-badge"].textContent = app.session?.code || "-----";
  app.ui["gameover-overlay"].classList.add("hidden");
  app.lastFrame = performance.now(); app.lastHud = 0; app.lastHostSend = 0;
  cancelAnimationFrame(app.raf);
  app.raf = requestAnimationFrame(gameFrame);
}

function gameFrame(now) {
  if (!app.view || !app.input) return;
  const dt = Math.min(0.05, Math.max(0, (now - (app.lastFrame || now)) / 1000));
  app.lastFrame = now;
  let world = app.mode === "online-client" ? app.remoteWorld : app.sim?.world;
  if (!world) { app.raf = requestAnimationFrame(gameFrame); return; }
  const player = world.players?.[app.localUid];
  let input = app.input.sample(player, app.view, world);
  if (app.pauseOpen) {
    input = neutralInput(player);
    input.aim = player?.angle || 0;
    input.seq = { ...app.input.seq };
  }
  input.at = Date.now();

  if (app.mode === "online-client") {
    app.session?.sendInput(input);
  } else if (app.sim && !(app.pauseOpen && app.mode === "solo")) {
    const inputMap = { ...(app.inputCache || {}), [app.localUid]: input, __local: input };
    app.sim.step(dt, inputMap, app.localUid);
    world = app.sim.world;
    app.remoteWorld = world;
    app.view.setWorld(world);
    if (app.mode === "online-host" && now - app.lastHostSend > 66) {
      app.lastHostSend = now;
      app.session?.sendWorld(JSON.parse(JSON.stringify(world)));
    }
    if (app.mode === "online-host" && now - app.lastPresenceSweep > 16000) {
      app.lastPresenceSweep = now;
      const live = new Set(Object.entries(app.latestPresence || {}).filter(([, p]) => Date.now() - Number(p?.seen || 0) < 14000).map(([uid]) => uid));
      app.session?.removeStalePresence(live).catch(() => {});
    }
  }
  app.view.render(app.localUid);
  if (now - app.lastHud > 90) { updateHud(app.remoteWorld || world); app.lastHud = now; }
  app.raf = requestAnimationFrame(gameFrame);
}

function updateHud(world) {
  if (!world) return;
  const p = world.players?.[app.localUid] || Object.values(world.players || {})[0];
  if (!p) return;
  const gun = p.weapons?.[p.selected] || null;
  const spec = gun ? getWeapon(gun.id) : null;
  app.ui["round-number"].textContent = String(world.round || 1).padStart(2, "0");
  app.ui["round-subtitle"].textContent = world.dogRound ? "CÃES DO INFERNO" : `${Math.max(0, (world.zombies?.length || 0) + (world.spawnLeft || 0))} HOSTIS`;
  app.ui["hud-player-name"].textContent = String(p.name || "OPERADOR").toUpperCase();
  app.ui["hud-player-dot"].style.background = p.color || "#80c8e1";
  app.ui["hud-player-state"].textContent = !p.alive ? "ELIMINADO" : p.downed ? "ABATIDO • PRECISA DE AJUDA" : (app.mode === "solo" ? "VIVO • KINO DER TOTEN" : "VIVO • ESQUADRÃO CO-OP");
  app.ui["hud-kills"].innerHTML = `${fmtNum(p.kills || 0)} <small>K</small>`;
  app.ui["health-value"].textContent = p.downed ? "0" : String(Math.max(0, Math.round(p.hp || 0)));
  app.ui["health-fill"].style.width = `${clamp((p.hp || 0) / (p.maxHp || 100) * 100, 0, 100)}%`;
  app.ui["health-fill"].style.background = p.downed ? "#dd596a" : p.hp < 40 ? "linear-gradient(90deg,#a6423e,#e17058)" : "linear-gradient(90deg,#a6423e,#e3b36b)";
  app.ui["score-value"].textContent = fmtNum(p.score || 0);
  app.ui["revive-indicator"].classList.toggle("hidden", !p.downed);
  app.ui["zombie-count"].textContent = String((world.zombies?.length || 0) + (world.spawnLeft || 0)).padStart(2, "0");
  app.ui["weapon-slot-label"].textContent = `${String(p.selected || "primary").toUpperCase()} [${p.selected === "secondary" ? "2" : p.selected === "tertiary" ? "3" : "1"}]`;
  app.ui["weapon-class"].textContent = spec?.kind?.toUpperCase() || "SEM ARMA";
  app.ui["weapon-name"].textContent = spec?.name?.toUpperCase() || "FACA";
  app.ui["weapon-ammo"].textContent = gun ? String(gun.clip ?? 0) : "∞";
  app.ui["weapon-reserve"].textContent = gun ? String(gun.reserve ?? 0) : "∞";
  app.ui["weapon-one"].classList.toggle("active", p.selected === "primary");
  app.ui["weapon-two"].classList.toggle("active", p.selected === "secondary");
  app.ui["weapon-one"].querySelector("small").textContent = p.weapons?.primary ? (getWeapon(p.weapons.primary.id)?.name || "ARMA").slice(0, 8).toUpperCase() : "VAZIO";
  app.ui["weapon-two"].querySelector("small").textContent = p.weapons?.secondary ? (getWeapon(p.weapons.secondary.id)?.name || "ARMA").slice(0, 8).toUpperCase() : "VAZIO";
  const tertiary = app.ui["weapon-three"];
  if (tertiary) {
    const hasMule = (p.perks || []).includes("specialty_twoprimaries");
    tertiary.classList.toggle("hidden", !hasMule);
    tertiary.classList.toggle("active", p.selected === "tertiary");
    tertiary.querySelector("small").textContent = p.weapons?.tertiary ? (getWeapon(p.weapons.tertiary.id)?.name || "ARMA").slice(0, 8).toUpperCase() : "VAZIO";
  }
  renderPerks(p);
  renderSquad(world, p);
  renderEffects(world);
  const prompt = promptFor(app.map, world, p);
  app.ui["interaction-prompt"].classList.toggle("hidden", !prompt);
  app.ui["interaction-prompt"].querySelector("span").textContent = prompt;
  renderAmmoDots(gun);
  renderNotices(world);
  if (Number(world.round) > app.lastRound) {
    app.lastRound = Number(world.round);
    showRoundBanner(world.round, world.dogRound);
  }
  if (world.status === "gameover" && !app.gameEndedUI) showGameOver(world);
  if (app.pauseOpen) {
    app.ui["pause-round"].textContent = String(world.round || 1).padStart(2, "0");
    app.ui["pause-kills"].textContent = fmtNum(p.kills || 0);
    app.ui["pause-message"].textContent = app.mode === "solo" ? "A partida está pausada." : "A sala online continua ativa para o esquadrão.";
  }
  if (!app.ui["scoreboard-overlay"].classList.contains("hidden")) renderScoreboard(world);
}

function renderAmmoDots(gun) {
  const parent = app.ui["ammo-dots"];
  const count = Math.min(10, Math.max(0, Number(gun?.clip) || 0));
  const signature = `${count}:${gun?.id || "none"}`;
  if (parent.dataset.signature === signature) return;
  parent.dataset.signature = signature;
  parent.innerHTML = Array.from({ length: count }, () => "<i></i>").join("");
}

function renderPerks(p) {
  const row = app.ui["perk-row"];
  const perks = Array.isArray(p.perks) ? p.perks : [];
  const signature = perks.join("|");
  if (row.dataset.signature === signature) return;
  row.dataset.signature = signature; row.innerHTML = "";
  for (const id of perks) {
    const perk = PERKS[id]; if (!perk) continue;
    const chip = document.createElement("div"); chip.className = "perk-chip"; chip.style.borderColor = `${perk.color}77`;
    chip.innerHTML = `<b style="color:${esc(perk.color)}">${esc(perk.short)}</b><small>${esc(perk.name.split(" ")[0].toUpperCase())}</small>`;
    row.append(chip);
  }
}

function renderSquad(world, local) {
  const root = app.ui["game-squad"];
  const players = Object.values(world.players || {}).filter((p) => p.uid !== app.localUid);
  const signature = players.map((p) => `${p.uid}:${p.score}:${p.alive}:${p.downed}`).join("|");
  if (root.dataset.signature === signature) return;
  root.dataset.signature = signature; root.innerHTML = "";
  for (const p of players.slice(0, 3)) {
    const row = document.createElement("div"); row.className = `squad-card${p.alive ? "" : " dead"}`;
    const dot = document.createElement("span"); dot.className = "operator-dot"; dot.style.background = p.color || "#aaa";
    const name = document.createElement("b"); name.textContent = String(p.name || "OPERADOR").toUpperCase().slice(0, 11);
    const score = document.createElement("small"); score.textContent = p.downed ? "DOWN" : fmtNum(p.score || 0);
    row.append(dot, name, score); root.append(row);
  }
}

function renderEffects(world) {
  const root = app.ui["effects-row"];
  const effects = world.effects || {};
  const active = [
    ["instaUntil", "INSTA", "red"], ["doubleUntil", "2×", ""], ["firesaleUntil", "SALE", "blue"]
  ].filter(([key]) => Number(effects[key] || 0) > Number(world.time || 0)).map(([key, label, cls]) => `${key}:${label}:${cls}`);
  const signature = active.join("|");
  if (root.dataset.signature === signature) return;
  root.dataset.signature = signature; root.innerHTML = active.map((item) => {
    const [, label, cls] = item.split(":"); return `<span class="effect-chip ${esc(cls)}">${esc(label)}</span>`;
  }).join("");
}

function renderNotices(world) {
  const root = app.ui["game-notices"];
  for (const n of (world.notices || [])) {
    const id = Number(n.id) || 0;
    if (id <= app.lastNoticeId) continue;
    app.lastNoticeId = Math.max(app.lastNoticeId, id);
    if (n.uid && n.uid !== app.localUid) continue;
    const el = document.createElement("div");
    const text = String(n.text || "");
    const important = /RODADA|INSTA-KILL|DOUBLE POINTS|NUKE|MAX AMMO|FIM DE JOGO|CÃES DO INFERNO/i.test(text);
    el.className = `game-notice${important ? " important" : ""}${/abatido|dano|eliminad/i.test(text) ? " danger" : ""}`;
    el.textContent = text; if (n.color) el.style.borderColor = n.color;
    root.append(el); setTimeout(() => el.remove(), 4700);
  }
}

function showRoundBanner(round, dogs) {
  const banner = app.ui["round-banner"];
  banner.innerHTML = `<small>RODADA</small><strong>${String(round).padStart(2, "0")}</strong><span>${dogs ? "CÃES DO INFERNO" : "PREPARE-SE"}</span>`;
  banner.classList.add("show");
  clearTimeout(banner._hideTimer); banner._hideTimer = setTimeout(() => banner.classList.remove("show"), 2400);
}

function scoreMarkup(world) {
  const list = Object.values(world.players || {}).sort((a, b) => (b.score || 0) - (a.score || 0));
  let html = `<div class="score-row header"><span>OPERADOR</span><span>ELIMINAÇÕES</span><span>REVIVES</span><span>PONTOS</span></div>`;
  for (const p of list) html += `<div class="score-row"><span class="score-name"><i style="background:${esc(p.color || "#aaa")}"></i>${esc(p.name || "OPERADOR")}${p.downed ? " • DOWN" : ""}</span><span class="score-num">${fmtNum(p.kills || 0)}</span><span class="score-num">${fmtNum(p.revives || 0)}</span><span class="score-num">${fmtNum(p.score || 0)}</span></div>`;
  return html;
}
function renderScoreboard(world) { app.ui["scoreboard-list"].innerHTML = scoreMarkup(world); }

function showGameOver(world) {
  app.gameEndedUI = true;
  app.ui["final-round"].textContent = String(world.round || 1).padStart(2, "0");
  app.ui["final-scoreboard"].innerHTML = scoreMarkup(world);
  const solo = app.mode === "solo";
  app.ui["play-again"].classList.toggle("hidden", !solo);
  app.ui["exit-home"].textContent = solo ? "VOLTAR AO MENU" : "SAIR DA PARTIDA";
  app.ui["gameover-overlay"].classList.remove("hidden");
}

function togglePause() {
  if (app.mode !== "solo" && app.mode !== "online-host" && app.mode !== "online-client") return;
  if (app.gameEndedUI) return;
  app.pauseOpen = !app.pauseOpen;
  app.ui["pause-overlay"].classList.toggle("hidden", !app.pauseOpen);
}

function openScoreboard(open = true) {
  if (!app.remoteWorld && !app.sim?.world) return;
  app.ui["scoreboard-overlay"].classList.toggle("hidden", !open);
  if (open) renderScoreboard(app.remoteWorld || app.sim?.world);
}

function teardownGame() {
  cancelAnimationFrame(app.raf); app.raf = 0;
  app.input?.destroy(); app.input = null;
  app.view?.destroy(); app.view = null;
  app.ui["pause-overlay"]?.classList.add("hidden");
  app.ui["scoreboard-overlay"]?.classList.add("hidden");
  app.ui["gameover-overlay"]?.classList.add("hidden");
  app.pauseOpen = false; app.gameEndedUI = false;
}

async function leaveLobby(notify = true) {
  const session = app.session;
  app.roomUnsub?.(); app.presenceUnsub?.(); app.roomUnsub = app.presenceUnsub = null;
  if (session) await session.close({ deleteRoom: session.isHost });
  app.session = null; app.roomData = null; app.latestPresence = {}; app.mode = "home";
  app.ui["lobby-panel"].classList.add("hidden");
  if (notify) toast("Você saiu da sala.");
}

async function returnHome() {
  teardownGame();
  const session = app.session;
  app.roomUnsub?.(); app.presenceUnsub?.(); app.worldUnsub?.(); app.inputUnsub?.();
  app.roomUnsub = app.presenceUnsub = app.worldUnsub = app.inputUnsub = null;
  if (session) await session.close({ deleteRoom: session.isHost });
  app.session = null; app.sim = null; app.remoteWorld = null; app.inputCache = {};
  setHomeVisible();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function bindUi() {
  app.ui["player-name"].value = savedName();
  app.ui["play-solo"].addEventListener("click", startSolo);
  app.ui["create-room"].addEventListener("click", createOnlineRoom);
  app.ui["join-room"].addEventListener("click", joinOnlineRoom);
  app.ui["room-code-input"].addEventListener("input", (e) => { e.target.value = e.target.value.toUpperCase().replace(/[^A-HJ-NP-Z2-9]/g, "").slice(0, 5); });
  app.ui["room-code-input"].addEventListener("keydown", (e) => { if (e.key === "Enter") joinOnlineRoom(); });
  app.ui["player-name"].addEventListener("keydown", (e) => { if (e.key === "Enter") app.ui["create-room"].click(); });
  app.ui["lobby-leave"].addEventListener("click", () => leaveLobby());
  app.ui["ready-toggle"].addEventListener("click", toggleReady);
  app.ui["start-online"].addEventListener("click", startOnlineGame);
  app.ui["copy-code"].addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(app.session.code); toast("Código copiado para a área de transferência."); }
    catch { toast(`Código da sala: ${app.session?.code || "-----"}`); }
  });
  app.ui["pause-open"].addEventListener("click", togglePause);
  app.ui["resume-game"].addEventListener("click", () => { app.pauseOpen = false; app.ui["pause-overlay"].classList.add("hidden"); });
  app.ui["leave-game"].addEventListener("click", returnHome);
  app.ui["scoreboard-open"].addEventListener("click", () => openScoreboard(app.ui["scoreboard-overlay"].classList.contains("hidden")));
  app.ui["exit-home"].addEventListener("click", returnHome);
  app.ui["play-again"].addEventListener("click", () => { returnHome().then(() => startSolo()); });
  app.ui["help-open"].addEventListener("click", () => app.ui["help-overlay"].classList.remove("hidden"));
  app.ui["help-close"].addEventListener("click", () => app.ui["help-overlay"].classList.add("hidden"));
  app.ui["help-ok"].addEventListener("click", () => app.ui["help-overlay"].classList.add("hidden"));
  app.ui["help-overlay"].addEventListener("click", (e) => { if (e.target === app.ui["help-overlay"]) app.ui["help-overlay"].classList.add("hidden"); });
  app.ui["scoreboard-overlay"].addEventListener("click", (e) => { if (e.target === app.ui["scoreboard-overlay"]) openScoreboard(false); });
  window.addEventListener("keydown", (e) => {
    if (e.key === "Tab" && app.input) openScoreboard(true);
  });
  window.addEventListener("keyup", (e) => { if (e.key === "Tab" && app.input) openScoreboard(false); });
  window.addEventListener("beforeunload", () => {
    if (app.session) app.session.close({ deleteRoom: app.session.isHost });
  });
}

async function boot() {
  cacheDom(); bindUi();
  try {
    const response = await fetch("./data/map_theater.json", { cache: "no-store" });
    if (!response.ok) throw new Error("O mapa não carregou.");
    app.map = prepareMap(await response.json());
    console.info(`Mapa ${app.map.displayName} pronto: ${app.map.rooms.length} salas, ${app.map.doors.length} portas, ${app.map.windows.length} janelas.`);
  } catch (error) {
    console.error(error); toast("Falha ao carregar o mapa. Rode o projeto por um servidor HTTP (npm start).", "error");
  }
}

boot();
