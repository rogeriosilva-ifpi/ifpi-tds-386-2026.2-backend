"""
Caso de Uso: Alternar Disponibilidade de Item do Cardápio (Command).
"""
from app.application.ports.cardapio_repository import CardapioRepository
from app.domain.cardapio import ItemCardapio
from app.domain.errors import ItemNaoEncontradoError


class AlternarDisponibilidadeUseCase:
    """Caso de uso para inversão rápida de disponibilidade (disponível / esgotado)."""

    def __init__(self, repository: CardapioRepository) -> None:
        self.repository = repository

    async def execute(self, item_id: int) -> ItemCardapio:
        item = await self.repository.obter_por_id(item_id)
        if not item:
            raise ItemNaoEncontradoError(item_id)

        item.alternar_disponibilidade()
        return await self.repository.salvar(item)
