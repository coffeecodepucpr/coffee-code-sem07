"""O que dá errado em um pedido, e o tempo limite."""
import time

import requests

BASE = "http://127.0.0.1:8080"

print("--- sem timeout, o programa espera o tempo que o servidor quiser")
inicio = time.perf_counter()
requests.get(f"{BASE}/lento")
print(f"esperou {time.perf_counter() - inicio:.1f} s")

print("--- com timeout, a espera tem limite")
inicio = time.perf_counter()
try:
    requests.get(f"{BASE}/lento", timeout=1)
except requests.exceptions.ReadTimeout as erro:
    print(f"ReadTimeout depois de {time.perf_counter() - inicio:.1f} s")
    print("é um Timeout?", isinstance(erro, requests.exceptions.Timeout))

print("--- o servidor não existe")
try:
    requests.get("http://127.0.0.1:9/", timeout=3)
except requests.exceptions.ConnectionError as erro:
    print("ConnectionError:", type(erro.args[0]).__name__)

print("--- a página não existe")
resposta = requests.get(f"{BASE}/vagas/v999", timeout=10)
print("status:", resposta.status_code, "| ok:", resposta.ok)
try:
    resposta.raise_for_status()
except requests.exceptions.HTTPError as erro:
    print("HTTPError:", erro)
