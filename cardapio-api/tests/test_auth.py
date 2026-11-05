import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select, func

from app.main import app
from app.database import engine
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.routers.auth import verificar_senha

# =====================================================================
# CONCEITO DIDÁTICO: Testes Automatizados para Autenticação (/auth/signup)
#
# Validações essenciais:
# 1. Autocadastro atômico (Cliente + Usuario vinculados em transação única).
# 2. Segurança de credenciais: senha salva com hash bcrypt ($2b$) e nunca
#    exposta no corpo da resposta (UsuarioResponse).
# 3. Unicidade de e-mail (HTTP 400) sem gerar registros órfãos de Cliente.
# 4. Contratos de validação Pydantic (HTTP 422) para e-mail, limites de
#    senha (6 a 72 caracteres) e dados obrigatórios de entrega.
# =====================================================================


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


def _limpar_usuario_teste(email: str) -> None:
    """Remove usuário e cliente de teste para garantir idempotência entre execuções."""
    with Session(engine) as sessao:
        usuario = sessao.exec(select(Usuario).where(Usuario.email == email)).first()
        if usuario:
            cliente_id = usuario.cliente_id
            sessao.delete(usuario)
            sessao.commit()
            if cliente_id:
                cliente = sessao.get(Cliente, cliente_id)
                if cliente:
                    sessao.delete(cliente)
                    sessao.commit()


def test_signup_sucesso_completo_e_hash_senha(client):
    """
    Valida o fluxo completo de autocadastro (POST /auth/signup -> 201 Created),
    ocultação da senha na resposta, geração correta do hash bcrypt no banco e
    criação atômica do perfil de Cliente vinculado.
    """
    email_teste = "maria.autenticada@exemplo.com"
    senha_plana = "SenhaSegura@123"
    _limpar_usuario_teste(email_teste)

    payload = {
        "email": email_teste,
        "password": senha_plana,
        "nome": "Maria Autenticada",
        "data_nascimento": "1996-08-20",
        "endereco": "Av. Nossa Senhora de Fátima, Fátima",
        "cep": "64048-180",
        "numero": "1500",
        "telefone": "86999112233",
    }

    try:
        resposta = client.post("/auth/signup", json=payload)
        assert resposta.status_code == 201

        dados = resposta.json()
        assert "id" in dados
        assert dados["email"] == email_teste
        assert dados["is_active"] is True
        assert dados["is_superuser"] is False
        assert dados["cliente_id"] is not None

        # Segurança: nem a senha plana nem o hash podem vazar no JSON de resposta
        assert "password" not in dados
        assert "hashed_password" not in dados

        # Verificar persistência e hash real no banco de dados
        with Session(engine) as sessao:
            usuario_banco = sessao.get(Usuario, dados["id"])
            assert usuario_banco is not None
            assert usuario_banco.hashed_password != senha_plana
            assert usuario_banco.hashed_password.startswith("$2b$")
            assert verificar_senha(senha_plana, usuario_banco.hashed_password) is True
            assert verificar_senha("SenhaErrada", usuario_banco.hashed_password) is False

        # Verificar se o Cliente vinculado foi criado com os dados de entrega
        cliente_id = dados["cliente_id"]
        resp_cliente = client.get(f"/clientes/{cliente_id}")
        assert resp_cliente.status_code == 200
        cliente_criado = resp_cliente.json()
        assert cliente_criado["nome"] == payload["nome"]
        assert cliente_criado["data_nascimento"] == payload["data_nascimento"]
        assert cliente_criado["endereco"] == payload["endereco"]
        assert cliente_criado["cep"] == payload["cep"]
        assert cliente_criado["numero"] == payload["numero"]
        assert cliente_criado["telefone"] == payload["telefone"]
    finally:
        _limpar_usuario_teste(email_teste)


def test_signup_sem_data_nascimento_opcional(client):
    """Valida que o campo opcional data_nascimento pode ser omitido no signup."""
    email_teste = "sem.nascimento@exemplo.com"
    _limpar_usuario_teste(email_teste)

    payload = {
        "email": email_teste,
        "password": "123456",
        "nome": "Cliente Sem Data",
        "endereco": "Rua Desembargador Pires de Castro",
        "cep": "64000-200",
        "numero": "210",
        "telefone": "86988112233",
    }

    try:
        resposta = client.post("/auth/signup", json=payload)
        assert resposta.status_code == 201
        dados = resposta.json()
        resp_cliente = client.get(f"/clientes/{dados['cliente_id']}")
        assert resp_cliente.status_code == 200
        assert resp_cliente.json()["data_nascimento"] is None
    finally:
        _limpar_usuario_teste(email_teste)


def test_signup_email_duplicado_retorna_400_e_nao_cria_cliente_orfao(client):
    """
    Valida que tentar cadastrar um e-mail já existente retorna HTTP 400 Bad Request
    e não insere um registro de Cliente duplicado/órfão no banco.
    """
    email_teste = "duplicado@exemplo.com"
    _limpar_usuario_teste(email_teste)

    payload = {
        "email": email_teste,
        "password": "123456",
        "nome": "Usuario Original",
        "endereco": "Rua Alfa, Centro",
        "cep": "64000-000",
        "numero": "10",
        "telefone": "86999001122",
    }

    try:
        # 1º cadastro deve funcionar (201)
        resp_1 = client.post("/auth/signup", json=payload)
        assert resp_1.status_code == 201

        with Session(engine) as sessao:
            total_clientes_antes = sessao.exec(select(func.count(Cliente.id))).one()

        # 2º cadastro com mesmo e-mail deve ser rejeitado (400)
        payload_duplicado = {**payload, "nome": "Tentativa Duplicada"}
        resp_2 = client.post("/auth/signup", json=payload_duplicado)
        assert resp_2.status_code == 400
        assert "já está em uso" in resp_2.json()["detail"]

        # Garante que nenhum Cliente extra foi salvo na tentativa rejeitada
        with Session(engine) as sessao:
            total_clientes_depois = sessao.exec(select(func.count(Cliente.id))).one()
        assert total_clientes_depois == total_clientes_antes
    finally:
        _limpar_usuario_teste(email_teste)


@pytest.mark.parametrize(
    "email_invalido",
    [
        "email-sem-arroba.com",
        "arroba-sem-dominio@",
        "@sem-usuario.com",
        "",
    ],
)
def test_signup_validacao_email_invalido_retorna_422(client, email_invalido):
    """Valida que formatos de e-mail inválidos são rejeitados com HTTP 422."""
    resposta = client.post(
        "/auth/signup",
        json={
            "email": email_invalido,
            "password": "123456",
            "nome": "Teste Email",
            "endereco": "Rua Teste",
            "cep": "64000-000",
            "numero": "10",
            "telefone": "86999990000",
        },
    )
    assert resposta.status_code == 422


@pytest.mark.parametrize(
    "senha_invalida",
    [
        "",           # Vazia
        "12345",      # Menor que min_length=6
        "a" * 73,     # Maior que max_length=72 (limite do bcrypt)
    ],
)
def test_signup_validacao_limites_senha_retorna_422(client, senha_invalida):
    """Valida que senhas menores que 6 ou maiores que 72 caracteres retornam HTTP 422."""
    resposta = client.post(
        "/auth/signup",
        json={
            "email": "validacao.senha@exemplo.com",
            "password": senha_invalida,
            "nome": "Teste Senha",
            "endereco": "Rua Teste",
            "cep": "64000-000",
            "numero": "10",
            "telefone": "86999990000",
        },
    )
    assert resposta.status_code == 422


@pytest.mark.parametrize(
    "campo_omitido",
    ["email", "password", "nome", "endereco", "cep", "numero", "telefone"],
)
def test_signup_campos_obrigatorios_ausentes_retorna_422(client, campo_omitido):
    """Valida que a ausência de qualquer campo obrigatório no signup retorna HTTP 422."""
    payload = {
        "email": "completo@exemplo.com",
        "password": "123456",
        "nome": "Cliente Completo",
        "endereco": "Rua Completa",
        "cep": "64000-000",
        "numero": "10",
        "telefone": "86999990000",
    }
    del payload[campo_omitido]

    resposta = client.post("/auth/signup", json=payload)
    assert resposta.status_code == 422


@pytest.mark.parametrize(
    "campo_invalido",
    [
        {"nome": "A"},              # min_length=2
        {"endereco": "AB"},         # min_length=3
        {"cep": "1234567"},         # min_length=8
        {"cep": "12345678901"},     # max_length=10
        {"numero": ""},             # min_length=1
        {"telefone": "1234567"},    # min_length=8
    ],
)
def test_signup_validacao_regras_perfil_cliente_retorna_422(client, campo_invalido):
    """Valida as restrições de tamanho dos campos do perfil de entrega no signup."""
    payload = {
        "email": "regras.cliente@exemplo.com",
        "password": "123456",
        "nome": "Cliente Valido",
        "endereco": "Rua Valida",
        "cep": "64000-000",
        "numero": "10",
        "telefone": "86999990000",
        **campo_invalido,
    }

    resposta = client.post("/auth/signup", json=payload)
    assert resposta.status_code == 422
