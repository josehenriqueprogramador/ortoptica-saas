FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema necessárias para processamento numérico/visão computacional
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Comando correto que lê o nosso Session Orchestrator modularizado
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
