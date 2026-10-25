"""Arsenal brasileiro: dados de jogo + dados de documentacao de cada arma.

Cada arma reutiliza uma das cinco plataformas do TacGuns (mk18 / glock17 /
coltpython / awp / m870) para herdar 100% do comportamento original: disparo,
municao, recarga, recarga tatica, inspecao, saque (draw), sprint, sway, recuo,
pose de terceira pessoa, bancada e contador de municao no HUD.
"""

# ---------------------------------------------------------------------------
# plataformas herdadas
# ---------------------------------------------------------------------------
FAMILIES = {
    "rifle": dict(template="mk18", bp_gun_ac="mk18", bp_reload_ac="mk18", rp_anim="mk18",
                  mag=30, prop="tac_guns:gunreload", prop_base=340, prop_span=31,
                  sounds_from="mk18", bullet_from="mk18", caliber="5.56x45mm"),
    "pistol": dict(template="glock17", bp_gun_ac="glock17", bp_reload_ac="glock17", rp_anim="glock17",
                   mag=18, prop="tac_guns:coltpythonreload", prop_base=0, prop_span=33,
                   sounds_from="glock17", bullet_from="glock17", caliber="9x19mm"),
    "revolver": dict(template="coltpython", bp_gun_ac="coltpython", bp_reload_ac="coltpython",
                     rp_anim="coltpython", mag=6, prop="tac_guns:coltpythonreload",
                     prop_base=0, prop_span=7, sounds_from="coltpython", bullet_from="coltpython",
                     caliber=".357 Magnum"),
    "sniper": dict(template="awp", bp_gun_ac="awp", bp_reload_ac="awp", rp_anim="awp",
                   mag=5, prop="tac_guns:gunreload", prop_base=260, prop_span=21,
                   sounds_from="awp", bullet_from="awp", caliber=".338 Lapua"),
    "shotgun": dict(template="m870", bp_gun_ac="m870", bp_reload_ac="m870", rp_anim="m870",
                    mag=6, prop=None, prop_base=0, prop_span=7,
                    sounds_from="m870", bullet_from="m870", caliber="12 gauge"),
}

# ---------------------------------------------------------------------------
# esqueleto do rig hospedeiro + bones que recebem pecas moveis
# ---------------------------------------------------------------------------
RIGS = {
    "mk18": dict(body_parent="mk18", part_bones={"mag": "magazine"}, tp_bone="mk18tp",
                 rails=dict(optic=(0, 4.6, 4.0), muzzle=(0, 0, 0), under=(0, -3.2, 6.0),
                            mag=(0, -6.0, 8.0))),
    "glock17": dict(body_parent="glcok17", part_bones={"mag": "mag", "slide": "slide"},
                    tp_bone="glock17tp",
                    rails=dict(optic=(0, 2.4, 1.6), muzzle=(0, 0, 0), under=(0, -2.0, 2.4),
                               mag=(0, -5.0, 3.0))),
    "coltpython": dict(body_parent="defaultgun", part_bones={"hammer": "hammer2"},
                       tp_bone="coltpythontp",
                       rails=dict(optic=(0, 2.6, 1.2), muzzle=(0, 0, 0), under=(0, -2.2, 3.0),
                                  mag=(0, -3.0, 4.0))),
    "awp": dict(body_parent="group35", part_bones={"mag": "maga", "bolt": "bolt"},
                tp_bone="awptp",
                rails=dict(optic=(0, 3.4, 8.0), muzzle=(0, 0, 0), under=(0, -3.6, 10.0),
                           mag=(0, -6.0, 12.0))),
    "m870": dict(body_parent="m870_classic", part_bones={"pump": "slide"}, tp_bone="m870tp",
                 rails=dict(optic=(0, 3.0, 6.0), muzzle=(0, 0, 0), under=(0, -3.2, 8.0),
                            mag=(0, -4.0, 10.0))),
}

# ---------------------------------------------------------------------------
# catalogo
#   design  -> forma voxel reaproveitada (DESIGNS)
#   prop_new-> base da faixa de propriedade exclusiva da arma
# ---------------------------------------------------------------------------
def W(**kw):
    return kw


SPECS = [
    # ============================ FUZIS ==================================
    W(id="ia2_556", name="Imbel IA2 5.56", family="rifle", design="m4a1", ammo="556x45mm",
      damage=7.2, prop_new=400, tab=0, itemtab=3, mag=30,
      craft={"minecraft:iron_ingot": 34, "minecraft:lapis_lazuli": 5, "minecraft:oak_log": 6},
      craft_extra="minecraft:lapis_lazuli",
      lore=dict(maker="Imbel (Indústria de Material Bélico do Brasil)",
                users="Exército Brasileiro, Fuzileiros Navais, BOPE",
                caliber="5,56x45 mm NATO", era="2010 – atual",
                note="Fuzil padrão de dotação das Forças Armadas; projeto nacional "
                     "com coronha rebatível, trilho superior e empunhadura em polímero."),
      attach=["Óptica (trilho superior)", "Supressor 5.56 (boca do cano)",
              "Foregrip vertical (trilho inferior)", "Lanterna/laser (trilho 3h)",
              "Carregador estendido 40 tiros", "Coronha telescópica"],
      finish="Polímero preto fosco com desgaste prateado nas arestas de apoio e poeira "
             "ocre nas ranhuras do guarda-mão (uso em cerrado).",
      mesh=["ferrolho", "gatilho", "retém do carregador", "carregador", "alavanca de manejo",
            "seletor de tiro", "coronha", "guarda-mão"],
      anim=dict(draw="saque em 0,9 s puxando a alça de manejo",
                inspect="checagem de câmara + retém do carregador em 5,0 s",
                fire="ciclo de ferrolho de 0,75 s com recuo de 3,4°",
                tactical="troca de carregador tático em 2,5 s mantendo a mira",
                empty="recarga seca em 3,2 s com liberação do ferrolho")),
    W(id="ia2_762", name="Imbel IA2 7.62", family="rifle", design="scar_h", ammo="308winchester",
      damage=9.6, prop_new=440, tab=0, itemtab=4, mag=30,
      craft={"minecraft:iron_ingot": 40, "minecraft:lapis_lazuli": 6, "minecraft:oak_log": 5},
      craft_extra="minecraft:lapis_lazuli",
      lore=dict(maker="Imbel", users="Exército Brasileiro (versão de batalha)",
                caliber="7,62x51 mm NATO", era="2012 – atual",
                note="Versão de batalha do IA2 com ferrolho reforçado e cano mais pesado; "
                     "mesma ergonomia do 5.56 para treinamento cruzado."),
      attach=["Óptica 1-4x (trilho superior)", "Supressor 7.62", "Bipé (trilho inferior)",
              "Lanterna tática", "Carregador 25 tiros", "Coronha ajustável"],
      finish="Metal fosfatizado escuro com marcas de calor no cano e fita de camuflagem "
             "verde-oliva no guarda-mão.",
      mesh=["ferrolho", "gatilho", "retém", "carregador", "alça de manejo", "bipé",
            "coronha", "guarda-mão"],
      anim=dict(draw="saque em 1,1 s com apoio da mão de suporte",
                inspect="checagem de culatra em 5,3 s",
                fire="recuo de 4,8° em 0,8 s",
                tactical="troca tática em 2,7 s",
                empty="recarga seca em 3,4 s")),
    W(id="md97l", name="Imbel MD97L", family="rifle", design="g36c", ammo="556x45mm",
      damage=6.8, prop_new=480, tab=0, itemtab=5, mag=30,
      craft={"minecraft:iron_ingot": 32, "minecraft:lapis_lazuli": 5, "minecraft:oak_log": 4},
      craft_extra="minecraft:lapis_lazuli",
      lore=dict(maker="Imbel", users="Exército Brasileiro (reserva), polícias militares",
                caliber="5,56x45 mm", era="1997 – 2010",
                note="Antecessor direto do IA2, com coronha esqueletizada e "
                     "carregador translúcido de 30 tiros."),
      attach=["Óptica (trilho superior)", "Supressor 5.56", "Foregrip curto",
              "Lanterna", "Carregador 30 tiros", "Coronha esqueletizada"],
      finish="Preto acetinado com desgaste intenso no punho e marcas de fita adesiva "
             "no guarda-mão.",
      mesh=["ferrolho", "gatilho", "retém", "carregador", "seletor", "coronha"],
      anim=dict(draw="saque em 1,0 s", inspect="inspeção de 4,9 s girando a arma",
                fire="0,72 s por disparo", tactical="2,4 s", empty="3,1 s")),
    W(id="md97lm", name="Imbel MD97LM", family="rifle", design="mp5", ammo="556x45mm",
      damage=6.4, prop_new=520, tab=0, itemtab=6, mag=30,
      craft={"minecraft:iron_ingot": 28, "minecraft:lapis_lazuli": 4, "minecraft:oak_log": 3},
      craft_extra="minecraft:lapis_lazuli",
      lore=dict(maker="Imbel", users="Polícia Civil, guardas municipais",
                caliber="5,56x45 mm", era="2000 – atual",
                note="Carabina curta derivada do MD97 para patrulhamento urbano e "
                     "espaços confinados."),
      attach=["Red dot (trilho superior)", "Supressor curto", "Foregrip",
              "Lanterna/laser", "Carregador 30 tiros"],
      finish="Preto fosco com bastante desgaste no guarda-mão e coronha rebatível.",
      mesh=["ferrolho", "gatilho", "retém", "carregador", "coronha"],
      anim=dict(draw="saque em 0,85 s", inspect="4,6 s", fire="0,7 s",
                tactical="2,3 s", empty="3,0 s")),
    W(id="m964_fal", name="Imbel M964 FAL", family="rifle", design="scar_h", ammo="308winchester",
      damage=10.2, prop_new=560, tab=0, itemtab=7, mag=30,
      craft={"minecraft:iron_ingot": 44, "minecraft:lapis_lazuli": 6, "minecraft:oak_log": 8},
      craft_extra="minecraft:lapis_lazuli",
      lore=dict(maker="Imbel (licença FN Herstal)", users="Exército Brasileiro, BOPE",
                caliber="7,62x51 mm NATO", era="1964 – atual (reserva)",
                note="O clássico “Para-FAL” brasileiro, ícone da infantaria e das "
                     "operações urbanas; coronha rebatível e punho de madeira."),
      attach=["Óptica (trilho aparafusado)", "Supressor 7.62", "Bipé",
              "Lanterna", "Carregador 20 tiros", "Coronha rebatível"],
      finish="Parkerização cinza-esverdeada, madeira escurecida por uso e marcas de "
             "oxidação nas molas expostas.",
      mesh=["ferrolho", "gatilho", "retém", "carregador", "alavanca de manejo",
            "coronha", "guarda-mão de madeira"],
      anim=dict(draw="saque em 1,2 s (arma pesada)", inspect="5,4 s",
                fire="recuo de 5,2° em 0,82 s", tactical="3,0 s", empty="3,6 s")),
    W(id="md2", name="Imbel MD2", family="rifle", design="m4a1", ammo="556x45mm",
      damage=6.6, prop_new=600, tab=0, itemtab=8, mag=30,
      craft={"minecraft:iron_ingot": 30, "minecraft:lapis_lazuli": 5, "minecraft:oak_log": 5},
      craft_extra="minecraft:lapis_lazuli",
      lore=dict(maker="Imbel", users="Polícia Federal, Força Nacional",
                caliber="5,56x45 mm", era="1985 – 2000",
                note="Família MD baseada no FAL convertida para 5,56; precursora da "
                     "linha que levou ao MD97 e ao IA2."),
      attach=["Óptica", "Supressor", "Foregrip", "Lanterna", "Carregador 30 tiros"],
      finish="Preto gasto com pontos de ferrugem superficiais e fita de identificação.",
      mesh=["ferrolho", "gatilho", "retém", "carregador", "coronha"],
      anim=dict(draw="1,0 s", inspect="5,0 s", fire="0,74 s", tactical="2,5 s", empty="3,2 s")),
    W(id="t4", name="Taurus T4", family="rifle", design="mp5", ammo="556x45mm",
      damage=6.9, prop_new=640, tab=0, itemtab=9, mag=30,
      craft={"minecraft:iron_ingot": 33, "minecraft:lapis_lazuli": 5, "minecraft:oak_log": 6},
      craft_extra="minecraft:lapis_lazuli",
      lore=dict(maker="Taurus Armas", users="Polícias militares, BOPE, mercado civil",
                caliber="5,56x45 mm NATO", era="2014 – atual",
                note="Plataforma AR-15 nacional, muito usada por forças táticas pelo "
                     "custo e pela disponibilidade de peças."),
      attach=["Red dot / holográfica (Picatinny)", "Supressor 5.56", "Foregrip angular",
              "Lanterna + laser", "Carregador 30 tiros", "Coronha telescópica"],
      finish="Cerakote preto com polímero FDE opcional; desgaste nas trilhas do "
             "carregador e no freio de boca.",
      mesh=["ferrolho (BCG)", "gatilho", "retém do carregador", "carregador",
            "alavanca de manejo", "seletor ambidestro", "coronha", "guarda-mão M-LOK"],
      anim=dict(draw="0,9 s", inspect="5,02 s", fire="0,75 s", tactical="2,46 s", empty="3,17 s")),
    W(id="t4_cqc", name="Taurus T4 CQC", family="rifle", design="vector", ammo="556x45mm",
      damage=6.3, prop_new=680, tab=0, itemtab=10, mag=30,
      craft={"minecraft:iron_ingot": 30, "minecraft:lapis_lazuli": 5, "minecraft:oak_log": 3},
      craft_extra="minecraft:lapis_lazuli",
      lore=dict(maker="Taurus Armas", users="Forças táticas, escolta de autoridades",
                caliber="5,56x45 mm", era="2016 – atual",
                note="Versão de cano ultracurto (CQC) para combate urbano e proteção "
                     "de dignitários."),
      attach=["Red dot", "Supressor curto", "Foregrip compacto", "Laser",
              "Carregador 30 tiros", "Coronha curta"],
      finish="Preto fosco com desgaste concentrado no freio de boca e na soleira.",
      mesh=["ferrolho", "gatilho", "retém", "carregador", "coronha"],
      anim=dict(draw="0,8 s", inspect="4,8 s", fire="0,68 s", tactical="2,2 s", empty="2,9 s")),

    # ============================ SMGs ===================================
    W(id="saf_9mm", name="Taurus/Famae SAF 9mm", family="rifle", design="mp5", ammo="9x19mm",
      damage=5.6, prop_new=720, tab=5, itemtab=1, mag=30,
      craft={"minecraft:iron_ingot": 22, "minecraft:gunpowder": 4},
      craft_extra="minecraft:copper_ingot",
      lore=dict(maker="Famae / Taurus", users="Polícias militares, Forças Armadas, BOPE",
                caliber="9x19 mm", era="1977 – atual",
                note="Submetralhadora nacional mais difundida no Brasil; recuo baixo e "
                     "extremamente compacta com coronha rebatível."),
      attach=["Red dot (trilho superior)", "Supressor 9 mm", "Foregrip vertical",
              "Lanterna", "Carregador 30 tiros", "Coronha rebatível"],
      finish="Preto brunitado desgastado no punho; polímero manchado de poeira clara.",
      mesh=["ferrolho", "gatilho", "retém", "carregador", "coronha rebatível", "alça de manejo"],
      anim=dict(draw="0,75 s", inspect="4,4 s", fire="0,52 s (alta cadência)",
                tactical="1,85 s", empty="2,15 s")),
    W(id="mini_saf", name="Famae Mini-SAF", family="rifle", design="mp5k", ammo="9x19mm",
      damage=5.1, prop_new=760, tab=5, itemtab=2, mag=30,
      craft={"minecraft:iron_ingot": 17, "minecraft:gunpowder": 3},
      craft_extra="minecraft:copper_ingot",
      lore=dict(maker="Famae", users="Segurança de autoridades, forças especiais",
                caliber="9x19 mm", era="1985 – atual",
                note="Versão encurtada da SAF, pensada para porte velado e "
                     "operações em ambientes fechados."),
      attach=["Red dot", "Supressor curto", "Foregrip curto", "Laser",
              "Carregador 20/30 tiros"],
      finish="Preto fosco com desgaste no topo do ferrolho.",
      mesh=["ferrolho", "gatilho", "retém", "carregador", "coronha"],
      anim=dict(draw="0,65 s", inspect="4,1 s", fire="0,5 s", tactical="1,7 s", empty="2,0 s")),
    W(id="mt9_g2", name="Taurus MT9 G2", family="rifle", design="ump45", ammo="9x19mm",
      damage=5.8, prop_new=800, tab=5, itemtab=3, mag=30,
      craft={"minecraft:iron_ingot": 20, "minecraft:gunpowder": 5},
      craft_extra="minecraft:copper_block",
      lore=dict(maker="Taurus Armas", users="Polícia Civil, guardas municipais",
                caliber="9x19 mm", era="2010 – atual",
                note="Segunda geração da família MT, com armação em polímero e "
                     "trilho Picatinny integrado."),
      attach=["Red dot", "Supressor 9 mm", "Foregrip", "Lanterna/laser",
              "Carregador 30 tiros", "Coronha retrátil"],
      finish="Polímero preto texturizado, marcas de atrito no guarda-mato.",
      mesh=["ferrolho", "gatilho", "retém", "carregador", "coronha"],
      anim=dict(draw="0,8 s", inspect="4,5 s", fire="0,56 s", tactical="1,9 s", empty="2,2 s")),
    W(id="smt9", name="Taurus SMT9", family="rifle", design="vector", ammo="9x19mm",
      damage=5.9, prop_new=840, tab=5, itemtab=4, mag=30,
      craft={"minecraft:iron_ingot": 24, "minecraft:gunpowder": 5},
      craft_extra="minecraft:copper_block",
      lore=dict(maker="Taurus Armas", users="Forças táticas, BOPE",
                caliber="9x19 mm", era="2019 – atual",
                note="Submetralhadora tática moderna com culatra fechada e "
                     "compatibilidade com acessórios da linha T4."),
      attach=["Holográfica", "Supressor 9 mm", "Foregrip angular", "Laser + lanterna",
              "Carregador 30 tiros", "Coronha telescópica"],
      finish="Cerakote cinza-escuro com trilhos polidos pelo uso.",
      mesh=["ferrolho", "gatilho", "retém", "carregador", "coronha", "guarda-mão M-LOK"],
      anim=dict(draw="0,78 s", inspect="4,6 s", fire="0,54 s", tactical="1,9 s", empty="2,25 s")),
    W(id="uru", name="Mekanika Uru 9mm", family="rifle", design="p90", ammo="9x19mm",
      damage=5.4, prop_new=880, tab=5, itemtab=5, mag=30,
      craft={"minecraft:iron_ingot": 18, "minecraft:gunpowder": 4},
      craft_extra="minecraft:copper_ingot",
      lore=dict(maker="Mekanika (RJ)", users="Polícias civis e militares (histórica)",
                caliber="9x19 mm", era="1974 – 1990",
                note="Submetralhadora brasileira dos anos 70/80, robusta e barata; "
                     "ainda aparece em apreensões e acervos."),
      attach=["Óptica pequena", "Supressor (adaptado)", "Carregador 30 tiros"],
      finish="Aço escurecido com oxidação e coronha de metal riscado.",
      mesh=["ferrolho", "gatilho", "retém", "carregador", "coronha metálica"],
      anim=dict(draw="0,85 s", inspect="4,3 s", fire="0,6 s", tactical="2,0 s", empty="2,4 s")),
    W(id="mt12", name="Taurus MT12", family="rifle", design="mp5k", ammo="9x19mm",
      damage=5.5, prop_new=920, tab=5, itemtab=6, mag=30,
      craft={"minecraft:iron_ingot": 19, "minecraft:gunpowder": 4},
      craft_extra="minecraft:copper_ingot",
      lore=dict(maker="Taurus / Beretta (licença)", users="Polícia Civil, Forças Armadas",
                caliber="9x19 mm", era="1980 – 2010",
                note="Cópia nacional da Beretta M12 com culatra telescópica e "
                     "ferrolho envolvente."),
      attach=["Red dot", "Supressor", "Lanterna", "Carregador 20/32 tiros"],
      finish="Preto brilhante com desgaste nas laterais do receptor.",
      mesh=["ferrolho", "gatilho", "retém", "carregador", "coronha"],
      anim=dict(draw="0,82 s", inspect="4,4 s", fire="0,58 s", tactical="2,0 s", empty="2,3 s")),

    # ============================ PISTOLAS ===============================
    W(id="pt92", name="Taurus PT92", family="pistol", design="five_seven", ammo="9x19mm",
      damage=5.2, prop_new=100, tab=2, itemtab=4, mag=18,
      craft={"minecraft:iron_ingot": 16, "minecraft:quartz": 2},
      craft_extra="minecraft:gold_nugget",
      lore=dict(maker="Taurus Armas (Beretta 92 sob licença)", users="Polícias militares, Exército",
                caliber="9x19 mm", era="1983 – atual",
                note="Pistola de serviço com armação de aço e trava de segurança "
                     "no ferrolho; símbolo do policiamento brasileiro dos anos 90."),
      attach=["Red dot (trilho)", "Supressor 9 mm", "Lanterna tática",
              "Carregador 17/20 tiros"],
      finish="Aço azulado com facetas prateadas nos cantos e empunhadura de "
             "madeira ou borracha.",
      mesh=["ferrolho", "cano", "gatilho", "retém do carregador", "carregador",
            "martelo", "trava de segurança"],
      anim=dict(draw="0,55 s", inspect="4,11 s", fire="0,35 s (recuo 2,1°)",
                tactical="1,85 s", empty="2,15 s")),
    W(id="pt24_7", name="Taurus PT24/7", family="pistol", design="five_seven", ammo="9x19mm",
      damage=5.0, prop_new=150, tab=2, itemtab=5, mag=18,
      craft={"minecraft:iron_ingot": 15, "minecraft:quartz": 2},
      craft_extra="minecraft:gold_nugget",
      lore=dict(maker="Taurus Armas", users="Polícia Civil, segurança privada",
                caliber="9x19 mm / .40 S&W", era="2000 – 2015",
                note="Pistola policial com sistema “24/7” de prontidão e "
                     "indicador de câmara carregada."),
      attach=["Red dot", "Supressor", "Lanterna", "Carregador 15/17 tiros"],
      finish="Polímero preto com insertos de borracha e desgaste no trilho.",
      mesh=["ferrolho", "cano", "gatilho", "retém", "carregador", "martelo"],
      anim=dict(draw="0,52 s", inspect="4,0 s", fire="0,33 s", tactical="1,8 s", empty="2,1 s")),
    W(id="ts9", name="Taurus TS9", family="pistol", design="five_seven", ammo="9x19mm",
      damage=5.1, prop_new=200, tab=2, itemtab=6, mag=18,
      craft={"minecraft:iron_ingot": 16, "minecraft:quartz": 2},
      craft_extra="minecraft:gold_nugget",
      lore=dict(maker="Taurus Armas", users="Polícia Militar, Polícia Federal",
                caliber="9x19 mm", era="2015 – atual",
                note="Pistola striker-fired adotada em concursos e editais de "
                     "segurança pública pelo gatilho constante."),
      attach=["Red dot", "Supressor", "Lanterna", "Carregador 17 tiros"],
      finish="Preto fosco com textura aderente no punho e desgaste no serrilhado.",
      mesh=["ferrolho", "cano", "gatilho", "retém", "carregador", "extrator"],
      anim=dict(draw="0,5 s", inspect="3,9 s", fire="0,32 s", tactical="1,75 s", empty="2,05 s")),
    W(id="th9", name="Taurus TH9", family="pistol", design="five_seven", ammo="9x19mm",
      damage=5.3, prop_new=250, tab=2, itemtab=7, mag=18,
      craft={"minecraft:iron_ingot": 17, "minecraft:quartz": 2},
      craft_extra="minecraft:gold_nugget",
      lore=dict(maker="Taurus Armas", users="Polícias militares, CAC",
                caliber="9x19 mm", era="2017 – atual",
                note="Martelo externo, armação completa e trilho para red dot; "
                     "projetada para o mercado de segurança pública."),
      attach=["Red dot (placa óptica)", "Supressor 9 mm", "Lanterna",
              "Carregador 17/20 tiros"],
      finish="Preto mate com desgaste leve e poeira nas reentrâncias do punho.",
      mesh=["ferrolho", "cano", "gatilho", "retém", "carregador", "martelo",
            "trava ambidestra"],
      anim=dict(draw="0,53 s", inspect="4,05 s", fire="0,33 s", tactical="1,8 s", empty="2,1 s")),
    W(id="g3c", name="Taurus G3c", family="pistol", design="five_seven", ammo="9x19mm",
      damage=4.8, prop_new=300, tab=2, itemtab=8, mag=18,
      craft={"minecraft:iron_ingot": 13, "minecraft:quartz": 1},
      craft_extra="minecraft:gold_nugget",
      lore=dict(maker="Taurus Armas", users="Porte velado, polícias civis",
                caliber="9x19 mm", era="2020 – atual",
                note="Compacta de 12+1, uma das pistolas mais vendidas do mundo; "
                     "gatilho curto e mira em fibra óptica."),
      attach=["Red dot", "Supressor compacto", "Lanterna mini", "Carregador 12/15 tiros"],
      finish="Polímero preto texturizado, desgaste no topo do ferrolho.",
      mesh=["ferrolho", "cano", "gatilho", "retém", "carregador", "extrator"],
      anim=dict(draw="0,48 s", inspect="3,8 s", fire="0,31 s", tactical="1,7 s", empty="2,0 s")),
    W(id="gx4", name="Taurus GX4", family="pistol", design="five_seven", ammo="9x19mm",
      damage=4.6, prop_new=350, tab=2, itemtab=9, mag=18,
      craft={"minecraft:iron_ingot": 12, "minecraft:quartz": 1},
      craft_extra="minecraft:gold_nugget",
      lore=dict(maker="Taurus Armas", users="Porte velado, forças de segurança",
                caliber="9x19 mm", era="2021 – atual",
                note="Micro-compacta de 11+1 com chassi de aço inox; pensada para "
                     "uso dissimulado."),
      attach=["Red dot micro", "Supressor compacto", "Lanterna mini",
              "Carregador 11/13 tiros"],
      finish="Inox escovado com armação preta e marcas de uso no gatilho.",
      mesh=["ferrolho", "cano", "gatilho", "retém", "carregador"],
      anim=dict(draw="0,45 s", inspect="3,7 s", fire="0,3 s", tactical="1,65 s", empty="1,95 s")),

    # ============================ REVOLVERES =============================
    W(id="rt85", name="Taurus RT85", family="revolver", design="model29", ammo="357magnum",
      damage=13.0, prop_new=500, tab=2, itemtab=10, mag=6,
      craft={"minecraft:gold_ingot": 5, "minecraft:iron_ingot": 38, "minecraft:quartz": 2},
      craft_extra="minecraft:gold_block",
      lore=dict(maker="Taurus Armas", users="Vigilantes, porte civil, polícias",
                caliber=".38 Special", era="1980 – atual",
                note="Revólver de 5 tiros em .38 Special, leve e barato; "
                     "presença massiva no mercado civil brasileiro."),
      attach=["Mira de fibra óptica (substitui a fixa)", "Cilindro extra (recarga rápida)"],
      finish="Aço inox fosco com riscos de coldre e fuligem nos alvéolos.",
      mesh=["tambor", "martelo", "gatilho", "cão", "ejetor", "trava do tambor"],
      anim=dict(draw="0,62 s", inspect="5,79 s girando o tambor",
                fire="0,45 s com recuo de 3,2°", tactical="recarga rápida de 6 tiros",
                empty="recarga completa com ejetor")),
    W(id="rt608", name="Taurus RT608", family="revolver", design="model29", ammo="357magnum",
      damage=15.5, prop_new=550, tab=2, itemtab=11, mag=6,
      craft={"minecraft:gold_ingot": 6, "minecraft:iron_ingot": 44, "minecraft:quartz": 2},
      craft_extra="minecraft:gold_block",
      lore=dict(maker="Taurus Armas", users="Caça, tiro esportivo, vigilância",
                caliber=".357 Magnum", era="1990 – atual",
                note="Revólver de 8 tiros com cano de 6 polegadas e "
                     "compensador de boca; muito usado em vigilância rural."),
      attach=["Red dot (trilho no cano)", "Cilindro extra", "Coronilha de mira"],
      finish="Inox polido com fuligem no compensador e desgaste na empunhadura.",
      mesh=["tambor", "martelo", "gatilho", "ejetor", "cano ventilado"],
      anim=dict(draw="0,7 s", inspect="5,9 s", fire="0,5 s (recuo 4,4°)",
                tactical="recarga rápida", empty="recarga completa")),
    W(id="raging_bull", name="Taurus Raging Bull .454", family="revolver", design="judge",
      ammo="50ae", damage=19.0, prop_new=600, tab=2, itemtab=12, mag=6,
      craft={"minecraft:gold_ingot": 10, "minecraft:iron_ingot": 52,
             "minecraft:diamond": 2},
      craft_extra="minecraft:diamond",
      lore=dict(maker="Taurus Armas", users="Caça maior, tiro esportivo",
                caliber=".454 Casull", era="1997 – atual",
                note="Revólver pesado com quadro reforçado e "
                     "compensador integrado; referência em caça de grande porte."),
      attach=["Red dot", "Cilindro extra", "Massa de mira de fibra"],
      finish="Aço escuro com jateamento e marcas de fuligem intensa.",
      mesh=["tambor", "martelo", "gatilho", "ejetor", "compensador"],
      anim=dict(draw="0,8 s", inspect="6,0 s", fire="0,55 s (recuo 5,6°)",
                tactical="recarga rápida", empty="recarga completa")),

    # ==================== PRECISAO / ESCOPETAS ===========================
    W(id="aglc", name="Imbel AGLC", family="sniper", design="intervention", ammo="308winchester",
      damage=32.0, prop_new=1000, tab=4, itemtab=3, mag=5,
      craft={"minecraft:diamond": 6, "minecraft:gold_ingot": 30, "minecraft:iron_ingot": 180,
             "minecraft:blaze_rod": 3},
      craft_extra="minecraft:obsidian",
      lore=dict(maker="Imbel", users="Exército Brasileiro (precisão), BOPE",
                caliber="7,62x51 mm NATO (.308 Win)", era="2010 – atual",
                note="Fuzil de precisão de ferrolho do Exército, com cano flutuante "
                     "e culatra de repetição manual."),
      attach=["Luneta 3-12x (trilho)", "Supressor .308", "Bipé", "Saco de apoio",
              "Carregador 5/10 tiros"],
      finish="Verde-oliva com rede de camuflagem e desgaste no ferrolho.",
      mesh=["ferrolho (bolt)", "gatilho", "retém", "carregador", "coronha ajustável",
            "bipé", "luneta"],
      anim=dict(draw="1,3 s", inspect="4,96 s", fire="0,9 s com ciclo de ferrolho",
                tactical="recarga tática 2,9 s", empty="recarga seca 3,5 s")),
    W(id="st12", name="Taurus ST12", family="shotgun", design="spas12", ammo="12gauge",
      damage=5.2, prop_new=None, tab=3, itemtab=3, mag=6,
      craft={"minecraft:iron_ingot": 46, "minecraft:lapis_lazuli": 7, "minecraft:oak_log": 5},
      craft_extra="minecraft:spruce_log",
      lore=dict(maker="Taurus Armas", users="Polícia Militar, BOPE, Força Nacional",
                caliber="12 gauge", era="2015 – atual",
                note="Escopeta tática de bombeamento com coronha retrátil e "
                     "trilho para acessórios; padrão em viaturas."),
      attach=["Red dot", "Lanterna/laser (trilho)", "Coronha retrátil",
              "Tube extensor 7+1", "Choke de boca"],
      finish="Preto fosco com polímero texturizado e desgaste no guarda-mão.",
      mesh=["bombeamento (pump)", "ferrolho", "gatilho", "retém", "tubo carregador",
            "coronha"],
      anim=dict(draw="0,9 s", inspect="4,46 s", fire="0,7 s",
                tactical="recarga tática de 0,55 s por cartucho",
                empty="recarga seca com liberação do pump")),
    W(id="cbc_military", name="CBC Military 3.0", family="shotgun", design="nova",
      ammo="12gauge", damage=4.9, prop_new=None, tab=3, itemtab=4, mag=6,
      craft={"minecraft:iron_ingot": 40, "minecraft:lapis_lazuli": 6, "minecraft:oak_log": 7},
      craft_extra="minecraft:birch_log",
      lore=dict(maker="CBC (Companhia Brasileira de Cartuchos)", users="Exército, polícias",
                caliber="12 gauge", era="2018 – atual",
                note="Escopeta de bombeamento padrão de dotação, simples e "
                     "resistente, usada em guarda de instalações."),
      attach=["Lanterna", "Coronha tática", "Tube extensor"],
      finish="Preto com coronha de polímero e marcas de uso na soleira.",
      mesh=["bombeamento", "ferrolho", "gatilho", "tubo carregador"],
      anim=dict(draw="0,95 s", inspect="4,46 s", fire="0,72 s",
                tactical="recarga por cartucho (0,55 s)", empty="recarga seca")),
]

BY_ID = {s["id"]: s for s in SPECS}


def recipe_items(spec, max_total=8):
    """Custo reduzido e proporcional para caber numa receita de bancada 3x3."""
    raw = spec["craft"]
    keys = list(raw)[:3]
    total = sum(raw[k] for k in keys) or 1
    counts = {k: max(1, round(raw[k] / total * max_total)) for k in keys}
    while sum(counts.values()) > max_total:
        top = max(counts, key=counts.get)
        counts[top] -= 1
    return {k: v for k, v in counts.items() if v > 0}


def recipe_pattern(counts):
    """Converte contagens em padrao 3x3 + chave (mira <= 9 slots)."""
    letters = "ABCDEFGHI"
    slots = []
    for letter, item in zip(letters, counts):
        slots += [letter] * counts[item]
    while len(slots) < 9:
        slots.append(" ")
    rows = ["".join(slots[i:i + 3]) for i in range(0, 9, 3)]
    key = {letter: {"item": item} for letter, item in zip(letters, counts)}
    return rows, key
