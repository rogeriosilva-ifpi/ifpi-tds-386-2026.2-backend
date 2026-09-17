"""
Caso de Uso: Listar Itens do Cardápio (Query).
"""
from app.application.ports.cardapio_repository import CardapioRepository
from app.domain.cardapio import ItemCardapio


class ListarCardapioUseCase:
    """Caso de uso para consulta de itens do cardápio com filtros dinâmicos."""

    def __init__(self, repository: CardapioRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        categoria: str | None = None,
        disponivel: bool | None = None,
        busca: str | None = None,
        preco_maximo: float | None = None,
    ) -> list[ItemCardapio]:
        return await self.repository.listar(
            categoria=categoria,
            disponivel=disponivel,
            busca=busca,
            preco_maximo=preco_maximo,
        )
