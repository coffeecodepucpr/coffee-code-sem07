"""O atalho: a página busca os dados em uma API, e você pode usá-la direto."""
import asyncio

import httpx
from playwright.async_api import async_playwright

from navegador import opcoes_playwright

BASE = "http://127.0.0.1:8080"


async def main():
    async with async_playwright() as p:
        navegador = await p.chromium.launch(**opcoes_playwright())
        pagina = await navegador.new_page()
        chamadas = []
        pagina.on("request",
                  lambda r: chamadas.append((r.resource_type, r.url)))
        async with pagina.expect_response("**/api/vagas*") as espera:
            await pagina.goto(f"{BASE}/vagas-js/")
        resposta = await espera.value
        dados = await resposta.json()
        print("a página chamou:", resposta.url)
        print("status:", resposta.status, "| total:", dados["total"],
              "| itens:", len(dados["itens"]))
        api = [u.replace(BASE, "") for tipo, u in chamadas
               if tipo in ("fetch", "xhr")]
        print("chamadas fetch/xhr:", api)
        await navegador.close()

    print("--- o atalho, sem navegador nenhum")
    async with httpx.AsyncClient(base_url=BASE) as cliente:
        resposta2 = await cliente.get(
            "/api/vagas", params={"pagina": 2, "por_pagina": 8})
        pagina2 = resposta2.json()
    print("página 2 direto da API:", [v["id"] for v in pagina2["itens"]])


asyncio.run(main())
