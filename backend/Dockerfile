FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV DATABASE_URL=postgresql://postgres:WIjbfaRGbyRnfKhKCkpRwggjMLRGbsmj@mainline.proxy.rlwy.net:14763/railway
ENV JWT_SECRET_KEY=my-secret-key-2026-change-this
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]
