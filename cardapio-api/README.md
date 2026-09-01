# 🍽️ Cardápio Digital - IFPI TDS 386

Projeto didático desenvolvido para a disciplina de **Backend** (Turma TDS 386 - 2026.2, IFPI).  
Demonstra a construção de uma **API RESTful profissional com FastAPI, SQLModel e PostgreSQL/Supabase**, versionamento de banco com **Alembic**, configurações seguras via **.env (Twelve-Factor)** e um **Frontend Reativo desacoplado (Vanilla JS + Padrão Observer)**.

---

## 🎯 Conceitos Didáticos Abordados

### Backend (Python & FastAPI)
1. **SQLModel**: Sintaxe unificada para schemas de validação (Pydantic) e modelos relacionais (SQLAlchemy).
2. **PostgreSQL / Supabase & SQLite Híbrido**: Suporte transparente a PostgreSQL local, Supabase na nuvem e SQLite de teste.
3. **Twelve-Factor App (Fator III: Config)**: Variáveis de ambiente lidas por `pydantic-settings` via arquivo `.env`. Zero senhas no código.
4. **Versionamento e Migrações (Alembic)**: Controle de versão do banco de dados (DDL), criação de tabelas, adição de colunas e rollback seguro.
5. **Injeção de Dependência (`Depends`)**: Gerenciamento automático do ciclo de vida das conexões com o banco.
6. **Verbos HTTP Semânticos**:
   - `GET /cardapio/`: Listagem com filtros dinâmicos via Query Parameters (`categoria`, `disponivel`, `busca`).
   - `GET /cardapio/{id}`: Consulta individual via Path Parameter com tratamento de erro `404 Not Found`.
   - `POST /cardapio/`: Cadastro com validação de payload e status `201 Created`.
   - `PUT /cardapio/{id}`: Atualização de recurso existente.
   - `PATCH /cardapio/{id}/disponibilidade`: Atualização parcial rápida (disponível / esgotado).
   - `DELETE /cardapio/{id}`: Exclusão com status `204 No Content`.
7. **CORS (Cross-Origin Resource Sharing)**: Habilitado para comunicação fluida com o frontend.

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
│       └── 0002_adiciona_tempo_preparo.py
├── app/
│   ├── __init__.py
│   ├── config.py               # Leitura tipada de variáveis de ambiente (.env)
│   ├── database.py             # Engine flexível (PostgreSQL/Supabase/SQLite)
│   ├── models.py               # Modelos SQLModel (Tabela e Schemas Pydantic)
│   ├── routers/
│   │   ├── __init__.py
│   │   └── cardapio.py         # Endpoints CRUD com status semânticos
│   └── main.py                 # Instância FastAPI, CORS, StaticFiles e Rotas
├── frontend/
│   ├── index.html              # Interface responsiva moderna com Tailwind CSS
│   ├── state.js            # [REATIVIDADE] Estado centralizado, notify(), subscribe() e mutators
│   ├── api.js              # [REDE] Funções puras de comunicação com a API REST
│   ├── render.js           # [VIEW] Funções puras de renderização orientadas a estado
│   └── app.js              # [CONTROLLER] Ponto de entrada e vinculação de eventos do DOM
├── tests/
│   ├── __init__.py
│   └── test_cardapio.py    # Testes automatizados com TestClient
├── main.py                 # Atalho de execução para 'uvicorn main:app'
├── PLANO_DIDATICO.md       # Documento de planejamento didático original
├── PLANO_FRONTEND_REATIVO.md # Planejamento da arquitetura reativa
├── PLANO_POSTGRES_MIGRACOES.md # Planejamento do PostgreSQL, Alembic e .env
└── requirements.txt        # Dependências do projeto
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

Para aplicar todas as alterações pendentes no banco configurado:
```bash
alembic upgrade head
```

Outros comandos didáticos do Alembic:
- Ver histórico de migrações: `alembic history --verbose`
- Ver revisão atual aplicada: `alembic current`
- Desfazer última alteração (Rollback): `alembic downgrade -1`
- Gerar nova migração após alterar models.py: `alembic revision --autogenerate -m "descricao"`

---

### 3. Iniciar o Backend

```bash
uvicorn main:app --reload --port 8000
```

- **API REST:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Documentação Swagger:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Frontend Integrado:** [http://127.0.0.1:8000/frontend/](http://127.0.0.1:8000/frontend/)

---

### 4. Executar os Testes Automatizados

Para rodar a suíte de testes:
```bash
pytest -v
```
