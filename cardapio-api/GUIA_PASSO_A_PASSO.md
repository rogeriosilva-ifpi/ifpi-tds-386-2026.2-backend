---
marp: true
theme: default
paginate: true
header: "IFPI TDS 386 • Roteiro Prático Passo a Passo (Hands-on Lab)"
footer: "Prof. Rogério Silva • 2026.2"
style: |
  section {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f8fafc;
    color: #1e293b;
    padding: 35px 50px;
  }
  h1 { color: #0f766e; }
  h2 { color: #047857; font-size: 1.5rem; border-bottom: 2px solid #10b981; padding-bottom: 4px; }
  h3 { color: #0369a1; font-size: 1.2rem; }
  code { background-color: #e2e8f0; color: #0f172a; padding: 2px 6px; border-radius: 4px; font-size: 0.88em; }
  pre code { background-color: transparent; font-size: 0.82em; }
  .step-badge { display: inline-block; background: #0f766e; color: white; padding: 3px 10px; border-radius: 20px; font-weight: bold; font-size: 0.85em; margin-bottom: 6px; }
  .box { background: #ffffff; border-left: 5px solid #10b981; padding: 10px 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin: 8px 0; }
  .cmd { background: #0f172a; color: #38bdf8; padding: 10px 14px; border-radius: 8px; font-family: monospace; font-size: 0.85em; margin: 8px 0; }
---

<!-- Slide 01: Capa -->
# 🛠️ Roteiro Prático Passo a Passo
## Construção do Cardápio Digital: Do Zero ao Deploy na Nuvem

**Curso:** Técnico em Desenvolvimento de Sistemas (IFPI TDS 386)  
**Disciplina:** Desenvolvimento Backend  
**Professor:** Rogério Silva  
**Guia Prático de Laboratório:** 40 Passos Granulares para Professor e Alunos

---

<!-- Slide 02: Mapa das 7 Fases -->
## 🗺️ Mapa Geral das 7 Fases do Projeto

```mermaid
flowchart LR
    F1["Fase 1\nAmbiente & Rotas"] --> F2["Fase 2\nParâmetros & Erros"]
    F2 --> F3["Fase 3\nSQLModel & Schemas"]
    F3 --> F4["Fase 4\nCRUD & Injeção"]
    F4 --> F5["Fase 5\n.env & Alembic"]
    F5 --> F6["Fase 6\nFrontend Reativo"]
    F6 --> F7["Fase 7\nDocker & Deploy"]
```

- **Fase 1 (Passos 1 a 5):** Setup do ambiente Python, Uvicorn e primeiro endpoint.
- **Fase 2 (Passos 6 a 10):** Path Params, Query Params, HTTPException e Git.
- **Fase 3 (Passos 11 a 15):** Schemas de validação e modelo ORM com SQLModel.
- **Fase 4 (Passos 16 a 21):** SQLite, Injeção de Dependência (`Depends`) e CRUD.
- **Fase 5 (Passos 22 a 29):** Variáveis de ambiente (`.env`), PostgreSQL e Alembic.
- **Fase 6 (Passos 30 a 35):** Arquitetura reativa no frontend (State, Observer, Fetch).
- **Fase 7 (Passos 36 a 40):** Testes com pytest, Dockerfile e deploy no Render com Supabase.

---

<!-- Slide 03: Passo 1 -->
## <span class="step-badge">Passo 01</span> Criar e Ativar o Ambiente Virtual

### Objetivo:
Isolar as dependências do projeto para não poluir o Python global do seu computador.

### Comandos no Terminal:
```bash
# 1. Entrar na pasta do projeto
cd cardapio-api

# 2. Criar o ambiente virtual .venv
python -m venv .venv

# 3. Ativar o ambiente virtual:
# No Linux / macOS:
source .venv/bin/activate

# No Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

<div class="box">
💡 <b>Verificação:</b> O prefixo <code>(.venv)</code> deve aparecer antes do seu prompt no terminal.
</div>

---

<!-- Slide 04: Passo 2 -->
## <span class="step-badge">Passo 02</span> Instalar FastAPI e Uvicorn

### Objetivo:
Instalar o framework web assíncrono e o servidor ASGI de alta performance.

### Comando no Terminal:
```bash
pip install "fastapi>=0.115.0" "uvicorn[standard]>=0.30.0"
```

### O que cada um faz?
- **`fastapi`:** Cuida das rotas, validações de tipos, serialização de JSON e Swagger.
- **`uvicorn[standard]`:** É o servidor web ultrarrápido que escuta requisições na porta de rede.

---

<!-- Slide 05: Passo 3 -->
## <span class="step-badge">Passo 03</span> Criar o Primeiro Endpoint (Hello World)

### Objetivo:
Escrever o código inicial no arquivo `main.py` e testar a resposta JSON.

### Ação: Criar o arquivo `main.py`:
```python
from fastapi import FastAPI

app = FastAPI(title="Cardápio API - IFPI TDS")

@app.get("/")
def raiz():
    return {"mensagem": "API do Cardápio no AR!"}

@app.get("/hello")
def saudacao():
    return {"mensagem": "Olá turma TDS 386! Bem-vindos ao Backend!"}
```

<div class="box">
💡 <b>Conceito:</b> Qualquer <code>dict</code> retornado por uma função decorada vira automaticamente um JSON HTTP válido!
</div>

---

<!-- Slide 06: Passo 4 -->
## <span class="step-badge">Passo 04</span> Iniciar o Servidor Uvicorn com `--reload`

### Objetivo:
Colocar a API para rodar com recarregamento automático a cada alteração de código.

### Comando no Terminal:
```bash
uvicorn main:app --reload --port 8000
```

### Entendendo o comando:
- `main`: Nome do arquivo Python (`main.py`).
- `:app`: Nome da variável da instância `FastAPI()` dentro do arquivo.
- `--reload`: Reinicia o servidor sozinho sempre que você salvar um arquivo `.py`.
- `--port 8000`: Define a porta TCP de escuta.

---

<!-- Slide 07: Passo 5 -->
## <span class="step-badge">Passo 05</span> Explorar o Swagger UI Interativo

### Objetivo:
Aprender a testar endpoints sem precisar de ferramentas externas como Postman ou Insomnia.

### Ação no Navegador:
1. Abra seu navegador e acesse: **`http://127.0.0.1:8000/docs`**
2. Observe a documentação interativa gerada automaticamente.
3. Clique em `GET /hello` $\rightarrow$ **Try it out** $\rightarrow$ **Execute**.
4. Veja a resposta com status `200 OK` e o JSON retornado.

<div class="box">
⭐ <b>Dica:</b> Experimente também acessar <code>http://127.0.0.1:8000/redoc</code> para uma documentação técnica alternativa.
</div>

---

<!-- Slide 08: Passo 6 -->
## <span class="step-badge">Passo 06</span> Criar Lista de Pratos em Memória

### Objetivo:
Simular uma fonte de dados para praticar operações de busca e filtros.

### Ação: Adicionar em `main.py`:
```python
# Lista de itens do cardápio (temporariamente em memória)
itens = [
    {"id": 10, "nome": "Filé com Fritas", "preco": 38.50, "categoria": "Lanches", "disponivel": True},
    {"id": 15, "nome": "Pão c/ Carne de Sol", "preco": 22.00, "categoria": "Lanches", "disponivel": True},
    {"id": 25, "nome": "Pastel de Queijo Coalho", "preco": 18.00, "categoria": "Lanches", "disponivel": False},
    {"id": 30, "nome": "Suco de Caju Fresco", "preco": 8.50, "categoria": "Bebidas", "disponivel": True},
]
```

---

<!-- Slide 09: Passo 7 -->
## <span class="step-badge">Passo 07</span> Criar Rota com Path Parameter (`{item_id}`)

### Objetivo:
Permitir que o cliente consulte um prato específico pelo seu ID na URL.

### Ação: Adicionar em `main.py`:
```python
@app.get("/cardapio/{item_id}")
def obter_item(item_id: int): # Type hint converte '10' da URL para o inteiro 10
    for item in itens:
        if item["id"] == item_id:
            return item
    return {"erro": "Item não encontrado"} # Ainda sem status HTTP correto!
```

### Testar no Swagger:
- Acesse `http://127.0.0.1:8000/cardapio/15` $\rightarrow$ Retorna o Pão com Carne de Sol.
- Acesse `http://127.0.0.1:8000/cardapio/texto` $\rightarrow$ O FastAPI devolve `422 Unprocessable Entity`!

---

<!-- Slide 10: Passo 8 -->
## <span class="step-badge">Passo 08</span> Aplicar Tratamento de Erro Semântico (404)

### Objetivo:
Lançar `HTTPException` com o status correto quando o prato não existir.

### Ação: Atualizar em `main.py`:
```python
from fastapi import FastAPI, HTTPException, status

@app.get("/cardapio/{item_id}")
def obter_item(item_id: int):
    for item in itens:
        if item["id"] == item_id:
            return item

    # Semântica correta do protocolo HTTP
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Prato não localizado com id={item_id}."
    )
```

<div class="box">
💡 <b>Regra:</b> Nunca devolva status 200 quando uma busca falhar. Use sempre <b>404 Not Found</b>!
</div>

---

<!-- Slide 11: Passo 9 -->
## <span class="step-badge">Passo 09</span> Criar Rota com Query Parameters Opcionais

### Objetivo:
Permitir filtrar o cardápio por categoria e por disponibilidade na mesma rota.

### Ação: Adicionar em `main.py`:
```python
@app.get("/cardapio/")
def listar_cardapio(categoria: str | None = None, disponivel: bool | None = None):
    resultado = itens

    if categoria:
        resultado = [i for i in resultado if i["categoria"] == categoria]

    if disponivel is not None:
        resultado = [i for i in resultado if i["disponivel"] == disponivel]

    return resultado
```

### Testes práticos no navegador:
- `http://127.0.0.1:8000/cardapio/` (Todos)
- `http://127.0.0.1:8000/cardapio/?categoria=Bebidas` (Apenas Bebidas)
- `http://127.0.0.1:8000/cardapio/?disponivel=true` (Apenas Pratos Prontos)

---

<!-- Slide 12: Passo 10 -->
## <span class="step-badge">Passo 10</span> Versionar no Git com `.gitignore` Adequado

### Objetivo:
Garantir que ambientes virtuais e arquivos temporários não poluam o repositório.

### Ação: Criar o arquivo `.gitignore`:
```gitignore
.venv/
__pycache__/
*.py[cod]
*.db
*.sqlite
.env
.DS_Store
```

### Comandos no Terminal:
```bash
git init
git add .gitignore main.py
git commit -m "feat: prototipo inicial da api com rotas basicas"
```

---

<!-- Slide 13: Passo 11 -->
## <span class="step-badge">Passo 11</span> Instalar o SQLModel

### Objetivo:
Adicionar a biblioteca que unifica validação de dados (Pydantic) e banco de dados (SQLAlchemy).

### Comando no Terminal:
```bash
pip install "sqlmodel>=0.0.22"
```

<div class="box">
💡 <b>Vantagem Didática:</b> O SQLModel substitui a necessidade de aprender duas sintaxes separadas. Usamos apenas classes Python comuns com type hints!
</div>

---

<!-- Slide 14: Passo 12 -->
## <span class="step-badge">Passo 12</span> Criar a Estrutura Modular `app/`

### Objetivo:
Organizar o projeto em módulos profissionais para separar regras de negócio de endpoints.

### Comandos no Terminal:
```bash
mkdir -p app/routers
touch app/__init__.py
touch app/routers/__init__.py
touch app/models.py
touch app/database.py
```

### Como fica a árvore de arquivos:
```text
cardapio-api/
├── app/
│   ├── __init__.py
│   ├── database.py     # Conexão com SQLite / Postgres
│   ├── models.py       # Classes SQLModel
│   └── routers/
│       └── __init__.py
```

---

<!-- Slide 15: Passo 13 -->
## <span class="step-badge">Passo 13</span> Definir a Classe Base no `app/models.py`

### Objetivo:
Centralizar os atributos comuns que pertencem tanto ao banco quanto às validações da API.

### Ação: Editar `app/models.py`:
```python
from sqlmodel import SQLModel, Field

class ItemCardapioBase(SQLModel):
    nome: str = Field(min_length=2, max_length=100, description="Nome do prato")
    descricao: str | None = Field(default=None, max_length=255)
    preco: float = Field(gt=0, description="Preço deve ser maior que zero")
    categoria: str = Field(default="Lanches")
    disponivel: bool = Field(default=True)
```

<div class="box">
⭐ <b>Validações Automáticas:</b> <code>min_length=2</code> impede nomes vazios e <code>gt=0</code> impede preços negativos ou zerados!
</div>

---

<!-- Slide 16: Passo 14 -->
## <span class="step-badge">Passo 14</span> Criar o Modelo da Tabela Relacional

### Objetivo:
Dizer ao SQLModel para transformar a classe Python em uma tabela real no banco de dados.

### Ação: Adicionar em `app/models.py`:
```python
# table=True cria a tabela itens_cardapio no banco
class ItemCardapio(ItemCardapioBase, table=True):
    __tablename__ = "itens_cardapio"

    # Chave primária autoincrementada gerenciada pelo banco
    id: int | None = Field(default=None, primary_key=True)
```

<div class="box">
💡 <b>Atenção:</b> O <code>id</code> é opcional no Python (<code>int | None = None</code>) porque antes de salvar no banco ele ainda não existe!
</div>

---

<!-- Slide 17: Passo 15 -->
## <span class="step-badge">Passo 15</span> Criar os Schemas Create, Update e Response

### Objetivo:
Controlar exatamente o que o cliente pode enviar no cadastro e na edição de pratos.

### Ação: Adicionar no final de `app/models.py`:
```python
# Usado no POST: o cliente NUNCA envia id
class ItemCardapioCreate(ItemCardapioBase):
    pass

# Usado no PUT: permite atualizar campos específicos
class ItemCardapioUpdate(SQLModel):
    nome: str | None = None
    descricao: str | None = None
    preco: float | None = None
    categoria: str | None = None
    disponivel: bool | None = None

# Usado nas respostas da API: garante que o id sempre retorne
class ItemCardapioResponse(ItemCardapioBase):
    id: int
```

---

<!-- Slide 18: Passo 16 -->
## <span class="step-badge">Passo 16</span> Configurar o Banco em `app/database.py`

### Objetivo:
Configurar a conexão com o banco de dados e habilitar DDL automático.

### Ação: Criar `app/database.py`:
```python
from sqlmodel import SQLModel, create_engine, Session

ARQUIVO_BANCO = "cardapio.db"
DATABASE_URL = f"sqlite:///{ARQUIVO_BANCO}"

engine = create_engine(
    DATABASE_URL, 
    echo=False, 
    connect_args={"check_same_thread": False} # Obrigatório no SQLite
)

def criar_tabelas():
    """Gera o CREATE TABLE automaticamente no banco"""
    SQLModel.metadata.create_all(engine)
```

---

<!-- Slide 19: Passo 17 -->
## <span class="step-badge">Passo 17</span> Criar a Injeção da Sessão (`obter_sessao`)

### Objetivo:
Garantir que cada requisição HTTP abra uma sessão e a feche automaticamente ao terminar.

### Ação: Adicionar em `app/database.py`:
```python
def obter_sessao():
    """
    CONCEITO: Função geradora com yield.
    Entrega uma sessão aberta para o endpoint e fecha com segurança ao final.
    """
    with Session(engine) as sessao:
        yield sessao
```

<div class="box">
💡 <b>Sem Vazamentos:</b> Mesmo se sua rota sofrer uma exceção, o bloco <code>with</code> garante que a conexão seja devolvida ao pool sem travar o banco!
</div>

---

<!-- Slide 20: Passo 18 -->
## <span class="step-badge">Passo 18</span> Criar o Router em `app/routers/cardapio.py`

### Objetivo:
Isolar todas as rotas do recurso `/cardapio` usando `APIRouter`.

### Ação: Criar `app/routers/cardapio.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import obter_sessao
from app.models import (
    ItemCardapio, ItemCardapioCreate, 
    ItemCardapioUpdate, ItemCardapioResponse
)

router = APIRouter(prefix="/cardapio", tags=["Cardápio"])
```

<div class="box">
⭐ <b>Modularização:</b> O prefixo <code>/cardapio</code> não precisa mais ser repetido em cada decorador de rota!
</div>

---

<!-- Slide 21: Passo 19 -->
## <span class="step-badge">Passo 19</span> Implementar POST e GET do Banco

### Objetivo:
Persistir e consultar pratos diretamente no banco relacional.

### Ação: Adicionar em `app/routers/cardapio.py`:
```python
@router.post("/", response_model=ItemCardapioResponse, status_code=status.HTTP_201_CREATED)
def criar_item(dados: ItemCardapioCreate, sessao: Session = Depends(obter_sessao)):
    novo_item = ItemCardapio.model_validate(dados)
    sessao.add(novo_item)
    sessao.commit()
    sessao.refresh(novo_item)
    return novo_item

@router.get("/", response_model=list[ItemCardapioResponse])
def listar_cardapio(sessao: Session = Depends(obter_sessao)):
    return sessao.exec(select(ItemCardapio).order_by(ItemCardapio.id)).all()
```

---

<!-- Slide 22: Passo 20 -->
## <span class="step-badge">Passo 20</span> Implementar PUT, PATCH e DELETE

### Ação: Adicionar em `app/routers/cardapio.py`:
```python
@router.put("/{item_id}", response_model=ItemCardapioResponse)
def atualizar_item(item_id: int, dados: ItemCardapioUpdate, sessao: Session = Depends(obter_sessao)):
    item = sessao.get(ItemCardapio, item_id)
    if not item: raise HTTPException(404, "Prato não localizado.")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(item, campo, valor)
    sessao.commit()
    sessao.refresh(item)
    return item

@router.patch("/{item_id}/disponibilidade", response_model=ItemCardapioResponse)
def alternar_status(item_id: int, sessao: Session = Depends(obter_sessao)):
    item = sessao.get(ItemCardapio, item_id)
    if not item: raise HTTPException(404, "Prato não localizado.")
    item.disponivel = not item.disponivel
    sessao.commit()
    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_item(item_id: int, sessao: Session = Depends(obter_sessao)):
    item = sessao.get(ItemCardapio, item_id)
    if not item: raise HTTPException(404, "Prato não localizado.")
    sessao.delete(item)
    sessao.commit()
    return None
```

---

<!-- Slide 23: Passo 21 -->
## <span class="step-badge">Passo 21</span> Configurar `app/main.py`, CORS e Seed

### Objetivo:
Juntar as rotas, liberar o CORS para o frontend e popular dados de exemplo automaticamente.

### Ação: Criar `app/main.py`:
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, criar_tabelas
from app.routers import cardapio

@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    criar_tabelas() # Garante existência das tabelas ao ligar
    yield

app = FastAPI(title="Cardápio Digital - IFPI TDS", lifespan=ciclo_de_vida)

# Habilita comunicação com qualquer frontend
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

app.include_router(cardapio.router)
```

---

<!-- Slide 24: Passo 22 -->
## <span class="step-badge">Passo 22</span> Instalar Bibliotecas de Produção e Banco

### Objetivo:
Instalar o gerenciador de migrações (Alembic), o driver PostgreSQL e o Pydantic Settings.

### Comando no Terminal:
```bash
pip install alembic psycopg2-binary pydantic-settings
```

### Registrar no `requirements.txt`:
```bash
pip freeze > requirements.txt
```

<div class="box">
💡 <b>Dica:</b> O arquivo <code>requirements.txt</code> é a lista oficial de compras que o servidor da nuvem (Render/Docker) usará para montar sua aplicação.
</div>

---

<!-- Slide 25: Passo 23 -->
## <span class="step-badge">Passo 23</span> Criar Módulo de Configuração (`app/config.py`)

### Objetivo:
Ler variáveis de ambiente do arquivo `.env` de forma tipada e segura (*Twelve-Factor App*).

### Ação: Criar `app/config.py`:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./cardapio.db" # Padrão seguro
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "Cardápio Digital - IFPI TDS 386"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
```

---

<!-- Slide 26: Passo 24 -->
## <span class="step-badge">Passo 24</span> Criar `.env.example` e `.env` Local

### Objetivo:
Documentar as opções de conexão para a turma sem expor senhas no Git.

### 1. Criar o template `.env.example`:
```env
# Opção 1: PostgreSQL Local
DATABASE_URL=postgresql://<usuario>:<senha>@localhost:5432/cardapio_db

# Opção 2: Supabase na Nuvem
# DATABASE_URL=postgresql://postgres.<ref>:<senha>@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?sslmode=require

# Opção 3: SQLite Local
# DATABASE_URL=sqlite:///./cardapio.db
```

### 2. Copiar para o `.env` local:
```bash
cp .env.example .env
```

---

<!-- Slide 27: Passo 25 -->
## <span class="step-badge">Passo 25</span> Inicializar o Alembic para Migrações

### Objetivo:
Criar a infraestrutura de controle de versão do banco de dados.

### Comando no Terminal:
```bash
alembic init migrations
```

### O que este comando gerou no seu projeto?
- **`alembic.ini`:** Arquivo mestre de configuração da ferramenta CLI.
- **`migrations/env.py`:** Script Python executado a cada comando do Alembic.
- **`migrations/versions/`:** Pasta onde ficarão os arquivos de migração versionados.

---

<!-- Slide 28: Passo 26 -->
## <span class="step-badge">Passo 26</span> Conectar o Alembic ao SQLModel e `.env`

### Objetivo:
Fazer o Alembic ler a `DATABASE_URL` do `.env` e inspecionar automaticamente os modelos.

### Ação: Ajustar em `migrations/env.py`:
```python
from sqlmodel import SQLModel
from app.config import settings
from app.database import engine
from app.models import ItemCardapio # Registra os modelos

target_metadata = SQLModel.metadata # Avisa o Alembic quais tabelas mapear

def run_migrations_online():
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True # Habilita migrações uniformes em SQLite e Postgres!
        )
        with context.begin_transaction():
            context.run_migrations()
```

---

<!-- Slide 29: Passo 27 -->
## <span class="step-badge">Passo 27</span> Criar e Aplicar a Primeira Migração

### Objetivo:
Gerar o script SQL de criação da tabela inicial e executá-lo no banco configurado.

### Comandos no Terminal:
```bash
# 1. Gerar o script de migração inicial comparando modelos com o banco
alembic revision --autogenerate -m "criacao_inicial_itens_cardapio"

# 2. Aplicar a migração no banco de dados
alembic upgrade head
```

### Inspecionar o resultado:
Abra o banco e observe a tabela `itens_cardapio` criada junto com a tabela interna `alembic_version`!

---

<!-- Slide 30: Passo 28 -->
## <span class="step-badge">Passo 28</span> Praticar Evolução de Esquema (Novo Campo)

### Cenário Real:
O restaurante precisa agora informar o **tempo de preparo em minutos** de cada prato!

### 1. Adicionar o atributo em `app/models.py`:
```python
class ItemCardapioBase(SQLModel):
    ...
    tempo_preparo_minutos: int | None = Field(default=None, ge=1)
```

### 2. Gerar e rodar a nova migração:
```bash
alembic revision --autogenerate -m "adiciona_tempo_preparo"
alembic upgrade head
```

<div class="box">
⭐ <b>Sem Perda de Dados:</b> O Alembic executa <code>ALTER TABLE ADD COLUMN</code> mantendo todos os pratos já salvos intactos!
</div>

---

<!-- Slide 31: Passo 29 -->
## <span class="step-badge">Passo 29</span> Praticar Rollback de Migração

### Cenário de Teste:
Você aplicou uma alteração incorreta e precisa desfazer rapidamente em produção.

### Comandos no Terminal:
```bash
# 1. Desfazer a última migração aplicada (Volta para a versão anterior)
alembic downgrade -1

# 2. Verificar o status atual do banco
alembic current

# 3. Re-aplicar para ficar na versão mais recente
alembic upgrade head
```

<div class="box">
💡 <b>Segurança Máxima:</b> Esse comando demonstra aos alunos a tranquilidade de poder desfazer alterações de banco sem precisar de backups manuais arriscados!
</div>

---

<!-- Slide 32: Passo 30 -->
## <span class="step-badge">Passo 30</span> Criar o HTML Base do Frontend (`frontend/`)

### Objetivo:
Construir uma interface moderna e responsiva com TailwindCSS via CDN (sem build tools).

### Ação: Criar `frontend/index.html`:
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Cardápio Digital - IFPI TDS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
</head>
<body class="bg-slate-50 text-slate-800">
    <!-- Navbar, Painel de Estatísticas, Filtros de Categoria, Grid de Cards e Modal -->
    <main class="max-w-6xl mx-auto p-6">
        <section id="grid-cardapio" class="grid grid-cols-1 md:grid-cols-3 gap-6"></section>
    </main>
    <script type="module" src="app.js"></script>
</body>
</html>
```

---

<!-- Slide 33: Passo 31 -->
## <span class="step-badge">Passo 31</span> Criar o Estado Centralizado (`frontend/state.js`)

### Objetivo:
Implementar o padrão Observer (Pub-Sub) com uma única fonte de verdade.

### Ação: Criar `frontend/state.js`:
```javascript
const state = {
    itens: [],
    categoriaAtiva: "",
    filtroDisponivel: false,
    busca: "",
    modalAberto: false,
};

const listeners = [];

export function subscribe(fn) { listeners.push(fn); }
export function notify() { listeners.forEach(fn => fn(getState())); }
export function getState() { return { ...state, itens: [...state.itens] }; }

export function setItens(novosItens) { state.itens = novosItens; notify(); }
export function setCategoria(cat) { state.categoriaAtiva = cat; notify(); }
```

---

<!-- Slide 34: Passo 32 -->
## <span class="step-badge">Passo 32</span> Criar a Camada de Rede Pura (`frontend/api.js`)

### Objetivo:
Isolar todas as chamadas HTTP `fetch()` em um módulo independente da interface gráfica.

### Ação: Criar `frontend/api.js`:
```javascript
const portasDev = ["3000", "5500", "5173"];
const API_BASE_URL = portasDev.includes(window.location.port) 
    ? "http://127.0.0.1:8000" 
    : window.location.origin;

export async function listarCardapio() {
    const res = await fetch(`${API_BASE_URL}/cardapio/`);
    return await res.json();
}

export async function alternarDisponibilidade(id) {
    const res = await fetch(`${API_BASE_URL}/cardapio/${id}/disponibilidade`, { method: "PATCH" });
    return await res.json();
}
```

---

<!-- Slide 35: Passo 33 -->
## <span class="step-badge">Passo 33</span> Criar Renderizador e Controlador do Frontend

### 1. Em `frontend/render.js`:
Função pura que recebe `estado` e apenas injeta o HTML dos cards:
```javascript
export function renderizarApp(estado) {
    const grid = document.getElementById("grid-cardapio");
    grid.innerHTML = estado.itens.map(item => `
        <article class="p-4 bg-white rounded-xl shadow border">
            <h3 class="font-bold">${item.nome}</h3>
            <p class="text-emerald-600 font-extrabold">R$ ${item.preco.toFixed(2)}</p>
        </article>
    `).join("");
}
```

### 2. Em `frontend/app.js`:
```javascript
import { subscribe, setItens } from "./state.js";
import { listarCardapio } from "./api.js";
import { renderizarApp } from "./render.js";

subscribe(renderizarApp); // Conexão reativa!
document.addEventListener("DOMContentLoaded", async () => {
    setItens(await listarCardapio()); // Dispara a renderização inicial!
});
```

---

<!-- Slide 36: Passo 34 -->
## <span class="step-badge">Passo 34</span> Servir o Frontend pelo FastAPI

### Objetivo:
Permitir que a aplicação inteira (API + Interface) funcione em uma única porta e domínio.

### Ação: Adicionar em `app/main.py`:
```python
from fastapi.staticfiles import StaticFiles

# Monta a pasta frontend como arquivos estáticos servidos pelo Uvicorn
app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")
```

### Testar no Navegador:
Acesse: **`http://127.0.0.1:8000/frontend/`**  
Sua aplicação web já consome a API REST em tempo real!

---

<!-- Slide 37: Passo 35 -->
## <span class="step-badge">Passo 35</span> Criar Testes Automatizados com `pytest`

### Objetivo:
Garantir a integridade da aplicação antes de subir para a produção na nuvem.

### Ação: Criar `tests/test_cardapio.py`:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def cliente():
    with TestClient(app) as c: yield c

def test_status_raiz(cliente):
    resp = cliente.get("/")
    assert resp.status_code == 200

def test_listar_cardapio(cliente):
    resp = cliente.get("/cardapio/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
```

### Rodar no Terminal:
```bash
pytest -v
```

---

<!-- Slide 38: Passo 36 -->
## <span class="step-badge">Passo 36</span> Criar o `Dockerfile` de Produção

### Objetivo:
Empacotar o código, migrações e frontend em uma imagem Linux portátil e otimizada.

### Ação: Criar o arquivo `Dockerfile`:
```dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl libpq5 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY frontend/ ./frontend/
COPY migrations/ ./migrations/
COPY alembic.ini main.py ./

EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

---

<!-- Slide 39: Passo 37 -->
## <span class="step-badge">Passo 37</span> Testar a Imagem Docker Localmente

### Objetivo:
Validar se o container sobe, executa as migrações e responde requisições sem erros.

### Comandos no Terminal:
```bash
# 1. Construir a imagem Docker local
docker build -t cardapio-api .

# 2. Executar o container em segundo plano
docker run --rm -d --name cardapio_app -p 8000:8000 -e PORT=8000 cardapio-api

# 3. Testar a rota de status
curl http://localhost:8000/

# 4. Parar o container após o teste
docker stop cardapio_app
```

---

<!-- Slide 40: Passo 38 -->
## <span class="step-badge">Passo 38</span> Criar Banco Gratuito no Supabase

### Objetivo:
Provisionar um banco de dados PostgreSQL real e gerenciado na nuvem.

### Ações no Painel do Supabase ([supabase.com](https://supabase.com)):
1. Crie uma conta gratuita e clique em **New Project**.
2. Defina o nome do projeto (ex: `cardapio-ifpi`) e uma senha forte.
3. Escolha a região mais próxima (ex: `São Paulo - sa-east-1`).
4. Após o provisionamento, vá em **Project Settings $\rightarrow$ Database**.
5. Em **Connection string**, selecione **URI** e copie o endereço.
   *(Ex: `postgresql://postgres.[ref]:[sua_senha]@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?sslmode=require`)*

---

<!-- Slide 41: Passo 39 & 40 -->
## <span class="step-badge">Passo 39 & 40</span> Publicar no Render e Comemorar! 🎉

### Ações no Painel do Render ([render.com](https://render.com)):
1. Clique em **New $\rightarrow$ Web Service** e conecte seu repositório GitHub.
2. O Render detectará automaticamente o seu **Dockerfile**.
3. Em **Environment Variables**, adicione:
   - `DATABASE_URL`: Cole a Connection String do Supabase copiada no Passo 38.
   - `ENVIRONMENT`: `production`
   - `DEBUG`: `false`
4. Clique em **Create Web Service**.

### 🚀 Resultado no Ar em Produção:
- O Render compila a imagem Docker.
- O container inicia e roda: `alembic upgrade head` $\rightarrow$ tabelas criadas no Supabase!
- O Uvicorn inicializa e entrega sua aplicação completa sob HTTPS com certificado SSL grátis:
  - 🌐 **Frontend:** `https://sua-api.onrender.com/frontend/`
  - 📖 **Swagger:** `https://sua-api.onrender.com/docs`
