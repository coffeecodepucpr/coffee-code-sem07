"""A armadilha: paginar 'até a página vir vazia' nunca termina neste site."""
import requests

from parsers import ler_html, ler_vagas_da_pagina

BASE = "http://127.0.0.1:8080"
MAX_PAGINAS = 6          # a trava de segurança que salva o programa

for numero in range(1, MAX_PAGINAS + 1):
    url = f"{BASE}/vagas/"
    sopa = ler_html(requests.get(url, params={"pagina": numero}, timeout=10))
    vagas = ler_vagas_da_pagina(sopa, url)
    rotulo = sopa.select_one(".paginacao span").get_text()
    ids = [v["id_externo"] for v in vagas]
    print(f"pedi a página {numero}: {len(vagas)} vagas | {rotulo} | {ids[0]}..{ids[-1]}")
