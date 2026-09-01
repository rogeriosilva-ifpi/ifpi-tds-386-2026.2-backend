# 🍽️ Cardápio Digital - IFPI TDS 386

Projeto didático desenvolvido para a disciplina de **Backend** (Turma TDS 386 - 2026.2, IFPI).  
Demonstra a construção de uma **API RESTful completa com FastAPI e SQLModel** integrada a um **Frontend Reativo desacoplado (Vanilla JS + Padrão Observer)**.

---

## 🎯 Conceitos Didáticos Abordados

### Backend (Python & FastAPI)
1. **SQLModel**: Sintaxe unificada para schemas de validação (Pydantic) e modelos relacionais (SQLAlchemy).
2. **SQLite**: Banco de dados relacional baseado em arquivo local (sem necessidade de configurar servidores externos).
3. **Injeção de Dependência (`Depends`)**: Gerenciamento automático do ciclo de vida das conexões com o banco.
4. **Verbos HTTP Semânticos**:
   - `GET /cardapio/`: Listagem com filtros dinâmicos via Query Parameters (`categoria`, `disponivel`, `busca`).
   - `GET /cardapio/{id}`: Consulta individual via Path Parameter com tratamento de erro `404 Not Found`.
   - `POST /cardapio/`: Cadastro com validação de payload e status `201 Created`.
   - `PUT /cardapio/{id}`: Atualização de recurso existente.
   - `PATCH /cardapio/{id}/disponibilidade`: Atualização parcial rápida (disponível / esgotado).
   - `DELETE /cardapio/{id}`: Exclusão com status `204 No Content`.
5. **CORS (Cross-Origin Resource Sharing)**: Habilitado para comunicação fluida com o frontend.

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
├── app/
│   ├── __init__.py
│   ├── database.py         # Engine SQLite e Injeção de Dependência (obter_sessao)
│   ├── models.py           # Modelos SQLModel (Tabela no SQLite e Schemas Pydantic)
│   ├── routers/
│   │   ├── __init__.py
│   │   └── cardapio.py     # Endpoints CRUD com status semânticos
│   └── main.py             # Instância FastAPI, CORS, StaticFiles e Rotas
├── frontend/
│   ├── index.html          # Interface responsiva moderna com Tailwind CSS
│   ├── state.js            # [REATIVIDADE] Estado centralizado, notify(), subscribe() e mutators
│   ├── api.js              # [REDE] Funções puras de comunicação com a API REST
│   ├── render.js           # [VIEW] Funções puras de renderização orientadas a estado
│   └── app.js              # [CONTROLLER] Ponto de entrada e vinculação de eventos do DOM
├── tests/
│   ├── __init__.py
│   └── test_cardapio.py    # Testes automatizados com TestClient
├── main.py                 # Atalho de execução para 'uvicorn main:app'
├── PLANO_DIDATICO.md       # Documento de planejamento didático original
├── PLANO_FRONTEND_REATIVO.md # Documento de planejamento da arquitetura reativa
└── requirements.txt        # Dependências do projeto
```

---

## 🚀 Como Executar

### 1. Iniciar o Backend

Ative o ambiente virtual e execute o servidor Uvicorn:

```bash
# macOS / Linux
source .venv/bin/activate

# Iniciar servidor FastAPI com recarregamento automático
uvicorn main:app --reload --port 8000
```

- **API REST:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Documentação Swagger:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Frontend Integrado:** [http://127.0.0.1:8000/frontend/](http://127.0.0.1:8000/frontend/)

---

### 2. Abrir o Frontend

Graças à montagem de arquivos estáticos no FastAPI, você pode simplesmente abrir:
👉 **[http://127.0.0.1:8000/frontend/](http://127.0.0.1:8000/frontend/)**

Caso prefira rodar um servidor frontend dedicado para demonstrar portas diferentes aos alunos:
```bash
python -m http.server 3000 --directory frontend
```
E acesse [http://localhost:3000](http://localhost:3000).

---

### 3. Executar os Testes Automatizados

Para rodar a suíte de testes com o `pytest`:

```bash
pytest -v
```
