"""Ler o robots.txt e perguntar: posso coletar isto?"""
from urllib.robotparser import RobotFileParser

import requests

BASE = "http://127.0.0.1:8080"
SEU_AGENTE = "MuralColetaBot/1.0 (projeto de estudo; contato: voce@example.com)"

texto = requests.get(f"{BASE}/robots.txt", timeout=10).text
print(texto)

robots = RobotFileParser()
robots.parse(texto.splitlines())

for agente, caminho in [(SEU_AGENTE, "/vagas/"), (SEU_AGENTE, "/eventos/"),
                        (SEU_AGENTE, "/interno/relatorio"),
                        ("BotAbusivo/1.0", "/vagas/")]:
    pode = robots.can_fetch(agente, f"{BASE}{caminho}")
    print(f"{agente.split('/')[0]:14} {caminho:22} pode? {pode}")

print("Crawl-delay para o seu agente:", robots.crawl_delay(SEU_AGENTE))

print("--- o robots.txt é um pedido, e não uma tranca")
proibida = requests.get(f"{BASE}/interno/relatorio", timeout=10)
print("a página proibida responde:", proibida.status_code, "(o servidor não impede)")
