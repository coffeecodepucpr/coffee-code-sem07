"""Selenium: a mesma coleta, com esperas explícitas."""
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from navegador import opcoes_selenium

BASE = "http://127.0.0.1:8080"

opcoes, servico = opcoes_selenium()
driver = webdriver.Chrome(options=opcoes, service=servico)
try:
    driver.get(f"{BASE}/vagas-js/")
    CARTAO = (By.CSS_SELECTOR, "article.vaga")
    print("logo depois do get:", len(driver.find_elements(*CARTAO)), "cartões")
    print("texto do #resultado:", driver.find_element(By.ID, "resultado").text)

    espera = WebDriverWait(driver, timeout=5)
    espera.until(EC.presence_of_element_located(CARTAO))
    cartoes = driver.find_elements(*CARTAO)
    print("depois de esperar:", len(cartoes), "cartões")
    titulos = [c.find_element(By.CSS_SELECTOR, "h2.titulo").text
               for c in cartoes[:3]]
    print("primeiros títulos:", titulos)
    print("data-id do primeiro:", cartoes[0].get_attribute("data-id"))

    print("--- find_elements não reclama quando não acha; find_element reclama")
    print("find_elements:", driver.find_elements(By.CSS_SELECTOR, ".nao-existe"))
    try:
        driver.find_element(By.CSS_SELECTOR, ".nao-existe")
    except NoSuchElementException as erro:
        print("NoSuchElementException:", erro.msg.splitlines()[0])
finally:
    driver.quit()
