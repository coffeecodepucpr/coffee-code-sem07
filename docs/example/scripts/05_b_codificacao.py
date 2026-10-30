"""O erro de acento: .text contra .content."""
import requests
from bs4 import BeautifulSoup

BASE = "http://127.0.0.1:8080"

certa = requests.get(f"{BASE}/vagas/", timeout=10)
legado = requests.get(f"{BASE}/legado/vagas", timeout=10)
print("cabeçalho da página certa :", certa.headers["Content-Type"])
print("cabeçalho da página legado:", legado.headers["Content-Type"])
print("encoding que o requests supôs:", legado.encoding)

for nome, r in (("certa", certa), ("legado", legado)):
    trecho = BeautifulSoup(r.content, "lxml").select_one(".paginacao span")
    inicio = r.text.index("<span>P") + 6
    print(f"{nome:6} .text -> {r.text[inicio:inicio + 14]!r}"
          f" | BeautifulSoup(.content) -> {trecho.get_text()!r}")
