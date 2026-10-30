"""Sequencial contra assíncrono, medidos no mesmo servidor (com latência)."""
import asyncio
import time

import requests

from coletor_async import coletar

BASE = "http://127.0.0.1:8080"


def sequencial():
    sessao = requests.Session()
    paginas = [f"{BASE}/vagas/?pagina={n}" for n in (1, 2, 3)]
    total = 0
    for url in paginas:
        sessao.get(url, timeout=10)
        total += 1
    for numero in range(1, 21):
        sessao.get(f"{BASE}/vagas/v{numero:03d}", timeout=10)
        total += 1
    return total


requests.get(f"{BASE}/_dev/latencia?valor=0.2")   # cada resposta demora 0,2 s

inicio = time.perf_counter()
pedidos = sequencial()
print(f"sequencial (requests):        {pedidos} pedidos em "
      f"{time.perf_counter() - inicio:.1f} s")

for concorrencia, intervalo in [(5, 0.0), (10, 0.0), (5, 0.2)]:
    inicio = time.perf_counter()
    vagas = asyncio.run(coletar(BASE, concorrencia, intervalo))
    print(f"assíncrono (conc. {concorrencia:2}, intervalo {intervalo} s): "
          f"{len(vagas)} vagas em {time.perf_counter() - inicio:.1f} s")

requests.get(f"{BASE}/_dev/latencia?valor=0")
