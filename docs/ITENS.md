# Ficha completa dos Itens Lendários — pesquisa e implementação

Documento de referência do addon. A primeira parte é a **pesquisa** (o que cada item fazia na
Creative Squad 4, com as limitações registradas na wiki) e a segunda é o **detalhamento técnico**
de como cada habilidade foi implementada no Minecraft Bedrock 26.52.

Fontes usadas na pesquisa:

* Wiki Multiverso Quadrado — [Itens Lendários (Creative Squad)](https://multiversoquadrado.fandom.com/pt-br/wiki/Itens_Lend%C3%A1rios_(Creative_Squad))
* Wiki Multiverso Quadrado — [Creative Squad (Temporada 4)](https://multiversoquadrado.fandom.com/pt-br/wiki/Creative_Squad_(Temporada_4))
* Wiki Creative Squad 3 — [lista dos itens lendários e seus portadores](https://creative-squad-3.fandom.com/pt-br/wiki/Creative_sguad_4)
* Documentação oficial de criadores — [1.26.0 Update Notes](https://learn.microsoft.com/en-us/minecraft/creator/documents/update1.26.0?view=minecraft-bedrock-stable) e [script API `@minecraft/server`](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/minecraft-server?view=minecraft-bedrock-stable)

---

## 1. O que eram os Itens Lendários

Na Creative Squad 4 (outubro de 2024 → maio de 2025), cada participante ganhou um **item único**
com uma habilidade que não existe no survival normal. Eram objetos que *pareciam* itens comuns
encantados, mas carregavam poderes próprios — e eram **praticamente indestrutíveis**: só sumiam
se fossem jogados no vazio ou em cactos.

Eles viraram o centro da temporada: geraram a disputa por poder no Vale da CS e a guerra entre o
**Time União** (Mendrake, Pedrux, Nait, Caduxinn, Geleia) e a **CIA** (Tonigon, Chip, 0nerb).
No último dia do servidor os itens foram destruídos pelos próprios jogadores para acabar com a
guerra.

### Tier list oficial (Tonigon e Mendrake)

| Tier | Itens |
|------|-------|
| **LEGENDARY** | Bota Lendária, Relógio Lendário, Lampião Lendário, Escudo Lendário |
| **VEEURI GUD** | Tridente Lendário, Capacetes dos Gêmeos, Bússola Lendária |
| **BOM** | Espada do Caçador, Poção Lendária |
| **RUIM** | Dragão Lendário, Picareta Lendária |
| **HORROROSO** | Batata do Bobo, Pena Lendária |

---

## 2. Ficha item por item

### ⚔️ Espada do Caçador — NaitPlayer
* **Item:** espada de ouro inquebrável.
* **Função:** **Repulsão X** (knockback nível 10) — um toque arremessa o alvo longe.
* **Regra especial:** quem morre para a espada **vira o novo portador** do item.
* **Limitação:** aplica **Mau Presságio** (Bad Omen) permanente no próprio portador.
* **No addon:** dano 9, knockback aplicado por script (`applyKnockback` com força 3.2),
  partículas de crítico + som de bigorna. Mau Presságio renovado a cada 5s. Ao matar um jogador,
  a espada sai do inventário do matador, fica marcada como "herança" e é entregue no respawn da
  vítima (com anúncio no chat). Encantamento `knockback 10` aplicado por script para aparecer no
  tooltip.

### 🥔 Batata do Bobo — Caduxinn
* **Item:** batata envenenada.
* **Função:** **anula a velocidade da Bota Lendária** (é o único item 100% negativo do conjunto).
* **Limitação:** deixa o portador com **Lentidão V** mesmo sem estar sendo segurada.
* **No addon:** enquanto estiver em qualquer slot do inventário, aplica Lentidão V e remove o
  efeito de Velocidade vindo da bota. Comer a batata dá Veneno + Náusea e ela **volta para o
  inventário** (não é consumida, como os itens lendários do servidor).

### 👢 Bota Lendária — 0nerb
* **Item:** botas de diamante.
* **Função:** deixa o portador **extremamente rápido**.
* **Limitação:** pode ser **nulificada pela Batata do Bobo**.
* **No addon:** calçada, aplica **Velocidade III** com duração curta renovada a cada 10 ticks —
  se você tirar a bota (ou pegar a batata), o efeito cai em menos de 2 segundos. Proteção 3 e
  textura própria aplicada pela camada de armadura (attachable).

### 🧭 Bússola Lendária — GeleiaPlays
* **Função:** localiza **qualquer jogador online**, **inclusive invisíveis**.
* **No addon:** ao usar, procura o jogador mais próximo na mesma dimensão (até 512 blocos),
  mostra nome, distância, direção (N/NE/L/SE/S/SO/O/NO) e coordenadas no chat, e deixa um rastro
  de partículas (`endrod` + `sculk_soul`) sobre o alvo por 8 segundos — que funciona mesmo com
  Lampião Lendário ativo. Cooldown de 2s.

### 🐢 Capacetes Lendários dos Gêmeos — Bern e Chip
* **Item:** dois capacetes de tartaruga (um de cada irmão).
* **Função:** **+5 corações** de vida e **respiração aquática infinita**.
* **Limitações:** só funcionam **vestidos** e a **vida é compartilhada** entre os dois portadores.
* **No addon:** `Health Boost` (+4 corações, o máximo que a API do Bedrock soma com segurança),
  `Water Breathing` infinito e **50% do dano recebido é transferido para o portador do outro
  capacete** (com aviso na actionbar dos dois). Se só um estiver com o capacete, não há divisão.

### 🐉 Dragão Lendário — Caduxinn
* **Item:** cabeça de dragão.
* **Função:** solta um **bafo de dragão com dano**.
* **No addon:** use (clique direito) → cone de 10 blocos e 32° de abertura, **8 de dano**
  creditado ao jogador + **Veneno II** por 6s, com trilha de partículas de bafo de dragão, som de
  rugido e recarga de 4s. Mostra o tempo restante na actionbar.

### 🛡️ Escudo Lendário — MucaHD
* **Função:** escudo **inquebrável** que dispara uma **Rajada Sônica de Warden**.
* **Limitações:** tem cooldown entre os ataques e **não pode ser usado para bloquear**.
* **No addon:** use → rajada em cone de 16 blocos, **12 de dano**, empurrão forte e **Cegueira**.
  Som e partículas de `sonic_boom`. Recarga de 8s. Como não tem componente de escudo real, ele
  não bloqueia dano — exatamente a limitação original.

### 🏮 Lampião Lendário — Tonigonn
* **Função:** deixa o usuário **invisível** enquanto estiver sendo segurado.
* **Limitações:** não esconde elytras, não anula sons, e é **anulado pela Bússola Lendária**.
* **No addon:** Invisibilidade infinita **sem partículas** enquanto estiver na mão principal ou
  na secundária; esconde a armadura automaticamente (comportamento do efeito no Bedrock). A
  bússola continua achando o jogador — a limitação foi mantida de propósito.

### 🪶 Pena Lendária — Feuripe
* **Função:** **levitação infinita** para quem segura (ótima com maça: sobe e desce batendo).
* **Limitação:** **não protege do dano de queda**.
* **No addon:** Levitação II renovada a cada 3s enquanto estiver na mão. Nenhum efeito de
  resistência a queda — quem segurar a pena e cair, morre. 😅

### ⛏️ Picareta Lendária — Pedrux
* **Função:** picareta de ferro que **quebra blocos muito rápido**.
* **Limitação:** **incapaz de coletar obsidiana e netherita**.
* **No addon:** `minecraft:digger` com velocidade 60 em 43 blocos comuns + **Eficiência V** e
  **Fortuna III**; minerar obsidiana, obsidiana chorosa, âncora de respawn, detritos ancestrais,
  bloco de netherita ou deepslate reforçado é **cancelado** (`beforeEvents.playerBreakBlock`) com
  aviso na actionbar.

### 🧪 Poção Lendária — Fixz
* **Função:** poção **arremessável e infinita** que aplica **cegueira**.
* **No addon:** use → trajetória em arco até 22 blocos (raycast para achar o ponto de impacto),
  nuvem de 5 blocos de raio que aplica **Cegueira II** por 15s e 1 de dano mágico. **O item não é
  consumido.** Recarga de 1,5s.

### ⏰ Relógio Lendário — Ligonz
* **Função:** transforma o jogador em **qualquer outra pessoa online**, replicando **skin e nick**.
* **No addon:** use → copia o **nick** do jogador mais próximo por 60 segundos (nome no chat,
  na lista de jogadores e acima da cabeça). A **skin não pode ser trocada por script no Bedrock**,
  então essa parte é a única adaptação em relação ao servidor. Cooldown de 20s, com aviso quando
  o disfarce termina.

### 🔱 Tridente Lendário — NaitPlayer
* **Função:** tridente versátil e poderoso que aplica **cansaço** no alvo.
* **Extra registrado na wiki:** em tempestade o tridente **invoca um raio** no alvo.
* **No addon:** +9 de dano, **Fadiga de Mineração II** por 10s em cada acerto. Se estiver
  trovejando, um **raio cai no alvo** (com recarga de 5s para não virar metralhadora).

---

## 3. Regras gerais mantidas

| Regra do servidor | No addon |
|-------------------|----------|
| Itens quase indestrutíveis | Nenhum item tem durabilidade → **nunca quebram** |
| Aparência de item encantado | `minecraft:glint: true` em todos |
| Só se perdem no vazio/cactos | Como qualquer item: cacto e vazio destroem; lava **não** |
| Nenhum item "quebra" o survival normal | Todos têm receita e custo razoável |
| Batata é o único item negativo | Mantido (Lentidão V + anula a bota) |

---

## 4. Notas de portabilidade (Bedrock 26.52)

* `@minecraft/server` **2.0.0**: `applyKnockback` mudou de assinatura na 2.x — o addon tenta a
  forma nova (`{x, z}, y`) e cai na antiga (`x, z, força, y`) se der erro.
* O efeito **`glowing` não existe** no Bedrock (verificado na `vanilladata` oficial), por isso a
  Bússola Lendária usa rastro de partículas em vez de contorno.
* `world.afterEvents.itemUse` dispara também para blocos e alimentos; o script filtra pelo `typeId`.
* O lore e os encantamentos fixos são aplicados **por script a cada 40 ticks** porque itens
  criados por `/give` não carregam NBT — assim eles ficam iguais em qualquer forma de obtenção.
* Nomes de efeitos são passados com o namespace (`minecraft:speed`) e os encantamentos tentam
  as duas formas (com e sem `minecraft:`), o que evita quebra entre builds.
