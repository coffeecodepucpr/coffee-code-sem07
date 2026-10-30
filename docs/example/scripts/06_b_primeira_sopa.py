"""A primeira sopa: baixar uma página e navegar pela árvore."""
import requests
from bs4 import BeautifulSoup

BASE = "http://127.0.0.1:8080"
resposta = requests.get(f"{BASE}/vagas/", timeout=10)
resposta.raise_for_status()

sopa = BeautifulSoup(resposta.content, "lxml")
print("tipo:", type(sopa).__name__)
print("título da página:", sopa.title.get_text())
print("h1:", sopa.h1.get_text())

cartoes = sopa.find_all("article", class_="vaga")
print("cartões:", len(cartoes), "| tipo:", type(cartoes).__name__)

primeiro = cartoes[0]
print("id:", primeiro["data-id"])
print("título:", primeiro.h2.get_text(strip=True))
print("empresa:", primeiro.find("p", class_="empresa").get_text(strip=True))

link = primeiro.find("a")
print("link:", link["href"])
print("atributos do link:", link.attrs)

hora = primeiro.find("time")
print("datetime:", hora["datetime"], "| texto:", hora.get_text())
print("classes:", primeiro["class"])
print("atributo que não existe, com .get:", primeiro.get("data-xyz"))
print("com valor padrão:", primeiro.get("data-xyz", "padrão"))
