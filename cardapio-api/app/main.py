from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from app.config import settings
from app.database import engine, criar_tabelas
from app.models import ItemCardapio
from app.routers import cardapio, auth


# =====================================================================
# CONCEITO DIDÁTICO: Lifespan e Carga Inicial de Dados (Seed)
# O lifespan gerencia o ciclo de vida da API ao iniciar e desligar.
# Se o banco estiver vazio, inserimos pratos didáticos com tempo de preparo.
# =====================================================================
@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    # Em SQLite, garante existência da estrutura caso migrações ainda não tenham rodado
    criar_tabelas()

    # Seed automático de demonstração
    with Session(engine) as sessao:
        itens_existentes = sessao.exec(select(ItemCardapio)).first()
        if not itens_existentes:
            dados_iniciais = [
                ItemCardapio(
                    nome="Filé com Fritas",
                    descricao="Filé mignon grelhado em tiras, servido com batatas fritas crocantes.",
                    preco=38.50,
                    categoria="Lanches",
                    disponivel=True,
                    tempo_preparo_minutos=25,
                ),
                ItemCardapio(
                    nome="Pão c/ Carne de Sol (3und)",
                    descricao="Mini pães recheados com carne de sol desfiada e nata especial.",
                    preco=22.00,
                    categoria="Lanches",
                    disponivel=True,
                    tempo_preparo_minutos=15,
                ),
                ItemCardapio(
                    nome="Pastel de Queijo Coalho (6und)",
                    descricao="Pastéis fritos na hora com recheio de queijo coalho nordestino.",
                    preco=18.00,
                    categoria="Lanches",
                    disponivel=False, # Demonstrar prato esgotado
                    tempo_preparo_minutos=12,
                ),
                ItemCardapio(
                    nome="Suco de Caju da Terra (500ml)",
                    descricao="Suco natural de caju fresco da região de Teresina.",
                    preco=8.50,
                    categoria="Bebidas",
                    disponivel=True,
                    tempo_preparo_minutos=5,
                ),
                ItemCardapio(
                    nome="Pudim de Leite Condensado",
                    descricao="Fatia generosa de pudim tradicional com calda de caramelo.",
                    preco=10.00,
                    categoria="Sobremesas",
                    disponivel=True,
                    tempo_preparo_minutos=2,
                ),
            ]
            sessao.add_all(dados_iniciais)
            sessao.commit()

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
app.include_router(cardapio.router)
app.include_router(auth.router)
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
