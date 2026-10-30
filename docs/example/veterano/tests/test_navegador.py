"""Testes com navegador de verdade. Pulam sozinhos se não houver navegador."""
import asyncio

import pytest
import requests

pytestmark = pytest.mark.navegador
playwright = pytest.importorskip("playwright.async_api")

from navegador import opcoes_playwright  # noqa: E402


async def _com_pagina(site, corpo):
    async with playwright.async_playwright() as p:
        try:
            navegador = await p.chromium.launch(**opcoes_playwright())
        except Exception as erro:             # navegador não instalado
            pytest.skip(f"sem navegador: {str(erro).splitlines()[0][:80]}")
        try:
            pagina = await navegador.new_page()
            return await corpo(pagina)
        finally:
            await navegador.close()


def test_requests_nao_enxerga_a_pagina_montada_por_javascript(site):
    html = requests.get(f"{site}/vagas-js/", timeout=5).text
    assert 'class="vaga"' not in html
    assert "Carregando..." in html


def test_playwright_espera_o_javascript_e_acha_as_vagas(site):
    async def corpo(pagina):
        await pagina.goto(f"{site}/vagas-js/")
        cartoes = pagina.locator("article.vaga")
        antes = await cartoes.count()
        await cartoes.first.wait_for()
        depois = await cartoes.count()
        primeiro = await cartoes.first.get_attribute("data-id")
        return antes, depois, primeiro

    assert asyncio.run(_com_pagina(site, corpo)) == (0, 8, "v002")


def test_playwright_captura_a_chamada_a_api_da_pagina(site):
    async def corpo(pagina):
        async with pagina.expect_response("**/api/vagas*") as espera:
            await pagina.goto(f"{site}/vagas-js/")
        resposta = await espera.value
        return resposta.status, (await resposta.json())["total"]

    assert asyncio.run(_com_pagina(site, corpo)) == (200, 20)


def test_locator_com_varios_elementos_viola_o_modo_estrito(site):
    async def corpo(pagina):
        await pagina.goto(f"{site}/vagas-js/")
        await pagina.locator("article.vaga").first.wait_for()
        with pytest.raises(playwright.Error, match="strict mode violation"):
            await pagina.locator("article.vaga").inner_text()
        return True

    assert asyncio.run(_com_pagina(site, corpo))


def test_selenium_espera_explicita_acha_os_cartoes(site):
    selenium = pytest.importorskip("selenium.webdriver")
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    from navegador import opcoes_selenium

    opcoes, servico = opcoes_selenium()
    try:
        driver = selenium.Chrome(options=opcoes, service=servico)
    except Exception as erro:
        pytest.skip(f"sem driver ou navegador: {str(erro).splitlines()[0][:80]}")
    try:
        driver.get(f"{site}/vagas-js/")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article.vaga")))
        assert len(driver.find_elements(By.CSS_SELECTOR, "article.vaga")) == 8
    finally:
        driver.quit()
