import pytest
import sys
from app.domain.cardapio import ItemCardapio
from app.domain.errors import ErroDominio, ItemNaoEncontradoError, RegraVioladaError


def test_criar_item_cardapio_valido():
    """Valida a instanciação de uma entidade pura com valores válidos."""
    item = ItemCardapio(
        nome="Hambúrguer Artesanal",
        preco=25.00,
        descricao="Pão brioche e carne 180g",
        categoria="Lanches",
        disponivel=True,
        tempo_preparo_minutos=20,
    )
    assert item.nome == "Hambúrguer Artesanal"
    assert item.preco == 25.00
    assert item.disponivel is True
    assert item.tempo_preparo_minutos == 20


def test_item_cardapio_valores_padrao():
    """Valida se os valores padrão são atribuídos corretamente."""
    item = ItemCardapio(nome="Suco de Laranja", preco=7.00)
    assert item.id is None
    assert item.descricao is None
    assert item.categoria == "Lanches"
    assert item.disponivel is True
    assert item.tempo_preparo_minutos is None


def test_rejeitar_preco_invalido():
    """Valida que preço <= 0 é rejeitado com RegraVioladaError."""
    with pytest.raises(RegraVioladaError) as exc_info:
        ItemCardapio(nome="Prato Grátis", preco=0.0)
    assert exc_info.value.codigo == "PRECO_INVALIDO"

    with pytest.raises(RegraVioladaError) as exc_info_neg:
        ItemCardapio(nome="Prato Negativo", preco=-5.0)
    assert exc_info_neg.value.codigo == "PRECO_INVALIDO"


def test_rejeitar_nome_invalido():
    """Valida que nome vazio ou com menos de 2 caracteres é rejeitado."""
    with pytest.raises(RegraVioladaError) as exc_info:
        ItemCardapio(nome="A", preco=10.0)
    assert exc_info.value.codigo == "NOME_INVALIDO"

    with pytest.raises(RegraVioladaError) as exc_info_space:
        ItemCardapio(nome="   ", preco=10.0)
    assert exc_info_space.value.codigo == "NOME_INVALIDO"


def test_rejeitar_tempo_preparo_invalido():
    """Valida que tempo de preparo < 1 minuto é rejeitado."""
    with pytest.raises(RegraVioladaError) as exc_info:
        ItemCardapio(nome="Café Expresso", preco=5.0, tempo_preparo_minutos=0)
    assert exc_info.value.codigo == "TEMPO_PREPARO_INVALIDO"


def test_alternar_disponibilidade():
    """Valida o método de alternância de disponibilidade."""
    item = ItemCardapio(nome="Item Teste", preco=10.0, disponivel=True)
    item.alternar_disponibilidade()
    assert item.disponivel is False
    item.alternar_disponibilidade()
    assert item.disponivel is True


def test_atualizar_campos_validos():
    """Valida a atualização parcial de campos."""
    item = ItemCardapio(nome="Nome Antigo", preco=15.0)
    item.atualizar(nome="Nome Novo", preco=20.0, disponivel=False)
    assert item.nome == "Nome Novo"
    assert item.preco == 20.0
    assert item.disponivel is False


def test_atualizar_rejeita_invariantes_invalidas():
    """Valida que o método atualizar revalida as invariantes."""
    item = ItemCardapio(nome="Nome Valido", preco=15.0)
    with pytest.raises(RegraVioladaError) as exc:
        item.atualizar(preco=-1.0)
    assert exc.value.codigo == "PRECO_INVALIDO"


def test_item_nao_encontrado_error():
    """Valida que ItemNaoEncontradoError possui codigo e mensagem semânticos."""
    erro = ItemNaoEncontradoError(item_id=42)
    assert isinstance(erro, ErroDominio)
    assert erro.item_id == 42
    assert erro.codigo == "ITEM_NAO_ENCONTRADO"
    assert erro.mensagem == "Item não localizado com id=42."


def test_pureza_arquitetural_da_camada_dominio():
    """INVARIANTE 1: Garante que app.domain não possui imports de frameworks externos."""
    import app.domain.cardapio
    import app.domain.errors

    modulos_proibidos = ["fastapi", "sqlmodel", "sqlalchemy", "starlette", "pydantic"]
    for nome_modulo, modulo in [
        ("cardapio", app.domain.cardapio),
        ("errors", app.domain.errors),
    ]:
        atributos = dir(modulo)
        for proibido in modulos_proibidos:
            assert proibido not in atributos, (
                f"Violação da Invariante 1: Módulo app.domain.{nome_modulo} importa '{proibido}'"
            )
