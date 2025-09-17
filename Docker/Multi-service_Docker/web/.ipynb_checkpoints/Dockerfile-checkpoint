FROM python:3.11-slim

WORKDIR /app

# system deps (Postgres client libs for psycopg2 if needed)
RUN apt-get update && apt-get install -y gcc libpq-dev --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copy app code
COPY . .

ENV PYTHONUNBUFFERED=1

# uvicorn entry
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
