# Week 07 Deliverable

[Português](../docs/entregavel.md) · English

`WEEK 07 // Data & Scraping, Part 1: Collection`

---

## // What to submit

**An automatic capture pipeline into the database**: a project that collects jobs and events from the training site, cleans the data, stores everything in a SQLite database **without duplicates**, records each run and can be scheduled to run on its own.

## // Checklist

### Collection and good manners
- [ ] The program reads `robots.txt` and **does not visit** what it forbids.
- [ ] It respects the wait between requests (the `Crawl-delay`, or whatever you configured).
- [ ] It uses an honest `User-Agent`, with the project name and a contact.
- [ ] **Every** request has a `timeout`.
- [ ] It retries `429`, `502`, `503`, `504` and network errors with a growing wait, and does **not** retry `404`.
- [ ] Pagination follows the Next link, and has the `visitadas` and `MAX_PAGINAS` safeguards.

### Data
- [ ] The job and event fields are extracted with selectors **by meaning**.
- [ ] Money is stored in integer cents, and dates in ISO 8601.
- [ ] Missing is `None` (never zero, and never a text like `A combinar`).
- [ ] A record with bad data does not bring down the collection: it is stored with a warning, or discarded with a log entry.

### Database
- [ ] The schema has a unique key (`fonte`, `id_externo`) and `NOT NULL` on the essential fields.
- [ ] Running **twice** duplicates nothing (idempotence).
- [ ] The collection classifies each item as new, updated or unchanged.
- [ ] What disappears from the site is **deactivated**, not deleted, and only after a **complete** collection.
- [ ] A collection is **incomplete** (and nothing is deactivated) when a page fails, pagination goes into a cycle, the page limit is reached, or an item arrives broken.
- [ ] A temporary failure on the detail page **does not erase** the description already known.
- [ ] All values go by parameter (`?`), never by f-string.

### Running
- [ ] On every run, one row in the `execucoes` table, with status and summary.
- [ ] The program writes a log to a file, with rotation.
- [ ] The exit codes are `0` (success), `1` (partial), `2` (failure) and `3` (already running).
- [ ] A lock prevents two runs at the same time.

### Scheduling
- [ ] There is a script that prepares the environment and calls the pipeline with absolute paths.
- [ ] The schedule expression was **checked** (with `croniter`), and runs **once a day**.
- [ ] I know how to check whether collection is running (log and `execucoes` table).

### Tests and documentation
- [ ] There are automated tests for the cleaning, the database and the pipeline, and they pass.
- [ ] The `README.md` explains how to install, start the site, run and test.
- [ ] The `.gitignore` leaves out `.venv/`, `dados/` and `logs/`.

## // How to submit

1. Put the project in a repository (for example, on GitHub), **without** the virtual environment, the database and the logs.
2. In the `README.md`, include the commands to install and run, and the list of what was tested and what was not.
3. Show the group, in a meeting, **two consecutive runs** of the pipeline: the first filling the database and the second showing "everything unchanged". Then switch the site to day 2 and show the third, with the new jobs and the deactivated one.

## // For those who did the experienced track

- [ ] An async collector with `httpx`, with a **concurrency limit** and a **minimum pace** between requests.
- [ ] A page built by JavaScript, collected with Playwright (or Selenium), or through the API it uses.
- [ ] A measurement, with your own numbers, of how much async gains **and of when it stops gaining** (Module 15).

---

`Study Material // Coffee & Code`
