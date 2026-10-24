#!/usr/bin/env bash
# Monta um "node_modules" falso com o mock da API @minecraft/server e roda o
# teste de fumaca dos scripts do addon.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${TMPDIR:-/tmp}/cs-mock"

rm -rf "$OUT"
mkdir -p "$OUT/node_modules/@minecraft/server" "$OUT/scripts"

# mock da API
cp "$ROOT/tools/mock/server.mjs" "$OUT/node_modules/@minecraft/server/index.mjs"
cat > "$OUT/node_modules/@minecraft/server/package.json" <<'EOF'
{ "name": "@minecraft/server", "version": "2.0.0", "type": "module", "main": "index.mjs" }
EOF

# scripts do addon (imports .js -> .mjs)
for f in "$ROOT"/src/behavior_pack/scripts/*.js; do
  base="$(basename "${f%.js}")"
  sed -E 's/(from "\.\/[a-z_]+)\.js"/\1.mjs"/g' "$f" > "$OUT/scripts/$base.mjs"
done

cp "$ROOT/tools/mock/harness.mjs" "$OUT/harness.mjs"
cd "$OUT"
node harness.mjs
