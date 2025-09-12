FROM python:3.10-slim
WORKDIR /app

# Install FastAPI and Uvicorn directly
RUN pip install --no-cache-dir fastapi uvicorn[standard]

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
