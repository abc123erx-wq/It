#pragma once
// ============================================================================
// MODO ONLINE (Firebase Realtime Database) — NÃO faz parte do jogo original.
//
// Cliente REST do Firebase para o modo online do BO1 Zombies. Substitui a nuvem
// DemonWare (morta) por salas/presença/chat/estado de partida no Realtime
// Database do projeto kaka-ca0ff — o MESMO banco usado pelo hub web em online/.
//
// Caminhos do banco (prefixo bo1z/):
//   bo1z/players/{uid}                 presença + estatísticas
//   bo1z/rooms/{CODIGO}                sala (host, mapa, modo, status, match)
//   bo1z/rooms/{CODIGO}/players/{uid}  pronto? + estado na partida
//   bo1z/rooms/{CODIGO}/chat/{id}      chat da sala
//   bo1z/rooms/{CODIGO}/events/{id}    eventos (round_start, kill, down, ...)
//
// Sem dependências do engine: só WinHTTP + C++ padrão. Chamado pelos builtins GSC
// de src/online/g_scr_online.cpp (onlineconnect, onlinepoll, ...).
// ============================================================================

// Inicializa o módulo (thread de rede). Idempotente.
void Online_Init();

// Encerra threads e limpa o estado. Chamar ao sair.
void Online_Shutdown();

// Identidade do jogador e conexão. "name" vira o apelido no hub web.
// Retorna 1 se a sessão foi iniciada (a conexão real é assíncrona).
int Online_Connect(const char *name);

// Estado atual: "off", "connecting", "online", "room:CODIGO", "erro: ...".
const char *Online_Status();

// 1 se conectado ao banco e autenticado (ou modo anônimo local).
int Online_IsOnline();

// Cria uma sala e entra nela. Retorna o código (ex.: "K1NO7") ou "" em erro.
// O código fica em Online_GetRoomCode(); sincrono (espera a REST, timeout 5 s).
const char *Online_CreateRoom(const char *roomName, const char *mapName, const char *mode, int maxPlayers);

// Entra numa sala existente pelo código. 1 = ok.
int Online_JoinRoom(const char *code);

// Sai da sala atual (remove o jogador do banco).
void Online_LeaveRoom();

// Código da sala atual ("", se não estiver em nenhuma).
const char *Online_GetRoomCode();

// Envia mensagem para o chat da sala atual (aparece no hub web).
void Online_Say(const char *text);

// Publica o estado do jogador local na sala (chamado a cada ~1 s pelo mod GSC).
void Online_PushState(int round, int alive, int kills, int downs, int points);

// Publica um evento na sala. dataJson é um objeto JSON (pode ser "{}").
void Online_PushEvent(const char *type, const char *dataJson);

// Bombeia a rede (fila REST + polling de eventos/chat). Retorna o nº de
// eventos novos desde a última chamada. Chamar ~1x/s do GSC.
int Online_Poll();

// Evento i da fila atual. field: 0=type, 1..3=campos do payload
// (ex.: kill → f1=nome, f2=abates, f3=pontos). Retorna "" fora do intervalo.
const char *Online_GetEvent(int i, int field);

// Roster da sala (última sincronização). field: 0=name, 1=ready, 2=points,
// 3=kills, 4=downs, 5=alive. i >= Online_RosterCount() → "".
int Online_RosterCount();
const char *Online_GetRoster(int i, int field);
