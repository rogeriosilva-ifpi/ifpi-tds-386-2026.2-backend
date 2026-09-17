"""
Implementação concreta da porta CardapioRepository utilizando SQLModel / SQLAlchemy.
"""
from sqlmodel import Session, select, or_
from app.domain.cardapio import ItemCardapio
from app.infrastructure.repositories.sqlmodel_models import ItemCardapioTable


class SQLModelCardapioRepository:
    """Adaptador de persistência concreto para itens do cardápio."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _to_domain(self, table: ItemCardapioTable) -> ItemCardapio:
        """Converte o modelo de tabela ORM para a entidade pura de domínio."""
        return ItemCardapio(
            id=table.id,
            nome=table.nome,
            descricao=table.descricao,
            preco=table.preco,
            categoria=table.categoria,
            disponivel=table.disponivel,
            tempo_preparo_minutos=table.tempo_preparo_minutos,
        )

    async def listar(
        self,
        categoria: str | None = None,
        disponivel: bool | None = None,
        busca: str | None = None,
        preco_maximo: float | None = None,
    ) -> list[ItemCardapio]:
        """Consulta e filtra registros da tabela de cardápio."""
        query = select(ItemCardapioTable)

        if preco_maximo is not None:
            query = query.where(ItemCardapioTable.preco <= preco_maximo)

        if categoria:
            query = query.where(ItemCardapioTable.categoria == categoria)

        if disponivel is not None:
            query = query.where(ItemCardapioTable.disponivel == disponivel)

        if busca:
            termo = f"%{busca}%"
            query = query.where(
                or_(
                    ItemCardapioTable.nome.ilike(termo),
                    ItemCardapioTable.descricao.ilike(termo),
                )
            )

        query = query.order_by(ItemCardapioTable.nome)
        registros = self.session.exec(query).all()
        return [self._to_domain(reg) for reg in registros]

    async def obter_por_id(self, item_id: int) -> ItemCardapio | None:
        """Localiza um registro por chave primária."""
        registro = self.session.get(ItemCardapioTable, item_id)
        if not registro:
            return None
        return self._to_domain(registro)

    async def salvar(self, item: ItemCardapio) -> ItemCardapio:
        """Cria ou atualiza um registro no banco de dados."""
        if item.id is None:
            novo_registro = ItemCardapioTable(
                nome=item.nome,
                descricao=item.descricao,
                preco=item.preco,
                categoria=item.categoria,
                disponivel=item.disponivel,
                tempo_preparo_minutos=item.tempo_preparo_minutos,
            )
            self.session.add(novo_registro)
            self.session.commit()
            self.session.refresh(novo_registro)
            item.id = novo_registro.id
            return self._to_domain(novo_registro)
        else:
            registro_existente = self.session.get(ItemCardapioTable, item.id)
            if not registro_existente:
                registro_existente = ItemCardapioTable(
                    id=item.id,
                    nome=item.nome,
                    descricao=item.descricao,
                    preco=item.preco,
                    categoria=item.categoria,
                    disponivel=item.disponivel,
                    tempo_preparo_minutos=item.tempo_preparo_minutos,
                )
                self.session.add(registro_existente)
            else:
                registro_existente.nome = item.nome
                registro_existente.descricao = item.descricao
                registro_existente.preco = item.preco
                registro_existente.categoria = item.categoria
                registro_existente.disponivel = item.disponivel
                registro_existente.tempo_preparo_minutos = item.tempo_preparo_minutos
                self.session.add(registro_existente)

            self.session.commit()
            self.session.refresh(registro_existente)
            return self._to_domain(registro_existente)

    async def remover(self, item_id: int) -> None:
        """Exclui o registro da tabela caso exista."""
        registro = self.session.get(ItemCardapioTable, item_id)
        if registro:
            self.session.delete(registro)
            self.session.commit()
