"""O servidor diz quanto esperar: o cabeçalho Retry-After."""
import time

import requests

BASE = "http://127.0.0.1:8080"

for numero in range(1, 6):
    resposta = requests.get(f"{BASE}/limitado/vagas", timeout=10)
    print(f"pedido {numero}: HTTP {resposta.status_code}")
    if resposta.status_code == 429:
        pedido = float(resposta.headers["Retry-After"])
        print(f"   o servidor pediu {pedido:.0f} s: eu espero esse tempo")
        time.sleep(pedido)
