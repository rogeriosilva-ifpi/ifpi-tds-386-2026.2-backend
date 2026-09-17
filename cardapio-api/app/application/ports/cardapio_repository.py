"""
Porta de Saída para Persistência do Cardápio.

CONVENÇÃO: Definida como Protocol puro em Python, sem acoplamento com ORMs ou bancos de dados.
"""
from typing import Protocol
from app.domain.cardapio import ItemCardapio


class CardapioRepository(Protocol):
    """Contrato da porta de persistência para itens do cardápio."""

    async def listar(
        self,
        categoria: str | None = None,
        disponivel: bool | None = None,
        busca: str | None = None,
        preco_maximo: float | None = None,
    ) -> list[ItemCardapio]:
        """Retorna itens com base nos filtros fornecidos."""
        ...

    async def obter_por_id(self, item_id: int) -> ItemCardapio | None:
        """Busca um item pelo identificador único."""
        ...

    async def salvar(self, item: ItemCardapio) -> ItemCardapio:
        """Persiste um item novo ou atualiza um item existente."""
        ...

    async def remover(self, item_id: int) -> None:
        """Remove o item do repositório."""
        ...
