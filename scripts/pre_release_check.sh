#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

required=(
  README.md
  LICENSE
  CITATION.cff
  .zenodo.json
  codemeta.json
  CHANGELOG.md
  RELEASE_NOTES_v1.0.0.md
  docker-compose.yml
)

for file in "${required[@]}"; do
  [[ -f "$file" ]] || { echo "ERRO: arquivo ausente: $file"; exit 1; }
done

python -m json.tool .zenodo.json >/dev/null
python -m json.tool codemeta.json >/dev/null
docker compose config -q

if find . -type f \( -name '*.rej' -o -name '*.orig' \) | grep -q .; then
  echo "ERRO: existem arquivos .rej ou .orig"
  exit 1
fi

if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  echo "ERRO: .env está versionado"
  exit 1
fi

if grep -RInE --exclude-dir=.git --exclude='*.md'   '(ZENODO_TOKEN|GITHUB_TOKEN|password[[:space:]]*=|secret[[:space:]]*=)' .; then
  echo "AVISO: revise possíveis segredos encontrados acima."
fi

echo "Metadados JSON válidos e estrutura básica aprovada."
echo "Execute a suíte de testes e o build do frontend antes da release."
