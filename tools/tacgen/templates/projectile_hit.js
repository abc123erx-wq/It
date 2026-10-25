import { world, Player } from "@minecraft/server";

/**
 * Dano dos projéteis com modificador de facção.
 * policial  + arma oficial  -> 1.05  (treinamento e mira)
 * policial  + arma de facção-> 0.70  (arma desconhecida / sem manutenção)
 * ladrão    + arma de facção-> 1.10  (poder de parada)
 * ladrão    + arma oficial  -> 0.75
 */
const POLICE_GUNS = new Set(__POLICE_WEAPONS__);
const CRIME_GUNS = new Set(__CRIME_WEAPONS__);

function multiplicador(player, gunId) {
    const policia = player.hasTag("policia");
    const ladrao = player.hasTag("ladrao");
    if (!policia && !ladrao) return 1;
    const oficial = POLICE_GUNS.has(gunId);
    const faccao = CRIME_GUNS.has(gunId);
    if (policia) return oficial ? 1.05 : faccao ? 0.7 : 1;
    return faccao ? 1.1 : oficial ? 0.75 : 1;
}

world.afterEvents.projectileHitEntity.subscribe((data) => {
    const { projectile, source: player } = data;

    if (!(player instanceof Player)) return;

    const entity = data.getEntityHit().entity;
    if (!entity) return;

    const health = entity.getComponent("health");
    if (!health) return;

    const bulletId = projectile.typeId.replace("bullet:", "");
    const bullet = tacg.bullets[bulletId];

    if (!bullet) return;

    const dano = bullet.damage * multiplicador(player, bulletId);
    const newHealth = Math.max(0, health.currentValue - dano);

    health.setCurrentValue(newHealth);
});
