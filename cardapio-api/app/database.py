from sqlmodel import SQLModel, create_engine, Session

# =====================================================================
# CONCEITO: Conexão e Persistência com SQLite
# SQLite é um banco de dados relacional embutido (baseado em arquivo).
# Não requer servidor externo, tornando-o perfeito para aprendizado.
# =====================================================================
ARQUIVO_BANCO = "cardapio.db"
DATABASE_URL = f"sqlite:///{ARQUIVO_BANCO}"

# connect_args={"check_same_thread": False} é obrigatório no SQLite
# para permitir que múltiplas requisições assíncronas usem a mesma conexão com segurança.
engine = create_engine(
    DATABASE_URL, 
    echo=False, 
    connect_args={"check_same_thread": False}
)


def criar_tabelas() -> None:
    """
    CONCEITO: DDL (Data Definition Language) Automático.
    O SQLModel lê todas as classes que herdaram de SQLModel com table=True
    e gera as instruções SQL CREATE TABLE no SQLite automaticamente.
    """
    SQLModel.metadata.create_all(engine)


def obter_sessao():
    """
    CONCEITO: Injeção de Dependência (Session Lifecycle).
    Esta função geradora (com yield) cria uma nova sessão do banco para cada
    requisição HTTP e garante seu fechamento ao término, liberando recursos.
    """
    with Session(engine) as sessao:
        yield sessao
