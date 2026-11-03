from fastapi import Header, HTTPException, Depends, status
from sqlmodel import Session
from app.database import obter_sessao
from app.models.cliente import Cliente

# =====================================================================
# CONCEITO DIDÁTICO: Injeção de Dependências e Autorização via Header HTTP
#
# 1. Identificação Provisória por Header (X-Cliente-Id):
#    Em arquiteturas REST, antes da introdução de tokens JWT (Bearer Tokens),
#    é comum em ambientes didáticos ou microsserviços internos utilizar um
#    cabeçalho HTTP customizado (X-*) para propagar a identidade do usuário.
#
# 2. Injeção de Dependência (Depends):
#    A dependência intercepta a requisição, extrai o valor de 'X-Cliente-Id',
#    valida a sua existência no banco de dados e fornece a entidade 'Cliente'
#    já pronta para a função da rota.
#
# 3. Tratamento de Erros Semânticos:
#    - HTTP 401 Unauthorized: Quando o header não aponta para um cliente válido.
#    - HTTP 403 Forbidden: Quando um cliente válido tenta operar sobre recursos
#      que pertencem a outro usuário (verificação de posse / ownership).
# =====================================================================


def obter_cliente_autenticado(
    x_cliente_id: int = Header(
        ...,
        alias="X-Cliente-Id",
        description="ID do cliente autenticado (controle de acesso provisório via Header HTTP)",
    ),
    sessao: Session = Depends(obter_sessao),
) -> Cliente:
    """
    Dependência FastAPI que autentica o cliente a partir do header HTTP 'X-Cliente-Id'.
    Garante que apenas clientes existentes no banco de dados possam realizar operações.
    """
    cliente = sessao.get(Cliente, x_cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Cliente não autorizado ou não localizado no banco (X-Cliente-Id={x_cliente_id}).",
        )
    return cliente
