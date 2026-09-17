"""
Exceções da Camada de Domínio.

CONVENÇÃO ARQUITETURAL:
1. Erros de domínio NUNCA importam HTTPException nem tratam status HTTP.
2. Todas as exceções herdam de ErroDominio e possuem um `codigo: str` semântico em UPPER_SNAKE_CASE.
"""


class ErroDominio(Exception):
    """Classe base para todas as exceções de domínio do sistema."""

    def __init__(self, mensagem: str, codigo: str) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.codigo = codigo


class ItemNaoEncontradoError(ErroDominio):
    """Lançado quando um item do cardápio não é localizado por ID."""

    def __init__(self, item_id: int) -> None:
        super().__init__(
            mensagem=f"Item não localizado com id={item_id}.",
            codigo="ITEM_NAO_ENCONTRADO",
        )
        self.item_id = item_id


class RegraVioladaError(ErroDominio):
    """Lançado quando uma invariante de negócio do domínio é violada."""

    def __init__(self, mensagem: str, codigo: str = "REGRA_VIOLADA") -> None:
        super().__init__(mensagem=mensagem, codigo=codigo)
