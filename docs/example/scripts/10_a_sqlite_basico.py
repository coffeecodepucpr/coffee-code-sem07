"""SQLite: criar, gravar, consultar e não duplicar."""
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

for linha in conn.execute("SELECT * FROM vagas ORDER BY titulo"):
    print(dict(linha))

print("--- a chave primária recusa a duplicata")
try:
    conn.execute("INSERT INTO vagas VALUES ('v1', 'Outra', 'Remoto', 1)")
except sqlite3.IntegrityError as erro:
    print("IntegrityError:", erro)

print("--- o upsert: cria ou atualiza, sem duplicar")
sql = """
    INSERT INTO vagas VALUES (?, ?, ?, ?)
    ON CONFLICT (id_externo) DO UPDATE SET
        titulo = excluded.titulo, salario_max = excluded.salario_max
"""
conn.execute(sql, ("v1", "Dev Python Sênior", "Remoto", 1200000))
conn.execute(sql, ("v4", "QA", "Remoto", 500000))
print("linhas:", conn.execute("SELECT count(*) FROM vagas").fetchone()[0])
print("v1 agora:", dict(conn.execute("SELECT * FROM vagas WHERE id_externo='v1'").fetchone()))

print("--- consultas que respondem perguntas")
sql = "SELECT modalidade, count(*) AS n FROM vagas GROUP BY modalidade ORDER BY n DESC"
print([tuple(l) for l in conn.execute(sql)])
sql = "SELECT titulo FROM vagas WHERE salario_max >= ? ORDER BY salario_max DESC"
print([l[0] for l in conn.execute(sql, (700000,))])
print("sem salário:", [l[0] for l in conn.execute("SELECT titulo FROM vagas WHERE salario_max IS NULL")])

print("--- por que usar ? e nunca f-string")
entrada = "x' OR '1'='1"
com_fstring = conn.execute(f"SELECT count(*) FROM vagas WHERE titulo = '{entrada}'").fetchone()[0]
com_parametro = conn.execute("SELECT count(*) FROM vagas WHERE titulo = ?", (entrada,)).fetchone()[0]
print("f-string  achou:", com_fstring, "linhas (a entrada virou parte do SQL)")
print("parâmetro achou:", com_parametro, "linhas")
