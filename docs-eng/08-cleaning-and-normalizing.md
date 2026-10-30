# Module 08, Cleaning and Normalizing

[Português](../docs/08-limpando-e-normalizando.md) · English

`WEEK 07 // Data & Scraping, Part 1: Collection`

---

## // Before you start

In Module 07, you collected 20 jobs, and every field is **text**: the salary is `R$ 7.000 a R$ 9.500`, not two numbers; the date is text, not a date. A database, however, wants real numbers and dates, so it can sort, sum and compare. This module teaches the bridge between the two worlds: **cleaning** (or normalization), which turns the page's text into usable data.

## // Text is not data

See what the scraper delivers, and what the database needs:

| Field | What the page shows | What the database needs |
|---|---|---|
| Salary | `R$ 7.000 a R$ 9.500` | A minimum and a maximum, as numbers |
| Salary | `A combinar` ("to be agreed") | "Not informed", not a number |
| Salary | `até R$ 11.000` ("up to") | Only the maximum |
| Location | `Curitiba, PR` | The city and the state, separated |
| Event date | `sábado, 17 de outubro de 2026, 14h00` | A standardized date and time |
| Price | `R$ 120,00 (estudantes: R$ 60,00)` | Two values |
| Free text | `  Dev   Python \n Júnior ` | `Dev Python Júnior` |

## // Three modeling decisions

Before writing the functions, three decisions that apply to any data project.

**1. Money in cents, as an integer.** Decimal numbers (`float`) get simple arithmetic wrong, and in Brazil there is an extra trap, the period as the thousands separator:

```
0.1 + 0.2 = 0.30000000000000004
float('7.000') = 7.0         (em português, 7.000 é sete mil)
float('3.200,50') -> ValueError: could not convert string to float: '3.200,50'
```

(In Brazilian Portuguese, `7.000` is seven thousand, and `3.200,50` is three thousand two hundred and fifty cents.) Storing `R$ 7.000` as `700000` (cents, integer) eliminates both problems.

**2. Dates in ISO 8601 format**, such as `2026-10-17T14:00`. It is the international standard (year, month, day, time), and it has a practical advantage: **it sorts correctly as text**, and SQLite and Python understand it.

**3. Missing is None, not zero.** A salary "A combinar" **is not** zero reais: it is information that is missing. A "Gratuito" (free) event **is** zero reais. Mixing the two ruins any average. The rule: `None` means "I do not know", and `0` means "it is zero".

## // The cleaning functions

They all live in a single file, `limpeza.py`, and **know nothing** about HTML, the network or the database: they receive text and return a value. That makes them easy to test.

**Clean text.** Removes repeated spaces and line breaks, and turns empty into `None`:

```python
def limpar_texto(texto: str | None) -> str | None:
    """Tira espaços repetidos e quebras de linha. Vazio vira None."""
    if texto is None:
        return None
    limpo = " ".join(texto.split())
    return limpo or None
```

**Money to cents.** Uses `Decimal`, which does exact decimal arithmetic, removes the thousands period and swaps the decimal comma:

```python
def para_centavos(valor: str) -> int:
    """'7.000' vira 700000 e '3.200,50' vira 320050 (inteiros, sem float)."""
    numero = Decimal(valor.replace(".", "").replace(",", "."))
    return int(numero * 100)
```

**The salary range.** Looks for the `R$ ...` values with a regular expression, and decides what to do based on how many it found:

```python
def parse_faixa_salarial(texto: str | None) -> tuple[int | None, int | None]:
    """Devolve (mínimo, máximo) em centavos. Sem valor: (None, None)."""
    if not texto:
        return (None, None)
    valores = [para_centavos(v) for v in _DINHEIRO.findall(texto)]
    if not valores:
        return (None, None)
    if len(valores) == 1:
        if texto.strip().lower().startswith("até"):
            return (None, valores[0])
        return (valores[0], valores[0])
    return (min(valores), max(valores))
```

**The location, the date and the price:**

```python
def parse_local(texto: str | None) -> tuple[str | None, str | None]:
    """'Curitiba, PR' vira ('Curitiba', 'PR'). 'Remoto' vira (None, None)."""
    texto = limpar_texto(texto)
    if not texto or "," not in texto:
        return (None, None)
    cidade, uf = (parte.strip() for parte in texto.rsplit(",", 1))
    return (cidade, uf.upper())


def parse_data_evento(texto: str | None) -> str | None:
    """'sábado, 17 de outubro de 2026, 14h00' vira '2026-10-17T14:00'."""
    achou = _DATA_LONGA.search(texto or "")
    if not achou:
        return None
    dia, mes, ano, hora, minuto = achou.groups()
    numero_mes = MESES.get(mes.lower())
    if numero_mes is None:
        return None
    try:
        momento = datetime(int(ano), numero_mes, int(dia), int(hora), int(minuto))
    except ValueError:                  # 30 de fevereiro, 25h00...
        return None
    return momento.isoformat(timespec="minutes")


def parse_preco(texto: str | None) -> tuple[int | None, int | None]:
    """Devolve (preço, preço para estudantes) em centavos. 'Gratuito' vale 0."""
    texto = limpar_texto(texto) or ""
    if texto.lower().startswith("gratuito"):
        return (0, None)
    valores = [para_centavos(v) for v in _DINHEIRO.findall(texto)]
    if not valores:
        return (None, None)
    return (valores[0], valores[1] if len(valores) > 1 else None)
```

The month names (`MESES`) and the regular expressions (`_DINHEIRO` and `_DATA_LONGA`) are at the top of the file. Notice that `parse_data_evento` **ignores the weekday** (`sábado`, Saturday) and uses only the numbers: the weekday is redundant, and a site can get it wrong.

This script (`08_demo_limpeza.py`) applies the functions to real examples, and the output is the real one:

```
--- salários (em centavos)
'R$ 7.000 a R$ 9.500'      -> (700000, 950000)
'R$ 4.500'                 -> (450000, 450000)
'R$ 3.200,50'              -> (320050, 320050)
'até R$ 11.000'            -> (None, 1100000)
'A combinar'               -> (None, None)
--- locais
'Curitiba, PR'               -> ('Curitiba', 'PR')
'São José dos Pinhais, PR'   -> ('São José dos Pinhais', 'PR')
'Remoto'                     -> (None, None)
'Online'                     -> (None, None)
--- datas dos eventos
'sábado, 17 de outubro de 2026, 14h00'         -> 2026-10-17T14:00
'sexta-feira, 6 de novembro de 2026, 08h30'    -> 2026-11-06T08:30
'data a confirmar'                             -> None
--- preços (em centavos)
'Gratuito'                             -> (0, None)
'R$ 40,00'                             -> (4000, None)
'R$ 120,00 (estudantes: R$ 60,00)'     -> (12000, 6000)
--- espaços e quebras de linha
'Dev Python Júnior'
```

## // Impossible dates and strange values

The real web is full of odd data, and a cleaning function **must never bring down the program** because of an ugly value. See what Python does with a date like "February 30", or "25h00":

```
ValueError: day is out of range for month
ValueError: hour must be in 0..23
```

That is why `parse_data_evento` wraps the date creation in a `try/except` and returns `None`: the event will be stored **without a date**, and the scraper will log a warning (you will see it in Module 09). The same care applies to money values: the text `R$ .` would make `Decimal` raise `InvalidOperation`, and the regular expression requires a digit right at the start of the number so that never happens.

## // The data template

Once clean, a job's fields go into a **dataclass**, a template with named, typed fields (Module 04). It is the `modelos.py` file:

```python
@dataclass
class Vaga:
    fonte: str
    id_externo: str
    titulo: str
    url: str
    empresa: str | None = None
    cidade: str | None = None
    uf: str | None = None
    modalidade: str | None = None
    nivel: str | None = None
    salario_min: int | None = None
    salario_max: int | None = None
    publicada: str | None = None
    tags: list[str] = field(default_factory=list)
    descricao: str | None = None
    # campos que não deu para ler hoje (diferente de "a página não tem")
    indisponiveis: tuple[str, ...] = ()

    def como_linha(self) -> dict:
        linha = {k: v for k, v in self.__dict__.items()
                 if k not in ("fonte", "id_externo", "indisponiveis")}
        linha["tags"] = ",".join(self.tags)
        return linha

    def conteudo_hash(self) -> str:
        return _hash(self.como_linha())
```

Two methods deserve attention. `como_linha()` returns the fields as a dictionary ready for the database (the tags become comma-separated text). `conteudo_hash()` computes a **fingerprint** of the content: if any field changes, the result changes. In Module 10, this is how the pipeline finds out whether a job **changed** since the last collection.

There is also the `indisponiveis` ("unavailable") field, which does not go to the database: it lists the fields that **could not be read today** (for example, the description, if the detail page failed). It is the difference between "the page has no description" and "I could not fetch the description right now": Module 10 shows what the database does with this.

## // Validating: what to do with a bad record

Not every record deserves to go into the database. A job with no title and no address is useless. The `montar_vaga` function (from the `coletores.py` file) decides:

```python
def montar_vaga(bruto: dict, descricao: str | None,
                indisponiveis: tuple[str, ...] = ()) -> Vaga | None:
    titulo = limpeza.limpar_texto(bruto["titulo"])
    if not titulo or not bruto["url"]:
        return None
    cidade, uf = limpeza.parse_local(bruto["local"])
    minimo, maximo = limpeza.parse_faixa_salarial(bruto["salario"])
    return Vaga(
        fonte=FONTE, id_externo=bruto["id_externo"], titulo=titulo,
        url=bruto["url"], empresa=limpeza.limpar_texto(bruto["empresa"]),
        cidade=cidade, uf=uf,
        modalidade=limpeza.limpar_texto(bruto["modalidade"]),
        nivel=limpeza.limpar_texto(bruto["nivel"]),
        salario_min=minimo, salario_max=maximo, publicada=bruto["publicada"],
        tags=[t.lower() for t in bruto["tags"]], descricao=descricao,
        indisponiveis=indisponiveis,
    )
```

If the title or the address is missing, it returns `None`, and the collector **logs an error** and moves on, instead of storing garbage or stopping everything. But it also marks the collection as **incomplete**: the job exists on the site, it just could not be recognized, and Module 10 explains why that matters.

## // Testing the cleaning

Functions that only receive text and return values are the best ground for **automated tests**: you list the inputs and the expected outputs, and `pytest` checks them all at once. This is an excerpt from the `tests/test_limpeza.py` file:

```python
@pytest.mark.parametrize("texto, esperado", [
    ("R$ 7.000 a R$ 9.500", (700000, 950000)),
    ("R$ 4.500", (450000, 450000)),
    ("R$ 3.200,50", (320050, 320050)),
    ("até R$ 11.000", (None, 1100000)),
    ("A combinar", (None, None)),
    ("R$ .", (None, None)),
    ("", (None, None)),
    (None, (None, None)),
])
def test_faixa_salarial(texto, esperado):
    assert limpeza.parse_faixa_salarial(texto) == esperado
```

```
pytest tests/test_limpeza.py
29 passed
```

Each line of the list is a test case. When you discover a new case that breaks the code (like the impossible date), you **add a line**, fix the function, and the case never breaks again without someone noticing.

## // Good example × bad example

**Bad example**: storing money as text, or as a decimal, and `A combinar` as zero:

```python
# e se o texto for "A combinar"?
salario = float(texto.replace("R$", "").replace(".", ""))
```

**Good example**: convert to integer cents, and return `None` when there is no value:

```python
minimo, maximo = parse_faixa_salarial(texto)
```

## // Common errors

These messages were obtained by running the code.

| Error | Why it happens | How to fix it |
|---|---|---|
| `float("7.000")` gives `7.0` | In Portuguese the period is the thousands separator, and Python reads it as a decimal point | Remove the periods before converting (`para_centavos`) |
| `ValueError: could not convert string to float: '3.200,50'` | Python does not understand the decimal comma | Swap the comma for a period, after removing the thousands separator |
| `ValueError: day is out of range for month` | A date that does not exist | Wrap the date creation in `try/except` |
| `decimal.InvalidOperation` | You tried to convert empty text, or text without digits, into `Decimal` | Require a digit in the regular expression |
| Odd salary averages | `A combinar` was stored as zero | Use `None` for "not informed" |

## // Guided practice

1. Run `08_demo_limpeza.py` and check each line of output against the table at the start of the module.
2. Copy `limpeza.py` into your project folder.
3. Run `pytest tests/test_limpeza.py` (install `pytest` with `pip install pytest`) and watch the 29 tests pass.
4. **Break it on purpose**: in `para_centavos`, change `* 100` to `* 10`. Run the tests: which ones fail? Then undo it.

## // Practice on your own

> **CHALLENGE**
> Write the `parse_modalidade(texto)` function that returns `remoto`, `hibrido` or `presencial` (lowercase and **without accents**) from `Remoto`, `Híbrido` or `Presencial`, and `None` for anything else. Hint: `unicodedata.normalize("NFD", texto)` separates the letter from the accent, and you can drop the characters in category `Mn`. Also write the tests with `parametrize`: `"Híbrido"` should give `hibrido`, and `"Outra coisa"` should give `None`.

## // Applying it to the week's project

1. In the project folder, put `limpeza.py` and `modelos.py`.
2. Change your `coletar_vagas.py` to clean each job and build a `Vaga` before saving. Print the first 3.
3. Check, in the new `vagas.json`, that the salary is now a number (in cents), not text.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> One day, the site starts writing salaries as `R$ 7 mil a R$ 9,5 mil` ("R$ 7 thousand to R$ 9.5 thousand"). What happens to `parse_faixa_salarial`, and how would you find out?

Answer: the regular expression finds no `R$ 7.000` (the format is different), the function returns `(None, None)` for **every** job, and the program keeps running, without any error. It is the same problem as in Module 06: handling absence avoids crashes, but **hides changes on the site**. You would only find out by counting the empty fields: if 100% of salaries suddenly become `None`, something changed. Module 11 turns that count into an alarm.

## // Module summary

- [ ] I know why the page's text is no good as data, and I convert it to real types.
- [ ] I can store money in integer cents, and I know why not to use `float`.
- [ ] I can use ISO 8601 dates, and I know missing is `None`, not zero.
- [ ] I can write cleaning functions that **never bring down** the program.
- [ ] I can use a dataclass as a template, and I know what the content fingerprint is.
- [ ] I can test the cleaning with `pytest` and `parametrize`.

---

**Next module:** `09-the-second-scraper-events.md`, one source already works. Now the second, reusing what you built.

`Study Material // Coffee & Code`
