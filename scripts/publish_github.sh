#!/usr/bin/env bash
set -euo pipefail

REPO="${1:-ncevidanes/hep-conference-hub}"
cd "$(dirname "$0")/.."

command -v git >/dev/null || { echo "git não encontrado"; exit 1; }
command -v gh >/dev/null || { echo "GitHub CLI não encontrado"; exit 1; }

gh auth status

if [[ ! -d .git ]]; then
  git init -b main
fi

git branch -M main
git add .

if ! git diff --cached --quiet; then
  git commit -m "release: prepare HEP Conference Hub v1.0.0"
fi

if git remote get-url origin >/dev/null 2>&1; then
  current="$(git remote get-url origin)"
  echo "Remote origin existente: $current"
else
  if gh repo view "$REPO" >/dev/null 2>&1; then
    git remote add origin "https://github.com/$REPO.git"
  else
    gh repo create "$REPO"       --public       --description "Auditable portal for discovering and monitoring high-energy physics events"       --source=.       --remote=origin
  fi
fi

git push -u origin main

echo
echo "Repositório enviado para https://github.com/$REPO"
echo "Ative agora o repositório no Zenodo ANTES de criar a release."
