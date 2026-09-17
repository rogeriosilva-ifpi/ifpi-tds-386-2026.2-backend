"""Roteadores da API."""
from app.api.routers.cardapio_router import router as cardapio_router
from app.api.routers.auth_router import router as auth_router
from app.api.routers.clientes_router import router as clientes_router

__all__ = ["cardapio_router", "auth_router", "clientes_router"]
