import asyncio
import httpx
from datetime import datetime

# Lista de CPFs e client-ids para testar múltiplos clientes
test_data = [
    {"cpf": "04444974125", "client_id": "vini"},
    {"cpf": "47079640873", "client_id": "liossi"},
    {"cpf": "05242199156", "client_id": "cadu"},
    {"cpf": "69314497100", "client_id": "paivini"},
    {"cpf": "46567216115", "client_id": "paipedrin"},
    {"cpf": "03529129100", "client_id": "tatabl"},
    {"cpf": "07309330161", "client_id": "pedrin"},
    {"cpf": "28131565823", "client_id": "maeze"},
    {"cpf": "38876252851", "client_id": "paicadu"},
    {"cpf": "61638125228", "client_id": "sete"},
]

# URL base do seu proxy local ou externo
PROXY_URL = "https://score.hsborges.dev/api/score?"

async def send_request(session, cpf, client_id):
    """Envia uma requisição para o proxy e retorna o resultado"""
    params = {"cpf": cpf}  # CPF continua como query param
    headers = {"client-id": client_id}  # client_id enviado como header
    start_time = datetime.now()
    response = await session.get(PROXY_URL, params=params, headers=headers)
    elapsed = (datetime.now() - start_time).total_seconds()
    try:
        content = response.json()
        score = content.get("score", "N/A")  # Mostra apenas o score
        print(f"[{datetime.now()}] CPF: {cpf}, Client: {client_id}, Score: {score}, Tempo: {elapsed:.2f}s")
    except:
        # Se não conseguir decodificar JSON, mostra apenas erro
        print(f"[{datetime.now()}] CPF: {cpf}, Client: {client_id}, Erro ao ler resposta, Tempo: {elapsed:.2f}s")

async def main():
    async with httpx.AsyncClient() as client:
        tasks = []

        # Envia 5 requisições para cada cliente simultaneamente
        for data in test_data:
                tasks.append(send_request(client, data["cpf"], data["client_id"]))

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
