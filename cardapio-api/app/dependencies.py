import jwt
from fastapi import Header,HTTPException, Depends, status
from sqlmodel import Session
import bcrypt
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from app.database import obter_sessao
from app.models.cliente import Cliente
from app.models.usuario import Usuario, UsuarioPerfil
from typing import Annotated


# =====================================================================
# CONCEITO DIDÁTICO: Injeção de Dependências e Autorização via Header HTTP
#
# 1. Identificação Provisória por Header (X-Cliente-Id):
#    Em arquiteturas REST, antes da introdução de tokens JWT (Bearer Tokens),
#    é comum em ambientes didáticos ou microsserviços internos utilizar um
#    cabeçalho HTTP customizado (X-*) para propagar a identidade do usuário.
#
# 2. Injeção de Dependência (Depends):
#    A dependência intercepta a requisição, extrai o valor de 'X-Cliente-Id',
#    valida a sua existência no banco de dados e fornece a entidade 'Cliente'
#    já pronta para a função da rota.
#
# 3. Tratamento de Erros Semânticos:
#    - HTTP 401 Unauthorized: Quando o header não aponta para um cliente válido.
#    - HTTP 403 Forbidden: Quando um cliente válido tenta operar sobre recursos
#      que pertencem a outro usuário (verificação de posse / ownership).
# =====================================================================


def obter_cliente_autenticado(
    x_cliente_id: int = Header(
        ...,
        alias="X-Cliente-Id",
        description="ID do cliente autenticado (controle de acesso provisório via Header HTTP)",
    ),
    sessao: Session = Depends(obter_sessao),
) -> Cliente:
    """
    Dependência FastAPI que autentica o cliente a partir do header HTTP 'X-Cliente-Id'.
    Garante que apenas clientes existentes no banco de dados possam realizar operações.
    """
    cliente = sessao.get(Cliente, x_cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Cliente não autorizado ou não localizado no banco (X-Cliente-Id={x_cliente_id}).",
        )
    return cliente


# =====================================================================
# CONCEITO: Configuração do Hashing de Senhas
# Utilizamos bcrypt para gerar um hash unidirecional seguro da senha.
# Nunca salvamos a senha em texto plano no banco de dados.
# =====================================================================
def obter_hash_senha(senha: str) -> str:
    """Gera o hash seguro da senha utilizando bcrypt puro."""
    senha_bytes = senha.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha_bytes, salt).decode("utf-8")


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Compara uma senha em texto plano com o hash salvo no banco."""
    return bcrypt.checkpw(
        senha_plana.encode("utf-8"),
        senha_hash.encode("utf-8"),
    )

def senha_forte(password: str):
    if len(password) < 6:
        return False

    simbolos = '!@#$%^&*'
    forte = False
    for caractere in password:
        if caractere in simbolos:
            forte = True
            break

    if not forte:
        return False

    numeros = '0987654321'
    forte = False
    for caractere in password:
        if caractere in numeros:
            forte = True
            break

    if not forte:
        return False


    return True


# Token JWT
SECRET_KEY = 'O Rato Roeu a Roupa do Rei de Portugal'
ALGORITHM = 'HS256'

def create_jwt_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Intercepção para Autorização
oauth_bearer = OAuth2PasswordBearer('/auth/signin/')

def obter_usuario_atual(token: Annotated['str', Depends(oauth_bearer)],
                        session: Session = Depends(obter_sessao)):
    try:
        # Abrir e validar o token
        dados = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id = int(dados.get('sub'))
        usuario = session.get(Usuario, usuario_id)
        return usuario
    except:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Accesso Negado!')


def verificar_perfil(perfis_permitidos: list[UsuarioPerfil]):

    def verificar(usuario: Annotated[Usuario, Depends(obter_usuario_atual)]):
        # Se perfil NOT OK
        if usuario.perfil not in perfis_permitidos:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='Operação não permitida para seu perfil!')

        # Se perfil OK:
        return usuario


    return verificar



