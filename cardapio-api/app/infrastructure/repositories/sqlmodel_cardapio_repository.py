"""
Implementação concreta da porta CardapioRepository utilizando SQLModel / SQLAlchemy.
"""
from sqlmodel import Session, select, or_
from app.domain.cardapio import ItemCardapio


class SQLModelCardapioRepository:
    """Adaptador de persistência concreto para itens do cardápio."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def listar(
        self,
        categoria: str | None = None,
        disponivel: bool | None = None,
        busca: str | None = None,
        preco_maximo: float | None = None,
    ) -> list[ItemCardapio]:
        """Consulta e filtra registros da tabela de cardápio."""
        query = select(ItemCardapio)

        if preco_maximo is not None:
            query = query.where(ItemCardapio.preco <= preco_maximo)

        if categoria:
            query = query.where(ItemCardapio.categoria == categoria)

        if disponivel is not None:
            query = query.where(ItemCardapio.disponivel == disponivel)

        if busca:
            termo = f"%{busca}%"
            query = query.where(
                or_(
                    ItemCardapio.nome.ilike(termo),
                    ItemCardapio.descricao.ilike(termo),
                )
            )

        query = query.order_by(ItemCardapio.nome)
        registros = self.session.exec(query).all()
        return list(registros)

    async def obter_por_id(self, item_id: int) -> ItemCardapio | None:
        """Localiza um registro por chave primária."""
        return self.session.get(ItemCardapio, item_id)

    async def salvar(self, item: ItemCardapio) -> ItemCardapio:
        """Cria ou atualiza um registro no banco de dados."""
        if item.id is None:
            self.session.add(item)
            self.session.commit()
            self.session.refresh(item)
            return item
        else:
            merged = self.session.merge(item)
            self.session.commit()
            self.session.refresh(merged)
            return merged

    async def remover(self, item_id: int) -> None:
        """Exclui o registro da tabela caso exista."""
        registro = self.session.get(ItemCardapio, item_id)
        if registro:
            self.session.delete(registro)
            self.session.commit()
