#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until python - <<'PY'
import os
import time
import psycopg
from urllib.parse import urlparse

url = os.environ.get("DATABASE_URL", "")
# DATABASE_URL like: postgresql+psycopg://user:pass@host:5432/db
url = url.replace("postgresql+psycopg://", "postgresql://")
p = urlparse(url)
host = p.hostname
port = p.port or 5432
db = (p.path or "/")[1:]
user = p.username
password = p.password

try:
    conn = psycopg.connect(host=host, port=port, dbname=db, user=user, password=password, connect_timeout=2)
    conn.close()
    print("DB OK")
except Exception as e:
    print("DB not ready:", e)
    raise
PY
do
  echo "DB not ready yet, sleeping..."
  sleep 1
done

echo "PostgreSQL is ready."
