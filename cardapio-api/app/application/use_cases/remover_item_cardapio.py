"""
Caso de Uso: Remover Item do Cardápio (Command).
"""
from app.application.ports.cardapio_repository import CardapioRepository
from app.domain.errors import ItemNaoEncontradoError


class RemoverItemCardapioUseCase:
    """Caso de uso para exclusão de um item existente por ID."""

    def __init__(self, repository: CardapioRepository) -> None:
        self.repository = repository

    async def execute(self, item_id: int) -> None:
        item = await self.repository.obter_por_id(item_id)
        if not item:
            raise ItemNaoEncontradoError(item_id)

        await self.repository.remover(item_id)
