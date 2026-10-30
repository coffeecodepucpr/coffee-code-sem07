# Module 04, Essential Python for Collection

[Português](../docs/04-python-essencial-para-coleta.md) · English

`WEEK 07 // Data & Scraping, Part 1: Collection`

---

## // Before you start

This module prepares the ground: the environment where your code will run, and the slice of Python that collection uses. It does not try to teach the whole language, only the **essentials** to read and write this week's scripts. If you already program in Python, you can skim it and do only the virtual environment part.

## // Checking Python

Open a terminal and check the version:

```
python3 --version
```

```
Python 3.12.3
```

This material requires **Python 3.10 or higher** (the code uses constructs such as `str | None`, which arrived in that version). On some systems, the command is called `python`, not `python3`. On Windows, installation and the activation commands follow different conventions, and **they were not tested** while producing this material: check the Python documentation for your system.

## // The virtual environment

Each project should have its own set of libraries, separate from the rest of the computer. A **virtual environment** is a folder with an isolated copy of Python and of the libraries installed only for that project. It avoids two problems: one project breaking another, and your code working on your machine and failing on someone else's.

The reason is real, and it came up while preparing this material. On the computer used for production, the system Python had `requests` at version **2.33.1**, and the project's virtual environment had **2.34.2**. Two different versions of the same library, on the same computer, with no error at all.

To create and activate it (Linux and macOS):

```
python3 -m venv .venv
source .venv/bin/activate
```

After activation, the terminal usually shows `(.venv)` at the start of the line. To install the week's libraries, from a `requirements.txt` file:

```
requests>=2.34,<3
beautifulsoup4>=4.15,<5
lxml>=6.1,<7
```

```
pip install -r requirements.txt
pip list
```

```
beautifulsoup4     4.15.0
lxml               6.1.3
requests           2.34.2
```

(The `pip list` output also shows other packages, which were omitted.) To leave the environment, run `deactivate`. On Windows, activation is done by a file inside `.venv\Scripts`, and that path was not tested here.

> **WHAT DOES NOT GO INTO THE REPOSITORY**
> If you version the project with Git, create a `.gitignore` file and put `.venv/`, `dados/` and `logs/` in it. The virtual environment is recreated from `requirements.txt`, and the database and the logs are the output of running, not code.

## // The Python that collection uses

This is a quick tour, with the real output of each excerpt (the file is `04_a_tour.py`).

**Variables, text and f-strings.** An f-string, written with `f` before the quotes, inserts values into text:

```python
cidade = "Curitiba"
vagas = 20
print(f"{vagas} vagas em {cidade}")
```

```
20 vagas em Curitiba
```

**Lists and dictionaries.** A list holds items in order; a dictionary holds key and value pairs. It is the format of each job you extract:

```python
tags = ["python", "sql", "docker"]
tags.append("git")
vaga = {"titulo": "Dev Python", "empresa": "Orbita", "tags": tags}
print(vaga["titulo"], "|", vaga.get("salario"))
print("com valor padrão:", vaga.get("salario", "sem salário"))
```

```
Dev Python | None
com valor padrão: sem salário
```

Notice `vaga.get("salario")`: with `.get`, a missing key returns `None` (or a default value), instead of an error. You will use this a lot.

**Loops, conditions and list comprehensions.** A comprehension is a short way to build a list from another:

```python
for tag in tags:
    if tag.startswith("p"):
        print("começa com p:", tag)
maiusculas = [t.upper() for t in tags if len(t) > 3]
print(maiusculas)
```

```
começa com p: python
['PYTHON', 'DOCKER']
```

**Functions.** They group a piece of code under a name, and that is how your scraper will be organized:

```python
def resumo(vaga):
    return f"{vaga['titulo']} ({len(vaga['tags'])} tags)"

print(resumo(vaga))
```

```
Dev Python (4 tags)
```

**Errors and try/except.** When something goes wrong, Python raises an error. With `try/except`, you decide what to do:

```python
try:
    print(int("R$ 5"))
except ValueError as erro:
    print("ValueError:", erro)
```

```
ValueError: invalid literal for int() with base 10: 'R$ 5'
```

**Files and JSON.** JSON is a text format for storing lists and dictionaries. `with open(...)` opens a file and closes it on its own at the end:

```python
with open("exemplo.json", "w", encoding="utf-8") as arquivo:
    json.dump([vaga], arquivo, ensure_ascii=False, indent=2)
with open("exemplo.json", encoding="utf-8") as arquivo:
    lidas = json.load(arquivo)
print("lidas do arquivo:", lidas[0]["titulo"], "| tipo:", type(lidas).__name__)
```

```
lidas do arquivo: Dev Python | tipo: list
```

Always write `encoding="utf-8"` when opening text files: without it, accents may be written and read differently on each system.

**Dataclasses.** A template for your data, with named fields:

```python
@dataclass
class Vaga:
    titulo: str
    empresa: str | None = None

print(Vaga("QA"))
print(Vaga("Dev", "Orbita"))
```

```
Vaga(titulo='QA', empresa=None)
Vaga(titulo='Dev', empresa='Orbita')
```

## // Running scripts and importing your own

A script is a `.py` file, and it runs with `python3 name.py`. When a file grows, you move functions into other files and **import** them. In Module 06, you will create `parsers.py`, and a script uses it like this:

```python
from parsers import ler_cartao_vaga
```

Python looks for `parsers.py` in the same folder as the script you are running, which is why the project files stay together.

## // Good example × bad example

**Bad example**: one giant file, with everything loose, that nobody can test or reuse:

```python
r = requests.get("http://127.0.0.1:8080/vagas/")
s = BeautifulSoup(r.content, "lxml")
for c in s.select("article.vaga"):
    print(c.select_one("h2 a").get_text())
```

**Good example**: small functions with clear names, each doing one thing:

```python
def baixar(url):
    ...

def ler_vagas(sopa):
    ...
```

This week's pipeline is exactly that, on a bigger scale: **each file and each function, one reason to change** (Module 14).

## // Common errors

These messages were obtained by running the code.

| Error | Why it happens | How to fix it |
|---|---|---|
| `ModuleNotFoundError: No module named '...'` | The library is not installed in the environment you are using | Activate the virtual environment and run `pip install -r requirements.txt` |
| `KeyError: 'salario'` | You asked for `vaga["salario"]` and the key does not exist | Use `vaga.get("salario")` |
| `IndentationError: expected an indented block after 'if' statement on line 1` | The body of the `if` is not indented | Indent the block (always use 4 spaces) |
| `TypeError: can only concatenate str (not "int") to str` | You mixed text and a number with `+` | Use an f-string: `f"{texto}{numero}"` |
| `IndexError: list index out of range` | You asked for an item the list does not have | Check the size with `len(lista)` |
| `ValueError: invalid literal for int()...` | You tried to convert text that is not a number | Clean the text first (Module 08), or use `try/except` |

## // Guided practice

1. Create the `projeto-coleta/` folder, go into it, create the virtual environment and activate it.
2. Create `requirements.txt` with the three lines above and run `pip install -r requirements.txt`.
3. Run `pip list` and check the versions.
4. Run `04_a_tour.py` and read each line of output next to the code.
5. Create `.gitignore` with `.venv/`, `dados/` and `logs/`.

## // Practice on your own

> **CHALLENGE**
> Write a script with a list of three job dictionaries (`titulo`, `modalidade`, `salario_max`, one of them without `salario_max`). Write a loop that prints each job's title and salary, or the text `sem salário` ("no salary") when it is missing. Then use a list comprehension to build only the titles of the `Remoto` (remote) jobs. Use `vaga.get(...)`, not `vaga[...]`, for the field that may be missing.

## // Applying it to the week's project

1. Make sure the virtual environment is active every time you open a new terminal in the project.
2. Keep the scripts of the next modules in the same folder, next to `parsers.py`, so the imports work.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> Your code works on your computer, but raises `ModuleNotFoundError` when someone else runs it on theirs. What is the most likely cause, and how do the virtual environment and `requirements.txt` prevent it?

Answer: the two computers have different libraries installed (or different versions). `requirements.txt` **lists** what the project needs, and the virtual environment **isolates** the project: on any machine, whoever creates the environment and runs `pip install -r requirements.txt` ends up with the same set, without depending on what was already installed.

## // Module summary

- [ ] I can check the Python version and I know I need 3.10 or higher.
- [ ] I can create, activate and use a virtual environment, and install from `requirements.txt`.
- [ ] I can use variables, f-strings, lists, dictionaries, loops and functions.
- [ ] I can use `.get`, `try/except` and `with open(..., encoding="utf-8")`.
- [ ] I know a dataclass is a template for data.
- [ ] I can recognize the most common beginner errors.

---

**Next module:** `05-requests-downloading-pages.md`, with the environment ready, let us download the first page, carefully and with limits.

`Study Material // Coffee & Code`
