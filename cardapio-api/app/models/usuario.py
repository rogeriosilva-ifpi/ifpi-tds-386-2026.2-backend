import enum
from datetime import date
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr

if TYPE_CHECKING:
    from app.models.cliente import Cliente

# =====================================================================
# CONCEITO DIDÁTICO: SQLModel para Usuários
# 1. UsuarioBase: campos de identificação e status do usuário.
# 2. Usuario: mapeamento ORM (table=True), incluindo senha em hash e FK.
# 3. UsuarioCreate: DTO para registro (recebe a senha em texto plano).
# 4. UsuarioUpdate: DTO para atualização parcial.
# 5. UsuarioResponse: DTO de saída da API (nunca retorna senhas).
# =====================================================================

class UsuarioPerfil(str, enum.Enum):
    ADMIN = 'admin'
    LOGISTA = 'logista'
    CLIENTE = 'cliente'


class UsuarioBase(SQLModel):
    """Campos base de identidade e controle de acesso do usuário."""
    email: EmailStr = Field(
        unique=True,
        index=True,
        max_length=255,
        description="E-mail principal para login"
    )
    is_active: bool = Field(
        default=True,
        description="Define se a conta do usuário está ativa para login"
    )
    is_superuser: bool = Field(
        default=False,
        description="Define se o usuário possui privilégios de administrador"
    )
    cliente_id: int | None = Field(
        default=None, 
        foreign_key="clientes.id",
        description="ID do cliente (perfil de entrega) associado a este usuário"
    )
    perfil: UsuarioPerfil = Field(default=UsuarioPerfil.CLIENTE, nullable=True)


class Usuario(UsuarioBase, table=True):
    """Modelo ORM que mapeia a tabela 'usuarios' no banco de dados."""
    __tablename__ = "usuarios"

    id: int | None = Field(default=None, primary_key=True)
    
    hashed_password: str = Field(
        nullable=False,
        description="Hash seguro da senha do usuário"
    )

    # Relacionamento 1:1 com Cliente
    cliente: Optional["Cliente"] = Relationship(back_populates="usuario")


class UsuarioCreate(UsuarioBase):
    """Schema para validação no registro de um novo usuário (POST)."""
    password: str = Field(
        min_length=6,
        max_length=72,
        description="Senha em texto plano (será convertida em hash no service)"
    )


class UsuarioUpdate(SQLModel):
    """Schema para atualização de dados de acesso do usuário (PUT/PATCH)."""
    email: EmailStr | None = None
    password: str | None = Field(
        default=None,
        min_length=6,
        max_length=72
    )
    is_active: bool | None = None
    is_superuser: bool | None = None
    cliente_id: int | None = None


class UsuarioResponse(UsuarioBase):
    """Schema retornado pela API nas requisições. Oculta a senha em hash por segurança."""
    id: int


class UsuarioRegistro(SQLModel):
    """Schema para o Endpoint de Signup. Recebe credenciais de acesso e dados do perfil do cliente."""
    # Credenciais
    email: EmailStr = Field(description="E-mail de acesso")
    password: str = Field(min_length=6, max_length=72, description="Senha em texto plano")
    
    # Dados do Cliente (Perfil de Entrega)
    nome: str = Field(min_length=2, max_length=150)
    data_nascimento: date | None = None
    endereco: str = Field(min_length=3, max_length=255)
    cep: str = Field(min_length=8, max_length=10)
    numero: str = Field(min_length=1, max_length=20)
    telefone: str = Field(min_length=8, max_length=20)


class LoginData(SQLModel):
    email: EmailStr = Field(description="E-mail de acesso")
    password: str = Field(min_length=6, max_length=72, description="Senha em texto plano")


class LoginResponse(SQLModel):
    access_token: str
    refresh_token: str


class RefreshData(SQLModel):
    refresh_token: str
        