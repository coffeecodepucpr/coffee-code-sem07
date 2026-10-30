# Module 12, The End-to-End Pipeline

[Português](../docs/12-o-pipeline-de-ponta-a-ponta.md) · English

`WEEK 07 // Data & Scraping, Part 1: Collection`

---

## // Before you start

You have the pieces: downloading politely (Modules 03, 05 and 11), reading the HTML (06), cleaning (08) and storing without duplicates (10). This module joins them into **one program**, which runs with one command, records what it did, and **ends in a way a scheduler understands**. That is the difference between a set of scripts and a pipeline.

## // The design

<div align="center">
<img src="../docs/assets/svg/pipeline-de-coleta.svg" alt="The collection pipeline: collect, extract, clean, store and record, with good manners at every step, and the scheduling" width="640">
</div>

The pipeline is the `executar.py` file, and it is an **orchestrator**: it does not know how to read HTML, clean, or talk to the server. It **calls** whoever knows how, in the right order, and takes care of what nobody else does: the run record, the final result and the exit code.

## // The orchestrating function

This is the `executar` ("run") function, in full:

```python
def executar(config: Config, fontes: tuple[str, ...], cliente=None) -> int:
    conn = banco.abrir(config.banco)
    inicio = agora()
    id_execucao = banco.iniciar_execucao(conn, inicio)
    resumos, erros_total, status = [], 0, "ok"
    try:
        cliente = cliente or Cliente(config)
        cliente.carregar_robots()
        etapas = {"vagas": ("vagas", coletores.coletar_vagas),
                  "eventos": ("eventos", coletores.coletar_eventos)}
        for fonte in fontes:
            tabela, coletar = etapas[fonte]
            resultado = coletar(cliente, config)
            with conn:
                contagem = banco.gravar(conn, tabela, resultado.itens, inicio)
                if resultado.completo:
                    contagem.inativadas = banco.inativar_nao_vistas(
                        conn, tabela, coletores.FONTE, inicio)
            erros_total += len(resultado.erros)
            resumos.append(f"{fonte}: {contagem}")
            log.info("%s: %s", fonte, contagem)
            for erro in resultado.erros:
                log.warning("%s: %s", fonte, erro)
        if erros_total:
            status = "parcial"
    except (RobotsIndisponivel, BloqueadoPorRobots) as erro:
        log.error("coleta interrompida: %s", erro)
        status = "falha"
        resumos.append(str(erro))
    except Exception as erro:               # qualquer surpresa vira "falha"
        log.exception("erro inesperado")
        status = "falha"
        resumos.append(f"{type(erro).__name__}: {erro}")
    banco.finalizar_execucao(conn, id_execucao, agora(), status,
                             " | ".join(resumos))
    conn.close()
    log.info("execução %d terminou: %s (%d pedidos, %d repetições)", id_execucao,
             status, getattr(cliente, "pedidos", 0),
             getattr(cliente, "repeticoes", 0))
    return {"ok": SUCESSO, "parcial": PARCIAL, "falha": FALHA}[status]
```

Read it in the order things happen:

1. **Opens the database and records the start** of the run, with the status `rodando` ("running"). If the program dies halfway, the record shows it did not finish.
2. **Reads robots.txt**. If it cannot (`RobotsIndisponivel`), nothing is collected.
3. **For each source** (jobs, events): collects, stores and, **only if the collection was complete**, deactivates what disappeared. All of this inside `with conn:`, a transaction: either the whole batch is stored, or nothing.
4. **Decides the status**: `ok` (no errors), `parcial` (there were errors, but something was stored) or `falha` (something prevented the collection).
5. **Finalizes the run record**, with the status and a summary.

The final `try/except` turns **any surprise** into `falha`, with the error in the log, instead of a program that simply vanishes.

## // When is a collection complete?

Only a **complete** collection may deactivate what disappeared (Module 10). In each situation below, the collector sets `completo = False`, and the orchestrator **deactivates nothing** in that source:

| Situation | Why the collection is incomplete |
|---|---|
| A list page failed, even after the retries | You do not know which jobs were on it |
| The page limit was reached | There may be pages that were not visited |
| Pagination went into a **cycle** (a page points back to one already visited) | The pages after the cycle were never visited |
| An item **exists on the site, but came broken** (a job without a title or a link, an invalid event) | It appeared: if it was already in the database, it cannot be deactivated for "not appearing" |

A different case is the **detail** page that fails. The job was recognized, and the collection is still complete. The description, however, **could not be read today**: the pipeline does not store an empty value in its place. It keeps the last known description, and the run ends as **partial** (code `1`).

> **A LESSON ABOUT THE BAD PATH**
> In a test run while producing this material, a collection in which **a single job** came broken deactivated **all 20 jobs** in the database, because the collection was considered complete. And a temporary detail failure turned a good description into an empty one. Both bugs only appeared when someone tested the **bad path**, not the happy one. Automated tests for these cases now prevent both.

## // Exit codes

When a program ends, it returns a number to the system: the **exit code**. By convention, `0` means "it worked", and any other number, "there was a problem". That is how a scheduler (Module 13) knows whether the run was good. The pipeline uses four:

| Code | Means | When |
|---|---|---|
| `0` | Success | It collected everything, with no errors |
| `1` | Partial | It collected, but there were errors (a page failed, an unreadable date...) |
| `2` | Failure | It did not collect: `robots.txt` blocked it or could not be read, the site is down, or there was an unexpected error |
| `3` | Already running | Another run is still in progress |

## // The log

A program that runs on its own **has to tell what it did**, because nobody is watching. Python has the `logging` module, and the pipeline configures it to write to **two places**: the terminal and a file (`logs/coleta.log`), which **rotates** when it reaches 1 MB (keeping 3 old files), so it never grows without limit:

```python
def configurar_logging(pasta: str, detalhado: bool = False) -> None:
    Path(pasta).mkdir(parents=True, exist_ok=True)
    formato = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s")
    raiz = logging.getLogger("coleta")
    raiz.handlers.clear()
    raiz.setLevel(logging.DEBUG if detalhado else logging.INFO)
    arquivo = RotatingFileHandler(Path(pasta) / "coleta.log",
                                  maxBytes=1_000_000, backupCount=3,
                                  encoding="utf-8")
    console = logging.StreamHandler()
    for destino in (arquivo, console):
        destino.setFormatter(formato)
        raiz.addHandler(destino)
```

The result is a record with time and level (`INFO` for normal things, `WARNING` for what deserves attention, `ERROR` for failures). These are real lines (the times were replaced with `HH:MM:SS`):

```
HH:MM:SS INFO    robots.txt lido; espera entre pedidos: 0.05s
HH:MM:SS INFO    vagas: 20 coletadas, 0 erros
HH:MM:SS INFO    vagas: 20 novas, 0 atualizadas, 0 iguais, 0 inativadas
HH:MM:SS INFO    eventos: 8 coletados, 0 erros
HH:MM:SS INFO    eventos: 8 novas, 0 atualizadas, 0 iguais, 0 inativadas
HH:MM:SS INFO    execução 1 terminou: ok (24 pedidos, 0 repetições)
```

## // Command-line arguments

The values that change (the site address, the database file, the wait) are not written in the code: they come from the command line, through the `argparse` module. The help, generated on its own, is this:

```
usage: python -m coleta [-h] [--base-url BASE_URL] [--banco BANCO]
                        [--pasta-logs PASTA_LOGS] [--espera ESPERA]
                        [--max-paginas MAX_PAGINAS] [--so {vagas,eventos}]
                        [-v]

Coleta vagas e eventos do Mural Tech

options:
  -h, --help            show this help message and exit
  --base-url BASE_URL
  --banco BANCO
  --pasta-logs PASTA_LOGS
  --espera ESPERA       segundos entre pedidos (padrão: o Crawl-delay do site)
  --max-paginas MAX_PAGINAS
  --so {vagas,eventos}
  -v, --detalhado
```

(The texts `options:` and `show this help message` come from Python itself.) Notice `--espera` ("wait"): if you pass **nothing**, the pipeline uses the `Crawl-delay` from `robots.txt` (1 second). While studying locally, `--espera 0.1` speeds things up, and it is acceptable **only against your training site**.

## // The lock against two simultaneous runs

What if the 7:00 collection is still running when the scheduler fires the 7:15 one? Two simultaneous runs could write to the same database, and double the load on the site. The solution is a **lock**: a file that exists while a run is in progress.

```python
class Trava:
    """Impede duas execuções ao mesmo tempo, com um arquivo de trava."""

    def __init__(self, caminho: str, validade_horas: float = 6.0):
        self.caminho = caminho
        self.validade = validade_horas * 3600

    def adquirir(self) -> bool:
        Path(self.caminho).parent.mkdir(parents=True, exist_ok=True)
        for _ in range(2):
            try:
                fd = os.open(self.caminho, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                idade = time.time() - os.path.getmtime(self.caminho)
                if idade < self.validade:
                    return False
                log.warning("trava abandonada há %.1f h: removendo", idade / 3600)
                os.remove(self.caminho)
                continue
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return True
        return False

    def liberar(self) -> None:
        if os.path.exists(self.caminho):
            os.remove(self.caminho)
```

The secret is in `os.O_CREAT | os.O_EXCL`: create the file **only if it does not exist**, in a single indivisible operation. Whoever manages to create it owns the lock; whoever cannot, exits with code `3`. An **abandoned** lock (the program died without releasing it) is removed after 6 hours, so the pipeline does not stay blocked forever. And `main()` makes sure the lock is released at the end, with `finally`:

```python
def main(argv=None) -> int:
    args = ler_argumentos(argv)
    config = Config(base_url=args.base_url, banco=args.banco,
                    pasta_logs=args.pasta_logs, espera=args.espera,
                    max_paginas=args.max_paginas)
    configurar_logging(config.pasta_logs, args.detalhado)
    trava = Trava(config.banco + ".lock")
    if not trava.adquirir():
        log.error("outra execução está em andamento: saindo")
        return JA_EM_EXECUCAO
    try:
        fontes = (args.so,) if args.so else ("vagas", "eventos")
        return executar(config, fontes)
    finally:
        trava.liberar()
```

## // Running it for real

With Mural Tech running, the pipeline runs with `python -m coleta`. These are **three consecutive runs** (day 1, day 1 again, and the site's day 2), with `--espera 0.05`. The summaries are the real ones:

```
EXECUÇÃO 1 (dia 1)
vagas: 20 novas, 0 atualizadas, 0 iguais, 0 inativadas
eventos: 8 novas, 0 atualizadas, 0 iguais, 0 inativadas
execução 1 terminou: ok (24 pedidos, 0 repetições)       código de saída: 0

EXECUÇÃO 2 (dia 1 de novo)
vagas: 0 novas, 0 atualizadas, 20 iguais, 0 inativadas
eventos: 0 novas, 0 atualizadas, 8 iguais, 0 inativadas
execução 2 terminou: ok (24 pedidos, 0 repetições)       código de saída: 0

EXECUÇÃO 3 (dia 2)
vagas: 3 novas, 2 atualizadas, 17 iguais, 1 inativadas
eventos: 2 novas, 0 atualizadas, 8 iguais, 0 inativadas
execução 3 terminou: ok (26 pedidos, 0 repetições)       código de saída: 0
```

(The real output also has the "coletadas" (collected) lines and the times, and was summarized here.) See what each run shows: the first **fills** the database (24 requests: 3 list pages, 20 detail pages and 1 events page). The second **changes nothing**: everything "igual" (unchanged), the idempotence from Module 10. The third notices the **next day**: 3 new jobs, 2 with a changed salary, 1 that disappeared (deactivated), and 2 new events.

The database keeps the history of every run, in the `execucoes` ("runs") table:

```
(1, 'ok', 'vagas: 20 novas, 0 atualizadas, 0 iguais, 0 inativadas | ...')
(2, 'ok', 'vagas: 0 novas, 0 atualizadas, 20 iguais, 0 inativadas | ...')
(3, 'ok', 'vagas: 3 novas, 2 atualizadas, 17 iguais, 1 inativadas | ...')
```

(The summaries were shortened: each one continues with the events part.)

### When the site is not up

And the bad case? With the site address pointing to a port where nobody answers:

```
ERROR   coleta interrompida: robots.txt inacessível: ...Max retries exceeded...
INFO    execução 1 terminou: falha (0 pedidos, 0 repetições)
código de saída: 2
```

The pipeline **collected nothing** (without a readable `robots.txt`, the RFC's rule is not to collect), logged the reason, **stored the run as a failure** in the database and exited with code `2`. That is exactly what a scheduler needs to know something went wrong.

## // The pipeline's tests

The `tests/test_pipeline.py` file runs the **whole** pipeline, against Mural Tech, which starts inside the test itself. The test names say what they guarantee:

| Test | Guarantees |
|---|---|
| `test_primeira_execucao_grava_vagas_e_eventos` | 20 jobs and 8 events in the database |
| `test_executar_de_novo_nao_duplica_nada` | Idempotence |
| `test_o_dia_seguinte_traz_novas_atualizadas_e_inativas` | `3 novas, 2 atualizadas, 17 iguais, 1 inativadas`, `v015` inactive, `v003`'s salary updated |
| `test_dados_limpos_no_banco` | Salary in cents, tags, ISO date, prices |
| `test_falha_no_detalhe_gera_resultado_parcial_mas_guarda_a_vaga` | Code `1`, job stored (without a description, on the first collection) |
| `test_falha_no_detalhe_preserva_a_descricao_ja_conhecida` | The good description does **not** become empty, and the job stays "unchanged" |
| `test_coleta_incompleta_por_vaga_quebrada_nao_inativa_ninguem` | One broken job does not deactivate the other 20 |
| `test_coleta_com_paginacao_em_ciclo_nao_inativa_ninguem` | A pagination cycle deactivates nobody |
| `test_pagina_de_lista_que_falha_nao_inativa_ninguem` | An incomplete collection does not deactivate |
| `test_site_fora_do_ar_devolve_falha` | Code `2` and status `falha` |
| `test_main_recusa_duas_execucoes_ao_mesmo_tempo` | Code `3` |
| `test_trava_abandonada_e_removida` | The old lock does not block forever |

In total, the project has **79 tests**. And the **reverse proof**, which shows they are useful: when you deliberately turn off the "unchanged" detection in `banco.py`, **3 tests fail** (idempotence and updating stop working); when you turn off respect for `robots.txt`, **1 test fails**. The completeness tests were proven the same way: without cycle detection, **2 fail**; if the known description is erased again, **1 fails**; if a broken job stops making the collection incomplete, **3 fail**. With the changes undone, all 79 pass again.

## // Good example × bad example

**Bad example**: a script that, on error, prints a message and ends with code `0`:

```python
try:
    coletar()
except Exception:
    print("deu erro")
```

The scheduler thinks **it worked**, and nobody finds out.

**Good example**: log it, store the status and return a code that tells the truth:

```python
return {"ok": SUCESSO, "parcial": PARCIAL, "falha": FALHA}[status]
```

## // Common errors

| Error | Why it happens | How to fix it |
|---|---|---|
| The pipeline exits with code `3` | There is a lock from a previous run | Check whether another run is in progress; if not, delete the `.lock` file |
| Every job shows up as "updated" | The fingerprint includes something that always changes (such as a time) | Leave out of the hash any field that varies without the content varying |
| Jobs deactivated by mistake | It deactivated after an incomplete collection | Only deactivate when `completo` is true |
| The log grows nonstop | Rotation is missing | Use `RotatingFileHandler` |
| The scheduler never warns about failures | The program always exits with `0` | Return nonzero codes when something fails |
| An error "vanishes" without a trace | The `except` swallows the error without logging | Use `log.exception(...)` |

## // Guided practice

1. With Mural Tech on day 1, run `python -m coleta --espera 0.1`, and then query the database (`dados/vagas.db`).
2. Run it **again**, and check "20 iguais".
3. Switch the site to day 2 (`curl http://127.0.0.1:8080/_dev/dia/2`) and run it: check the new, updated and deactivated ones.
4. Run `echo $?` right after a run, and check the exit code.
5. Stop the site and run it again: the code should be `2`, and the `execucoes` table should have a `falha` row.
6. Open `logs/coleta.log` and read the history.

## // Practice on your own

> **CHALLENGE**
> Add the `--max-paginas 1` option to the pipeline, and run it. What happens to the jobs left out? Expected result: the collection takes only the first page (8 jobs), the collector logs the error "limite de páginas atingido" ("page limit reached") and sets `completo = False`, the run ends as **partial**, and **no job is deactivated**. Reread, in `coletores.py`, the `else` of the `for` loop, and explain why it exists.

## // Applying it to the week's project

1. In the project folder, build the `coleta/` package with the files `config.py`, `http.py`, `parsers.py`, `limpeza.py`, `modelos.py`, `coletores.py`, `banco.py`, `executar.py`, `__init__.py` and `__main__.py`.
2. Run `python -m coleta --help`, and then a complete collection.
3. Check `dados/vagas.db` and `logs/coleta.log`.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> One night, the job collection ends fine, but the event collection fails because the events page went down. What does the pipeline store, what is the run's status, and what is the exit code?

Answer: the **jobs are stored** normally (each source is a separate transaction), the events are not, and the run ends as **partial**, with code **1**, and the events page error in the log. The events already in the database **are not deactivated** (their collection was incomplete). Tomorrow, when the site is back, the pipeline completes what was missing. That is why the pipeline separates the sources, and why code `1` exists: something worked, something did not, and whoever reads the record needs to know it.

## // Module summary

- [ ] I know the orchestrator calls the pieces in the right order, and takes care of the record and the result.
- [ ] I know the four exit codes, and why they matter to a scheduler.
- [ ] I can configure `logging` with a rotating file, and read a log.
- [ ] I can use `argparse`, and I know `--espera` without a value uses the site's `Crawl-delay`.
- [ ] I can use a lock to prevent simultaneous runs.
- [ ] I know why the pipeline is idempotent, and what each count in the summary means.
- [ ] I know only a complete collection may deactivate what disappeared.

---

**Next module:** `13-scheduling-the-collection.md`, the pipeline works when you call it. What is left is making it run on its own.

`Study Material // Coffee & Code`
