import inspect
import pytest
from app.application.use_cases import (
    ListarCardapioUseCase,
    ObterItemCardapioUseCase,
    CriarItemCardapioUseCase,
    AtualizarItemCardapioUseCase,
    AlternarDisponibilidadeUseCase,
    RemoverItemCardapioUseCase,
)
from app.domain.cardapio import ItemCardapio
from app.domain.errors import ItemNaoEncontradoError, RegraVioladaError


class FakeCardapioRepository:
    """Implementação em memória da porta CardapioRepository para testes unitários."""

    def __init__(self, itens: list[ItemCardapio] | None = None) -> None:
        self.itens: dict[int, ItemCardapio] = {}
        self._next_id = 1
        if itens:
            for item in itens:
                if item.id is None:
                    item.id = self._next_id
                    self._next_id += 1
                self.itens[item.id] = item

    async def listar(
        self,
        categoria: str | None = None,
        disponivel: bool | None = None,
        busca: str | None = None,
        preco_maximo: float | None = None,
    ) -> list[ItemCardapio]:
        resultado = list(self.itens.values())
        if categoria:
            resultado = [i for i in resultado if i.categoria == categoria]
        if disponivel is not None:
            resultado = [i for i in resultado if i.disponivel == disponivel]
        if busca:
            termo = busca.lower()
            resultado = [
                i for i in resultado
                if termo in i.nome.lower() or (i.descricao and termo in i.descricao.lower())
            ]
        if preco_maximo is not None:
            resultado = [i for i in resultado if i.preco <= preco_maximo]
        resultado.sort(key=lambda x: x.nome)
        return resultado

    async def obter_por_id(self, item_id: int) -> ItemCardapio | None:
        return self.itens.get(item_id)

    async def salvar(self, item: ItemCardapio) -> ItemCardapio:
        if item.id is None:
            item.id = self._next_id
            self._next_id += 1
        self.itens[item.id] = item
        return item

    async def remover(self, item_id: int) -> None:
        self.itens.pop(item_id, None)


@pytest.mark.anyio
async def test_listar_cardapio_use_case():
    item1 = ItemCardapio(nome="Suco", preco=8.0, categoria="Bebidas")
    item2 = ItemCardapio(nome="Hambúrguer", preco=25.0, categoria="Lanches")
    repo = FakeCardapioRepository([item1, item2])
    uc = ListarCardapioUseCase(repository=repo)

    itens = await uc.execute(categoria="Bebidas")
    assert len(itens) == 1
    assert itens[0].nome == "Suco"


@pytest.mark.anyio
async def test_obter_item_cardapio_sucesso():
    item = ItemCardapio(nome="Pudim", preco=10.0)
    repo = FakeCardapioRepository([item])
    uc = ObterItemCardapioUseCase(repository=repo)

    encontrado = await uc.execute(item_id=1)
    assert encontrado.nome == "Pudim"


@pytest.mark.anyio
async def test_obter_item_cardapio_nao_encontrado_lanca_erro():
    repo = FakeCardapioRepository()
    uc = ObterItemCardapioUseCase(repository=repo)

    with pytest.raises(ItemNaoEncontradoError) as exc_info:
        await uc.execute(item_id=999)
    assert exc_info.value.codigo == "ITEM_NAO_ENCONTRADO"
    assert exc_info.value.item_id == 999


@pytest.mark.anyio
async def test_criar_item_cardapio_sucesso():
    repo = FakeCardapioRepository()
    uc = CriarItemCardapioUseCase(repository=repo)

    novo = ItemCardapio(nome="Pastel", preco=12.0)
    criado = await uc.execute(novo)
    assert criado.id == 1
    assert criado.nome == "Pastel"


@pytest.mark.anyio
async def test_atualizar_item_cardapio_sucesso():
    item = ItemCardapio(nome="Nome Velho", preco=15.0)
    repo = FakeCardapioRepository([item])
    uc = AtualizarItemCardapioUseCase(repository=repo)

    atualizado = await uc.execute(item_id=1, nome="Nome Novo", preco=22.0)
    assert atualizado.nome == "Nome Novo"
    assert atualizado.preco == 22.0


@pytest.mark.anyio
async def test_atualizar_item_cardapio_nao_encontrado():
    repo = FakeCardapioRepository()
    uc = AtualizarItemCardapioUseCase(repository=repo)

    with pytest.raises(ItemNaoEncontradoError):
        await uc.execute(item_id=999, nome="Inexistente")


@pytest.mark.anyio
async def test_alternar_disponibilidade_sucesso():
    item = ItemCardapio(nome="Prato do Dia", preco=30.0, disponivel=True)
    repo = FakeCardapioRepository([item])
    uc = AlternarDisponibilidadeUseCase(repository=repo)

    alterado = await uc.execute(item_id=1)
    assert alterado.disponivel is False


@pytest.mark.anyio
async def test_alternar_disponibilidade_nao_encontrado():
    repo = FakeCardapioRepository()
    uc = AlternarDisponibilidadeUseCase(repository=repo)

    with pytest.raises(ItemNaoEncontradoError):
        await uc.execute(item_id=999)


@pytest.mark.anyio
async def test_remover_item_cardapio_sucesso():
    item = ItemCardapio(nome="Item a Excluir", preco=5.0)
    repo = FakeCardapioRepository([item])
    uc = RemoverItemCardapioUseCase(repository=repo)

    await uc.execute(item_id=1)
    assert await repo.obter_por_id(1) is None


@pytest.mark.anyio
async def test_remover_item_cardapio_nao_encontrado():
    repo = FakeCardapioRepository()
    uc = RemoverItemCardapioUseCase(repository=repo)

    with pytest.raises(ItemNaoEncontradoError):
        await uc.execute(item_id=999)


def test_invariante_2_metodo_unico_execute():
    """INVARIANTE 2: Todo caso de uso deve ter apenas __init__ e execute como métodos públicos."""
    import app.application.use_cases as use_cases_pkg

    classes = [
        cls for name, cls in inspect.getmembers(use_cases_pkg, inspect.isclass)
        if name.endswith("UseCase")
    ]
    assert len(classes) == 6, f"Esperado 6 casos de uso, localizado {len(classes)}"

    for cls in classes:
        metodos_publicos = [
            m for m in dir(cls)
            if not m.startswith("_") and callable(getattr(cls, m))
        ]
        assert metodos_publicos == ["execute"], (
            f"Violação da Invariante 2 em {cls.__name__}: métodos públicos permitidos apenas ['execute'], localizado {metodos_publicos}"
        )
        assert inspect.iscoroutinefunction(cls.execute), (
            f"Violação da Invariante 2 em {cls.__name__}: método execute deve ser assíncrono (async def)"
        )
