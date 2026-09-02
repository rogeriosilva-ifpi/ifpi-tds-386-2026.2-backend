from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, or_

from app.database import obter_sessao
from app.models import (
    ItemCardapio,
    ItemCardapioCreate,
    ItemCardapioUpdate,
    ItemCardapioResponse,
)

# =====================================================================
# CONCEITO: APIRouter (Modularização de Rotas)
# O APIRouter agrupa endpoints relacionados a um mesmo recurso (/cardapio).
# Isso impede que o arquivo principal (main.py) fique gigantesco.
# =====================================================================
router = APIRouter(prefix="/cardapio", tags=["Cardápio"])


# =====================================================================
# CONCEITO: Consulta com Query Parameters e Filtros Dinâmicos
# Os parâmetros de consulta (após o '?' na URL) são opcionais.
# Exemplo: /cardapio?categoria=Bebidas&disponivel=true&busca=suco
# =====================================================================
@router.get("/", response_model=list[ItemCardapioResponse], summary="Listar itens do cardápio")
def listar_cardapio(
    categoria: str | None = Query(default=None, description="Filtrar por categoria (ex: Lanches, Bebidas)"),
    disponivel: bool | None = Query(default=None, description="Filtrar por disponibilidade (true ou false)"),
    busca: str | None = Query(default=None, description="Buscar por termo no nome ou descrição"),
    preco_maximo: float | None = Query(default=None, description='Filtrar por no máximo este preço R$.'),
    sessao: Session = Depends(obter_sessao),
):
    query = select(ItemCardapio)

    if preco_maximo:
        query = query.where(ItemCardapio.preco <= preco_maximo)

    if categoria:
        query = query.where(ItemCardapio.categoria == categoria)

    if disponivel is not None:
        query = query.where(ItemCardapio.disponivel == disponivel)

    if busca:
        termo = f"%{busca}%"
        query = query.where(
            or_(
                ItemCardapio.nome.ilike(termo),
                ItemCardapio.descricao.ilike(termo)
            )
        )

    # Ordenar por ID para manter listagem consistente
    query = query.order_by(ItemCardapio.id)
    itens = sessao.exec(query).all()
    return itens


# =====================================================================
# CONCEITO: Path Parameter (Parâmetro de Rota) e Tratamento 404
# O ID vem direto no caminho da URL: /cardapio/10
# Se não existir, lançamos semanticamente HTTPException com status 404.
# =====================================================================
@router.get("/{item_id}", response_model=ItemCardapioResponse, summary="Obter item por ID")
def obter_item(
    item_id: int, 
    sessao: Session = Depends(obter_sessao)
):
    item = sessao.get(ItemCardapio, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item não localizado com id={item_id}."
        )
    return item


# =====================================================================
# CONCEITO: Criação de Recurso com POST e Status 201 Created
# 1. Recebe os dados validados pelo schema ItemCardapioCreate.
# 2. Converte para o modelo ItemCardapio da tabela.
# 3. Executa sessao.add() e sessao.commit() para persistir no SQLite.
# 4. Usa sessao.refresh() para carregar o 'id' gerado pelo banco.
# =====================================================================
@router.post(
    "/", 
    response_model=ItemCardapioResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo item no cardápio"
)
def criar_item(
    dados: ItemCardapioCreate, 
    sessao: Session = Depends(obter_sessao)
):
    novo_item = ItemCardapio.model_validate(dados)
    sessao.add(novo_item)
    sessao.commit()
    sessao.refresh(novo_item)
    return novo_item


# =====================================================================
# CONCEITO: Atualização de Recurso com PUT (Substituição/Edição)
# Localiza o registro existente no banco e atualiza apenas os campos enviados.
# =====================================================================
@router.put(
    "/{item_id}", 
    response_model=ItemCardapioResponse,
    summary="Atualizar dados de um item existente"
)
def atualizar_item(
    item_id: int, 
    dados: ItemCardapioUpdate, 
    sessao: Session = Depends(obter_sessao)
):
    item_banco = sessao.get(ItemCardapio, item_id)
    if not item_banco:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item não localizado com id={item_id}."
        )

    # exclude_unset=True ignora campos que o cliente não enviou no payload
    dados_atualizados = dados.model_dump(exclude_unset=True)
    for campo, valor in dados_atualizados.items():
        setattr(item_banco, campo, valor)

    sessao.add(item_banco)
    sessao.commit()
    sessao.refresh(item_banco)
    return item_banco


# =====================================================================
# CONCEITO: Atualização Parcial Rápida com PATCH
# Ideal para alternar rapidamente a disponibilidade de um prato (ex: esgotou na cozinha!).
# =====================================================================
@router.patch(
    "/{item_id}/disponibilidade", 
    response_model=ItemCardapioResponse,
    summary="Alternar disponibilidade (disponível / esgotado)"
)
def alternar_disponibilidade(
    item_id: int, 
    sessao: Session = Depends(obter_sessao)
):
    item_banco = sessao.get(ItemCardapio, item_id)
    if not item_banco:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item não localizado com id={item_id}."
        )

    item_banco.disponivel = not item_banco.disponivel
    sessao.add(item_banco)
    sessao.commit()
    sessao.refresh(item_banco)
    return item_banco


# =====================================================================
# CONCEITO: Exclusão com DELETE e Status 204 No Content
# Sucesso em DELETE normalmente não precisa retornar corpo de resposta (HTTP 204).
# =====================================================================
@router.delete(
    "/{item_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover item do cardápio"
)
def remover_item(
    item_id: int, 
    sessao: Session = Depends(obter_sessao)
):
    item_banco = sessao.get(ItemCardapio, item_id)
    if not item_banco:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item não localizado com id={item_id}."
        )

    sessao.delete(item_banco)
    sessao.commit()
    return None
