"""Tentar de novo, esperando cada vez mais."""
import time
import uuid

import requests

BASE = "http://127.0.0.1:8080"


def baixar_com_tentativas(url, tentativas=4, base=0.5):
    for numero in range(1, tentativas + 1):
        inicio = time.perf_counter()
        resposta = requests.get(url, timeout=10)
        gasto = time.perf_counter() - inicio
        print(f"tentativa {numero}: HTTP {resposta.status_code} ({gasto:.2f} s)")
        if resposta.status_code < 500:
            return resposta
        if numero < tentativas:
            espera = base * 2 ** (numero - 1)
            print(f"   servidor indisponível: esperando {espera} s")
            time.sleep(espera)
    raise RuntimeError(f"{url}: sem sucesso em {tentativas} tentativas")


chave = uuid.uuid4().hex     # cada execução começa do zero
resposta = baixar_com_tentativas(f"{BASE}/instavel/vagas?chave={chave}&falhas=2")
print("deu certo:", resposta.status_code, "| bytes:", len(resposta.content))
