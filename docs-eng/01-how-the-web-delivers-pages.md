# Module 01, How the Web Delivers Pages

[Português](../docs/01-como-a-web-entrega-paginas.md) · English

`WEEK 07 // Data & Scraping, Part 1: Collection`

---

## // Before you start

To collect data from a page, you need to understand **what your program receives** when it requests that page. This module requires nothing from earlier modules: it explains, from scratch, the conversation between a program and a site, and what changes when the page is built by JavaScript.

## // A request and a response

Every page you open is the result of a short conversation between two sides: the **client** (the browser, or your program) and the **server** (the computer that holds the site). The client makes a **request**, the server sends back a **response**, and the conversation ends.

<div align="center">
<img src="../docs/assets/svg/pedido-e-html.svg" alt="A GET request with its headers, the server's response with status, headers and the HTML body" width="640">
</div>

The protocol for this conversation is called **HTTP**. The request has a first line with the **method** (almost always `GET`, which means "give me this") and the **path**, followed by **headers**, which are information about who is asking. The response has a **status code**, its own headers and the **body**: the page's HTML. The body is what BeautifulSoup will read.

## // The address (URL)

An address like `http://127.0.0.1:8080/vagas/?pagina=2` has parts, and each one matters to someone collecting data:

| Part | In the example | What it is for |
|---|---|---|
| Scheme | `http` | The protocol (`https` is the same, with encryption) |
| Server (host) | `127.0.0.1` | Who answers. `127.0.0.1` is **your own computer** |
| Port | `8080` | The server's "door". Without it, the default applies (80 for `http`, 443 for `https`) |
| Path | `/vagas/` | Which page or resource you want |
| Query | `?pagina=2` | Parameters, in the `name=value` format. Several are separated by `&` |
| Fragment | `#candidatar` | A point inside the page. **It is never sent to the server** |

The query is your ally in pagination: `?pagina=1`, `?pagina=2`... It is how you request each page of a list.

## // Status codes

The first piece of data in a response is the status code, a three-digit number. The first digit tells the family:

| Family | Means | Examples you will meet this week |
|---|---|---|
| `2xx` | It worked | `200` OK |
| `3xx` | Go somewhere else, or nothing changed | `301` moved, `304` not modified |
| `4xx` | The **request** has a problem | `404` does not exist, `403` access denied, `429` too many requests |
| `5xx` | The **server** has a problem | `500` internal error, `503` unavailable right now |

Mural Tech, the training site, produces each of them on purpose, and you will see all of them in the next modules. The ones worth memorizing now: on the pages you collect with `GET`, `200` OK is the expected success response (there are other `2xx` codes, such as `201` and `206`, for other kinds of response); there is no point repeating `404` and `403`; `429` and `503` mean "wait a little and try again", and a good scraper is obliged to comply.

## // The headers that matter

This is a real Mural Tech response, obtained with the command `curl -s -D - -o /dev/null http://127.0.0.1:8080/vagas/` (which shows only the headers):

```
HTTP/1.0 200 OK
Server: BaseHTTP/0.6 Python/3.12.3
Date: (data e hora)
Content-Type: text/html; charset=utf-8
Content-Length: 4122
ETag: "d3aa7cdebab346b2"
```

| Header | What it says | Why it matters for collection |
|---|---|---|
| `Content-Type` | The body's format and **encoding** | Without the `charset`, accents can come out wrong (Module 05) |
| `Content-Length` | The body's size, in bytes | Gives an idea of each page's weight |
| `ETag` | A "fingerprint" of this version of the page | Lets you ask "did it change?" without downloading again (Module 11) |
| `Retry-After` | How many seconds to wait | Shows up with `429` and `503`: obey it (Module 11) |
| `Location` | Where to go | Shows up with `301` |

And there is a header of **yours**, which you send with every request: the `User-Agent`, which says who is asking. The browser sends its own. `requests`, if you say nothing, sends `python-requests/2.34.2`. A good scraper identifies itself truthfully (Module 03).

## // Static page and page built by JavaScript

This is the most important distinction in the module, because it decides **which tool** you will use.

<div align="center">
<img src="../docs/assets/svg/estatico-x-renderizado.svg" alt="Comparison between a static page, where the data is already in the HTML, and a page built by JavaScript, where the data arrives later" width="640">
</div>

In a **static** page, the data is already in the HTML that the server delivers. This is a real excerpt of the body of `/vagas/`:

```html
<article class="vaga" data-id="v002">
  <h2 class="titulo"><a href="/vagas/v002">Analista de Dados Pleno</a></h2>
  <p class="empresa">Pinhão Dados</p>
  ...
</article>
```

In a page **built by JavaScript**, the server delivers only a skeleton, and the browser runs a program (the `<script>`) that fetches the data and fills in the page. This is the real HTML of `/vagas-js/`, exactly as your program receives it:

```html
<main>
<h1>Vagas de tecnologia</h1>
<div id="resultado">Carregando...</div>
<script>
async function carregar() {
  await new Promise((r) => setTimeout(r, 400));
  const resp = await fetch("/api/vagas?pagina=1&por_pagina=8");
  const dados = await resp.json();
  const alvo = document.getElementById("resultado");
  ...
```

Whoever opens `/vagas-js/` in the browser sees the jobs after less than a second. Whoever downloads it with `requests` sees **"Carregando..."** ("Loading...") and **no cards**: `requests` delivers the HTML, but **does not run the JavaScript**. Running the real script against the page:

```
status: 200
cartões na página: 0
texto do #resultado: Carregando...
há um <script> no HTML? True
```

For pages like this there are two paths, and Module 16 shows both: use a real browser, driven by code (Playwright), or discover **the API the page uses** (in the example, `/api/vagas`) and call it directly.

> **HOW TO TELL WHICH CASE IT IS**
> Compare what the browser shows with what `requests` received. One count settles it: `len(sopa.select("article.vaga"))`. If the browser shows 8 jobs and the count is 0, the page is built by JavaScript. Another clue: in the browser, the **Ctrl+U** shortcut opens the original HTML (what the server delivered), and the **Inspect** tool shows the page already built. The interface of these tools was not checked while producing this material, and the names vary between browsers.

## // Mural Tech, the training site

In a terminal, inside the `site-treino` folder, start the site:

```
python3 servidor.py
```

```
Mural Tech no ar em http://127.0.0.1:8080  (dia 1). Ctrl+C para parar.
```

Leave that terminal open: the site only exists while the program runs. These are its pages, and each one exists for a reason:

| Address | What it has | Used in module |
|---|---|---|
| `/vagas/` and `/vagas/?pagina=2` | The job list, in 3 pages | 06, 07 |
| `/vagas/v003` | The detail of a job | 02, 07 |
| `/eventos/` | The event list | 09 |
| `/robots.txt` | The rules for robots | 03 |
| `/vagas-js/` and `/api/vagas` | Jobs built by JavaScript, and the API that delivers them | 16, 17 |
| `/quebrado/` | Badly written HTML | 06 |
| `/legado/vagas` | A page without a declared encoding | 05 |
| `/lento` | A response that takes 3 seconds | 05 |
| `/instavel/vagas` and `/limitado/vagas` | `503` failures and a `429` request limit | 11 |
| `/eco` and `/antigo/vagas` | Returns your headers, and a `301` redirect | 05 |
| `/_dev/...` | Practice controls: change the data's "day", turn on a delay | 10, 12, 15 |

The site also has a **"day 2"**: after `/_dev/dia/2`, some jobs are new, two salaries change and one job disappears. That is how the pipeline will learn to update the database instead of just filling it.

## // Good example × bad example

**Bad example**: treating every response as if it were good, without looking at the status:

```python
html = requests.get(url).text
```

If the page does not exist (`404`) or the server is asking you to slow down (`429`), the text of the error page will be read as if it were a job, and the error will only show up much later, in the database.

**Good example**: look at the status before reading, and give the request a time limit:

```python
resposta = requests.get(url, timeout=10)
resposta.raise_for_status()
```

Module 05 explains each of these two lines.

## // Common errors

| Error | Why it happens | How to fix it |
|---|---|---|
| `ConnectionError: ... Connection refused` | The training site is not running (message obtained on Linux; other systems word it differently) | Start `servidor.py` and leave the terminal open |
| 0 cards on a page that shows jobs in the browser | The page is built by JavaScript | Compare with `Ctrl+U`; use Module 16 |
| `404` on an address that looks right | The trailing slash is missing, or there is a typo | Check the exact path, and copy it from the browser |
| What you see in the browser differs from what the program receives | The browser ran JavaScript, or sent other headers | Download the page and read the raw HTML |

## // Guided practice

1. Start Mural Tech and open `http://127.0.0.1:8080/vagas/` in the browser.
2. Open the page's source code (`Ctrl+U`) and find an `<article class="vaga">`.
3. Open `http://127.0.0.1:8080/vagas-js/`, wait for the content to appear, and open its source code. Compare: what appears on screen **is not** in the source code.
4. Open `http://127.0.0.1:8080/api/vagas?pagina=1&por_pagina=3` and read the JSON: it is the data source of the previous page.
5. In another terminal, run `curl -s -D - -o /dev/null http://127.0.0.1:8080/vagas/` and identify the `Content-Type` and the `ETag`.

## // Practice on your own

> **CHALLENGE**
> Write a script that requests, **without following redirects**, the addresses `/vagas/`, `/vagas/v999` and `/antigo/vagas`, and prints the status code and the `Content-Type` of each. Use `requests.get(url, allow_redirects=False, timeout=10)`. Expected result: `200`, `404` and `301`.

## // Applying it to the week's project

1. Create the `projeto-coleta/` folder on your computer. It will grow with each module, until it becomes the pipeline.
2. Copy the `site-treino/` folder from this material into it.
3. Create the `anotacoes.md` file and write, in your own words, the difference between a static page and one built by JavaScript. You will reread it in Module 16.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> Your scraper downloads `/vagas-js/` and finds 0 jobs, with no error at all. The server answered `200`. Why did the program not raise an error, and what does that teach about how to check your work?

Answer: because, for `requests`, everything went fine: it asked for a page, received a page, and the page (the skeleton) has no error at all. What is wrong is the **expectation** that the HTML would have the jobs. A `200` says the response arrived, not that the data is in it. That is why a well-made scraper **checks the result** (how many jobs came? how many fields are empty?) instead of trusting only the absence of errors. Module 11 turns this check into an alarm.

## // Module summary

- [ ] I can describe an HTTP request and response.
- [ ] I can identify the parts of a URL, and what the query (`?pagina=2`) is for.
- [ ] I know the four families of status codes, and which ones ask you to wait.
- [ ] I know the `Content-Type` carries the encoding, and that `ETag` and `Retry-After` exist.
- [ ] I know the difference between a static page and one built by JavaScript.
- [ ] I can start Mural Tech and say what each of its pages is for.

---

**Next module:** `02-html-for-those-who-will-extract.md`, you already know how the page arrives. Now, how to read what is inside it.

`Study Material // Coffee & Code`
