"""Playwright: abrir a página de verdade, esperar o JavaScript e extrair."""
import asyncio

from playwright.async_api import async_playwright

from navegador import opcoes_playwright

BASE = "http://127.0.0.1:8080"


async def main():
    async with async_playwright() as p:
        navegador = await p.chromium.launch(**opcoes_playwright())
        pagina = await navegador.new_page()
        await pagina.goto(f"{BASE}/vagas-js/")

        cartoes = pagina.locator("article.vaga")
        print("logo depois do goto:", await cartoes.count(), "cartões")
        print("texto do #resultado:", await pagina.inner_text("#resultado"))

        await cartoes.first.wait_for()          # espera o JavaScript terminar
        print("depois de esperar:", await cartoes.count(), "cartões")

        titulos = await pagina.eval_on_selector_all(
            "article.vaga h2.titulo", "els => els.map(e => e.textContent)")
        print("primeiros títulos:", titulos[:3])
        primeiro = cartoes.first
        print("data-id do primeiro:", await primeiro.get_attribute("data-id"))
        empresa = await primeiro.locator(".empresa").inner_text()
        print("empresa do primeiro:", empresa)
        await navegador.close()


asyncio.run(main())
