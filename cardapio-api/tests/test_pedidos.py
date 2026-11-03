import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.main import app
from app.database import engine
from app.models.item_cardapio import ItemCardapio
from app.models.item_pedido import ItemPedido
from app.models.pedido import Pedido, StatusPedido

# =====================================================================
# CONCEITO DIDÁTICO: Testes Automatizados para Relacionamentos e Sub-Recursos
#
# Validações essenciais:
# 1. Autenticação e autorização provisória via header 'X-Cliente-Id'.
# 2. Integridade de relacionamentos 1:N (Cliente -> Pedidos, Pedido -> Itens).
# 3. Snapshot de Preço: Imutabilidade do valor histórico do item de pedido.
# 4. Operações completas de sub-recursos REST (/pedidos/{id}/itens).
# 5. Deleção em Cascata (Cascade Delete) entre Pedido e ItensPedido.
# =====================================================================

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


def test_criar_pedido_sem_header_retorna_422(client):
    """Valida que a ausência do cabeçalho obrigatório X-Cliente-Id é rejeitada com 422."""
    resposta = client.post("/pedidos/", json={"observacoes": "Sem talher"})
    assert resposta.status_code == 422


def test_criar_pedido_com_cliente_inexistente_retorna_401(client):
    """Valida que um X-Cliente-Id não cadastrado é barrado com HTTP 401 Unauthorized."""
    resposta = client.post(
        "/pedidos/",
        headers={"X-Cliente-Id": "999999"},
        json={"observacoes": "Teste de segurança"},
    )
    assert resposta.status_code == 401
    assert "Cliente não autorizado" in resposta.json()["detail"]


def test_criar_pedido_com_itens_e_snapshot_de_preco(client):
    """
    Valida a criação de pedido com itens inline, cálculo de total e
    imutabilidade do snapshot de preço histórico.
    """
    # 1. Obter um prato comprovadamente disponível (disponivel=true)
    resposta_cardapio = client.get("/cardapio/?disponivel=true")
    assert resposta_cardapio.status_code == 200
    itens_disponiveis = resposta_cardapio.json()
    assert len(itens_disponiveis) >= 1
    prato = itens_disponiveis[0]
    prato_id = prato["id"]
    preco_original = prato["preco"]

    # 2. Criar pedido com 2 unidades deste prato
    payload = {
        "observacoes": "Entregar no 3º andar",
        "itens": [
            {
                "item_cardapio_id": prato_id,
                "quantidade": 2,
                "observacao": "Ponto da carne: ao ponto",
            }
        ],
    }
    resp_post = client.post(
        "/pedidos/",
        headers={"X-Cliente-Id": "1"},
        json=payload,
    )
    assert resp_post.status_code == 201
    pedido = resp_post.json()
    pedido_id = pedido["id"]

    assert pedido["cliente_id"] == 1
    assert pedido["status"] == "CRIADO"
    assert len(pedido["itens"]) == 1

    item_criado = pedido["itens"][0]
    assert item_criado["item_cardapio_id"] == prato_id
    assert item_criado["quantidade"] == 2
    assert item_criado["preco_unitario"] == preco_original
    assert item_criado["subtotal"] == round(preco_original * 2, 2)
    assert pedido["valor_total"] == round(preco_original * 2, 2)

    # 3. Demonstrar o Snapshot de Preço:
    # Se o restaurante alterar o preço do cardápio para R$ 100.00 amanhã:
    client.put(
        f"/cardapio/{prato_id}",
        json={"preco": 100.00},
    )

    # O pedido histórico CONTINUA com o preço de R$ 38.50 e total inalterado:
    resp_check = client.get(f"/pedidos/{pedido_id}", headers={"X-Cliente-Id": "1"})
    assert resp_check.status_code == 200
    pedido_historico = resp_check.json()
    assert pedido_historico["itens"][0]["preco_unitario"] == preco_original
    assert pedido_historico["valor_total"] == round(preco_original * 2, 2)

    # Restaurar preço para manter consistência dos demais testes
    client.put(f"/cardapio/{prato_id}", json={"preco": preco_original})


def test_adicionar_item_indisponivel_rejeitado_com_400(client):
    """Valida que adicionar um item esgotado/indisponível é rejeitado com 400."""
    # Buscar item com disponivel=False
    resp_indisp = client.get("/cardapio/?disponivel=false")
    assert resp_indisp.status_code == 200
    itens_indisp = resp_indisp.json()
    assert len(itens_indisp) >= 1
    item_esgotado = itens_indisp[0]

    # Tentar criar pedido com este item
    resp_falha = client.post(
        "/pedidos/",
        headers={"X-Cliente-Id": "1"},
        json={
            "itens": [{"item_cardapio_id": item_esgotado["id"], "quantidade": 1}]
        },
    )
    assert resp_falha.status_code == 400
    assert "indisponível" in resp_falha.json()["detail"].lower()


def test_subrecurso_fluxo_completo_itens_pedido(client):
    """
    Valida as operações completas do sub-recurso /pedidos/{id}/itens:
    1. Listar itens
    2. Adicionar novo item (POST)
    3. Atualizar quantidade do item (PUT)
    4. Remover item (DELETE)
    5. Conferir recálculo automático do valor total
    """
    # 1. Cria pedido inicial vazio
    resp_novo = client.post(
        "/pedidos/",
        headers={"X-Cliente-Id": "1"},
        json={"observacoes": "Pedido para teste de sub-recursos"},
    )
    assert resp_novo.status_code == 201
    pedido_id = resp_novo.json()["id"]
    assert resp_novo.json()["valor_total"] == 0.0

    # 2. Adicionar item 1 via sub-recurso (Suco de Caju R$ 8.50)
    resp_prato = client.get("/cardapio/?busca=Caju")
    suco = resp_prato.json()[0]

    resp_add = client.post(
        f"/pedidos/{pedido_id}/itens",
        headers={"X-Cliente-Id": "1"},
        json={"item_cardapio_id": suco["id"], "quantidade": 2},
    )
    assert resp_add.status_code == 201
    item1 = resp_add.json()
    item1_id = item1["id"]
    assert item1["subtotal"] == round(suco["preco"] * 2, 2)

    # Conferir se total do pedido subiu para R$ 17.00
    resp_p = client.get(f"/pedidos/{pedido_id}", headers={"X-Cliente-Id": "1"})
    assert resp_p.json()["valor_total"] == round(suco["preco"] * 2, 2)

    # 3. Listar itens via sub-recurso (GET /pedidos/{id}/itens)
    resp_lista = client.get(
        f"/pedidos/{pedido_id}/itens",
        headers={"X-Cliente-Id": "1"},
    )
    assert resp_lista.status_code == 200
    itens = resp_lista.json()
    assert len(itens) == 1
    assert itens[0]["nome_item"] == suco["nome"]

    # 4. Atualizar quantidade do item para 4 unidades (PUT /pedidos/{id}/itens/{item_id})
    resp_put = client.put(
        f"/pedidos/{pedido_id}/itens/{item1_id}",
        headers={"X-Cliente-Id": "1"},
        json={"quantidade": 4, "observacao": "Sem gelo"},
    )
    assert resp_put.status_code == 200
    assert resp_put.json()["quantidade"] == 4
    assert resp_put.json()["subtotal"] == round(suco["preco"] * 4, 2)

    # Total do pedido deve ser atualizado para R$ 34.00
    resp_p2 = client.get(f"/pedidos/{pedido_id}", headers={"X-Cliente-Id": "1"})
    assert resp_p2.json()["valor_total"] == round(suco["preco"] * 4, 2)

    # 5. Remover item do pedido (DELETE /pedidos/{id}/itens/{item_id})
    resp_del = client.delete(
        f"/pedidos/{pedido_id}/itens/{item1_id}",
        headers={"X-Cliente-Id": "1"},
    )
    assert resp_del.status_code == 204

    # Total do pedido deve voltar para R$ 0.00
    resp_p3 = client.get(f"/pedidos/{pedido_id}", headers={"X-Cliente-Id": "1"})
    assert resp_p3.json()["valor_total"] == 0.0
    assert len(resp_p3.json()["itens"]) == 0


def test_autorizacao_acesso_cruzado_retorna_403(client):
    """
    Valida que o Cliente 2 não pode visualizar, alterar ou excluir o pedido do Cliente 1.
    """
    # 1. Cria pedido para o Cliente 1
    resp_p1 = client.post(
        "/pedidos/",
        headers={"X-Cliente-Id": "1"},
        json={"observacoes": "Pedido particular do cliente 1"},
    )
    pedido_id = resp_p1.json()["id"]

    # 2. Cliente 2 tenta visualizar o pedido do Cliente 1
    resp_get = client.get(f"/pedidos/{pedido_id}", headers={"X-Cliente-Id": "2"})
    assert resp_get.status_code == 403
    assert "Acesso negado" in resp_get.json()["detail"]

    # 3. Cliente 2 tenta adicionar item no pedido do Cliente 1
    resp_post_item = client.post(
        f"/pedidos/{pedido_id}/itens",
        headers={"X-Cliente-Id": "2"},
        json={"item_cardapio_id": 1, "quantidade": 1},
    )
    assert resp_post_item.status_code == 403

    # 4. Cliente 2 tenta deletar o pedido do Cliente 1
    resp_del = client.delete(f"/pedidos/{pedido_id}", headers={"X-Cliente-Id": "2"})
    assert resp_del.status_code == 403


def test_cascade_delete_pedido_remove_itens(client):
    """
    Valida que ao excluir um Pedido, seus registros dependentes em ItensPedido
    são automaticamente removidos do banco (Cascade Delete).
    """
    # 1. Obter prato
    prato = client.get("/cardapio/?busca=Pudim").json()[0]

    # 2. Criar pedido temporário com item
    resp_p = client.post(
        "/pedidos/",
        headers={"X-Cliente-Id": "1"},
        json={
            "observacoes": "Pedido para teste de cascade",
            "itens": [{"item_cardapio_id": prato["id"], "quantidade": 3}],
        },
    )
    assert resp_p.status_code == 201
    pedido_id = resp_p.json()["id"]
    item_id = resp_p.json()["itens"][0]["id"]

    # 3. Verificar que o item existe no banco
    with Session(engine) as sessao:
        item_no_banco = sessao.get(ItemPedido, item_id)
        assert item_no_banco is not None

    # 4. Deletar o pedido pai (DELETE /pedidos/{id})
    resp_del = client.delete(f"/pedidos/{pedido_id}", headers={"X-Cliente-Id": "1"})
    assert resp_del.status_code == 204

    # 5. Conferir que o pedido foi removido
    resp_check = client.get(f"/pedidos/{pedido_id}", headers={"X-Cliente-Id": "1"})
    assert resp_check.status_code == 404

    # 6. Conferir que o item foi deletado em CASCATA
    with Session(engine) as sessao:
        item_apagado = sessao.get(ItemPedido, item_id)
        assert item_apagado is None


def test_subrecurso_pedidos_do_cliente(client):
    """
    Valida o sub-recurso GET /clientes/{id}/pedidos e seu controle de autorização.
    """
    # Cliente 1 consulta seus próprios pedidos -> 200 OK
    resp_ok = client.get("/clientes/1/pedidos", headers={"X-Cliente-Id": "1"})
    assert resp_ok.status_code == 200
    dados = resp_ok.json()
    assert isinstance(dados, list)
    assert len(dados) >= 1

    # Cliente 1 tenta consultar pedidos do Cliente 2 -> 403 Forbidden
    resp_barrado = client.get("/clientes/2/pedidos", headers={"X-Cliente-Id": "1"})
    assert resp_barrado.status_code == 403
    assert "Acesso negado" in resp_barrado.json()["detail"]
