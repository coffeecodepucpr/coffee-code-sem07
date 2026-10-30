"""Quem é você? O User-Agent, e a sessão que o repete em todo pedido."""
import requests

BASE = "http://127.0.0.1:8080"

padrao = requests.get(f"{BASE}/eco", timeout=10).json()
print("User-Agent padrão:", padrao["user-agent"])

USER_AGENT = "MuralColetaBot/1.0 (projeto de estudo; contato: voce@example.com)"
sessao = requests.Session()
sessao.headers["User-Agent"] = USER_AGENT

for numero in (1, 2):
    eco = sessao.get(f"{BASE}/eco", timeout=10).json()
    print(f"pedido {numero} pela sessão:", eco["user-agent"])
print("a sessão reaproveita a conexão:", eco["connection"])
