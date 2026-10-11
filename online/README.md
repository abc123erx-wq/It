# BO1 Zombies — Modo Online (hub web)

Modo online do jogo **Black Ops 1 Zombies** (o zip `bo1-zombies-decompiled-main.zip` da
release **Vlaude** deste repositório), construído sobre o **Firebase Realtime Database**
do projeto `kaka-ca0ff`.

![hub](../images/1.webp)

## O que o modo online faz

| Recurso | Descrição |
|---|---|
| **Identidade** | Apelido de operador + autenticação anônima do Firebase (com fallback local) |
| **Presença** | Lista de operadores online em tempo real (com heartbeat e `onDisconnect`) |
| **Salas** | Criar/entrar/sair de salas com código de convite de 6 caracteres (ex.: `K1NO7`) |
| **Pronto?** | Sistema de ready-up; o anfitrião inicia a partida quando o esquadrão está pronto |
| **Partida ao vivo** | Rodada, abates, baixas, pontos e status vivo/abatido de cada jogador — sincronizados em tempo real |
| **Eventos** | Feed de eventos da partida (início, rodadas, abates, derrubadas, revives, fim) |
| **Chat** | Chat global e chat da sala |
| **Ranking** | Placar histórico de todos os operadores (partidas, abates, baixas, melhor rodada, pontos) |
| **Convite** | Botão "Copiar convite" gera um link que abre o hub já na sala (`#sala=CODIGO`) |
| **Demo** | "Simular partida" gera eventos ao vivo para testar a sincronização entre abas/janelas |

## Como rodar

```bash
python3 online/serve.py          # http://localhost:8080
```

Ou qualquer servidor estático apontando para esta pasta. A página fala direto com o
Firebase — não há backend próprio.

> **Dica:** abra o hub em duas janelas/perfis diferentes, entre na mesma sala e clique em
> "SIMULAR PARTIDA (DEMO)" como anfitrião para ver a sincronização em tempo real.

## Firebase

Configuração em `js/config.js` (projeto `kaka-ca0ff`):

```js
const firebaseConfig = {
  apiKey: "AIzaSyBAR6HwrGBmwUxVDvIVuGYar82Lozg1Sck",
  authDomain: "kaka-ca0ff.firebaseapp.com",
  databaseURL: "https://kaka-ca0ff-default-rtdb.firebaseio.com",
  projectId: "kaka-ca0ff",
  storageBucket: "kaka-ca0ff.firebasestorage.app",
  messagingSenderId: "803477967370",
  appId: "1:803477967370:web:fc8b9614f3e319c8c205f3"
};
```

O SDK do Firebase (compat, empacotado com esbuild) está em `vendor/firebase-all.js` —
a página funciona sem CDN.

### Regras do Realtime Database

Se o hub mostrar `PERMISSION_DENIED`, publique as regras de `database.rules.json`
(Firebase Console → Realtime Database → Regras):

```json
{
  "rules": {
    "bo1z": {
      ".read": true,
      ".write": true,
      "players": { "$uid": { ".write": "auth != null ? auth.uid == $uid : true" } }
    }
  }
}
```

E ative **Sign-in method → Anônimo** em Authentication (recomendado).

## Estrutura de dados (`bo1z/…`)

```
bo1z/
  players/{uid}            nome, status, roomId, lastSeen, stats{matches,kills,downs,bestRound,points}
  rooms/{CODIGO}           code, name, map, mode, maxPlayers, hostId, hostName, status, match{round,...}
  rooms/{CODIGO}/players/{uid}   ready, isHost, state{alive,points,kills,downs}
  rooms/{CODIGO}/chat/{id}       mensagens da sala
  rooms/{CODIGO}/events/{id}     eventos da partida (match_start, round_start, kill, down, revive, game_over)
  chat/{id}                chat global
```

A mesma estrutura é usada pelo cliente dentro do jogo (`src/online/` + `mods/online/`).

## Integração com o jogo (BO1Zombies.exe)

O engine também fala com este banco (REST + SSE via WinHTTP):

1. Compile o jogo (CMake + Visual Studio, ver `README.md` da raiz).
2. Inicie com mods online:

```powershell
.\BO1Zombies.exe +set fs_b $R +set fs_h $R +set bo1_zombies 1 `
  +set fs_mods online +set online_name "SeuNick" +set online_room CODIGO
```

3. O mod `mods/online` publica presença, rodadas, abates e baixas na mesma sala do hub;
   o chat do jogo aparece no hub e vice-versa.

Comandos GSC disponíveis no jogo (`src/online/g_scr_online.cpp`):
`onlineconnect`, `onlinestatus`, `onlineroomcreate`, `onlineroomjoin`, `onlineroomleave`,
`onlinepushstate`, `onlineevent`, `onlinepoll`, `onlineeventget`, `onlinesay`,
`onlineroomcode`, `onlineroster`.

---

*Projeto de fã, não afiliado à Activision. O código decompilado serve fins de estudo/modding.*
