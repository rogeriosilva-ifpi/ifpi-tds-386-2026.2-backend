# 📋 PROMPT-NOVA-FEATURE.md — Template e Guia de Novas Funcionalidades

Utilize este template para solicitar novas funcionalidades no projeto já refatorado para Arquitetura Hexagonal.  
O template segue a estrutura **Goal / Context / Constraints / Done when**, garantindo que qualquer agente de IA ou desenvolvedor implemente a funcionalidade respeitando rigorosamente as fronteiras de camadas.

---

## 📑 Parte 1: Template Reutilizável

```markdown
<USER_REQUEST>
Goal
Implementar a funcionalidade [NOME_DA_FEATURE]: [DESCRICAO_RESUMIDA_DO_OBJETIVO_E_VALOR_DE_NEGOCIO].

Context
- O projeto segue Arquitetura Hexagonal (Ports & Adapters) conforme descrito em AGENTS.md.
- A funcionalidade envolve o recurso [NOME_DO_RECURSO_DO_DOMINIO] localizado em `app/domain/`.
- Camadas a serem consideradas:
  · domain: [DESCREVER_ENTIDADE_OU_REGRAS_DE_NEGOCIO_A_ADICIONAR]
  · application: Caso de uso no padrão CQS com classe de método único `async def execute(...)`
  · infrastructure: [INDICAR_SE_HA_ALTERACAO_DE_BANCO_OU_PORTA_DE_REPOSITORIO]
  · api: [INDICAR_NOVO_ENDPOINT_OU_SCHEMA_HTTP]

Constraints
- Pureza do Domínio: Zero imports externos em `app/domain/`. Regras de negócio vivem na entidade ou em serviços de domínio.
- Erros Semânticos: Toda exceção de negócio deve herdar de `ErroDominio` e definir um atributo `codigo: str` único em UPPER_SNAKE_CASE.
- Casos de Uso CQS: Exatamente 1 classe por operação, com único método público `async def execute(self, ...)`.
- Mapeamento de Erro: Registrar novos códigos no `MAPA_ERRO_STATUS` em `app/api/exception_handlers.py` (proibido encadeamento de `isinstance`).
- Injeção de Dependência: Usar exclusivamente `fastapi.Depends` em `app/api/dependencies.py`.
- Compatibilidade da API: Respostas de erro devem manter o formato `{"detail": exc.mensagem, "codigo": exc.codigo}`.
- Gate Verde: Testes unitários (domínio e caso de uso) e testes de integração devem passar com `pytest -v`.

Done when
1. Entidade de domínio atualizada/criada com validações de regras e testes em `tests/test_domain.py`.
2. Caso de uso implementado com porta injetada e testes unitários em `tests/test_use_cases.py`.
3. Adaptador de persistência atualizado (e migração Alembic criada, caso o schema do banco tenha mudado).
4. Schema Pydantic, controller e router registrados sob `app/api/`.
5. Suíte de testes passando com `pytest -v` e sem violações no `ruff check app tests`.
</USER_REQUEST>
```

---

## 🎯 Parte 2: Exemplo Completo Preenchido no Domínio do Projeto

Abaixo está um exemplo real pronto para execução, utilizando o recurso **`ItemCardapio`** da aplicação:

```markdown
<USER_REQUEST>
Goal
Implementar a funcionalidade de "Desconto Promocional em Item do Cardápio": permitir que o restaurante aplique um percentual de desconto (entre 1% e 70%) sobre o preço de um prato existente, registrando o preço original e o novo preço com desconto, com endpoint dedicado `PATCH /cardapio/{id}/desconto`.

Context
- O projeto utiliza a arquitetura hexagonal descrita em `AGENTS.md`.
- O recurso envolvido é o `ItemCardapio` em `app/domain/cardapio.py`.
- Camadas a modificar:
  1. `domain`:
     - Adicionar o método `aplicar_desconto(self, percentual: float) -> None` na entidade `ItemCardapio`.
     - Regra: o percentual deve estar entre 1.0 e 70.0. Caso contrário, disparar `DescontoInvalidoError` com `codigo = "DESCONTO_INVALIDO"`.
     - O item não pode estar indisponível para receber desconto; se estiver, disparar `ItemIndisponivelParaPromocaoError` com `codigo = "ITEM_INDISPONIVEL"`.
  2. `application`:
     - Criar `AplicarDescontoItemCardapioUseCase` em `app/application/use_cases/aplicar_desconto.py`.
     - Assinatura: `async def execute(self, item_id: int, percentual: float) -> ItemCardapio`.
     - Orquestração: buscar item por ID via `CardapioRepository`; se não existir, lançar `ItemNaoEncontradoError`; chamar `item.aplicar_desconto(percentual)`; persistir via repositório e retornar a entidade.
  3. `infrastructure`:
     - O método `salvar(item)` já existente na interface `CardapioRepository` é suficiente. Não há necessidade de nova migração DDL neste primeiro momento.
  4. `api`:
     - Criar schema de entrada `AplicarDescontoRequest(percentual: float = Field(gt=0, le=70, description="Percentual de 1 a 70%"))` em `app/api/schemas/cardapio_schemas.py`.
     - Atualizar `app/api/exception_handlers.py` adicionando os novos códigos no `MAPA_ERRO_STATUS`:
       - `"DESCONTO_INVALIDO": status.HTTP_400_BAD_REQUEST`
       - `"ITEM_INDISPONIVEL": status.HTTP_400_BAD_REQUEST`
     - Adicionar método `aplicar_desconto` no controller e expor rota `PATCH /cardapio/{id}/desconto` com status HTTP 200 em `app/api/routers/cardapio_router.py`.

Constraints
- Não utilizar `HTTPException` na camada de domínio ou aplicação.
- O caso de uso deve ser uma classe independente com método único `async def execute()`.
- O endpoint deve retornar `ItemCardapioResponse` com o preço já recalculado com o desconto.
- Caso o `id` não exista, a resposta deve ser `HTTP 404 Not Found` com payload `{"detail": "Item não localizado com id=...", "codigo": "ITEM_NAO_ENCONTRADO"}`.
- O comando `pytest -v` deve validar o novo endpoint, as regras de domínio e os casos de erro.

Done when
1. Entidade `ItemCardapio` possui o método `aplicar_desconto` com testes unitários em `tests/test_domain.py` cobrindo cálculo correto, percentual negativo/acima de 70% e item indisponível.
2. Caso de uso `AplicarDescontoItemCardapioUseCase` implementado e coberto com testes unitários em `tests/test_use_cases.py` (usando `FakeCardapioRepository`).
3. DTO `AplicarDescontoRequest` criado e integrado ao router `PATCH /cardapio/{id}/desconto`.
4. Mapeamento de status registrado no `MAPA_ERRO_STATUS`.
5. Testes de integração adicionados em `tests/test_cardapio_api.py` validando respostas 200, 400 (desconto inválido) e 404 (item não encontrado).
6. Execução verde do gate completo: `ruff check app tests && mypy app && pytest -v`.
</USER_REQUEST>
```
