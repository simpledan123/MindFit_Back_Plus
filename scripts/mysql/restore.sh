#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <backup.sql>"
  exit 1
fi

FILE=$1
CONTAINER=${MYSQL_CONTAINER:-mindfit-mysql}
DB=${MYSQL_DATABASE:-mindfit_db}
USER=${MYSQL_USER:-mindfit_app}
PASS=${MYSQL_PASSWORD:-mindfit_pass}

cat "$FILE" | docker exec -i "$CONTAINER" sh -c "mysql -u${USER} -p${PASS} ${DB}"

echo "✅ Restored from: $FILE"
