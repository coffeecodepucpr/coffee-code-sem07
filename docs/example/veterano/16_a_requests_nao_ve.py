"""O que o requests recebe de uma página montada por JavaScript."""
import requests
from bs4 import BeautifulSoup

BASE = "http://127.0.0.1:8080"

resposta = requests.get(f"{BASE}/vagas-js/", timeout=10)
sopa = BeautifulSoup(resposta.content, "lxml")
print("status:", resposta.status_code)
print("cartões na página:", len(sopa.select("article.vaga")))
print("texto do #resultado:", sopa.select_one("#resultado").get_text())
print("há um <script> no HTML?", sopa.find("script") is not None)
