from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.database import engine, criar_tabelas
from app.models import ItemCardapio
from app.routers import cardapio


# =====================================================================
# CONCEITO: Lifespan e Carga Inicial de Dados (Seed)
# O lifespan gerencia o ciclo de vida da API (o que roda ao ligar e desligar).
# Aqui garantimos que as tabelas existam e, se o banco estiver vazio,
# inserimos alguns pratos típicos para os alunos já verem dados na tela.
# =====================================================================
@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    # 1. Cria tabelas no SQLite caso ainda não existam
    criar_tabelas()

    # 2. Seed: Inserir dados iniciais caso a tabela esteja vazia
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
                ),
                ItemCardapio(
                    nome="Pão c/ Carne de Sol (3und)",
                    descricao="Mini pães recheados com carne de sol desfiada e nata especial.",
                    preco=22.00,
                    categoria="Lanches",
                    disponivel=True,
                ),
                ItemCardapio(
                    nome="Pastel de Queijo Coalho (6und)",
                    descricao="Pastéis fritos na hora com recheio de queijo coalho nordestino.",
                    preco=18.00,
                    categoria="Lanches",
                    disponivel=False, # Demonstrar prato esgotado
                ),
                ItemCardapio(
                    nome="Suco de Caju da Terra (500ml)",
                    descricao="Suco natural de caju fresco da região de Teresina.",
                    preco=8.50,
                    categoria="Bebidas",
                    disponivel=True,
                ),
                ItemCardapio(
                    nome="Pudim de Leite Condensado",
                    descricao="Fatia generosa de pudim tradicional com calda de caramelo.",
                    preco=10.00,
                    categoria="Sobremesas",
                    disponivel=True,
                ),
            ]
            sessao.add_all(dados_iniciais)
            sessao.commit()

    yield
    # Limpezas ao desligar o servidor (se necessário)


# =====================================================================
# CONCEITO: Instância Principal da Aplicação FastAPI
# =====================================================================
app = FastAPI(
    title="Cardápio Digital - IFPI TDS 386",
    description="API didática construída com FastAPI e SQLModel para gestão de cardápio de restaurante.",
    version="2.0.0",
    lifespan=ciclo_de_vida,
)


# =====================================================================
# CONCEITO: Middleware de CORS (Cross-Origin Resource Sharing)
# Permite que qualquer página web (frontend local, Live Server ou portas 3000/5173)
# consiga fazer requisições HTTP para esta API sem ser bloqueada pelo navegador.
# =====================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Aberto para facilidade pedagógica
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi.staticfiles import StaticFiles

# =====================================================================
# CONCEITO: Inclusão de Rotas Modulares e Arquivos Estáticos
# O StaticFiles permite servir a interface HTML/CSS/JS diretamente pelo FastAPI,
# facilitando testes em sala de aula sem precisar de outro servidor web.
# Acesse em: http://127.0.0.1:8000/frontend/
# =====================================================================
app.include_router(cardapio.router)
app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")


# Endpoints informativos básicos (preservando o histórico da primeira aula)
@app.get("/", summary="Status da API")
def raiz():
    return {
        "mensagem": "API do Cardápio IFPI no AR!",
        "versao": "2.0.0",
        "docs_swagger": "/docs",
        "docs_redoc": "/redoc",
    }


@app.get("/hello", summary="Saudação")
def saudacao():
    nome = "Rogério Silva"
    return {
        "mensagem": f"Olá {nome}! Bem-vindo ao Cardápio Digital IFPI TDS!"
    }
