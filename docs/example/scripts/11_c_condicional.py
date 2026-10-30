"""Perguntar 'mudou?' antes de baixar de novo: ETag e If-None-Match."""
import requests

BASE = "http://127.0.0.1:8080"
url = f"{BASE}/vagas/"

primeira = requests.get(url, timeout=10)
etag = primeira.headers["ETag"]
print("1ª vez:", primeira.status_code, "| bytes recebidos:", len(primeira.content))
print("ETag guardada:", etag)

segunda = requests.get(url, headers={"If-None-Match": etag}, timeout=10)
print("2ª vez:", segunda.status_code, "| bytes recebidos:", len(segunda.content))

outra = requests.get(url, params={"pagina": 2}, timeout=10)
print("página 2 tem outra ETag:", outra.headers["ETag"] != etag)

requests.get(f"{BASE}/_dev/dia/2", timeout=10)
mudou = requests.get(url, headers={"If-None-Match": etag}, timeout=10)
print("no dia seguinte:", mudou.status_code, "| bytes recebidos:", len(mudou.content))
requests.get(f"{BASE}/_dev/dia/1", timeout=10)
