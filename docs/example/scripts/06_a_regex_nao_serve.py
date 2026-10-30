"""Por que expressões regulares não são o caminho para ler HTML."""
import re

import requests

BASE = "http://127.0.0.1:8080"
html = requests.get(f"{BASE}/vagas/", timeout=10).text

# Tentativa 1: procurar <h2>título</h2>
achados = re.findall(r"<h2>(.*?)</h2>", html)
print("regex <h2>...</h2> achou:", len(achados))

# Tentativa 2: aceitar o atributo class, mas o título está dentro de um <a>
achados = re.findall(r'<h2 class="titulo">(.*?)</h2>', html)
print("regex com class achou:", len(achados))
print("primeiro resultado:", achados[0])
