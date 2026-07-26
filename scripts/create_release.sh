#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-1.0.0}"
TAG="v$VERSION"

cd "$(dirname "$0")/.."

command -v gh >/dev/null || { echo "GitHub CLI não encontrado"; exit 1; }

read -r -p "O repositório já foi habilitado na integração GitHub do Zenodo? [s/N] " answer
case "$answer" in
  s|S|sim|SIM) ;;
  *) echo "Release cancelada. Habilite o repositório no Zenodo primeiro."; exit 1 ;;
esac

bash scripts/pre_release_check.sh

git status --short
if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERRO: existem mudanças sem commit."
  exit 1
fi

if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "ERRO: tag $TAG já existe."
  exit 1
fi

git tag -a "$TAG" -m "HEP Conference Hub $VERSION"
git push origin "$TAG"

gh release create "$TAG"   --title "HEP Conference Hub $VERSION"   --notes-file RELEASE_NOTES_v1.0.0.md   --latest

echo "Release publicada. Aguarde o processamento no Zenodo."
