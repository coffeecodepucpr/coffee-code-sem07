# Module 09, The Second Scraper: Events

[Português](../docs/09-o-segundo-scraper-eventos.md) · English

`WEEK 07 // Data & Scraping, Part 1: Collection`

---

## // Before you start

You have a working job scraper, with cleaning. This module collects a **second source**, tech events, and serves to show what a well-organized project gains: almost everything you built is **reused**, and only what is truly specific to events needs to be written.

## // The field plan for events

Before any code, the plan (Module 02). Each event on the `/eventos/` page is a list item (`li.evento`). This is a real excerpt:

```html
<li class="evento" data-id="e001">
  <h3><a href="/eventos/e001">Python Day Curitiba</a></h3>
  <p class="quando">sábado, 17 de outubro de 2026, 14h00</p>
  <p class="onde">Curitiba, PR</p>
  <p class="preco">Gratuito</p>
  <p class="organizacao">Comunidade Py Sul</p>
</li>
```

| Field | Selector | Example | Cleaning (Module 08) |
|---|---|---|---|
| id | `data-id` of `li.evento` | `e001` | none |
| title | `h3 a` | `Python Day Curitiba` | `limpar_texto` |
| when | `.quando` | `sábado, 17 de outubro de 2026, 14h00` | `parse_data_evento` |
| where | `.onde` | `Curitiba, PR` or `Online` | `limpar_texto`, and `online` if it is `Online` |
| price | `.preco` | `R$ 120,00 (estudantes: R$ 60,00)` | `parse_preco` |
| organizer | `.organizacao` | `Comunidade Py Sul` | `limpar_texto` |
| link | `href` of `h3 a` | `/eventos/e001` | `urljoin` |

## // What changes, and what stays the same

| Step | Jobs | Events |
|---|---|---|
| Download the page | `baixar()` from Module 05 | **same** |
| Read the HTML | `ler_html()` | **same** |
| Clean text and money | `limpar_texto`, `para_centavos` | **same** |
| Pagination | 3 pages, following the Next link | **does not exist**: it is a single page |
| Detail page | 20 pages, one per job | **we do not visit them** (the list is enough) |
| Selectors | `article.vaga` | `li.evento` (**new**) |
| Dates | `<time datetime>` (already ISO) | long text in Portuguese (**new**: `parse_data_evento`) |
| Template | `Vaga` | `Evento` (**new**) |

Almost everything is reused. What is new fits in **one reading function** and **one template**.

## // Reading the events

This is the new function, in `parsers.py`:

```python
def ler_eventos(sopa, url_pagina: str) -> list[dict]:
    eventos = []
    for item in sopa.select("li.evento"):
        link = item.select_one("h3 a")
        eventos.append({
            "id_externo": item["data-id"],
            "titulo": texto(link),
            "quando": texto(item.select_one(".quando")),
            "onde": texto(item.select_one(".onde")),
            "preco": texto(item.select_one(".preco")),
            "organizacao": texto(item.select_one(".organizacao")),
            "url": (urljoin(url_pagina, link["href"])
                    if link is not None else None),
        })
    return eventos
```

And this is the script (`09_eventos.py`) that uses it, together with the cleaning functions you already have:

```python
import requests

from limpeza import limpar_texto, parse_data_evento, parse_preco
from parsers import ler_eventos, ler_html

BASE = "http://127.0.0.1:8080"
url = f"{BASE}/eventos/"
sopa = ler_html(requests.get(url, timeout=10))

eventos = []
for bruto in ler_eventos(sopa, url):
    preco, preco_estudante = parse_preco(bruto["preco"])
    onde = limpar_texto(bruto["onde"])
    eventos.append({
        "id": bruto["id_externo"],
        "titulo": bruto["titulo"],
        "inicio": parse_data_evento(bruto["quando"]),
        "local": onde,
        "online": (onde or "").lower() == "online",
        "preco_centavos": preco,
        "preco_estudante_centavos": preco_estudante,
    })

print("eventos coletados:", len(eventos))
for e in eventos[:3]:
    print(e)
print("online:", [e["id"] for e in eventos if e["online"]])
print("gratuitos:", [e["id"] for e in eventos if e["preco_centavos"] == 0])
print("sem data:", [e["id"] for e in eventos if e["inicio"] is None])
```

```
eventos coletados: 8
{'id': 'e001', 'titulo': 'Python Day Curitiba', 'inicio': '2026-10-17T14:00',
 'local': 'Curitiba, PR', 'online': False, 'preco_centavos': 0,
 'preco_estudante_centavos': None}
{'id': 'e002', 'titulo': 'Meetup de Dados', 'inicio': '2026-10-22T19:30',
 'local': 'Online', 'online': True, 'preco_centavos': 0,
 'preco_estudante_centavos': None}
{'id': 'e003', 'titulo': 'Workshop de Docker na Prática',
 'inicio': '2026-10-24T09:00', 'local': 'Curitiba, PR', 'online': False,
 'preco_centavos': 4000, 'preco_estudante_centavos': None}
online: ['e002', 'e006', 'e007']
gratuitos: ['e001', 'e002', 'e005', 'e006', 'e008']
sem data: []
```

(The real output writes each dictionary on a single line, and it was broken here to fit the page.)

Notice two details. **Free is 0, not None**: the event has a price, and it is zero (Module 08). And the `online` field is a **cleaning decision**: the page only says `Online` instead of the location, and our data needs a field of its own to answer "which events are online?".

## // Dates that do not work out

The event with the impossible date does not bring anything down. In `coletores.py`, the event collector **keeps the event even without a readable date, and logs an error**:

```python
        inicio = limpeza.parse_data_evento(bruto["quando"])
        if inicio is None:              # guarda o evento, mas avisa
            resultado.erros.append(
                f"evento sem data legível: {bruto['id_externo']}")
```

It is the same philosophy as the rest of the week: **do not lose the data** that came, and **do not hide the problem**. An event without a date is still useful (it has a title and a link), and the logged error warns that the date needs attention. An automated test checks this behavior, using a fake events page with an impossible date.

## // Two sources, one way of working

What you just did is the pattern of any collection project that grows:

1. **Field plan** for the new source.
2. **A reading function** (HTML to dictionaries of raw text).
3. **The cleaning**, reusing what exists, and adding only what is new.
4. **A template** for the clean data.

A third source would follow the same four steps. If, instead, you had **copied and pasted** the job scraper and changed what was needed, every fix (like the impossible date one) would have to be made twice, and soon the two copies would differ.

## // Good example × bad example

**Bad example**: copy the whole job scraper and edit it:

```python
# coletar_eventos.py: 90% igual ao coletar_vagas.py
```

**Good example**: small, shared functions (`baixar`, `ler_html`, `limpar_texto`), and only what is different in files of their own (`ler_eventos`, `Evento`).

## // Common errors

| Error | Why it happens | How to fix it |
|---|---|---|
| `inicio: None` on every event | The date text changed format | Compare with the real HTML, and adjust `_DATA_LONGA` |
| A month is not recognized (`março`) | The name has an accent, and the `MESES` table does not | Check the spelling in `MESES`; `\w` already accepts accents |
| An "Online" event shows up with a city | The text is `Online` with a different spelling | Compare in lowercase: `onde.lower() == "online"` |
| The student price does not show up | The text has only one value | The second value is `None`, which is expected |
| Trusting the weekday in the text | The site can get it wrong | Use only day, month, year and time |

## // Guided practice

1. Open `/eventos/` in the browser and read an event's HTML with `Ctrl+U`.
2. Run `09_eventos.py` and compare the output with the page.
3. In `servidor.py`, turn on day 2 (`/_dev/dia/2`) and run it again: two new events appear (`e009` and `e010`).
4. Edit the site's HTML (or use a copy) so that an event has the date `30 de fevereiro` (February 30) and run the script: what shows up in `sem data`?

## // Practice on your own

> **CHALLENGE**
> From the event list, print the ones that happen **on a weekend**. Hint: `datetime.date.fromisoformat(inicio[:10]).weekday()` returns 0 (Monday) to 6 (Sunday), and the weekend is 5 or 6. Expected result on day 1: `e001`, `e003`, `e005` and `e007`.

## // Applying it to the week's project

1. In the project folder, add `ler_eventos` to `parsers.py` and the `Evento` dataclass to `modelos.py`.
2. Create `coletar_eventos.py`, which builds a list of `Evento` with the cleaning.
3. Print the online events and the free ones, and check against the page.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> A third source shows up: a course site, with pagination and detail, like the jobs, but with dates in the `17/10/2026` format. Which parts of your code do you reuse, and which do you write?

Answer: you reuse `baixar`, `ler_html`, `limpar_texto`, `para_centavos`, the pagination loop from Module 07 and the idea of validating the record. You write **the reading function** (the new site's selectors), **a date function** for the `17/10/2026` format (much simpler than the events one), and **a template** for the courses. That is the gain of an organized project: the amount of new code is proportional to what is really new.

## // Module summary

- [ ] I can make the field plan for a new source.
- [ ] I can separate what is reused from what is specific to the source.
- [ ] I can read an event list and clean Portuguese dates and prices.
- [ ] I know free is `0`, not `None`, and that `online` is a cleaning decision.
- [ ] I can keep a record with bad data, **with a warning**, instead of losing or hiding it.
- [ ] I know why not to copy and paste a scraper.

---

**Next module:** `10-sqlite-storing-the-data.md`, the data is clean. What is left is storing it, without duplicates.

`Study Material // Coffee & Code`
