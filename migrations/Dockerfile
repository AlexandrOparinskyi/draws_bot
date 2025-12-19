FROM python:3.11-slim

WORKDIR /app

RUN pip install alembic environs asyncpg

COPY migrations/ ./migrations/
COPY alembic.ini .
COPY database/ ./database/
COPY config.py .

CMD ["alembic", "upgrade", "head"]