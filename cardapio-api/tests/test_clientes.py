import pytest
from fastapi.testclient import TestClient
from app.main import app

# =====================================================================
# CONCEITO: Testes Automatizados para Rotas de Clientes
# Validação completa das operações fundamentais (CRUD) com foco nas
# regras de negócio, dados de entrega e tratamento semântico de erros HTTP.
# =====================================================================
@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


def test_listar_clientes(client):
    """Valida se a listagem de clientes retorna uma lista e código HTTP 200."""
    resposta = client.get("/clientes/")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert isinstance(dados, list)
    assert len(dados) >= 1  # Graças ao seed automático
    primeiro = dados[0]
    assert "id" in primeiro
    assert "nome" in primeiro
    assert "endereco" in primeiro
    assert "cep" in primeiro
    assert "numero" in primeiro
    assert "telefone" in primeiro


def test_filtrar_clientes_por_busca(client):
    """Valida o filtro dinâmico de clientes por termo de busca."""
    resposta = client.get("/clientes/?busca=Silva")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert isinstance(dados, list)
    assert any("Silva" in c["nome"] for c in dados)


def test_criar_e_consultar_cliente(client):
    """Valida o ciclo completo de criação (POST 201) e consulta por ID (GET 200)."""
    novo_cliente = {
        "nome": "Carlos Eduardo",
        "data_nascimento": "1988-12-05",
        "endereco": "Av. Raul Lopes, Ininga",
        "cep": "64049-540",
        "numero": "890",
        "telefone": "86991112233",
    }

    # 1. Enviar requisição POST com corpo JSON
    resposta_post = client.post("/clientes/", json=novo_cliente)
    assert resposta_post.status_code == 201
    cliente_criado = resposta_post.json()
    assert "id" in cliente_criado
    assert cliente_criado["nome"] == novo_cliente["nome"]
    assert cliente_criado["data_nascimento"] == novo_cliente["data_nascimento"]
    assert cliente_criado["endereco"] == novo_cliente["endereco"]
    assert cliente_criado["cep"] == novo_cliente["cep"]
    assert cliente_criado["numero"] == novo_cliente["numero"]
    assert cliente_criado["telefone"] == novo_cliente["telefone"]
    cliente_id = cliente_criado["id"]

    # 2. Consultar o cliente recém-criado por ID
    resposta_get = client.get(f"/clientes/{cliente_id}")
    assert resposta_get.status_code == 200
    cliente_buscado = resposta_get.json()
    assert cliente_buscado["id"] == cliente_id
    assert cliente_buscado["nome"] == novo_cliente["nome"]
    assert cliente_buscado["telefone"] == novo_cliente["telefone"]


def test_validacao_campos_obrigatorios_para_entrega(client):
    """Valida que a omissão de campos vitais para entrega (telefone, CEP, número) é rejeitada com 422."""
    # Sem telefone
    resp_sem_telefone = client.post("/clientes/", json={
        "nome": "Incompleto Silva",
        "endereco": "Rua Teste",
        "cep": "64000-000",
        "numero": "10",
    })
    assert resp_sem_telefone.status_code == 422

    # Sem CEP
    resp_sem_cep = client.post("/clientes/", json={
        "nome": "Incompleto Silva",
        "endereco": "Rua Teste",
        "numero": "10",
        "telefone": "86999990000",
    })
    assert resp_sem_cep.status_code == 422

    # Sem número
    resp_sem_numero = client.post("/clientes/", json={
        "nome": "Incompleto Silva",
        "endereco": "Rua Teste",
        "cep": "64000-000",
        "telefone": "86999990000",
    })
    assert resp_sem_numero.status_code == 422


def test_cliente_nao_encontrado_retorna_404(client):
    """Valida se buscar um ID inexistente retorna status HTTP 404."""
    resposta = client.get("/clientes/999999")
    assert resposta.status_code == 404
    assert "detail" in resposta.json()


def test_atualizar_e_excluir_cliente(client):
    """Valida a atualização parcial via PUT e exclusão com DELETE (204 No Content)."""
    # 1. Cria cliente temporário
    cliente = {
        "nome": "Cliente Temporario",
        "endereco": "Rua Provisoria",
        "cep": "64000-111",
        "numero": "50",
        "telefone": "86988887777",
    }
    resp_post = client.post("/clientes/", json=cliente)
    assert resp_post.status_code == 201
    cliente_id = resp_post.json()["id"]

    # 2. Atualiza dados do cliente com PUT
    resp_put = client.put(f"/clientes/{cliente_id}", json={
        "endereco": "Rua Atualizada Definitiva",
        "numero": "50-A",
    })
    assert resp_put.status_code == 200
    dados_atualizados = resp_put.json()
    assert dados_atualizados["endereco"] == "Rua Atualizada Definitiva"
    assert dados_atualizados["numero"] == "50-A"
    assert dados_atualizados["nome"] == cliente["nome"]  # Mantém dados inalterados

    # 3. Exclui cliente com DELETE
    resp_del = client.delete(f"/clientes/{cliente_id}")
    assert resp_del.status_code == 204

    # 4. Confirma exclusão (404)
    resp_check = client.get(f"/clientes/{cliente_id}")
    assert resp_check.status_code == 404
