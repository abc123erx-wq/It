import { world, Player } from "@minecraft/server";

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

    const newHealth = Math.max(
        0,
        health.currentValue - bullet.damage
    );

    health.setCurrentValue(newHealth);
});