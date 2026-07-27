#!/usr/bin/env bash
set -euo pipefail

API_URL="${1:?Uso: $0 <api-url> <web-url>}"
WEB_URL="${2:?Uso: $0 <api-url> <web-url>}"

API_URL="${API_URL%/}"
WEB_URL="${WEB_URL%/}"

echo "[1/4] Saúde da API"
curl --fail --silent --show-error "$API_URL/health"
echo

echo "[2/4] Eventos da América Latina"
curl --fail --silent --show-error \
  "$API_URL/api/v1/events?region=latin-america&include_finished=true&limit=30" \
  | python -c 'import json,sys; data=json.load(sys.stdin); print("total:", data["total"])'

echo "[3/4] Saúde do frontend"
curl --fail --silent --show-error "$WEB_URL/api/health"
echo

echo "[4/4] Página inicial"
curl --fail --silent --show-error --output /dev/null "$WEB_URL/"

echo "Implantação validada."
