"""
Schemas Pydantic / SQLModel para validação de entrada e serialização de saída (DTOs).

CONCEITO: Re-exporta a hierarquia canônica de app.domain.cardapio, eliminando duplicações
de atributos e mantendo compatibilidade de importação em toda a aplicação.
"""
from app.domain.cardapio import (
    ItemCardapioBase,
    ItemCardapioCreate,
    ItemCardapioUpdate,
    ItemCardapioResponse,
)

__all__ = [
    "ItemCardapioBase",
    "ItemCardapioCreate",
    "ItemCardapioUpdate",
    "ItemCardapioResponse",
]
