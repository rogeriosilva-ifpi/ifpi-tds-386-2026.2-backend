"""
Entidade de Domínio ItemCardapio.

CONCEITO ARQUITETURAL: Domínio Puro.
Zero dependências de SQLModel, SQLAlchemy, Pydantic com ORM ou frameworks web.
"""
from dataclasses import dataclass
from app.domain.errors import RegraVioladaError


@dataclass
class ItemCardapio:
    """Entidade pura representando um item no cardápio."""

    nome: str
    preco: float
    id: int | None = None
    descricao: str | None = None
    categoria: str = "Lanches"
    disponivel: bool = True
    tempo_preparo_minutos: int | None = None

    def __post_init__(self) -> None:
        self.validar()

    def validar(self) -> None:
        """Garante as invariantes de negócio da entidade."""
        if not self.nome or len(self.nome.strip()) < 2:
            raise RegraVioladaError(
                "O nome do item deve ter no mínimo 2 caracteres.",
                codigo="NOME_INVALIDO",
            )
        if self.preco <= 0:
            raise RegraVioladaError(
                "O preço do item deve ser estritamente maior que zero.",
                codigo="PRECO_INVALIDO",
            )
        if self.tempo_preparo_minutos is not None and self.tempo_preparo_minutos < 1:
            raise RegraVioladaError(
                "O tempo estimado de preparo deve ser de no mínimo 1 minuto.",
                codigo="TEMPO_PREPARO_INVALIDO",
            )

    def alternar_disponibilidade(self) -> None:
        """Alterna a disponibilidade do item (disponível <-> esgotado)."""
        self.disponivel = not self.disponivel

    def atualizar(
        self,
        nome: str | None = None,
        descricao: str | None = None,
        preco: float | None = None,
        categoria: str | None = None,
        disponivel: bool | None = None,
        tempo_preparo_minutos: int | None = None,
    ) -> None:
        """Atualiza campos fornecidos e revalida as invariantes."""
        if nome is not None:
            self.nome = nome
        if descricao is not None:
            self.descricao = descricao
        if preco is not None:
            self.preco = preco
        if categoria is not None:
            self.categoria = categoria
        if disponivel is not None:
            self.disponivel = disponivel
        if tempo_preparo_minutos is not None:
            self.tempo_preparo_minutos = tempo_preparo_minutos

        self.validar()
