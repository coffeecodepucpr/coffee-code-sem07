"""A espera do Selenium: o intervalo entre verificações e o Timeout."""
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from navegador import opcoes_selenium

BASE = "http://127.0.0.1:8080"

opcoes, servico = opcoes_selenium()
driver = webdriver.Chrome(options=opcoes, service=servico)
try:
    driver.get(f"{BASE}/vagas-js/")

    print("--- esperar por algo que nunca aparece")
    inicio = time.perf_counter()
    try:
        WebDriverWait(driver, timeout=1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".nao-existe")))
    except TimeoutException as erro:
        gasto = time.perf_counter() - inicio
        print(f"TimeoutException depois de {gasto:.1f} s | "
              f"mensagem: {erro.msg!r}")

    print("--- a espera olha de tempos em tempos (por padrão, a cada 0,5 s)")
    espera = WebDriverWait(driver, timeout=5, poll_frequency=0.1)
    print("intervalo entre as verificações:", espera._poll, "s")
    espera.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "article.vaga")))
    print("cartões:", len(driver.find_elements(By.CSS_SELECTOR, "article.vaga")))
    print("intervalo padrão:", WebDriverWait(driver, 5)._poll, "s")
finally:
    driver.quit()
