import asyncio
import httpx
from datetime import datetime

test_data = [
    {"cpf": "04444974125", "client_id": "vini"},
    {"cpf": "47079640873", "client_id": "liossi"},
    {"cpf": "05242199156", "client_id": "cadu"},
    {"cpf": "69314497100", "client_id": "paiVini"},
    {"cpf": "46567216115", "client_id": "paiPedrin"},
    {"cpf": "03529129100", "client_id": "otavio"},
    {"cpf": "07309330161", "client_id": "pedrin"},
    {"cpf": "28131565823", "client_id": "maeZe"},
    {"cpf": "38876252851", "client_id": "paIcadu"},
    {"cpf": "61638125228", "client_id": "teste"},
]

PROXY_URL = "http://127.0.0.1:8000/api/score"

async def send_request(session, cpf, client_id):
    start_time = datetime.now()
    try:
        params = {"cpf": cpf, "client_id": client_id}
        response = await session.get(PROXY_URL, params=params)
        elapsed = (datetime.now() - start_time).total_seconds()
        data = response.json()
        score = data.get("score", data.get("error", "N/A"))
        print(f"[{datetime.now()}] CPF: {cpf}, Client: {client_id}, Score: {score}, Tempo: {elapsed:.2f}s")
    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"[{datetime.now()}] CPF: {cpf}, Client: {client_id}, ERRO: {e}, Tempo: {elapsed:.2f}s")

async def main():
    async with httpx.AsyncClient(timeout=40.0) as client:
        tasks = []

        # Envia 2 requisições para cada cliente (simultâneo)
        for data in test_data:
            for _ in range(1):  # repete para testar cache/deduplicação
                tasks.append(send_request(client, data["cpf"], data["client_id"]))

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
