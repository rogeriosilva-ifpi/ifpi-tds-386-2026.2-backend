"""
Injeção de Dependência Nativa do FastAPI (fastapi.Depends).

CONVENÇÃO: Montagem de adaptadores e casos de uso exclusivamente via geradores e Depends().
"""
from fastapi import Depends
from sqlmodel import Session
from app.database import obter_sessao
from app.application.ports.cardapio_repository import CardapioRepository
from app.infrastructure.repositories.sqlmodel_cardapio_repository import (
    SQLModelCardapioRepository,
)
from app.application.use_cases import (
    ListarCardapioUseCase,
    ObterItemCardapioUseCase,
    CriarItemCardapioUseCase,
    AtualizarItemCardapioUseCase,
    AlternarDisponibilidadeUseCase,
    RemoverItemCardapioUseCase,
)


def obter_cardapio_repository(
    session: Session = Depends(obter_sessao),
) -> CardapioRepository:
    """Instancia o repositório concreto utilizando a sessão do banco da requisição."""
    return SQLModelCardapioRepository(session)


def obter_listar_cardapio_use_case(
    repo: CardapioRepository = Depends(obter_cardapio_repository),
) -> ListarCardapioUseCase:
    return ListarCardapioUseCase(repository=repo)


def obter_obter_item_use_case(
    repo: CardapioRepository = Depends(obter_cardapio_repository),
) -> ObterItemCardapioUseCase:
    return ObterItemCardapioUseCase(repository=repo)


def obter_criar_item_use_case(
    repo: CardapioRepository = Depends(obter_cardapio_repository),
) -> CriarItemCardapioUseCase:
    return CriarItemCardapioUseCase(repository=repo)


def obter_atualizar_item_use_case(
    repo: CardapioRepository = Depends(obter_cardapio_repository),
) -> AtualizarItemCardapioUseCase:
    return AtualizarItemCardapioUseCase(repository=repo)


def obter_alternar_disponibilidade_use_case(
    repo: CardapioRepository = Depends(obter_cardapio_repository),
) -> AlternarDisponibilidadeUseCase:
    return AlternarDisponibilidadeUseCase(repository=repo)


def obter_remover_item_use_case(
    repo: CardapioRepository = Depends(obter_cardapio_repository),
) -> RemoverItemCardapioUseCase:
    return RemoverItemCardapioUseCase(repository=repo)
