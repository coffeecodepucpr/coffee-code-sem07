# Module 10, SQLite: Storing the Data

[Português](../docs/10-sqlite-guardando-os-dados.md) · English

`WEEK 07 // Data & Scraping, Part 1: Collection`

---

## // Before you start

Until now, the collected data lived in memory or in a JSON file, and each run started from scratch. A real pipeline needs to **store** what it collected, and do two things JSON does not do well: **not duplicate** the same job on every run, and **notice what changed** from one day to the next. This module introduces the database that does this, and requires no prior knowledge of SQL.

## // What a database is, and why SQLite

> **DATABASE: IN SIMPLE WORDS**
> It is a program that stores data in **tables** (rows and columns, like a spreadsheet), and that knows how to answer questions about it, with a language called **SQL**. The difference from a spreadsheet: the database **enforces rules** (for example, "there cannot be two jobs with the same id"), and answers queries over thousands of rows in an instant.

**SQLite** is a database that fits in **a single file**, needs no server, and already comes with Python (the `sqlite3` module). That makes it ideal for studying and for small projects. This material was verified with SQLite **3.45.1**. The "upsert" feature we will use requires a recent version (3.24 or later).

## // Minimal SQL

SQL has few commands, and you will use these:

| Command | Does | Example |
|---|---|---|
| `CREATE TABLE` | Creates a table | `CREATE TABLE vagas (...)` |
| `INSERT` | Adds a row | `INSERT INTO vagas VALUES (...)` |
| `SELECT` | Queries | `SELECT titulo FROM vagas WHERE ...` |
| `UPDATE` | Changes existing rows | `UPDATE vagas SET ativa = 0 WHERE ...` |
| `WHERE` | Filters | `WHERE salario_max >= 1000000` |
| `ORDER BY` | Sorts | `ORDER BY salario_max DESC` |
| `GROUP BY` | Groups, and counts | `SELECT modalidade, count(*) ... GROUP BY modalidade` |

The types we use: `TEXT` (text), `INTEGER` (integer). And the **column rules**: `PRIMARY KEY` (identifies the row, and does not repeat), `NOT NULL` (cannot be empty) and `UNIQUE` (cannot repeat).

This script (`10_a_sqlite_basico.py`) shows the whole cycle, in a temporary in-memory database:

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row
conn.execute("""
    CREATE TABLE vagas (
        id_externo TEXT PRIMARY KEY,
        titulo     TEXT NOT NULL,
        modalidade TEXT,
        salario_max INTEGER
    )
""")

dados = [("v1", "Dev Python", "Remoto", 900000),
         ("v2", "Analista de Dados", "Híbrido", 700000),
         ("v3", "DevOps", "Remoto", None)]
conn.executemany("INSERT INTO vagas VALUES (?, ?, ?, ?)", dados)
print("linhas:", conn.execute("SELECT count(*) FROM vagas").fetchone()[0])
```

```
linhas: 3
```

`row_factory = sqlite3.Row` makes each row behave like a dictionary (`linha["titulo"]`). And notice the `?`: they are **parameters**, and the values come separately, in the list. Why that matters is further down.

## // The key that prevents duplicates

The `id_externo` column is the `PRIMARY KEY`. If you try to store a second job with the same id, the database **refuses**:

```
IntegrityError: UNIQUE constraint failed: vagas.id_externo
```

This is a valuable protection: even if your code has a bug, the database does not accept the duplicate. To know that two collections are talking about the **same** job, we need an id that the site itself gives: the `data-id` you saw in Module 02.

## // The upsert: create or update

What if the job already exists, but the salary changed? Refusing is no good: you want to **update**. The command that does "insert, and if it already exists, update" is called **upsert** (from *update* plus *insert*):

```
INSERT INTO vagas VALUES (?, ?, ?, ?)
ON CONFLICT (id_externo) DO UPDATE SET
    titulo = excluded.titulo, salario_max = excluded.salario_max
```

`excluded` refers to the new values you tried to insert. Running it twice, with one existing job and one new one:

```
linhas: 4
v1 agora: {'id_externo': 'v1', 'titulo': 'Dev Python Sênior',
 'modalidade': 'Remoto', 'salario_max': 1200000}
```

(The real output writes the dictionary on a single line.)

Four rows (not five): `v1` was **updated**, and `v4` was **created**.

<div align="center">
<img src="../docs/assets/svg/upsert-sem-duplicar.svg" alt="The database before, today's collection and the database after, with jobs that are unchanged, updated, new and deactivated" width="640">
</div>

## // Knowing what changed: unchanged, updated, new and deactivated

The diagram shows what we want from each collection: for each job, classify it into one of four situations. The question "did it change?" is answered with the **fingerprint** (`conteudo_hash`) from Module 08: we store the content's fingerprint from the last collection, and compare it with the current one.

| Situation | How the pipeline notices | What it does |
|---|---|---|
| **New** | The id does not exist in the database | `INSERT` |
| **Updated** | The id exists, but the fingerprint changed | `UPDATE` on the same row |
| **Unchanged** | The id exists, and the fingerprint is the same | Only updates `visto_em` ("seen at") |
| **Deactivated** | It was active, and **did not appear** in this collection | `ativa = 0`, **without deleting** |

This is the `gravar` ("store") function, from `banco.py`, which does the classification:

```python
def gravar(conn, tabela: str, itens: list, agora: str) -> Contagem:
    """Grava os itens sem duplicar. O nome da tabela é nosso, nunca do usuário."""
    contagem = Contagem()
    for item in itens:
        existente = conn.execute(
            f"SELECT * FROM {tabela} WHERE fonte = ? AND id_externo = ?",
            (item.fonte, item.id_externo),
        ).fetchone()
        for campo in getattr(item, "indisponiveis", ()):
            if existente is not None:   # não deu para ler hoje: mantém o antigo
                setattr(item, campo, existente[campo])
        linha = item.como_linha()
        hash_novo = item.conteudo_hash()
        if existente and existente["conteudo_hash"] == hash_novo:
            conn.execute(
                f"UPDATE {tabela} SET visto_em = ?, ativa = 1 "
                "WHERE fonte = ? AND id_externo = ?",
                (agora, item.fonte, item.id_externo),
            )
            contagem.iguais += 1
            continue
        colunas = ["fonte", "id_externo", *linha, "conteudo_hash",
                   "primeira_vez", "visto_em"]
        valores = [item.fonte, item.id_externo, *linha.values(), hash_novo,
                   agora, agora]
        atualizar = ", ".join(f"{c} = excluded.{c}" for c in
                              [*linha, "conteudo_hash", "visto_em"])
        conn.execute(
            f"INSERT INTO {tabela} ({', '.join(colunas)}) "
            f"VALUES ({', '.join('?' * len(colunas))}) "
            "ON CONFLICT (fonte, id_externo) "
            f"DO UPDATE SET {atualizar}, ativa = 1",
            valores,
        )
        if existente:
            contagem.atualizadas += 1
        else:
            contagem.novas += 1
    return contagem
```

And this is the one that deactivates whatever disappeared:

```python
def inativar_nao_vistas(conn, tabela: str, fonte: str, agora: str) -> int:
    """Marca como inativos os itens que não apareceram na coleta de agora."""
    cursor = conn.execute(
        f"UPDATE {tabela} SET ativa = 0 "
        "WHERE fonte = ? AND ativa = 1 AND visto_em < ?",
        (fonte, agora),
    )
    return cursor.rowcount
```

Two important precautions. **Nothing is deleted**: a job that went offline becomes `ativa = 0`, and stays in the history (and if it comes back, it is reactivated). And **deactivation only happens after a complete collection**: if the collection failed halfway (say, on page 2), the jobs on the following pages "did not appear", but not because they disappeared. The pipeline only calls deactivation when the collection was **complete**. It is incomplete when a list page failed, when the page limit was reached, when pagination went into a **cycle**, and when an item **exists on the site but came broken** (a job without a title, for example): it appeared, and cannot be treated as "gone". Module 12 details each case.

The same care applies to **fields**. In the `gravar` function, notice the loop over `indisponiveis`: if the detail page failed today, the description **is not erased**. The pipeline keeps the last known description, and the job stays "unchanged" if nothing else changed. Without this, a one-minute `503` would turn a good description into an empty one, and the reliable history would degrade without warning.

## // The jobs table schema

This is the real `CREATE TABLE` of the `vagas` table, which the pipeline creates:

```sql
CREATE TABLE IF NOT EXISTS vagas (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    fonte         TEXT NOT NULL,
    id_externo    TEXT NOT NULL,
    titulo        TEXT NOT NULL,
    empresa       TEXT,
    cidade        TEXT,
    uf            TEXT,
    modalidade    TEXT,
    nivel         TEXT,
    salario_min   INTEGER,
    salario_max   INTEGER,
    publicada     TEXT,
    tags          TEXT,
    url           TEXT NOT NULL,
    descricao     TEXT,
    conteudo_hash TEXT NOT NULL,
    ativa         INTEGER NOT NULL DEFAULT 1,
    primeira_vez  TEXT NOT NULL,
    visto_em      TEXT NOT NULL,
    UNIQUE (fonte, id_externo)
);
```

Each decision has a reason:

| Column | Why it exists |
|---|---|
| `id` | An internal number, generated by the database |
| `fonte` and `id_externo` | Who the job is **on the site**. `UNIQUE (fonte, id_externo)` prevents duplicates, and `fonte` ("source") keeps the schema ready for a second site |
| `salario_min`, `salario_max` | In cents, integers (Module 08). `NULL` means "not informed" |
| `tags` | The tags, in comma-separated text |
| `conteudo_hash` | The content's fingerprint, to notice changes |
| `ativa` | `1` while the job appears, `0` after it disappears |
| `primeira_vez`, `visto_em` | When the job first appeared, and when it was last seen |

## // Running it three times

This script (`10_b_gravar_vagas.py`) collects the job list and stores it in a file, classifying each job. Run at three moments (day 1, day 1 again, and then the site's day 2):

```
resultado desta execução: {'nova': 20, 'atualizada': 0, 'igual': 0}
vagas no banco: 20
resultado desta execução: {'nova': 0, 'atualizada': 0, 'igual': 20}
vagas no banco: 20
resultado desta execução: {'nova': 3, 'atualizada': 2, 'igual': 17}
vagas no banco: 23
```

The **second run changed nothing**: 20 "unchanged" jobs, none duplicated. This property has a name: **idempotence** (running it once or ten times gives the same result). On day 2, the 3 new jobs went in, the 2 with changed salaries were updated, and the remaining 17 stayed as they were. (This simplified script does not deactivate the job that disappeared, which is why the total is 23: the complete pipeline, from Module 12, does that.)

## // Transactions: all or nothing

Storing 20 jobs is 20 commands. What if the 12th fails? Without care, the database ends up with 11 jobs, half written. A **transaction** groups commands so they take effect **all together or not at all**. In Python, `with conn:` does this: if something raises an error inside it, everything is undone.

```python
try:
    with conn:
        conn.execute("INSERT INTO t VALUES ('a', 1)")
        conn.execute("INSERT INTO t VALUES ('b', 2)")
        raise RuntimeError("falhou no meio")
except RuntimeError as e:
    print("erro:", e)
print("linhas gravadas:", conn.execute("SELECT count(*) FROM t").fetchone()[0])
```

```
erro: falhou no meio
linhas gravadas: 0
```

Zero rows: both inserts were undone. And the opposite: without `with conn:` (or without calling `conn.commit()`), **nothing is really saved**. In a test, a connection that wrote a row and was closed without `commit` left **0 rows** in the file.

## // Queries that answer questions

The gain of having the data in a database is asking questions. These are real results, on the database the complete pipeline generates (Module 12), after running day 1, day 1 again and day 2:

```sql
SELECT ativa, count(*) FROM vagas GROUP BY ativa;
```
```
[(0, 1), (1, 22)]
```

```sql
SELECT modalidade, count(*) n FROM vagas WHERE ativa = 1
GROUP BY modalidade ORDER BY n DESC, modalidade;
```
```
[('Remoto', 10), ('Híbrido', 6), ('Presencial', 6)]
```

```sql
SELECT titulo, inicio FROM eventos WHERE preco_centavos = 0
ORDER BY inicio LIMIT 3;
```
```
[('Python Day Curitiba', '2026-10-17T14:00'),
 ('Meetup de Dados', '2026-10-22T19:30'),
 ('Hackathon Cidades Inteligentes', '2026-11-07T09:00')]
```

(The last result was broken into lines to fit.) Sorting works **because the dates are ISO**: the text `2026-10-17T14:00` sorts like a date. And notice `NULL`: to find the jobs **without** a salary, you do not use `= NULL`, but `IS NULL`:

```sql
SELECT id_externo, titulo FROM vagas WHERE salario_max IS NULL;
```
```
[('v006', 'DevOps Júnior'), ('v013', 'UX Designer Pleno')]
```

## // Why use ? and never build SQL with an f-string

This is the most classic security error of anyone working with databases, and it exists **even when the data comes from a scraper**, because the text of a page is not trustworthy. See the real result of the same piece of code, written two ways, with a malicious input:

```python
entrada = "x' OR '1'='1"
com_fstring = conn.execute(
    f"SELECT count(*) FROM vagas WHERE titulo = '{entrada}'").fetchone()[0]
com_parametro = conn.execute(
    "SELECT count(*) FROM vagas WHERE titulo = ?", (entrada,)).fetchone()[0]
```

```
f-string  achou: 4 linhas (a entrada virou parte do SQL)
parâmetro achou: 0 linhas
```

With the f-string, the input text **became part of the command** and made the condition true for every row. With the `?` parameter, the database treats the input as **a value**, never as a command. The rule: **values always go by parameter** (the `?`). (Only the table name, which is a constant in your code, may go in an f-string, as the `gravar` function does.)

## // Good example × bad example

**Bad example**: storing without caring about duplicates, and building SQL with an f-string:

```python
conn.execute(f"INSERT INTO vagas VALUES ('{id}', '{titulo}')")
```

**Good example**: unique key, upsert, parameters and a transaction:

```python
with conn:
    conn.execute("INSERT ... ON CONFLICT (...) DO UPDATE SET ...", valores)
```

## // Common errors

These messages were obtained by running the code.

| Error | Why it happens | How to fix it |
|---|---|---|
| `IntegrityError: UNIQUE constraint failed: vagas.id_externo` | You tried to store an id that already exists | Use the upsert (`ON CONFLICT ... DO UPDATE`) |
| `IntegrityError: NOT NULL constraint failed: t.a` | A value is missing in a required column | Validate before storing (Module 08) |
| `OperationalError: no such table: nao_existe` | The table was not created, or the name is wrong | Run the `CREATE TABLE`, and check the database file name |
| `ProgrammingError: Incorrect number of bindings supplied. The current statement uses 2, and there are 1 supplied.` | There are more `?` than values (or the other way round) | Count the `?` and the values |
| The data "disappears" when reopening the database | The `commit` is missing | Use `with conn:` around the writes |
| A job disappears from the database when it leaves the site | The code deleted what it did not see | Mark `ativa = 0`, do not delete |

## // Guided practice

1. Run `10_a_sqlite_basico.py` and read each output next to the code.
2. Run `10_b_gravar_vagas.py` **twice** (with Mural Tech on day 1) and confirm the second run changes nothing.
3. Switch the site to day 2 (`/_dev/dia/2`) and run it again. Check the 3 new and the 2 updated jobs.
4. Open the `vagas_demo.db` file with a database tool (for example, the `sqlite3` program, if you have it) and run a `SELECT`.

## // Practice on your own

> **CHALLENGE**
> With the `10_b_gravar_vagas.py` database run on day 1 (20 jobs), write a query that counts the jobs with a **maximum salary of at least R$ 10,000**. Remember: the database stores cents, so the value is `1000000`. Expected result: **7 jobs** (`v003`, `v005`, `v008`, `v011`, `v012`, `v016` and `v017`).

## // Applying it to the week's project

1. In the project folder, create `banco.py`, with `ESQUEMA`, `abrir()`, `gravar()` and `inativar_nao_vistas()`.
2. Change `coletar_vagas.py` to store in the database instead of JSON.
3. Run it twice and check that the number of rows does not change.
4. Put `dados/` in `.gitignore`: the database is output, not code.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> A collection fails on page 2 of 3 (the site went down for a minute). The jobs on pages 2 and 3 were not seen. If the pipeline deactivates "everything that did not appear", what happens, and how does the pipeline avoid it?

Answer: the 12 jobs on pages 2 and 3 would be **marked inactive by mistake**, and the database would start saying they went offline, when they simply were not read. The pipeline avoids this by only deactivating after a **complete** collection: the collector sets `completo = False` when a list page fails, and the orchestrator skips deactivation in that case. There is an automated test for this (Module 12).

## // Module summary

- [ ] I know what a database is, and why SQLite works for this week.
- [ ] I can create tables with `PRIMARY KEY`, `NOT NULL` and `UNIQUE`.
- [ ] I can use the upsert to create or update without duplicating.
- [ ] I can classify a job as new, updated, unchanged or deactivated, by its fingerprint.
- [ ] I can use transactions (`with conn:`) to store all or nothing.
- [ ] I can write queries with `WHERE`, `ORDER BY` and `GROUP BY`, and use `IS NULL`.
- [ ] I know values always go by `?`, never by f-string.

---

**Next module:** `11-robustness-and-good-manners.md`, the data already has a home. Now, make the collection stand up to the real world.

`Study Material // Coffee & Code`
