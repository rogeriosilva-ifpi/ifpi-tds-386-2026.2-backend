"""
Caso de Uso: Obter Item do Cardápio por ID (Query).
"""
from app.application.ports.cardapio_repository import CardapioRepository
from app.domain.cardapio import ItemCardapio
from app.domain.errors import ItemNaoEncontradoError


class ObterItemCardapioUseCase:
    """Caso de uso para consulta de um item específico por ID."""

    def __init__(self, repository: CardapioRepository) -> None:
        self.repository = repository

    async def execute(self, item_id: int) -> ItemCardapio:
        item = await self.repository.obter_por_id(item_id)
        if not item:
            raise ItemNaoEncontradoError(item_id)
        return item
