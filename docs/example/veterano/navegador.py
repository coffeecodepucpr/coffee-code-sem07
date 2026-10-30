"""Opções para usar um Chromium próprio, só se você precisar.

No uso normal, NÃO defina nenhuma variável: o Playwright usa o navegador que
o comando `playwright install chromium` baixou, e o Selenium 4 acha o driver.
"""
import os
import shlex


def opcoes_playwright() -> dict:
    caminho = os.environ.get("CHROMIUM_PATH")
    if not caminho:
        return {}
    args = shlex.split(os.environ.get("CHROMIUM_ARGS", ""))
    return {"executable_path": caminho, "args": args}


def opcoes_selenium():
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    opcoes = Options()
    opcoes.add_argument("--headless=new")
    servico = None
    caminho = os.environ.get("CHROMIUM_PATH")
    if caminho:
        opcoes.binary_location = caminho
        for argumento in shlex.split(os.environ.get("CHROMIUM_ARGS", "")):
            opcoes.add_argument(argumento)
    driver = os.environ.get("CHROMEDRIVER_PATH")
    if driver:
        servico = Service(executable_path=driver)
    return opcoes, servico
