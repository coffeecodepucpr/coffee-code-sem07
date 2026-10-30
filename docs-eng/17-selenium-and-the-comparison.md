# Module 17, Selenium and the Comparison

[Português](../docs/17-selenium-e-a-comparacao.md) · English

`WEEK 07 // Data & Scraping, Part 1: Collection` | **Experienced track, bonus**

---

## // Before you start

**Selenium** is the oldest and best-known browser automation tool, widely used for testing sites. This module does **the same task as Module 16** with it, and ends with an honest comparison between the two tools. It is a **bonus** module: Playwright alone already covers what the week asks for.

## // Selenium

Installation: `pip install selenium` (verified at version **4.51.0**). Selenium talks to the browser through an intermediate program, the **driver** (for Chrome, `chromedriver`). According to the Selenium 4 documentation, it usually finds and downloads the right driver on its own, through "Selenium Manager". **This material did not test that path**: the production environment had no access to the download. The tests used a `chromedriver` from the same series as the browser (version 153), pointed to by the `navegador.py` variables. On your computer, in normal use, set nothing, and check the Selenium documentation if something fails at startup.

## // The same collection, with Selenium

This is `17_a_selenium_basico.py`:

```python
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
```

```
logo depois do get: 0 cartões
texto do #resultado: Carregando...
depois de esperar: 8 cartões
primeiros títulos: ['Analista de Dados Pleno',
 'Desenvolvedor(a) Python Júnior', 'Estágio em Desenvolvimento Web']
data-id do primeiro: v002
--- find_elements não reclama quando não acha; find_element reclama
find_elements: []
NoSuchElementException: no such element: Unable to locate element:
 {"method":"css selector","selector":".nao-existe"}
```

(Two lines were broken to fit.) The result is the same as with Playwright: **0 cards** right after opening the page, **8** after waiting. The differences are in the **way** of waiting and searching:

- **The wait is explicit.** In Selenium, you write `WebDriverWait(driver, timeout=5).until(...)`, with the condition (`presence_of_element_located`). Without it, `find_element` fails **right away** if the element does not exist yet.
- **Two verbs for searching.** `find_elements` (plural) returns a **list**, empty if nothing matches. `find_element` (singular) **raises** `NoSuchElementException` if nothing matches.

## // The wait checks from time to time

A surprise the run revealed, which deserves attention. `WebDriverWait` does **not** look continuously: it **checks the condition every 0.5 seconds**, by default. The `17_b_esperar_demais.py` script:

```python
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
```

```
--- esperar por algo que nunca aparece
TimeoutException depois de 1.0 s | mensagem: ''
--- a espera olha de tempos em tempos (por padrão, a cada 0,5 s)
intervalo entre as verificações: 0.1 s
cartões: 8
intervalo padrão: 0.5 s
```

Three facts: (1) waiting for something that **never appears** ends in `TimeoutException`, after the agreed time (1.0 s), and **with an empty message**: do not expect an explanatory text. (2) The interval between checks can be adjusted (`poll_frequency=0.1`). (3) The **default** interval is 0.5 s. That is why a wait with `timeout=0.1` and a 0.5 s check is a conceptual mistake: it only checks at time zero, and runs out before the next check.

## // Playwright × Selenium

The two tools solved **the same problem**, on the same page, and extracted the same 8 cards. This comparison separates what was **observed** from what comes from the **documentation** (and was not tested here):

| Aspect | Playwright | Selenium |
|---|---|---|
| Read the 8 cards from the JavaScript page | Yes (observed) | Yes (observed) |
| How it waits | **Automatically**, before acting; and with `wait_for` for a condition | **Explicitly**: you write `WebDriverWait(...).until(...)` |
| Element that does not exist | `count()` returns `0`, and waiting too long gives `TimeoutError` | `find_elements` returns `[]`, `find_element` raises `NoSuchElementException` |
| Several elements for a single text | Refuses (strict mode) | `find_element` returns **the first**, without complaining (not tested in this material) |
| Discovering the API call the page makes | `expect_response` (observed) | Not the tool's focus (the Selenium documentation covers other features for that) |
| Supported browsers | According to the documentation, Chromium, Firefox and WebKit | According to the documentation, several, through the drivers |
| Driver | Comes built into the browser installation | A separate driver (Selenium Manager tries to handle it) |
| Speed | **Not measured** | **Not measured** |

The choice, then, is less about "which is better" and more about context:

- **Start with the API** (Module 16), if the page has one you may use with permission.
- **For a new browser-based collection project**, Playwright saves you the waiting code, which in Selenium is where people make the most mistakes.
- **If your group already uses Selenium** (in site testing, for example), reusing the knowledge and infrastructure is usually worth more than switching.

## // The tests

In the `veterano/tests/test_navegador.py` file, one test confirms that Selenium, with an explicit wait, finds the 8 cards. Like the other browser tests, it **skips itself** if the browser or the driver is not available.

## // Good example × bad example

**Bad example**: a fixed `sleep`, or the "implicit wait" mixed with the explicit one:

```python
driver.get(url)
time.sleep(3)
```

**Good example**: an explicit wait, for a condition:

```python
WebDriverWait(driver, timeout=5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "article.vaga")))
```

## // Common errors

These messages were obtained by running the code.

| Error | Why it happens | How to fix it |
|---|---|---|
| `NoSuchElementException: no such element: Unable to locate element` | `find_element` found nothing (maybe the page has not been built yet) | Wait with `WebDriverWait`, or use `find_elements` and check the list |
| `TimeoutException` with an empty message | The condition did not become true in the agreed time | Check the selector and the page, and raise the time only if it makes sense |
| A wait that is too short fails, even with a fast page | The check runs every 0.5 s, by default | Adjust `poll_frequency`, or the time |
| The browser "stays open" after the script | The `driver.quit()` is missing | Use `try/finally` |
| The driver does not start | The driver version does not match the browser's, or it was not found | Check the versions, and the Selenium documentation (not reproduced here) |

## // Guided practice

1. Run `17_a_selenium_basico.py` (with Chromium and `chromedriver`, or with Selenium Manager working) and compare it with `16_b`.
2. Run `17_b_esperar_demais.py` and read the 0.5 s default interval.
3. Add to `17_a` a wait for an element that does not exist, and watch the `TimeoutException`.

## // Practice on your own

> **CHALLENGE**
> Write the same extraction (title and `data-id` of the 8 cards on `/vagas-js/`) **twice**, with Playwright and with Selenium, and compare: how many lines does each one have? Where is the wait in each one? Expected result: the same 8 pairs (`v002` and `Analista de Dados Pleno` first), and a clear difference in the part that handles the wait.

## // Applying it to the week's project

1. In `anotacoes.md`, write the three questions you ask before choosing between the API, Playwright and Selenium.
2. Choose **one** of the two browser tools for your project, and justify the choice in two sentences.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> Your Selenium script runs fine on your computer, and fails now and then on another, slower one, with `NoSuchElementException`. What is happening, and what is the fix?

Answer: the slower computer builds the page **after** the moment the script already searched for the element. On your computer, the page was built in time, by luck. The fix is the **explicit wait** (`WebDriverWait` with a condition), not a longer `sleep`: the `sleep` only **postpones** the problem to the next slower computer. The same goes for Playwright, where `wait_for()` plays that role.

## // Module summary

- [ ] I can do the same collection with Selenium, with an explicit wait.
- [ ] I know the difference between `find_element` and `find_elements`.
- [ ] I know Selenium's wait checks every 0.5 s, by default.
- [ ] I can compare the two tools, separating what was observed from what comes from the documentation.
- [ ] I can choose: the API first, and then the tool my context calls for.

---

**End of the experienced track.** Check `deliverable.md` for the final list of what to submit.

`Study Material // Coffee & Code`
