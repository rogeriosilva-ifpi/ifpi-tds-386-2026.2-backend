"""
Exception Handler Global para Erros de Domínio.

CONVENÇÃO ARQUITETURAL:
1. Mapeamento declarativo ErroDominio.codigo -> HTTP Status Code via dicionário estático.
2. Proibido encadeamento de `if isinstance(...)`.
3. O corpo da resposta preserva a chave `detail` para compatibilidade estrita com o frontend.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.domain.errors import ErroDominio

# Dicionário estático de mapeamento semântico
MAPA_ERRO_STATUS: dict[str, int] = {
    "ITEM_NAO_ENCONTRADO": status.HTTP_404_NOT_FOUND,
    "PRECO_INVALIDO": 422,
    "NOME_INVALIDO": 422,
    "TEMPO_PREPARO_INVALIDO": 422,
    "REGRA_VIOLADA": status.HTTP_400_BAD_REQUEST,
}


async def erro_dominio_handler(request: Request, exc: ErroDominio) -> JSONResponse:
    """Manipula qualquer exceção de domínio convertendo para resposta HTTP padronizada."""
    status_code = MAPA_ERRO_STATUS.get(
        exc.codigo,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": exc.mensagem,
            "codigo": exc.codigo,
        },
    )
