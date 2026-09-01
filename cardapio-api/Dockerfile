# =====================================================================
# DOCKERFILE DIDÁTICO - CARDÁPIO API (PRODUÇÃO / RENDER)
# =====================================================================

# 1. Imagem Base Oficial do Python (Versão Slim: leve, rápida e segura)
FROM python:3.13-slim

# 2. Variáveis de ambiente para comportamento ideal do Python em containers:
#    - PYTHONDONTWRITEBYTECODE: impede a criação de arquivos .pyc
#    - PYTHONUNBUFFERED: envia saídas de log diretamente para o terminal em tempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Diretório de trabalho dentro do container
WORKDIR /app

# 4. Instalação de dependências mínimas do sistema (libpq para PostgreSQL e curl para healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 5. CONCEITO: Otimização de Cache de Camadas do Docker
#    Copia apenas o requirements.txt primeiro. Se o código mudar mas os
#    pacotes continuarem os mesmos, o Docker reutiliza o cache do pip install!
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 6. Copia os arquivos da aplicação
COPY app/ ./app/
COPY frontend/ ./frontend/
COPY migrations/ ./migrations/
COPY alembic.ini .
COPY main.py .

# 7. Documenta a porta que a aplicação escuta internamente
EXPOSE 8000

# 8. CONCEITO: Execução de Migrações no Boot e Inicialização
#    - alembic upgrade head: garante que as tabelas no Supabase sejam criadas/atualizadas automaticamente no deploy.
#    - uvicorn main:app: inicia o servidor FastAPI.
#    - ${PORT:-8000}: escuta na porta dinâmica injetada pelo Render (ex: 10000) ou 8000 por padrão.
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]

