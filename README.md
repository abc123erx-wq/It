# TacGuns — Arsenal Brasileiro

Expansão do addon **TacGuns** (Minecraft Bedrock) com **26 armas brasileiras** que
herdam 100% do comportamento das armas originais: disparo, munição, recarga, recarga
tática, inspeção, saque, sprint, sway, recuo, pose de terceira pessoa, bancada de
trabalho e contador de munição no HUD.

## Conteúdo

| Categoria | Armas |
|---|---|
| Fuzis | IA2 5.56, IA2 7.62, MD97L, MD97LM, M964 FAL, MD2, T4, T4 CQC |
| Submetralhadoras | SAF 9mm, Mini-SAF, MT9 G2, SMT9, Uru 9mm, MT12 |
| Pistolas | PT92, PT24/7, TS9, TH9, G3c, GX4 |
| Revólveres | RT85, RT608, Raging Bull .454 |
| Precisão / escopetas | AGLC, ST12, CBC Military 3.0 |

Além das armas: **5 acessórios modulares** (red dot, supressor, lanterna/laser,
foregrip, carregador estendido) que se instalam em qualquer arma, com peça 3D
própria em um bone dedicado.

- Documentação técnica completa: [`docs/ARSENAL_BRASIL.md`](docs/ARSENAL_BRASIL.md)
- Pacote pronto para instalar: `out/TacGuns_Brasil.mcaddon`

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
| `tools/tacgen/geometry.py` | enxerta o corpo novo no rig original + locators + cópia de 3ª pessoa + bones de attachment |
| `tools/tacgen/texture.py` | atlas 128×128 (grade 8×8 de células de 16 px) |
| `tools/tacgen/build.py` | clona itens, entidades, controladores, animações, eventos, funções, sons, ícones e lang |
| `tools/validate.py` | garante que todo id, animação, som, locator e bone referenciado existe |
| `tools/tacgen/docs.py` | gera a documentação a partir do modelo realmente produzido |

## Adicionar uma arma nova

1. Acrescente uma entrada em `tools/tacgen/specs.py` (`id`, `family`, `design`,
   `ammo`, `damage`, `prop_new` — faixa de propriedade livre —, `craft`, textos).
2. Rode `build.py`, `validate.py` e `docs.py`.

A arma nova nasce com todo o comportamento, o modelo voxel, o ícone, os sons, a
receita e a página na bancada.
