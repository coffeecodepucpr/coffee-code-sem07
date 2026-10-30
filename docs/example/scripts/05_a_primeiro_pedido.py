"""O primeiro pedido com requests: o que vem na resposta."""
import requests

BASE = "http://127.0.0.1:8080"

resposta = requests.get(f"{BASE}/vagas/", timeout=10)
print("status:", resposta.status_code, "| ok:", resposta.ok)
print("url final:", resposta.url)
print("content-type:", resposta.headers["Content-Type"])
print("etag:", resposta.headers["ETag"])
print("tamanho em bytes:", len(resposta.content))
print("tipo de .content:", type(resposta.content).__name__)
print("tipo de .text:", type(resposta.text).__name__)
print("encoding:", resposta.encoding)
print("tempo da resposta:", resposta.elapsed.total_seconds() < 1)

print("--- um redirecionamento")
antigo = requests.get(f"{BASE}/antigo/vagas", timeout=10)
print("status final:", antigo.status_code, "| url final:", antigo.url)
caminho = [(r.status_code, r.headers["Location"]) for r in antigo.history]
print("histórico:", caminho)
sem_seguir = requests.get(f"{BASE}/antigo/vagas", allow_redirects=False,
                          timeout=10)
print("sem seguir:", sem_seguir.status_code, sem_seguir.headers["Location"])

print("--- parâmetros na URL")
com_params = requests.get(f"{BASE}/vagas/", params={"pagina": 2}, timeout=10)
print(com_params.url)
