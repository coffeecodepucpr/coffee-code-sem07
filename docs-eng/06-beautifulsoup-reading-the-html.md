# Module 06, BeautifulSoup: Reading the HTML

[Português](../docs/06-beautifulsoup-lendo-o-html.md) · English

`WEEK 07 // Data & Scraping, Part 1: Collection`

---

## // Before you start

In Module 05 you downloaded a page with `requests` and kept the HTML in a variable. To Python, that HTML is **a long text with no structure**. This module introduces the tool that turns that text into something you can navigate and query: **BeautifulSoup**. It is the central module of the week, because this is where a page becomes data.

All examples use Mural Tech, the training site. Start it in a terminal (`python3 servidor.py`, inside the `site-treino` folder) and leave it running.

## // The problem: HTML is text, and text has no structure

What is the most obvious way to get a job's title? Search the text for what is between `<h2>` and `</h2>`. See what happens, in a real run against the jobs page:

```python
import re

import requests

BASE = "http://127.0.0.1:8080"
html = requests.get(f"{BASE}/vagas/", timeout=10).text

# Tentativa 1: procurar <h2>título</h2>
achados = re.findall(r"<h2>(.*?)</h2>", html)
print("regex <h2>...</h2> achou:", len(achados))

# Tentativa 2: aceitar o atributo class, mas o título está dentro de um <a>
achados = re.findall(r'<h2 class="titulo">(.*?)</h2>', html)
print("regex com class achou:", len(achados))
print("primeiro resultado:", achados[0])
```

```
regex <h2>...</h2> achou: 0
regex com class achou: 8
primeiro resultado: <a href="/vagas/v002">Analista de Dados Pleno</a>
```

The first attempt found **zero** titles, because the real `<h2>` has an attribute (`class="titulo"`). The second found eight, but returned **the link's HTML**, not the title. And any small change on the site (a single quote instead of a double one, an extra attribute, a line break) would break the expression again. Regular expressions see **characters**. What you want to see are **elements**.

## // What BeautifulSoup is

> **BEAUTIFULSOUP: IN SIMPLE WORDS**
> It is a Python library that reads HTML text and turns it into a **tree of objects**, which you query by tag name, by class or by a CSS selector. It also handles badly written HTML, which is common on the real web.

Install it, together with `lxml` (a fast HTML reader that BeautifulSoup can use), inside the virtual environment from Module 04:

```
pip install beautifulsoup4 lxml
```

The package name is `beautifulsoup4`, but the import is `from bs4 import BeautifulSoup`. This material was verified with version 4.15.0, and its documentation was checked on October 9, 2026.

## // The first soup

The name "soup" comes from the slang for messy HTML ("tag soup"). You create the soup by passing the page's content and the name of the reader (the *parser*):

```python
import requests
from bs4 import BeautifulSoup

BASE = "http://127.0.0.1:8080"
resposta = requests.get(f"{BASE}/vagas/", timeout=10)
resposta.raise_for_status()

sopa = BeautifulSoup(resposta.content, "lxml")
print("tipo:", type(sopa).__name__)
print("título da página:", sopa.title.get_text())
print("h1:", sopa.h1.get_text())

cartoes = sopa.find_all("article", class_="vaga")
print("cartões:", len(cartoes), "| tipo:", type(cartoes).__name__)

primeiro = cartoes[0]
print("id:", primeiro["data-id"])
print("título:", primeiro.h2.get_text(strip=True))
print("empresa:", primeiro.find("p", class_="empresa").get_text(strip=True))

link = primeiro.find("a")
print("link:", link["href"])
print("atributos do link:", link.attrs)

hora = primeiro.find("time")
print("datetime:", hora["datetime"], "| texto:", hora.get_text())
print("classes:", primeiro["class"])
print("atributo que não existe, com .get:", primeiro.get("data-xyz"))
print("com valor padrão:", primeiro.get("data-xyz", "padrão"))
```

```
tipo: BeautifulSoup
título da página: Vagas | Mural Tech
h1: Vagas de tecnologia
cartões: 8 | tipo: ResultSet
id: v002
título: Analista de Dados Pleno
empresa: Pinhão Dados
link: /vagas/v002
atributos do link: {'href': '/vagas/v002'}
datetime: 2026-10-08 | texto: 08/10/2026
classes: ['vaga']
atributo que não existe, com .get: None
com valor padrão: padrão
```

Notice two things in the code: we use `resposta.content` (the response's **bytes**), not `resposta.text`. Letting BeautifulSoup decide the encoding from the bytes avoids accent errors (see the section on common errors). And `raise_for_status()` makes sure an error page is not read as if it were a jobs page.

| You write | What it means |
|---|---|
| `sopa.title`, `sopa.h1` | The **first** tag with that name on the page |
| `find("p", class_="empresa")` | The first `p` tag with the `empresa` class, or `None` |
| `find_all("article", class_="vaga")` | **All** `article` tags with the `vaga` class, in a list (`ResultSet`) |
| `tag["href"]` | An attribute's value. Raises an error if the attribute does not exist |
| `tag.get("data-xyz")` | An attribute's value, or `None` (or the default you give) |
| `tag.attrs` | All attributes, in a dictionary |
| `tag.get_text(strip=True)` | The text inside the tag, without spaces at the ends |

> **WHY class_ AND NOT class?**
> In Python, `class` is a reserved word (the one that creates classes). Writing `find_all("article", class="vaga")` is a syntax error (`SyntaxError: invalid syntax`). BeautifulSoup solves it with `class_`, with an underscore at the end. Attributes with several classes (`class="vaga destaque"`) come back as a **list**: `['vaga']`.

## // The tree and the selectors

<div align="center">
<img src="../docs/assets/svg/arvore-html.svg" alt="The HTML of a job card as a tree, with the CSS selectors that lead to each piece of data" width="640">
</div>

The diagram shows the HTML of a card and the **tree** BeautifulSoup builds: an `article` with children (`h2`, `p`, `span`, `time` and `ul`), and the `h2` and `ul` with children of their own. Navigating is choosing the path to the data.

A more powerful and shorter way to choose the path is the **CSS selector**, the same language that stylesheets use. BeautifulSoup offers two methods:

| Method | Returns |
|---|---|
| `select("selector")` | **All** matching tags, in a list (empty if none match) |
| `select_one("selector")` | The **first** matching tag, or `None` |

| Selector | What it picks | Example on this page |
|---|---|---|
| `article` | Every `article` tag | The cards |
| `.vaga` | Every element with the `vaga` class | The cards |
| `article.vaga` | An `article` **with** the `vaga` class | The cards |
| `h2.titulo a` | An `a` **inside** an `h2.titulo` (at any level) | The title link |
| `ul.tags li` | Each `li` inside `ul.tags` | The job's tags |
| `a[rel=next]` | An `a` with the `rel` attribute equal to `next` | The "Próxima" ("Next") link |

Here is the script that extracts all the cards on the page, using selectors:

```python
import requests
from bs4 import BeautifulSoup

BASE = "http://127.0.0.1:8080"


def texto(tag):
    """O texto limpo de uma tag, ou None se a tag não existe."""
    return tag.get_text(strip=True) if tag is not None else None


def ler_cartao(cartao):
    return {
        "id": cartao["data-id"],
        "titulo": texto(cartao.select_one("h2.titulo a")),
        "empresa": texto(cartao.select_one(".empresa")),
        "local": texto(cartao.select_one(".local")),
        "salario": texto(cartao.select_one(".salario")),
        "publicada": cartao.select_one("time")["datetime"],
        "tags": [li.get_text(strip=True) for li in cartao.select("ul.tags li")],
        "link": cartao.select_one("h2.titulo a")["href"],
    }


resposta = requests.get(f"{BASE}/vagas/", timeout=10)
resposta.raise_for_status()
sopa = BeautifulSoup(resposta.content, "lxml")

vagas = [ler_cartao(c) for c in sopa.select("article.vaga")]
print("vagas extraídas:", len(vagas))
for v in vagas[:3]:
    print(v)

print("só os títulos:", [v["titulo"] for v in vagas[:3]])
print("com 'python' nas tags:", [v["id"] for v in vagas if "python" in v["tags"]])
```

```
vagas extraídas: 8
{'id': 'v002', 'titulo': 'Analista de Dados Pleno', 'empresa': 'Pinhão Dados',
 'local': 'Remoto', 'salario': 'R$ 7.000 a R$ 9.500', 'publicada': '2026-10-08',
 'tags': ['python', 'pandas', 'sql', 'power bi'], 'link': '/vagas/v002'}
só os títulos: ['Analista de Dados Pleno', 'Desenvolvedor(a) Python Júnior',
 'Estágio em Desenvolvimento Web']
com 'python' nas tags: ['v002', 'v001', 'v008', 'v007']
```

(The real output writes each dictionary on a single line, and it was broken here to fit the page. The other two dictionaries were omitted.)

Two decisions in this code are worth their weight in gold. The first is the **dictionary**: each job becomes a dictionary with the same fields, the format the database will receive in Module 10. The second is the `texto()` function, explained next.

> **FIND OR SELECT?**
> Both do the same job. CSS selectors (`select`) tend to be shorter and are the same ones you use in the browser when inspecting a page, which is why this material prefers them. `find` and `find_all` are handy for simple searches, such as `sopa.find("h1")`.

## // The parser: the choice that changes the result

When the HTML is well written, any parser returns the same tree. But the real web is full of broken HTML: tags that were never closed, attributes without quotes. According to the documentation, when the document is invalid, **different parsers build different trees**.

<div align="center">
<img src="../docs/assets/svg/dois-parsers.svg" alt="The same HTML with unclosed li tags, read by html.parser and by lxml, with different trees" width="640">
</div>

Mural Tech has a deliberately broken page (`/quebrado/`), with unclosed `<li>` and `<p>` tags. This script reads it with both parsers:

```python
import requests
from bs4 import BeautifulSoup

BASE = "http://127.0.0.1:8080"
bruto = requests.get(f"{BASE}/quebrado/", timeout=10).content

for parser in ("html.parser", "lxml"):
    sopa = BeautifulSoup(bruto, parser)
    print(f"--- {parser}")
    print("itens da lista (li):", len(sopa.find_all("li")))
    primeiro_li = sopa.find("li")
    print("o primeiro li contém outro li?", primeiro_li.find("li") is not None)
    print("parágrafos (p):", len(sopa.find_all("p")))
    print(str(sopa.body)[:140].replace("\n", " "))
```

```
--- html.parser
itens da lista (li): 2
o primeiro li contém outro li? True
parágrafos (p): 3
<body><ul class="tags"><li>Python<li>SQL</li></li></ul> <p>um<p>dois ...
--- lxml
itens da lista (li): 2
o primeiro li contém outro li? False
parágrafos (p): 3
<body><ul class="tags"><li>Python</li><li>SQL</li></ul> <p>um</p><p>dois ...
```

(The last line for each parser was cut here; the real output continues with the rest of the `<body>`.)

The HTML was the same, and the two parsers agreed on the **count** (2 items, 3 paragraphs), but disagreed on the **structure**: `html.parser` put one `<li>` **inside** the other, and `lxml` left them as **siblings**. A selector such as `ul.tags > li` would find both items in one tree, and only one in the other.

| | `html.parser` | `lxml` |
|---|---|---|
| Installation | Comes with Python | `pip install lxml` |
| Speed | Slower | Faster |
| Broken HTML | Follows the tags literally | Rebuilds the malformed HTML according to the parser's own rules |

> **RULE: WRITE THE PARSER, AND ALWAYS USE THE SAME ONE**
> Always pass the parser's name (`"lxml"` or `"html.parser"`) and use the **same** one across the whole project. Without it, BeautifulSoup picks a parser on its own, and the result may vary from one machine to another. This material uses `"lxml"`.

If you ask for a parser that does not exist, or is not installed, the error is clear:

```
FeatureNotFound: Couldn't find a tree builder with the features you requested:
naoexiste. Do you need to install a parser library?
```

## // When the element does not exist

This is the most common beginner error. Not every job publishes a salary, and a page can change. What happens when the selector finds nothing? This script reproduces the problem with a card that has no salary field:

```python
from urllib.parse import urljoin

from bs4 import BeautifulSoup

HTML = """
<article class="vaga" data-id="x1">
  <h2 class="titulo"><a href="/vagas/x1">Vaga sem salário</a></h2>
  <p class="empresa">Empresa Fictícia</p>
</article>
"""
sopa = BeautifulSoup(HTML, "lxml")
cartao = sopa.select_one("article.vaga")

salario = cartao.select_one(".salario")
print("select_one de algo que não existe:", salario)
print("find com classe errada:", cartao.find("p", class_="nao-existe"))
print("find_all de algo que não existe:", cartao.find_all("span"))

try:
    cartao.select_one(".salario").get_text()
except AttributeError as erro:
    print("AttributeError:", erro)
```

```
select_one de algo que não existe: None
find com classe errada: None
find_all de algo que não existe: []
AttributeError: 'NoneType' object has no attribute 'get_text'
```

The rule: `select_one` and `find` return `None` when they find nothing, and `select` and `find_all` return an **empty list**. Calling `.get_text()` on `None` breaks the program with `AttributeError`. That is why the script at the start of the module uses the `texto()` function, which returns `None` when the tag does not exist, instead of breaking:

```python
def texto(tag):
    """O texto limpo de uma tag, ou None se a tag não existe."""
    return tag.get_text(strip=True) if tag is not None else None
```

With it, a job without a salary becomes `{"salario": None}`, and the scraper moves on. A missing field is **information** (the job did not publish the salary), not a reason for the program to stop.

## // Relative links

The job's `href` is `/vagas/v002`, a **relative** address: it has no `http://` and no server. To download the detail page, you need the full address, and the standard library solves this with `urljoin`:

```python
link = cartao.select_one("h2 a")["href"]
print("link relativo:", link)
print("link absoluto:", urljoin("http://127.0.0.1:8080/vagas/", link))
print("paginação relativa:", urljoin("http://127.0.0.1:8080/vagas/", "?pagina=2"))
```

```
link relativo: /vagas/x1
link absoluto: http://127.0.0.1:8080/vagas/x1
paginação relativa: http://127.0.0.1:8080/vagas/?pagina=2
```

## // Peeking at the tree

When a selector does not find what you expect, the first thing to do is **look**. The `prettify()` method rewrites the tree with indentation, and shows exactly what BeautifulSoup saw:

```python
print(cartao.prettify())
```

```
<article class="vaga" data-id="x1">
 <h2 class="titulo">
  <a href="/vagas/x1">
   Vaga sem salário
  </a>
 </h2>
 <p class="empresa">
  Empresa Fictícia
 </p>
</article>
```

Another useful habit is counting: `len(sopa.select("article.vaga"))` should be 8 on this page. If it is 0, the selector is wrong, the page is not the one you imagined, or the HTML `requests` received **is not the same as what the browser shows** (pages built by JavaScript, the subject of Modules 01 and 16).

## // Good example × bad example

**Bad example**: trusting that the element always exists, and taking the text without cleaning it:

```python
salario = cartao.select_one(".salario").get_text()
```

On a job without a salary, the program breaks with `AttributeError`. And, without `strip=True`, the text may come with line breaks and spaces (the `get_text()` of the whole card, without cleaning, starts with `'\nAnalista de Dados Pleno\nPinhão Dados\n...'`).

**Good example**: handle the absence, and clean the text:

```python
salario = texto(cartao.select_one(".salario"))
```

## // Common errors

These messages and results were obtained by running the code.

| Error | Why it happens | How to fix it |
|---|---|---|
| `AttributeError: 'NoneType' object has no attribute 'get_text'` | The selector found nothing and returned `None` | Use the `texto()` function, or check `if tag is not None` |
| `SyntaxError: invalid syntax` in `find_all(..., class="vaga")` | `class` is a Python reserved word | Write `class_="vaga"`, or use `select("article.vaga")` |
| `FeatureNotFound: Couldn't find a tree builder...` | The requested parser does not exist or is not installed | Check the name (`"lxml"`) and run `pip install lxml` |
| `PÃ¡gina` instead of `Página` | `resposta.text` was used on a page without a `charset` in the header | Pass `resposta.content` (bytes) to BeautifulSoup |
| `select("article.vaga")` returns `[]` | The page does not have those elements (another page, or built by JavaScript) | Look at `prettify()` and compare with what the browser shows |
| `KeyError: 'href'` | You used `tag["href"]` on a tag without that attribute | Use `tag.get("href")` |
| `.string` returns `None` | The tag has several children, and `.string` only works with one | Use `get_text()` |
| Different results on two machines | Each one used a different parser | Write the parser (`"lxml"`) in the code |

The `PÃ¡gina` case deserves proof. Mural Tech has a page that does not declare its encoding (`/legado/vagas`), and `requests`, without that information, assumes `ISO-8859-1`:

```
encoding detectado pelo requests: ISO-8859-1
resposta.text:                    PÃ¡gina 1 de 3
BeautifulSoup(resposta.content):  Página 1 de 3
```

## // Guided practice

1. Start Mural Tech (`python3 servidor.py`, in the `site-treino` folder) and open `http://127.0.0.1:8080/vagas/` in the browser.
2. Run the regular expressions script and confirm the results `0` and `8`.
3. Run the first soup script and read each line of output next to the code.
4. Run the cards script and check that `ler_cartao()` returns one dictionary per job.
5. Run the two parsers script and check the difference between `html.parser` and `lxml`.
6. In the browser, right-click a job, choose **Inspect**, and compare the tree the browser shows with BeautifulSoup's `prettify()`.

## // Practice on your own

> **CHALLENGE**
> Using only what you saw in this module, write a script that reads page 1 of jobs and prints (a) the `id` of the **Remoto** (remote) jobs that have `sql` in their tags, and (b) how many jobs exist in each work mode (`Remoto`, `Híbrido` and `Presencial`). Hint for (b): `collections.Counter`. Expected answers, on page 1: (a) `['v002']`; (b) `{'Remoto': 3, 'Híbrido': 3, 'Presencial': 2}`. Check the work mode with `select_one(".modalidade")`.

## // Applying it to the week's project

1. In your project folder, create the `parsers.py` file and put this module's `texto()` and `ler_cartao()` functions in it. They will be reused in the next modules.
2. Create a second file, `testar_parsers.py`, that imports `ler_cartao` and prints the data of the first job on page 1.
3. If you version the project with Git, make a commit: `git commit -m "Adiciona a leitura dos cartões de vaga com BeautifulSoup"`.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> Your scraper runs fine for weeks. One day, the site changes its HTML, and the salary field becomes `.remuneracao`. What happens to your `ler_cartao()`, with and without the `texto()` function?

Answer: with the `texto()` function, `select_one(".salario")` returns `None`, `texto(None)` returns `None`, and **every job ends up with an empty salary** (`salario: None`), without any error: the program keeps running, and the data comes out incomplete. Without the function, `.get_text()` on `None` breaks the program with `AttributeError` on the first job, which is **louder**, and therefore easier to notice. The lesson: handling absence avoids crashes, but **hides changes on the site**. In Module 11, you learn to count how many fields came empty and to raise an alert when that number spikes.

## // Module summary

- [ ] I know why regular expressions are no good for reading HTML.
- [ ] I can create a soup with `BeautifulSoup(resposta.content, "lxml")`.
- [ ] I can use `find`, `find_all`, `select` and `select_one`, and write simple CSS selectors.
- [ ] I can read text (`get_text(strip=True)`) and attributes (`tag["href"]` and `tag.get`).
- [ ] I know `select_one` and `find` return `None`, and that `select` and `find_all` return a list.
- [ ] I know why the parser matters, and that I should always write it.
- [ ] I can turn a relative link into an absolute one with `urljoin`.
- [ ] I can use `prettify()` to peek at what BeautifulSoup saw.

---

**Next module:** `07-the-first-scraper-jobs.md`, you already know how to read a page. Now, the complete collection: the list, the detail of each job and every page.

`Study Material // Coffee & Code`
