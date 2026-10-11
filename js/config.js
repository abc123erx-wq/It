// ============================================================
//  BO1 ZOMBIES: WEB  —  Configuração (Firebase)
//  Projeto: kaka-ca0ff
// ============================================================

export const FIREBASE_CONFIG = {
  apiKey:            "AIzaSyBAR6HwrGBmwUxVDvIVuGYar82Lozg1Sck",
  authDomain:        "kaka-ca0ff.firebaseapp.com",
  databaseURL:       "https://kaka-ca0ff-default-rtdb.firebaseio.com",
  projectId:         "kaka-ca0ff",
  storageBucket:     "kaka-ca0ff.firebasestorage.app",
  messagingSenderId: "803477967370",
  appId:             "1:803477967370:web:fc8b9614f3e319c8c205f3"
};

// Raiz usada dentro do Realtime Database. Troque se quiser isolar versões.
export const DB_ROOT = "bo1zweb";

// Versão do protocolo de rede. Salas com versões diferentes não se misturam.
export const NET_VERSION = 3;

export const GAME = {
  MAX_PLAYERS: 4,
  TICK_HZ: 60,           // simulação
  CLIENT_SEND_HZ: 20,    // estado do próprio jogador
  HOST_SEND_HZ: 15,      // snapshot do mundo
  HEARTBEAT_MS: 2500,
  STALE_MS: 9000,
  ROOM_CODE_LEN: 5
};
