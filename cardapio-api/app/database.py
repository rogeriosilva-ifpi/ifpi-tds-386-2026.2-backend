from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

# =====================================================================
# CONCEITO DIDÁTICO: Conexão Flexível com Banco de Dados Relacional
#
# 1. Suporte Híbrido:
#    - PostgreSQL (Local ou Supabase na Nuvem): Usado em desenvolvimento profissional e produção.
#    - SQLite: Usado como fallback didático local e em suítes de testes rápidos.
#
# 2. Argumentos de Conexão:
#    - SQLite requer connect_args={"check_same_thread": False} devido a threads assíncronas do FastAPI.
#    - PostgreSQL não precisa desse argumento.
# =====================================================================

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL, 
    echo=settings.DEBUG, 
    connect_args=connect_args
)


def criar_tabelas() -> None:
    """
    Cria as tabelas caso ainda não existam.
    Em ambientes profissionais com PostgreSQL/Supabase, essa função dá lugar
    às migrações versionadas do Alembic (alembic upgrade head).
    """
    SQLModel.metadata.create_all(engine)


def obter_sessao():
    """
    CONCEITO: Injeção de Dependência (Session Lifecycle).
    Gera uma sessão para cada requisição HTTP e garante o fechamento automático.
    """
    with Session(engine) as sessao:
        yield sessao
