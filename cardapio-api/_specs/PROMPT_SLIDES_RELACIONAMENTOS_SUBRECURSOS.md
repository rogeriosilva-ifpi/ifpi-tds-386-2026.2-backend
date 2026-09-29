# 📜 Prompt Mestre para Geração dos Slides: Relacionamentos no SQLModel, Sub-Recursos REST e Autorização por Header

> **Como usar este prompt:** Copie o texto abaixo na íntegra e envie para o modelo de IA (ou utilize para alimentar geradores de slides). O prompt já está calibrado para gerar uma apresentação profissional de **mais de 30 slides no formato Marp Markdown**, perfeitamente alinhada à didática do **Prof. Rogério Silva** no **IFPI TDS 386**.

---

```markdown
Você é o Prof. Rogério Silva, docente da disciplina de Desenvolvimento Backend no Instituto Federal do Piauí (IFPI - Campus Teresina Central, Turma TDS 386 - 2026.2).
Sua missão é criar uma apresentação didática completa, aprofundada e visualmente impecável em formato Marp Markdown, contendo exatamente 35 slides detalhados sobre o tema:

"Relacionamentos no SQLModel, Sub-Recursos em APIs RESTful e Controle de Acesso por Header HTTP".

A apresentação deve se basear diretamente na arquitetura e no código real do projeto "Cardápio Digital / Delivery API" em desenvolvimento pelos alunos.

=============================================================================
DIRETRIZES TÉCNICAS E DE FORMATAÇÃO DO MARP:
=============================================================================
1. Cabeçalho obrigatório (Frontmatter YAML):
---
marp: true
theme: default
paginate: true
header: "IFPI TDS 386 • Relacionamentos no SQLModel e Sub-Recursos REST"
footer: "Prof. Rogério Silva • 2026.2"
style: |
  section {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f8fafc;
    color: #1e293b;
    padding: 35px 55px;
  }
  h1 { color: #0f766e; }
  h2 { color: #047857; font-size: 1.5rem; border-bottom: 2px solid #10b981; padding-bottom: 4px; }
  h3 { color: #0369a1; font-size: 1.2rem; }
  code { background-color: #e2e8f0; color: #0f172a; padding: 2px 6px; border-radius: 4px; font-size: 0.88em; }
  pre code { background-color: transparent; font-size: 0.80em; }
  .box { background: #ffffff; border-left: 5px solid #10b981; padding: 10px 16px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin: 8px 0; }
  .alert { background: #fff1f2; border-left: 5px solid #f43f5e; padding: 10px 16px; border-radius: 8px; margin: 8px 0; }
  .analogy { background: #eff6ff; border-left: 5px solid #3b82f6; padding: 10px 16px; border-radius: 8px; margin: 8px 0; }
  table { width: 100%; border-collapse: collapse; font-size: 0.85em; margin: 10px 0; }
  th { background-color: #0f766e; color: white; padding: 8px 12px; text-align: left; }
  td { padding: 8px 12px; border-bottom: 1px solid #cbd5e1; background-color: #ffffff; }
---

2. Regras visuais:
   - Separe cada slide rigorosamente por '---'.
   - Cada slide deve ter um comentário no topo indicando o número e o tema: `<!-- Slide XX: Título -->`.
   - Utilize diagramas Mermaid (`flowchart` e `erDiagram`) onde houver modelagem ou fluxo.
   - Utilize tabelas lado a lado e blocos comparativos entre SQL Puro vs SQLModel.
   - Inclua analogias cotidianas didáticas (caixa registradora, comanda de restaurante, crachá, nota fiscal).

=============================================================================
GRADE COMPLETA E DETALHADA DOS 35 SLIDES:
=============================================================================

### MÓDULO 1: O MUNDO RELACIONAL ALÉM DE TABELAS ISOLADAS (Slides 1 a 4)
- Slide 01: Capa Oficial da Aula (Título, IFPI, Professor, Disciplina, Contexto do Cardápio Digital).
- Slide 02: Objetivos de Aprendizagem & Roteiro Pedagógico (Os 5 pilares: FK, Relationship, Sub-recursos, Cascade e Auth).
- Slide 03: Por que Normalizar? O Problema de Tabelas Isoladas (Por que não colocar os itens dentro de uma coluna de texto do pedido?).
- Slide 04: O Descompasso Objeto-Relacional em Relacionamentos (Bancos usam ponteiros de IDs planos; Orientação a Objetos usa listas e referências diretas de instâncias na memória).

### MÓDULO 2: MODELANDO RELACIONAMENTOS NO SQLMODEL (Slides 5 a 9)
- Slide 05: A Trindade Relacional do SQLModel: Chave Estrangeira (`foreign_key`), Atributo ORM (`Relationship`) e Espelho Bidirecional (`back_populates`).
- Slide 06: Anatomia da Chave Estrangeira: O Atributo Físico no Banco (`cliente_id: int = Field(foreign_key="clientes.id")`).
- Slide 07: Anatomia do Atributo Virtual: A Coleção em Python (`itens: list["ItemPedido"] = Relationship(...)`).
- Slide 08: Diagrama Entidade-Relacionamento do Nosso Sistema (Mermaid erDiagram com Cliente, Pedido, ItemPedido, ItemCardapio).
- Slide 09: Comparativo Lado a Lado: DDL em SQL Puro (`CREATE TABLE ... REFERENCES`) vs Código Python SQLModel.

### MÓDULO 3: EVOLUÇÃO DE ESQUEMA EM TABELAS EXISTENTES (Slides 10 a 13)
- Slide 10: O Desafio: Como conectar novas tabelas a modelos que já estavam funcionando (`Cliente` e `ItemCardapio`)?
- Slide 11: Adicionando `Relationship` em Modelos Existentes: Por que essa alteração NÃO cria colunas novas no banco relacional?
- Slide 12: O Papel das Migrações com Alembic (`0004_cria_tabelas_pedidos_e_itens_pedido.py`): Como o Alembic detecta e cria as tabelas dependentes.
- Slide 13: Cuidados na Ordem de Execução do DDL: Por que não podemos criar `itens_pedido` antes de `pedidos` nem `pedidos` antes de `clientes`?

### MÓDULO 4: O PERIGO E A NECESSIDADE DO CASCADE (Slides 14 a 18)
- Slide 14: O Que é a Deleção em Cascata (*Cascade Delete*)? A diferença vital entre Cascade no Banco de Dados (`ON DELETE CASCADE`) e Cascade no ORM (`cascade_delete=True`).
- Slide 15: Caso 1 (Composição Forte): `Pedido -> ItemPedido`. Por que se o pedido morre, os itens do pedido DEVEM morrer juntos?
- Slide 16: Caso 2 (Catálogo e Histórico): `ItemCardapio -> ItemPedido`. O PERIGO FATAL: Por que NUNCA colocar cascade delete entre o cardápio e o item do pedido!
- Slide 17: Caso 3 (Relacionamento de Negócio): `Cliente -> Pedidos`. O debate profissional: Excluir pedidos ou aplicar Soft-Delete/Anonimização?
- Slide 18: Tabela Comparativa de Comportamentos de Integridade: `CASCADE`, `RESTRICT`, `SET NULL` e `NO ACTION`.

### MÓDULO 5: PREOCUPAÇÕES CRÍTICAS DE ENGENHARIA NO MUNDO REAL (Slides 19 a 23)
- Slide 19: O Snapshot de Preço Histórico: Por que `ItemPedido.preco_unitario` deve ser gravado e congelado no momento da compra (Analogia da Nota Fiscal).
- Slide 20: A Máquina de Estados do Pedido: Ciclo de Vida (`CRIADO` -> `CONFIRMADO` -> `EM_PREPARO` -> `PRONTO` -> `ENTREGUE` ou `CANCELADO`).
- Slide 21: O Fantasma da Recursão Infinita em Serialização: Como referências circulares (`Pedido -> Itens -> Pedido`) quebram o FastAPI com `RecursionError` e como os DTOs Pydantic resolvem isso.
- Slide 22: O Problema do N+1 Queries: O que acontece se percorrermos pedidos em um loop sem Eager Loading (`selectinload` vs Lazy Loading).
- Slide 23: Transações Atômicas e Integridade Financeira: Garantindo que inserção de item e recálculo do `valor_total` ocorram no mesmo `commit()`.

### MÓDULO 6: SUB-RECURSOS EM APIS RESTFUL (Slides 24 a 28)
- Slide 24: O Que é um Sub-Recurso REST? A semântica de hierarquia de URIs (`/pedidos/{pedido_id}/itens`).
- Slide 25: Sub-Recurso vs Recurso Direto: Quando usar `/pedidos/{id}/itens` e quando usar `/itens-pedido/{id}`?
- Slide 26: As Quatro Operações no Sub-Recurso de Itens: Listar (GET), Inserir (POST), Alterar Quantidade (PUT) e Remover (DELETE).
- Slide 27: O Sub-Recurso `/clientes/{cliente_id}/pedidos`: Obtendo o histórico de consumo sob a perspectiva da entidade Cliente.
- Slide 28: Códigos de Status HTTP Semânticos em Sub-Recursos: 201 Created com Location/Response, 204 No Content, 400 Bad Request e 404 Not Found.

### MÓDULO 7: AUTORIZAÇÃO E SEGURANÇA PROVISÓRIA VIA HEADER (Slides 29 a 32)
- Slide 29: Por que Autenticação por Header HTTP? Como o cabeçalho `X-Cliente-Id` funciona antes de implantarmos JWT/OAuth2.
- Slide 30: Injeção de Dependências no FastAPI com `Header(...)` e `Depends(obter_cliente_autenticado)`.
- Slide 31: Autenticação (Quem é você? 401) vs Autorização (O que você pode fazer? 403): Diferenças conceituais práticas.
- Slide 32: O Controle de Posse (*Ownership Check*): Como impedimos que o Cliente 2 consulte, altere ou delete os pedidos do Cliente 1.

### MÓDULO 8: SÍNTESE, ARQUITETURA E DESAFIO PRÁTICO (Slides 33 a 35)
- Slide 33: Tabela Resumo do Backend: Entidades, Tabelas Físicas, Relacionamentos, Tipos de Cascade e Rotas Expostas.
- Slide 34: Mapa Mental Completo da Solução Integrada (Mermaid flowchart mostrando a requisição com Header passando pela dependência, router, banco e resposta).
- Slide 35: Desafio de Laboratório para a Turma: Adicionar taxa de entrega dinâmica baseada no bairro do cliente e calcular no total do pedido.
```
