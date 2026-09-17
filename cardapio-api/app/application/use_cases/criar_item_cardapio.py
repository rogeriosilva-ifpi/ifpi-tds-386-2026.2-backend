"""
Caso de Uso: Criar Item no Cardápio (Command).
"""
from app.application.ports.cardapio_repository import CardapioRepository
from app.domain.cardapio import ItemCardapio


class CriarItemCardapioUseCase:
    """Caso de uso para cadastrar um novo item no cardápio."""

    def __init__(self, repository: CardapioRepository) -> None:
        self.repository = repository

    async def execute(self, item: ItemCardapio) -> ItemCardapio:
        item.validar()
        return await self.repository.salvar(item)
