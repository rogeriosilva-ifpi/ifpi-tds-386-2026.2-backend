import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

# Força o ambiente de testes para SQLite em memória antes de qualquer inicialização
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import app.database as app_db
from app.main import app

# Engine SQLite em memória compartilhado por threads via StaticPool
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Redireciona o engine global da aplicação e do main para o engine de teste
app_db.engine = test_engine
import app.main as app_main_module
app_main_module.engine = test_engine


@pytest.fixture(autouse=True)
def isolar_banco_dados():
    """Garante que cada teste tenha um banco limpo e recriado com o seed inicial."""
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def cliente():
    """Fornece um TestClient com a sessão de banco isolada e lifespan executado."""
    def _obter_sessao_override():
        with Session(test_engine) as sessao:
            yield sessao

    app.dependency_overrides[app_db.obter_sessao] = _obter_sessao_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
