"""Os dois erros mais comuns do Playwright."""
import asyncio

from playwright.async_api import Error, TimeoutError, async_playwright

from navegador import opcoes_playwright

BASE = "http://127.0.0.1:8080"


async def main():
    async with async_playwright() as p:
        navegador = await p.chromium.launch(**opcoes_playwright())
        pagina = await navegador.new_page()
        await pagina.goto(f"{BASE}/vagas-js/")
        await pagina.locator("article.vaga").first.wait_for()

        print("--- 1) o seletor casa com VÁRIOS elementos e você pede um texto")
        try:
            await pagina.locator("article.vaga").inner_text()
        except Error as erro:
            print(type(erro).__name__ + ":", str(erro).splitlines()[0][:110])

        print("--- 2) esperar por algo que nunca aparece")
        try:
            await pagina.wait_for_selector(".nao-existe", timeout=1000)
        except TimeoutError as erro:
            print(type(erro).__name__ + ":", str(erro).splitlines()[0])
        await navegador.close()


asyncio.run(main())
