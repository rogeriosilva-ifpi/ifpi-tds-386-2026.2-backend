"""
Caso de Uso: Atualizar Item do Cardápio (Command).
"""
from app.application.ports.cardapio_repository import CardapioRepository
from app.domain.cardapio import ItemCardapio
from app.domain.errors import ItemNaoEncontradoError


class AtualizarItemCardapioUseCase:
    """Caso de uso para atualização de dados de um item existente."""

    def __init__(self, repository: CardapioRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        item_id: int,
        nome: str | None = None,
        descricao: str | None = None,
        preco: float | None = None,
        categoria: str | None = None,
        disponivel: bool | None = None,
        tempo_preparo_minutos: int | None = None,
    ) -> ItemCardapio:
        item = await self.repository.obter_por_id(item_id)
        if not item:
            raise ItemNaoEncontradoError(item_id)

        item.atualizar(
            nome=nome,
            descricao=descricao,
            preco=preco,
            categoria=categoria,
            disponivel=disponivel,
            tempo_preparo_minutos=tempo_preparo_minutos,
        )
        return await self.repository.salvar(item)
