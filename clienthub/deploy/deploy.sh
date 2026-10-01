#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/clienthub-8007"
umask 077
# Arguments non secrets : nom complet de l'image et SHA Git.
image="$1"
sha="$2"
[[ "$image" =~ ^[a-z0-9._/-]+$ && "$sha" =~ ^[a-f0-9]{40}$ ]]
docker compose version >/dev/null
# Les mots de passe restent identiques entre deux déploiements.
if [[ ! -f .env ]]; then
  printf 'DB_PASSWORD=%s\nMYSQL_ROOT_PASSWORD=%s\n' \
    "$(openssl rand -hex 32)" "$(openssl rand -hex 32)" > .env
fi
export APP_IMAGE="$image:$sha"
docker compose -f compose.yml pull
docker compose -f compose.yml up -d --wait --wait-timeout 180
curl --fail --silent --show-error --retry 10 --retry-all-errors --retry-delay 2 \
  --max-time 5 http://127.0.0.1:8007/health
docker compose -f compose.yml ps
