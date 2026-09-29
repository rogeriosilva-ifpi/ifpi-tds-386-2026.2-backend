from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import obter_sessao
from app.dependencies import obter_cliente_autenticado
from app.models.cliente import Cliente
from app.models.item_cardapio import ItemCardapio
from app.models.item_pedido import (
    ItemPedido,
    ItemPedidoCreate,
    ItemPedidoUpdate,
    ItemPedidoResponse,
)
from app.models.pedido import (
    Pedido,
    PedidoCreate,
    PedidoUpdateStatus,
    PedidoResponse,
    PedidoListResponse,
    StatusPedido,
)

# =====================================================================
# CONCEITO DIDÁTICO: APIRouter para Pedidos e Sub-Recursos (/pedidos)
#
# 1. Hierarquia de Recursos RESTful:
#    - Recurso Principal: /pedidos
#    - Sub-Recurso Aninhado: /pedidos/{pedido_id}/itens
#    Representa que um item de pedido só faz sentido existindo DENTRO
#    do contexto de um pedido específico.
#
# 2. Autorização e Posse (Ownership):
#    O header 'X-Cliente-Id' identifica o usuário logado. Toda operação
#    valida se o pedido pertence àquele cliente. Se não pertencer:
#    HTTP 403 Forbidden.
#
# 3. Snapshot de Preço:
#    Ao incluir itens, o valor atual de 'ItemCardapio.preco' é gravado
#    em 'ItemPedido.preco_unitario'.
#
# 4. Transações Atômicas e Atualização de Total:
#    Qualquer inclusão, alteração ou exclusão de item recalcula o total
#    do pedido pai dentro da mesma transação de banco.
# =====================================================================

router = APIRouter(prefix="/pedidos", tags=["Pedidos e Sub-Recursos"])


# ---------------------------------------------------------------------
# FUNÇÕES AUXILIARES DIDÁTICAS
# ---------------------------------------------------------------------

def verificar_autorizacao_pedido(pedido: Pedido, cliente: Cliente) -> None:
    """Verifica se o cliente autenticado é o proprietário do pedido."""
    if pedido.cliente_id != cliente.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acesso negado: o pedido ID={pedido.id} pertence a outro cliente.",
        )


def recalcular_total_pedido(pedido: Pedido, sessao: Session) -> float:
    """Recalcula a soma dos subtotais dos itens e atualiza o pedido pai."""
    instrucao = select(ItemPedido).where(ItemPedido.pedido_id == pedido.id)
    itens = sessao.exec(instrucao).all()
    total = sum(item.preco_unitario * item.quantidade for item in itens)
    pedido.valor_total = round(total, 2)
    sessao.add(pedido)
    sessao.commit()
    sessao.refresh(pedido)
    return pedido.valor_total


def montar_item_response(item: ItemPedido, sessao: Session) -> ItemPedidoResponse:
    """Gera o schema ItemPedidoResponse enriquecido com o nome do prato."""
    item_cardapio = sessao.get(ItemCardapio, item.item_cardapio_id)
    nome_item = item_cardapio.nome if item_cardapio else "Item do Cardápio"
    return ItemPedidoResponse(
        id=item.id,
        pedido_id=item.pedido_id,
        item_cardapio_id=item.item_cardapio_id,
        nome_item=nome_item,
        preco_unitario=item.preco_unitario,
        quantidade=item.quantidade,
        observacao=item.observacao,
    )


def montar_pedido_response(pedido: Pedido, sessao: Session) -> PedidoResponse:
    """Gera o schema detalhado PedidoResponse contendo seus itens."""
    itens_resp = [montar_item_response(it, sessao) for it in pedido.itens]
    return PedidoResponse(
        id=pedido.id,
        cliente_id=pedido.cliente_id,
        data_hora=pedido.data_hora,
        status=pedido.status,
        observacoes=pedido.observacoes,
        valor_total=pedido.valor_total,
        itens=itens_resp,
    )


# =====================================================================
# ENDPOINTS PRINCIPAIS: /pedidos
# =====================================================================

@router.post(
    "/",
    response_model=PedidoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo pedido para o cliente autenticado",
)
def criar_pedido(
    dados: PedidoCreate,
    cliente: Cliente = Depends(obter_cliente_autenticado),
    sessao: Session = Depends(obter_sessao),
):
    """
    Cria um novo pedido associado automaticamente ao cliente do header X-Cliente-Id.
    Permite opcionalmente enviar uma lista inicial de itens ('itens').
    """
    novo_pedido = Pedido(
        cliente_id=cliente.id,
        observacoes=dados.observacoes,
        status=StatusPedido.CRIADO,
        valor_total=0.0,
    )
    sessao.add(novo_pedido)
    sessao.commit()
    sessao.refresh(novo_pedido)

    # Processar itens enviados no corpo
    if dados.itens:
        for item_in in dados.itens:
            prato = sessao.get(ItemCardapio, item_in.item_cardapio_id)
            if not prato:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item de cardápio ID={item_in.item_cardapio_id} não encontrado.",
                )
            if not prato.disponivel:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"O prato '{prato.nome}' está indisponível para pedidos.",
                )

            item_pedido = ItemPedido(
                pedido_id=novo_pedido.id,
                item_cardapio_id=prato.id,
                quantidade=item_in.quantidade,
                observacao=item_in.observacao,
                preco_unitario=prato.preco,  # Snapshot de preço
            )
            sessao.add(item_pedido)

        sessao.commit()
        recalcular_total_pedido(novo_pedido, sessao)

    sessao.refresh(novo_pedido)
    return montar_pedido_response(novo_pedido, sessao)


@router.get(
    "/",
    response_model=list[PedidoListResponse],
    summary="Listar pedidos do cliente autenticado",
)
def listar_pedidos(
    cliente: Cliente = Depends(obter_cliente_autenticado),
    sessao: Session = Depends(obter_sessao),
):
    """Retorna o histórico resumido de todos os pedidos pertencentes ao cliente autenticado."""
    instrucao = (
        select(Pedido)
        .where(Pedido.cliente_id == cliente.id)
        .order_by(Pedido.id.desc())
    )
    pedidos = sessao.exec(instrucao).all()

    resposta = []
    for p in pedidos:
        resposta.append(
            PedidoListResponse(
                id=p.id,
                cliente_id=p.cliente_id,
                data_hora=p.data_hora,
                status=p.status,
                valor_total=p.valor_total,
                total_itens=len(p.itens),
            )
        )
    return resposta


@router.get(
    "/{pedido_id}",
    response_model=PedidoResponse,
    summary="Obter detalhes completos de um pedido",
)
def obter_pedido(
    pedido_id: int,
    cliente: Cliente = Depends(obter_cliente_autenticado),
    sessao: Session = Depends(obter_sessao),
):
    """Consulta os dados e itens de um pedido específico com verificação de autorização."""
    pedido = sessao.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido ID={pedido_id} não encontrado.",
        )
    verificar_autorizacao_pedido(pedido, cliente)
    return montar_pedido_response(pedido, sessao)


@router.patch(
    "/{pedido_id}/status",
    response_model=PedidoResponse,
    summary="Atualizar status de um pedido",
)
def atualizar_status_pedido(
    pedido_id: int,
    dados: PedidoUpdateStatus,
    cliente: Cliente = Depends(obter_cliente_autenticado),
    sessao: Session = Depends(obter_sessao),
):
    """
    Atualiza a situação do pedido na máquina de estados.
    Impede cancelamento de pedidos já em preparo ou entregues.
    """
    pedido = sessao.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido ID={pedido_id} não encontrado.",
        )
    verificar_autorizacao_pedido(pedido, cliente)

    # Regra de negócio: cliente só cancela pedidos ainda não iniciados
    if dados.status == StatusPedido.CANCELADO and pedido.status in [
        StatusPedido.EM_PREPARO,
        StatusPedido.PRONTO,
        StatusPedido.ENTREGUE,
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é permitido cancelar pedido no status '{pedido.status}'.",
        )

    pedido.status = dados.status
    sessao.add(pedido)
    sessao.commit()
    sessao.refresh(pedido)
    return montar_pedido_response(pedido, sessao)


@router.delete(
    "/{pedido_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover pedido (Exclusão em Cascata)",
)
def remover_pedido(
    pedido_id: int,
    cliente: Cliente = Depends(obter_cliente_autenticado),
    sessao: Session = Depends(obter_sessao),
):
    """
    Remove um pedido e todos os seus itens associados (Cascade Delete).
    Apenas pedidos nos status CRIADO ou CANCELADO podem ser removidos.
    """
    pedido = sessao.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido ID={pedido_id} não encontrado.",
        )
    verificar_autorizacao_pedido(pedido, cliente)

    if pedido.status not in [StatusPedido.CRIADO, StatusPedido.CANCELADO]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Apenas pedidos com status CRIADO ou CANCELADO podem ser excluídos. Status atual: {pedido.status}.",
        )

    sessao.delete(pedido)
    sessao.commit()
    return None


# =====================================================================
# SUB-RECURSOS: /pedidos/{pedido_id}/itens
# =====================================================================

@router.get(
    "/{pedido_id}/itens",
    response_model=list[ItemPedidoResponse],
    summary="Sub-recurso: Listar itens de um pedido",
)
def listar_itens_pedido(
    pedido_id: int,
    cliente: Cliente = Depends(obter_cliente_autenticado),
    sessao: Session = Depends(obter_sessao),
):
    """Lista todos os itens vinculados ao pedido especificado."""
    pedido = sessao.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido ID={pedido_id} não encontrado.",
        )
    verificar_autorizacao_pedido(pedido, cliente)

    return [montar_item_response(it, sessao) for it in pedido.itens]


@router.post(
    "/{pedido_id}/itens",
    response_model=ItemPedidoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sub-recurso: Adicionar item ao pedido",
)
def adicionar_item_ao_pedido(
    pedido_id: int,
    dados: ItemPedidoCreate,
    cliente: Cliente = Depends(obter_cliente_autenticado),
    sessao: Session = Depends(obter_sessao),
):
    """
    Adiciona um novo item ao pedido existente.
    Congela o preço do cardápio e recalcula o total do pedido.
    """
    pedido = sessao.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido ID={pedido_id} não encontrado.",
        )
    verificar_autorizacao_pedido(pedido, cliente)

    if pedido.status not in [StatusPedido.CRIADO, StatusPedido.CONFIRMADO]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é permitido adicionar itens a um pedido no status '{pedido.status}'.",
        )

    prato = sessao.get(ItemCardapio, dados.item_cardapio_id)
    if not prato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item de cardápio ID={dados.item_cardapio_id} não encontrado.",
        )
    if not prato.disponivel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"O item '{prato.nome}' está indisponível para pedidos.",
        )

    novo_item = ItemPedido(
        pedido_id=pedido.id,
        item_cardapio_id=prato.id,
        quantidade=dados.quantidade,
        observacao=dados.observacao,
        preco_unitario=prato.preco,  # Snapshot de preço
    )
    sessao.add(novo_item)
    sessao.commit()
    sessao.refresh(novo_item)

    # Recalcula e atualiza o total no pedido pai
    recalcular_total_pedido(pedido, sessao)

    return montar_item_response(novo_item, sessao)


@router.get(
    "/{pedido_id}/itens/{item_id}",
    response_model=ItemPedidoResponse,
    summary="Sub-recurso: Obter detalhe de um item específico no pedido",
)
def obter_item_do_pedido(
    pedido_id: int,
    item_id: int,
    cliente: Cliente = Depends(obter_cliente_autenticado),
    sessao: Session = Depends(obter_sessao),
):
    """Retorna detalhes de um item específico pertencente ao pedido pai."""
    pedido = sessao.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido ID={pedido_id} não encontrado.",
        )
    verificar_autorizacao_pedido(pedido, cliente)

    item = sessao.get(ItemPedido, item_id)
    if not item or item.pedido_id != pedido_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item ID={item_id} não encontrado no pedido ID={pedido_id}.",
        )

    return montar_item_response(item, sessao)


@router.put(
    "/{pedido_id}/itens/{item_id}",
    response_model=ItemPedidoResponse,
    summary="Sub-recurso: Atualizar quantidade ou observação do item",
)
def atualizar_item_do_pedido(
    pedido_id: int,
    item_id: int,
    dados: ItemPedidoUpdate,
    cliente: Cliente = Depends(obter_cliente_autenticado),
    sessao: Session = Depends(obter_sessao),
):
    """
    Atualiza atributos de um item já adicionado ao pedido.
    Se a quantidade for alterada, o valor total do pedido é recalculado.
    """
    pedido = sessao.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido ID={pedido_id} não encontrado.",
        )
    verificar_autorizacao_pedido(pedido, cliente)

    if pedido.status not in [StatusPedido.CRIADO, StatusPedido.CONFIRMADO]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é permitido alterar itens de um pedido no status '{pedido.status}'.",
        )

    item = sessao.get(ItemPedido, item_id)
    if not item or item.pedido_id != pedido_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item ID={item_id} não encontrado no pedido ID={pedido_id}.",
        )

    dados_atualizacao = dados.model_dump(exclude_unset=True)
    for campo, valor in dados_atualizacao.items():
        setattr(item, campo, valor)

    sessao.add(item)
    sessao.commit()
    sessao.refresh(item)

    # Recalcula o total consolidado
    recalcular_total_pedido(pedido, sessao)

    return montar_item_response(item, sessao)


@router.delete(
    "/{pedido_id}/itens/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Sub-recurso: Remover item do pedido",
)
def remover_item_do_pedido(
    pedido_id: int,
    item_id: int,
    cliente: Cliente = Depends(obter_cliente_autenticado),
    sessao: Session = Depends(obter_sessao),
):
    """Remove um item do pedido e atualiza automaticamente o valor total do pedido pai."""
    pedido = sessao.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido ID={pedido_id} não encontrado.",
        )
    verificar_autorizacao_pedido(pedido, cliente)

    if pedido.status not in [StatusPedido.CRIADO, StatusPedido.CONFIRMADO]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é permitido remover itens de um pedido no status '{pedido.status}'.",
        )

    item = sessao.get(ItemPedido, item_id)
    if not item or item.pedido_id != pedido_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item ID={item_id} não encontrado no pedido ID={pedido_id}.",
        )

    sessao.delete(item)
    sessao.commit()

    # Recalcula o total após a exclusão do item
    recalcular_total_pedido(pedido, sessao)
    return None
