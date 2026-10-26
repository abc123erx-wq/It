import { world, system, ItemStack, EquipmentSlot } from "@minecraft/server";

/**
 * SISTEMA DE TIRO E RECARGA (script)
 * ---------------------------------------------------------------
 * O TacGuns original dispara por uma cadeia de controllers de animação que
 * depende de `q.is_using_item`, `q.mark_variant` e de várias functions. Em
 * versões novas essa cadeia falha e a arma "não faz nada".
 *
 * Este módulo assume o controle: o script conta o pente, gasta a munição,
 * recarrega e cospe a bala (`bullet:<arma>`), que continua sendo resolvida pelo
 * `projectileHitEntity.js` (dano da tabela + multiplicador de facção).
 */

const ARMAS = __TABLE__;

const LEGADO = {
    ak47: "762x39mm", coltpython: "357magnum", awp: "338lapua", deagle: "50ae",
    glock17: "9x19mm", m134: "308winchester", mk18: "556x45mm", m870: "12gauge",
    db: "12gauge", dp28: "762x54mmr",
};

const segurando = new Map();     // playerId -> { arma, proximo }
const recarregando = new Set();  // playerId

function valido(entidade) {
    try {
        if (!entidade) return false;
        const v = entidade.isValid;
        return typeof v === "function" ? v.call(entidade) : v !== false;
    } catch (e) {
        return false;
    }
}

function obj(nome) {
    let o = world.scoreboard.getObjective(nome);
    if (!o) o = world.scoreboard.addObjective(nome, nome);
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

function definirPente(player, arma, valor) {
    const o = obj(arma);
    try {
        o.setScore(player, valor);
    } catch (e) {
        try {
            o.addScore(player, valor - pontos(arma, player));
        } catch (e2) { }
    }
}

function aviso(player, texto) {
    try {
        player.onScreenDisplay.setActionBar(texto);
    } catch (e) { }
}

function armaNaMao(player) {
    try {
        const mao = player.getComponent("minecraft:equippable")?.getEquipment(EquipmentSlot.Mainhand);
        if (!mao || !mao.typeId || !mao.typeId.startsWith("tac_guns:")) return undefined;
        const id = mao.typeId.slice(9).replace("_emp", "");
        if (!ARMAS[id]) return undefined;
        return { id, vazia: mao.typeId.endsWith("_emp"), dados: ARMAS[id] };
    } catch (e) {
        return undefined;
    }
}

function contarMunicao(player, ammoId) {
    let total = 0;
    try {
        const inv = player.getComponent("minecraft:inventory");
        const container = inv?.container;
        if (!container) return 0;
        for (let i = 0; i < container.size; i++) {
            const item = container.getItem(i);
            if (item && item.typeId === ammoId) total += item.amount;
        }
    } catch (e) { }
    return total;
}

function trocarItem(player, novo) {
    try {
        const equip = player.getComponent("minecraft:equippable");
        if (equip) equip.setEquipment(EquipmentSlot.Mainhand, new ItemStack(novo, 1));
    } catch (e) { }
}

function gastarMunicao(player, ammoId, quantidade) {
    let falta = quantidade;
    try {
        const container = player.getComponent("minecraft:inventory")?.container;
        if (!container) return 0;
        for (let i = 0; i < container.size && falta > 0; i++) {
            const item = container.getItem(i);
            if (!item || item.typeId !== ammoId) continue;
            const usar = Math.min(item.amount, falta);
            falta -= usar;
            if (item.amount - usar <= 0) {
                container.setItem(i, undefined);
            } else {
                item.amount -= usar;
                container.setItem(i, item);
            }
        }
    } catch (e) { }
    return quantidade - falta;
}

// ------------------------------------------------------------------ disparo
function disparar(player, id, dados) {
    const pente = pontos(id, player);
    if (pente <= 0) {
        aviso(player, "§cPente vazio §7— agache e use para recarregar");
        try {
            player.playSound("note.bass", { pitch: 0.7, volume: 0.4 });
        } catch (e) { }
        return false;
    }

    let dir;
    try {
        dir = player.getViewDirection();
    } catch (e) {
        return false;
    }
    let base;
    try {
        base = player.getHeadLocation();
    } catch (e) {
        base = player.location;
    }
    const pos = { x: base.x + dir.x * 1.0, y: base.y - 0.12 + dir.y * 1.0,
                  z: base.z + dir.z * 1.0 };

    try {
        const bala = player.dimension.spawnEntity(`bullet:${id}`, pos);
        try {
            bala.triggerEvent(`${id}:nsight`);
        } catch (e) { }
        system.runTimeout(() => {
            try {
                if (!valido(bala)) return;
                const v = bala.getVelocity();
                const parada = Math.abs(v.x) + Math.abs(v.y) + Math.abs(v.z) < 0.05;
                if (parada) {
                    bala.getComponent("minecraft:projectile")?.shoot(dir);
                }
            } catch (e) { }
        }, 1);
    } catch (e) {
        // se a entidade da bala falhar, aplica dano direto no alvo mais próximo
        try {
            const alvo = player.getEntitiesFromViewDirection({ maxDistance: 60 })[0]?.entity;
            if (alvo) {
                const vida = alvo.getComponent("minecraft:health");
                if (vida) {
                    const dano = (typeof tacg !== "undefined" && tacg.bullets?.[id]?.damage) || dados.dano || 5;
                    vida.setCurrentValue(Math.max(0, vida.currentValue - dano));
                }
            }
        } catch (e2) { }
    }

    try {
        player.playAnimation(`animation.${id}.shoot.nsight`, { blendOutTime: 0.05 });
    } catch (e) { }
    try {
        player.playSound(`${id}.shoot`, { volume: 0.9, pitch: 1.0 });
    } catch (e) { }
    try {
        player.runCommand("camerashake add @s 0.03 0.12 rotational");
    } catch (e) { }

    const restante = pente - 1;
    definirPente(player, id, restante);
    if (restante <= 0) {
        trocarItem(player, `tac_guns:${id}_emp`);
        aviso(player, "§cPente vazio");
    }
    return true;
}

// ------------------------------------------------------------------ recarga
function recarregar(player, id, dados, silencioso) {
    if (recarregando.has(player.id)) return;
    const cheio = pontos(id, player);
    const capacidade = dados.mag;
    if (cheio >= capacidade) {
        if (!silencioso) aviso(player, "§7Pente já está cheio");
        return;
    }
    const disponivel = contarMunicao(player, dados.ammo);
    if (disponivel <= 0) {
        if (!silencioso) {
            aviso(player, `§cSem munição §7(${dados.ammo.replace("tac_guns:", "")})`);
            try {
                player.playSound("note.bass", { pitch: 0.8, volume: 0.4 });
            } catch (e) { }
        }
        return;
    }

    recarregando.add(player.id);
    try {
        player.playAnimation(`animation.${id}.reload`, { blendOutTime: 0.2 });
    } catch (e) { }
    try {
        player.playSound(`${id}.reload`, { volume: 1.0 });
    } catch (e) { }
    aviso(player, `§7Recarregando §f${dados.nome}§7...`);

    const demora = Math.max(14, Math.round(dados.recarga * 20));
    system.runTimeout(() => {
        recarregando.delete(player.id);
        try {
            if (!valido(player)) return;
            const atual = pontos(id, player);
            const inv = contarMunicao(player, dados.ammo);
            const usar = Math.min(capacidade - atual, inv);
            if (usar <= 0) return;
            const gasto = gastarMunicao(player, dados.ammo, usar);
            definirPente(player, id, atual + gasto);
            // se o item na mão estiver na variante vazia, volta para a cheia
            const mao = armaNaMao(player);
            if (mao && mao.vazia) trocarItem(player, `tac_guns:${id}`);
            aviso(player, `§aPente §f${atual + gasto}§7/${capacidade} §8· ` +
                `§emunição na mochila §f${inv - gasto}`);
        } catch (e) { }
    }, demora);
}

// ------------------------------------------------------------- gatilhos
world.afterEvents.itemStartUse.subscribe(({ itemStack, source }) => {
    try {
        if (!source || !itemStack) return;
        const estado = armaNaMao(source);
        if (!estado) return;
        const { id, dados } = estado;

        // agachado = recarregar; pente vazio = recarregar
        if (source.isSneaking || pontos(id, source) <= 0) {
            recarregar(source, id, dados);
            return;
        }
        if (disparar(source, id, dados) && dados.auto) {
            segurando.set(source.id, { arma: id, proximo: Date.now() + dados.cadencia });
        }
    } catch (e) { }
});

world.afterEvents.itemStopUse.subscribe(({ source }) => {
    try {
        if (source) segurando.delete(source.id);
    } catch (e) { }
});

system.runInterval(() => {
    const agora = Date.now();
    for (const [idJogador, estado] of [...segurando.entries()]) {
        const player = world.getAllPlayers().find((p) => p.id === idJogador);
        if (!player || !valido(player)) {
            segurando.delete(idJogador);
            continue;
        }
        const mao = armaNaMao(player);
        if (!mao || mao.id !== estado.arma) {
            segurando.delete(idJogador);
            continue;
        }
        const dados = mao.dados;
        if (pontos(mao.id, player) <= 0) {
            segurando.delete(idJogador);
            continue;
        }
        if (agora < estado.proximo) continue;
        if (disparar(player, mao.id, dados)) {
            estado.proximo = agora + dados.cadencia;
        } else {
            segurando.delete(idJogador);
        }
    }
}, 1);

// recarga manual por comando e por tecla de agachar + uso (antes do itemUse)
world.beforeEvents.itemUse.subscribe((evento) => {
    const player = evento.source;
    if (!player) return;
    try {
        const mao = armaNaMao(player);
        if (!mao) return;
        // deixa o uso seguir para disparar/recarregar via itemStartUse
    } catch (e) { }
});

world.afterEvents.playerSpawn.subscribe(({ player }) => {
    try {
        system.runTimeout(() => {
            if (!valido(player)) return;
            const mao = armaNaMao(player);
            if (mao) return;
        }, 60);
    } catch (e) { }
});

// --------------------------------------------------------------- comandos
system.afterEvents.scriptEventReceive.subscribe((ev) => {
    const player = ev.sourceEntity;
    if (!player || player.typeId !== "minecraft:player") return;
    try {
        if (ev.id === "tac_guns:recarregar") {
            const mao = armaNaMao(player);
            if (mao) recarregar(player, mao.id, mao.dados);
            else aviso(player, "§7Segure uma arma do TacGuns.");
        } else if (ev.id === "tac_guns:teste") {
            const mao = armaNaMao(player);
            if (!mao) {
                player.sendMessage("§cSegure uma arma do TacGuns para testar.");
                return;
            }
            definirPente(player, mao.id, mao.dados.mag);
            const ok = disparar(player, mao.id, mao.dados);
            player.sendMessage(
                `§6Teste: §f${mao.dados.nome}\n` +
                `§7Item: §f${mao.vazia ? "vazio" : "cheio"}§7 · Pente: §f${pontos(mao.id, player)}` +
                `§7/${mao.dados.mag}\n` +
                `§7Munição na mochila: §f${contarMunicao(player, mao.dados.ammo)} ` +
                `§8(${mao.dados.ammo})§7 · Tiro: ${ok ? "§aok" : "§cfalhou"}`);
        }
    } catch (e) {
        try {
            player.sendMessage("§cErro no sistema de armas: " + e);
        } catch (e2) { }
    }
});
