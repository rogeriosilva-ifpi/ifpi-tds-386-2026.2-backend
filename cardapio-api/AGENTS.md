# 🤖 AGENTS.md — Instruções para Agentes de IA e Desenvolvedores

Bem-vindo ao repositório do **Cardápio Digital (IFPI TDS 386)**.  
Este projeto segue rigorosamente a **Arquitetura Hexagonal (Ports & Adapters)** com casos de uso no padrão **CQS (Command-Query Separation)** de método único (`execute()`), otimizada para legibilidade, testabilidade e autonomia de agentes de IA.

---

## 🛠️ Stack Tecnológica Real

- **Linguagem:** Python 3.13+
- **Framework Web:** FastAPI (`>=0.115.0`)
- **Validação e Configurações:** Pydantic v2 & `pydantic-settings` (Twelve-Factor App)
- **Persistência / ORM:** SQLModel (`>=0.0.22`) sobre SQLAlchemy 2.x
- **Drivers de Banco:** Híbrido — `psycopg2-binary` (PostgreSQL / Supabase) e SQLite (desenvolvimento local e testes)
- **Migrações de Banco:** Alembic (`>=1.13.0`)
- **Servidor ASGI:** Uvicorn (`>=0.30.0`)
- **Suíte de Testes:** Pytest (`>=8.0.0`) + Starlette TestClient / HTTPX
- **Frontend Integrado:** Vanilla JavaScript desacoplado (Padrão Observer / State centralizado) servido em `/frontend/`

---

## 🏛️ Estrutura de Pastas e Fronteiras Arquiteturais

```text
app/
├── domain/                  # 1. NÚCLEO PURO (Zero dependências externas)
│   ├── cardapio.py          #    Entidade pura ItemCardapio (dataclass ou Pydantic sem vínculos ORM)
│   └── errors.py            #    Erros com atributo semântico `codigo: str`
├── application/             # 2. CASOS DE USO (CQS) & PORTAS
│   ├── ports/               #    Interfaces definidas estritamente como Protocol
│   │   └── cardapio_repository.py
│   └── use_cases/           #    1 classe por operação, único método async execute()
│       ├── listar_cardapio.py
│       ├── obter_item_cardapio.py
│       ├── criar_item_cardapio.py
│       ├── atualizar_item_cardapio.py
│       ├── alternar_disponibilidade.py
│       └── remover_item_cardapio.py
├── infrastructure/          # 3. ADAPTADORES DE SAÍDA (Tabelas, Repositórios, DB)
│   ├── database.py          #    Engine, gerenciamento de sessões
│   ├── seed.py              #    Carga inicial de pratos demonstrativos
│   └── repositories/
│       ├── sqlmodel_models.py           # Modelos de tabela DDL para o Alembic
│       └── sqlmodel_cardapio_repository.py # Implementação concreta da porta
├── api/                     # 4. ADAPTADORES DE ENTRADA (FastAPI, Schemas, Routers)
│   ├── dependencies.py      #    Injeção de dependência nativa (fastapi.Depends)
│   ├── exception_handlers.py#    Mapeamento de ErroDominio.codigo -> HTTP Status Code
│   ├── schemas/             #    Pydantic Schemas de entrada e saída (DTOs da API)
│   │   └── cardapio_schemas.py
│   ├── controllers/         #    Controllers assíncronos desacoplados
│   │   └── cardapio_controller.py
│   └── routers/             #    APIRouters finos
│       ├── cardapio_router.py
│       ├── auth_router.py
│       └── clientes_router.py
└── main.py                  # Ponto de entrada FastAPI, middlewares, CORS e lifespan
```

---

## ⚡ Comandos Essenciais do Projeto

Execute sempre com o ambiente virtual ativado (`source .venv/bin/activate`):

### 1. Executar a Aplicação Localmente
```bash
uvicorn main:app --reload --port 8000
```
- API REST: `http://127.0.0.1:8000`
- Swagger Docs: `http://127.0.0.1:8000/docs`
- Frontend Integrado: `http://127.0.0.1:8000/frontend/`

### 2. Suíte de Testes
Os testes utilizam fixture SQLite em memória com isolamento total de transações:
```bash
# Executar todos os testes
pytest -v

# Executar apenas testes de uma camada
pytest tests/test_domain.py -v
pytest tests/test_use_cases.py -v
pytest tests/test_cardapio_api.py -v
```

### 3. Verificação de Tipos e Lint
```bash
# Verificação estática de tipos
mypy app

# Verificação de estilo e padrões de código
ruff check app tests

# Formatação automática de código
ruff format app tests
```

### 4. Gate de Qualidade Obrigatório
Antes de submeter qualquer modificação, execute o gate completo. Todo agente deve assegurar que este comando termine verde:
```bash
ruff check app tests && mypy app && pytest -v
```

### 5. Migrações de Banco de Dados (Alembic)
As tabelas vivem em `app/infrastructure/repositories/sqlmodel_models.py` e são inspecionadas pelo `migrations/env.py`:
```bash
# Aplicar migrações pendentes
alembic upgrade head

# Gerar nova migração após alterar modelos de banco
alembic revision --autogenerate -m "descricao_da_mudanca"

# Verificar consistência do modelo com o banco
alembic check
```

---

## 📌 Convenções que Divergem do Padrão Python

Ao implementar ou modificar código neste repositório, obedeça às seguintes convenções obrigatórias:

### 1. Casos de Uso como Classe com Método Único `async def execute(...)`
- **Regra:** Nunca crie "God Services" com múltiplos métodos (`CardapioService.criar()`, `CardapioService.listar()`).
- **Padrão:** Cada intenção do usuário ou sistema é uma classe isolada em `app/application/use_cases/` que possui **apenas** o construtor `__init__` e o método `async def execute(self, ...)`.
- **Exemplo:**
  ```python
  class AlternarDisponibilidadeUseCase:
      def __init__(self, repository: CardapioRepository) -> None:
          self.repository = repository

      async def execute(self, item_id: int) -> ItemCardapio:
          item = await self.repository.obter_por_id(item_id)
          if not item:
              raise ItemNaoEncontradoError(item_id)
          item.alternar_disponibilidade()
          return await self.repository.salvar(item)
  ```

### 2. Erros de Domínio com `codigo` Semântico
- **Regra:** O domínio **nunca** importa `HTTPException` nem define status codes HTTP.
- **Padrão:** Todas as exceções de domínio herdam de `ErroDominio` e definem um `codigo: str` em UPPER_SNAKE_CASE.
- **Exemplo:**
  ```python
  class ErroDominio(Exception):
      def __init__(self, mensagem: str, codigo: str) -> None:
          super().__init__(mensagem)
          self.mensagem = mensagem
          self.codigo = codigo

  class ItemNaoEncontradoError(ErroDominio):
      def __init__(self, item_id: int) -> None:
          super().__init__(
              mensagem=f"Item não localizado com id={item_id}.",
              codigo="ITEM_NAO_ENCONTRADO"
          )
  ```

### 3. Mapeamento Global de Erros sem Cadeia de `isinstance`
- **Regra:** Proibido encadear `if isinstance(e, ErroX): ... elif isinstance(e, ErroY): ...`.
- **Padrão:** O arquivo `app/api/exception_handlers.py` mantém um dicionário estático `MAPA_ERRO_STATUS: dict[str, int]` mapeando o `codigo` da exceção para o status HTTP correspondente.
- **Formato da Resposta:** O payload JSON retornado deve sempre incluir a chave `detail` para compatibilidade estrita com o frontend:
  ```python
  return JSONResponse(
      status_code=status_code,
      content={"detail": exc.mensagem, "codigo": exc.codigo}
  )
  ```

### 4. Injeção de Dependências Exclusiva via `fastapi.Depends`
- **Regra:** Não utilize bibliotecas de injeção como `dependency_injector` ou containers reflexivos complexos.
- **Padrão:** A injeção é montada em `app/api/dependencies.py` usando geradores e funções nativas do FastAPI:
  ```python
  def obter_cardapio_repository(session: Session = Depends(obter_sessao)) -> CardapioRepository:
      return SQLModelCardapioRepository(session)

  def obter_criar_item_use_case(
      repo: CardapioRepository = Depends(obter_cardapio_repository)
  ) -> CriarItemCardapioUseCase:
      return CriarItemCardapioUseCase(repository=repo)
  ```

### 5. Contrato Estrito com o Frontend Reativo
- O frontend (`frontend/api.js`) consome os endpoints sob o prefixo `/cardapio/`.
- Qualquer mudança de campos em `ItemCardapioResponse` (`id`, `nome`, `descricao`, `preco`, `categoria`, `disponivel`, `tempo_preparo_minutos`) quebra a tela de pedidos.
- Erros capturados pelo frontend dependem explicitamente da propriedade `erroJson.detail`.
