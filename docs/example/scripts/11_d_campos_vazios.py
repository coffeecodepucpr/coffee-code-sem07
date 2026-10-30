"""Um alarme para quando o site muda e os campos começam a vir vazios."""
import requests
from bs4 import BeautifulSoup

BASE = "http://127.0.0.1:8080"
LIMITE = 0.30        # mais de 30% de campos vazios acende o alarme


def texto(tag):
    return tag.get_text(strip=True) if tag is not None else None


def coletar(seletor_salario):
    sopa = BeautifulSoup(requests.get(f"{BASE}/vagas/", timeout=10).content, "lxml")
    return [{"titulo": texto(c.select_one("h2.titulo a")),
             "salario": texto(c.select_one(seletor_salario))}
            for c in sopa.select("article.vaga")]


def conferir(vagas, campo):
    vazios = sum(1 for v in vagas if not v[campo])
    proporcao = vazios / len(vagas)
    estado = "ALARME" if proporcao > LIMITE else "ok"
    print(f"{campo}: {vazios} de {len(vagas)} vazios ({proporcao:.0%}) "
          f"-> {estado}")


print("seletor certo (.salario):")
conferir(coletar(".salario"), "salario")
print("o site mudou o nome da classe para .remuneracao, e o seletor ficou velho:")
conferir(coletar(".remuneracao"), "salario")
