"""O primeiro scraper: todas as vagas, com o detalhe de cada uma."""
import json
import time
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests

from parsers import ler_descricao, ler_html, ler_vagas_da_pagina, proxima_pagina

BASE = "http://127.0.0.1:8080"
USER_AGENT = "MuralColetaBot/1.0 (projeto de estudo; contato: voce@example.com)"
MAX_PAGINAS = 20

sessao = requests.Session()
sessao.headers["User-Agent"] = USER_AGENT

robots = RobotFileParser()
robots.parse(sessao.get(f"{BASE}/robots.txt", timeout=10).text.splitlines())
espera = float(robots.crawl_delay(USER_AGENT) or 0)
print(f"robots.txt lido. Espera entre pedidos: {espera} s")


def baixar(url):
    if not robots.can_fetch(USER_AGENT, url):
        raise RuntimeError(f"o robots.txt não permite {url}")
    time.sleep(espera)
    resposta = sessao.get(url, timeout=10)
    resposta.raise_for_status()
    return ler_html(resposta)


inicio = time.perf_counter()
vagas, visitadas = [], set()
url = urljoin(BASE, "/vagas/")
while url and url not in visitadas and len(visitadas) < MAX_PAGINAS:
    visitadas.add(url)
    sopa = baixar(url)
    da_pagina = ler_vagas_da_pagina(sopa, url)
    print(f"página {len(visitadas)}: {len(da_pagina)} vagas")
    for vaga in da_pagina:
        vaga["descricao"] = ler_descricao(baixar(vaga["url"]))
        vagas.append(vaga)
    url = proxima_pagina(sopa, url)

with open("vagas.json", "w", encoding="utf-8") as arquivo:
    json.dump(vagas, arquivo, ensure_ascii=False, indent=2)

print(f"total: {len(vagas)} vagas em {len(visitadas)} páginas")
print(f"tempo: {time.perf_counter() - inicio:.0f} s")
print("primeira:", vagas[0]["titulo"], "|", vagas[0]["empresa"])
print("descrição:", vagas[0]["descricao"][:50] + "...")
