# 🍽️ Cardápio Digital - IFPI TDS 386

Projeto didático desenvolvido para a disciplina de **Backend** (Turma TDS 386 - 2026.2, IFPI).  
Demonstra a construção de uma **API RESTful completa com FastAPI e SQLModel** integrada a um **Frontend interativo em Tailwind CSS e Fetch API**.

---

## 🎯 Conceitos Didáticos Abordados

1. **SQLModel**: Sintaxe unificada para schemas de validação (Pydantic) e modelos relacionais (SQLAlchemy).
2. **SQLite**: Banco de dados relacional baseado em arquivo local (sem necessidade de configurar servidores externos).
3. **Injeção de Dependência (`Depends`)**: Gerenciamento automático do ciclo de vida das sessões do banco de dados.
4. **Verbos HTTP Semânticos**:
   - `GET /cardapio/`: Listagem com filtros dinâmicos via Query Parameters (`categoria`, `disponivel`, `busca`).
   - `GET /cardapio/{id}`: Consulta individual via Path Parameter com tratamento de erro `404 Not Found`.
   - `POST /cardapio/`: Cadastro com validação de payload e status `201 Created`.
   - `PUT /cardapio/{id}`: Atualização de recurso existente.
   - `PATCH /cardapio/{id}/disponibilidade`: Atualização parcial rápida (disponível / esgotado).
   - `DELETE /cardapio/{id}`: Exclusão com status `204 No Content`.
5. **CORS (Cross-Origin Resource Sharing)**: Habilitado para comunicação fluida entre o navegador e a API.
6. **Frontend Didático**: Interface em HTML5 + Tailwind CSS (via CDN) consumindo a API com JavaScript assíncrono (`fetch` + `async/await`).

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
│   └── main.py             # Instância FastAPI, CORS, Carga Inicial (Seed) e Rotas
├── frontend/
│   ├── index.html          # Interface responsiva com cards, filtros e modal
│   └── app.js              # Consumo assíncrono da API (Fetch API comentado)
├── tests/
│   ├── __init__.py
│   └── test_cardapio.py    # Testes automatizados com TestClient
├── main.py                 # Atalho de execução para 'uvicorn main:app'
├── PLANO_DIDATICO.md       # Documento de planejamento didático
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

- **API no ar em:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Documentação Interativa (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Documentação Alternativa (ReDoc):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

> 💡 **Nota:** Na primeira execução, a aplicação cria o arquivo `cardapio.db` e insere automaticamente pratos típicos de exemplo (seed) caso o banco esteja vazio.

---

### 2. Abrir o Frontend

Você pode abrir o frontend de duas formas simples:

- **Opção A (Mais simples):** Dê um duplo clique no arquivo [`frontend/index.html`](file:///Users/rogerio410/ifpi-tds-386-2026.2-backend/cardapio-api/frontend/index.html) ou use a extensão *Live Server* do VS Code.
- **Opção B (Via Python):** Em outro terminal, execute:
  ```bash
  python -m http.server 3000 --directory frontend
  ```
  E acesse [http://localhost:3000](http://localhost:3000) no seu navegador.

---

### 3. Executar os Testes Automatizados

Para rodar a suíte de testes com o `pytest`:

```bash
pytest -v
```
