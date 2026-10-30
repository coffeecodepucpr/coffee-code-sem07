# Module 02, HTML for Those Who Will Extract

[Português](../docs/02-html-para-quem-vai-extrair.md) · English

`WEEK 07 // Data & Scraping, Part 1: Collection`

---

## // Before you start

To extract a piece of data from a page, you need to know **where it is**. This module teaches you to read HTML from the point of view of someone who will collect: without trying to learn how to build sites, just recognizing the pieces and choosing the most reliable ones. It requires no prior knowledge of HTML.

## // What HTML is

> **HTML: IN SIMPLE WORDS**
> It is text with **marks** that say what each piece is: a heading, a paragraph, a link, a list. The browser reads the marks and draws the page. You, with BeautifulSoup, will read the same marks to find the data.

The marks are called **tags**, and they come in pairs, one opening and one closing. This is a real job card from Mural Tech:

```html
<article class="vaga" data-id="v002">
  <h2 class="titulo"><a href="/vagas/v002">Analista de Dados Pleno</a></h2>
  <p class="empresa">Pinhão Dados</p>
  <p class="local">Remoto</p>
  <span class="modalidade">Remoto</span>
  <span class="nivel">Pleno</span>
  <span class="salario">R$ 7.000 a R$ 9.500</span>
  <time datetime="2026-10-08">08/10/2026</time>
  <ul class="tags">
    <li>python</li><li>pandas</li><li>sql</li><li>power bi</li></ul>
</article>
```

(The real HTML writes the tag list on a single line, and it was broken here to fit the page.)

Read it like this: `<p class="empresa">Pinhão Dados</p>` is a **paragraph** (`p`) that has an **attribute** (`class`) with the value `empresa` ("company"), and whose **content** is the text `Pinhão Dados`. Attributes go inside the opening tag, in the `name="value"` format.

## // The tree

Tags **nest**: the `<h2>` is inside the `<article>`, and the `<a>` is inside the `<h2>`. That is why HTML is said to form a **tree**, and we use family words to describe it: the `article` is the **parent** of the `h2`; the `h2` and the `p` are **siblings**; the `a` is a **child** of the `h2` and a **descendant** of the `article`.

<div align="center">
<img src="../docs/assets/svg/arvore-html.svg" alt="The HTML of a job card as a tree, with the CSS selectors that lead to each piece of data" width="640">
</div>

This idea is the basis of everything: **extracting is choosing a path in the tree**. In Module 06, you will write these paths as selectors.

## // The pieces that show up most

| Tag | What it is | Where it shows up on Mural Tech |
|---|---|---|
| `h1`, `h2`, `h3` | Headings, from largest to smallest | The title of the page, the job, the event |
| `p` | A paragraph | Company, location, description |
| `span` | A piece of text, with no meaning of its own | Work mode, level, salary |
| `a` | A link. The destination is in the `href` attribute | The job title leads to the detail |
| `ul` and `li` | A list and its items | The job's tags, the requirements |
| `time` | A date. The machine value is in `datetime` | The publication date |
| `article` | A standalone block | Each job card |
| `div` | A generic block, with no meaning | The job description |

## // The attributes worth their weight in gold

For someone collecting, three attributes are especially important:

- **The class attribute**: gives the element a name. An element can have several classes (`class="vaga destaque"`). It is the most common hook for selectors.
- **The id attribute**: a **unique** name on the page (`<div id="resultado">`).
- **The data- attributes**: attributes made to hold data. Notice the card's `data-id="v002"`: it is the **job's identifier on the site**, and it will be used to recognize the same job across different collections (Module 10).

And two attributes hold the data **already clean**, and it is worth preferring them to the displayed text:

| Attribute | In the example | Why it is better than the text |
|---|---|---|
| `datetime` of `time` | `2026-10-08` | The displayed text (`08/10/2026`) changes with the language; the attribute is standardized |
| `href` of `a` | `/vagas/v002` | It is the real address, which you will visit |

## // The detail of a job

The detail page (`/vagas/v003`) uses the same ideas, with more information. This is a real excerpt:

```html
<article class="vaga-detalhe" data-id="v003">
<h1 class="titulo">Engenheiro(a) de Software Sênior</h1>
<p class="empresa">Araucária Labs</p>
<p class="local">Curitiba, PR (Presencial)</p>
<p class="salario">R$ 14.000 a R$ 18.000</p>
<time datetime="2026-10-07">Publicada em 07/10/2026</time>
<div class="descricao"><p>A Araucária Labs procura uma pessoa para ...</p></div>
<h2>Requisitos</h2>
<ul class="requisitos"><li>Experiência com java</li>...</ul>
</article>
```

Notice that the same data can have **different formats** on different pages: in the list, the location is `Curitiba, PR`, and in the detail it is `Curitiba, PR (Presencial)`. This is the kind of difference that cleaning (Module 08) will absorb.

## // Choosing what to extract

Before writing code, make a **field plan**: for each piece of data you want, note where it is. This is the plan for the job list:

| Field | Where it is | Selector (Module 06) | Example |
|---|---|---|---|
| job id | `data-id` attribute of the `article` | `article.vaga` | `v002` |
| title | text of the link inside the `h2` | `h2.titulo a` | `Analista de Dados Pleno` |
| company | text of the `p` | `.empresa` | `Pinhão Dados` |
| salary | text of the `span` | `.salario` | `R$ 7.000 a R$ 9.500` |
| date | `datetime` attribute | `time` | `2026-10-08` |
| tags | text of each `li` | `ul.tags li` | `python`, `pandas`... |
| detail link | `href` attribute | `h2.titulo a` | `/vagas/v002` |

## // Good example × bad example

**Bad example**: pointing at the element's **position**. A selector like "the third `span` of the second `div`" breaks the day the site adds any element before it.

**Good example**: pointing at the **meaning**. The `.salario` class says what the element **is**, and keeps working even if the site rearranges the rest of the page. Always prefer, in this order: a data attribute (`data-id`), a meaningful class (`.salario`), and only as a last resort the position.

## // Common errors

| Error | Why it happens | How to fix it |
|---|---|---|
| Searching the code for a text that is on screen, and not finding it | The page is built by JavaScript | See Module 01 |
| An odd accent or symbol in the text (`&amp;`, `&lt;`) | HTML writes certain symbols as "entities" | BeautifulSoup converts them on its own: `Cafe &amp; C&oacute;digo` becomes `Cafe & Código` |
| Mixing up `class` and `id` | `class` can repeat, and `id` is unique | For lists of items, use classes |
| Expecting the text to come clean | HTML keeps spaces and line breaks | Use `get_text(strip=True)` (Module 06) |

## // Guided practice

1. With Mural Tech running, open `/vagas/` in the browser and use `Ctrl+U` to see the source code.
2. Find the first `<article class="vaga">` and read its HTML, field by field, next to the screen.
3. Open `/vagas/v003` and do the same.
4. Save a page to study calmly: `curl -s http://127.0.0.1:8080/vagas/ -o vagas.html`, and open `vagas.html` in your editor.

## // Practice on your own

> **CHALLENGE**
> Build the field plan for a job's **detail page** (`/vagas/v003`), in the same format as the table above. Which fields does the detail have that the list **does not**? Hint: compare the list card with `article.vaga-detalhe`. Answer: the **description** (`.descricao`) and the **requirements** (`ul.requisitos li`).

## // Applying it to the week's project

1. In `anotacoes.md`, paste the field plan for the job list and the one for the detail.
2. Add a "what may be missing" column: for example, the salary may come as `A combinar` ("to be agreed"). You will handle this in Module 08.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> Two selectors find a job's title: `h2.titulo a` and "the first link on the page inside the third block". Which is better, and what happens to each one if the site adds a banner at the top of the page?

Answer: `h2.titulo a`, because it points at the **meaning**. The new banner shifts the position of everything, and the position selector starts pointing at the wrong element (or at nothing), without warning. The class selector keeps finding the title, because the banner did not change what a title is.

## // Module summary

- [ ] I can read a tag, an attribute and the content of an element.
- [ ] I can describe the tree with parent, child and sibling.
- [ ] I know what `class`, `id` and `data-*` are for.
- [ ] I know `datetime` and `href` hold the clean data.
- [ ] I can make a field plan before writing code.
- [ ] I prefer selectors by meaning, not by position.

---

**Next module:** `03-ethics-terms-and-robots-txt.md`, you already know how to read a page. Before collecting for real, comes the most important question: are you allowed to?

`Study Material // Coffee & Code`
