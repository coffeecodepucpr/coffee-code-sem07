# Module 14, Guided Project

[Português](../docs/14-projeto-guiado.md) · English

`WEEK 07 // Data & Scraping, Part 1: Collection`

---

## // Before you start

All the pieces are ready. This module **closes the main track**: you build the complete pipeline, run a checklist of **14 checks** with the expected result of each, and see how to take what you built to a real source, carefully. At the end, you have the week's deliverable: **an automatic capture pipeline into the database**.

## // The project structure

<div align="center">
<img src="../docs/assets/svg/estrutura-do-projeto.svg" alt="The files of the coleta package and how they relate: executar calls the collectors and the database, and the collectors use http, parsers, limpeza and modelos" width="640">
</div>

Each file has **one reason to change**:

| File | Changes when... |
|---|---|
| `config.py` | A configuration value changes (timeout, page limit) |
| `http.py` | The way pages are requested changes (wait, retries, `robots.txt`) |
| `parsers.py` | The **site's HTML changes** (the selectors) |
| `limpeza.py` | A new salary, date or price format shows up |
| `modelos.py` | A new field to store shows up |
| `coletores.py` | A source's route changes (pages, details) |
| `banco.py` | The database schema changes |
| `executar.py` | The way the run is orchestrated changes (arguments, exit codes, log) |

The gain is practical: when the site changes its HTML (and it will), **you know which file to touch**: `parsers.py`. The other seven do not need to know.

## // Building it

1. Create the project folder and copy the `pipeline/` and `site-treino/` folders into it.
2. Inside `pipeline/`, create the virtual environment and install the libraries:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-testes.txt
```

3. In **another terminal**, start the training site: `python3 servidor.py`, inside `site-treino/`.
4. Back in the first terminal, inside `pipeline/`, run the collection: `python -m coleta --espera 0.1`.

## // The verification checklist

The expected results below were obtained by actually running the checklist. To query the database, use the `sqlite3 dados/vagas.db` command (if you have it) or a small Python script with the `sqlite3` module.

| # | What to do | What should happen |
|---|---|---|
| 1 | With the site running, open `http://127.0.0.1:8080/` | Mural Tech's home page appears |
| 2 | Run `python -m coleta --espera 0.1` | The log shows `vagas: 20 novas, 0 atualizadas, 0 iguais, 0 inativadas` and `eventos: 8 novas, ...`, and ends with `ok (24 pedidos, 0 repetições)` |
| 3 | Query `SELECT count(*) FROM vagas` and `FROM eventos` | `20` and `8` |
| 4 | Run it **again** | `20 iguais` and `8 iguais`, and the counts from item 3 **do not change** |
| 5 | Query job `v002` (`salario_min`, `salario_max`) and `v001` (`cidade`, `uf`) | `700000` and `950000`; `Curitiba` and `PR` |
| 6 | Query event `e004` (`inicio`, `online`, `preco_centavos`, `preco_estudante_centavos`) | `2026-11-06T08:30`, `0`, `12000` and `6000` |
| 7 | Switch the site to day 2 (`curl http://127.0.0.1:8080/_dev/dia/2`) and run it | `vagas: 3 novas, 2 atualizadas, 17 iguais, 1 inativadas` and `eventos: 2 novas, ...` |
| 8 | Query job `v003` (salary) and `v015` (`ativa`) | `1500000` and `1900000`; `0` (inactive, and **not deleted**) |
| 9 | Run `echo $?` right after a good run | `0` |
| 10 | Run the pipeline **twice at the same time**, in two terminals | The second exits with code `3` and the message "outra execução está em andamento" ("another run is in progress") |
| 11 | Stop the site, and run it | The exit code is `2`, and the `execucoes` table has a row with status `falha` |
| 12 | Run `pytest -k proibida` | `1 passed`: the pipeline does **not** visit a page that `robots.txt` forbids |
| 13 | Run `pytest -k 503` | `1 passed`: a `503` is retried until it works |
| 14 | Run `pytest` | `79 passed` |

If an item does not match, go back to the corresponding module: items 2 to 4 and 7 and 8 come from Modules 10 and 12; 5 and 6, from 08 and 09; 9 to 11, from 12; 12 and 13, from 03 and 11.

## // What the automated tests cover

Item 14 sums up the project's life insurance. Of the 79 tests, **most run without a browser and without internet**: Mural Tech starts inside the test itself, on a free port, and the test starts and stops it on its own. They cover cleaning (salary, location, date and price cases), reading the HTML, the HTTP client (`robots.txt`, waits, retries), the database (upsert, deactivation, constraints) and the whole pipeline (idempotence, the next day, failures, the lock, exit codes, incomplete collection and preserved data).

What the tests do **not** check: the behavior of **real sites**, `cron` itself and the Windows Task Scheduler. For the first, the checklist in the next section is your defense.

## // From the training site to the real world (optional)

> **READ FIRST**
> This section is optional, and **none of it was tested against a real site** while producing this material. Before pointing the pipeline at any site, go through the diagram in Module 03: official API? Terms of use? `robots.txt`? `Crawl-delay`? Personal data? If any answer is "not allowed" or "I don't know", **stop**.

If, after that, you have a **permitted** source (a site that authorizes collection, or a public API), these are the steps:

1. **Start small.** Run with `--max-paginas 1` and `--so vagas`, and look at the result before anything else.
2. **Save a page** (`curl -o pagina.html`) and write its field plan (Module 02).
3. **Adjust parsers.py**: the selectors. It is the only file that **needs** to change, in most cases.
4. **Adjust limpeza.py**, if the salary, date or price formats are different.
5. **Change the address** (`--base-url`), the source name (`FONTE` in `coletores.py`) and the `User-Agent` (in `config.py`, with **a real contact of yours**).
6. **Write a test with the saved HTML**: a page stored in a file, and a test that checks the extracted fields. It is your safety net for when the site changes.
7. **Respect the Crawl-delay** and **schedule at most once a day**.

### When the site changes

It will change. The process is the one from Module 11: the empty-fields alarm goes off, you open a new page, compare it with the saved one, **adjust the selector**, update the test's saved HTML, and run the suite. If the site owner asks you to stop, **stop**.

## // Good example × bad example

**Bad example**: pointing the pipeline at a real site **without reading** anything first, with the example `User-Agent`, and scheduling it every 5 minutes.

**Good example**: reading `robots.txt` and the terms, testing with a single page, identifying yourself with a real contact, keeping a test page, and scheduling once a day.

## // Common errors

| Error | Why it happens | How to fix it |
|---|---|---|
| `ModuleNotFoundError: No module named 'coleta'` | You ran it outside the `pipeline/` folder | Run `python -m coleta` **inside** `pipeline/` |
| `ConnectionError` on `robots.txt` | The training site is off | Start `servidor.py` |
| The counts in item 7 do not match | The site is not on day 2, or the database already had day 2 data | Delete `dados/` and redo from day 1 |
| Item 10 does not give code `3` | The first run finished too fast | Use `--espera 1` on the first so it takes longer |
| Tests fail because a port is busy | Another program is using the port | The tests choose a free port, so restart the terminal |

## // Guided practice

1. Build the project and go through the 14 checklist items, marking each one.
2. Take a **database snapshot** after item 7 (copy the `vagas.db` file) and query it.
3. Run the tests, and then **break something on purpose** (for example, delete a `?` from an `INSERT`) and see which test catches it.

## // Practice on your own

> **CHALLENGE**
> Switch the `robots.txt` reader in `http.py` from `urllib.robotparser` to **Protego** (Module 03). You change three points: the `pip install protego`, the creation (`Protego.parse(texto)`) and the question (`can_fetch(url, agente)`, with the **argument order reversed**). The `robots.txt` tests in `test_http.py` should keep passing.

## // Applying it to the week's project

This module **is** the application. Your deliverable (checklist in `deliverable.md`) is the working pipeline, with the checklist verified.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> Six months later, you pick the project back up. The site changed, and salaries now come empty. What do you open first, and what does the project give you to fix it quickly?

Answer: you open `parsers.py`, because it is the only file that knows the HTML. The project gives you **the log** (which shows empty fields, if you added the Module 11 alarm), **the runs table** (which tells you since when things degraded), **the saved test HTML** (to compare the old page with the new one), and **the tests** (which tell you whether the fix broke something else). Every organizational decision this week exists so that this day is an afternoon, not a week.

## // Module summary

- [ ] I built the complete pipeline, and I know the reason for each file.
- [ ] I went through the 14 checklist items, and the results matched.
- [ ] I know what the tests cover, and what they do **not** cover.
- [ ] I know the steps to adapt the pipeline to a real source, and that I must stop if there is no permission.
- [ ] I know what to do when the site changes.

---

**Next module:** `15-async-scraping-with-httpx.md` (**experienced track**). Whoever wants to collect faster, carefully, continues here. Whoever is on the main track can go straight to `deliverable.md`.

`Study Material // Coffee & Code`
