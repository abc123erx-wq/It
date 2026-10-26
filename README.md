# TacGuns — Arsenal Brasileiro

Expansão do addon **TacGuns** (Minecraft Bedrock) com **46 armas brasileiras e de
facção** que herdam 100% do comportamento das armas originais: disparo, munição,
recarga, recarga tática, inspeção, saque, sprint, sway, recuo, pose de terceira
pessoa, bancada de trabalho e contador de munição no HUD.

## Conteúdo

| Categoria | Armas |
|---|---|
| Fuzis | IA2 5.56, IA2 7.62, MD97L, MD97LM, M964 FAL, MD2, T4, T4 CQC |
| Submetralhadoras | SAF 9mm, Mini-SAF, MT9 G2, SMT9, Uru 9mm, MT12 |
| Pistolas | PT92, PT24/7, TS9, TH9, G3c, GX4 |
| Revólveres | RT85, RT608, Raging Bull .454 |
| Precisão / escopetas | AGLC, ST12, CBC Military 3.0 |
| Facção — fuzis | AK-47, AKM, AK curta, AR-15 fantasma 3D, M16A1, G3A3, FAL internacional, SKS, Mini-14, Mosin serrado |
| Facção — SMG/pistolas | TEC-9, TEC-DC9, MAC-10, M11, Uzi, Kit Roni, Glock 18, espingarda serrada, FGC-9, PT24/7 raspada |

Além das armas: **7 acessórios modulares** — red dot, supressor, lanterna/laser,
foregrip e carregador estendido em qualquer arma; e os improvisados
**luneta amarrada** e **carregador duplo fitado**, exclusivos das armas de facção.
Todos com peça 3D própria em bone dedicado e propriedade sincronizada.

- Documentação técnica completa: [`docs/ARSENAL_BRASIL.md`](docs/ARSENAL_BRASIL.md)
- **Pacote pronto para instalar: [`release/TacGuns_Brasil.mcaddon`](release/TacGuns_Brasil.mcaddon)**
  (é o `.mcaddon` com os dois packs; clique em *Download* na pré-visualização do arquivo)

## Facções: escolha de lado (policial x ladrão)

O addon agora abre, no primeiro spawn, a tela **ESCOLHA SEU LADO — LEI OU
LIBERDADE?**: um card escuro dividido em duas metades, azul **POLICIAL** (escudo,
*PROTEJA A CIDADE / MANTENHA A ORDEM*) e vermelha **LADRÃO** (máscara, *FAÇA SEU
DINHEIRO / DESAFIE A LEI*). O lado escolhido vira tag (`policia` / `ladrao`),
define arsenal, kit inicial, economia e placar lateral.

| Recurso | POLICIAL | LADRÃO |
|---|---|---|
| Arsenal | 26 armas de dotação e forças especiais + 10 armas neutras | 20 armas de facção + 10 neutras |
| Acessórios exclusivos | — | luneta amarrada e carregador duplo fitado |
| Recuo por disparo | 0,022 (treinado) | 0,058 (arma sem manutenção) |
| Dano com arma própria / alheia | ×1,05 / ×0,75 | ×1,10 / ×0,70 |
| Recompensa por abate | +R$ 400 | +R$ 400 |
| Patentes | Recruta → Coronel | Verme → Dono |

Usar arma do lado oposto é bloqueado no `itemUse`; abater um oponente derruba a
arma dele no chão (apreensão). Comandos: `/scriptevent tac_guns:faccao` (trocar de
lado), `tac_guns:loja` (loja com dinheiro), `tac_guns:info` (ficha do jogador), e
`/tag @s add policia|ladrao` para definir por comando.

### Prisão e procurado

- **Algemas** (`tac_guns:algemas`, 4 ferro + 1 corrente): item policial; usar em um jogador
  do lado oposto prende — lentidão, sem armas e teleporte para a cela marcada com
  `/scriptevent tac_guns:marcar_cela`. Solta com novo clique, `/scriptevent tac_guns:soltar`
  ou em 60 s.
- **Nível de procurado** sobe com assaltos (+2) e abates entre facções (+4) e cai 1 ponto a
  cada 20 s; em 3 o ladrão vira **PROCURADO** (brilho + alerta com coordenadas para a polícia).

## Bases prontas por `/function`

Cheats ligados, área aberta e carregada, e:

| Comando | O que constrói |
|---|---|
| `/function policial` | base da PM: pátio com viatura, muro e portão, prédio de 2 andares, 2 celas, arsenal, heliponto com "H", torre e iluminação |
| `/function favela` | favela inteira: morro de 4 patamares, **52 barracos** colados com telha/laje/lona, becos de 1 bloco, escadões, varais, fios, galpão, quadra, **boca de fumo** e mirador |
| `/function lado_policial` | entrar/trocar para a Polícia sem depender do menu (tag + scoreboard + kit) |
| `/function lado_ladrao` | entrar/trocar para o Ladrão sem depender do menu |
| `/function faccao` | ajuda com todos os comandos de facção |

Cada estrutura é dividida em partes chamáveis (ex.: `/function favela/04_boca`). Mapas:
[`docs/estrutura_policial.png`](docs/estrutura_policial.png) e
[`docs/estrutura_favela.png`](docs/estrutura_favela.png).


## Instalação e solução de problemas

1. **Importe `release/TacGuns_Brasil.mcaddon`** (clique no arquivo → *Abrir com Minecraft*).
   Ele traz **dois packs**: `TacGuns(B)` (comportamento) e `TacGuns(R)` (recursos).
2. No mundo, ative **os dois** em *Conjuntos de comportamento* e *Pacotes de recursos*;
   a ordem do pacote de recursos não importa, mas o de comportamento precisa estar ativo
   para as armas atirarem.
3. Ligue **Cheats/Ativar trapaças** para usar `/function` e `/scriptevent`.
4. Versões antigas do addon com o **mesmo UUID** podem continuar sendo usadas pelo jogo:
   esta versão é **1.2.0** nas duas pontas — se você já tinha importado a 1.1.0, apague a
   cópia antiga em *Configurações → Armazenamento → Pacotes* antes de testar.

| Sintoma | Causa provável | Solução |
|---|---|---|
| Arma na mão sem modelo 3D / jogador invisível em 1ª pessoa | pack de **recursos** desativado, ou cópia antiga (1.1.0) com as raízes de primeira pessoa quebradas (corrigido na 1.2.0) | ative `TacGuns(R)` e reinstale a 1.2.0 |
| Menu de escolha de lado não abre | API de script indisponível na versão do jogo | use `/function lado_policial` ou `/function lado_ladrao` (funciona sem script) |
| Armas não causam dano / sem HUD de munição | pack de **comportamento** desativado ou script desligado | ative `TacGuns(B)`; o dano vem de `scripts/events/projectileHitEntity.js` |
| Não consigo atirar nem recarregar | cadeia de Molang do pack (que exige `is_using_item`) | nesta versão o tiro e a recarga são feitos por script (`events/weapons.js`): segure usar para atirar, agache + usar para recarregar; diagnóstico com `/scriptevent tac_guns:teste` |
| Arma flutuando longe da mão | o corpo novo não pode girar em torno de (0,0,0) | corrigido: cada modelo usa o bone e o pivô da arma original; o validador agora reprova o build se divergir |
| Nada acontece ao usar `/function` | cheats desligadas | ative *Ativar trapaças* no mundo |

Os scripts declaram `@minecraft/server` **2.0.0** e `@minecraft/server-ui` **2.0.0**
(API estável a partir do Minecraft 1.21.90 — versões 1.26.x inclusas).

## Como regenerar

```bash
pip install --break-system-packages pillow numpy
python3 tools/tacgen/build.py      # gera out/TacGuns(B) e out/TacGuns(R)
python3 tools/validate.py          # checagem estática (JSON, referências, sons, bones)
python3 tools/tacgen/docs.py       # gera docs/ARSENAL_BRASIL.md
python3 tools/tacgen/render_structures.py   # mapas das bases em docs/
cd out && zip -qr TacGuns_Brasil.mcaddon "TacGuns(B)" "TacGuns(R)"
mkdir -p ../release && cp TacGuns_Brasil.mcaddon ../release/
```

## Estrutura do gerador

| Arquivo | Função |
|---|---|
| `tools/tacgen/specs.py` | catálogo (id, família, calibre, dano, faixa de recarga, receita, lore, attachments, diretrizes 3D e animações) |
| `tools/tacgen/designs.py` | 18 desenhos voxel reutilizados pelas armas |
| `tools/tacgen/designs_crime.py` | 9 desenhos voxel da linha de facção (AK, AK curta, SKS, TEC-9, MAC-10, UZI, Kit Roni, AR fantasma, serrada) |
| `tools/tacgen/geometry.py` | enxerta o corpo novo no rig original + locators + cópia de 3ª pessoa + bones de attachment |
| `tools/tacgen/texture.py` | atlas 128×128 (grade 8×8 de células de 16 px) |
| `tools/tacgen/build.py` | clona itens, entidades, controladores, animações, eventos, funções, sons, ícones e lang |
| `tools/validate.py` | garante que todo id, animação, som, locator e bone referenciado existe |
| `tools/tacgen/templates/factions.js` | script da camada de facção (tela de escolha, loja, economia, prisão, procurado) |
| `tools/tacgen/structures.py` | gera as bases de `/function` (polícia e favela) em `.mcfunction` |
| `tools/tacgen/render_structures.py` | desenha os mapas das estruturas para a documentação |
| `tools/tacgen/docs.py` | gera a documentação a partir do modelo realmente produzido |

## Adicionar uma arma nova

1. Acrescente uma entrada em `tools/tacgen/specs.py` (`id`, `family`, `design`,
   `ammo`, `damage`, `prop_new` — faixa de propriedade livre —, `craft`, textos).
   Para armas de facção use `faction="crime"` (ganha os acessórios improvisados),
   `scale=` para ajustar o tamanho da silhueta e `recolor=` (`worn`, `rusty`,
   `ghost`, `wood`) para a paleta desgastada.
2. Rode `build.py`, `validate.py` e `docs.py`.

A arma nova nasce com todo o comportamento, o modelo voxel, o ícone, os sons, a
receita e a página na bancada.
