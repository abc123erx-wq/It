// ============================================================================
//  Creative Squad - Itens Lendarios  |  config.js
//  Todos os identificadores e ajustes de balanceamento em um so lugar.
// ============================================================================

export const ITEM = {
  espada: "cs:espada_do_cacador",
  batata: "cs:batata_do_bobo",
  bota: "cs:bota_lendaria",
  capaceteBern: "cs:capacete_gemeo_bern",
  capaceteChip: "cs:capacete_gemeo_chip",
  dragao: "cs:dragao_lendario",
  escudo: "cs:escudo_lendario",
  bussola: "cs:bussola_lendaria",
  lampiao: "cs:lampiao_lendario",
  pena: "cs:pena_lendaria",
  picareta: "cs:picareta_lendaria",
  pocao: "cs:pocao_lendaria",
  relogio: "cs:relogio_lendario",
  tridente: "cs:tridente_lendario",
};

export const ALL_ITEMS = Object.values(ITEM);

// Itens que o script conhece (prefixo dos identificadores do addon).
export const NAMESPACE = "cs:";

// ---------------------------------------------------------------- balanceamento
export const CFG = {
  tickPassivo: 10,          // ticks entre cada varredura dos efeitos passivos
  tickLore: 40,             // ticks entre cada tentativa de aplicar lore

  batataSlowAmp: 4,         // Lentidao V
  botaSpeedAmp: 2,          // Velocidade III
  capaceteVidaAmp: 1,       // Vida extra (4 coracoes) + respiracao aquatica
  penaLevAmp: 1,            // Levitacao
  picaretaSpeed: 60,        // velocidade de quebra dos blocos "macios"

  // recargas (em ticks)
  cdDragao: 80,             // 4s
  cdEscudo: 160,            // 8s
  cdPocao: 30,              // 1,5s
  cdBussola: 40,
  cdRelogio: 1200,          // 20s para poder se disfarcar de novo
  relogioDuracao: 1200,     // 60s disfarcado
  cdTridenteRaio: 100,
};

// Blocos que a Picareta Lendaria NAO consegue minerar (regra do servidor)
export const PICARETA_PROIBIDOS = [
  "minecraft:obsidian",
  "minecraft:crying_obsidian",
  "minecraft:ancient_debris",
  "minecraft:respawn_anchor",
  "minecraft:netherite_block",
  "minecraft:reinforced_deepslate",
];

// Prefixos de mensagem no chat
export const PREFIX = "§8[§6CS§8] §r";

// Nome dos portadores originais (usado no /function cs/ajuda e nas mensagens)
export const PORTADOR = {
  "cs:espada_do_cacador": "NaitPlayer",
  "cs:batata_do_bobo": "Caduxinn",
  "cs:bota_lendaria": "0nerb",
  "cs:capacete_gemeo_bern": "Bern",
  "cs:capacete_gemeo_chip": "Chip Naughter",
  "cs:dragao_lendario": "Caduxinn",
  "cs:escudo_lendario": "MucaHD",
  "cs:bussola_lendaria": "GeleiaPlays",
  "cs:lampiao_lendario": "Tonigonn",
  "cs:pena_lendaria": "Feuripe",
  "cs:picareta_lendaria": "Pedrux",
  "cs:pocao_lendaria": "Fixz",
  "cs:relogio_lendario": "Ligonz",
  "cs:tridente_lendario": "NaitPlayer",
};

// Encantamentos "de fabrica" aplicados pelo script
export const ENCHANTS = {
  "cs:espada_do_cacador": [
    { type: "knockback", level: 10 },
  ],
  "cs:picareta_lendaria": [
    { type: "efficiency", level: 5 },
    { type: "fortune", level: 3 },
  ],
};

// dynamic properties
export const DP = {
  herdouEspada: "cs:herdou_espada_",
  fakeName: "cs:fakename",
  fakeUntil: "cs:fakeuntil",
};
