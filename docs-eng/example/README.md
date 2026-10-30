# Week 07 Examples

[Português](../../docs/example/README.md) · English

`WEEK 07 // Data & Scraping, Part 1: Collection`

> The code lives in [`docs/example/`](../../docs/example/), and its names, messages and comments are in Portuguese, the same as the rest of the track.

Everything here was **run on Linux**. See the week's `README.en.md` for what was and was not tested.

## // What is in each folder

| Folder | What it is | Modules |
|---|---|---|
| `site-treino/` | Mural Tech: the fictional training site | 01 to 17 |
| `scripts/` | Lesson scripts, with `parsers.py` and `limpeza.py` | 03 to 11 |
| `pipeline/` | The final project, with the tests | 12 and 14 |
| `agendamento/` | The script `cron` calls, and examples | 13 |
| `veterano/` | Async `httpx`, Playwright and Selenium, with tests | 15 to 17 |

## // Setting up the environment

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r pipeline/requirements.txt
pip install -r pipeline/requirements-testes.txt
```

For the experienced track, also `pip install -r veterano/requirements.txt` (and, for Playwright, `playwright install chromium`). On Windows, activating the environment is different, and **was not tested**.

## // Starting the training site

In a terminal, inside `site-treino/`:

```
python3 servidor.py                    # dia 1, porta 8080
python3 servidor.py --dia 2            # dados do "dia 2"
python3 servidor.py --latencia 0.2     # cada resposta demora 0,2 s
```

(Day 1 on port 8080; the "day 2" data; each response takes 0.2 s.) While studying, switch the day without restarting: `curl http://127.0.0.1:8080/_dev/dia/2` (and `/_dev/dia/1`, `/_dev/reset`).

## // Running the pipeline and the tests

In another terminal, inside `pipeline/`:

```
python -m coleta --espera 0.1          # coleta vagas e eventos
python -m coleta --so vagas            # só as vagas
python -m coleta --help                # todas as opções
pytest                                 # 79 testes (o site sobe sozinho)
```

(Collects jobs and events; only the jobs; all the options; 79 tests, and the site starts on its own.) The pipeline writes the database to `dados/vagas.db` and the log to `logs/coleta.log`. The exit codes are `0` (success), `1` (partial), `2` (failure) and `3` (already running). `--espera 0.1` is only acceptable against your **training site**: without it, the pipeline uses the `Crawl-delay` from `robots.txt`.

## // Running the experienced track

Inside `veterano/`, with the site running:

```
python 15_a_comparar.py                # sequencial contra assíncrono
python 16_b_playwright_basico.py       # exige o Playwright e o Chromium
python 17_a_selenium_basico.py         # exige o Selenium e um driver
pytest  # 16 testes; os de navegador se pulam sem navegador
```

(Sequential against async; requires Playwright and Chromium; requires Selenium and a driver; 16 tests, and the browser ones skip themselves without a browser.)

## // What stays out of the repository

`.venv/`, `dados/` and `logs/` (the output of runs), and any `__pycache__`.

---

`Study Material // Coffee & Code`
