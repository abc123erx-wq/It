#include maps\_utility;
#include common_scripts\utility;
#include maps\_zombiemode_utility;

// ONLINE MOD - não faz parte do jogo original. Carregado com +set fs_mods "online".
// Liga o jogo ao Firebase Realtime Database (mesmo banco do hub web em online/):
// presença, chat, rodadas, abates e baixas aparecem no hub em tempo real.
// Builtins usados aqui: src/online/g_scr_online.cpp (onlineconnect, onlinepoll, ...).
// Config por dvar: online_name (apelido), online_room (código da sala, opcional).
// Registro nos hooks: maps/online/_hooks.gsc.

// Five tem o hook próprio; qualquer mapa cai aqui. Roda já (sem wait até o 1º wait).
main_end_any_map()
{
	if ( IsDefined( level.online_main_end_done ) )
	{
		return;
	}
	level.online_main_end_done = true;

	name = GetDvar( #"online_name" );
	if ( name == "" )
	{
		// sem +set online_name o modo online fica desligado (jogo original)
		return;
	}

	if ( !onlineconnect( name ) )
	{
		LogPrint( "online: falha ao iniciar a conexao\n" );
		return;
	}
	LogPrint( "online: conectado como " + name + "\n" );
	level.online_name = name;

	room = GetDvar( #"online_room" );
	if ( room != "" )
	{
		if ( onlineroomjoin( room ) )
		{
			LogPrint( "online: entrou na sala " + room + "\n" );
		}
		else
		{
			code = onlineroomcreate( "Sala de " + name, GetDvar( #"mapname" ), "survival", 4 );
			LogPrint( "online: sala nao encontrada, criou " + code + "\n" );
		}
	}
	else
	{
		code = onlineroomcreate( "Sala de " + name, GetDvar( #"mapname" ), "survival", 4 );
		LogPrint( "online: sala criada " + code + "\n" );
	}

	level thread online_think();
	level thread online_round_watch();
}

// Laço principal: bombeia a rede, trata eventos vindos do hub e publica o estado.
online_think()
{
	level endon( "end_game" );

	for ( ;; )
	{
		n = onlinepoll();
		for ( i = 0; i < n; i++ )
		{
			type = onlineeventget( i, 0 );
			f1 = onlineeventget( i, 1 );
			f2 = onlineeventget( i, 2 );
			online_handle_event( type, f1, f2 );
		}
		online_push_state();
		wait( 1 );
	}
}

online_handle_event( type, f1, f2 )
{
	if ( type == "chat" )
	{
		// mensagem do hub web → console do jogo
		iprintln( "^3[online] " + f1 + ":^7 " + f2 );
		return;
	}
	if ( type == "match_start" )
	{
		iprintln( "^2[online] partida iniciada no hub^7" );
		return;
	}
	if ( type == "game_over" )
	{
		iprintln( "^1[online] partida encerrada no hub^7" );
		return;
	}
	if ( type == "round_start" )
	{
		iprintln( "^2[online] rodada " + f1 + "^7" );
		return;
	}
}

// Estado agregado da sessão → Firebase (aparece no hub em tempo real).
online_push_state()
{
	players = get_players();
	alive = 0;
	kills = 0;
	downs = 0;
	points = 0;
	for ( i = 0; i < players.size; i++ )
	{
		p = players[i];
		if ( IsDefined( p ) && IsAlive( p ) )
		{
			alive++;
		}
		if ( IsDefined( p.score ) )
		{
			points += p.score;
		}
		if ( IsDefined( p.stats ) )
		{
			if ( IsDefined( p.stats["kills"] ) )
			{
				kills += p.stats["kills"];
			}
			if ( IsDefined( p.stats["downs"] ) )
			{
				downs += p.stats["downs"];
			}
		}
	}

	round = 0;
	if ( IsDefined( level.round_number ) )
	{
		round = level.round_number;
	}
	onlinepushstate( round, alive, kills, downs, points );
}

// Publica avanço de rodada como evento (o hub mostra no feed da partida).
online_round_watch()
{
	level endon( "end_game" );

	last_round = -1;
	for ( ;; )
	{
		if ( IsDefined( level.round_number ) && level.round_number != last_round )
		{
			last_round = level.round_number;
			onlineevent( "round_start", "{\"round\":" + last_round + "}" );
			LogPrint( "online: rodada " + last_round + "\n" );
		}
		wait( 0.5 );
	}
}
