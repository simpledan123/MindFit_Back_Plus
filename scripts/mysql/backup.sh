#!/usr/bin/env bash
set -euo pipefail

CONTAINER=${MYSQL_CONTAINER:-mindfit-mysql}
DB=${MYSQL_DATABASE:-mindfit_db}
USER=${MYSQL_USER:-mindfit_app}
PASS=${MYSQL_PASSWORD:-mindfit_pass}
OUTDIR=${OUTDIR:-./backups/mysql}
TS=$(date +"%Y%m%d_%H%M%S")

mkdir -p "$OUTDIR"

docker exec "$CONTAINER" sh -c \
  "mysqldump -u${USER} -p${PASS} --single-transaction --routines --events ${DB}" \
  > "${OUTDIR}/${DB}_${TS}.sql"

echo "✅ Backup saved: ${OUTDIR}/${DB}_${TS}.sql"
