from datetime import date
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.pedido import Pedido

# =====================================================================
# CONCEITO DIDÁTICO: SQLModel para Clientes
# 1. ClienteBase: campos comuns e regras de validação para entrega/delivery.
# 2. Cliente: mapeamento ORM (table=True) na tabela 'clientes'.
# 3. ClienteCreate / ClienteUpdate / ClienteResponse: DTOs da API.
# =====================================================================

class ClienteBase(SQLModel):
    """Campos comuns do Cliente compartilhados entre Banco e API."""
    nome: str = Field(
        min_length=2,
        max_length=150,
        description="Nome completo do cliente"
    )
    data_nascimento: date | None = Field(
        default=None,
        description="Data de nascimento do cliente (AAAA-MM-DD)"
    )
    endereco: str = Field(
        min_length=3,
        max_length=255,
        description="Endereço residencial (rua, avenida, bairro)"
    )
    cep: str = Field(
        min_length=8,
        max_length=10,
        description="Código de Endereçamento Postal (CEP)"
    )
    numero: str = Field(
        min_length=1,
        max_length=20,
        description="Número da residência ou complemento"
    )
    telefone: str = Field(
        min_length=8,
        max_length=20,
        description="Telefone com WhatsApp para contato e entregas"
    )
    


class Cliente(ClienteBase, table=True):
    """Modelo ORM que mapeia a tabela 'clientes' no banco de dados."""
    __tablename__ = "clientes"

    id: int | None = Field(default=None, primary_key=True)

    # Relacionamento 1:N com Pedidos (Deleção em cascata ativada)
    pedidos: list["Pedido"] = Relationship(
        back_populates="cliente",
        cascade_delete=True
    )


class ClienteCreate(SQLModel):
    """Schema para validação no cadastro de cliente (POST). Todos os campos de entrega são obrigatórios."""
    nome: str = Field(
            min_length=2,
            max_length=150,
            description="Nome completo do cliente"
        )
    data_nascimento: date | None = Field(
        default=None,
        description="Data de nascimento do cliente (AAAA-MM-DD)"
    )
    endereco: str = Field(
        min_length=3,
        max_length=255,
        description="Endereço residencial (rua, avenida, bairro)"
    )
    cep: str = Field(
        min_length=8,
        max_length=10,
        description="Código de Endereçamento Postal (CEP)"
    )
    numero: str = Field(
        min_length=1,
        max_length=20,
        description="Número da residência ou complemento"
    )
    telefone: str = Field(
        min_length=8,
        max_length=20,
        description="Telefone com WhatsApp para contato e entregas"
    )


class ClienteUpdate(SQLModel):
    """Schema para atualização parcial de dados do cliente (PUT). Permite atualizar qualquer campo individualmente."""
    nome: str | None = None
    data_nascimento: date | None = None
    endereco: str | None = None
    cep: str | None = None
    numero: str | None = None
    telefone: str | None = None


class ClienteResponse(ClienteBase):
    """Schema retornado pela API nas consultas de cliente. Garante a presença do campo 'id'."""
    id: int
