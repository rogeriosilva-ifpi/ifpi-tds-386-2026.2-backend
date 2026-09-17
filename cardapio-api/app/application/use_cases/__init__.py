"""Casos de uso no padrão CQS de método único async execute()."""
from app.application.use_cases.listar_cardapio import ListarCardapioUseCase
from app.application.use_cases.obter_item_cardapio import ObterItemCardapioUseCase
from app.application.use_cases.criar_item_cardapio import CriarItemCardapioUseCase
from app.application.use_cases.atualizar_item_cardapio import AtualizarItemCardapioUseCase
from app.application.use_cases.alternar_disponibilidade import AlternarDisponibilidadeUseCase
from app.application.use_cases.remover_item_cardapio import RemoverItemCardapioUseCase

__all__ = [
    "ListarCardapioUseCase",
    "ObterItemCardapioUseCase",
    "CriarItemCardapioUseCase",
    "AtualizarItemCardapioUseCase",
    "AlternarDisponibilidadeUseCase",
    "RemoverItemCardapioUseCase",
]
