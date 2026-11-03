from pydantic_settings import BaseSettings, SettingsConfigDict

# =====================================================================
# CONCEITO DIDÁTICO: Twelve-Factor App (Fator III: Configurações no Ambiente)
#
# 1. Por que variáveis de ambiente?
#    - Segurança: Senhas e credenciais de banco não devem estar no código-fonte.
#    - Portabilidade: A mesma aplicação roda no ambiente Local (desenvolvimento)
#      e na Nuvem (Supabase / produção) alterando apenas a variável DATABASE_URL.
#
# 2. Pydantic Settings:
#    Lê do arquivo .env ou das variáveis do Sistema Operacional, convertendo
#    e validando os tipos de dados automaticamente.
# =====================================================================


class Settings(BaseSettings):
    # URL de conexão com o banco de dados (PostgreSQL local, Supabase ou SQLite)
    # Por padrão, usa SQLite caso o aluno ainda não tenha criado o .env
    DATABASE_URL: str = "sqlite:///./cardapio.db"

    # Ambiente de execução (development, production, testing)
    ENVIRONMENT: str = "development"

    # Habilita mensagens detalhadas de log e depuração
    DEBUG: bool = True

    # Nome da aplicação exibido na documentação Swagger
    APP_NAME: str = "Cardápio Digital - IFPI TDS 386"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Instância única (Singleton) compartilhada por toda a aplicação
settings = Settings()
