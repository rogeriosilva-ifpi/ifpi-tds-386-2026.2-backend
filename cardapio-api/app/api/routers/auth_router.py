"""
APIRouter de Autenticação (Endpoints didáticos preservados).
"""
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.get("/me")
def me() -> str:
    return "Sou Rogério"


@router.post("/login")
def login() -> str:
    return "Autenticado com sucesso!"
