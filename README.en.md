# Coffee & Code | WEEK 07 | Data & Scraping (Part 1: Collection)

[Português](README.md) · English

```text
> module: sem-07
> topic: data & scraping (collection)
> status: online
> coffee loaded
```

Material for **Week 07** of the Coffee & Code track, a technology club founded by Software Engineering students at PUCPR and open to anyone who wants to learn by building.

This week teaches how to **collect data from the web in an organized, polite and repeatable way**: download pages, extract what matters, clean it, store it in a database without duplicates and make all of it run on its own. The result is an **automatic capture pipeline into the database**, with Requests, BeautifulSoup, SQLite and scheduling.

> **A standalone week:** it does not require any other week of the club. The HTML, Python and SQL that collection needs are introduced from scratch. This is Part 1 of the "Data & Scraping" module; analyzing the data is left for Part 2.

> **About the language:** the English material lives in [`docs-eng/`](docs-eng/), with the same structure as [`docs/`](docs/) (Portuguese); the READMEs have an English version with the `.en.md` suffix. The diagrams and the runnable examples' code (names, messages and comments) stay in Portuguese.

## Where to start

**[docs-eng/00-start-here.md](docs-eng/00-start-here.md)**: read this one first. It gives the week's overview and the whole collection pipeline.

Then follow the modules in order. Modules `01` to `14` make up the main track:

| # | Module | About |
|---|---|---|
| 01 | [How the web delivers pages](docs-eng/01-how-the-web-delivers-pages.md) | Request, response, status and the page built by JavaScript |
| 02 | [HTML for those who will extract](docs-eng/02-html-for-those-who-will-extract.md) | Tags, attributes, the tree and the field plan |
| 03 | [Ethics, terms and robots.txt](docs-eng/03-ethics-terms-and-robots-txt.md) | May you collect? And how, politely? |
| 04 | [Essential Python for collection](docs-eng/04-essential-python-for-collection.md) | Virtual environment and the Python that collection uses |
| 05 | [requests: downloading pages](docs-eng/05-requests-downloading-pages.md) | Timeout, status, encoding and session |
| 06 | [BeautifulSoup: reading the HTML](docs-eng/06-beautifulsoup-reading-the-html.md) | `find`, CSS selectors and the parsers |
| 07 | [The first scraper: jobs](docs-eng/07-the-first-scraper-jobs.md) | List, detail and pagination |
| 08 | [Cleaning and normalizing](docs-eng/08-cleaning-and-normalizing.md) | Salaries, dates and prices become data |
| 09 | [The second scraper: events](docs-eng/09-the-second-scraper-events.md) | Reusing what already exists |
| 10 | [SQLite: storing the data](docs-eng/10-sqlite-storing-the-data.md) | Upsert, no duplicates, and knowing what changed |
| 11 | [Robustness and good manners](docs-eng/11-robustness-and-good-manners.md) | Retries, `Retry-After`, `ETag` and alarms |
| 12 | [The end-to-end pipeline](docs-eng/12-the-end-to-end-pipeline.md) | Orchestration, log, lock and exit codes |
| 13 | [Scheduling the collection](docs-eng/13-scheduling-the-collection.md) | `cron`, and running on its own |
| 14 | [Guided project](docs-eng/14-guided-project.md) | Building it, checking it in 14 items and taking it to a real source |

Modules `15` and `16` are the **experienced track**, and module `17` is a bonus in that track. They are all optional and can be read after the essentials:

| # | Module | About |
|---|---|---|
| 15 | [Async scraping with httpx](docs-eng/15-async-scraping-with-httpx.md) | Limited concurrency and the rate limiter |
| 16 | [Playwright: pages with JavaScript](docs-eng/16-playwright-pages-with-javascript.md) | A browser driven by code, and the page's API |
| 17 | [Selenium and the comparison](docs-eng/17-selenium-and-the-comparison.md) | Bonus: the other tool, and when to pick each one |

And, to look up whenever you need:

- [Runnable examples](docs-eng/example/README.md): the training site, the lesson scripts, the pipeline and the experienced track
- [Challenges](docs-eng/challenges.md): optional, to go beyond what is asked
- [Deliverable](docs-eng/deliverable.md): final checklist before closing the week

## The training site

The week uses **Mural Tech**, a **fictional** site that runs on your computer (`python3 servidor.py`), with made-up jobs and events. It behaves like a real site: it has pagination, a `robots.txt`, a "day 2" with changes, slow pages, `429` and `503` errors, broken HTML and a page built by JavaScript.

The reason: real sites change without warning, many forbid collection, and practice needs to work every time.

## The runnable examples

The [`docs/example/`](docs/example/) folder has all of the week's code:

- `site-treino/`: Mural Tech, built only with Python's standard library.
- `scripts/`: the lesson scripts for modules 03 to 11.
- `pipeline/`: the final project, with 79 automated tests.
- `agendamento/`: the script that `cron` calls, and examples.
- `veterano/`: async `httpx`, Playwright and Selenium, with tests.

Everything was run, and the outputs quoted in the modules come from those runs. See the [folder's README](docs-eng/example/README.md) to install and run them.

It is **reference material, not an answer key**: the example is there for you to see one possible solution when you get stuck, not to copy.

## The deliverable

At the end of Week 07, the repository of **your project** (not this one) should have an **automatic capture pipeline into the database**: a program that, on every run, reads the `robots.txt`, collects the jobs and events from the training site, cleans the data, writes it to a SQLite database **without duplicates**, **deactivates** what went offline, records the run, writes a log and ends with an **exit code** that a scheduler understands.

```text
pipeline-coleta/
├── coleta/           ← the pipeline package (python -m coleta)
├── tests/            ← the automated tests
├── requirements.txt
├── .gitignore        ← without .venv/, dados/ and logs/
└── README.md         ← how to install, start the site, run and test
```

The full checklist is in [docs-eng/deliverable.md](docs-eng/deliverable.md).

## Class submissions

There are no Week 07 submissions yet. Want to be the first? See [how to submit](entregas/README.en.md).

## Versions and date checked

Material verified with **Python 3.12.3**, `requests` 2.34.2, `beautifulsoup4` 4.15.0, `lxml` 6.1.3, `httpx` 0.28.1, `protego` 0.7.0, `croniter` 6.2.4, `pytest` 9.1.1, SQLite 3.45.1, Playwright 1.63.0 and Selenium 4.51.0. The BeautifulSoup documentation, RFC 9309 (`robots.txt`) and the Playwright documentation were checked on **October 9, 2026**. Libraries change often: if something differs from what is here, the official documentation is the reference.

**What was and was not tested.** All the code was run on Linux, and the outputs quoted in the modules are the real ones. The training site, the scripts of every module, the pipeline (79 tests), the experienced track (16 tests) and the scheduling expressions were tested. **Not tested:** real sites (all practice used the fictional site), `cron` itself, the Windows Task Scheduler, macOS `launchd` and, in general, Windows and macOS. Playwright and Selenium were tested against a script-driven Chromium, not the browser that `playwright install` downloads.

## Before collecting from any real site

Go through the questions in Module 03: is there an official API? Do the terms of use allow it? Does the `robots.txt` allow the path? Is there a `Crawl-delay`? Does the page have personal data? If any answer is "not allowed" or "I don't know", **stop**. This material is not legal advice.

## How it works

Coffee & Code is **100% online**. Each module was written to be self-contained: you study at your own pace, and you can move ahead faster, go back to previous weeks and look things up during the project.

The weekly meetings, also online, are there to answer questions, review concepts, code together and show what you have built, **not to lecture** (Brasília time, UTC-3):

- **Wednesday**: 8:00 PM to 9:30 PM
- **Saturday**: 10:00 AM to 11:30 AM

Both cover the same content. Pick whichever fits your week best, and you do not need to stay on the call for the whole time.

## Stuck?

Bring a specific question to the meeting or to Discord. `"select('.vaga') returns an empty list, but the cards show up in the browser"` usually gets solved much faster than `"my scraper doesn't work"`.

This week, always compare the HTML that `requests` received with what the browser shows: the difference between the two solves a good share of the problems.

And remember: not knowing something is not a problem. Knowing how to research is part of the field.

## Diagrams

All the diagrams used in the modules are in [`docs/assets/svg/`](docs/assets/svg/), as SVG.

## Previous weeks

- [WEEK 01: Kickoff & Design System](https://github.com/coffeecodepucpr/coffee-code-sem01)
- [WEEK 02: Web Interface (Part 1: Layout)](https://github.com/coffeecodepucpr/coffee-code-sem02)
- [WEEK 03: Web Interface (Part 2: Interactivity)](https://github.com/coffeecodepucpr/coffee-code-sem03)
- [WEEK 04: Data Modeling](https://github.com/coffeecodepucpr/coffee-code-sem04)
- [WEEK 05: Central RESTful API (Part 1: CRUD)](https://github.com/coffeecodepucpr/coffee-code-sem05)
- [WEEK 06: Central RESTful API (Part 2: Integration)](https://github.com/coffeecodepucpr/coffee-code-sem06)

Full track and upcoming weeks: [Coffee & Code profile](https://github.com/coffeecodepucpr)

---

```text
HTTP 418: I'm a teapot
> ready to code
```
