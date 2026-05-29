# Base estável e leve com suporte a binários compilados em C
FROM python:3.11-slim

# Evita que o Python escreva arquivos .pyc no disco e força o output para o terminal sem buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências nativas de sistema necessárias para OpenCV Headless e SQLite assíncrono
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala a lista de dependências Python para aproveitar o cache de camadas do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia a estrutura da aplicação e o inicializador do banco de dados
COPY app/ ./app/
COPY database.py .

# Expõe a porta padrão do motor biométrico
EXPOSE 8000

# Inicializa o servidor Uvicorn apontando para o gateway mestre na porta exposta
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
