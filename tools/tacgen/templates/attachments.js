import { world, system } from "@minecraft/server";

/**
 * Acessorios modulares das armas brasileiras.
 * Agachado + usar o item instala a peca na arma equipada; repetir o gesto remove.
 * A peca aparece no modelo porque o render controller mostra o bone
 * correspondente quando a propriedade do jogador esta ligada.
 */
const ATTACHMENTS = __TABLE__;

world.afterEvents.itemUse.subscribe(({ itemStack, source: player }) => {
    const att = ATTACHMENTS[itemStack?.typeId];
    if (!att || !player.isSneaking) return;

    system.runTimeout(() => {
        const active = player.getProperty(att.prop);
        player.setProperty(att.prop, !active);
        player.playSound(active ? "random.break" : "random.click");
        player.onScreenDisplay.setActionBar(
            `\u00a7e${att.name}\u00a7f ${active ? "removido" : "instalado"}`
        );
        if (active) return;

        const inv = player.getComponent("minecraft:inventory")?.container;
        if (!inv) return;
        for (let slot = 0; slot < inv.size; slot++) {
            const item = inv.getItem(slot);
            if (item?.typeId !== itemStack.typeId) continue;
            if (item.amount > 1) {
                item.amount -= 1;
                inv.setItem(slot, item);
            } else {
                inv.setItem(slot, undefined);
            }
            break;
        }
    }, 1);
});
