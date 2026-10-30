"""Um passeio pelo Python que a coleta usa."""
import json
from dataclasses import dataclass

# variáveis, textos e f-strings
cidade = "Curitiba"
vagas = 20
print(f"{vagas} vagas em {cidade}")

# listas e dicionários
tags = ["python", "sql", "docker"]
tags.append("git")
vaga = {"titulo": "Dev Python", "empresa": "Orbita", "tags": tags}
print(vaga["titulo"], "|", vaga.get("salario"))
print("com valor padrão:", vaga.get("salario", "sem salário"))

# laços, condições e compreensões de lista
for tag in tags:
    if tag.startswith("p"):
        print("começa com p:", tag)
maiusculas = [t.upper() for t in tags if len(t) > 3]
print(maiusculas)

# funções
def resumo(vaga):
    return f"{vaga['titulo']} ({len(vaga['tags'])} tags)"

print(resumo(vaga))

# erros e try/except
try:
    print(int("R$ 5"))
except ValueError as erro:
    print("ValueError:", erro)

# arquivos e JSON
with open("exemplo.json", "w", encoding="utf-8") as arquivo:
    json.dump([vaga], arquivo, ensure_ascii=False, indent=2)
with open("exemplo.json", encoding="utf-8") as arquivo:
    lidas = json.load(arquivo)
print("lidas do arquivo:", lidas[0]["titulo"], "| tipo:", type(lidas).__name__)

# dataclass: um molde para os dados
@dataclass
class Vaga:
    titulo: str
    empresa: str | None = None

print(Vaga("QA"))
print(Vaga("Dev", "Orbita"))
