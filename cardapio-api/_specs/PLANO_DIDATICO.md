# Plano de Implementação Didática: Cardápio API (FastAPI + SQLModel + SQLite + Frontend)

## Visão Geral do Projeto Didático
O objetivo é transformar o protótipo inicial do `cardapio-api` em uma aplicação didática completa, estruturada e profissional para o curso Técnico em Desenvolvimento de Sistemas (IFPI TDS 386 - 2026.2).

### Por que SQLModel em vez de SQLAlchemy direto?
**SQLModel** (criado por Sebastián Ramírez, autor do FastAPI) foi desenhado especificamente para resolver a duplicação entre **modelos ORM** e **schemas Pydantic**:
1. **Sintaxe Unificada:** Os alunos usam apenas *type hints* padrão do Python (`str`, `float`, `bool`), sem precisar aprender duas linguagens diferentes (`Column(String)` do SQLAlchemy vs `str` do Pydantic).
2. **Menos Boilerplate:** A mesma classe base serve para validação na API e mapeamento das tabelas no SQLite.
3. **Didática Imbatível:** Reduz a sobrecarga cognitiva e foca no que realmente importa: métodos HTTP, persistência e consumo de dados.

---

## User Review Required

> [!IMPORTANT]
> **Adição de `sqlmodel`**:
> A dependência `sqlmodel` (que já instala o SQLAlchemy 2.0 por baixo dos panos) será instalada no ambiente virtual e fixada no `requirements.txt`.

> [!NOTE]
> **Comentários Conceituais**:
> O código incluirá blocos claros de destaque (ex: `# --- CONCEITO: SQLModel (Tabela + Validação) ---`, `# --- CONCEITO: Injeção de Dependência (Session) ---`), ideais para projeção em sala de aula, sem sobrecarregar linhas triviais.

---

## Estrutura de Diretórios Proposta

```text
cardapio-api/
├── .gitignore
├── requirements.txt            # Dependências (fastapi, uvicorn, sqlmodel, pytest, httpx)
├── PLANO_DIDATICO.md           # Cópia deste plano visível no editor
├── app/
│   ├── __init__.py
│   ├── database.py             # Engine SQLite, criação de tabelas e injeção de Sessão
│   ├── models.py               # Classes SQLModel (Tabela no SQLite e Schemas de Entrada/Saída)
│   ├── routers/
│   │   ├── __init__.py
│   │   └── cardapio.py         # Endpoints RESTful (GET, POST, PUT, PATCH, DELETE)
│   └── main.py                 # Instância FastAPI, CORS, Carga Inicial (Seed) e Rotas
├── frontend/
│   ├── index.html              # Interface moderna com Tailwind (Cards, Filtros, Modal)
│   └── app.js                  # Lógica de consumo da API (Fetch API comentado)
└── tests/
    ├── __init__.py
    └── test_cardapio.py        # Testes com TestClient para demonstração de garantia de qualidade
```

---

## Proposed Changes

---

### Componente 1: Dependências & Banco de Dados

#### [NEW] `requirements.txt`
```text
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
sqlmodel>=0.0.22
httpx>=0.27.0
pytest>=8.0.0
```

#### [NEW] `app/database.py`
Gerencia a conexão SQLite e fornece a sessão do banco para os endpoints via injeção de dependência:

```python
from sqlmodel import SQLModel, create_engine, Session

# Nome do arquivo de banco local
ARQUIVO_BANCO = "cardapio.db"
DATABASE_URL = f"sqlite:///{ARQUIVO_BANCO}"

# connect_args={"check_same_thread": False} é necessário no SQLite com FastAPI
engine = create_engine(
    DATABASE_URL, 
    echo=False, 
    connect_args={"check_same_thread": False}
)

def criar_tabelas():
    """--- CONCEITO: DDL Automático via SQLModel ---"""
    SQLModel.metadata.create_all(engine)

def obter_sessao():
    """--- CONCEITO: Injeção de Dependência (Session Lifecycle) ---"""
    with Session(engine) as sessao:
        yield sessao
```

---

### Componente 2: Modelos Didáticos com SQLModel

#### [NEW] `app/models.py`
Demonstra herança orientada a objetos para reaproveitamento inteligente de campos:

```python
from sqlmodel import SQLModel, Field

# --- CONCEITO: Classe Base com campos comuns ---
class ItemCardapioBase(SQLModel):
    nome: str = Field(min_length=2, max_length=100, description="Nome do prato ou bebida")
    descricao: str | None = Field(default=None, max_length=255, description="Descrição detalhada")
    preco: float = Field(gt=0, description="Preço em reais (deve ser maior que zero)")
    categoria: str = Field(default="Lanches", description="Lanches, Bebidas ou Sobremesas")
    disponivel: bool = Field(default=True, description="Indica se o item está disponível")

# --- CONCEITO: Tabela no Banco de Dados (table=True) ---
class ItemCardapio(ItemCardapioBase, table=True):
    __tablename__ = "itens_cardapio"
    id: int | None = Field(default=None, primary_key=True)

# --- CONCEITO: Schemas para Entrada e Saída (Validação de API) ---
class ItemCardapioCreate(ItemCardapioBase):
    """Usado no POST: os dados que o cliente envia para cadastrar."""
    pass

class ItemCardapioUpdate(SQLModel):
    """Usado no PUT: permite atualizar todos ou parte dos campos."""
    nome: str
    descricao: str | None = None
    preco: float
    categoria: str
    disponivel: bool

class ItemCardapioResponse(ItemCardapioBase):
    """Usado nas respostas: garante que o ID seja sempre retornado."""
    id: int
```

---

### Componente 3: Endpoints RESTful

#### [NEW] `app/routers/cardapio.py`
Endpoints com comentários conceituais e boas práticas HTTP:

- `GET /cardapio`: Lista itens com filtros opcionais (`categoria`, `disponivel`, `busca`).
- `GET /cardapio/{item_id}`: Busca individual por ID com tratamento `404 Not Found`.
- `POST /cardapio`: Criação de item com status semântico `201 Created`.
- `PUT /cardapio/{item_id}`: Atualização completa.
- `PATCH /cardapio/{item_id}/disponibilidade`: Atualização parcial rápida (alternar status).
- `DELETE /cardapio/{item_id}`: Exclusão com status semântico `204 No Content`.

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import obter_sessao
from app.models import ItemCardapio, ItemCardapioCreate, ItemCardapioUpdate, ItemCardapioResponse

router = APIRouter(prefix="/cardapio", tags=["Cardápio"])

@router.get("/", response_model=list[ItemCardapioResponse])
def listar_cardapio(
    categoria: str | None = None,
    disponivel: bool | None = None,
    busca: str | None = None,
    sessao: Session = Depends(obter_sessao)
):
    """--- CONCEITO: Query Parameters e Filtros Dinâmicos ---"""
    query = select(ItemCardapio)
    if categoria:
        query = query.where(ItemCardapio.categoria == categoria)
    if disponivel is not None:
        query = query.where(ItemCardapio.disponivel == disponivel)
    if busca:
        query = query.where(ItemCardapio.nome.contains(busca))
    return sessao.exec(query).all()
```

---

### Componente 4: Inicialização, CORS e Carga Inicial (Seed)

#### [MODIFY] `app/main.py`
- Instância do FastAPI com título e descrição didática.
- Middleware de CORS configurado para permitir requisições de qualquer origem (inclusive arquivos locais `file://` e servidores de desenvolvimento do frontend).
- **Lifespan / Carga Inicial (Seed):** Se a tabela estiver vazia na primeira inicialização, insere automaticamente 5 itens variados (Filé com Fritas, Pão com Carne de Sol, Suco de Caju, etc.), para que os alunos já vejam dados na tela de primeira.

---

### Componente 5: Frontend Didático (Sem build tools)

#### [NEW] `frontend/index.html`
- Layout moderno e responsivo com TailwindCSS via CDN.
- Navbar com logo do IFPI TDS e estatísticas rápidas.
- Barra de filtros: Campo de busca interativo + botões de categoria ("Todos", "Lanches", "Bebidas", "Sobremesas") + checkbox "Apenas Disponíveis".
- Grid de cards elegantes:
  - Título do prato, descrição e badge de categoria.
  - Preço formatado em Real (`R$ 15,00`).
  - Badge de status (`Disponível` em verde / `Esgotado` em vermelho).
  - Botão de alternar disponibilidade instantânea.
  - Botão de editar e excluir.
- Modal universal: Serve tanto para "+ Novo Item" quanto para "Editar Item".

#### [NEW] `frontend/app.js`
- Código JavaScript didático, organizado em funções assíncronas com comentários conceituais:
  - `carregarItens()`: Exemplo prático de `fetch()` com `GET`.
  - `salvarItem()`: Exemplo de `fetch()` com `POST` ou `PUT` e envio de cabeçalho `application/json`.
  - `alternarDisponibilidade()`: Exemplo de `fetch()` com `PATCH`.
  - `excluirItem()`: Exemplo de `fetch()` com `DELETE`.

---

### Componente 6: Testes Automatizados Didáticos

#### [NEW] `tests/test_cardapio.py`
- Usa o `TestClient` do FastAPI para validar:
  1. `test_listar_cardapio`: Valida status 200 e estrutura de lista.
  2. `test_criar_item`: Valida status 201 e retorno do ID gerado.
  3. `test_item_nao_encontrado`: Valida status 404 para ID inexistente.

---

## Plano de Verificação

### 1. Instalação e Testes
```bash
.venv/bin/pip install sqlmodel pytest httpx
.venv/bin/pytest tests/
```

### 2. Execução da API
```bash
.venv/bin/uvicorn app.main:app --reload --port 8000
```
- Acessar `http://127.0.0.1:8000/docs` e validar os Schemas e rotas gerados no Swagger.
- Verificar a criação automática de `cardapio.db` e a injeção dos dados de exemplo.

### 3. Teste Integrado com Frontend
- Abrir [`frontend/index.html`](file:///Users/rogerio410/ifpi-tds-386-2026.2-backend/cardapio-api/frontend/index.html) no navegador.
- Realizar o ciclo completo: Criar um item, filtrar por categoria, alternar disponibilidade, editar preço e excluir.
