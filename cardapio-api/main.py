from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get('/')
def raiz():
    resultado = {'mensagem': 'API cardápio no AR'}
    return resultado


@app.get('/hello')
def saudacao():
    nome = 'Rogério Silva'
    resultado = {
        'mensagem': f'Olá {nome}! Boa noite!'
    }
    return resultado

# Lista de Itens do Cardápio
itens = [
        {'id': 10, 'nome': 'Filé com Fritas', 'disponivel': False},
        {'id': 15, 'nome': 'Pão c/ Carne de sol (3und)', 'disponivel': True},
        {'id': 25, 'nome': 'Pastel de Queijo (6und)', 'disponivel': False}
    ]

#Query Param
@app.get('/cardapio') 
def cardapio(disponivel: bool):
    itens_filtrados = []

    for item in itens:
        if item['disponivel'] == disponivel:
            itens_filtrados.append(item)

    return itens_filtrados

# Path Param
@app.get('/cardapio/{item_id}') 
def obter_item(item_id: int): 
    for item in itens:
        if item['id'] == item_id:
            return item

    raise HTTPException(status_code=404, 
                        detail=f'Item não localizado com id={item_id}.')
