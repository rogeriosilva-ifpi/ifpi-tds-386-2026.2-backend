from logging.config import fileConfig
from alembic import context
from sqlmodel import SQLModel

# Importar configurações e modelos da aplicação
from app.config import settings
from app.database import engine
from app.models import ItemCardapio  # Garante que os modelos sejam registrados no SQLModel.metadata

# =====================================================================
# CONCEITO DIDÁTICO: Integração do Alembic com SQLModel & .env
#
# 1. target_metadata = SQLModel.metadata
#    Permite que o comando 'alembic revision --autogenerate' inspecione
#    as classes Python e gere o SQL das migrações automaticamente.
#
# 2. Configuração Dinâmica da URL:
#    Lê settings.DATABASE_URL do .env (seja PostgreSQL local, Supabase ou SQLite).
#
# 3. render_as_batch=True:
#    Recurso essencial que permite rodar migrações tanto em PostgreSQL
#    quanto em SQLite sem erro de sintaxe de ALTER TABLE.
# =====================================================================

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Define os metadados do banco para o Alembic inspecionar
target_metadata = SQLModel.metadata

# Injeta a URL definida nas variáveis de ambiente (.env)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Executa migrações no modo 'offline' (gera scripts SQL sem conectar ao banco)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migrações no modo 'online' (conectado diretamente ao banco de dados)."""
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
