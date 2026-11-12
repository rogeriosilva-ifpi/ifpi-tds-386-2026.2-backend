import jwt
from jwt.exceptions import InvalidTokenError
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Annotated
from app.dependencies import senha_forte, \
            verificar_senha, obter_hash_senha, \
                create_jwt_token, obter_usuario_atual, verificar_perfil
            

from app.database import obter_sessao
from app.models.usuario import Usuario, UsuarioResponse, UsuarioRegistro, LoginData, LoginResponse, RefreshData, UsuarioPerfil
from app.models.cliente import Cliente



# =====================================================================
# CONCEITO: APIRouter para Autenticação
# Agrupa endpoints focados em login, cadastro e tokens sob o prefixo /auth.
# =====================================================================
router = APIRouter(prefix="/auth", tags=["Autenticação"])


# =====================================================================
# CONCEITO: Endpoint de Autocadastro (Signup)
# 1. Verifica se o e-mail já existe.
# 2. Gera o Hash da senha.
# 3. Cria instâncias de Cliente e Usuario na memória.
# 4. Vincula as instâncias e salva no banco de forma atômica (único commit).
# =====================================================================
@router.post(
    "/signup",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Autocadastro de um novo usuário na plataforma",
)
def signup(dados: UsuarioRegistro, sessao: Session = Depends(obter_sessao)):
    # 1. Validação de E-mail Único
    consulta = select(Usuario).where(Usuario.email == dados.email)
    usuario_existente = sessao.exec(consulta).first()
    
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este e-mail já está em uso na plataforma."
        )

    if not senha_forte(dados.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Senha não atende ao critérios de segurança'
        )

    # 2. Criar a instância de Cliente com os dados extraídos do DTO Combinado
    novo_cliente = Cliente(
        nome=dados.nome,
        data_nascimento=dados.data_nascimento,
        endereco=dados.endereco,
        cep=dados.cep,
        numero=dados.numero,
        telefone=dados.telefone
    )

    # 3. Criar a instância de Usuário
    # O SQLModel vincula automaticamente o cliente_id pela relação
    novo_usuario = Usuario(
        email=dados.email,
        hashed_password=obter_hash_senha(dados.password),
        is_active=True,
        is_superuser=False,
        cliente=novo_cliente  # Vínculo feito via Relationship!
    )

    # 4. Persistir no banco de dados
    # O SQLModel/SQLAlchemy sabe que precisa inserir o Cliente primeiro devido à ForeignKey
    sessao.add(novo_usuario) 
    sessao.commit()
    sessao.refresh(novo_usuario)

    # Retorna usando o UsuarioResponse (que oculta o hashed_password)
    return novo_usuario


@router.post('/signin',
             response_model=LoginResponse,
             status_code=status.HTTP_200_OK,
             summary='Rota para Obteção de Token JWT (Login)')
def signin(dados: LoginData, 
           sessao: Session = Depends(obter_sessao)):

    # 1. Validação de E-mail Único
    consulta = select(Usuario).where(Usuario.email == dados.email)
    usuario_existente = sessao.exec(consulta).first()
    
    if not usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A: Usuário e/ou senha incorretos!!!"
        )

    # 2. Validar a senha
    senha_eh_valida = verificar_senha(dados.password, 
                                usuario_existente.hashed_password)

    if not senha_eh_valida:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="B: Usuário e/ou senha incorretos!!!"
                )

    access_token = create_jwt_token({'sub': str(usuario_existente.id), 'type': 'access'}, 
                                       timedelta(minutes=7))
    refresh_token = create_jwt_token({'sub': str(usuario_existente.id), 'type': 'refresh'}, 
                                        timedelta(days=7))

    # Código de Login
    return {'access_token': access_token, 
            'refresh_token': refresh_token}


@router.post('/refresh',
             status_code=status.HTTP_200_OK,
             response_model=LoginResponse,
             summary='Rota para renovar os Tokens de Autenticação')
def refresh(dados: RefreshData, 
                  sessao: Session = Depends(obter_sessao)):

    token = dados.refresh_token

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id = payload.get('sub')
        if payload.get('type') != 'refresh':
            raise InvalidTokenError()
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Token de renovação inválido!'
        )

    access_token = create_jwt_token({'sub': str(usuario_id), 'type': 'access'}, 
                                                   timedelta(minutes=7))
    refresh_token = create_jwt_token({'sub': str(usuario_id), 'type': 'refresh'}, 
                                            timedelta(days=7))
    return {'access_token': access_token, 
                'refresh_token': refresh_token}


@router.post('/{usuario_id}/promover',
             summary='Promove um usuário CLIENTE para perfil LOGISTA')
def promover(usuario_id: int,
             usuario: Annotated[Usuario, Depends(verificar_perfil([UsuarioPerfil.ADMIN]))],):

    ...

@router.get('/me',
            response_model=UsuarioResponse,
            status_code=status.HTTP_200_OK,
            summary='Retorna detalhes do usuário logado.')
def me(usuario: Annotated[Usuario, Depends(obter_usuario_atual)]):
    return usuario