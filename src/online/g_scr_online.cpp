// ============================================================================
// MODO ONLINE (Firebase) — builtins GSC — NÃO faz parte do jogo original.
// Funções registradas em functions[] (src/game_mp/g_scr_main_mp.cpp). Ver
// g_scr_online.h para a documentação de cada builtin.
// ============================================================================

#include <clientscript/cscr_vm.h>
#include <clientscript/cscr_main.h>

#include "firebase_online.h"
#include "g_scr_online.h"

// onlineconnect( "apelido" ) → 1/0
void __cdecl GScr_OnlineConnect()
{
    if (Scr_GetNumParam(SCRIPTINSTANCE_SERVER) < 1)
    {
        Scr_Error(SCRIPTINSTANCE_SERVER, "onlineconnect( apelido ): falta o apelido", 0);
        return;
    }
    char *name = Scr_GetString(0, SCRIPTINSTANCE_SERVER);
    int ok = Online_Connect(name ? name : "Operador");
    Scr_AddInt(ok, SCRIPTINSTANCE_SERVER);
}

// onlinestatus() → str
void __cdecl GScr_OnlineStatus()
{
    Scr_AddString((char *)Online_Status(), SCRIPTINSTANCE_SERVER);
}

// onlineroomcreate( nome, mapa, modo, maxjogadores ) → str (código)
void __cdecl GScr_OnlineRoomCreate()
{
    if (Scr_GetNumParam(SCRIPTINSTANCE_SERVER) < 1)
    {
        Scr_Error(SCRIPTINSTANCE_SERVER, "onlineroomcreate( nome, mapa, modo, maxjogadores )", 0);
        return;
    }
    char *roomName = Scr_GetString(0, SCRIPTINSTANCE_SERVER);
    const char *mapName = Scr_GetNumParam(SCRIPTINSTANCE_SERVER) > 1 ? Scr_GetString(1, SCRIPTINSTANCE_SERVER) : "zombie_theater";
    const char *mode = Scr_GetNumParam(SCRIPTINSTANCE_SERVER) > 2 ? Scr_GetString(2, SCRIPTINSTANCE_SERVER) : "survival";
    int maxPlayers = Scr_GetNumParam(SCRIPTINSTANCE_SERVER) > 3 ? Scr_GetInt(3, SCRIPTINSTANCE_SERVER) : 4;

    const char *code = Online_CreateRoom(roomName ? roomName : "Sala",
                                         mapName ? mapName : "zombie_theater",
                                         mode ? mode : "survival",
                                         maxPlayers);
    Scr_AddString((char *)code, SCRIPTINSTANCE_SERVER);
}

// onlineroomjoin( "CODIGO" ) → 1/0
void __cdecl GScr_OnlineRoomJoin()
{
    if (Scr_GetNumParam(SCRIPTINSTANCE_SERVER) < 1)
    {
        Scr_Error(SCRIPTINSTANCE_SERVER, "onlineroomjoin( codigo )", 0);
        return;
    }
    char *code = Scr_GetString(0, SCRIPTINSTANCE_SERVER);
    Scr_AddInt(Online_JoinRoom(code), SCRIPTINSTANCE_SERVER);
}

// onlineroomleave() → —
void __cdecl GScr_OnlineRoomLeave()
{
    Online_LeaveRoom();
}

// onlineroomcode() → str
void __cdecl GScr_OnlineRoomCode()
{
    Scr_AddString((char *)Online_GetRoomCode(), SCRIPTINSTANCE_SERVER);
}

// onlinesay( "texto" ) → —
void __cdecl GScr_OnlineSay()
{
    if (Scr_GetNumParam(SCRIPTINSTANCE_SERVER) < 1)
        return;
    char *text = Scr_GetString(0, SCRIPTINSTANCE_SERVER);
    if (text)
        Online_Say(text);
}

// onlinepushstate( rodada, vivos, abates, baixas, pontos ) → —
void __cdecl GScr_OnlinePushState()
{
    int n = Scr_GetNumParam(SCRIPTINSTANCE_SERVER);
    if (n < 1)
        return;
    int round = Scr_GetInt(0, SCRIPTINSTANCE_SERVER);
    int alive = n > 1 ? Scr_GetInt(1, SCRIPTINSTANCE_SERVER) : 1;
    int kills = n > 2 ? Scr_GetInt(2, SCRIPTINSTANCE_SERVER) : 0;
    int downs = n > 3 ? Scr_GetInt(3, SCRIPTINSTANCE_SERVER) : 0;
    int points = n > 4 ? Scr_GetInt(4, SCRIPTINSTANCE_SERVER) : 0;
    Online_PushState(round, alive, kills, downs, points);
}

// onlineevent( "tipo", "json" ) → —
void __cdecl GScr_OnlineEvent()
{
    if (Scr_GetNumParam(SCRIPTINSTANCE_SERVER) < 1)
        return;
    char *type = Scr_GetString(0, SCRIPTINSTANCE_SERVER);
    const char *data = Scr_GetNumParam(SCRIPTINSTANCE_SERVER) > 1 ? Scr_GetString(1, SCRIPTINSTANCE_SERVER) : "{}";
    Online_PushEvent(type ? type : "evento", data ? data : "{}");
}

// onlinepoll() → int (eventos novos; leia com onlineeventget)
void __cdecl GScr_OnlinePoll()
{
    Scr_AddInt(Online_Poll(), SCRIPTINSTANCE_SERVER);
}

// onlineeventget( i, campo ) → str
void __cdecl GScr_OnlineEventGet()
{
    if (Scr_GetNumParam(SCRIPTINSTANCE_SERVER) < 1)
    {
        Scr_AddString((char *)"", SCRIPTINSTANCE_SERVER);
        return;
    }
    int i = Scr_GetInt(0, SCRIPTINSTANCE_SERVER);
    int field = Scr_GetNumParam(SCRIPTINSTANCE_SERVER) > 1 ? Scr_GetInt(1, SCRIPTINSTANCE_SERVER) : 0;
    Scr_AddString((char *)Online_GetEvent(i, field), SCRIPTINSTANCE_SERVER);
}

// onlinerostercount() → int
void __cdecl GScr_OnlineRosterCount()
{
    Scr_AddInt(Online_RosterCount(), SCRIPTINSTANCE_SERVER);
}

// onlinerosterget( i, campo ) → str
void __cdecl GScr_OnlineRosterGet()
{
    if (Scr_GetNumParam(SCRIPTINSTANCE_SERVER) < 1)
    {
        Scr_AddString((char *)"", SCRIPTINSTANCE_SERVER);
        return;
    }
    int i = Scr_GetInt(0, SCRIPTINSTANCE_SERVER);
    int field = Scr_GetNumParam(SCRIPTINSTANCE_SERVER) > 1 ? Scr_GetInt(1, SCRIPTINSTANCE_SERVER) : 0;
    Scr_AddString((char *)Online_GetRoster(i, field), SCRIPTINSTANCE_SERVER);
}
