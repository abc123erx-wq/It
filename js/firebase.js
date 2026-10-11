// ============================================================
// Firebase Auth anônima + Realtime Database
// SDK modular 10.12.5, servido localmente (sem dependência de CDN).
// ============================================================
import { FIREBASE_CONFIG, DB_ROOT, NET_VERSION, GAME } from "./config.js";
import { initializeApp, getApps } from "../vendor/firebase/firebase-app.js";
import { getAuth, signInAnonymously, onAuthStateChanged } from "../vendor/firebase/firebase-auth.js";
import {
  getDatabase, ref, get, set, update, remove, onValue, onDisconnect, serverTimestamp
} from "../vendor/firebase/firebase-database.js";

let app;
let auth;
let db;
let authReady;

export function firebaseAvailable() {
  return typeof window !== "undefined" && typeof navigator !== "undefined" && navigator.onLine;
}

export async function connectFirebase() {
  if (!app) app = getApps().length ? getApps()[0] : initializeApp(FIREBASE_CONFIG);
  if (!auth) auth = getAuth(app);
  if (!db) db = getDatabase(app);
  if (!authReady) {
    authReady = new Promise((resolve, reject) => {
      let unsub = () => {};
      unsub = onAuthStateChanged(auth, async (user) => {
        unsub();
        try {
          if (user) resolve(user);
          else {
            const credential = await signInAnonymously(auth);
            resolve(credential.user);
          }
        } catch (error) { reject(error); }
      }, reject);
    });
  }
  return { user: await authReady, db };
}

export function firebaseErrorMessage(error) {
  const code = String(error?.code || "");
  if (code.includes("operation-not-allowed")) return "Ative o provedor de login Anônimo em Firebase → Authentication → Sign-in method.";
  if (code.includes("permission-denied") || code.includes("PERMISSION_DENIED")) return "O Realtime Database recusou o acesso. Publique as regras de database.rules.json e confira se o Anonymous Auth está ativado.";
  if (code.includes("network") || code.includes("unavailable")) return "Sem conexão com Firebase. Verifique a internet e tente novamente.";
  if (code.includes("api-key-not-valid")) return "A chave Firebase não foi aceita. Confira a configuração em js/config.js.";
  return error?.message || "Não foi possível conectar ao Firebase.";
}

const roomPath = (code) => `${DB_ROOT}/rooms/${String(code).toUpperCase()}`;

export class RoomSession {
  constructor(dbInstance, user, code, isHost, name, color) {
    this.db = dbInstance;
    this.user = user;
    this.uid = user.uid;
    this.code = String(code).toUpperCase();
    this.isHost = isHost;
    this.name = name;
    this.color = color;
    this.root = ref(dbInstance, roomPath(this.code));
    this.selfPresence = ref(dbInstance, `${roomPath(this.code)}/presence/${this.uid}`);
    this.selfInput = ref(dbInstance, `${roomPath(this.code)}/inputs/${this.uid}`);
    this.unsubs = [];
    this.closed = false;
    this.lastInput = 0;
    this.heartbeat = 0;
  }

  async registerPresence() {
    await set(this.selfPresence, {
      uid: this.uid,
      name: this.name.slice(0, 18),
      color: this.color,
      ready: this.isHost,
      seen: serverTimestamp()
    });
    await onDisconnect(this.selfPresence).remove();
    await onDisconnect(this.selfInput).remove();
    if (this.isHost) await onDisconnect(ref(this.db, `${roomPath(this.code)}/state`)).set("closed");
    this.heartbeat = window.setInterval(() => {
      if (this.closed) return;
      set(this.selfPresence, {
        uid: this.uid, name: this.name.slice(0, 18), color: this.color,
        ready: this.ready ?? this.isHost, seen: serverTimestamp()
      }).catch(() => {});
    }, GAME.HEARTBEAT_MS);
  }

  async setReady(ready) {
    this.ready = !!ready;
    await update(this.selfPresence, { ready: this.ready, seen: serverTimestamp() });
  }

  observeRoom(callback, onError = () => {}) {
    const unsub = onValue(this.root, (snap) => callback(snap.exists() ? snap.val() : null), onError);
    this.unsubs.push(unsub);
    return unsub;
  }

  observePresence(callback, onError = () => {}) {
    const unsub = onValue(ref(this.db, `${roomPath(this.code)}/presence`), (snap) => callback(snap.val() || {}), onError);
    this.unsubs.push(unsub);
    return unsub;
  }

  observeInputs(callback, onError = () => {}) {
    const unsub = onValue(ref(this.db, `${roomPath(this.code)}/inputs`), (snap) => callback(snap.val() || {}), onError);
    this.unsubs.push(unsub);
    return unsub;
  }

  observeWorld(callback, onError = () => {}) {
    const unsub = onValue(ref(this.db, `${roomPath(this.code)}/world`), (snap) => callback(snap.val() || null), onError);
    this.unsubs.push(unsub);
    return unsub;
  }

  async sendInput(input, force = false) {
    if (this.closed) return;
    const now = performance.now();
    if (!force && now - this.lastInput < 42) return;
    this.lastInput = now;
    try { await set(this.selfInput, { ...input, at: serverTimestamp() }); }
    catch (error) { console.warn("input Firebase:", error); }
  }

  async sendWorld(world) {
    if (!this.isHost || this.closed) return;
    try { await set(ref(this.db, `${roomPath(this.code)}/world`), world); }
    catch (error) { console.warn("snapshot Firebase:", error); }
  }

  async updateRoom(data) {
    if (!this.isHost || this.closed) throw new Error("Só o host pode alterar a sala.");
    await update(this.root, data);
  }

  async removeStalePresence(liveUids) {
    if (!this.isHost || this.closed) return;
    const now = Date.now();
    const snap = await get(ref(this.db, `${roomPath(this.code)}/presence`));
    const presence = snap.val() || {};
    for (const [uid, p] of Object.entries(presence)) {
      if (!liveUids.has(uid) && now - Number(p?.seen || 0) > 14000) {
        remove(ref(this.db, `${roomPath(this.code)}/presence/${uid}`)).catch(() => {});
        remove(ref(this.db, `${roomPath(this.code)}/inputs/${uid}`)).catch(() => {});
      }
    }
  }

  async close({ deleteRoom = this.isHost } = {}) {
    if (this.closed) return;
    this.closed = true;
    if (this.heartbeat) clearInterval(this.heartbeat);
    for (const unsub of this.unsubs) { try { unsub(); } catch {} }
    this.unsubs.length = 0;
    if (deleteRoom && this.isHost) {
      try { await remove(this.root); } catch (error) { console.warn(error); }
    } else {
      try { await remove(this.selfInput); await remove(this.selfPresence); } catch (error) { console.warn(error); }
    }
  }
}

export async function createRoom(name, color) {
  const { db, user } = await connectFirebase();
  for (let tries = 0; tries < 6; tries++) {
    const code = makeCode();
    const target = ref(db, roomPath(code));
    const snap = await get(target);
    if (snap.exists()) continue;
    const room = {
      owner: user.uid,
      protocol: NET_VERSION,
      name: "Kino der Toten",
      mapId: "kino",
      state: "waiting",
      createdAt: Date.now(),
      maxPlayers: GAME.MAX_PLAYERS,
      settings: { difficulty: "normal" },
      presence: {}, inputs: {}, world: null
    };
    await set(target, room);
    const session = new RoomSession(db, user, code, true, name, color);
    await session.registerPresence();
    return session;
  }
  throw new Error("Não foi possível reservar um código de sala. Tente de novo.");
}

export async function joinRoom(code, name, color) {
  const { db, user } = await connectFirebase();
  const clean = String(code || "").toUpperCase().replace(/[^A-HJ-NP-Z2-9]/g, "").slice(0, 5);
  if (clean.length !== 5) throw new Error("Digite o código de 5 letras/números da sala.");
  const target = ref(db, roomPath(clean));
  const snap = await get(target);
  if (!snap.exists()) throw new Error("Sala não encontrada. Confira o código com o host.");
  const room = snap.val();
  if (room.protocol !== NET_VERSION) throw new Error("Essa sala usa outra versão do jogo. Atualize a página.");
  if (room.state !== "waiting") throw new Error("A partida já começou ou a sala foi encerrada.");
  const online = Object.values(room.presence || {}).filter((p) => Date.now() - Number(p?.seen || 0) < 14000).length;
  if (online >= (room.maxPlayers || GAME.MAX_PLAYERS)) throw new Error("A sala está cheia (máximo de 4 jogadores).");
  const session = new RoomSession(db, user, clean, false, name, color);
  await session.registerPresence();
  return session;
}

export async function setRoomState(session, state, extra = {}) {
  if (!session?.isHost) throw new Error("Só o host pode iniciar a partida.");
  await session.updateRoom({ state, updatedAt: Date.now(), ...extra });
}

export { serverTimestamp };

function makeCode() {
  const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  const bytes = new Uint8Array(5);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (b) => alphabet[b % alphabet.length]).join("");
}
