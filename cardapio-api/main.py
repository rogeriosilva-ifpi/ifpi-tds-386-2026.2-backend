"""
Ponto de entrada raiz da aplicação.

CONCEITO: Compatibilidade e Atalho de Execução.
Permite iniciar o servidor tanto por:
    uvicorn main:app --reload
quanto por:
    uvicorn app.main:app --reload
"""
from app.main import app

__all__ = ["app"]
