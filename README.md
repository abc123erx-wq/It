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
- Pacote pronto para instalar: `out/TacGuns_Brasil.mcaddon`

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

## Como regenerar

```bash
pip install --break-system-packages pillow numpy
python3 tools/tacgen/build.py      # gera out/TacGuns(B) e out/TacGuns(R)
python3 tools/validate.py          # checagem estática (JSON, referências, sons, bones)
python3 tools/tacgen/docs.py       # gera docs/ARSENAL_BRASIL.md
cd out && zip -qr TacGuns_Brasil.mcaddon "TacGuns(B)" "TacGuns(R)"
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
| `tools/tacgen/templates/factions.js` | script da camada de facção (tela de escolha, loja, economia, apreensão) |
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
