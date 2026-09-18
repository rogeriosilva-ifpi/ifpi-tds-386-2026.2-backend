from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from app.config import settings
from app.database import engine, criar_tabelas
from app.domain.errors import ErroDominio
from app.infrastructure.seed import popular_seed_se_vazio
from app.api.exception_handlers import erro_dominio_handler
from app.api.routers import cardapio_router, auth_router, clientes_router


# =====================================================================
# CONCEITO: Lifespan e Carga Inicial de Dados (Seed)
# O lifespan gerencia o ciclo de vida da API ao iniciar e desligar.
# Se o banco estiver vazio, inserimos pratos didáticos através do serviço de seed.
# =====================================================================
@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    # Em SQLite, garante existência da estrutura caso migrações ainda não tenham rodado
    criar_tabelas()

    # Seed automático de demonstração
    with Session(engine) as sessao:
        popular_seed_se_vazio(sessao)

    yield


# =====================================================================
# CONCEITO: Instância Principal da Aplicação FastAPI
# =====================================================================
app = FastAPI(
    title=settings.APP_NAME,
    description="API didática com FastAPI, SQLModel, Alembic Migrations e PostgreSQL/Supabase.",
    version="2.1.0",
    lifespan=ciclo_de_vida,
)

# Exception handler global para erros da camada de domínio
app.add_exception_handler(ErroDominio, erro_dominio_handler)  # type: ignore[arg-type]


# =====================================================================
# CONCEITO: Middleware de CORS (Cross-Origin Resource Sharing)
# =====================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================================
# CONCEITO: Inclusão de Rotas Modulares e Arquivos Estáticos
# =====================================================================
app.include_router(auth_router)
app.include_router(cardapio_router)
app.include_router(clientes_router)
app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")


# Endpoints informativos básicos
@app.get("/", summary="Status da API")
def raiz():
    return {
        "mensagem": "API do Cardápio IFPI no AR!",
        "versao": "2.1.0",
        "ambiente": settings.ENVIRONMENT,
        "docs_swagger": "/docs",
        "frontend": "/frontend/",
    }


@app.get("/hello", summary="Saudação")
def saudacao():
    nome = "Rogério Silva"
    return {
        "mensagem": f"Olá {nome}! Bem-vindo ao Cardápio Digital IFPI TDS!"
    }
