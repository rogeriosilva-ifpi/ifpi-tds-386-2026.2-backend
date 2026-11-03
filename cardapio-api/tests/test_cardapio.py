import pytest
from fastapi.testclient import TestClient
from app.main import app

# =====================================================================
# CONCEITO: Testes Automatizados com TestClient e Lifespan
# Usar o TestClient dentro de um context manager (with) garante que
# o evento de ciclo de vida (lifespan) seja executado, criando as tabelas
# e executando o seed inicial no banco SQLite.
# =====================================================================
@pytest.fixture(scope="session")
def cliente():
    with TestClient(app) as c:
        yield c


def test_status_raiz(cliente):
    """Valida se a rota raiz responde com status HTTP 200 e mensagem esperada."""
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert "mensagem" in dados
    assert "versao" in dados


def test_listar_cardapio(cliente):
    """Valida se a listagem de pratos retorna uma lista e código 200."""
    resposta = cliente.get("/cardapio/")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert isinstance(dados, list)
    assert len(dados) >= 1  # Graças ao seed automático


def test_criar_e_consultar_item(cliente):
    """Valida o ciclo completo de criação (POST 201) e consulta por ID (GET 200)."""
    novo_item = {
        "nome": "Bolo de Rolo com Sorvete",
        "descricao": "Fatia de bolo de rolo pernambucano acompanhada de sorvete de creme.",
        "preco": 16.50,
        "categoria": "Sobremesas",
        "disponivel": True,
        "tempo_preparo_minutos": 10,
    }

    # 1. Enviar requisição POST com corpo JSON
    resposta_post = cliente.post("/cardapio/", json=novo_item)
    assert resposta_post.status_code == 201
    item_criado = resposta_post.json()
    assert "id" in item_criado
    assert item_criado["nome"] == novo_item["nome"]
    assert item_criado["tempo_preparo_minutos"] == 10
    item_id = item_criado["id"]

    # 2. Consultar o item recém-criado por ID
    resposta_get = cliente.get(f"/cardapio/{item_id}")
    assert resposta_get.status_code == 200
    item_buscado = resposta_get.json()
    assert item_buscado["id"] == item_id
    assert item_buscado["preco"] == 16.50
    assert item_buscado["tempo_preparo_minutos"] == 10


def test_alternar_disponibilidade(cliente):
    """Valida a atualização parcial rápida (PATCH)."""
    # Usando o item 1 existente do seed
    resposta_antes = cliente.get("/cardapio/1")
    assert resposta_antes.status_code == 200
    status_anterior = resposta_antes.json()["disponivel"]

    resposta_patch = cliente.patch("/cardapio/1/disponibilidade")
    assert resposta_patch.status_code == 200
    assert resposta_patch.json()["disponivel"] is not status_anterior


def test_item_nao_encontrado_retorna_404(cliente):
    """Valida se buscar um ID inexistente retorna adequadamente o status HTTP 404."""
    resposta = cliente.get("/cardapio/999999")
    assert resposta.status_code == 404
    assert "detail" in resposta.json()


def test_atualizar_e_excluir_item(cliente):
    """Valida a atualização completa com PUT e exclusão com DELETE (204 No Content)."""
    # 1. Cria um item para teste de exclusão
    item = {
        "nome": "Item Temporario",
        "descricao": "Sera excluido",
        "preco": 5.0,
        "categoria": "Bebidas",
        "disponivel": True,
    }
    resp_post = cliente.post("/cardapio/", json=item)
    assert resp_post.status_code == 201
    item_id = resp_post.json()["id"]

    # 2. Atualiza o item com PUT
    resp_put = cliente.put(f"/cardapio/{item_id}", json={"preco": 7.50, "nome": "Item Atualizado"})
    assert resp_put.status_code == 200
    assert resp_put.json()["preco"] == 7.50
    assert resp_put.json()["nome"] == "Item Atualizado"

    # 3. Exclui o item com DELETE
    resp_del = cliente.delete(f"/cardapio/{item_id}")
    assert resp_del.status_code == 204

    # 4. Confirma que o item não existe mais (404)
    resp_check = cliente.get(f"/cardapio/{item_id}")
    assert resp_check.status_code == 404

