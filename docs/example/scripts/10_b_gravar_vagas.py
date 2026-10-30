"""Gravar as vagas coletadas, sem duplicar, e dizer o que mudou."""
import sqlite3
import sys

import requests

from limpeza import limpar_texto, parse_faixa_salarial
from parsers import ler_html, ler_vagas_da_pagina, proxima_pagina

BASE = "http://127.0.0.1:8080"
CAMINHO = sys.argv[1] if len(sys.argv) > 1 else "vagas_demo.db"

conn = sqlite3.connect(CAMINHO)
conn.row_factory = sqlite3.Row
conn.execute("""
    CREATE TABLE IF NOT EXISTS vagas (
        id_externo  TEXT PRIMARY KEY,
        titulo      TEXT NOT NULL,
        empresa     TEXT,
        salario_min INTEGER,
        salario_max INTEGER
    )
""")


def coletar():
    url, vagas = f"{BASE}/vagas/", []
    while url:
        sopa = ler_html(requests.get(url, timeout=10))
        vagas += ler_vagas_da_pagina(sopa, url)
        url = proxima_pagina(sopa, url)
    return vagas


def gravar(vaga):
    minimo, maximo = parse_faixa_salarial(vaga["salario"])
    novo = (limpar_texto(vaga["titulo"]), limpar_texto(vaga["empresa"]),
            minimo, maximo)
    antigo = conn.execute(
        "SELECT titulo, empresa, salario_min, salario_max FROM vagas "
        "WHERE id_externo = ?", (vaga["id_externo"],)).fetchone()
    if antigo is not None and tuple(antigo) == novo:
        return "igual"
    conn.execute(
        "INSERT INTO vagas VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT (id_externo) DO UPDATE SET titulo = excluded.titulo, "
        "empresa = excluded.empresa, salario_min = excluded.salario_min, "
        "salario_max = excluded.salario_max",
        (vaga["id_externo"], *novo))
    return "nova" if antigo is None else "atualizada"


resultados = {"nova": 0, "atualizada": 0, "igual": 0}
with conn:
    for vaga in coletar():
        resultados[gravar(vaga)] += 1
print("resultado desta execução:", resultados)
print("vagas no banco:", conn.execute("SELECT count(*) FROM vagas").fetchone()[0])
