"""O segundo scraper: eventos, reaproveitando o que já existe."""
import requests

from limpeza import limpar_texto, parse_data_evento, parse_preco
from parsers import ler_eventos, ler_html

BASE = "http://127.0.0.1:8080"
url = f"{BASE}/eventos/"
sopa = ler_html(requests.get(url, timeout=10))

eventos = []
for bruto in ler_eventos(sopa, url):
    preco, preco_estudante = parse_preco(bruto["preco"])
    onde = limpar_texto(bruto["onde"])
    eventos.append({
        "id": bruto["id_externo"],
        "titulo": bruto["titulo"],
        "inicio": parse_data_evento(bruto["quando"]),
        "local": onde,
        "online": (onde or "").lower() == "online",
        "preco_centavos": preco,
        "preco_estudante_centavos": preco_estudante,
    })

print("eventos coletados:", len(eventos))
for e in eventos[:3]:
    print(e)
print("online:", [e["id"] for e in eventos if e["online"]])
print("gratuitos:", [e["id"] for e in eventos if e["preco_centavos"] == 0])
print("sem data:", [e["id"] for e in eventos if e["inicio"] is None])
