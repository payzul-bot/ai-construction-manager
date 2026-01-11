FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

# 1) Метаданные проекта (нужно для pip install .)
COPY pyproject.toml /app/pyproject.toml

# 2) ВАЖНО: копируем пакет app ДО pip install .
COPY app /app/app

# 3) Скрипты
COPY scripts /app/scripts

# 4) Ставим зависимости и сам пакет
RUN python -m pip install --no-cache-dir -U pip \
 && python -m pip install --no-cache-dir .

RUN chmod +x /app/scripts/wait_for_db.sh || true

EXPOSE 8000

CMD ["/bin/sh","-c","/app/scripts/wait_for_db.sh && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
