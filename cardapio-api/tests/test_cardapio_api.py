import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.api.routers import cardapio_router, auth_router, clientes_router
from app.api.exception_handlers import erro_dominio_handler
from app.domain.errors import ErroDominio
from app.database import obter_sessao
from app.infrastructure.seed import popular_seed_se_vazio
from tests.conftest import test_engine

# Cria uma instância da aplicação FastAPI configurada com a nova arquitetura
api_app = FastAPI()
api_app.add_exception_handler(ErroDominio, erro_dominio_handler)  # type: ignore[arg-type]
api_app.include_router(cardapio_router)
api_app.include_router(auth_router)
api_app.include_router(clientes_router)


@pytest.fixture
def cliente_api():
    """TestClient apontando diretamente para os adaptadores da nova camada de API."""
    def _override():
        with Session(test_engine) as sessao:
            yield sessao

    api_app.dependency_overrides[obter_sessao] = _override
    with Session(test_engine) as sessao:
        popular_seed_se_vazio(sessao)

    with TestClient(api_app) as client:
        yield client
    api_app.dependency_overrides.clear()


def test_api_listar_cardapio_completo(cliente_api):
    resposta = cliente_api.get("/cardapio/")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert len(dados) == 5
    assert dados[0]["nome"] <= dados[1]["nome"]


def test_api_consultar_por_id_existente(cliente_api):
    resposta = cliente_api.get("/cardapio/1")
    assert resposta.status_code == 200
    assert resposta.json()["id"] == 1


def test_api_consultar_por_id_inexistente_retorna_404_com_codigo(cliente_api):
    resposta = cliente_api.get("/cardapio/99999")
    assert resposta.status_code == 404
    dados = resposta.json()
    assert dados["detail"] == "Item não localizado com id=99999."
    assert dados["codigo"] == "ITEM_NAO_ENCONTRADO"


def test_api_criar_item_cardapio(cliente_api):
    payload = {
        "nome": "Suco de Graviola",
        "descricao": "Suco natural 400ml",
        "preco": 9.00,
        "categoria": "Bebidas",
        "disponivel": True,
        "tempo_preparo_minutos": 5,
    }
    resposta = cliente_api.post("/cardapio/", json=payload)
    assert resposta.status_code == 201
    criado = resposta.json()
    assert criado["id"] is not None
    assert criado["nome"] == "Suco de Graviola"


def test_api_atualizar_item_cardapio(cliente_api):
    resposta = cliente_api.put("/cardapio/1", json={"preco": 45.00, "nome": "Filé Especial"})
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["preco"] == 45.00
    assert dados["nome"] == "Filé Especial"


def test_api_alternar_disponibilidade(cliente_api):
    resp_antes = cliente_api.get("/cardapio/1")
    disp_inicial = resp_antes.json()["disponivel"]

    resp_patch = cliente_api.patch("/cardapio/1/disponibilidade")
    assert resp_patch.status_code == 200
    assert resp_patch.json()["disponivel"] is not disp_inicial


def test_api_remover_item_cardapio(cliente_api):
    resp_del = cliente_api.delete("/cardapio/1")
    assert resp_del.status_code == 204

    resp_check = cliente_api.get("/cardapio/1")
    assert resp_check.status_code == 404
