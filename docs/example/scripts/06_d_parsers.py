"""O mesmo HTML quebrado, lido por dois parsers."""
import requests
from bs4 import BeautifulSoup

BASE = "http://127.0.0.1:8080"
bruto = requests.get(f"{BASE}/quebrado/", timeout=10).content

for parser in ("html.parser", "lxml"):
    sopa = BeautifulSoup(bruto, parser)
    print(f"--- {parser}")
    print("itens da lista (li):", len(sopa.find_all("li")))
    primeiro_li = sopa.find("li")
    print("o primeiro li contém outro li?", primeiro_li.find("li") is not None)
    print("parágrafos (p):", len(sopa.find_all("p")))
    print(str(sopa.body)[:140].replace("\n", " "))
