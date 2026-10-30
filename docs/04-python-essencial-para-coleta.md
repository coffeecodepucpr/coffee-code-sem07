# Módulo 04, Python Essencial para Coleta

Português · [English](../docs-eng/04-essential-python-for-collection.md)

`SEM 07 // Data & Scraping, Parte 1: Coleta`

---

## // Antes de começar

Este módulo prepara o terreno: o ambiente onde o seu código vai rodar, e o pedaço de Python que a coleta usa. Ele não pretende ensinar a linguagem inteira, e sim o **essencial** para ler e escrever os scripts desta semana. Quem já programa em Python pode percorrê-lo rapidamente e fazer só a parte do ambiente virtual.

## // Conferindo o Python

Abra um terminal e confira a versão:

```
python3 --version
```

```
Python 3.12.3
```

Este material pede **Python 3.10 ou superior** (o código usa construções como `str | None`, que chegaram nessa versão). Em alguns sistemas, o comando se chama `python`, e não `python3`. No Windows, a instalação e os comandos de ativação seguem convenções diferentes, e **não foram testados** na produção deste material: consulte a documentação do Python para o seu sistema.

## // O ambiente virtual

Cada projeto deve ter o seu próprio conjunto de bibliotecas, separado do resto do computador. Um **ambiente virtual** é uma pasta com uma cópia isolada do Python e das bibliotecas instaladas só para aquele projeto. Isso evita dois problemas: um projeto quebrar o outro, e o seu código funcionar na sua máquina e falhar na de outra pessoa.

A razão é real, e apareceu na preparação deste material. No computador usado para a produção, o Python do sistema tinha o `requests` na versão **2.33.1**, e o ambiente virtual do projeto, na **2.34.2**. Duas versões diferentes da mesma biblioteca, no mesmo computador, sem nenhum erro.

Para criar e ativar (Linux e macOS):

```
python3 -m venv .venv
source .venv/bin/activate
```

Depois da ativação, o terminal costuma mostrar `(.venv)` no começo da linha. Para instalar as bibliotecas da semana, a partir de um arquivo `requirements.txt`:

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

(A saída do `pip list` mostra também outros pacotes, que foram omitidos.) Para sair do ambiente, rode `deactivate`. No Windows, a ativação é feita por um arquivo dentro de `.venv\Scripts`, e esse caminho não foi testado aqui.

> **O QUE NÃO VAI PARA O REPOSITÓRIO**
> Se você versiona o projeto com Git, crie um arquivo `.gitignore` e coloque nele `.venv/`, `dados/` e `logs/`. O ambiente virtual se recria a partir do `requirements.txt`, e o banco e os logs são resultado da execução, e não código.

## // O Python que a coleta usa

Este é um passeio rápido, com a saída real de cada trecho (o arquivo é `04_a_tour.py`).

**Variáveis, textos e f-strings.** Uma f-string, escrita com `f` antes das aspas, insere valores no texto:

```python
cidade = "Curitiba"
vagas = 20
print(f"{vagas} vagas em {cidade}")
```

```
20 vagas em Curitiba
```

**Listas e dicionários.** A lista guarda itens em ordem; o dicionário guarda pares chave e valor. É o formato de cada vaga que você extrai:

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

Repare em `vaga.get("salario")`: com `.get`, uma chave ausente devolve `None` (ou um valor padrão), em vez de um erro. Você usará muito isso.

**Laços, condições e compreensões de lista.** A compreensão é uma forma curta de montar uma lista a partir de outra:

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

**Funções.** Agrupam um trecho de código sob um nome, e é como o seu scraper vai ser organizado:

```python
def resumo(vaga):
    return f"{vaga['titulo']} ({len(vaga['tags'])} tags)"

print(resumo(vaga))
```

```
Dev Python (4 tags)
```

**Erros e try/except.** Quando algo dá errado, o Python levanta um erro. Com `try/except`, você decide o que fazer:

```python
try:
    print(int("R$ 5"))
except ValueError as erro:
    print("ValueError:", erro)
```

```
ValueError: invalid literal for int() with base 10: 'R$ 5'
```

**Arquivos e JSON.** O JSON é um formato de texto para guardar listas e dicionários. O `with open(...)` abre um arquivo e o fecha sozinho no fim:

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

Sempre escreva `encoding="utf-8"` ao abrir arquivos de texto: sem isso, os acentos podem ser gravados e lidos de forma diferente em cada sistema.

**Dataclasses.** Um molde para os seus dados, com campos nomeados:

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

## // Rodando scripts e importando os seus

Um script é um arquivo `.py`, e se roda com `python3 nome.py`. Quando um arquivo cresce, você separa as funções em outros arquivos e as **importa**. No Módulo 06, você criou o `parsers.py`, e um script o usa assim:

```python
from parsers import ler_cartao_vaga
```

O Python procura o `parsers.py` na mesma pasta do script que você está rodando, por isso os arquivos do projeto ficam juntos.

## // Bom exemplo × mau exemplo

**Mau exemplo**: um arquivo gigante, com tudo solto, que ninguém consegue testar nem reaproveitar:

```python
r = requests.get("http://127.0.0.1:8080/vagas/")
s = BeautifulSoup(r.content, "lxml")
for c in s.select("article.vaga"):
    print(c.select_one("h2 a").get_text())
```

**Bom exemplo**: pequenas funções com nomes claros, cada uma fazendo uma coisa:

```python
def baixar(url):
    ...

def ler_vagas(sopa):
    ...
```

O pipeline desta semana é isso, em escala maior: **cada arquivo e cada função, um motivo para mudar** (Módulo 14).

## // Erros comuns

Estas mensagens foram obtidas ao executar o código.

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| `ModuleNotFoundError: No module named '...'` | A biblioteca não está instalada no ambiente que você está usando | Ative o ambiente virtual e rode `pip install -r requirements.txt` |
| `KeyError: 'salario'` | Pediu `vaga["salario"]` e a chave não existe | Use `vaga.get("salario")` |
| `IndentationError: expected an indented block after 'if' statement on line 1` | O corpo do `if` não está recuado | Recue o bloco (use 4 espaços, sempre) |
| `TypeError: can only concatenate str (not "int") to str` | Misturou texto e número com `+` | Use uma f-string: `f"{texto}{numero}"` |
| `IndexError: list index out of range` | Pediu um item que a lista não tem | Confira o tamanho com `len(lista)` |
| `ValueError: invalid literal for int()...` | Tentou converter um texto que não é número | Limpe o texto antes (Módulo 08), ou use `try/except` |

## // Prática guiada

1. Crie a pasta `projeto-coleta/`, entre nela, crie o ambiente virtual e ative-o.
2. Crie o `requirements.txt` com as três linhas acima e rode `pip install -r requirements.txt`.
3. Rode `pip list` e confira as versões.
4. Rode `04_a_tour.py` e leia cada linha da saída ao lado do código.
5. Crie o `.gitignore` com `.venv/`, `dados/` e `logs/`.

## // Pratique sozinho

> **DESAFIO**
> Escreva um script com uma lista de três dicionários de vagas (`titulo`, `modalidade`, `salario_max`, sendo um deles sem `salario_max`). Faça um laço que imprima o título de cada vaga e o salário, ou o texto `sem salário` quando faltar. Depois, use uma compreensão de lista para montar só os títulos das vagas `Remoto`. Use `vaga.get(...)`, e não `vaga[...]`, para o campo que pode faltar.

## // Aplicando no projeto da semana

1. Confirme que o ambiente virtual está ativo toda vez que abrir um terminal novo no projeto.
2. Guarde os scripts dos próximos módulos na mesma pasta, junto do `parsers.py`, para que as importações funcionem.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> O seu código funciona no seu computador, mas dá `ModuleNotFoundError` quando outra pessoa o roda no dela. Qual é a causa mais provável, e como o ambiente virtual e o `requirements.txt` evitam isso?

Resposta: os dois computadores têm bibliotecas diferentes instaladas (ou versões diferentes). O `requirements.txt` **lista** o que o projeto precisa, e o ambiente virtual **isola** o projeto: em qualquer máquina, quem cria o ambiente e roda `pip install -r requirements.txt` fica com o mesmo conjunto, sem depender do que já estava instalado.

## // Resumo do módulo

- [ ] Sei conferir a versão do Python e que preciso da 3.10 ou superior.
- [ ] Sei criar, ativar e usar um ambiente virtual, e instalar do `requirements.txt`.
- [ ] Sei usar variáveis, f-strings, listas, dicionários, laços e funções.
- [ ] Sei usar `.get`, `try/except` e `with open(..., encoding="utf-8")`.
- [ ] Sei que um dataclass é um molde para os dados.
- [ ] Sei reconhecer os erros mais comuns de quem começa.

---

**Próximo módulo:** `05-requests-baixando-paginas.md`, com o ambiente pronto, vamos baixar a primeira página, com cuidado e com limites.

`Material de Estudo // Coffee & Code`
