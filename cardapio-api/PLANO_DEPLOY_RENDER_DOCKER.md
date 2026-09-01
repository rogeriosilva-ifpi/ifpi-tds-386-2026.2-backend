# Plano Didático: Preparação para Deploy no Render com Docker e Supabase

## Visão Geral do Projeto Didático
O objetivo desta etapa é preparar o projeto `cardapio-api` para ser publicado na nuvem (**Deploy**) na plataforma **Render** utilizando **Docker**, conectando-se ao **Supabase** como banco de dados PostgreSQL gerenciado.

Com essa configuração, a aplicação terá:
1. **Containerização Portável (Dockerfile)**: A aplicação roda em qualquer servidor (Linux, Mac, Windows, Cloud) exatamente da mesma forma.
2. **Execução Automática de Migrações no Boot**: O container roda `alembic upgrade head` antes de subir o Uvicorn, garantindo que as tabelas no Supabase estejam sempre atualizadas.
3. **Frontend e Backend Integrados no Mesmo Domínio**: O Render servirá tanto a API REST quanto o Frontend Reativo sob HTTPS (`https://sua-api.onrender.com/frontend/`), eliminando qualquer problema de CORS ou protocolo misto.
4. **Respeito Dinâmico à Porta do Render**: O Render injeta dinamicamente a variável de ambiente `PORT` (geralmente `10000`). O container se adaptará automaticamente.

---

## Fluxo de Deploy: Do Git ao Render e Supabase

```mermaid
flowchart TD
    subgraph Dev ["1. Ambiente de Desenvolvimento"]
        GIT["Git (GitHub / GitLab)"]
        DOCKERFILE["Dockerfile + .dockerignore"]
    end

    subgraph RenderPlatform ["2. Plataforma Render (Web Service)"]
        BUILD["Render Docker Builder"]
        RUN["Container em Execução\n(Porta dinâmica: $PORT)"]
        ALEMBIC_BOOT["alembic upgrade head\n(Executado no arranque)"]
        UVICORN["uvicorn main:app --host 0.0.0.0 --port $PORT"]
    end

    subgraph SupabaseCloud ["3. Banco de Dados (Supabase)"]
        PG_CLOUD[("PostgreSQL Gerenciado\n(SSL Obrigatório)")]
    end

    GIT -->|git push| BUILD
    DOCKERFILE --> BUILD
    BUILD --> RUN
    RUN --> ALEMBIC_BOOT
    ALEMBIC_BOOT -->|Aplica Migrações DDL| PG_CLOUD
    ALEMBIC_BOOT --> UVICORN
    UVICORN -->|Consultas e Operações CRUD| PG_CLOUD
```

---

## User Review Required

> [!IMPORTANT]
> **Ajuste no `frontend/api.js` para Domínios da Nuvem**:
> Atualmente, o `API_BASE_URL` verifica se a porta local é `:8000`. Na nuvem (Render), a aplicação roda na porta padrão HTTPS (443) em um domínio como `https://cardapio-api.onrender.com`. Ajustaremos o `API_BASE_URL` para detectar automaticamente quando estiver rodando no Render, consumindo o próprio domínio de forma transparente.

> [!NOTE]
> **Execução de Migrações no Arranque do Container**:
> Configuraremos o comando de inicialização do container para rodar `alembic upgrade head && uvicorn ...`. Dessa forma, os alunos não precisam rodar migrações manualmente no banco de produção: o próprio container atualiza o Supabase ao ser iniciado.

> [!TIP]
> **Prevenção do Erro de Quebra de Linha (CRLF do Windows)**:
> Em vez de criar um arquivo `entrypoint.sh` separado (que frequentemente falha em máquinas de alunos Windows devido a quebras de linha `\r\n`), utilizaremos `CMD sh -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"` direto no `Dockerfile`. É 100% à prova de falhas em qualquer sistema operacional.

---

## Estrutura de Arquivos Proposta

```text
cardapio-api/
├── Dockerfile                  # [NOVO] Especificação da imagem Docker de produção
├── .dockerignore               # [NOVO] Impede envio de .venv, .env, *.db e caches
├── render.yaml                 # [NOVO - Opcional] Blueprint de infraestrutura como código (IaC)
├── frontend/
│   └── api.js                  # [MODIFICAR] Suporte automático ao domínio de produção do Render
├── PLANO_DEPLOY_RENDER_DOCKER.md # [NOVO] Guia passo a passo para o Render e Supabase
└── README.md                   # [MODIFICAR] Inclusão das instruções de Deploy
```

---

## Proposed Changes

---

### Componente 1: Containerização da Aplicação

#### [NEW] `Dockerfile`
Imagem leve baseada em `python:3.13-slim` com cache eficiente de camadas e segurança:

```dockerfile
# Imagem base oficial do Python (leve e segura)
FROM python:3.13-slim

# Variáveis de ambiente para comportamento ideal do Python em containers:
# - PYTHONDONTWRITEBYTECODE: evita geração de arquivos .pyc no container
# - PYTHONUNBUFFERED: envia logs diretamente para o stdout/stderr em tempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema necessárias para PostgreSQL e utilitários
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 1. Copia primeiro apenas o requirements.txt para aproveitar o cache de camadas do Docker
COPY requirements.txt .

# 2. Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copia o código-fonte da aplicação
COPY app/ ./app/
COPY frontend/ ./frontend/
COPY migrations/ ./migrations/
COPY alembic.ini .
COPY main.py .

# Informa a porta esperada (documentação interna do Docker)
EXPOSE 8000

# Executa as migrações no banco (Alembic) e inicia o servidor Uvicorn
# ${PORT:-8000} permite que o Render defina a porta dinamicamente (ex: 10000)
CMD sh -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"
```

#### [NEW] `.dockerignore`
Garante que arquivos pesados ou confidenciais não sejam copiados para a imagem Docker:
```dockerignore
# Ambientes virtuais locais
.venv/
venv/
env/

# Byte-code Python
__pycache__/
*.py[cod]

# Bancos de dados locais e caches
*.db
*.sqlite
*.sqlite3
.pytest_cache/
.coverage
htmlcov/

# Segredos e variáveis de ambiente (CRÍTICO!)
.env
.env.local
.env.*.local

# Controle de versão e IDEs
.git/
.gitignore
.vscode/
.idea/
.DS_Store

# Documentos locais dispensáveis no container
PLANO*.md
```

---

### Componente 2: Ajuste no Frontend para Produção

#### [MODIFY] `frontend/api.js`
Garante que em produção no Render (`https://...onrender.com`), a API utilize o próprio domínio de onde a página foi carregada, enquanto em servidores locais de desenvolvimento (`3000`, `5500`, `5173`) aponte para `http://127.0.0.1:8000`:

```javascript
// Detecta se está rodando em servidor local separado (ex: Live Server 5500 ou Vite 5173)
// Caso contrário (rodando no Render na nuvem ou no FastAPI local), usa a própria origem!
const portasDevSeparadas = ["3000", "5500", "5173"];
const API_BASE_URL = portasDevSeparadas.includes(window.location.port)
    ? "http://127.0.0.1:8000"
    : window.location.origin;
```

---

### Componente 3: Infraestrutura como Código para o Render (IaC)

#### [NEW] `render.yaml`
Permite aos alunos subir o serviço no Render com configuração automática:
```yaml
services:
  - type: web
    name: cardapio-api
    env: docker
    plan: free
    region: oregon
    healthCheckPath: /
    envVars:
      - key: DATABASE_URL
        sync: false # O aluno preencherá a string do Supabase no painel do Render
      - key: ENVIRONMENT
        value: production
      - key: DEBUG
        value: "false"
```

---

## Guia Didático: Como os Alunos Publicam no Render e Supabase

### Passo 1: Obter o Banco PostgreSQL no Supabase
1. Acesse [supabase.com](https://supabase.com) e crie um projeto gratuito.
2. Em **Project Settings $\rightarrow$ Database**, localize a seção **Connection string**.
3. Selecione a aba **URI** e copie a URL no modo **Pooler** (Porta 6543) ou **Direct** (Porta 5432).
   Exemplo: `postgresql://postgres.[ref]:[sua_senha]@aws-0-[regiao].pooler.supabase.com:6543/postgres?sslmode=require`

### Passo 2: Subir o Projeto no Render
1. Acesse [render.com](https://render.com) e conecte seu repositório GitHub.
2. Clique em **New $\rightarrow$ Web Service**.
3. Selecione o repositório `cardapio-api`.
4. O Render detectará automaticamente o **Dockerfile**.
5. Em **Environment Variables**, adicione:
   - `DATABASE_URL`: cole a string obtida do Supabase no Passo 1.
   - `ENVIRONMENT`: `production`
   - `DEBUG`: `false`
6. Clique em **Create Web Service**.

### Passo 3: O Render Faz Tudo Automaticamente!
- O Render compila a imagem Docker.
- O container inicia e roda: `alembic upgrade head` $\rightarrow$ cria e atualiza as tabelas no Supabase!
- O Uvicorn sobe e disponibiliza a aplicação sob HTTPS com certificado SSL grátis:
  - **API:** `https://seu-cardapio.onrender.com/`
  - **Swagger:** `https://seu-cardapio.onrender.com/docs`
  - **Frontend:** `https://seu-cardapio.onrender.com/frontend/`

---

## Plano de Verificação

### 1. Teste de Build Local da Imagem Docker
Executar o comando no terminal para garantir que a imagem compila sem erros:
```bash
docker build -t cardapio-api:local .
```

### 2. Teste de Execução do Container Local
Subir o container localmente apontando para SQLite ou PostgreSQL:
```bash
docker run --rm -p 8000:8000 -e PORT=8000 -e DATABASE_URL=sqlite:///./cardapio.db cardapio-api:local
```
Validar se:
- O Alembic roda `upgrade head` sem falhas.
- O Uvicorn responde na porta 8000.
- A rota `/` responde 200 OK.
- O frontend em `http://localhost:8000/frontend/` carrega e lista os pratos.

### 3. Validação dos Testes Automatizados
```bash
pytest -v
```
Garantir que a suíte de testes continue 100% passando.
