from fastapi import FastAPI

app = FastAPI()

# endpoints
@app.get("/")
def raiz():
    return {"mensagem": "API do Cardápio no AR!"}


@app.get("/hello")
def home():
    return {"mensagem": "Olá Rogério! Tudo bem?!"}


# {item_id} --> Route ou Path Param, Parâmetro de Rota
@app.get("/cardapio/{item_id}")
def obter_item(item_id: int):
    resultado = {
        "item": f"Você solicitou o item {item_id}"
    }
    return resultado