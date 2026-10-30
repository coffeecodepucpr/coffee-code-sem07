# Module 05, requests: Downloading Pages

[Português](../docs/05-requests-baixando-paginas.md) · English

`WEEK 07 // Data & Scraping, Part 1: Collection`

---

## // Before you start

The first step of any collection is **downloading the page**. This module introduces `requests`, the library that does it, and gives more space to what can go wrong than to what goes right, because errors are where an amateur scraper parts ways with a reliable one. Keep Mural Tech running, as in every module.

## // What requests is

> **REQUESTS: IN SIMPLE WORDS**
> It is a Python library that makes HTTP requests: you give it the address, and it returns an object with the response (status, headers and body). It is your program's "browser", with no window and no JavaScript.

Install it in the project's virtual environment (`pip install requests`). This material was verified with version **2.34.2**.

## // The first request

This script (`05_a_primeiro_pedido.py`) makes a request and examines the response:

```python
import requests

BASE = "http://127.0.0.1:8080"

resposta = requests.get(f"{BASE}/vagas/", timeout=10)
print("status:", resposta.status_code, "| ok:", resposta.ok)
print("url final:", resposta.url)
print("content-type:", resposta.headers["Content-Type"])
print("etag:", resposta.headers["ETag"])
print("tamanho em bytes:", len(resposta.content))
print("tipo de .content:", type(resposta.content).__name__)
print("tipo de .text:", type(resposta.text).__name__)
print("encoding:", resposta.encoding)
```

```
status: 200 | ok: True
url final: http://127.0.0.1:8080/vagas/
content-type: text/html; charset=utf-8
etag: "d3aa7cdebab346b2"
tamanho em bytes: 4122
tipo de .content: bytes
tipo de .text: str
encoding: utf-8
```

| What you use | What it is |
|---|---|
| `resposta.status_code` | The status code (`200`, `404`...) |
| `resposta.ok` | `True` for any status below 400 |
| `resposta.headers` | The headers, in a case-insensitive dictionary |
| `resposta.content` | The body in **bytes**, as it arrived |
| `resposta.text` | The body as **text**, decoded by `requests` |
| `resposta.encoding` | The encoding `requests` used to decode |
| `resposta.url` | The final address (after redirects) |
| `resposta.elapsed` | How long the response took |

## // Parameters and redirects

To build a query (`?pagina=2`), pass a dictionary in `params`, and `requests` takes care of the formatting:

```python
com_params = requests.get(f"{BASE}/vagas/", params={"pagina": 2}, timeout=10)
print(com_params.url)
```

```
http://127.0.0.1:8080/vagas/?pagina=2
```

Some addresses have moved: the server answers `301` and says where to go. `requests` **follows these redirects on its own**, and keeps the path in `resposta.history`:

```python
antigo = requests.get(f"{BASE}/antigo/vagas", timeout=10)
print("status final:", antigo.status_code, "| url final:", antigo.url)
caminho = [(r.status_code, r.headers["Location"]) for r in antigo.history]
print("histórico:", caminho)
sem_seguir = requests.get(f"{BASE}/antigo/vagas", allow_redirects=False,
                          timeout=10)
print("sem seguir:", sem_seguir.status_code, sem_seguir.headers["Location"])
```

```
status final: 200 | url final: http://127.0.0.1:8080/vagas/
histórico: [(301, '/vagas/')]
sem seguir: 301 /vagas/
```

## // The encoding trap

This error hits **anyone who writes in Portuguese** (or any language with accents). Mural Tech has a page that **does not declare its encoding** (`/legado/vagas`): the header says only `text/html`, with no `charset`. Without that information, `requests` makes a guess, and gets it wrong:

```python
certa = requests.get(f"{BASE}/vagas/", timeout=10)
legado = requests.get(f"{BASE}/legado/vagas", timeout=10)
print("cabeçalho da página certa :", certa.headers["Content-Type"])
print("cabeçalho da página legado:", legado.headers["Content-Type"])
print("encoding que o requests supôs:", legado.encoding)
```

```
cabeçalho da página certa : text/html; charset=utf-8
cabeçalho da página legado: text/html
encoding que o requests supôs: ISO-8859-1
```

The result, when reading the same sentence ("Página 1 de 3", "Page 1 of 3") from both pages:

```
certa  .text -> 'Página 1 de 3<' | BeautifulSoup(.content) -> 'Página 1 de 3'
legado .text -> 'PÃ¡gina 1 de 3' | BeautifulSoup(.content) -> 'Página 1 de 3'
```

On the page without a `charset`, `resposta.text` became **PÃ¡gina**, because `requests` decoded it as `ISO-8859-1`. Handing the **bytes** (`resposta.content`) to BeautifulSoup gave the right result: it examines the document itself to discover the encoding. That is why, this week, **we hand the bytes to BeautifulSoup** (`resposta.content`), not the text (`resposta.text`).

## // The time limit: the error that freezes programs

If you do not say how long to wait, `requests` **waits as long as the server wants**. Mural Tech has a page that takes 3 seconds (`/lento`). This script (`05_c_erros_e_timeout.py`) measures it:

```python
inicio = time.perf_counter()
requests.get(f"{BASE}/lento")
print(f"esperou {time.perf_counter() - inicio:.1f} s")

inicio = time.perf_counter()
try:
    requests.get(f"{BASE}/lento", timeout=1)
except requests.exceptions.ReadTimeout as erro:
    print(f"ReadTimeout depois de {time.perf_counter() - inicio:.1f} s")
    print("é um Timeout?", isinstance(erro, requests.exceptions.Timeout))
```

```
esperou 3.0 s
ReadTimeout depois de 1.0 s
é um Timeout? True
```

Three seconds seem like little, but a server that **really hangs** would leave the program waiting forever, and that is how a scheduled scraper (Module 13) "disappears" in the middle of the night. The rule: **every request gets a timeout**. It accepts a number (seconds) or a `(connect, read)` pair, such as `(3.05, 10)`: up to 3.05 s to connect, and up to 10 s for the server to answer. That is what the pipeline uses.

## // When the request goes wrong

Two kinds of problem, handled in different ways:

**The request never reached the server** (the site is down, the network dropped): `requests` raises an exception.

```python
try:
    requests.get("http://127.0.0.1:9/", timeout=3)
except requests.exceptions.ConnectionError as erro:
    print("ConnectionError:", type(erro.args[0]).__name__)
```

```
ConnectionError: MaxRetryError
```

(`requests` wraps the low-level error, and `MaxRetryError` is the wrapper's name. Inside it is the cause: on Linux, "Connection refused".)

**The request arrived, but the response is an error** (`404`, `500`...): **there is no exception**, and the program carries on as if nothing had happened, unless you ask. That is what `raise_for_status()` is for: it raises an error if the status is `4xx` or `5xx`:

```python
resposta = requests.get(f"{BASE}/vagas/v999", timeout=10)
print("status:", resposta.status_code, "| ok:", resposta.ok)
try:
    resposta.raise_for_status()
except requests.exceptions.HTTPError as erro:
    print("HTTPError:", erro)
```

```
status: 404 | ok: False
HTTPError: 404 Client Error: Not Found for url: http://127.0.0.1:8080/vagas/v999
```

| Situation | What `requests` does |
|---|---|
| The site does not answer, or the network fails | Raises `ConnectionError` |
| The server takes longer than the `timeout` | Raises `Timeout` (`ReadTimeout`, or `ConnectTimeout` on connection) |
| The server answers `404`, `500`... | **Nothing.** You call `raise_for_status()` to turn it into `HTTPError` |

## // The session and the User-Agent

Each loose `requests.get(...)` opens a new connection. A **session** reuses the connection and repeats the same headers on every request, and it is the right place for your `User-Agent` (remember Module 03?). The `05_d_sessao_e_user_agent.py` script asks `/eco` what the server received:

```python
padrao = requests.get(f"{BASE}/eco", timeout=10).json()
print("User-Agent padrão:", padrao["user-agent"])

USER_AGENT = "MuralColetaBot/1.0 (projeto de estudo; contato: voce@example.com)"
sessao = requests.Session()
sessao.headers["User-Agent"] = USER_AGENT

for numero in (1, 2):
    eco = sessao.get(f"{BASE}/eco", timeout=10).json()
    print(f"pedido {numero} pela sessão:", eco["user-agent"])
print("a sessão reaproveita a conexão:", eco["connection"])
```

```
User-Agent padrão: python-requests/2.34.2
pedido 1 pela sessão: MuralColetaBot/1.0
 (projeto de estudo; contato: voce@example.com)
pedido 2 pela sessão: MuralColetaBot/1.0
 (projeto de estudo; contato: voce@example.com)
a sessão reaproveita a conexão: keep-alive
```

(The real output writes each `User-Agent` on a single line.)

## // Good example × bad example

**Bad example**: no `timeout`, no status check, and reading `.text` blindly:

```python
html = requests.get(url).text
```

**Good example**: a function that gathers the precautions, and that you reuse across the whole project:

```python
def baixar(sessao, url):
    resposta = sessao.get(url, timeout=(3.05, 10))
    resposta.raise_for_status()
    return resposta
```

## // Common errors

| Error | Why it happens | How to fix it |
|---|---|---|
| The program hangs and never ends | The `timeout` is missing | Pass `timeout=` on **every** request |
| `ReadTimeout` | The server took longer than the limit | Raise the limit, or retry the request (Module 11) |
| `ConnectionError` (on Linux, "Connection refused") | The site is not up | Start the site, and check the address and port |
| The program reads an error page as if it were good | The `raise_for_status()` is missing | Call it right after the request |
| `PÃ¡gina` instead of `Página` | `resposta.text` guessed the wrong encoding | Use `resposta.content` (bytes) with BeautifulSoup |
| `HTTPError: 404 Client Error` | The page does not exist | Check the address; retrying will not help |

## // Guided practice

1. Run `05_a_primeiro_pedido.py` and check each line of output.
2. Run `05_b_codificacao.py` and see `PÃ¡gina` with your own eyes.
3. Run `05_c_erros_e_timeout.py` and compare the times (3.0 s with no limit, 1.0 s with one).
4. Stop Mural Tech (`Ctrl+C` in its terminal) and run `05_a` again. Which error appears, and on which line?
5. Run `05_d_sessao_e_user_agent.py` and confirm the server received your `User-Agent`.

## // Practice on your own

> **CHALLENGE**
> Write the `baixar(sessao, url)` function from the "good example", and use it to request `/vagas/?pagina=3` and `/vagas/v999`. The first should print the size in bytes, and the second should be caught with `try/except` and print `404 Client Error: Not Found for url: ...`. Hint: `raise_for_status()` raises `requests.exceptions.HTTPError`.

## // Applying it to the week's project

1. In the project folder, create the `http_basico.py` file with the `baixar()` function and a session with your `User-Agent` (the one from Module 03).
2. Test it against `/vagas/`. You will reuse it in Module 07.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> Your scraper runs every night. One night, the site's server hung and kept accepting connections without ever answering. What happens to your program, with and without a `timeout`?

Answer: **without a timeout**, the program stays stuck on the first request, waiting forever. It does not raise an error, does not write anything and does not end, and in the morning you only find out because the data stopped arriving. **With a timeout**, the request fails in a few seconds with `Timeout`, the program handles the error (for example, trying again later), records the problem and moves on.

## // Module summary

- [ ] I can make a request with `requests.get` and read the status, headers, `.content` and `.text`.
- [ ] I can use `params` and I know redirects are followed on their own.
- [ ] I know why I pass `resposta.content` to BeautifulSoup (the `PÃ¡gina` trap).
- [ ] I know **every request** gets a `timeout`.
- [ ] I know the difference between an exception (`ConnectionError`, `Timeout`) and an error status (`raise_for_status`).
- [ ] I can use a session with an honest `User-Agent`.

---

**Next module:** `06-beautifulsoup-reading-the-html.md`, the page has arrived. Now, read what is inside it.

`Study Material // Coffee & Code`
