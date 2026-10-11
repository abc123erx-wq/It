# online — modo online via Firebase (NÃO faz parte do jogo original)

Conecta o jogo ao **Firebase Realtime Database** do projeto `kaka-ca0ff` — o mesmo
banco do hub web em [`online/`](../../online/README.md). Presença, chat, rodadas,
abates e baixas sincronizam em tempo real com o navegador.

## Iniciar

```powershell
cd build\Release
$R = (Get-Location).Path
.\BO1Zombies.exe +set fs_b $R +set fs_h $R +set r_fullscreen 0 +set bo1_zombies 1 `
  +set fs_mods online +set online_name "SeuNick" +set online_room CODIGO
```

- `online_name` — apelido no hub (obrigatório para ligar o modo online).
- `online_room` — código da sala do hub (opcional; sem ele o jogo cria uma sala nova
  e o código aparece no log — digite-o no botão "Entrar com código" do hub).

Empilha com outros mods normalmente: `+set fs_mods "horde online zinfo"`.

## O que sincroniza

| Jogo → Firebase (hub) | Hub → jogo |
|---|---|
| Presença e nome do host da sala | Chat da sala (aparece no console com `iprintln`) |
| Rodada atual (`level.round_number`) | Eventos `match_start` / `game_over` |
| Jogadores vivos, pontos, abates, baixas | Evento `round_start` (do painel do hub) |
| Evento `round_start` a cada rodada | |

## Builtins GSC (src/online/g_scr_online.cpp)

`onlineconnect(name)`, `onlinestatus()`, `onlineroomcreate(nome, mapa, modo, max)`,
`onlineroomjoin(codigo)`, `onlineroomleave()`, `onlineroomcode()`, `onlinesay(texto)`,
`onlinepushstate(rodada, vivos, abates, baixas, pontos)`, `onlineevent(tipo, json)`,
`onlinepoll()` → nº de eventos novos, `onlineeventget(i, campo)`,
`onlinerostercount()`, `onlinerosterget(i, campo)`.

Campo do evento: `0` = tipo, `1..3` = payload (ex.: `kill` → 1=nome; `chat` → 1=nome, 2=texto).

## Notas

- O cliente REST (WinHTTP) está em `src/online/firebase_online.cpp`; sem internet ou
  com regras do banco negando acesso, o jogo segue normal — só o modo online fica off
  (`onlinestatus()` → `"erro: ..."`).
- O hub web (`online/serve.py`) é a interface completa do modo online: salas,
  convites, chat, ranking e partida ao vivo.
