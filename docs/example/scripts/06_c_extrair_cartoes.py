"""Extrair todos os cartões de uma página, com seletores CSS."""
import requests
from bs4 import BeautifulSoup

BASE = "http://127.0.0.1:8080"


def texto(tag):
    """O texto limpo de uma tag, ou None se a tag não existe."""
    return tag.get_text(strip=True) if tag is not None else None


def ler_cartao(cartao):
    return {
        "id": cartao["data-id"],
        "titulo": texto(cartao.select_one("h2.titulo a")),
        "empresa": texto(cartao.select_one(".empresa")),
        "local": texto(cartao.select_one(".local")),
        "salario": texto(cartao.select_one(".salario")),
        "publicada": cartao.select_one("time")["datetime"],
        "tags": [li.get_text(strip=True) for li in cartao.select("ul.tags li")],
        "link": cartao.select_one("h2.titulo a")["href"],
    }


resposta = requests.get(f"{BASE}/vagas/", timeout=10)
resposta.raise_for_status()
sopa = BeautifulSoup(resposta.content, "lxml")

vagas = [ler_cartao(c) for c in sopa.select("article.vaga")]
print("vagas extraídas:", len(vagas))
for v in vagas[:3]:
    print(v)

print("só os títulos:", [v["titulo"] for v in vagas[:3]])
print("com 'python' nas tags:", [v["id"] for v in vagas if "python" in v["tags"]])
