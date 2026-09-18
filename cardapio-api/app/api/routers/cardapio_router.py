"""
APIRouter de Cardápio (Adaptador de Entrada HTTP).

CONCEITO: Recebe as requisições HTTP, valida payloads com Pydantic,
executa os Casos de Uso (CQS) e serializa para Schemas de resposta.
"""
from fastapi import APIRouter, Depends, Query, status
from app.domain.cardapio import ItemCardapio
from app.api.schemas.cardapio_schemas import (
    ItemCardapioCreate,
    ItemCardapioUpdate,
    ItemCardapioResponse,
)
from app.api.dependencies import (
    obter_listar_cardapio_use_case,
    obter_obter_item_use_case,
    obter_criar_item_use_case,
    obter_atualizar_item_use_case,
    obter_alternar_disponibilidade_use_case,
    obter_remover_item_use_case,
)
from app.application.use_cases import (
    ListarCardapioUseCase,
    ObterItemCardapioUseCase,
    CriarItemCardapioUseCase,
    AtualizarItemCardapioUseCase,
    AlternarDisponibilidadeUseCase,
    RemoverItemCardapioUseCase,
)

router = APIRouter(prefix="/cardapio", tags=["Cardápio"])


def _to_response(item: ItemCardapio) -> ItemCardapioResponse:
    """Converte a entidade de domínio em DTO de resposta da API."""
    return ItemCardapioResponse(
        id=item.id,  # type: ignore[arg-type]
        nome=item.nome,
        descricao=item.descricao,
        preco=item.preco,
        categoria=item.categoria,
        disponivel=item.disponivel,
        tempo_preparo_minutos=item.tempo_preparo_minutos,
    )


@router.get(
    "/",
    response_model=list[ItemCardapioResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar itens do cardápio do restaurante",
)
async def listar_cardapio(
    categoria: str | None = Query(default=None, description="Filtrar por categoria (ex: Lanches, Bebidas)"),
    disponivel: bool | None = Query(default=None, description="Filtrar por disponibilidade (true ou false)"),
    busca: str | None = Query(default=None, description="Buscar por termo no nome ou descrição"),
    preco_maximo: float | None = Query(default=None, description="Filtrar por no máximo este preço R$."),
    use_case: ListarCardapioUseCase = Depends(obter_listar_cardapio_use_case),
) -> list[ItemCardapioResponse]:
    itens = await use_case.execute(
        categoria=categoria,
        disponivel=disponivel,
        busca=busca,
        preco_maximo=preco_maximo,
    )
    return [_to_response(it) for it in itens]


@router.get(
    "/{item_id}",
    response_model=ItemCardapioResponse,
    status_code=status.HTTP_200_OK,
    summary="Obter item por ID",
)
async def obter_item(
    item_id: int,
    use_case: ObterItemCardapioUseCase = Depends(obter_obter_item_use_case),
) -> ItemCardapioResponse:
    item = await use_case.execute(item_id=item_id)
    return _to_response(item)


@router.post(
    "/",
    response_model=ItemCardapioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo item no cardápio",
)
async def criar_item(
    dados: ItemCardapioCreate,
    use_case: CriarItemCardapioUseCase = Depends(obter_criar_item_use_case),
) -> ItemCardapioResponse:
    novo_item = ItemCardapio(
        nome=dados.nome,
        descricao=dados.descricao,
        preco=dados.preco,
        categoria=dados.categoria,
        disponivel=dados.disponivel,
        tempo_preparo_minutos=dados.tempo_preparo_minutos,
    )
    item_criado = await use_case.execute(novo_item)
    return _to_response(item_criado)


@router.put(
    "/{item_id}",
    response_model=ItemCardapioResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar dados de um item existente",
)
async def atualizar_item(
    item_id: int,
    dados: ItemCardapioUpdate,
    use_case: AtualizarItemCardapioUseCase = Depends(obter_atualizar_item_use_case),
) -> ItemCardapioResponse:
    dados_atualizados = dados.model_dump(exclude_unset=True)
    item_atualizado = await use_case.execute(item_id=item_id, **dados_atualizados)
    return _to_response(item_atualizado)


@router.patch(
    "/{item_id}/disponibilidade",
    response_model=ItemCardapioResponse,
    status_code=status.HTTP_200_OK,
    summary="Alternar disponibilidade (disponível / esgotado)",
)
async def alternar_disponibilidade(
    item_id: int,
    use_case: AlternarDisponibilidadeUseCase = Depends(obter_alternar_disponibilidade_use_case),
) -> ItemCardapioResponse:
    item_atualizado = await use_case.execute(item_id=item_id)
    return _to_response(item_atualizado)


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover item do cardápio",
)
async def remover_item(
    item_id: int,
    use_case: RemoverItemCardapioUseCase = Depends(obter_remover_item_use_case),
) -> None:
    await use_case.execute(item_id=item_id)
