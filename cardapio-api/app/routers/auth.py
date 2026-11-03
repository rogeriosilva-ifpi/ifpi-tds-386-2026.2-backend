from fastapi import APIRouter

router = APIRouter(prefix='/auth', tags=["Autenticação"])

# Criar os endpoints
@router.get('/me') # /auth/me
def me():
    # Retorno Fake
    return 'Sou Rogério'


@router.post('/login')
def login():
    return 'Autenticado com sucesso!'