# Module 16, Playwright: Pages with JavaScript

[Português](../docs/16-playwright-paginas-com-javascript.md) · English

`WEEK 07 // Data & Scraping, Part 1: Collection` | **Experienced track**

---

## // Before you start

In Module 01, you saw that a page can arrive **empty** and be filled in by JavaScript later. `requests` and BeautifulSoup do not run JavaScript, and so they do not see these pages. This module presents the two ways out: **driving a real browser** with Playwright, and (better, when possible) **finding the API the page uses** and calling it directly.

## // The problem, again

This is the `16_a_requests_nao_ve.py` script, with the real result, against the `/vagas-js/` page:

```python
resposta = requests.get(f"{BASE}/vagas-js/", timeout=10)
sopa = BeautifulSoup(resposta.content, "lxml")
print("status:", resposta.status_code)
print("cartões na página:", len(sopa.select("article.vaga")))
print("texto do #resultado:", sopa.select_one("#resultado").get_text())
print("há um <script> no HTML?", sopa.find("script") is not None)
```

```
status: 200
cartões na página: 0
texto do #resultado: Carregando...
há um <script> no HTML? True
```

<div align="center">
<img src="../docs/assets/svg/estatico-x-renderizado.svg" alt="Comparison between a static page and one built by JavaScript, with the Playwright or direct API call solutions" width="640">
</div>

## // Playwright

> **PLAYWRIGHT: IN SIMPLE WORDS**
> It is a library that **drives a real browser** (Chromium, and others) through code: it opens pages, waits for the JavaScript to finish, reads what appeared and clicks buttons. Playwright runs the page in a real browser, JavaScript included. That does **not** mean the automation is indistinguishable from a person: browser automation can be detectable.

Installation, in two steps (the second downloads the browser):

```
pip install playwright
playwright install chromium
```

This material was verified with Playwright **1.63.0**. An honest warning: the tests were run with a Chromium **153** packaged by third parties, and **not** with the browser that `playwright install` downloads (the production environment had no access to the download). `playwright install chromium` on your machine will install another build, and small differences are possible. The scripts use the `navegador.py` file, which **only** changes behavior if you set the `CHROMIUM_PATH` and `CHROMIUM_ARGS` variables. In normal use, set nothing.

## // The first script

This is `16_b_playwright_basico.py`:

```python
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
```

```
logo depois do goto: 0 cartões
texto do #resultado: Carregando...
depois de esperar: 8 cartões
primeiros títulos: ['Analista de Dados Pleno',
 'Desenvolvedor(a) Python Júnior', 'Estágio em Desenvolvimento Web']
data-id do primeiro: v002
empresa do primeiro: Pinhão Dados
```

(The list of titles was broken to fit.) The result tells the whole story: **right after goto**, the page is in the same state `requests` saw: 0 cards, and "Carregando..." ("Loading..."). Only after `wait_for()` (which waits for the first card to appear) do the 8 cards exist. What each piece does:

| Piece | What it does |
|---|---|
| `async_playwright()` and `p.chromium.launch()` | Starts Playwright and opens the browser (by default, with no window) |
| `navegador.new_page()` and `pagina.goto(url)` | Opens a tab, and navigates |
| `pagina.locator("article.vaga")` | A **locator**: describes what to look for, with a CSS selector, but does not search yet |
| `.count()` | How many elements exist **now** |
| `.first.wait_for()` | **Waits** for the first element to appear |
| `inner_text()`, `get_attribute()` | Reads the text and the attributes |
| `eval_on_selector_all(selector, js)` | Runs a small JavaScript function over all the elements |

## // Automatic waiting

Playwright was designed to **wait on its own**: before acting on an element (clicking, reading the text), it checks whether the element is ready, and waits as long as needed (the documentation calls these checks "actionability", and they apply to the methods that act on the element). That is why, in general, **you do not use time.sleep**: it waits too long (waste) or too little (intermittent error). What the code above uses is a **condition**: "wait for the first card to appear".

The count right after `goto`, which returned `0`, is a good reminder: `count()` is a **snapshot of the moment**, and does not wait. To count what is going to appear, wait first.

## // The most robust route: finding the API

Reading a page built by JavaScript through the browser works, but it is **heavy** (it opens a whole browser) and **fragile** (it depends on the final HTML). There is a better path, when it exists: to build itself, the page **asks an API for the data**. If you find out which one, you can call it directly, without any browser, and receive the data already in JSON, organized.

Playwright helps you **discover** the call. This is `16_c_achar_a_api.py`:

```python
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
```

```
a página chamou: http://127.0.0.1:8080/api/vagas?pagina=1&por_pagina=8
status: 200 | total: 20 | itens: 8
chamadas fetch/xhr: ['/api/vagas?pagina=1&por_pagina=8']
--- o atalho, sem navegador nenhum
página 2 direto da API: ['v010', 'v009', 'v012', 'v011', 'v014', 'v013',
 'v016', 'v015']
```

(The last line was broken to fit.) `expect_response` waits for a response whose address matches the pattern in the code (any address ending in `/api/vagas` and its parameters), and delivers the response, JSON included. Once the address is discovered, the rest of the script **drops the browser** and calls the API with `httpx`. The API brings the `total` (20), and lets you request **any page** (`pagina=2`) without navigating. And, unlike the HTML list (Module 07), **requesting a page past the end returns an empty list**: paginating the API "until it comes back empty", the real result is 20 jobs in 3 pages, 20 unique ids, and a declared `total` of 20.

In browsers, the developer tools show these calls in the network tab, and that is usually how an API is discovered. The interface of these tools was not checked while producing this material, and the names vary between browsers.

> **THE API HAS RULES TOO**
> Calling an API that the page uses does not free it from rules. The same precautions from Module 03 apply: terms of use, pace, identification, and (if any) what the API owner declares. An API **without documentation**, which only exists for the page, can change without warning.

## // Good manners with a browser

- **Playwright does not read robots.txt for you.** Check `can_fetch` before opening the page, as in Module 07.
- **A browser is heavy.** Open **one** browser and reuse it for several pages; do not open one per page.
- **Do not use the browser to escape protections.** It runs JavaScript, which makes it capable of many things this material **does not teach**: getting around captchas, imitating human behavior to dodge a block. If the site blocks robots, the answer is to ask the owner, not to disguise the robot.

## // Common errors

These messages were obtained by running the code.

| Error | Why it happens | How to fix it |
|---|---|---|
| `strict mode violation: locator("article.vaga") resolved to 8 elements` | The locator matched several elements, and you asked for **one** text | Use `.first`, `.nth(i)`, or `.all_inner_texts()` |
| `TimeoutError: Page.wait_for_selector: Timeout 1000ms exceeded.` | The element did not appear in time (or never will) | Check the selector and the page; raise the `timeout` only if it makes sense |
| `count()` returns `0` right after `goto` | The JavaScript has not built the page yet | Wait first: `.first.wait_for()` |
| `BrowserType.launch: Executable doesn't exist at ...` | The browser was not downloaded | Run `playwright install chromium` |
| It works sometimes, and fails other times | A fixed `time.sleep`, too short | Wait for a **condition**, not for a time |
| The browser "stays open" after the script | The `await navegador.close()` is missing | Close it at the end, preferably inside `try/finally` |

The first error deserves the `16_d_erros.py` script (broken to fit):

```
--- 1) o seletor casa com VÁRIOS elementos e você pede um texto
Error: Locator.inner_text: Error: strict mode violation:
 locator("article.vaga") resolved to 8 elements:
--- 2) esperar por algo que nunca aparece
TimeoutError: Page.wait_for_selector: Timeout 1000ms exceeded.
```

"Strict mode" is a protection: Playwright would rather **refuse** than guess which of the 8 elements you meant.

## // The tests

The browser tests are in `veterano/tests/test_navegador.py`. They **skip themselves** if no browser is installed. With a browser available, five tests confirm: that `requests` does not see the cards, that Playwright waits for the JavaScript and finds the 8 cards (the first is `v002`), that it captures the API call (status `200`, `total` of 20), that the locator with several elements violates strict mode, and (in Module 17) that Selenium does the same. Running without a browser, **12 pass and 4 are skipped**; with the browser, all 16 pass.

## // Good example × bad example

**Bad example**: a fixed `sleep`, and a position selector:

```python
await pagina.goto(url)
await asyncio.sleep(3)
html = await pagina.content()
```

**Good example**: wait for a condition, and prefer the API when it exists:

```python
await pagina.locator("article.vaga").first.wait_for()
```

## // Guided practice

1. Run `16_a_requests_nao_ve.py` and confirm the 0 cards.
2. Install Playwright and Chromium, and run `16_b_playwright_basico.py`.
3. Run `16_c_achar_a_api.py` and look at the API address.
4. Run `16_d_erros.py` and read the two messages.
5. Try removing the `wait_for()` from `16_b` and see what changes.

## // Practice on your own

> **CHALLENGE**
> Write a collector that, **without opening a browser**, collects all the jobs from the `/api/vagas` API, paginating with `por_pagina=8` until the list comes back empty. Expected result: **20 jobs in 3 pages**, with 20 unique ids, and a declared `total` of 20. Then add the rate limiter from Module 15 and the `User-Agent` from Module 03.

## // Applying it to the week's project

1. In the project's `veterano/` folder, put `navegador.py`, `16_b` and `16_c`.
2. Do the API challenge, and store the result in the database with the Module 10 functions.
3. Note in `anotacoes.md` **when** you would choose a browser, and **when** the API.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> You need to collect a page built by JavaScript, and you discover it uses an internal API, with no documentation or terms of its own. What do you do before calling it directly?

Answer: go back to **Module 03**. Being easy to call does not mean it is allowed: read the site's terms, the `robots.txt` (is the API under a path it forbids?), and use a polite pace and an honest `User-Agent`. An internal API has no stability guarantee, so **count on** it changing, and keep the empty-fields alarm (Module 11). If there is a real doubt about permission, ask the site owner.

## // Module summary

- [ ] I know why `requests` does not see a page built by JavaScript.
- [ ] I can open a page with Playwright, wait for the JavaScript and extract with locators.
- [ ] I know `count()` is a snapshot of the moment, and that I should wait for **conditions**, not for time.
- [ ] I can discover the API a page uses, and call it directly.
- [ ] I know good manners with a browser, and what **not** to do with it.
- [ ] I can recognize strict mode and `TimeoutError`.

---

**Next module:** `17-selenium-and-the-comparison.md` (**bonus**), the other browser tool, and when to choose each one.

`Study Material // Coffee & Code`
