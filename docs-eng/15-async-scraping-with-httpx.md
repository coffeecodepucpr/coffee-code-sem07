# Module 15, Async Scraping with httpx

[Português](../docs/15-scraping-assincrono-com-httpx.md) · English

`WEEK 07 // Data & Scraping, Part 1: Collection` | **Experienced track**

---

## // Before you start

This module belongs to the **experienced track**: it assumes you have already written scrapers with `requests` (Modules 05 to 07), and want to collect **faster**, without losing good manners. It introduces `asyncio` and `httpx` from scratch, but at the pace of someone who already programs. The central idea, which will come back again and again: **async is not a license to ignore the pace the site asks for**.

## // The bottleneck is the wait

The Module 07 scraper makes one request at a time. On each one, the program **waits** for the response to arrive, doing nothing else. With a server that takes 0.2 seconds to answer, 23 requests cost, in sequence, 23 × 0.2 = **4.6 seconds**, and almost all of that time is waiting, not work. The idea of asynchronous programming: while **one** request waits, **others** can go out.

## // asyncio in a few lines

`asyncio` is Python's standard library for this. Three words are enough:

- **async def** creates a function that can "wait" without freezing the program (a *coroutine*).
- **await** marks the point where it waits, and lets the program do something else in the meantime.
- **asyncio.gather** runs several coroutines at the same time, and returns the results in order.

```python
async def tarefa(n):
    await asyncio.sleep(0.5)
    return n

# em sequência:
r = [await tarefa(i) for i in range(6)]
# todas juntas:
r = await asyncio.gather(*(tarefa(i) for i in range(6)))
```

```
em sequência: [0, 1, 2, 3, 4, 5] 3.0 s
com gather  : [0, 1, 2, 3, 4, 5] 0.5 s
```

Six half-second tasks: 3.0 seconds one after the other, and **0.5** all together. Important: everything runs on **a single thread of execution**. There is no processor parallelism; the gain comes from using the waiting time. That is why `asyncio` helps with tasks that **wait on the network**, not with heavy computation.

## // httpx

**httpx** (version 0.28.1, this week) is an HTTP request library with an interface very similar to `requests`, and with an async version (`httpx.AsyncClient`). Install it with `pip install httpx`. Two differences that matter:

- `requests` **has no default time limit**, as you saw in Module 05. `httpx` does: `Timeout(timeout=5.0)`. Even so, **write your own**, so the behavior is clear: `httpx.Timeout(10, connect=3)`.
- The async client is used with `async with`, and each request takes `await`: `resposta = await cliente.get(url)`.

## // Limiting concurrency: the semaphore

Firing 20 requests at once is easy, and a terrible idea: you can bring the site down, or get blocked. The **semaphore** (`asyncio.Semaphore(n)`) lets **at most n** through at a time; the others wait their turn. Measuring the async scraper against a server with 0.2 s latency, with 23 requests (each value is the median of 3 runs, and they were all very close):

| Concurrency | Time | Gain over the sequence (4.7 s) |
|---|---|---|
| 1 (one at a time) | 4.7 s | none |
| 2 | 2.6 s | about 1.8 times |
| 5 | 1.3 s | about 3.6 times |
| 10 | 0.9 s | about 5.2 times |
| 20 | 0.7 s | about 6.7 times |
| 50 | 0.7 s | about 6.7 times |

Two things to notice. **The gain has a ceiling**: from 20 to 50, nothing changes. The reason is that the collection has **steps that depend on each other**: page 1 comes first (it says how many pages exist), then pages 2 and 3, and only then the 20 details. That is three "waves" of at least 0.2 s, and no amount of concurrency removes that chain. A simple formula describes the numbers well: the time is about `ceil(20 / c) × 0.2 + 0.4` seconds (with concurrency 5: 4 rounds of 0.2 s details, plus 0.4 s for the first two steps, gives 1.2 s, and we measured 1.3 s).

> **A LESSON ABOUT MEASURING**
> In an earlier version of this material, the training site accepted few pending connections at once (a small limit of Python's own server), and the high-concurrency measurements came out **slower and unstable** (concurrency 10 took as long as 1.7 s, against 0.9 s after the fix). The defect was in the server, not in async. When a measurement looks odd, suspect **everything** in the path, not just your code.

## // Limiting the pace: what the semaphore does not do

The semaphore limits **how many at the same time**. Module 03's `Crawl-delay` asks for something else: a **minimum interval between requests**. They are different things, and respecting the second needs a **rate limiter**: a piece that guarantees the **start** of two requests is never closer than the agreed interval, for all requests together.

```python
class LimitadorDeRitmo:
    """Garante um intervalo mínimo entre o INÍCIO de dois pedidos, para todos."""

    def __init__(self, intervalo: float):
        self.intervalo = intervalo
        self._proximo = 0.0
        self._trava = asyncio.Lock()

    async def esperar(self) -> None:
        async with self._trava:
            agora = asyncio.get_running_loop().time()
            espera = max(0.0, self._proximo - agora)
            self._proximo = max(agora, self._proximo) + self.intervalo
        if espera:
            await asyncio.sleep(espera)
```

The idea: each request asks for its turn (`esperar`, "wait"), and the limiter marks the next time someone may go out. The `Lock` prevents two requests from booking the same slot. With it set to an interval of 0.2 s, the result changes completely:

```
em sequência (requests):        23 pedidos em 4.7 s
assíncrono (conc.  5, intervalo 0.0 s): 20 vagas em 1.4 s
assíncrono (conc. 10, intervalo 0.0 s): 20 vagas em 0.9 s
assíncrono (conc.  5, intervalo 0.2 s): 20 vagas em 4.7 s
```

(Measurements from `15_a_comparar.py`, repeated three times, with 0.1 s of variation.) On the last line, concurrency is still 5, but the limiter imposes 0.2 s between starts, and the time **goes back to the sequence's**: 23 × 0.2 = 4.6 s, and we measured 4.7. The limiter **rules**.

<div align="center">
<img src="../docs/assets/svg/sincrono-x-assincrono.svg" alt="Bars comparing the time in sequence, with 5 and 10 at the same time, and with 5 plus a 0.2 second interval, which goes back to the sequence's time" width="640">
</div>

The practical consequence: Mural Tech's `robots.txt` asks for 1 second between requests. With a 1 s limiter, these same 23 requests would take about 23 s, as in Module 07, **however much concurrency you use**. (It is a calculation, not a measurement: the 0.2 s measurement showed that the limiter dominates, and 1 s only amplifies the effect.)

> **WHEN ASYNC PAYS OFF**
> **It pays off**: collecting from **many different sites** (each with its own pace, all waiting at the same time), downloading from an API that declares a generous usage limit, or dealing with slow responses. **It does not pay off**: collecting from **a single site** that asks for an interval between requests. In that case, it only gives you more code to maintain.

## // The async collector

This is the function that downloads a page with a **semaphore**, a **limiter** and **retries** (the async version of the Module 11 ideas, with the same policy as the main pipeline: it retries `429`, `502`, `503` and `504`). The small `segundos_de` function handles `Retry-After`: if it is not a number (the HTTP standard allows a **date**), the growing wait applies:

```python
def segundos_de(retry_after, padrao: float) -> float:
    """Retry-After pode ser um número ou uma data HTTP: se não der, o padrão."""
    try:
        return float(retry_after)
    except (TypeError, ValueError):
        return padrao


async def baixar(cliente, url, semaforo, limitador, tentativas=3,
                 dormir=asyncio.sleep):
    async with semaforo:                 # no máximo N pedidos ao mesmo tempo
        for numero in range(1, tentativas + 1):
            await limitador.esperar()    # e no máximo 1 a cada intervalo
            try:
                resposta = await cliente.get(url)
            except (httpx.TimeoutException, httpx.TransportError):
                resposta = None
            if resposta is not None and resposta.status_code not in RETENTAR:
                resposta.raise_for_status()
                return resposta
            if numero < tentativas:
                pedido = resposta.headers.get("Retry-After") if resposta else None
                espera = segundos_de(pedido, 0.5 * 2 ** (numero - 1))
                await dormir(espera)
        raise RuntimeError(f"{url}: sem sucesso em {tentativas} tentativas")
```

And this is the collection, which uses `gather` in two waves (the pages, and then the details). Notice `return_exceptions=True`: **a failure on one detail does not bring down the others**, and the following loop decides what to do with each result.

```python
async def coletar(base=BASE, concorrencia=5, intervalo=0.0):
    semaforo = asyncio.Semaphore(concorrencia)
    limitador = LimitadorDeRitmo(intervalo)
    cabecalhos = {"User-Agent": USER_AGENT}
    tempo = httpx.Timeout(10, connect=3)
    async with httpx.AsyncClient(headers=cabecalhos, timeout=tempo) as cliente:
        url1 = urljoin(base, "/vagas/")
        primeira = sopa(await baixar(cliente, url1, semaforo, limitador))
        rotulo = primeira.select_one(".paginacao span").get_text()
        total = int(re.search(r"de (\d+)", rotulo).group(1))
        urls = [f"{url1}?pagina={n}" for n in range(2, total + 1)]
        outras = await asyncio.gather(
            *(baixar(cliente, u, semaforo, limitador) for u in urls))
        vagas = ler_vagas_da_pagina(primeira, url1)
        for resposta in outras:
            vagas += ler_vagas_da_pagina(sopa(resposta), str(resposta.url))
        detalhes = await asyncio.gather(
            *(baixar(cliente, v["url"], semaforo, limitador) for v in vagas),
            return_exceptions=True)
        for vaga, detalhe in zip(vagas, detalhes):
            if isinstance(detalhe, Exception):
                vaga["descricao"] = None      # uma falha não derruba as outras
            else:
                vaga["descricao"] = ler_descricao(sopa(detalhe))
    return vagas
```

## // The tests

On top of the pipeline's **79 tests**, this track adds another **16** (in `veterano/tests/`), 11 of which are for the async collector. They confirm, among other points:

- the semaphore limits concurrency (never more than 3 at the same time, in a test with a limit of 3);
- the limiter spaces out the start of requests (never less than 0.045 s, with a 0.05 s interval);
- a `503` is retried, obeying `Retry-After` when it exists (the waits were `2.0` and `1.0`);
- a `504` is also retried, and a `Retry-After` in date format (which does not become a number) falls back to the growing wait, instead of breaking;
- a `404` is not retried, and after 4 attempts the collector gives up;
- async brings **the same 20 ids** as the sequential version;
- a failure on one detail leaves `descricao: None` on it, and the other 19 stay intact.

## // Good example × bad example

**Bad example**: firing everything at once, without limits, against a single site:

```python
await asyncio.gather(*(cliente.get(u) for u in urls_das_20_paginas))
```

**Good example**: semaphore, rate limiter, time limit and retries:

```python
await baixar(cliente, url, semaforo, limitador)
```

## // Common errors

These messages and results were obtained by running the code.

| Error | Why it happens | How to fix it |
|---|---|---|
| `RuntimeWarning: coroutine 'f' was never awaited` | You called an `async` function without `await`: it became an object, and never ran | Write `await f()` |
| `RuntimeError: asyncio.run() cannot be called from a running event loop` | You called `asyncio.run` inside code that is already async | Use `await` inside async code, and `asyncio.run` only at the entry point |
| Async gains nothing | There is a `time.sleep` (or another "blocking" wait) inside an `async` function | Use `await asyncio.sleep(...)`. With `time.sleep(0.2)`, 5 tasks took **1.0 s**, and with `asyncio.sleep(0.2)`, **0.2 s** |
| The site returns `429` or blocks you | High concurrency, without a limiter | Use a semaphore and a rate limiter |
| The program brings down the training site | No semaphore | Limit it to a few dozen, at most |
| One failure brings everything down | `gather` without `return_exceptions=True` | Use `return_exceptions=True`, and handle each result |
| Results out of order | You expected the order of **arrival** | `gather` returns in the order of **input** |

## // Guided practice

1. Run `15_a_comparar.py` (with the site running) and check the four times.
2. Run `coletor_async.py` with `concorrencia=1`, `2`, `5` and `10`, and fill in the module's table with **your** numbers.
3. Cause the error: put a `time.sleep(0.2)` inside `baixar` and measure again.
4. Run `pytest tests/test_async.py` and read the test names.

## // Practice on your own

> **CHALLENGE**
> Use the formula `ceil(20 / c) × 0.2 + 0.4` to **predict** the time for concurrency 4 and concurrency 3. Then **measure** it (with the site at `--latencia 0.2`). Result: the formula gives 1.4 s and 1.8 s, and the measurement (median of 3 runs) gave 1.5 s and 1.9 s. Why is the measured value usually a bit higher than the formula's? (Hint: the formula ignores the time to open connections, read the HTML and schedule the tasks.)

## // Applying it to the week's project

1. Copy `coletor_async.py` and `parsers.py` to a `veterano/` folder in the project.
2. Tie the limiter to the `Crawl-delay` from `robots.txt` (read it with the Module 11 client), instead of using a fixed value.
3. Measure your collector against the training site with and without the limiter, and note the numbers for the deliverable.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> You need to collect 5,000 pages from **a single site** that asks for 1 second between requests. Is it worth building the async collector?

Answer: **not to gain speed**. With a minimum interval of 1 s between request starts, 5,000 pages take about 5,000 s (an hour and a half), with concurrency 1 or 50. Async would only help if the site **accepted more requests** (`robots.txt` and the terms decide that) or if you were collecting from **several sites** at the same time. The right question is not "how do I collect faster?", but "what pace does the site accept?". Answering the second is what makes the first legitimate.

## // Module summary

- [ ] I know a scraper's bottleneck is waiting on the network, and what `asyncio` does about it.
- [ ] I can use `async def`, `await`, `asyncio.gather` and `httpx.AsyncClient`.
- [ ] I can limit concurrency with a semaphore, and I know the gain has a ceiling.
- [ ] I can limit the **pace** with a limiter, and I know it is the piece that respects `Crawl-delay`.
- [ ] I can isolate failures with `return_exceptions=True`.
- [ ] I can say when async pays off, and when it does not.

---

**Next module:** `16-playwright-pages-with-javascript.md`, so far, the HTML already came with the data. What about when JavaScript builds it later?

`Study Material // Coffee & Code`
