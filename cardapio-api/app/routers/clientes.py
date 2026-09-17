from fastapi import APIRouter

router = APIRouter(prefix='/clientes', tags=["Clientes"])

# EndsPoint METHOD + PATH, ex.: "GET /clientes/18"
@router.get('/')
def listar_clientes():
    return ['Rogério', 'Daniel Pereira', 'Daniel Santos']


@router.get('/{id}')
def obter_cliente(id: int):
    return f'Cliente de ID={id}'


@router.post('/')
def criar_cliente():
    return ''


@router.put('/{id}')
def atualizar_cliente(id: int):
    return ''
