"""
Controller de Cardápio (Adaptador de Entrada Assíncrono).

CONCEITO: Orquestra a requisição HTTP, aciona os Casos de Uso e serializa para Schemas de resposta.
"""
from app.domain.cardapio import ItemCardapio
from app.api.schemas.cardapio_schemas import (
    ItemCardapioCreate,
    ItemCardapioUpdate,
    ItemCardapioResponse,
)
from app.application.use_cases import (
    ListarCardapioUseCase,
    ObterItemCardapioUseCase,
    CriarItemCardapioUseCase,
    AtualizarItemCardapioUseCase,
    AlternarDisponibilidadeUseCase,
    RemoverItemCardapioUseCase,
)


class CardapioController:
    """Controller responsável pela orquestração dos endpoints de cardápio."""

    @staticmethod
    def _to_response(item: ItemCardapio) -> ItemCardapioResponse:
        return ItemCardapioResponse(
            id=item.id,  # type: ignore[arg-type]
            nome=item.nome,
            descricao=item.descricao,
            preco=item.preco,
            categoria=item.categoria,
            disponivel=item.disponivel,
            tempo_preparo_minutos=item.tempo_preparo_minutos,
        )

    async def listar(
        self,
        categoria: str | None,
        disponivel: bool | None,
        busca: str | None,
        preco_maximo: float | None,
        use_case: ListarCardapioUseCase,
    ) -> list[ItemCardapioResponse]:
        itens = await use_case.execute(
            categoria=categoria,
            disponivel=disponivel,
            busca=busca,
            preco_maximo=preco_maximo,
        )
        return [self._to_response(it) for it in itens]

    async def obter_por_id(
        self,
        item_id: int,
        use_case: ObterItemCardapioUseCase,
    ) -> ItemCardapioResponse:
        item = await use_case.execute(item_id=item_id)
        return self._to_response(item)

    async def criar(
        self,
        dados: ItemCardapioCreate,
        use_case: CriarItemCardapioUseCase,
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
        return self._to_response(item_criado)

    async def atualizar(
        self,
        item_id: int,
        dados: ItemCardapioUpdate,
        use_case: AtualizarItemCardapioUseCase,
    ) -> ItemCardapioResponse:
        dados_atualizados = dados.model_dump(exclude_unset=True)
        item_atualizado = await use_case.execute(
            item_id=item_id,
            **dados_atualizados,
        )
        return self._to_response(item_atualizado)

    async def alternar_disponibilidade(
        self,
        item_id: int,
        use_case: AlternarDisponibilidadeUseCase,
    ) -> ItemCardapioResponse:
        item_atualizado = await use_case.execute(item_id=item_id)
        return self._to_response(item_atualizado)

    async def remover(
        self,
        item_id: int,
        use_case: RemoverItemCardapioUseCase,
    ) -> None:
        await use_case.execute(item_id=item_id)
