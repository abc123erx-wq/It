import './events/projectileHitEntity.js';
import './global/global.js';
import {
    world,
    system
} from "@minecraft/server"

let guns = {
    "tac_guns:ak47": "tac_guns:762x39mm",
    "tac_guns:coltpython": "tac_guns:357magnum",
    "tac_guns:awp": "tac_guns:338lapua",
    "tac_guns:deagle": "tac_guns:50ae",
    "tac_guns:glock17": "tac_guns:9x19mm",
    "tac_guns:m134": "tac_guns:308winchester",
    "tac_guns:mk18": "tac_guns:556x45mm",
    "tac_guns:m870": "tac_guns:12gauge",
    "tac_guns:db": "tac_guns:12gauge",
    "tac_guns:dp28": "tac_guns:762x54mmr"
}

function getObj(obj) {
    if (!world.scoreboard.getObjective(obj)) {
        world.scoreboard.addObjective(obj)
    }
    return world.scoreboard.getObjective(obj)
}

function getDist(p1, p2) {
    return Math.sqrt(
        Math.pow(p1.x - p2.x, 2) +
        Math.pow(p1.y - p2.y, 2) +
        Math.pow(p1.z - p2.z, 2)
    )
}

let maxTemp = 100;
let cooling = 75;

system.runInterval(() => {
    world.getAllPlayers().forEach(player => {

        const direction = getMovementDirection(player);

        if (player.isSneaking) {
            system.runTimeout(() => {
                player.triggerEvent("tac_guns:nosway");
            }, 1);
        } else {
            switch (direction) {
                case "left":
                    player.triggerEvent("tac_guns:leftsway");
                    break;
                case "right":
                    player.triggerEvent("tac_guns:rightsway");
                    break;
                case "forward":
                case "backward":
                case undefined:
                    player.triggerEvent("tac_guns:nosway");
                    break;
            }
        }

        let gunTempObj = getObj(`m134_temp`);
        let gunUsage = getObj(`m134Usage`);

        if (gunUsage.addScore(player, 0) == 1 && gunTempObj.addScore(player, 0) < maxTemp) {
            gunTempObj.addScore(player, 1);

        } else if (gunUsage.addScore(player, 0) == 0 && gunTempObj.addScore(player, 0) > 0) {
            let result = Math.ceil(maxTemp / cooling);
            gunTempObj.addScore(player, -result);

        } else if (gunTempObj.addScore(player, 0) >= maxTemp && !player.hasTag("overheat")) {
            player.addTag("overheat");
            player.triggerEvent("tac_guns:reload");

            player.dimension.playSound(`m134.overheat`, player.location)

        } else if (player.hasTag("overheat") && gunTempObj.addScore(player, 0) == 0) {
            player.removeTag("overheat");
            player.triggerEvent("tac_guns:noreload");
        }

        let compo = player.getComponent("minecraft:inventory");
        let totalAmmo = 0;
        let itemMainHand = undefined;

        let component = player.getComponent("minecraft:equippable");
        itemMainHand = component?.getEquipment("Mainhand")?.typeId

        if (!itemMainHand) return;
        if (!(itemMainHand?.split("_emp")[0] in guns)) return;

        system.runTimeout(() => {
            let component = player.getComponent("minecraft:equippable")
            itemMainHand = component.getEquipment("Mainhand")?.typeId

            if (!itemMainHand) player.runCommand(`title @s actionbar xv`)

            if (!(itemMainHand?.split("_emp")[0] in guns)) player.runCommand(`title @s actionbar xv`)

        }, 1)

        let obj = getObj(`${itemMainHand.split("_emp")[0]}_ammo`)
        obj.setScore(player, 0)

        let ammoForGun = guns[`${itemMainHand.split("_emp")[0]}`]

        for (let slot = 0; slot < compo?.container?.size; slot++) {
            let item = compo?.container.getItem(slot)

            if (item?.typeId == ammoForGun) {
                totalAmmo += item.amount
            }
        }

        if (itemMainHand.split("_emp")[0] == "tac_guns:m134") {
            getObj("m134").setScore(player, totalAmmo)
        }

        obj = getObj(`${itemMainHand.split("_emp")[0]}_ammo`)
        obj.setScore(player, totalAmmo)

        let objId = `${itemMainHand.split(":")[1].split("_emp")[0]}`

        let ammo = getObj(objId).addScore(player, 0)
        let ammoInInv = totalAmmo

        if (ammo < 10) {
            ammo = `00${ammo}`
        } else if (ammo < 100) {
            ammo = `0${ammo}`
        } else {
            ammo = String(ammo)
        }

        if (ammoInInv < 10) {
            ammoInInv = `00${ammoInInv}`
        } else if (ammoInInv < 100) {
            ammoInInv = `0${ammoInInv}`
        } else {
            ammoInInv = String(ammoInInv)
        }

        let temp = 0
        temp = gunTempObj.addScore(player, 0)
        if (temp > 0 && !player.hasTag("overheat")) {
            temp = Math.floor((temp / maxTemp) * 100)
        } else if (player.hasTag("overheat")) {
            temp = 200 - Math.floor((temp / maxTemp) * 100)
        }

        if (temp < 10) {
            temp = `00${temp}`
        } else if (temp < 100) {
            temp = `0${temp}`
        } else {
            temp = String(temp)
        }

        if (Number(ammoInInv) > 999) {
            ammoInInv = "999"
        }

        if (itemMainHand.split("_emp")[0] == "tac_guns:m134") {
            player.runCommand(`title @s actionbar xv${ammoInInv}m${temp}`)

        } else {
            compo = player.getComponent("minecraft:mark_variant")
            if (compo.value == 2 || compo.value == 1) return;

            player.runCommand(`title @s actionbar xv${ammo}b${ammoInInv}`)
        }
    })
})

world.beforeEvents.itemUse.subscribe(({ itemStack: item, source: player, cancel }) => {

    if (item?.typeId == "tac_guns:m134") {
        if (player.hasTag("overheat")) cancel = true

        system.runTimeout(() => {
            let gunTempObj = getObj(`m134_temp`)
            if (gunTempObj.addScore(player, 0) > maxTemp && !player.hasTag("overheat")) {
                player.addTag("overheat")
            }
        })
    }
})

world.afterEvents.itemStartUse.subscribe(({ itemStack: item, source: player }) => {

    let obj = getObj(`m134Usage`)
    let ammoObj = getObj(`m134`)

    if (item?.typeId === "tac_guns:m134" && ammoObj.getScore(player) > 0) {
        obj.addScore(player, 1)
    } else {
        obj.setScore(player, 0)
    }
})

world.afterEvents.itemStopUse.subscribe(({ itemStack: item, source: player }) => {

    if (item?.typeId === "tac_guns:m134") {
        let obj = getObj(`m134Usage`)
        obj.setScore(player, 0)
    }
})

system.runInterval(() => {
    world.getAllPlayers().forEach(player => {
        let itemMainHand = player.getComponent("minecraft:equippable")?.getEquipment("Mainhand")?.typeId;

        if (itemMainHand?.split("_emp")[0] == "tac_guns:m134") {
            player.playSound(`m134.barrel`);
        }
    });
}, 166);

/**
 * 
 * @param {Player} player 
 * @returns {string}
 */
function getMovementDirection(player) {
    const vector = player.inputInfo.getMovementVector();
    if (vector.x == 0 && vector.y == 0) return;
    if (Math.abs(vector.x) > Math.abs(vector.y)) {
        return vector.x > 0 ? 'left' : 'right'
    } else {
        return vector.y > 0 ? 'forward' : 'backward'
    }
}

// Grenade throw test
system.runInterval(() => {
    world.getAllPlayers().forEach(player => {
        if (player.hasTag("test")) {
            player.removeTag("test");
            let grenade = player.dimension.spawnEntity("tac_guns:m67_grenade_thrown", player.location);
            grenade.getComponent("projectile").shoot(player.getViewDirection());
        } else if (player.hasTag("test_flash")) {
            player.removeTag("test_flash");
            let flashGrenade = player.dimension.spawnEntity("tac_guns:flash_grenade_thrown", player.location);
            flashGrenade.getComponent("projectile").shoot(player.getViewDirection());
        } else if (player.hasTag("test_impact_flash")) {
            player.removeTag("test_impact_flash");
            let impactFlashGrenade = player.dimension.spawnEntity("tac_guns:impact_flash_grenade_thrown", player.location);
            impactFlashGrenade.getComponent("projectile").shoot(player.getViewDirection());
        }
    });

    const overworld = world.getDimension("overworld");

    // M67 grenade smoke particles with bounds check
    overworld.getEntities({ type: "tac_guns:m67_grenade_thrown" }).forEach(grenade => {
        const loc = grenade.location;
        if (loc.y >= 0 && loc.y <= 319) {
            try {
                overworld.spawnParticle("minecraft:basic_smoke_particle", loc);
            } catch (e) {
            }
        }
    });

    // Flash grenade smoke particles with bounds check
    overworld.getEntities({ type: "tac_guns:flash_grenade_thrown" }).forEach(flashGrenade => {
        const loc = flashGrenade.location;
        if (loc.y >= 0 && loc.y <= 319) {
            try {
                overworld.spawnParticle("minecraft:basic_smoke_particle", loc);
            } catch (e) {
                console.warn(`Failed to spawn particle at (${loc.x}, ${loc.y}, ${loc.z}):`, e);
            }
        }
    });

    // Impact flash grenade smoke particles with bounds check
    overworld.getEntities({ type: "tac_guns:impact_flash_grenade_thrown" }).forEach(impactFlashGrenade => {
        const loc = impactFlashGrenade.location;
        if (loc.y >= 0 && loc.y <= 319) {
            try {
                overworld.spawnParticle("minecraft:basic_smoke_particle", loc);
            } catch (e) {
                console.warn(`Failed to spawn particle at (${loc.x}, ${loc.y}, ${loc.z}):`, e);
            }
        }
    });
});

const triggeredFlashGrenades = new Set();

// Grenade bounce
world.afterEvents.projectileHitBlock.subscribe(event => {
    let proj = event.projectile;
    let vector = event.hitVector;
    let location = event.location;
    let blockHitInfo = event.getBlockHit();

    // Check for all grenade types
    if (!["tac_guns:m67_grenade_thrown", "tac_guns:flash_grenade_thrown", "tac_guns:impact_flash_grenade_thrown"].includes(proj?.typeId)) return;

    let velocity = proj.getVelocity();

    if (!blockHitInfo?.block) return;

    let faceLocation = blockHitInfo.faceLocation;

    let hitDiff = blockHitInfo.block.location;
    hitDiff.x -= location.x;
    hitDiff.y -= location.y;
    hitDiff.z -= location.z;

    let newVelocity = {
        x: (Math.floor(velocity.x * 10) / 10) / 1.15,
        y: (Math.floor(velocity.y * 10) / 10) / 1.15,
        z: (Math.floor(velocity.z * 10) / 10) / 1.15,
    };

    if (Math.abs(faceLocation.x) == 1) newVelocity.x = -(Math.floor(newVelocity.x * 10) / 10) / 2.5;
    if (Math.abs(faceLocation.y) == 1) newVelocity.y = -(Math.floor(newVelocity.y * 10) / 10) / 2.5;
    if (Math.abs(faceLocation.z) == 1) newVelocity.z = -(Math.floor(newVelocity.z * 10) / 10) / 2.5;

    proj.clearVelocity();
    proj.applyImpulse(newVelocity);

    // Flash and impact flash grenade delayed effect
    if (["tac_guns:flash_grenade_thrown", "tac_guns:impact_flash_grenade_thrown"].includes(proj.typeId)) {
        let grenadeId = proj.id;

        if (!triggeredFlashGrenades.has(grenadeId)) {
            triggeredFlashGrenades.add(grenadeId);

            // Set delay based on grenade type
            const delayTicks = proj.typeId === "tac_guns:impact_flash_grenade_thrown" ? 1 : 100;

            system.runTimeout(() => {
                // Run the command AS the entity (the grenade itself)
                proj.runCommand(`camera @a[r=10] fade time 0 5 1 color 255 255 255`);
                proj.runCommand(`playsound flash_grenade.ring @a[r=10]`);
                proj.runCommand(`playsound flash_grenade.explosion @a[r=45]`);
                proj.runCommand(`particle minecraft:egg_destroy_emitter`);
                proj.runCommand(`particle minecraft:knockback_roar_particle`);
                proj.remove()
            }, delayTicks);
        }
    }
});

function workbenchUI(player, state) {
    if (!state) {
        player.removeTag("inWorkbench");
        player.inputPermissions.setPermissionCategory(1, true);
        player.inputPermissions.setPermissionCategory(2, true);
        player.triggerEvent("tac_guns:noreload");
        player.setProperty("tac_guns:item", false);
        player.runCommand("hud @s reset crosshair");
        player.runCommand("gamerule sendcommandfeedback true");
    } else {
        player.addTag("inWorkbench");
        player.inputPermissions.setPermissionCategory(1, false);
        player.inputPermissions.setPermissionCategory(2, false);
        player.triggerEvent("tac_guns:workbench_ui");
        player.runCommand("hud @s hide crosshair");
        player.runCommand("gamerule sendcommandfeedback false");
    }
}

let recipes = {
    0: {
        default: {
            items: {
                "minecraft:iron_ingot": 38,
                "minecraft:lapis_lazuli": 6,
                "minecraft:oak_log": 8
            },
            result: {
                "tac_guns:ak47_emp": 1
            }
        },
        2: {
            items: {
                "minecraft:gold_ingot": 8,
                "minecraft:iron_ingot": 58,
                "minecraft:quartz": 4
            },
            result: {
                "tac_guns:mk18_emp": 1
            }
        }
    },
    1: {
        default: {
            items: {
                "minecraft:iron_ingot": 62,
                "minecraft:lapis_lazuli": 10,
                "minecraft:oak_log": 10
            },
            result: {
                "tac_guns:dp28_emp": 1
            }
        },
        2: {
            items: {
                "minecraft:netherite_ingot": 2,
                "minecraft:diamond": 16,
                "minecraft:gold_ingot": 60,
                "minecraft:iron_ingot": 300,
                "minecraft:nether_star": 1
            },
            result: {
                "tac_guns:m134": 1
            }
        }
    },
    2: {
        default: {
            items: {
                "minecraft:diamond": 2,
                "minecraft:gold_ingot": 6,
                "minecraft:iron_ingot": 60,
                "minecraft:blaze_rod": 1
            },
            result: {
                "tac_guns:deagle_emp": 1
            }
        },
        2: {
            items: {
                "minecraft:iron_ingot": 18
            },
            result: {
                "tac_guns:glock17_emp": 1
            }
        },
        3: {
            items: {
                "minecraft:gold_ingot": 5,
                "minecraft:iron_ingot": 40,
                "minecraft:quartz": 2
            },
            result: {
                "tac_guns:coltpython_emp": 1
            }
        }
    },
    3: {
        default: {
            items: {
                "minecraft:iron_ingot": 45,
                "minecraft:lapis_lazuli": 7,
                "minecraft:oak_log": 7
            },
            result: {
                "tac_guns:m870_emp": 1
            }
        },
        2: {
            items: {
                "minecraft:iron_ingot": 12,
                "minecraft:oak_log": 4
            },
            result: {
                "tac_guns:db_emp": 1
            }
        }
    },
    4: {
        default: {
            items: {
                "minecraft:diamond": 10,
                "minecraft:gold_ingot": 50,
                "minecraft:iron_ingot": 250,
                "minecraft:blaze_rod": 5
            },
            result: {
                "tac_guns:awp_emp": 1
            }
        }
    },
    6: {
        default: {
            items: {
                "minecraft:iron_ingot": 3,
                "minecraft:gunpowder": 6,
                "minecraft:iron_nugget": 18
            },
            result: {
                "tac_guns:12gauge": 18
            }
        },
        2: {
            items: {
                "minecraft:iron_ingot": 6,
                "minecraft:lapis_lazuli": 1,
                "minecraft:gunpowder": 10
            },
            result: {
                "tac_guns:762x54mmr": 50
            }
        },
        3: {
            items: {
                "minecraft:iron_ingot": 3,
                "minecraft:gunpowder": 2
            },
            result: {
                "tac_guns:556x45mm": 60
            }
        },
        4: {
            items: {
                "minecraft:iron_ingot": 2,
                "minecraft:gunpowder": 2
            },
            result: {
                "tac_guns:9x19mm": 60
            }
        },
        5: {
            items: {
                "minecraft:iron_ingot": 6,
                "minecraft:lapis_lazuli": 1,
                "minecraft:gunpowder": 12
            },
            result: {
                "tac_guns:308winchester": 60
            }
        },
        6: {
            items: {
                "minecraft:iron_ingot": 6,
                "minecraft:lapis_lazuli": 1,
                "minecraft:gunpowder": 10
            },
            result: {
                "tac_guns:338lapua": 24
            }
        },
        7: {
            items: {
                "minecraft:iron_ingot": 5,
                "minecraft:gunpowder": 6
            },
            result: {
                "tac_guns:357magnum": 48
            }
        },
        8: {
            items: {
                "minecraft:iron_ingot": 6,
                "minecraft:lapis_lazuli": 1,
                "minecraft:gunpowder": 10
            },
            result: {
                "tac_guns:50ae": 48
            }
        },
        9: {
            items: {
                "minecraft:iron_ingot": 3,
                "minecraft:gunpowder": 2
            },
            result: {
                "tac_guns:762x39mm": 45
            }
        },
        10: {
            items: {
                "minecraft:iron_ingot": 6,
                "minecraft:gunpowder": 3
            },
            result: {
                "tac_guns:m67_grenade": 1
            }
        }
    }
};

function getCurrentRecipe(player) {
    let slot = player.selectedSlotIndex;
    let slotRecipes = recipes[slot];
    if (!slotRecipes) return null;
    if (typeof slotRecipes === 'object' && slotRecipes.hasOwnProperty('default')) {
        let itemtab = player.getProperty("tac_guns:itemtab");
        return slotRecipes[itemtab] || slotRecipes.default;
    } else {
        return slotRecipes;
    }
}

world.beforeEvents.playerInteractWithBlock.subscribe(event => {
    let block = event.block;
    let player = event.player;

    if (!event.isFirstEvent) return;

    system.runTimeout(() => {
        if (block?.typeId == "tac_guns:workbench") {
            if (!player.hasTag("inWorkbench") && player.selectedSlotIndex !== 7 && player.selectedSlotIndex !== 8) {
                workbenchUI(player, true);
            } else if (player.selectedSlotIndex === 7 || player.selectedSlotIndex === 8) {
                player.playSound("random.click");
            }
        } else if (block?.typeId == "tac_guns:invis_block" && player.hasTag("inWorkbench")) {
            let recipe = getCurrentRecipe(player);
            if (!recipe) {
                player.playSound("random.click");
                return;
            }

            let craftable = checkCraftable(player);

            if (!craftable) {
                return;
            }
            player.triggerEvent("tac_guns:build");
            player.playSound("random.click");

            let container = player.getComponent("minecraft:inventory")?.container;
            let checksPassed = 0;

            // Deduct items from inventory
            for (let itemId in recipe.items) {
                let cost = recipe.items[itemId];
                let remainingCost = cost;

                for (let slot = 0; slot < container.size; slot++) {
                    let item = container.getItem(slot);
                    if (item && item.typeId === itemId) {
                        let newAmount = item.amount - remainingCost;
                        remainingCost -= item.amount;

                        if (newAmount <= 0) {
                            container.setItem(slot, undefined);
                        } else {
                            item.amount = newAmount;
                            container.setItem(slot, item);
                        }

                        if (remainingCost <= 0) {
                            checksPassed++;
                            break;
                        }
                    }
                }
            }

            if (checksPassed >= Object.keys(recipe.items).length) {
                for (let item in recipe.result) {
                    let quantity = recipe.result[item];
                    player.runCommand(`give @s ${item} ${quantity}`);
                }
            }
        }
    });
});

function checkCraftable(player) {
    if (player.hasTag("inWorkbench")) {
        if (player.selectedSlotIndex === 7 || player.selectedSlotIndex === 8) {
            workbenchUI(player, false);
            return false;
        }

        let location = player.location;
        location.y += 1;
        let dimension = player.dimension;

        dimension.runCommand(`execute positioned ${location.x} ${location.y} ${location.z} run fill ~2~2~2 ~-2~-2~-2 air [] replace tac_guns:invis_block`);
        dimension.runCommand(`execute positioned ${location.x} ${location.y} ${location.z} run fill ~1~1~1 ~-1~-1~-1 tac_guns:invis_block [] keep`);
        system.runTimeout(() => {
            if (!player.hasTag("inWorkbench")) dimension.runCommand(`execute positioned ${location.x} ${location.y} ${location.z} run fill ~1~1~1 ~-1~-1~-1 air [] replace tac_guns:invis_block`);
        }, 1);

        let allItems = {};
        let container = player.getComponent("minecraft:inventory")?.container;
        for (let i = 0; i < container.size; i++) {
            let item = container.getItem(i);
            if (item) {
                if (!allItems[item.typeId]) {
                    allItems[item.typeId] = item.amount;
                } else {
                    allItems[item.typeId] += item.amount;
                }
            }
        }

        player.setProperty("tac_guns:tab", player.selectedSlotIndex);

        let recipe = getCurrentRecipe(player);
        let recipeFeedback = "";
        if (recipe) {
            for (let itemId in recipe.items) {
                recipeFeedback += `§7${itemId.replace("minecraft:", "")}§f: ${recipe.items[itemId]}\n`;
            }
        }

        if (!recipe) return false;

        let totalSlots = 0;
        for (let itemId in recipe.items) {
            let cost = recipe.items[itemId];
            let itemsTotal = allItems[itemId] || 0;
            if (itemsTotal >= cost) {
                totalSlots++;
            }
        }

        return totalSlots >= Object.keys(recipe.items).length;
    }

    return false;
}

let previousSlots = new Map();

system.runInterval(() => {
    world.getAllPlayers().forEach(player => {
        // Only process if mark_variant is 100
        if (player.getComponent("minecraft:mark_variant")?.value === 100) {
            let currentSlot = player.selectedSlotIndex;
            let playerId = player.id;
            let previousSlot = previousSlots.get(playerId);

            if (previousSlot !== undefined && currentSlot !== previousSlot) {
                player.setProperty("tac_guns:itemtab", 1);
                // Play random.click sound if the new slot is not 7 or 8
                if (currentSlot !== 7 && currentSlot !== 8) {
                    player.playSound("random.click");
                }
            }
            previousSlots.set(playerId, currentSlot);

            // Check if player is in workbench
            if (player.hasTag("inWorkbench")) {
                let craftable = checkCraftable(player);
                if (craftable) {
                    player.setProperty("tac_guns:item", true);
                } else {
                    player.setProperty("tac_guns:item", false);
                }
            } else {
                player.setProperty("tac_guns:item", false);
            }
        } else if (player.hasTag("inWorkbench")) {
            // Exit workbench UI if mark_variant is not 100
            workbenchUI(player, false);
        }
    });
});