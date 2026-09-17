import pytest
from fastapi.testclient import TestClient
from app.main import app

# =====================================================================
# CONCEITO: Testes Automatizados com TestClient e Lifespan
# Usar o TestClient dentro de um context manager (with) garante que
# o evento de ciclo de vida (lifespan) seja executado, criando as tabelas
# e executando o seed inicial no banco SQLite.
# =====================================================================


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


# =====================================================================
# REDE DE SEGURANÇA (FASE 0): Testes de Caracterização Adicionais
# =====================================================================

def test_listar_cardapio_filtro_categoria(cliente):
    """Valida se o filtro por categoria restringe os resultados corretamente."""
    resposta = cliente.get("/cardapio/?categoria=Bebidas")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert len(dados) >= 1
    for item in dados:
        assert item["categoria"] == "Bebidas"


def test_listar_cardapio_filtro_disponivel(cliente):
    """Valida se o filtro por disponibilidade (esgotado/disponível) funciona."""
    resposta = cliente.get("/cardapio/?disponivel=false")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert len(dados) >= 1
    for item in dados:
        assert item["disponivel"] is False


def test_listar_cardapio_filtro_busca(cliente):
    """Valida se o termo de busca é localizado no nome ou descrição (case-insensitive)."""
    resposta = cliente.get("/cardapio/?busca=caju")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert len(dados) >= 1
    for item in dados:
        termo_no_nome = "caju" in item["nome"].lower()
        termo_na_desc = item["descricao"] and "caju" in item["descricao"].lower()
        assert termo_no_nome or termo_na_desc


def test_listar_cardapio_filtro_preco_maximo(cliente):
    """Valida se o filtro por preco_maximo restringe os itens até o teto estipulado."""
    teto = 15.00
    resposta = cliente.get(f"/cardapio/?preco_maximo={teto}")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert len(dados) >= 1
    for item in dados:
        assert item["preco"] <= teto


def test_listar_cardapio_ordenacao_alfabetica(cliente):
    """Valida se a listagem padrão retorna os itens ordenados alfabeticamente por nome."""
    resposta = cliente.get("/cardapio/")
    assert resposta.status_code == 200
    dados = resposta.json()
    nomes = [item["nome"] for item in dados]
    assert nomes == sorted(nomes)


def test_put_item_nao_encontrado_retorna_404(cliente):
    """Valida que atualizar um item inexistente via PUT retorna 404 e detail semântico."""
    resposta = cliente.put("/cardapio/999999", json={"preco": 20.0})
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Item não localizado com id=999999."


def test_patch_disponibilidade_item_nao_encontrado_retorna_404(cliente):
    """Valida que alternar disponibilidade de ID inexistente retorna 404."""
    resposta = cliente.patch("/cardapio/999999/disponibilidade")
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Item não localizado com id=999999."


def test_delete_item_nao_encontrado_retorna_404(cliente):
    """Valida que excluir ID inexistente via DELETE retorna 404."""
    resposta = cliente.delete("/cardapio/999999")
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Item não localizado com id=999999."


def test_validacao_preco_invalido_retorna_422(cliente):
    """Valida que cadastrar item com preço <= 0 é rejeitado com status 422."""
    item_invalido = {
        "nome": "Prato com Preco Zero",
        "preco": 0.0,
        "categoria": "Lanches",
    }
    resposta = cliente.post("/cardapio/", json=item_invalido)
    assert resposta.status_code == 422

    item_negativo = {
        "nome": "Prato Preco Negativo",
        "preco": -10.0,
        "categoria": "Lanches",
    }
    resposta_negativa = cliente.post("/cardapio/", json=item_negativo)
    assert resposta_negativa.status_code == 422


def test_validacao_nome_curto_retorna_422(cliente):
    """Valida que nome com menos de 2 caracteres é rejeitado com status 422."""
    item_invalido = {
        "nome": "X",
        "preco": 10.0,
    }
    resposta = cliente.post("/cardapio/", json=item_invalido)
    assert resposta.status_code == 422


def test_validacao_tempo_preparo_invalido_retorna_422(cliente):
    """Valida que tempo de preparo < 1 minuto é rejeitado com status 422."""
    item_invalido = {
        "nome": "Item Tempo Zero",
        "preco": 10.0,
        "tempo_preparo_minutos": 0,
    }
    resposta = cliente.post("/cardapio/", json=item_invalido)
    assert resposta.status_code == 422


def test_rotas_auxiliares_da_aplicacao(cliente):
    """Garante que endpoints informativos e didáticos mantêm seus comportamentos."""
    resp_hello = cliente.get("/hello")
    assert resp_hello.status_code == 200
    assert "Rogério Silva" in resp_hello.json()["mensagem"]

    resp_clientes = cliente.get("/clientes/")
    assert resp_clientes.status_code == 200
    assert isinstance(resp_clientes.json(), list)

    resp_cliente_id = cliente.get("/clientes/10")
    assert resp_cliente_id.status_code == 200
    assert resp_cliente_id.json() == "Cliente de ID=10"

    resp_auth_me = cliente.get("/auth/me")
    assert resp_auth_me.status_code == 200
    assert resp_auth_me.json() == "Sou Rogério"

    resp_auth_login = cliente.post("/auth/login")
    assert resp_auth_login.status_code == 200
    assert resp_auth_login.json() == "Autenticado com sucesso!"

