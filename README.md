# KINO // Zombies — Browser Co-op

Um survival top-down original para navegador, inspirado no loop de rodadas, armas, perks, barricadas, Mystery Box e Pack-a-Punch de **Black Ops 1 Zombies**. Feito em Canvas 2D, sem assets oficiais; o mapa e os elementos visuais são desenhados pelo próprio projeto.

> **Sobre o ZIP do release:** `bo1-zombies-decompiled-main.zip` contém a decompilação do jogo nativo em C/C++ (não uma aplicação web). O código nativo não é executável em um navegador nem foi embutido neste projeto. Este repositório cria uma adaptação web independente para oferecer a partida online solicitada.

## Rodar localmente

Requer Node.js 18+; não precisa instalar dependências.

```bash
npm start
```

Abra `http://localhost:4173`. Para hospedar em qualquer servidor estático, publique os arquivos do repositório (a entrada é `index.html`).

## Ativar o modo online no Firebase

O cliente usa Firebase JavaScript SDK **10.12.5**, servido localmente em `vendor/firebase/`.

1. No Firebase Console do projeto `kaka-ca0ff`, crie/ative o **Realtime Database**.
2. Em **Authentication → Sign-in method**, habilite **Anonymous**.
3. Publique as regras em `database.rules.json` no Realtime Database. Pela Firebase CLI, depois de selecionar o projeto:

   ```bash
   firebase deploy --only database
   ```

4. Publique a aplicação em um servidor HTTPS. Para Firebase Hosting:

   ```bash
   firebase deploy --only hosting
   ```

   `firebase.json` já aponta para a raiz do projeto e para as regras do Database.
5. Abra a página, escolha um codinome e crie uma sala. Compartilhe o código de 5 caracteres; os demais jogadores digitam o código, marcam **Pronto** e o host inicia.

A configuração web enviada pelo usuário está em `js/config.js`. A chave `apiKey` do SDK web identifica o projeto, não é uma senha; a proteção de escrita vem das regras do Realtime Database. As regras exigem usuário autenticado anonimamente, limitam cada jogador às próprias entradas de presença/controles e reservam os snapshots da partida ao host da sala.

### Limites do modelo online

A simulação é autoritativa no navegador do host: clientes enviam movimento/ações e recebem snapshots do Firebase. Se o host fechar a página, a sala é encerrada; não há migração de host ou servidor anti-cheat. Para lançamento público competitivo, mova a simulação para um backend confiável e revise quotas/limites do Firebase.

## Controles

- **WASD** — mover; **Shift** — correr.
- **Mouse** — mirar e atirar; **R** — recarregar; **V** ou **Espaço** — corpo a corpo.
- **E** — abrir porta, comprar arma/perk, ligar energia, usar a Mystery Box/Pack-a-Punch ou reparar barricada. Segure **E** perto de um aliado abatido para reanimá-lo.
- **1 / 2 / 3** — trocar slot de arma; **Tab** — placar; **Esc** — menu de pausa.
- Em telas touch, use os analógicos e botões na tela.

## Estrutura

- `js/simulation.js` — rodadas, zumbis, combate, compras, perks e estado autoritativo.
- `js/firebase.js` — autenticação anônima, salas, presença e snapshots no Realtime Database.
- `js/map.js` + `data/map_theater.json` — parser de layout no formato familiar ao mapkit e colisões do mapa web.
- `js/view.js` — renderer Canvas 2D; `js/input.js` — controles teclado/mouse/touch.
- `database.rules.json` — regras do Firebase; `vendor/firebase/` — SDK modular local e licença Apache-2.0.

## Créditos e licença

Projeto de fã independente, sem associação com Activision/Treyarch. Nomes internos de algumas armas/perks foram usados apenas como referência de compatibilidade conceitual; não foram copiados executáveis, modelos, texturas, áudio ou mapas oficiais. Os bundles do Firebase são distribuídos sob Apache-2.0; consulte `vendor/firebase/LICENSE`.
