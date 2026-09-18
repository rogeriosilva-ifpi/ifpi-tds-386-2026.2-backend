# 📐 Plano de Refatoração para Arquitetura Hexagonal (Ports & Adapters)
**Projeto:** Cardápio Digital - IFPI TDS 386  
**Metodologia:** Arquitetura Hexagonal na Era dos Agentes (Ports & Adapters + Casos de Uso CQS com método único `execute()`)  
**Status:** Planejamento (Aguardando Aprovação Fase a Fase)

---

## 1. 🔍 Diagnóstico do Estado Atual

O diagnóstico a seguir foi obtido por inspeção direta do código-fonte e da suíte de testes do repositório.

### 1.1 Onde mora a regra de negócio hoje
Atualmente, **100% da regra de negócio está acoplada e misturada nas rotas HTTP** (`app/routers/cardapio.py`) e no evento de ciclo de vida da aplicação (`app/main.py`):
1. **Filtros e Busca Dinâmica:** Lógica de filtragem com `ilike`, composição condicional de query parameters (`categoria`, `disponivel`, `busca`, `preco_maximo`) e ordenação alfabética implementada diretamente dentro da função `listar_cardapio` em `app/routers/cardapio.py` (linhas 36-58).
2. **Alternância de Estado/Disponibilidade:** A regra de negócio de inversão de estado (`item_banco.disponivel = not item_banco.disponivel`) está implementada diretamente no handler HTTP `alternar_disponibilidade` em `app/routers/cardapio.py` (linha 159).
3. **Atualização Parcial de Dados:** Lógica de inspeção e reflexão com `dados.model_dump(exclude_unset=True)` e `setattr(item_banco, campo, valor)` está misturada com a sessão ORM dentro de `atualizar_item` em `app/routers/cardapio.py` (linhas 129-132).
4. **Verificação de Existência e Erros 404:** A verificação `if not item: raise HTTPException(...)` está duplicada e dispersa em quatro funções de rota diferentes.
5. **Carga Inicial (Seed):** A regra que verifica a existência de dados e popula 5 pratos didáticos iniciais está acoplada ao lifespan do FastAPI em `app/main.py` (linhas 24-71).

### 1.2 Framework de acesso a dados
- O projeto utiliza **SQLModel** (v0.0.42) construído sobre o **SQLAlchemy** (v2.0.52).
- As classes em `app/models.py` (`ItemCardapioBase`, `ItemCardapio`, `ItemCardapioCreate`, `ItemCardapioUpdate`, `ItemCardapioResponse`) misturam, no mesmo arquivo e na mesma hierarquia, **definição de schema DDL de banco de dados (`table=True`)** e **validação de payload de API (Pydantic)**.
- O acesso ao banco é **síncrono**, utilizando `create_engine` e `Session(engine)` via gerador `obter_sessao()` com FastAPI `Depends()`.
- O banco de dados configurado no `.env` padrão é PostgreSQL (`DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cardapio_db`), com fallback documentado para SQLite.

### 1.3 Organização das rotas hoje
- `app/routers/cardapio.py`: Contém todos os endpoints operacionais do domínio (`GET /cardapio/`, `GET /cardapio/{item_id}`, `POST /cardapio/`, `PUT /cardapio/{item_id}`, `PATCH /cardapio/{item_id}/disponibilidade`, `DELETE /cardapio/{item_id}`).
- `app/routers/clientes.py`: Contém stubs didáticos incompletos que retornam strings fixas (`['Rogério', 'Daniel Pereira']`).
- `app/routers/auth.py`: Contém stubs didáticos incompletos (`/auth/me`, `/auth/login`) sem autenticação real.
- `app/main.py`: Expõe rotas de status (`GET /`, `GET /hello`) e monta os arquivos estáticos do frontend (`app.mount("/frontend", ...)`).

### 1.4 Onde mora a validação de entrada
- Validação declarativa via Pydantic/SQLModel em `app/models.py`:
  - `nome`: `min_length=2`, `max_length=100`
  - `descricao`: `max_length=255`
  - `preco`: `gt=0`
  - `categoria`: padrão `"Lanches"`
  - `tempo_preparo_minutos`: `ge=1`
- Validação de parâmetros de consulta via `Query(...)` do FastAPI em `app/routers/cardapio.py`.

### 1.5 Tratamento de erros e status HTTP expostos
- Erros são tratados com disparo explícito de `raise HTTPException(status_code=404, detail="Item não localizado com id={item_id}.")` dentro dos handlers de rota.
- Não existem exceções de domínio nem handler global centralizado.
- Status HTTP expostos pela API:
  - `200 OK`: listagem, busca por ID, PUT, PATCH e endpoints raiz/informativos.
  - `201 Created`: criação com POST.
  - `204 No Content`: exclusão com DELETE.
  - `404 Not Found`: item não localizado (payload: `{"detail": "Item não localizado com id=..."}`).
  - `422 Unprocessable Entity`: erros de validação do Pydantic (ex: preço negativo, nome curto).
  - `500 Internal Server Error`: falhas de conexão com banco ou erros não capturados.

### 1.6 Diagnóstico da suíte de testes
- Existe apenas um arquivo de teste: `tests/test_cardapio.py` com 6 funções de teste usando `TestClient`.
- **Problema Crítico de Execução:** Ao rodar `pytest` diretamente, os testes falham imediatamente com `psycopg2.OperationalError: Connection refused` porque o arquivo `.env` aponta para PostgreSQL na porta 5432 (que não está em execução no ambiente local). Os testes só passam quando `DATABASE_URL` é explicitamente sobrescrita com SQLite.
- **Falta de Isolamento:** Os testes rodam contra o banco configurado sem teardown ou banco isolado; cada execução altera dados reais (ex: `PATCH /cardapio/1/disponibilidade` inverte a disponibilidade do item seedado; `POST` insere pratos sem limpeza).
- **Cobertura Incompleta:** Não há testes cobrindo:
  - Filtros de consulta (`categoria`, `disponivel`, `busca`, `preco_maximo`) e ordenação alfabética.
  - Erros 404 em `PUT`, `PATCH` e `DELETE` para IDs inexistentes.
  - Validação de entrada inválida (422) para preços menores ou iguais a zero, nomes inválidos ou tempos negativos.
  - Rotas de `app/main.py` (`GET /hello`), `auth.py` e `clientes.py`.

### 1.7 Pontos de acoplamento mais arriscados
1. **`app/routers/cardapio.py`:** É o coração funcional do projeto. Mistura protocolo HTTP, transação de banco de dados (`sessao.commit()`), tratamento de erro, regras de negócio e contrato com o frontend (`frontend/api.js`). Qualquer alteração na estrutura de payload quebra a interface web existente.
2. **`app/models.py`:** Acopla as migrações do Alembic (`alembic/env.py` inspeciona `SQLModel.metadata`) com a validação da API. Desacoplar a entidade de domínio sem quebrar o Alembic exige manter os metadados do banco intactos.
3. **`app/main.py`:** O lifespan executa DDL (`criar_tabelas()`) e seed inicial diretamente acoplados ao SQLModel.

---

## 2. 🏛️ Arquitetura-Alvo de Referência

A arquitetura seguirá estritamente o padrão **Ports & Adapters (Hexagonal)** com casos de uso no padrão **CQS (Command-Query Separation)** com método único assíncrono `execute()`.

### 2.1 Árvore de Pastas Final

```text
cardapio-api/
├── app/
│   ├── __init__.py
│   ├── config.py                           # Twelve-Factor config (pydantic-settings)
│   ├── domain/                             # NÚCLEO: Entidades e Erros puros
│   │   ├── __init__.py
│   │   ├── cardapio.py                     # Entidade pura ItemCardapio + regras de domínio
│   │   └── errors.py                       # Erros com `codigo` semântico (zero imports externos)
│   ├── application/                        # CASOS DE USO (CQS) & PORTAS
│   │   ├── __init__.py
│   │   ├── ports/
│   │   │   ├── __init__.py
│   │   │   └── cardapio_repository.py      # Protocol / Interface de persistência
│   │   └── use_cases/
│   │       ├── __init__.py
│   │       ├── listar_cardapio.py          # Query: ListarCardapioUseCase
│   │       ├── obter_item_cardapio.py      # Query: ObterItemCardapioUseCase
│   │       ├── criar_item_cardapio.py      # Command: CriarItemCardapioUseCase
│   │       ├── atualizar_item_cardapio.py  # Command: AtualizarItemCardapioUseCase
│   │       ├── alternar_disponibilidade.py # Command: AlternarDisponibilidadeUseCase
│   │       └── remover_item_cardapio.py    # Command: RemoverItemCardapioUseCase
│   ├── infrastructure/                     # ADAPTADORES DE SAÍDA (Bases, Tabelas, Repositórios)
│   │   ├── __init__.py
│   │   ├── database.py                     # Engine e Session lifecycle
│   │   ├── seed.py                         # Serviço de carga inicial desacoplado do lifespan
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── sqlmodel_models.py          # Tabelas ORM/SQLModel (DDL para Alembic)
│   │       └── sqlmodel_cardapio_repository.py # Implementação concreta da porta
│   └── api/                                # ADAPTADORES DE ENTRADA (FastAPI, Schemas, Routers)
│       ├── __init__.py
│       ├── dependencies.py                 # Injeção de dependência nativa (Depends)
│       ├── exception_handlers.py           # Mapeador global: `codigo` de domínio -> HTTP status
│       ├── schemas/
│       │   ├── __init__.py
│       │   └── cardapio_schemas.py         # Pydantic Schemas de entrada e saída (DTOs da API)
│       └── routers/
│           ├── __init__.py
│           ├── cardapio_router.py          # APIRouter para /cardapio (orquestra entrada e aciona use cases)
│           ├── auth_router.py              # APIRouter para /auth (legado preservado)
│           └── clientes_router.py          # APIRouter para /clientes (legado preservado)
├── tests/
│   ├── conftest.py                         # Fixtures com banco SQLite isolado em memória
│   ├── test_cardapio_api.py                # Testes de integração cobrindo endpoints e contratos
│   ├── test_domain.py                      # Testes unitários puros de domínio
│   └── test_use_cases.py                   # Testes unitários de casos de uso com repositório fake
├── migrations/                             # Alembic mantido 100% funcional
├── frontend/                               # Interface web Vanilla JS mantida 100% funcional
└── main.py                                 # Ponto de entrada raiz
```

### 2.2 Responsabilidades por Camada

#### Camada `domain/`
- **O que entra:** Entidades puras em Python (dataclasses ou Pydantic BaseModel sem vínculos com ORM/tabelas), métodos que expressam comportamentos intrínsecos da entidade (ex: `alternar_disponibilidade()`, validações de invariantes de negócio como `preco > 0`), e exceções de domínio que herdam de `ErroDominio`, contendo obrigatoriamente um atributo semântico `codigo: str` (ex: `"ITEM_NAO_ENCONTRADO"`).
- **O que NÃO entra:** Frameworks web (FastAPI, Starlette), ORMs (SQLModel, SQLAlchemy), chamadas de I/O, bancos de dados, injeção de dependência ou bibliotecas de terceiros. A camada possui **zero dependências externas**.

#### Camada `application/`
- **O que entra:** Casos de uso modelados como classes de responsabilidade única (uma classe por intenção do usuário), contendo um único método público assíncrono `async def execute(self, ...)`, parâmetros de entrada tipados (Commands/Queries ou tipos primitivos), e as portas de saída (interfaces de repositório) definidas estritamente como `typing.Protocol` ou `abc.ABC`.
- **O que NÃO entra:** Queries SQL, sessões de banco (`Session`), decorators de rota HTTP, objetos de requisição/resposta do FastAPI (`Request`, `Response`, `HTTPException`), ou serialização JSON. A camada de aplicação desconhece se está sendo chamada por uma API HTTP, CLI ou fila assíncrona.

#### Camada `infrastructure/`
- **O que entra:** Implementações concretas das portas de saída. Contém as definições de tabela do SQLModel/SQLAlchemy para o banco relacional (`sqlmodel_models.py`), as migrações do Alembic, o gerenciamento de conexão e engine (`database.py`), e o repositório concreto `SQLModelCardapioRepository`, responsável por traduzir entidades de domínio para modelos de persistência e executar operações de banco.
- **O que NÃO entra:** Regras de negócio de domínio, lógica de orquestração de casos de uso, e contratos de endpoints HTTP da API.

#### Camada `api/`
- **O que entra:** Adaptadores de entrada HTTP. Contém os routers do FastAPI (`APIRouter`) que recebem os payloads validados pela requisição, acionam diretamente os casos de uso via injeção com `fastapi.Depends()`, schemas Pydantic de entrada e saída (DTOs da API), e o exception handler global registrado no FastAPI que mapeia o atributo `codigo` das exceções de domínio para os status HTTP corretos via dicionário estático (sem cadeia de `isinstance`).
- **O que NÃO entra:** Lógica de negócio, consultas diretas ao banco de dados, transações ORM (`sessao.commit()`), ou instâncias diretas de modelos de banco.

---

## 3. 🔄 Migração em Fases Incrementais

A estratégia de migração é 100% incremental e reversível. Cada fase é um PR pequeno, testável e revertível sozinho, sem depender de nenhuma fase futura para funcionar.

```mermaid
flowchart LR
    F0["Fase 0<br/>Rede de Segurança<br/>(Testes & Harness)"] --> F1["Fase 1<br/>Camada Domain<br/>(Entidades & Erros)"]
    F1 --> F2["Fase 2<br/>Camada Application<br/>(Portas & Use Cases)"]
    F2 --> F3["Fase 3<br/>Camada Infrastructure<br/>(Repo SQLModel & DDL)"]
    F3 --> F4["Fase 4<br/>Camada API<br/>(Routers, DTOs & Handlers)"]
    F4 --> F5["Fase 5<br/>Fiação Final & Gate<br/>(Cleanup & Invariantes)"]
```

---

### Fase 0: Rede de Segurança de Testes e Isolamento de Ambiente
- **Objetivo:** Estabelecer um test harness robusto e independente de infraestrutura externa (PostgreSQL local), adicionando testes de caracterização que cobrem 100% do comportamento observável atual antes de tocar em qualquer linha da aplicação.
- **Arquivos afetados:**
  - `[NOVO] tests/conftest.py`: Fixture com engine SQLite em memória usando `StaticPool` e substituição limpa do dependency override de `obter_sessao`, garantindo que os testes rodem em qualquer máquina com zero configuração.
  - `[MODIFICADO] tests/test_cardapio.py`: Expansão da suíte para cobrir filtros (`categoria`, `disponivel`, `busca`, `preco_maximo`), ordenação, erros 404 em PUT/PATCH/DELETE, erros 422 de validação e rotas auxiliares (`/hello`, `/clientes`, `/auth`).
- **Critério de pronto verificável por máquina:**
  - Comando: `pytest -v` executado sem variáveis de ambiente prévias (com `.env` apontando para PostgreSQL inexistente).
  - Saída esperada: 100% dos testes passando (`exit code 0`), sem erro de conexão com PostgreSQL e sem poluição de banco em disco.
- **Risco específico:** A fixture alterar inadvertidamente a ordem de execução ou não isolar transações entre testes.
  - *Mitigação:* Usar fixture de banco com escopo `function` que recria o schema ou efetua rollback a cada teste.

---

### Fase 1: Camada de Domínio Pura (`domain/`)
- **Objetivo:** Criar a entidade pura `ItemCardapio` e a hierarquia de exceções de domínio com `codigo` semântico, com zero dependências externas.
- **Arquivos afetados:**
  - `[NOVO] app/domain/__init__.py`
  - `[NOVO] app/domain/errors.py`: Classe base `ErroDominio(Exception)` com atributos `mensagem: str` e `codigo: str`; classe `ItemNaoEncontradoError(ErroDominio)` com `codigo = "ITEM_NAO_ENCONTRADO"`.
  - `[NOVO] app/domain/cardapio.py`: Entidade pura `ItemCardapio` contendo campos e comportamentos de domínio (ex: `alternar_disponibilidade()`).
  - `[NOVO] tests/test_domain.py`: Testes unitários puros da entidade e seus erros.
- **Critério de pronto verificável por máquina:**
  - Comando: `python -c "import app.domain.cardapio; import app.domain.errors"` e `pytest tests/test_domain.py`
  - Saída esperada: Sucesso com zero imports de `sqlmodel`, `sqlalchemy` ou `fastapi` em `app/domain`.
- **Risco específico:** Acoplar acidentalmente tipos do Pydantic/SQLModel na camada de domínio.
  - *Mitigação:* Script de verificação automatizada (`grep` ou `ast`) garantindo ausência de imports de fora de `app.domain` e da biblioteca padrão.

---

### Fase 2: Camada de Aplicação (`application/`)
- **Objetivo:** Criar as portas de saída (`CardapioRepository` via `Protocol`) e os 6 casos de uso no padrão CQS, cada um em sua própria classe com método único `async def execute(...)`.
- **Arquivos afetados:**
  - `[NOVO] app/application/__init__.py`
  - `[NOVO] app/application/ports/cardapio_repository.py`: Interface `Protocol` com métodos assíncronos (`listar`, `obter_por_id`, `salvar`, `remover`).
  - `[NOVO] app/application/use_cases/listar_cardapio.py`
  - `[NOVO] app/application/use_cases/obter_item_cardapio.py`
  - `[NOVO] app/application/use_cases/criar_item_cardapio.py`
  - `[NOVO] app/application/use_cases/atualizar_item_cardapio.py`
  - `[NOVO] app/application/use_cases/alternar_disponibilidade.py`
  - `[NOVO] app/application/use_cases/remover_item_cardapio.py`
  - `[NOVO] tests/test_use_cases.py`: Testes unitários de cada caso de uso utilizando um repositório em memória falso (`FakeCardapioRepository`).
- **Critério de pronto verificável por máquina:**
  - Comando: `pytest tests/test_use_cases.py`
  - Saída esperada: Todos os casos de uso testados e validados unitariamente, inclusive lançando `ItemNaoEncontradoError`.
- **Risco específico:** Caso de uso realizar operações de persistência direta ou assumir tipos específicos de banco.
  - *Mitigação:* Casos de uso dependem exclusivamente da porta `CardapioRepository` injetada via construtor `__init__`.

---

### Fase 3: Camada de Infraestrutura (`infrastructure/`)
- **Objetivo:** Isolar as tabelas ORM do SQLModel em `infrastructure/repositories/sqlmodel_models.py`, implementar o repositório concreto `SQLModelCardapioRepository`, e atualizar `migrations/env.py` para que as migrações do Alembic continuem funcionando perfeitamente sem alteração de schema DDL.
- **Arquivos afetados:**
  - `[NOVO] app/infrastructure/__init__.py`
  - `[NOVO] app/infrastructure/repositories/sqlmodel_models.py`: Tabela `ItemCardapioTable` com `__tablename__ = "itens_cardapio"`.
  - `[NOVO] app/infrastructure/repositories/sqlmodel_cardapio_repository.py`: Adaptador concreto que implementa `CardapioRepository` usando a sessão do SQLModel.
  - `[NOVO] app/infrastructure/seed.py`: Função `seed_dados_iniciais(session)` extraída do `app/main.py`.
  - `[MODIFICADO] migrations/env.py`: Atualização do import de metadados para apontar para o novo arquivo de modelos de infraestrutura sem alterar nenhuma migration existente.
  - `[NOVO] tests/test_infrastructure_repository.py`: Teste de integração do repositório com SQLite.
- **Critério de pronto verificável por máquina:**
  - Comando: `alembic check` e `pytest tests/test_infrastructure_repository.py`
  - Saída esperada: Alembic reconhece o schema sem divergências (`No new upgrade operations detected`) e o repositório passa em todas as operações CRUD.
- **Risco específico:** Divergência no nome da tabela ou colunas causando alteração indevida de DDL nas migrações do Alembic.
  - *Mitigação:* `__tablename__ = "itens_cardapio"` e tipos de colunas mantidos rigorosamente idênticos.

---

### Fase 4: Camada de API e Adaptadores de Entrada (`api/`)
- **Objetivo:** Implementar os schemas de requisição/resposta (DTOs), routers unificados do FastAPI que orquestram a requisição e invocam os casos de uso via injeção de dependência nativa com `Depends()`, e o exception handler global para mapear `ErroDominio.codigo` para status HTTP sem usar `isinstance`.
- **Arquivos afetados:**
  - `[NOVO] app/api/__init__.py`
  - `[NOVO] app/api/schemas/cardapio_schemas.py`: `ItemCardapioCreate`, `ItemCardapioUpdate`, `ItemCardapioResponse`.
  - `[NOVO] app/api/exception_handlers.py`: Exception handler global com dicionário estático `MAPA_ERRO_STATUS = {"ITEM_NAO_ENCONTRADO": 404, ...}` retornando `{"detail": exc.mensagem, "codigo": exc.codigo}`.
  - `[NOVO] app/api/dependencies.py`: Funções geradoras para `FastAPI.Depends` que fornecem a sessão, instanciam o repositório e injetam nos casos de uso.
  - `[NOVO] app/api/routers/cardapio_router.py`: Roteador que recebe parâmetros, executa os casos de uso e retorna schemas de resposta.
- **Critério de pronto verificável por máquina:**
  - Comando: `pytest tests/test_cardapio.py`
  - Saída esperada: Todos os testes existentes da API continuam passando com exatamente as mesmas URLs, status codes e payloads.
- **Risco específico:** Formato de erro quebrar o frontend web (`frontend/api.js` lê `erroJson.detail`).
  - *Mitigação:* O payload retornado pelo exception handler global preserva explicitamente a chave `detail`: `{"detail": exc.mensagem, "codigo": exc.codigo}`.

---

### Fase 5: Conexão Final, Remoção de Código Legado e Validação de Gate
- **Objetivo:** Atualizar `app/main.py` para usar as novas rotas da camada `api/`, registrar o exception handler global, remover os arquivos legados obsoletos (`app/models.py`, `app/routers/cardapio.py`), e garantir o gate de qualidade.
- **Arquivos afetados:**
  - `[MODIFICADO] app/main.py`: Registra o exception handler global, inclui as rotas de `app.api.routers`, e chama o seed através de `infrastructure`.
  - `[REMOVIDO] app/models.py`: Código substituído pelas camadas de domínio, schemas e tabelas de infraestrutura.
  - `[REMOVIDO] app/routers/cardapio.py`: Substituído por `app/api/routers/cardapio_router.py`.
- **Critério de pronto verificável por máquina:**
  - Comando: Execução da suíte completa de testes (`pytest -v`), teste de frontend estático e checagem de integridade das importações.
  - Saída esperada: Zero erros, zero warnings bloqueantes, frontend acessível e funcional.
- **Risco específico:** Algum import esquecido apontando para `app.models` ou `app.routers`.
  - *Mitigação:* Busca global (`grep`) no repositório por referências antigas antes de finalizar a remoção.

---

## 4. 🛡️ Candidatos a INVARIANTES.md

Estes 7 invariantes capturam as regras arquiteturais e de negócio inegociáveis do projeto, estruturados no formato: **Invariante**, **Caminho seguro** e **Enforcement**.

### Invariante 1: Pureza Absoluta da Camada de Domínio
- **Invariante:** O diretório `app/domain/` não pode conter nenhum import de bibliotecas externas ou frameworks (proibidos: `fastapi`, `sqlmodel`, `sqlalchemy`, `pydantic.Field` com binds de ORM, `starlette`, etc.).
- **Caminho seguro:** Entidades de domínio usam `dataclasses` padrão ou modelos puros. Regras de negócio vivem em métodos da entidade ou em serviços de domínio puros.
- **Enforcement:** Teste automatizado com AST ou verificação via script de lint que falha o build caso qualquer import fora da biblioteca padrão ou de `app.domain` seja detectado em `app/domain/`.

### Invariante 2: Casos de Uso com Responsabilidade Única e Método Único `execute()`
- **Invariante:** Todo caso de uso na camada `app/application/use_cases/` deve ser uma classe independente contendo exatamente um único método público assíncrono chamado `async def execute(self, ...)`.
- **Caminho seguro:** Crie uma classe por intenção do usuário (ex: `CriarItemCardapioUseCase`, `AlternarDisponibilidadeUseCase`). Dependências externas são recebidas no `__init__` através de portas (`Protocol`).
- **Enforcement:** Teste unitário arquitetural que inspeciona dinamicamente as classes sob `app.application.use_cases` e valida que cada classe possui apenas `__init__` e `execute` como métodos públicos.

### Invariante 3: Mapeamento de Erros por `codigo` Semântico sem Cadeia de `isinstance`
- **Invariante:** Erros de domínio nunca devem conter status HTTP, e a camada de API nunca deve inspecionar exceções usando cadeias de `if isinstance(e, ...)`.
- **Caminho seguro:** Toda exceção de domínio herda de `ErroDominio` e define um atributo `codigo: str` único e semântico em caixa alta (ex: `"ITEM_NAO_ENCONTRADO"`). A camada de API registra um exception handler global que busca o status HTTP em uma tabela/dicionário mapeando `codigo -> status_code`.
- **Enforcement:** Code review e teste automatizado que garante que toda nova subclasse de `ErroDominio` possua um código mapeado no dicionário de status da API.

### Invariante 4: Preservação Estrita de Contrato e Compatibilidade com o Frontend
- **Invariante:** Nenhuma refatoração pode alterar o caminho das URLs, verbos HTTP, parâmetros de consulta, status codes ou o formato do corpo JSON de resposta (sucesso ou erro).
- **Caminho seguro:** Em respostas de erro, o campo `detail` deve ser sempre preservado para não quebrar a lógica de captura do `frontend/api.js` (`throw new Error(erroJson.detail || ...)`).
- **Enforcement:** Suíte de testes de integração na camada de API executando asserções rigorosas contra o schema JSON e status HTTP esperados pelo frontend.

### Invariante 5: Injeção de Dependência Exclusiva via Recursos Nativos do FastAPI
- **Invariante:** A montagem de dependências da API deve utilizar estritamente o mecanismo nativo `fastapi.Depends()`. Proibido o uso de containers de IoC ou bibliotecas de injeção externas.
- **Caminho seguro:** Crie funções de fábrica em `app/api/dependencies.py` que recebem a sessão de banco, instanciam o repositório concreto e o passam ao caso de uso.
- **Enforcement:** Revisão estática de dependências no `requirements.txt` garantindo que nenhuma biblioteca de injeção de dependência externa seja adicionada.

### Invariante 6: Regra de Negócio de Validação de Preço e Dados do Prato
- **Invariante:** Um item do cardápio não pode existir no domínio com preço menor ou igual a zero (`preco > 0`), nem com nome com menos de 2 caracteres (`len(nome) >= 2`).
- **Caminho seguro:** A validação é aplicada tanto na barreira de entrada da API (via Pydantic schema) quanto na criação/atualização da entidade de domínio (invariante de domínio).
- **Enforcement:** Testes unitários na camada de domínio garantindo que valores inválidos disparem exceções de domínio apropriadas (`RegraVioladaError`).

### Invariante 7: Isolamento Total dos Testes sem Dependência de Banco Externo
- **Invariante:** A execução de `pytest` deve passar em qualquer máquina com zero dependências externas em execução (sem exigir PostgreSQL local ou na nuvem).
- **Caminho seguro:** A suíte de testes utiliza fixture com SQLite em memória (`sqlite:///:memory:` ou arquivo temporário isolado), aplicando override de sessão via dependency injection do FastAPI.
- **Enforcement:** Execução do comando `DATABASE_URL="" pytest` no pipeline de CI/CD para assegurar que nenhum teste acesse a rede ou tente conectar ao PostgreSQL local por padrão.

---

## 5. ⚠️ Riscos Gerais da Migração e Mitigações

| Risco | Impacto | Probabilidade | Mitigação |
| :--- | :--- | :--- | :--- |
| **1. Quebra de compatibilidade com o Frontend Vanilla JS** | Alto | Média | O frontend consome `erroJson.detail` e schemas específicos. Mitigado mantendo o payload de erro como `{"detail": exc.mensagem, "codigo": exc.codigo}` e validando com os testes de ponta a ponta da Fase 0. |
| **2. Quebra de migrações do Alembic** | Crítico | Baixa | O Alembic depende do `SQLModel.metadata`. Ao mover os modelos para `infrastructure/repositories/sqlmodel_models.py`, o `migrations/env.py` deve importar de lá e validar via comando `alembic check` antes de qualquer merge. |
| **3. Bloqueio síncrono vs assíncrono** | Médio | Média | O SQLAlchemy/SQLModel atual opera de modo síncrono no SQLite/PostgreSQL (`psycopg2-binary`). Os casos de uso serão assíncronos (`async def execute`), mas chamarão o repositório de forma segura, mantendo a compatibilidade sem forçar troca arriscada de driver de banco neste momento. |
| **4. Efeito "Big Bang" e regressões silenciosas** | Alto | Baixa | A migração é fatiada em 6 etapas (Fase 0 a 5). Cada etapa é um PR autocontido com critério de pronto verificável por máquina. O código legado só é removido na Fase 5, após a nova fiação estar 100% verde nos testes. |
| **5. Dependência de PostgreSQL local nos testes** | Médio | Alta | Resolvido logo na Fase 0 com a criação do `conftest.py` com isolamento completo em SQLite, impedindo que a ausência de PostgreSQL no host quebre a esteira de desenvolvimento. |
