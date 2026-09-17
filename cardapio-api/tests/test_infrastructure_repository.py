import pytest
from sqlmodel import Session
from app.domain.cardapio import ItemCardapio
from app.infrastructure.repositories.sqlmodel_cardapio_repository import (
    SQLModelCardapioRepository,
)
from app.infrastructure.seed import popular_seed_se_vazio
from tests.conftest import test_engine


@pytest.fixture
def repo():
    """Fornece um repositório concreto conectado à sessão de teste isolada."""
    with Session(test_engine) as sessao:
        yield SQLModelCardapioRepository(session=sessao)


@pytest.mark.anyio
async def test_repository_salvar_e_obter_por_id(repo):
    """Valida a inserção e busca por ID no repositório SQLModel."""
    novo_item = ItemCardapio(
        nome="Tapioca com Coco",
        descricao="Tapioca tradicional recheada",
        preco=12.00,
        categoria="Lanches",
        disponivel=True,
        tempo_preparo_minutos=10,
    )
    salvo = await repo.salvar(novo_item)
    assert salvo.id is not None
    assert salvo.nome == "Tapioca com Coco"

    buscado = await repo.obter_por_id(salvo.id)
    assert buscado is not None
    assert buscado.id == salvo.id
    assert buscado.preco == 12.00


@pytest.mark.anyio
async def test_repository_atualizar(repo):
    """Valida a atualização de um registro existente."""
    item = ItemCardapio(nome="Item Antigo", preco=10.0)
    salvo = await repo.salvar(item)

    salvo.atualizar(nome="Item Novo", preco=15.50, disponivel=False)
    atualizado = await repo.salvar(salvo)

    assert atualizado.nome == "Item Novo"
    assert atualizado.preco == 15.50
    assert atualizado.disponivel is False


@pytest.mark.anyio
async def test_repository_remover(repo):
    """Valida a remoção de um item."""
    item = ItemCardapio(nome="Para Deletar", preco=5.0)
    salvo = await repo.salvar(item)
    item_id = salvo.id

    await repo.remover(item_id)
    buscado = await repo.obter_por_id(item_id)
    assert buscado is None


@pytest.mark.anyio
async def test_repository_listar_com_filtros(repo):
    """Valida consultas com filtros de categoria, preco_maximo, busca e ordenação."""
    await repo.salvar(ItemCardapio(nome="Bolo de Cenoura", preco=8.0, categoria="Sobremesas"))
    await repo.salvar(ItemCardapio(nome="Açaí na Tigela", preco=18.0, categoria="Sobremesas"))
    await repo.salvar(ItemCardapio(nome="Café Preto", preco=4.0, categoria="Bebidas"))

    # Filtro por categoria
    sobremesas = await repo.listar(categoria="Sobremesas")
    assert len(sobremesas) == 2
    # Ordenação alfabética
    assert sobremesas[0].nome == "Açaí na Tigela"
    assert sobremesas[1].nome == "Bolo de Cenoura"

    # Filtro por preco_maximo
    baratos = await repo.listar(preco_maximo=10.0)
    for b in baratos:
        assert b.preco <= 10.0

    # Filtro por busca
    busca_acai = await repo.listar(busca="açaí")
    assert len(busca_acai) == 1
    assert busca_acai[0].nome == "Açaí na Tigela"


def test_seed_popular_dados_iniciais():
    """Valida a função de carga inicial demonstrativa."""
    with Session(test_engine) as sessao:
        popular_seed_se_vazio(sessao)
        repo = SQLModelCardapioRepository(session=sessao)

    with Session(test_engine) as sessao2:
        repo2 = SQLModelCardapioRepository(session=sessao2)
        itens = sessao2.exec(
            __import__("sqlmodel").select(
                __import__("app.infrastructure.repositories.sqlmodel_models", fromlist=["ItemCardapioTable"]).ItemCardapioTable
            )
        ).all()
        assert len(itens) == 5
