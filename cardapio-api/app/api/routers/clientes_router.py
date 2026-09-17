"""
APIRouter de Clientes (Endpoints didáticos preservados).
"""
from fastapi import APIRouter

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("/")
def listar_clientes() -> list[str]:
    return ["Rogério", "Daniel Pereira", "Daniel Santos"]


@router.get("/{id}")
def obter_cliente(id: int) -> str:
    return f"Cliente de ID={id}"


@router.post("/")
def criar_cliente() -> str:
    return ""


@router.put("/{id}")
def atualizar_cliente(id: int) -> str:
    return ""
