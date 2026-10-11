#pragma once
// ============================================================================
// MODO ONLINE (Firebase) — builtins GSC — NÃO faz parte do jogo original.
// Registrados na tabela functions[] de src/game_mp/g_scr_main_mp.cpp.
// Chamados pelos scripts de mods/online (GSC).
//
//   onlineconnect( "apelido" )              → 1/0   conecta ao Firebase
//   onlinestatus()                          → str   "off"/"connecting"/"online"/"room:COD"/"erro: ..."
//   onlineroomcreate( nome, mapa, modo, n ) → str   código da sala criada ("" = erro)
//   onlineroomjoin( "CODIGO" )              → 1/0
//   onlineroomleave()                       → —
//   onlineroomcode()                        → str   código da sala atual
//   onlinesay( "texto" )                    → —     chat da sala (aparece no hub web)
//   onlinepushstate( rodada, vivos, abates, baixas, pontos )
//   onlineevent( "tipo", "json" )           → —     publica evento na sala
//   onlinepoll()                            → int   nº de eventos novos prontos p/ leitura
//   onlineeventget( i, campo )              → str   campo 0=tipo 1..3=payload
//   onlinerostercount()                     → int   jogadores na sala (última sincronização)
//   onlinerosterget( i, campo )             → str   campo 0=nome 1=pronto 2=pontos 3=abates 4=baixas 5=vivo
// ============================================================================

void __cdecl GScr_OnlineConnect();
void __cdecl GScr_OnlineStatus();
void __cdecl GScr_OnlineRoomCreate();
void __cdecl GScr_OnlineRoomJoin();
void __cdecl GScr_OnlineRoomLeave();
void __cdecl GScr_OnlineRoomCode();
void __cdecl GScr_OnlineSay();
void __cdecl GScr_OnlinePushState();
void __cdecl GScr_OnlineEvent();
void __cdecl GScr_OnlinePoll();
void __cdecl GScr_OnlineEventGet();
void __cdecl GScr_OnlineRosterCount();
void __cdecl GScr_OnlineRosterGet();
