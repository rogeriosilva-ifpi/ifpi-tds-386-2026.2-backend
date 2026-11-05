# 🍽️ Cardápio Digital - IFPI TDS 386

Projeto didático desenvolvido para a disciplina de **Backend** (Turma TDS 386 - 2026.2, IFPI).  
Demonstra a construção de uma **API RESTful profissional com FastAPI, SQLModel e PostgreSQL/Supabase**, versionamento de banco com **Alembic**, configurações seguras via **.env (Twelve-Factor)** e um **Frontend Reativo desacoplado (Vanilla JS + Padrão Observer)**.

---

## 🎯 Conceitos Didáticos Abordados

### Backend (Python & FastAPI)
1. **SQLModel Modularizado**: Sintaxe unificada para schemas de validação (Pydantic) e modelos relacionais (SQLAlchemy), organizados em módulos dedicados por entidade ([`app/models/item_cardapio.py`](file:///Users/rogerio410/ifpi-tds-386-2026.2-backend/cardapio-api/app/models/item_cardapio.py) e [`app/models/cliente.py`](file:///Users/rogerio410/ifpi-tds-386-2026.2-backend/cardapio-api/app/models/cliente.py)).
2. **PostgreSQL / Supabase & SQLite Híbrido**: Suporte transparente a PostgreSQL local, Supabase na nuvem e SQLite de teste.
3. **Twelve-Factor App (Fator III: Config)**: Variáveis de ambiente lidas por `pydantic-settings` via arquivo `.env`. Zero senhas no código.
4. **Versionamento e Migrações (Alembic)**: Controle de versão do banco de dados (DDL) com migrações idempotentes para criação de tabelas (`itens_cardapio`, `clientes`) e evolução de esquema (`tempo_preparo_minutos`).
5. **Injeção de Dependência (`Depends`)**: Gerenciamento automático do ciclo de vida das sessões com o banco (`obter_sessao`).
6. **Verbos HTTP Semânticos e Operações Fundamentais (CRUD)**:
   - **Cardápio (`/cardapio`):**
     - `GET /cardapio/`: Listagem com filtros dinâmicos via Query Parameters (`categoria`, `disponivel`, `busca`, `preco_maximo`).
     - `GET /cardapio/{id}`: Consulta individual por ID com tratamento de erro `404 Not Found`.
     - `POST /cardapio/`: Cadastro com validação de payload e status `201 Created`.
     - `PUT /cardapio/{id}`: Atualização de prato ou bebida existente.
     - `PATCH /cardapio/{id}/disponibilidade`: Atualização parcial rápida (disponível / esgotado).
     - `DELETE /cardapio/{id}`: Exclusão com status `204 No Content`.
   - **Clientes (`/clientes`) — Preparado para Delivery:**
     - `GET /clientes/`: Listagem com busca textual por nome, telefone, CEP ou endereço e ordenação alfabética.
     - `GET /clientes/{id}`: Consulta de cliente por ID com retorno `404 Not Found`.
     - `POST /clientes/`: Cadastro com validação rigorosa de dados de entrega (`nome`, `endereco`, `cep`, `numero`, `telefone/WhatsApp` obrigatórios; `422` se ausentes) e status `201 Created`.
      - `PUT /clientes/{id}`: Atualização parcial de dados cadastrais.
      - `DELETE /clientes/{id}`: Exclusão de cadastro com status `204 No Content`.
      - `GET /clientes/{id}/pedidos`: Sub-recurso para listar os pedidos do cliente autenticado.
   - **Pedidos e Sub-Recursos (`/pedidos`):**
      - `POST /pedidos/`: Criação de pedido vinculado ao cliente do header `X-Cliente-Id`, com snapshot de preço e suporte a itens inline.
      - `GET /pedidos/`: Histórico resumido de pedidos do cliente autenticado.
      - `GET /pedidos/{id}`: Consulta detalhada com itens e validação de posse (`403 Forbidden` se não for o dono).
      - `PATCH /pedidos/{id}/status`: Transição de status na máquina de estados (`CRIADO` -> `CONFIRMADO` -> `EM_PREPARO` -> `PRONTO` -> `ENTREGUE` ou `CANCELADO`).
      - `DELETE /pedidos/{id}`: Cancelamento/remoção com exclusão em cascata dos itens associados.
      - **Sub-Recurso de Itens do Pedido (`/pedidos/{id}/itens`):**
        - `GET /pedidos/{id}/itens`: Listagem de itens com nome, quantidade, preço unitário e subtotal calculado.
        - `POST /pedidos/{id}/itens`: Adiciona item, congela preço do cardápio e recalcula o total do pedido.
        - `PUT /pedidos/{id}/itens/{item_id}`: Altera quantidade/observação e sincroniza o total pai.
        - `DELETE /pedidos/{id}/itens/{item_id}`: Remove item e subtrai do total pai (`204 No Content`).
7. **Identificação e Autorização por Header (`X-Cliente-Id`)**: Controle provisório de acesso e posse de recursos.
8. **Integridade Referencial e Cascade**:
   - `Pedido -> ItensPedido`: Exclusão em cascata ativada (`cascade_delete=True` e `ondelete="CASCADE"`).
   - `ItemCardapio -> ItensPedido`: Proteção contra deleção acidental de histórico de vendas.
9. **CORS (Cross-Origin Resource Sharing)**: Habilitado para comunicação fluida com aplicações frontend e mobile.

### Frontend Reativo (JavaScript Vanilla sem Frameworks)
1. **Estado Centralizado (*Single Source of Truth*)** (`state.js`): Controla todas as variáveis visuais da aplicação.
2. **Padrão Observador (*Observer / Pub-Sub*)**: `subscribe()` registra os ouvintes e `notify()` propaga as mudanças.
3. **Camada de Rede Pura** (`api.js`): Módulo focado exclusivamente em chamadas HTTP (`fetch`).
4. **Camada de Visualização Pura** (`render.js`): Projeta o estado recebido no DOM sem regras de negócio misturadas.
5. **Controlador Desacoplado** (`app.js`): Vinculação de eventos do DOM e orquestração do ciclo reativo.

---

## 📁 Estrutura do Projeto

```text
cardapio-api/
├── .env                        # [Git Ignored] Configurações e segredos locais
├── .env.example                # [Template] Exemplo sem senhas para os alunos
├── alembic.ini                 # Configuração mestre do Alembic
├── migrations/                 # Scripts versionados de migração de banco
│   ├── env.py                  # Integração com SQLModel e app.config
│   └── versions/               # Histórico de alterações do banco
│       ├── 0001_criacao_inicial_itens_cardapio.py
│       ├── 0002_adiciona_tempo_preparo.py
│       ├── 0003_cria_tabela_clientes.py
│       └── 0004_cria_tabelas_pedidos_e_itens_pedido.py
├── app/
│   ├── __init__.py
│   ├── config.py               # Leitura tipada de variáveis de ambiente (.env)
│   ├── database.py             # Engine flexível (PostgreSQL/Supabase/SQLite)
│   ├── dependencies.py         # Injeção de dependência e autenticação por Header (X-Cliente-Id)
│   ├── models/                 # Modelos SQLModel modularizados por recurso
│   │   ├── __init__.py         # Reexportação unificada de todos os modelos
│   │   ├── item_cardapio.py    # Tabela e Schemas de Itens do Cardápio
│   │   ├── cliente.py          # Tabela e Schemas de Clientes (dados de entrega)
│   │   ├── pedido.py           # Tabela, StatusPedido e Schemas de Pedidos
│   │   └── item_pedido.py      # Tabela de Itens de Pedido com Snapshot de Preço
│   ├── routers/                # Roteadores modulares da API (APIRouter)
│   │   ├── __init__.py
│   │   ├── auth.py             # Autenticação e perfil
│   │   ├── cardapio.py         # Endpoints CRUD do cardápio
│   │   ├── clientes.py         # Endpoints CRUD de clientes e sub-recurso /pedidos
│   │   └── pedidos.py          # Endpoints de pedidos e sub-recursos /itens
│   └── main.py                 # Instância FastAPI, Lifespan (Seed), CORS e StaticFiles
├── frontend/
│   ├── index.html              # Interface responsiva moderna com Tailwind CSS
│   ├── state.js                # [REATIVIDADE] Estado centralizado, notify(), subscribe()
│   ├── api.js                  # [REDE] Funções puras de comunicação com a API REST
│   ├── render.js               # [VIEW] Funções puras de renderização orientadas a estado
│   └── app.js                  # [CONTROLLER] Ponto de entrada e eventos do DOM
├── tests/
│   ├── __init__.py
│   ├── test_cardapio.py        # Testes automatizados dos endpoints do cardápio
│   ├── test_clientes.py        # Testes automatizados do CRUD e validações de clientes
│   └── test_pedidos.py         # Testes de relacionamentos, sub-recursos e autorização
├── main.py                     # Atalho de execução para 'uvicorn main:app'
├── _docs/                      # [AULAS E ESTUDOS] Materiais didáticos e roteiros
│   ├── AULA_CARDAPIO_API.md    # Apresentação completa em 36 slides didáticos
│   ├── AULA_ORM_SQLMODEL.md    # Do SQL Puro ao SQLModel Lado a Lado (30 slides)
│   └── GUIA_PASSO_A_PASSO.md   # Roteiro de laboratório passo a passo (41 slides)
├── _specs/                     # [ESPECIFICAÇÕES] Planos técnicos de evolução
│   ├── PLANO_DIDATICO.md
│   ├── PLANO_FRONTEND_REATIVO.md
│   ├── PLANO_POSTGRES_MIGRACOES.md
│   ├── PLANO_DEPLOY_RENDER_DOCKER.md
│   ├── PLANO_MATERIAL_DE_AULA.md
│   └── PLANO_SLIDES_ORM_SQLMODEL.md
└── requirements.txt            # Dependências do projeto
```

---

## 🚀 Como Executar

### 1. Configurar as Variáveis de Ambiente (.env)

Copie o template para criar seu arquivo local:
```bash
cp .env.example .env
```

Abra o arquivo `.env` e configure a `DATABASE_URL`:

- **Para PostgreSQL Local:**
  ```env
  DATABASE_URL=postgresql://<usuario>:<sua_senha>@localhost:5432/cardapio_db
  ```
  *(Crie a base antes caso ainda não exista: `createdb cardapio_db` ou no SQL: `CREATE DATABASE cardapio_db;`)*

- **Para Supabase na Nuvem:**
  ```env
  DATABASE_URL=postgresql://postgres.<project_ref>:<sua_senha>@aws-0-<region>.pooler.supabase.com:6543/postgres?sslmode=require
  ```

- **Para SQLite de Teste Local:**
  ```env
  DATABASE_URL=sqlite:///./cardapio.db
  ```

---

### 2. Executar as Migrações do Banco de Dados (Alembic)

Para aplicar todas as alterações pendentes no banco configurado (tabelas de cardápio e clientes):
```bash
alembic upgrade head
```

Outros comandos didáticos do Alembic:
- Ver histórico de migrações: `alembic history --verbose`
- Ver revisão atual aplicada: `alembic current`
- Desfazer última alteração (Rollback): `alembic downgrade -1`
- Gerar nova migração após alterar models: `alembic revision --autogenerate -m "descricao"`

---

### 3. Iniciar o Backend

```bash
uvicorn main:app --reload --port 8000
```

- **API REST:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Documentação Interativa (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Documentação Alternativa (ReDoc):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Frontend Integrado:** [http://127.0.0.1:8000/frontend/](http://127.0.0.1:8000/frontend/)

---

### 4. Executar os Testes Automatizados

Para rodar a suíte completa de testes (Cardápio e Clientes):
```bash
pytest -v
```

---

### 5. Executar com Docker (Local)

Construa e execute a imagem Docker localmente:
```bash
# 1. Construir a imagem Docker
docker build -t cardapio-api .

# 2. Executar o container apontando para seu banco (ou SQLite de teste)
docker run --rm -p 8000:8000 -e PORT=8000 -e DATABASE_URL=sqlite:///./cardapio.db cardapio-api
```
Acesse em: [http://localhost:8000/frontend/](http://localhost:8000/frontend/)

---

### 6. Publicar na Nuvem (Deploy no Render com Supabase)

1. **Obter Banco no Supabase:**
   - Crie um projeto em [supabase.com](https://supabase.com).
   - Copie a **Connection String (URI)** em **Project Settings $\rightarrow$ Database**.
2. **Criar Web Service no Render:**
   - Acesse [render.com](https://render.com) e crie um **New Web Service** apontando para o repositório.
   - O Render detecta o `Dockerfile` automaticamente.
   - Adicione as variáveis de ambiente:
     - `DATABASE_URL`: Cole a URI do Supabase (`postgresql://postgres.[ref]:[senha]@...pooler.supabase.com:6543/postgres?sslmode=require`).
     - `ENVIRONMENT`: `production`
     - `DEBUG`: `false`
3. **Pronto!**
   - O Render compila a imagem, executa `alembic upgrade head` no Supabase e disponibiliza sua aplicação online com HTTPS grátis:
     - **API:** `https://sua-api.onrender.com/`
     - **Frontend Reativo:** `https://sua-api.onrender.com/frontend/`
     - **Swagger:** `https://sua-api.onrender.com/docs`
