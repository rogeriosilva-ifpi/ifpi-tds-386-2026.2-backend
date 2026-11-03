from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, or_

from app.database import obter_sessao
from app.dependencies import obter_cliente_autenticado
from app.models.cliente import (
    Cliente,
    ClienteCreate,
    ClienteUpdate,
    ClienteResponse,
)
from app.models.pedido import Pedido, PedidoListResponse

# =====================================================================
# CONCEITO: APIRouter (Modularização de Rotas para Clientes)
# O APIRouter agrupa os endpoints relacionados ao recurso (/clientes),
# mantendo o código organizado e isolado da lógica de cardápio e autenticação.
# =====================================================================
router = APIRouter(prefix="/clientes", tags=["Clientes"])


# =====================================================================
# CONCEITO: Consulta com Query Parameters e Filtros Dinâmicos
# Permite buscar clientes por nome, endereço, CEP ou telefone.
# Exemplo: /clientes?busca=Maria
# =====================================================================
@router.get(
    "/",
    response_model=list[ClienteResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar clientes cadastrados",
)
def listar_clientes(
    busca: str | None = Query(
        default=None,
        description="Buscar por termo no nome, endereço, CEP ou telefone/WhatsApp",
    ),
    sessao: Session = Depends(obter_sessao),
):
    instrucao = select(Cliente)

    if busca:
        termo = f"%{busca}%"
        instrucao = instrucao.where(
            or_(
                Cliente.nome.ilike(termo),
                Cliente.endereco.ilike(termo),
                Cliente.cep.ilike(termo),
                Cliente.telefone.ilike(termo),
            )
        )

    # Ordenar alfabeticamente por nome para consistência
    instrucao = instrucao.order_by(Cliente.nome)
    clientes = sessao.exec(instrucao).all()
    return clientes


# =====================================================================
# CONCEITO: Path Parameter (Parâmetro de Rota) e Tratamento 404
# O ID vem direto no caminho da URL: /clientes/10
# Se não for encontrado, lançamos semanticamente HTTPException com status 404.
# =====================================================================
@router.get(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Obter dados de um cliente por ID",
)
def obter_cliente(
    cliente_id: int,
    sessao: Session = Depends(obter_sessao),
):
    cliente = sessao.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente não localizado com id={cliente_id}.",
        )
    return cliente


# =====================================================================
# CONCEITO: Criação de Recurso com POST e Status 201 Created
# 1. Recebe os dados validados pelo schema ClienteCreate (obrigatoriedade de CEP, número, tel).
# 2. Converte para o modelo Cliente da tabela.
# 3. Executa sessao.add() e sessao.commit() para persistir no banco.
# 4. Usa sessao.refresh() para carregar o 'id' gerado pelo banco.
# =====================================================================
@router.post(
    "/",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo cliente",
)
def criar_cliente(
    dados: ClienteCreate,
    sessao: Session = Depends(obter_sessao),
):
    novo_cliente = Cliente.model_validate(dados)
    sessao.add(novo_cliente)
    sessao.commit()
    sessao.refresh(novo_cliente)
    return novo_cliente


# =====================================================================
# CONCEITO: Atualização de Recurso com PUT (Edição)
# Localiza o registro existente no banco e atualiza apenas os campos enviados.
# =====================================================================
@router.put(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Atualizar dados de um cliente existente",
)
def atualizar_cliente(
    cliente_id: int,
    dados: ClienteUpdate,
    sessao: Session = Depends(obter_sessao),
):
    cliente_banco = sessao.get(Cliente, cliente_id)
    if not cliente_banco:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente não localizado com id={cliente_id}.",
        )

    # exclude_unset=True ignora campos que o cliente não enviou no payload
    dados_atualizados = dados.model_dump(exclude_unset=True)
    for campo, valor in dados_atualizados.items():
        setattr(cliente_banco, campo, valor)

    sessao.add(cliente_banco)
    sessao.commit()
    sessao.refresh(cliente_banco)
    return cliente_banco


# =====================================================================
# CONCEITO: Exclusão com DELETE e Status 204 No Content
# Sucesso em DELETE normalmente não precisa retornar corpo de resposta (HTTP 204).
# =====================================================================
@router.delete(
    "/{cliente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover cliente cadastrado",
)
def remover_cliente(
    cliente_id: int,
    sessao: Session = Depends(obter_sessao),
):
    cliente_banco = sessao.get(Cliente, cliente_id)
    if not cliente_banco:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente não localizado com id={cliente_id}.",
        )

    sessao.delete(cliente_banco)
    sessao.commit()
    return None


# =====================================================================
# CONCEITO: Sub-Recurso Hierárquico (/clientes/{cliente_id}/pedidos)
# Expõe os pedidos vinculados diretamente à entidade Cliente pai.
# Exige o header 'X-Cliente-Id' e valida se o cliente autenticado é o dono.
# =====================================================================
@router.get(
    "/{cliente_id}/pedidos",
    response_model=list[PedidoListResponse],
    summary="Sub-recurso: Listar pedidos de um cliente específico",
)
def listar_pedidos_do_cliente(
    cliente_id: int,
    cliente_logado: Cliente = Depends(obter_cliente_autenticado),
    sessao: Session = Depends(obter_sessao),
):
    cliente_banco = sessao.get(Cliente, cliente_id)
    if not cliente_banco:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente não localizado com id={cliente_id}.",
        )

    # Controle de Autorização: o cliente logado só pode ver seus próprios pedidos
    if cliente_id != cliente_logado.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acesso negado: você não tem permissão para visualizar pedidos do cliente ID={cliente_id}.",
        )

    instrucao = (
        select(Pedido)
        .where(Pedido.cliente_id == cliente_id)
        .order_by(Pedido.id.desc())
    )
    pedidos = sessao.exec(instrucao).all()

    return [
        PedidoListResponse(
            id=p.id,
            cliente_id=p.cliente_id,
            data_hora=p.data_hora,
            status=p.status,
            valor_total=p.valor_total,
            total_itens=len(p.itens),
        )
        for p in pedidos
    ]

