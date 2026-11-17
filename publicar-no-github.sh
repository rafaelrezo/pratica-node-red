#!/usr/bin/env bash
# Executar em um terminal com internet e gh autenticado como rafaelrezo.
set -euo pipefail

origem="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repositorio="rafaelrezo/pratica-node-red"
url="https://github.com/${repositorio}.git"
# O token legado do ambiente pode estar inválido; usa a sessão autenticada do gh.
unset GITHUB_TOKEN GH_TOKEN

if ! gh auth status >/dev/null 2>&1; then
  echo "Autentique o GitHub CLI: gh auth login -h github.com" >&2
  exit 1
fi

temporario="$(mktemp -d)"
trap 'rm -rf "$temporario"' EXIT
destino="$temporario/pratica-node-red"

if gh repo view "$repositorio" >/dev/null 2>&1; then
  gh repo clone "$repositorio" "$destino"
else
  mkdir -p "$destino"
fi

cp "$origem"/sensor.py "$origem"/atuador.py "$origem"/planta.js \
   "$origem"/gerar_fluxo.py "$origem"/fluxo-node-red.json \
   "$origem"/gerar_pdf.py "$origem"/gerar_figuras.py \
   "$origem"/PROMPTS-ESQUEMATICOS.md "$origem"/publicar-no-github.sh \
   "$origem"/README.md "$destino"/
mkdir -p "$destino/figuras"
cp "$origem"/figuras/*.png "$destino/figuras/"

export PRATICA_REPO_URL="$url"
export PRATICA_DESTINO="$destino"
python3 - <<'PY'
import os
from pathlib import Path
p = Path(os.environ['PRATICA_DESTINO']) / 'README.md'
texto = p.read_text(encoding='utf-8')
texto = texto.replace('URL_DO_REPOSITORIO', os.environ['PRATICA_REPO_URL'])
p.write_text(texto, encoding='utf-8')
PY

python3 "$destino/gerar_pdf.py"

if ! git -C "$destino" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$destino" init -b main
fi
if ! git -C "$destino" config user.name >/dev/null; then
  git -C "$destino" config user.name rafaelrezo
fi
if ! git -C "$destino" config user.email >/dev/null; then
  git -C "$destino" config user.email rafaelrezo@users.noreply.github.com
fi
git -C "$destino" add README.md sensor.py atuador.py planta.js gerar_fluxo.py \
  fluxo-node-red.json gerar_pdf.py gerar_figuras.py PROMPTS-ESQUEMATICOS.md \
  publicar-no-github.sh figuras pratica-node-red.pdf
if ! git -C "$destino" diff --cached --quiet; then
  git -C "$destino" commit -m "Publica prática TCP e Node-RED para alunos"
fi

if gh repo view "$repositorio" >/dev/null 2>&1; then
  git -C "$destino" push origin HEAD:main
else
  gh repo create "$repositorio" --public --source "$destino" --remote origin --push
fi

gh api "repos/$repositorio/contents/sensor.py" --jq .html_url
gh api "repos/$repositorio/contents/atuador.py" --jq .html_url
cp "$destino/README.md" "$destino/pratica-node-red.pdf" "$origem/"
echo "Publicado: https://github.com/$repositorio"
