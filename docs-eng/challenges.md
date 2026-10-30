# Week 07 Optional Challenges

[Português](../docs/desafios.md) · English

`WEEK 07 // Data & Scraping, Part 1: Collection`

---

The challenges below are **optional**: they are for anyone who wants to go beyond the deliverable. Each one has an indication of what should happen, and none requires anything from outside this week.

## // Basic level

**1. Collect the event detail.** The pipeline only reads the event list. Add a visit to each event's detail page (`/eventos/e001`). Mural Tech, however, **does not have** that page: `/eventos/e001` returns `404`. What should your collector do? (Hint: isolate the failure, as with the job detail.)

**2. A text report.** Write a script that queries the database and prints: how many active jobs exist per work mode, the average maximum salary per level (in reais) and the next 3 free events. Compare with the numbers in Module 10.

**3. Export to CSV.** Write a script that reads the active jobs from the database and writes them to a `vagas.csv` file, with the `csv` module. Open the file in a spreadsheet and check the accents.

## // Intermediate level

**4. A third source.** Mural Tech has no more pages, so make one up: add a `/cursos/` page to `servidor.py` with 5 courses (title, date in the `17/10/2026` format, price), and write its scraper following the four steps of Module 09. What did you reuse, and what did you write?

**5. An empty-fields alarm in the pipeline.** Make the pipeline count each source's empty fields and, if more than 30% of a field (such as the salary) comes back `None`, log a `WARNING` and mark the run as `parcial`. Test it by simulating the class change from Module 11.

**6. The RFC's robots.txt reader.** Replace `urllib.robotparser` with Protego (see Module 14), and add a test with example 5.2 from RFC 9309 (`Allow: /example/page/` and `Disallow: /example/page/disallowed.gif`), which the standard library reader gets wrong.

**7. Conditional request.** Make the client keep the `ETag` of each list page and send `If-None-Match`. When a `304` comes back, what does the pipeline do with that page's jobs? (Hint: it needs a copy of the data, and Module 11 explains why.)

## // Advanced level

**8. An API of your own for the data.** Build a small API (with the library you prefer) that serves the database's jobs as JSON, with filters by work mode and by minimum salary. The data you collect starts being **consumed** by another program.

**9. A price history.** Instead of just updating the salary of a job that changed, keep **every version** in a `vagas_historico` table (id, date, salary). Run day 1 and day 2, and query how `v003` evolved.

**10. Notifications.** When a new job with `python` in its tags shows up, write a line to a `novidades.txt` file. Run day 2 and check.

## // For the experienced track

**11. Async collection in the pipeline.** In `coletores.py`, replace the sequential visit to the job details with the async collector from Module 15, keeping respect for `Crawl-delay` with the rate limiter. How much time do you gain? If the site's `Crawl-delay` is 1 second, do you gain anything?

**12. Playwright with a cache.** In Module 16, the `/vagas-js/` page is built by JavaScript. Write a collector that discovers the **API call** with Playwright **once**, and then collects every page directly from the API, with `httpx`.

**13. A browser test in the pipeline.** Write a test that uses Playwright (and skips itself if there is no browser) and checks that `/vagas-js/` shows 8 cards after waiting.

---

`Study Material // Coffee & Code`
