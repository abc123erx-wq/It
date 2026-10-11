/* ============================================================================
 * BO1 Zombies — Modo Online (hub web)
 * Firebase Realtime Database: presença, salas, chat, partida ao vivo, ranking.
 * ==========================================================================*/
(function () {
  'use strict';

  var db = firebase.database();
  var auth = firebase.auth();

  // --------------------------- Estado local ---------------------------
  var state = {
    uid: null,
    name: null,
    authMode: null,          // 'anonymous' | 'local'
    connected: false,
    serverTimeOffset: 0,
    roomCode: null,          // sala atual (código)
    room: null,              // snapshot da sala atual
    roomPlayers: {},
    simTimer: null,
    simRunning: false,
    pendingEvents: [],
    stats: { matches: 0, kills: 0, downs: 0, bestRound: 0, points: 0 }
  };

  var MAPS = [
    { id: 'zombie_pentagon',    name: 'Five (Pentágono)' },
    { id: 'zombie_theater',     name: 'Kino der Toten' },
    { id: 'zombie_coast',       name: 'Call of the Dead' },
    { id: 'zombie_cosmodrome',  name: 'Ascension' },
    { id: 'zombie_temple',      name: 'Shangri-La' },
    { id: 'zombie_moon',        name: 'Moon' }
  ];
  var MODES = [
    { id: 'survival',  name: 'Sobrevivência' },
    { id: 'horde',     name: 'Horda (rounds contínuos)' },
    { id: 'nightmare', name: 'Pesadelo' },
    { id: 'sandbox',   name: 'Sandbox' }
  ];

  function mapName(id) {
    for (var i = 0; i < MAPS.length; i++) if (MAPS[i].id === id) return MAPS[i].name;
    return id || '—';
  }
  function modeName(id) {
    for (var i = 0; i < MODES.length; i++) if (MODES[i].id === id) return MODES[i].name;
    return id || '—';
  }

  // --------------------------- Utilidades ---------------------------
  function $(sel) { return document.querySelector(sel); }
  function $$(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }
  function now() { return Date.now() + state.serverTimeOffset; }
  function clampStr(s, n) { return String(s == null ? '' : s).slice(0, n); }
  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function toast(msg, type) {
    var box = document.createElement('div');
    box.className = 'toast ' + (type || '');
    box.textContent = msg;
    $('#toasts').appendChild(box);
    setTimeout(function () { box.remove(); }, 5200);
  }

  function showBanner(html) {
    var b = $('#banner');
    b.innerHTML = html;
    b.classList.remove('hidden');
  }
  function hideBanner() { $('#banner').classList.add('hidden'); }

  function fbError(err) {
    var code = err && err.code ? err.code : '';
    var msg = (err && err.message) ? err.message : String(err);
    if (code.indexOf('PERMISSION_DENIED') >= 0 || msg.indexOf('PERMISSION_DENIED') >= 0) {
      showBanner(
        'FIREBASE RECUSOU O ACESSO (PERMISSION_DENIED). Publique as regras de <code>online/database.rules.json</code> ' +
        'no console do Firebase (Realtime Database → Regras) e, se necessário, ative a Autenticação Anônima. ' +
        'Detalhes no console do navegador (F12).'
      );
    }
    console.error('[BO1Z Online]', err);
    return msg;
  }

  function genCode() {
    var alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    var code = '';
    for (var i = 0; i < 6; i++) code += alphabet.charAt(Math.floor(Math.random() * alphabet.length));
    return code;
  }

  function uidLocal() {
    var u = localStorage.getItem('bo1z_uid');
    if (!u) {
      u = 'local-' + (window.crypto && crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2) + Date.now());
      localStorage.setItem('bo1z_uid', u);
    }
    return u;
  }

  // --------------------------- Conexão / Auth ---------------------------
  function renderConn() {
    var pill = $('#conn-pill');
    var txt = $('#conn-text');
    pill.classList.remove('pill-on', 'pill-off', 'pill-err');
    if (state.connected) {
      pill.classList.add('pill-on');
      txt.textContent = 'firebase conectado';
    } else {
      pill.classList.add('pill-off');
      txt.textContent = 'conectando ao firebase…';
    }
  }

  function initFirebaseListeners() {
    db.ref('.info/connected').on('value', function (snap) {
      state.connected = snap.val() === true;
      renderConn();
      if (state.connected && state.uid) {
        // Reafirma presença ao reconectar
        heartbeat();
        if (state.roomCode) {
          var meInRoom = db.ref('bo1z/rooms/' + state.roomCode + '/players/' + state.uid);
          meInRoom.onDisconnect().remove();
        }
      }
    });
    db.ref('.info/serverTimeOffset').on('value', function (snap) {
      state.serverTimeOffset = snap.val() || 0;
    });
  }

  function ensureAuth() {
    return auth.signInAnonymously().then(function (cred) {
      state.uid = cred.user.uid;
      state.authMode = 'anonymous';
    }).catch(function (err) {
      // Sem autenticação anônima habilitada: identidade local (funciona se as
      // regras do Realtime Database permitirem acesso público de teste).
      state.uid = uidLocal();
      state.authMode = 'local';
      console.warn('[BO1Z Online] signInAnonymously falhou, usando identidade local:', err && err.code);
    });
  }

  // --------------------------- Presença ---------------------------
  var heartbeatTimer = null;
  function heartbeat() {
    if (!state.uid) return;
    var me = db.ref('bo1z/players/' + state.uid);
    me.update({
      name: state.name,
      status: state.roomCode ? (state.room && state.room.status === 'in_game' ? 'in_game' : 'in_room') : 'online',
      roomId: state.roomCode || null,
      lastSeen: firebase.database.ServerValue.TIMESTAMP
    }).catch(fbError);
  }

  function startPresence() {
    var me = db.ref('bo1z/players/' + state.uid);
    me.once('value').then(function (snap) {
      var prev = snap.val() || {};
      state.stats = Object.assign({ matches: 0, kills: 0, downs: 0, bestRound: 0, points: 0 }, prev.stats || {});
      me.update({
        name: state.name,
        status: 'online',
        roomId: null,
        createdAt: prev.createdAt || firebase.database.ServerValue.TIMESTAMP,
        stats: state.stats,
        lastSeen: firebase.database.ServerValue.TIMESTAMP
      }).catch(fbError);
      me.child('status').onDisconnect().set('offline');
      me.child('lastSeen').onDisconnect().set(firebase.database.ServerValue.TIMESTAMP);
    }).catch(fbError);

    if (heartbeatTimer) clearInterval(heartbeatTimer);
    heartbeatTimer = setInterval(heartbeat, 20000);
  }

  function isFresh(p) {
    return p && typeof p.lastSeen === 'number' && (now() - p.lastSeen) < 60000;
  }

  // --------------------------- Salas ---------------------------
  function roomsRef() { return db.ref('bo1z/rooms'); }

  function createRoom(opts) {
    var code = genCode();
    var roomRef = db.ref('bo1z/rooms/' + code);
    var room = {
      code: code,
      name: clampStr(opts.name, 28) || (state.name + ' & Cia'),
      map: opts.map,
      mode: opts.mode,
      maxPlayers: parseInt(opts.maxPlayers, 10) || 4,
      hostId: state.uid,
      hostName: state.name,
      status: 'waiting',
      createdAt: firebase.database.ServerValue.TIMESTAMP,
      match: { round: 0, kills: 0, downs: 0, points: 0, startedAt: null }
    };
    return roomRef.set(room).then(function () {
      return joinRoom(code, true);
    }).catch(function (err) { fbError(err); toast('Não foi possível criar a sala.', 'error'); });
  }

  function joinRoom(code, asHost) {
    code = String(code || '').trim().toUpperCase();
    if (!code) { toast('Informe o código da sala.', 'warn'); return Promise.resolve(); }
    var roomRef = db.ref('bo1z/rooms/' + code);
    return roomRef.once('value').then(function (snap) {
      if (!snap.exists()) { toast('Sala não encontrada: ' + code, 'error'); return; }
      var room = snap.val() || {};
      var players = room.players || {};
      var count = Object.keys(players).length;
      if (!asHost && players[state.uid] === undefined && count >= (room.maxPlayers || 4)) {
        toast('Sala cheia (' + count + '/' + room.maxPlayers + ').', 'warn');
        return;
      }
      // Se o anfitrião sumiu, assume quem entra
      var hostGone = room.hostId && !players[room.hostId];

      var myEntry = {
        name: state.name,
        isHost: !!(asHost || hostGone),
        ready: false,
        joinedAt: firebase.database.ServerValue.TIMESTAMP,
        state: { alive: true, points: 0, kills: 0, downs: 0 }
      };

      var updates = {};
      updates['bo1z/rooms/' + code + '/players/' + state.uid] = myEntry;
      if (asHost || hostGone) {
        updates['bo1z/rooms/' + code + '/hostId'] = state.uid;
        updates['bo1z/rooms/' + code + '/hostName'] = state.name;
      }
      updates['bo1z/players/' + state.uid + '/roomId'] = code;
      updates['bo1z/players/' + state.uid + '/status'] = 'in_room';

      return db.ref().update(updates).then(function () {
        roomRef.child('players/' + state.uid).onDisconnect().remove();
        state.roomCode = code;
        attachRoom(code);
        switchTab('room');
        toast('Você entrou na sala ' + code + '.', 'ok');
        var sys = { sys: true, text: state.name + ' entrou na sala.', ts: firebase.database.ServerValue.TIMESTAMP };
        roomRef.child('chat').push(sys).catch(function () {});
        heartbeat();
      });
    }).catch(function (err) { fbError(err); toast('Falha ao entrar na sala.', 'error'); });
  }

  function leaveRoom() {
    if (!state.roomCode) return;
    stopSimulation(true);
    var code = state.roomCode;
    var roomRef = db.ref('bo1z/rooms/' + code);
    var meRef = roomRef.child('players/' + state.uid);
    meRef.onDisconnect().cancel();
    meRef.remove().catch(function () {});
    roomRef.child('chat').push({
      sys: true, text: state.name + ' saiu da sala.', ts: firebase.database.ServerValue.TIMESTAMP
    }).catch(function () {});

    // Migração de anfitrião / limpeza da sala vazia
    roomRef.once('value').then(function (snap) {
      var room = snap.val();
      if (!room) return;
      var players = room.players || {};
      var ids = Object.keys(players);
      if (ids.length === 0) {
        roomRef.remove().catch(function () {});
      } else if (room.hostId === state.uid) {
        var next = ids[0];
        roomRef.update({ hostId: next, hostName: players[next].name }).catch(function () {});
      }
    });

    db.ref('bo1z/players/' + state.uid).update({ status: 'online', roomId: null }).catch(function () {});
    if (state.roomRefOff) { state.roomRefOff(); state.roomRefOff = null; }
    state.roomCode = null;
    state.room = null;
    $('#room-view').classList.add('hidden');
    $('#room-empty').classList.remove('hidden');
    toast('Você saiu da sala.', '');
    heartbeat();
    switchTab('rooms');
  }

  function attachRoom(code) {
    if (state.roomRefOff) state.roomRefOff();
    var roomRef = db.ref('bo1z/rooms/' + code);
    var chatRef = roomRef.child('chat').limitToLast(80);
    var evRef = roomRef.child('events').limitToLast(40);

    function offAll() {
      roomRef.off();
      chatRef.off();
      evRef.off();
    }
    state.roomRefOff = offAll;

    roomRef.on('value', function (snap) {
      var room = snap.val();
      if (!room) return;
      state.room = room;
      state.roomPlayers = room.players || {};
      renderRoom();
    }, function (err) { fbError(err); });

    chatRef.on('value', function (snap) {
      renderChat('#room-chat', snap.val());
    }, function (err) { fbError(err); });

    evRef.on('value', function (snap) {
      renderEvents(snap.val());
    }, function (err) { fbError(err); });
  }

  // --------------------------- Pronto / Partida ---------------------------
  function toggleReady() {
    if (!state.roomCode) return;
    var me = (state.roomPlayers || {})[state.uid] || {};
    var ready = !me.ready;
    db.ref('bo1z/rooms/' + state.roomCode + '/players/' + state.uid + '/ready').set(ready).catch(fbError);
  }

  function startMatch() {
    if (!state.roomCode || !state.room) return;
    if (state.room.hostId !== state.uid) return;
    var roomRef = db.ref('bo1z/rooms/' + state.roomCode);
    var players = state.roomPlayers || {};
    var updates = {};
    updates['status'] = 'in_game';
    updates['match'] = { round: 1, kills: 0, downs: 0, points: 0, startedAt: firebase.database.ServerValue.TIMESTAMP };
    Object.keys(players).forEach(function (uid) {
      updates['players/' + uid + '/state'] = { alive: true, points: 0, kills: 0, downs: 0 };
      updates['players/' + uid + '/ready'] = true;
    });
    roomRef.update(updates).then(function () {
      roomRef.child('events').push({ type: 'match_start', ts: firebase.database.ServerValue.TIMESTAMP }).catch(function () {});
      toast('Partida iniciada!', 'ok');
    }).catch(fbError);
  }

  function endMatch() {
    if (!state.roomCode || !state.room || state.room.hostId !== state.uid) return;
    stopSimulation(true);
    var roomRef = db.ref('bo1z/rooms/' + state.roomCode);
    roomRef.child('events').push({ type: 'game_over', ts: firebase.database.ServerValue.TIMESTAMP }).catch(function () {});
    roomRef.update({ status: 'waiting', 'match/round': 0, 'match/startedAt': null }).then(function () {
      commitStats();
      toast('Partida encerrada. Estatísticas salvas.', 'ok');
    }).catch(fbError);
  }

  function commitStats() {
    if (!state.room) return;
    var match = state.room.match || {};
    var me = (state.roomPlayers || {})[state.uid];
    if (!me) return;
    var st = me.state || {};
    var s = state.stats;
    s.matches = (s.matches || 0) + 1;
    s.kills = (s.kills || 0) + (st.kills || 0);
    s.downs = (s.downs || 0) + (st.downs || 0);
    s.points = (s.points || 0) + (st.points || 0);
    s.bestRound = Math.max(s.bestRound || 0, match.round || 0);
    db.ref('bo1z/players/' + state.uid + '/stats').set(s).catch(fbError);
    renderProfile();
  }

  // --------------------------- Simulação (demo) ---------------------------
  var simTick = 0;
  function toggleSimulation() {
    if (state.simRunning) { stopSimulation(); return; }
    if (!state.roomCode || !state.room || state.room.hostId !== state.uid) return;
    if (state.room.status !== 'in_game') { toast('Inicie a partida primeiro.', 'warn'); return; }
    state.simRunning = true;
    simTick = 0;
    $('#btn-simulate').textContent = 'PARAR SIMULAÇÃO';
    toast('Simulação de partida ativa (demo de sincronização em tempo real).', 'ok');
    state.simTimer = setInterval(simStep, 1800);
  }

  function stopSimulation(silent) {
    if (state.simTimer) clearInterval(state.simTimer);
    state.simTimer = null;
    if (state.simRunning && !silent) toast('Simulação parada.', '');
    state.simRunning = false;
    var btn = $('#btn-simulate');
    if (btn) btn.textContent = 'SIMULAR PARTIDA (DEMO)';
  }

  function simStep() {
    if (!state.roomCode || !state.room) return;
    var roomRef = db.ref('bo1z/rooms/' + state.roomCode);
    var players = state.roomPlayers || {};
    var uids = Object.keys(players);
    if (uids.length === 0) return;
    simTick++;

    var match = Object.assign({ round: 1, kills: 0, downs: 0, points: 0 }, state.room.match || {});
    var roll = Math.random();

    if (simTick % 12 === 0) {
      // Avanço de rodada
      match.round = (match.round || 1) + 1;
      roomRef.child('match').update({ round: match.round }).catch(function () {});
      roomRef.child('events').push({ type: 'round_start', round: match.round, ts: firebase.database.ServerValue.TIMESTAMP }).catch(function () {});
    } else if (roll < 0.62) {
      // Abate de zumbi por um jogador aleatório
      var u = uids[Math.floor(Math.random() * uids.length)];
      var st = players[u].state || { alive: true, points: 0, kills: 0, downs: 0 };
      if (!st.alive) return;
      st.kills = (st.kills || 0) + 1;
      st.points = (st.points || 0) + 10;
      match.kills = (match.kills || 0) + 1;
      match.points = (match.points || 0) + 10;
      roomRef.child('players/' + u + '/state').set(st).catch(function () {});
      roomRef.child('match').update({ kills: match.kills, points: match.points }).catch(function () {});
      roomRef.child('events').push({ type: 'kill', uid: u, name: players[u].name, ts: firebase.database.ServerValue.TIMESTAMP }).catch(function () {});
    } else if (roll < 0.78) {
      // Jogador derrubado
      var d = uids[Math.floor(Math.random() * uids.length)];
      var std = players[d].state || { alive: true, points: 0, kills: 0, downs: 0 };
      if (!std.alive) return;
      std.alive = false;
      std.downs = (std.downs || 0) + 1;
      match.downs = (match.downs || 0) + 1;
      roomRef.child('players/' + d + '/state').set(std).catch(function () {});
      roomRef.child('match').update({ downs: match.downs }).catch(function () {});
      roomRef.child('events').push({ type: 'down', uid: d, name: players[d].name, ts: firebase.database.ServerValue.TIMESTAMP }).catch(function () {});
    } else {
      // Reviver
      var downIds = uids.filter(function (uid) { return players[uid].state && !players[uid].state.alive; });
      if (downIds.length > 0) {
        var r = downIds[0];
        var str = players[r].state;
        str.alive = true;
        roomRef.child('players/' + r + '/state').set(str).catch(function () {});
        roomRef.child('events').push({ type: 'revive', uid: r, name: players[r].name, ts: firebase.database.ServerValue.TIMESTAMP }).catch(function () {});
      }
    }
  }

  // --------------------------- Chat ---------------------------
  function sendChat(target) {
    var input = target === 'global' ? $('#input-global-chat') : $('#input-room-chat');
    var text = clampStr(input.value.trim(), 140);
    if (!text) return;
    var msg = { uid: state.uid, name: state.name, text: text, ts: firebase.database.ServerValue.TIMESTAMP };
    var ref = target === 'global' ? db.ref('bo1z/chat') : db.ref('bo1z/rooms/' + state.roomCode + '/chat');
    ref.push(msg).then(function () { input.value = ''; }).catch(function (err) { fbError(err); toast('Mensagem não enviada.', 'error'); });
  }

  function renderChat(sel, val) {
    var box = $(sel);
    if (!box) return;
    box.innerHTML = '';
    if (!val) { box.innerHTML = '<div class="empty">Sem mensagens ainda.</div>'; return; }
    var keys = Object.keys(val).sort(function (a, b) { return (val[a].ts || 0) - (val[b].ts || 0); });
    keys.forEach(function (k) {
      var m = val[k];
      var div = document.createElement('div');
      if (m.sys) {
        div.className = 'chat-msg sys';
        div.textContent = m.text;
      } else {
        div.className = 'chat-msg' + (m.uid === state.uid ? ' me' : '');
        div.innerHTML = '<span class="who">' + esc(m.name) + '</span>' + esc(m.text);
      }
      box.appendChild(div);
    });
    box.scrollTop = box.scrollHeight;
  }

  // --------------------------- Render ---------------------------
  function renderProfile() {
    var s = state.stats || {};
    $('#profile-box').innerHTML =
      'apelido: <b>' + esc(state.name) + '</b><br>' +
      'partidas: <b>' + (s.matches || 0) + '</b><br>' +
      'abates: <b>' + (s.kills || 0) + '</b><br>' +
      'baixas: <b>' + (s.downs || 0) + '</b><br>' +
      'melhor rodada: <b>' + (s.bestRound || 0) + '</b><br>' +
      'pontos: <b>' + (s.points || 0) + '</b>';
  }

  function renderPlayersOnline(val) {
    var box = $('#players-online');
    var rows = [];
    Object.keys(val || {}).forEach(function (uid) {
      var p = val[uid];
      if (!p || !isFresh(p) || p.status === 'offline') return;
      rows.push({ uid: uid, p: p });
    });
    rows.sort(function (a, b) { return (b.p.lastSeen || 0) - (a.p.lastSeen || 0); });
    $('#online-count').textContent = rows.length;
    if (rows.length === 0) { box.innerHTML = '<div class="empty">Nenhum operador online no momento.</div>'; return; }
    box.innerHTML = rows.map(function (r) {
      var where = r.p.status === 'in_game' ? 'EM PARTIDA' : (r.p.roomId ? 'SALA ' + esc(r.p.roomId) : 'NO HUB');
      return '<div class="pl-row">' +
        '<span class="pl-dot"></span>' +
        '<span class="pl-name">' + esc(r.p.name) + (r.uid === state.uid ? ' (você)' : '') + '</span>' +
        '<span class="pl-where">' + where + '</span></div>';
    }).join('');
  }

  function renderRooms(val) {
    var box = $('#rooms-list');
    var list = [];
    Object.keys(val || {}).forEach(function (code) {
      var r = val[code];
      if (r) list.push(r);
    });
    list.sort(function (a, b) { return (b.createdAt || 0) - (a.createdAt || 0); });
    if (list.length === 0) {
      box.innerHTML = '<div class="empty">Nenhuma sala aberta. Crie a primeira!</div>';
      return;
    }
    box.innerHTML = list.map(function (r) {
      var players = r.players || {};
      var count = Object.keys(players).length;
      var badge = r.status === 'in_game' ? '<span class="badge badge-ingame">EM PARTIDA</span>'
        : r.status === 'ended' ? '<span class="badge badge-ended">ENCERRADA</span>'
        : '<span class="badge badge-waiting">AGUARDANDO</span>';
      var mine = players[state.uid] !== undefined;
      return '<div class="room-card">' +
        '<div class="room-card-main">' +
          '<div class="room-card-title">' + esc(r.name) + ' ' + badge +
            ' <span class="room-code">' + esc(r.code || '') + '</span></div>' +
          '<div class="room-card-meta">' + esc(mapName(r.map)) + ' · ' + esc(modeName(r.mode)) +
            ' · anfitrião ' + esc(r.hostName || '?') + ' · ' + count + '/' + (r.maxPlayers || 4) + '</div>' +
        '</div>' +
        '<button class="btn btn-sm' + (mine ? ' btn-primary' : '') + '" data-join="' + esc(r.code || '') + '">' +
          (mine ? 'ABRIR' : 'ENTRAR') + '</button>' +
        '</div>';
    }).join('');
  }

  function renderRoom() {
    var room = state.room;
    if (!room) return;
    $('#room-empty').classList.add('hidden');
    $('#room-view').classList.remove('hidden');

    $('#room-name').textContent = room.name || 'Sala';
    $('#room-map').textContent = mapName(room.map);
    $('#room-mode').textContent = modeName(room.mode);
    $('#room-host').textContent = room.hostName || '—';
    var players = state.roomPlayers || {};
    var count = Object.keys(players).length;
    $('#room-count').textContent = count + '/' + (room.maxPlayers || 4);

    var badge = $('#room-status-badge');
    badge.classList.remove('badge-waiting', 'badge-ingame', 'badge-ended');
    if (room.status === 'in_game') { badge.textContent = 'EM PARTIDA'; badge.classList.add('badge-ingame'); }
    else if (room.status === 'ended') { badge.textContent = 'ENCERRADA'; badge.classList.add('badge-ended'); }
    else { badge.textContent = 'AGUARDANDO'; badge.classList.add('badge-waiting'); }

    var isHost = room.hostId === state.uid;
    $('#btn-start-match').classList.toggle('hidden', !(isHost && room.status === 'waiting'));
    $('#btn-end-match').classList.toggle('hidden', !(isHost && room.status === 'in_game'));
    $('#btn-simulate').classList.toggle('hidden', !isHost);
    $('#btn-ready').textContent = (players[state.uid] && players[state.uid].ready) ? 'NÃO PRONTO' : 'PRONTO';

    // Esquadrão
    var box = $('#room-players');
    var uids = Object.keys(players);
    if (uids.length === 0) { box.innerHTML = '<div class="empty">Nenhum jogador na sala.</div>'; }
    else {
      box.innerHTML = uids.map(function (uid) {
        var p = players[uid] || {};
        var st = p.state || {};
        return '<div class="rp-row' + (uid === state.uid ? ' me' : '') + '">' +
          '<span class="rp-name">' + esc(p.name) + (uid === state.uid ? ' (você)' : '') + '</span>' +
          (uid === room.hostId ? '<span class="rp-host-tag">ANFITRIÃO</span>' : '') +
          '<span class="rp-ready-tag' + (p.ready ? ' yes' : '') + '">' + (p.ready ? 'PRONTO' : 'AGUARDANDO') + '</span>' +
          '<span class="rp-state ' + (st.alive === false ? 'down' : 'alive') + '">' + (st.alive === false ? 'ABATIDO' : 'VIVO') + '</span>' +
          '<span class="rp-stats">pts <b>' + (st.points || 0) + '</b> · abates <b>' + (st.kills || 0) + '</b> · baixas <b>' + (st.downs || 0) + '</b></span>' +
          '</div>';
      }).join('');
    }

    // Partida ao vivo
    var match = room.match || {};
    $('#match-round').textContent = match.round || 0;
    $('#match-kills').textContent = match.kills || 0;
    $('#match-downs').textContent = match.downs || 0;
    $('#match-points').textContent = match.points || 0;
    var alive = 0;
    uids.forEach(function (uid) { if (players[uid].state && players[uid].state.alive !== false) alive++; });
    $('#match-alive').textContent = room.status === 'in_game' ? alive : 0;
  }

  function renderEvents(val) {
    var box = $('#match-events');
    if (!val) { box.innerHTML = '<div class="empty">Aguardando início da partida…</div>'; return; }
    var keys = Object.keys(val).sort(function (a, b) { return (val[a].ts || 0) - (val[b].ts || 0); });
    box.innerHTML = keys.map(function (k) {
      var e = val[k];
      var cls = 'ev', txt = '';
      switch (e.type) {
        case 'match_start': cls += ' round'; txt = '⚔ Partida iniciada!'; break;
        case 'game_over':   cls += ' round'; txt = '🏁 Partida encerrada.'; break;
        case 'round_start': cls += ' round'; txt = '🌀 Rodada ' + (e.round || '?') + ' começou.'; break;
        case 'kill':        cls += ' kill';  txt = '🧟 ' + esc(e.name || '?') + ' abateu um zumbi.'; break;
        case 'down':        cls += ' down';  txt = '💀 ' + esc(e.name || '?') + ' foi derrubado!'; break;
        case 'revive':      cls += ' kill';  txt = '💊 ' + esc(e.name || '?') + ' foi revivido.'; break;
        default: txt = esc(e.type);
      }
      return '<div class="' + cls + '">' + txt + '</div>';
    }).join('');
    box.scrollTop = box.scrollHeight;
  }

  function renderLeaderboard(val) {
    var tbody = $('#leaderboard-table tbody');
    var rows = [];
    Object.keys(val || {}).forEach(function (uid) {
      var p = val[uid];
      if (!p || !p.name) return;
      var s = p.stats || {};
      rows.push({ name: p.name, s: s });
    });
    rows.sort(function (a, b) {
      return (b.s.points || 0) - (a.s.points || 0) || (b.s.kills || 0) - (a.s.kills || 0);
    });
    $('#leaderboard-empty').classList.toggle('hidden', rows.length > 0);
    tbody.innerHTML = rows.slice(0, 25).map(function (r, i) {
      return '<tr><td>' + (i + 1) + '</td><td>' + esc(r.name) + '</td><td>' + (r.s.matches || 0) +
        '</td><td>' + (r.s.kills || 0) + '</td><td>' + (r.s.downs || 0) + '</td><td>' + (r.s.bestRound || 0) +
        '</td><td>' + (r.s.points || 0) + '</td></tr>';
    }).join('');
  }

  // --------------------------- Tabs / modal ---------------------------
  function switchTab(name) {
    $$('.tab').forEach(function (t) { t.classList.toggle('active', t.dataset.tab === name); });
    $$('.tab-pane').forEach(function (p) { p.classList.toggle('active', p.id === 'pane-' + name); });
  }

  function openCreateModal() {
    $('#modal-create').classList.remove('hidden');
    $('#input-room-name').value = state.name + ' & Cia';
    $('#input-room-name').focus();
  }
  function closeCreateModal() { $('#modal-create').classList.add('hidden'); }

  // --------------------------- Login flow ---------------------------
  function enterHub() {
    var nick = clampStr($('#input-nickname').value.trim(), 20);
    if (nick.length < 2) { toast('Apelido muito curto (mín. 2 letras).', 'warn'); return; }
    state.name = nick;
    localStorage.setItem('bo1z_name', nick);

    $('#view-login').classList.add('hidden');
    $('#view-app').classList.remove('hidden');
    $('#player-chip').classList.remove('hidden');
    $('#player-name').textContent = nick;
    $('#player-avatar').textContent = nick.charAt(0).toUpperCase();

    startPresence();
    renderProfile();

    // Listeners globais
    db.ref('bo1z/rooms').on('value', function (snap) { renderRooms(snap.val()); }, fbError);
    db.ref('bo1z/players').on('value', function (snap) {
      renderPlayersOnline(snap.val());
      renderLeaderboard(snap.val());
    }, fbError);
    db.ref('bo1z/chat').limitToLast(100).on('value', function (snap) {
      renderChat('#global-chat', snap.val());
    }, fbError);

    // Convite por link (#sala=CODIGO)
    var m = /#sala=([A-Za-z0-9]{4,8})/.exec(location.hash || '');
    if (m) {
      $('#input-room-code').value = m[1].toUpperCase();
      joinRoom(m[1]);
      history.replaceState(null, '', location.pathname);
    }
  }

  function logout() {
    if (state.roomCode) leaveRoom();
    if (heartbeatTimer) clearInterval(heartbeatTimer);
    location.reload();
  }

  // --------------------------- Eventos de UI ---------------------------
  function bindUI() {
    $('#btn-enter').addEventListener('click', enterHub);
    $('#input-nickname').addEventListener('keydown', function (e) {
      if (e.key === 'Enter') enterHub();
    });
    $('#btn-logout').addEventListener('click', logout);

    $$('.tab').forEach(function (t) {
      t.addEventListener('click', function () { switchTab(t.dataset.tab); });
    });

    $('#btn-create-room').addEventListener('click', openCreateModal);
    $('#btn-cancel-create').addEventListener('click', closeCreateModal);
    $('#btn-confirm-create').addEventListener('click', function () {
      createRoom({
        name: $('#input-room-name').value,
        map: $('#select-map').value,
        mode: $('#select-mode').value,
        maxPlayers: $('#select-max').value
      }).then(closeCreateModal);
    });

    $('#btn-join-code').addEventListener('click', function () { joinRoom($('#input-room-code').value); });
    $('#input-room-code').addEventListener('keydown', function (e) {
      if (e.key === 'Enter') joinRoom($('#input-room-code').value);
    });

    $('#rooms-list').addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('[data-join]') : null;
      if (b && b.dataset.join) joinRoom(b.dataset.join);
    });

    $('#btn-leave-room').addEventListener('click', leaveRoom);
    $('#btn-ready').addEventListener('click', toggleReady);
    $('#btn-start-match').addEventListener('click', startMatch);
    $('#btn-end-match').addEventListener('click', endMatch);
    $('#btn-simulate').addEventListener('click', toggleSimulation);
    $('#btn-copy-invite').addEventListener('click', function () {
      if (!state.roomCode) return;
      var link = location.href.split('#')[0] + '#sala=' + state.roomCode;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(link).then(function () { toast('Link do convite copiado!', 'ok'); });
      } else {
        window.prompt('Copie o link do convite:', link);
      }
    });

    $('#btn-send-room-chat').addEventListener('click', function () { sendChat('room'); });
    $('#input-room-chat').addEventListener('keydown', function (e) {
      if (e.key === 'Enter') sendChat('room');
    });
    $('#btn-send-global-chat').addEventListener('click', function () { sendChat('global'); });
    $('#input-global-chat').addEventListener('keydown', function (e) {
      if (e.key === 'Enter') sendChat('global');
    });

    window.addEventListener('beforeunload', function () {
      if (state.uid) {
        var me = db.ref('bo1z/players/' + state.uid);
        me.child('status').set('offline');
        me.child('lastSeen').set(firebase.database.ServerValue.TIMESTAMP);
      }
    });
  }

  function fillSelects() {
    $('#select-map').innerHTML = MAPS.map(function (m) {
      return '<option value="' + m.id + '">' + esc(m.name) + '</option>';
    }).join('');
    $('#select-mode').innerHTML = MODES.map(function (m) {
      return '<option value="' + m.id + '">' + esc(m.name) + '</option>';
    }).join('');
  }

  // --------------------------- Bootstrap ---------------------------
  function boot() {
    fillSelects();
    bindUI();
    initFirebaseListeners();

    var savedName = localStorage.getItem('bo1z_name');
    if (savedName) $('#input-nickname').value = savedName;

    ensureAuth().then(function () {
      $('#btn-enter').disabled = false;
      if (savedName) {
        // já tem nome salvo: entra direto
        $('#input-nickname').value = savedName;
        enterHub();
      }
    }).catch(function (err) {
      fbError(err);
    });

    if (auth.onAuthStateChanged) {
      auth.onAuthStateChanged(function (user) {
        if (user && user.uid && state.authMode === 'anonymous') state.uid = user.uid;
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
