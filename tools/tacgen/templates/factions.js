import { world, system, ItemStack, EquipmentSlot } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";

/**
 * CAMADA DE FACCOES — Policial x Ladrao
 * -------------------------------------------------------------
 * - Tela inicial de escolha de lado (abre no primeiro spawn)
 * - Arsenal restrito: cada lado so dispara as armas do seu lado
 * - Economia: dinheiro por abates, assaltos e patrulha
 * - Loja de armamento (/scriptevent tac_guns:loja)
 * - Apreensao: abater alguem do lado oposto toma a arma dele
 * - Recuo por lado: policial treinado chacoalha menos a camera
 */

const OBJ_MONEY = "dinheiro";
const OBJ_KILLS = "abates";
const OBJ_REP = "reputacao";
const OBJ_SIDE = "faccao";
const OBJ_HUD = "faccao_hud";
const OBJ_WANTED = "procurado";
const ALGEMAS = "tac_guns:algemas";
const PROP_CELA = "tac_guns:cela";

const POLICIA = {
    id: "policia",
    tag: "policia",
    nome: "POLICIAL",
    cor: "§9",
    icone: "textures/ui/policial",
    lema: "PROTEJA A CIDADE",
    lema2: "MANTENHA A ORDEM",
    corTitulo: "§9§l",
    kit: ["tac_guns:pt92_emp", "tac_guns:9x19mm"],
    kitQtd: [1, 60],
};

const LADRAO = {
    id: "ladrao",
    tag: "ladrao",
    nome: "LADRÃO",
    cor: "§4",
    icone: "textures/ui/ladrao",
    lema: "FAÇA SEU DINHEIRO",
    lema2: "DESAFIE A LEI",
    corTitulo: "§4§l",
    kit: ["tac_guns:tec9_emp", "tac_guns:9x19mm"],
    kitQtd: [1, 60],
};


// armas exclusivas (gerado a partir do catalogo)
const ARMAS_POLICIA = new Set(__POLICE_WEAPONS__);
const ARMAS_LADRAO = new Set(__CRIME_WEAPONS__);

// arma -> preco na loja de campanha
const LOJA = __SHOP__;

// patentes: reputação sobe com abates e ações do lado
const PATENTES = {
    policia: ["Recruta", "Soldado", "Cabo", "Sargento", "Tenente", "Capitão", "Coronel"],
    ladrao: ["Verme", "Aviãozinho", "Olheiro", "Soldado do morro", "Gerente", "Fogueteiro", "Dono"],
};

const RECUO = {
    policia: 0.022,   // treinamento: recuo controlado
    ladrao: 0.058,    // arma velha e sem culatra compensada
};

// ---------------------------------------------------------------- utilidades
function valido(entidade) {
    try {
        if (!entidade) return false;
        const v = entidade.isValid;
        return typeof v === "function" ? v.call(entidade) : v !== false;
    } catch (e) {
        return false;
    }
}

function obj(nome, display) {
    let o = world.scoreboard.getObjective(nome);
    if (!o) o = world.scoreboard.addObjective(nome, display);
    return o;
}

function pontos(nome, alvo) {
    const o = world.scoreboard.getObjective(nome);
    if (!o) return 0;
    try {
        return o.getScore(alvo) ?? 0;
    } catch (e) {
        return 0;
    }
}

function addPontos(nome, alvo, valor) {
    const o = obj(nome, nome);
    try {
        o.addScore(alvo, valor);
    } catch (e) {
        o.setScore(alvo, valor);
    }
}

function ladoDe(player) {
    if (player.hasTag(POLICIA.tag)) return POLICIA;
    if (player.hasTag(LADRAO.tag)) return LADRAO;
    return undefined;
}

function idArma(typeId) {
    if (!typeId || !typeId.startsWith("tac_guns:")) return undefined;
    return typeId.slice("tac_guns:".length).replace("_emp", "");
}

function donoDaArma(typeId) {
    const id = idArma(typeId);
    if (!id) return undefined;
    if (ARMAS_POLICIA.has(id)) return "policia";
    if (ARMAS_LADRAO.has(id)) return "ladrao";
    return undefined;
}

function ehArma(typeId) {
    return donoDaArma(typeId) !== undefined;
}

function dinheiro(player) {
    return pontos(OBJ_MONEY, player);
}

function pagar(player, valor) {
    addPontos(OBJ_MONEY, player, valor);
    if (valor > 0) player.playSound("random.orb", { pitch: 1.4, volume: 0.6 });
}

function patente(player) {
    const lado = ladoDe(player);
    if (!lado) return "—";
    const lista = PATENTES[lado.id];
    const rep = pontos(OBJ_REP, player);
    return lista[Math.min(lista.length - 1, Math.floor(rep / 5))];
}

function aviso(player, texto) {
    player.onScreenDisplay.setActionBar(texto);
}

// ------------------------------------------------------------------ tela inicial
function telaDeEscolha(player, primeiraVez = true) {
    const dinheiroAtual = dinheiro(player);
    const form = new ActionFormData()
        .title("§lESCOLHA SEU LADO")
        .body(
            "§7LEI OU LIBERDADE?\n\n" +
            "§8Cada lado tem arsenal, economia e táticas próprias.\n" +
            "§8Armas do lado oposto não disparam nas suas mãos.\n\n" +
            (primeiraVez
                ? "§eEscolha com cuidado: dá para trocar depois, mas o dinheiro zera.\n" +
                  "§8Sem menu? /function lado_policial ou /function lado_ladrao"
                : `§7Seu dinheiro atual: §aR$ ${dinheiroAtual} §8(trocar de lado zera)`)
        )
        .button(`§9§lPOLICIAL\n§r§7${POLICIA.lema}`, POLICIA.icone)
        .button(`§4§lLADRÃO\n§r§7${LADRAO.lema}`, LADRAO.icone);

    form.show(player).then((res) => {
        if (res.canceled) {
            aviso(player, "§7Escolha seu lado: §e/scriptevent tac_guns:faccao");
            return;
        }
        const lado = res.selection === 0 ? POLICIA : LADRAO;
        system.run(() => escolher(player, lado, !primeiraVez));
    }).catch(() => {
        try {
            player.sendMessage("§6Escolha seu lado sem menu: §f/function lado_policial " +
                "§6ou §f/function lado_ladrao");
        } catch (e) { }
    });
}

function escolher(player, lado, limpando) {
    const anterior = ladoDe(player);
    if (anterior && anterior.id === lado.id) {
        aviso(player, `§7Você já é ${lado.cor}${lado.nome}§7.`);
        return;
    }
    if (anterior && limpando) {
        obj(OBJ_MONEY, OBJ_MONEY).setScore(player, 0);
        obj(OBJ_KILLS, OBJ_KILLS).setScore(player, 0);
        obj(OBJ_REP, OBJ_REP).setScore(player, 0);
    }
    player.removeTag(POLICIA.tag);
    player.removeTag(LADRAO.tag);
    player.addTag(lado.tag);

    const o = obj(OBJ_SIDE, "faccao");
    o.setScore(player, lado.id === "policia" ? 1 : 2);

    player.onScreenDisplay.setTitle(lado.corTitulo + lado.nome, {
        subtitle: `§7${lado.lema} · ${lado.lema2}`,
        fadeInDuration: 10,
        stayDuration: 60,
        fadeOutDuration: 20,
    });
    player.playSound(lado.id === "policia" ? "random.levelup" : "mob.wither.spawn",
        { volume: 0.5 });

    // kit inicial
    if (!player.hasTag("kit_" + lado.id)) {
        lado.kit.forEach((item, i) => {
            player.runCommand(`give @s ${item} ${lado.kitQtd[i]}`);
        });
        player.addTag("kit_" + lado.id);
    }

    aviso(player, `${lado.cor}${lado.nome}§f · arsenal e loja liberados`);
    atualizarHud(player);
    world.sendMessage(`§8[§6Facção§8] §f${player.name} entrou como ${lado.cor}${lado.nome}§f.`);
}

// ------------------------------------------------------------------------ loja
function abrirLoja(player) {
    const lado = ladoDe(player);
    if (!lado) {
        telaDeEscolha(player, false);
        return;
    }
    const itens = LOJA[lado.id] || [];
    const form = new ActionFormData()
        .title(`§lARSENAL ${lado.cor}${lado.nome}`)
        .body(`§7Caixa: §aR$ ${dinheiro(player)}\n§8Compra inclui 3 carregadores de munição.`);
    itens.forEach((it) => {
        form.button(`§e${it.nome} §8· §aR$ ${it.preco}\n§r§7${it.ammo.replace("tac_guns:", "")}`,
            it.icone);
    });
    form.button("§8Fechar");

    form.show(player).then((res) => {
        if (res.canceled || res.selection >= itens.length) return;
        const it = itens[res.selection];
        system.run(() => {
            const saldo = dinheiro(player);
            if (saldo < it.preco) {
                aviso(player, `§cFaltam R$ ${it.preco - saldo}`);
                player.playSound("note.bass", { pitch: 0.7 });
                return;
            }
            addPontos(OBJ_MONEY, player, -it.preco);
            player.runCommand(`give @s ${it.item} 1`);
            player.runCommand(`give @s ${it.ammo} ${it.municao}`);
            aviso(player, `§aComprado: §f${it.nome} §8(-R$ ${it.preco})`);
            player.playSound("random.anvil_use", { pitch: 1.2, volume: 0.5 });
            atualizarHud(player);
        });
    }).catch(() => {});
}

// ------------------------------------------------------- prisão e procurado
function celaSalva() {
    const bruto = world.getDynamicProperty(PROP_CELA);
    if (!bruto) return undefined;
    try {
        return JSON.parse(bruto);
    } catch (e) {
        return undefined;
    }
}

function levarParaCela(player) {
    const cela = celaSalva();
    if (!cela) {
        aviso(player, "§7Nenhuma cela marcada (§f/scriptevent tac_guns:marcar_cela§7).");
        return false;
    }
    try {
        const dim = world.getDimension(cela.dim || "overworld");
        player.teleport({ x: cela.x, y: cela.y, z: cela.z }, { dimension: dim });
        return true;
    } catch (e) {
        return false;
    }
}

function prender(policial, alvo) {
    if (alvo.hasTag("algemado")) {
        soltar(alvo);
        aviso(policial, `§a${alvo.name} liberado.`);
        return;
    }
    alvo.addTag("algemado");
    alvo.runCommand("effect @s slowness 60 3 true");
    alvo.runCommand("effect @s mining_fatigue 60 2 true");
    const foiPraCela = levarParaCela(alvo);
    obj(OBJ_WANTED, OBJ_WANTED).setScore(alvo, 0);
    pagar(policial, 250);
    addPontos(OBJ_REP, policial, 1);

    alvo.onScreenDisplay.setTitle("§4§lPRESO", {
        subtitle: "§7Você foi algemado pela polícia",
        fadeInDuration: 5,
        stayDuration: 40,
        fadeOutDuration: 10,
    });
    alvo.playSound("random.anvil_land", { volume: 0.5 });
    aviso(alvo, foiPraCela
        ? "§cVocê foi levado para a cela. §7Aguarde ou peça para ser liberado."
        : "§cVocê está algemado. §7Aguarde ser liberado pela polícia.");
    world.sendMessage(`§8[§6Facção§8] §9${policial.name}§f prendeu §4${alvo.name}§f.`);
    system.runTimeout(() => soltar(alvo, true), 20 * 60);
}

function soltar(player, automatico = false) {
    try {
        if (!player || !player.hasTag("algemado")) return;
    } catch (e) {
        return;
    }
    player.removeTag("algemado");
    try {
        player.runCommand("effect @s clear");
    } catch (e) { }
    if (automatico) aviso(player, "§aPrazo da prisão acabou — você está livre.");
}

function jogadorMaisProximo(policial) {
    let melhor;
    let menor = 4.0;
    world.getAllPlayers().forEach((outro) => {
        if (outro.id === policial.id) return;
        if (outro.dimension.id !== policial.dimension.id) return;
        const dx = outro.location.x - policial.location.x;
        const dy = outro.location.y - policial.location.y;
        const dz = outro.location.z - policial.location.z;
        const d = Math.sqrt(dx * dx + dy * dy + dz * dz);
        if (d < menor && !outro.hasTag(POLICIA.tag)) {
            menor = d;
            melhor = outro;
        }
    });
    return melhor;
}

// nível de procurado: sobe com crimes, decai com o tempo e brilha o procurado
function addProcurado(player, valor) {
    if (!player.hasTag(LADRAO.tag)) return;
    const o = obj(OBJ_WANTED, OBJ_WANTED);
    o.addScore(player, valor);
    const nivel = pontos(OBJ_WANTED, player);
    if (nivel >= 3 && !player.hasTag("procurado_ativo")) {
        player.addTag("procurado_ativo");
        player.onScreenDisplay.setTitle("§4§lPROCURADO", {
            subtitle: `§7Nível ${nivel} — a polícia sabe onde você está`,
            fadeInDuration: 5,
            stayDuration: 40,
            fadeOutDuration: 10,
        });
        const p = player.location;
        world.getAllPlayers().filter((pl) => pl.hasTag(POLICIA.tag)).forEach((pl) => {
            pl.sendMessage(`§8[§9Polícia§8] §fProcurado: §4${player.name}§f — ` +
                `§7${Math.round(p.x)} ${Math.round(p.y)} ${Math.round(p.z)} §8(${player.dimension.id})`);
            pl.playSound("note.pling", { pitch: 1.6, volume: 0.6 });
        });
    }
}

// ------------------------------------------------------------------------- HUD
let hudLigado = false;

function atualizarHud(player) {
    const o = obj(OBJ_HUD, "§6§lFACÇÃO BRASIL");
    ["§aDinheiro", "§cAbates", "§eReputação", "§cProcurado", "§9Lado",
     "§9Policiais", "§4Ladrões"].forEach((linha) => {
        if (!o.hasParticipant(linha)) o.setScore(linha, 0);
    });
    if (!hudLigado) {
        try {
            world.scoreboard.setObjectiveAtDisplaySlot("sidebar", { objective: o });
            hudLigado = true;
        } catch (e) { }
    }
    refreshHud();
}

function refreshHud() {
    const o = obj(OBJ_HUD, "§6§lFACÇÃO BRASIL");
    const players = world.getAllPlayers();
    o.setScore("§9Policiais", players.filter((p) => p.hasTag(POLICIA.tag)).length);
    o.setScore("§4Ladrões", players.filter((p) => p.hasTag(LADRAO.tag)).length);
    const alvo = players.length === 1 ? players[0] : undefined;
    if (alvo) {
        const lado = ladoDe(alvo);
        o.setScore("§9Lado", lado ? (lado.id === "policia" ? 1 : 2) : 0);
        o.setScore("§aDinheiro", dinheiro(alvo));
        o.setScore("§cAbates", pontos(OBJ_KILLS, alvo));
        o.setScore("§eReputação", pontos(OBJ_REP, alvo));
        o.setScore("§cProcurado", pontos(OBJ_WANTED, alvo));
    }
}

// --------------------------------------------------------------- inicializacao
function iniciarJogador(player, inicial = true) {
    try {
        if (!valido(player)) return;
        obj(OBJ_MONEY, OBJ_MONEY);
        obj(OBJ_KILLS, OBJ_KILLS);
        obj(OBJ_REP, OBJ_REP);
        obj(OBJ_WANTED, OBJ_WANTED);
        obj(OBJ_SIDE, "faccao");
        atualizarHud(player);
        if (!ladoDe(player)) {
            telaDeEscolha(player, inicial);
        } else {
            const lado = ladoDe(player);
            aviso(player, `${lado.cor}${lado.nome}§f · ${patente(player)} §8| §aR$ ` +
                `${dinheiro(player)} §8| §eloja: §f/scriptevent tac_guns:loja`);
        }
    } catch (e) { }
}

world.afterEvents.playerSpawn.subscribe((evento) => {
    try {
        const player = evento.player;
        system.runTimeout(() => iniciarJogador(player, evento.initialSpawn !== false), 40);
    } catch (e) { }
});

// rede de seguranca: se o evento de spawn passar batido (ou o form falhar), a tela
// aparece assim mesmo quando o jogador ainda nao tem lado
const ultimaTela = new Map();
system.runInterval(() => {
    try {
        world.getAllPlayers().forEach((player) => {
            if (!valido(player) || ladoDe(player)) return;
            const agora = Date.now();
            if (agora - (ultimaTela.get(player.id) ?? 0) < 20000) return;
            ultimaTela.set(player.id, agora);
            telaDeEscolha(player, true);
        });
    } catch (e) { }
}, 20 * 6);

world.beforeEvents.itemUse.subscribe((event) => {
    // dentro de beforeEvents o jogo está em modo somente-leitura: aqui só decidimos,
    // qualquer efeito (som, mensagem, comando) é agendado com system.run
    const player = event.source;
    const item = event.itemStack;
    if (!player || !item || !item.typeId) return;
    const id = item.typeId;

    const ehArmaUsada = ehArma(id);
    if (!ehArmaUsada && id !== ALGEMAS) return;

    if (player.hasTag("algemado")) {
        event.cancel = true;
        system.run(() => aviso(player, "§cVocê está algemado — sem armas até ser liberado."));
        return;
    }

    if (id === ALGEMAS) {
        event.cancel = true;
        system.run(() => {
            if (!player.hasTag(POLICIA.tag)) {
                aviso(player, "§cAlgemas são equipamento policial.");
                return;
            }
            const alvo = jogadorMaisProximo(player);
            if (!alvo) {
                aviso(player, "§7Chegue mais perto de um suspeito (4 blocos).");
                return;
            }
            prender(player, alvo);
        });
        return;
    }

    // arma de facção na mão da polícia (ou vice-versa): não dispara
    if (player.hasTag(POLICIA.tag) &&
        (id === "tac_guns:att_tape_optic" || id === "tac_guns:att_dualmag")) {
        event.cancel = true;
        system.run(() => aviso(player, "§cKit improvisado é material de facção."));
        return;
    }

    const lado = ladoDe(player);
    if (!lado) return;
    const dono = donoDaArma(id);
    if (dono && dono !== lado.id) {
        event.cancel = true;
        system.run(() => {
            const nome = id.split(":")[1];
            aviso(player, `§c${nome} §7não é do seu lado — arma apreendida.`);
            try {
                player.playSound("note.bass", { pitch: 0.6, volume: 0.4 });
            } catch (e) { }
        });
    }
});

// -------------------------------------------------------------- recuo por lado
const ultimoPente = new Map();

system.runInterval(() => {
    world.getAllPlayers().forEach((player) => {
        const lado = ladoDe(player);
        if (!lado) return;
        let mao;
        try {
            mao = player.getComponent("minecraft:equippable")?.getEquipment(EquipmentSlot.Mainhand);
        } catch (e) {
            return;
        }
        const id = mao ? idArma(mao.typeId) : undefined;
        if (!id) {
            ultimoPente.delete(player.id);
            return;
        }
        const pente = pontos(id, player);
        const anterior = ultimoPente.get(player.id);
        ultimoPente.set(player.id, pente);
        if (anterior === undefined || pente >= anterior) return;
        // disparou: aplica o recuo característico do lado
        const forca = RECUO[lado.id] ?? 0.04;
        try {
            player.runCommand(`camerashake add @s ${forca} 0.12 rotational`);
        } catch (e) { }
    });
}, 2);

// ------------------------------------------------------- abates / apreensao
world.afterEvents.entityDie.subscribe(({ deadEntity, damageSource }) => {
    const killer = damageSource?.damagingEntity;
    if (!killer || killer.typeId !== "minecraft:player") return;
    const ladoKiller = ladoDe(killer);
    if (!ladoKiller) return;

    let alvo = deadEntity;
    if (alvo.typeId === "minecraft:player") {
        const ladoAlvo = ladoDe(alvo);
        if (!ladoAlvo || ladoAlvo.id === ladoKiller.id) return;
        // abate entre lados: recompensa + apreensão da arma
        pagar(killer, 400);
        addPontos(OBJ_KILLS, killer, 1);
        addPontos(OBJ_REP, killer, 1);
        addProcurado(killer, 4);
        apreender(alvo, killer);
        world.sendMessage(`§8[§6Facção§8] ${ladoKiller.cor}${killer.name}§f abateu ` +
            `${ladoAlvo.cor}${alvo.name}§f e apreendeu o armamento.`);
        return;
    }

    // NPCs hostis: patrulha x assalto
    let hostil = false;
    try {
        hostil = alvo.matches({ families: ["monster"] });
    } catch (e) { }
    if (hostil) {
        pagar(killer, ladoKiller.id === "policia" ? 40 : 25);
        addPontos(OBJ_KILLS, killer, 1);
        if (pontos(OBJ_KILLS, killer) % 5 === 0) addPontos(OBJ_REP, killer, 1);
        return;
    }
    if (alvo.typeId === "minecraft:villager" || alvo.typeId === "minecraft:villager_v2") {
        if (ladoKiller.id === "ladrao") {
            pagar(killer, 120);
            addProcurado(killer, 2);
            aviso(killer, "§aAssalto concluído §7+ R$ 120 §8· procurado +2");
        } else {
            pagar(killer, -100);
            aviso(killer, "§cConduta imprópria §7- R$ 100");
        }
    }
});

function apreender(vitima, vencedor) {
    try {
        const equip = vitima.getComponent("minecraft:equippable");
        const arma = equip?.getEquipment(EquipmentSlot.Mainhand);
        if (!arma || !ehArma(arma.typeId)) return;
        const id = idArma(arma.typeId);
        equip.setEquipment(EquipmentSlot.Mainhand, undefined);
        vitima.dimension.spawnItem(new ItemStack(arma.typeId, 1), vitima.location);
        try {
            obj(id, id).setScore(vitima, 0);
        } catch (e) { }
        aviso(vitima, "§cArma apreendida pelo lado oposto!");
        aviso(vencedor, "§aArma do oponente largada no chão.");
    } catch (e) { }
}

// ---------------------------------------------------------------- comandos
system.afterEvents.scriptEventReceive.subscribe((ev) => {
    const player = ev.sourceEntity;
    if (!player || player.typeId !== "minecraft:player") return;
    switch (ev.id) {
        case "tac_guns:faccao":
            telaDeEscolha(player, !ladoDe(player));
            break;
        case "tac_guns:loja":
            abrirLoja(player);
            break;
        case "tac_guns:marcar_cela": {
            if (!player.hasTag(POLICIA.tag)) {
                aviso(player, "§cSó a polícia marca a cela.");
                break;
            }
            const loc = player.location;
            world.setDynamicProperty(PROP_CELA, JSON.stringify({
                x: loc.x, y: loc.y, z: loc.z, dim: player.dimension.id,
            }));
            player.sendMessage(`§aCela marcada em §f${Math.round(loc.x)} ${Math.round(loc.y)} ` +
                `${Math.round(loc.z)} §7(${player.dimension.id}).`);
            break;
        }
        case "tac_guns:soltar": {
            soltar(player);
            aviso(player, "§aLiberado.");
            break;
        }
        case "tac_guns:info": {
            const lado = ladoDe(player);
            player.sendMessage(
                "§6§l=== FACÇÃO BRASIL ===\n" +
                `§7Lado: ${lado ? lado.cor + lado.nome : "§8nenhum"}\n` +
                `§7Dinheiro: §aR$ ${dinheiro(player)}\n` +
                `§7Abates: §c${pontos(OBJ_KILLS, player)}§7  ·  Patente: §e${patente(player)}\n` +
                `§7Procurado: §c${pontos(OBJ_WANTED, player)}§7  ·  Algemado: ` +
                `${player.hasTag("algemado") ? "§csim" : "§anao"}\n` +
                "§8/scriptevent tac_guns:faccao  §8/scriptevent tac_guns:loja"
            );
            break;
        }
        default:
            break;
    }
});

// decadência do nível de procurado e brilho em quem está na lista
system.runInterval(() => {
    const o = world.scoreboard.getObjective(OBJ_WANTED);
    if (!o) return;
    world.getAllPlayers().forEach((player) => {
        const nivel = pontos(OBJ_WANTED, player);
        if (nivel > 0) {
            o.setScore(player, Math.max(0, nivel - 1));
        }
        if (nivel >= 3) {
            try {
                player.runCommand("effect @s glowing 8 0 true");
            } catch (e) { }
        } else if (player.hasTag("procurado_ativo")) {
            player.removeTag("procurado_ativo");
        }
    });
}, 20 * 20);

system.runInterval(refreshHud, 100);
refreshHud();
