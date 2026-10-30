"""Quando o elemento não existe: o erro mais comum de quem começa."""
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

link = cartao.select_one("h2 a")["href"]
print("link relativo:", link)
print("link absoluto:", urljoin("http://127.0.0.1:8080/vagas/", link))
print("paginação relativa:", urljoin("http://127.0.0.1:8080/vagas/", "?pagina=2"))
print("prettify do cartão:")
print(cartao.prettify())
