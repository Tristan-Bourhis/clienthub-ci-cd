#!/usr/bin/env bash
# Test isolé sur le runner CI : même configuration que la VM, port 8007.
set -euo pipefail
deploy_test_dir=$(mktemp -d)
cp deploy/compose.yml init.sql "$deploy_test_dir/"
export APP_IMAGE=clienthub-api:local
export DB_PASSWORD MYSQL_ROOT_PASSWORD
DB_PASSWORD=$(openssl rand -hex 24)
MYSQL_ROOT_PASSWORD=$(openssl rand -hex 24)
compose=(docker compose -p clienthub-deploy-test -f "$deploy_test_dir/compose.yml")
cleanup() {
  "${compose[@]}" logs --tail=50 || true
  "${compose[@]}" down -v || true
}
trap cleanup EXIT
"${compose[@]}" up -d --wait --wait-timeout 180
first_id=$("${compose[@]}" ps -q api)
"${compose[@]}" up -d --wait --wait-timeout 180
second_id=$("${compose[@]}" ps -q api)
test -n "$first_id" && test "$first_id" = "$second_id"
API_URL=http://127.0.0.1:8007 WEB_URL=http://127.0.0.1:8007 python3 tests/check_http.py
echo 'Déploiement répété : même conteneur API, tests HTTP réussis sur 8007.'
