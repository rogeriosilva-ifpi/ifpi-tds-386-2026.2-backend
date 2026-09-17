"""
APIRouter de Cardápio (Adaptador de Entrada Fino).

CONCEITO: APIRouter fino que apenas declara rotas, validações de query/path e delega ao Controller.
"""
from fastapi import APIRouter, Depends, Query, status
from app.api.schemas.cardapio_schemas import (
    ItemCardapioCreate,
    ItemCardapioUpdate,
    ItemCardapioResponse,
)
from app.api.controllers.cardapio_controller import CardapioController
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
controller = CardapioController()


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
    return await controller.listar(
        categoria=categoria,
        disponivel=disponivel,
        busca=busca,
        preco_maximo=preco_maximo,
        use_case=use_case,
    )


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
    return await controller.obter_por_id(item_id=item_id, use_case=use_case)


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
    return await controller.criar(dados=dados, use_case=use_case)


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
    return await controller.atualizar(item_id=item_id, dados=dados, use_case=use_case)


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
    return await controller.alternar_disponibilidade(item_id=item_id, use_case=use_case)


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover item do cardápio",
)
async def remover_item(
    item_id: int,
    use_case: RemoverItemCardapioUseCase = Depends(obter_remover_item_use_case),
) -> None:
    await controller.remover(item_id=item_id, use_case=use_case)
