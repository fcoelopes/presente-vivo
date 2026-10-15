#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p backups
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
docker compose exec -T presente-vivo python -c 'import os,sqlite3,sys; src=sqlite3.connect(os.environ["DB_PATH"]); dst=sqlite3.connect(sys.argv[1]); src.backup(dst); dst.close(); src.close()' "/data/.backup-${stamp}.sqlite3"
docker compose cp "presente-vivo:/data/.backup-${stamp}.sqlite3" "backups/presentes-${stamp}.sqlite3"
docker compose exec -T presente-vivo python -c 'import os,sys; os.remove(sys.argv[1])' "/data/.backup-${stamp}.sqlite3"
echo "Backup concluído: backups/presentes-${stamp}.sqlite3"
