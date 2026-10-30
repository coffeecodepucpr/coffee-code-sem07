# Module 00, Start Here

[Português](../docs/00-comece-aqui.md) · English

`WEEK 07 // Data & Scraping, Part 1: Collection`

---

## // Welcome to Week 07

Imagine you want to keep track of the tech jobs and events that show up on several sites in your city. Opening every site every day is tiring. Copying and pasting by hand is worse: you forget a page, paste a wrong value, lose what changed since yesterday. Now imagine a program that does this work on its own: it visits the pages, reads the jobs and events, stores everything in a database and, the next day, only adds what is new.

That is the idea of this week. The data you care about is **inside pages made for people to read**, not for programs to consume. Learning to extract it in an organized, polite and repeatable way is the subject of **data collection**.

> **THIS WEEK IS STANDALONE**
> This is Part 1 of the "Data & Scraping" module (collection), but it was written to be read **on its own**. You do not need to have studied anything before: the HTML, Python and SQL that collection needs are introduced from scratch, at the right size.

## // What web scraping is

> **WEB SCRAPING: IN SIMPLE WORDS**
> It is using a program to download web pages and **extract structured data from them**, such as the title, company and salary of each job. The program does what a person would do in the browser (open the page, read, take notes), only fast, without getting tired and in a repeatable way.

A scraper combines four skills, which are this week's modules: **requesting** a page (the `requests` library), **reading** the HTML (the BeautifulSoup library), **storing** what was read (the SQLite database) and **repeating** it all on its own (automation).

> **BEFORE ANY CODE: GOOD MANNERS**
> Taking data from a site is not the same as looking at a page. A robot can overload a server, read areas the owner asked not to be visited, or collect personal data protected by law. Module 03 is entirely about this, and it comes **before** the first scraper on purpose. This week, everything you collect comes from a training site created for that.

## // The collection pipeline

<div align="center">
<img src="../docs/assets/svg/pipeline-de-coleta.svg" alt="The collection pipeline: collect, extract, clean, store and record, with good manners at every step, and the scheduling" width="640">
</div>

A **pipeline** is a sequence of steps in which the output of one is the input of the next. This week's pipeline has five steps and a schedule:

| Step | What it does | Tool |
|---|---|---|
| 1. Collect | Downloads the page's HTML, with a time limit | `requests` |
| 2. Extract | Reads the HTML and separates the fields of each job | BeautifulSoup |
| 3. Clean | Standardizes dates, salaries and text | Python |
| 4. Store | Writes to the database **without duplicating** what already exists | SQLite |
| 5. Record | Notes what happened in this run | `logging` and a table |
| 6. Schedule | Repeats everything on its own, every day | `cron` |

## // What you will build

- A **training site**, Mural Tech, which runs on your computer and behaves like a real site: it has pagination, a `robots.txt`, slow pages, `429` and `503` errors, and a page built by JavaScript.
- **Collection scripts** that extract the jobs and events from Mural Tech.
- A **complete pipeline** that writes the data to a SQLite database, **without duplicates**, and records each run.
- A **schedule** that runs this pipeline on its own.

## // Why a training site, and not a real site

There are three reasons, and the third is the most important:

1. **Real sites change.** A site changes its HTML without warning, and a tutorial that worked yesterday breaks today. Mural Tech does not change unless you ask it to.
2. **Many sites forbid collection** in their terms of use, or limit it. Practicing on a site you are allowed to use avoids problems.
3. **You can make mistakes freely.** A loop that requests a thousand pages by accident brings down your training site, not a company's.

Module 03 teaches how to evaluate a real site, and Module 14 has an optional adaptation step for anyone who wants to take the pipeline to a real, permitted source.

## // What is left out

> **NOT THIS WEEK YET**
> **Data analysis** (charts, statistics) is left for Part 2. Also left out: login, captchas and any form of **bypassing a site's protections** (this is never taught here), server databases (such as PostgreSQL), deploying to the cloud and collecting personal data.

## // What you need to start

- A computer with Windows, macOS or Linux and permission to install programs.
- **Python 3.10 or higher** (Module 04 shows how to check and how to set up the environment).
- A text or code editor and a terminal.
- An internet connection **only to install** the libraries: the training site runs on your computer.
- **No prior knowledge** of HTML, SQL or scraping. Basic Python is reviewed in Module 04.

> **VERSIONS, DATE CHECKED AND WHAT WAS TESTED**
> The material was verified with **Python 3.12.3**, `requests` 2.34.2, `beautifulsoup4` 4.15.0, `lxml` 6.1.3, `httpx` 0.28.1, Playwright 1.63.0, Selenium 4.51.0 and SQLite 3.45.1. The BeautifulSoup 4.15.0 documentation, RFC 9309 (`robots.txt`) and the Playwright documentation were checked on **October 9, 2026**. All scripts were **run on Linux against the training site**, and the outputs quoted in the modules are the real ones. The browser tools of the experienced track were tested with Chromium 153 (a build packaged by third parties): `playwright install chromium` on your machine installs a different build, and small differences are possible. **Not tested:** real sites, Windows, macOS and the Windows Task Scheduler. Libraries change often: if something differs from what is here, the official documentation is the reference.

## // The two tracks

**If you are starting out**, you have never done web scraping. The main path assumes this: Modules 01 to 14 introduce each concept before it is needed and end in a working collection pipeline.

**If you already have experience**, you have written scrapers with `requests`. Modules 15 to 17, clearly marked as the experienced track and placed after the essentials, cover **async scraping** (`httpx` and `asyncio`) and **browser tools** (Playwright and Selenium) for pages built by JavaScript.

Both tracks use the same training site.

## // Week 07 map

| Module | Content | You will be able to |
|---|---|---|
| 01 | How the web delivers pages | Tell a static page from one built by JavaScript |
| 02 | HTML for those who will extract | Read the tag tree and write selectors |
| 03 | Ethics, terms and `robots.txt` | Evaluate whether, and how, you may collect from a site |
| 04 | Essential Python for collection | Set up the environment and write functions, dictionaries and files |
| 05 | `requests`: downloading pages | Download a page with a timeout and handle errors |
| 06 | BeautifulSoup: reading the HTML | Extract fields with `find` and CSS selectors |
| 07 | The first scraper: jobs | Collect the list, the detail and every page |
| 08 | Cleaning and normalizing | Turn dates, salaries and text into clean data |
| 09 | The second scraper: events | Reuse the code on a second source |
| 10 | SQLite: storing the data | Write without duplicates, with a unique key and upsert |
| 11 | Robustness and good manners | Retry with a wait, and respect `429` and `503` |
| 12 | The end-to-end pipeline | Join the steps, with a log and an exit code |
| 13 | Scheduling the collection | Run the pipeline on its own, without double runs |
| 14 | Guided project | Have the complete, verified pipeline |
| 15 | Async scraping with `httpx` (experienced) | Collect several pages at the same time, with a limit |
| 16 | Playwright: pages with JavaScript (experienced) | Extract from pages that only exist after the JavaScript |
| 17 | Selenium and the comparison (experienced, bonus) | Choose between the two browser tools |

Each module is a standalone file, but they were written to be read in this order: you do not write a scraper without knowing how to read HTML, and you do not publish one without knowing good manners.

---

**Next module:** `01-how-the-web-delivers-pages.md`, before extracting data from a page, you need to understand how it reaches your program.

`Study Material // Coffee & Code`
