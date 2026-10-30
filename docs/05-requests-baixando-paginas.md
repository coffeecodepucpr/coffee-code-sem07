# Módulo 05, requests: Baixando Páginas

Português · [English](../docs-eng/05-requests-downloading-pages.md)

`SEM 07 // Data & Scraping, Parte 1: Coleta`

---

## // Antes de começar

O primeiro passo de qualquer coleta é **baixar a página**. Este módulo apresenta o `requests`, a biblioteca que faz isso, e dedica mais espaço ao que pode dar errado do que ao que dá certo, porque é nos erros que um scraper amador se separa de um confiável. Use o Mural Tech ligado, como em todos os módulos.

## // O que é o requests

> **REQUESTS: EM PALAVRAS SIMPLES**
> É uma biblioteca do Python que faz pedidos HTTP: você diz o endereço, e ela devolve um objeto com a resposta (status, cabeçalhos e corpo). É o "navegador" do seu programa, sem janela e sem executar JavaScript.

Instale-a no ambiente virtual do projeto (`pip install requests`). Este material foi verificado com a versão **2.34.2**.

## // O primeiro pedido

Este script (`05_a_primeiro_pedido.py`) faz um pedido e examina a resposta:

```python
import requests

BASE = "http://127.0.0.1:8080"

resposta = requests.get(f"{BASE}/vagas/", timeout=10)
print("status:", resposta.status_code, "| ok:", resposta.ok)
print("url final:", resposta.url)
print("content-type:", resposta.headers["Content-Type"])
print("etag:", resposta.headers["ETag"])
print("tamanho em bytes:", len(resposta.content))
print("tipo de .content:", type(resposta.content).__name__)
print("tipo de .text:", type(resposta.text).__name__)
print("encoding:", resposta.encoding)
```

```
status: 200 | ok: True
url final: http://127.0.0.1:8080/vagas/
content-type: text/html; charset=utf-8
etag: "d3aa7cdebab346b2"
tamanho em bytes: 4122
tipo de .content: bytes
tipo de .text: str
encoding: utf-8
```

| O que você usa | O que é |
|---|---|
| `resposta.status_code` | O código de status (`200`, `404`...) |
| `resposta.ok` | `True` para qualquer status abaixo de 400 |
| `resposta.headers` | Os cabeçalhos, em um dicionário que ignora maiúsculas |
| `resposta.content` | O corpo em **bytes**, como chegou |
| `resposta.text` | O corpo como **texto**, decodificado pelo `requests` |
| `resposta.encoding` | A codificação que o `requests` usou para decodificar |
| `resposta.url` | O endereço final (depois de redirecionamentos) |
| `resposta.elapsed` | O tempo que a resposta levou |

## // Parâmetros e redirecionamentos

Para montar uma consulta (`?pagina=2`), passe um dicionário em `params`, e o `requests` cuida da formatação:

```python
com_params = requests.get(f"{BASE}/vagas/", params={"pagina": 2}, timeout=10)
print(com_params.url)
```

```
http://127.0.0.1:8080/vagas/?pagina=2
```

Alguns endereços mudaram de lugar: o servidor responde `301` e diz para onde ir. O `requests` **segue esses redirecionamentos sozinho**, e guarda o caminho em `resposta.history`:

```python
antigo = requests.get(f"{BASE}/antigo/vagas", timeout=10)
print("status final:", antigo.status_code, "| url final:", antigo.url)
caminho = [(r.status_code, r.headers["Location"]) for r in antigo.history]
print("histórico:", caminho)
sem_seguir = requests.get(f"{BASE}/antigo/vagas", allow_redirects=False,
                          timeout=10)
print("sem seguir:", sem_seguir.status_code, sem_seguir.headers["Location"])
```

```
status final: 200 | url final: http://127.0.0.1:8080/vagas/
histórico: [(301, '/vagas/')]
sem seguir: 301 /vagas/
```

## // A armadilha da codificação

Este é um erro que atinge **quem escreve em português**. O Mural Tech tem uma página que **não declara a codificação** (`/legado/vagas`): o cabeçalho diz só `text/html`, sem o `charset`. Sem essa informação, o `requests` faz uma suposição, e erra:

```python
certa = requests.get(f"{BASE}/vagas/", timeout=10)
legado = requests.get(f"{BASE}/legado/vagas", timeout=10)
print("cabeçalho da página certa :", certa.headers["Content-Type"])
print("cabeçalho da página legado:", legado.headers["Content-Type"])
print("encoding que o requests supôs:", legado.encoding)
```

```
cabeçalho da página certa : text/html; charset=utf-8
cabeçalho da página legado: text/html
encoding que o requests supôs: ISO-8859-1
```

O resultado, ao ler a mesma frase das duas páginas:

```
certa  .text -> 'Página 1 de 3<' | BeautifulSoup(.content) -> 'Página 1 de 3'
legado .text -> 'PÃ¡gina 1 de 3' | BeautifulSoup(.content) -> 'Página 1 de 3'
```

Na página sem `charset`, o `resposta.text` virou **PÃ¡gina**, porque o `requests` decodificou como `ISO-8859-1`. Já entregar os **bytes** (`resposta.content`) ao BeautifulSoup deu o resultado certo: ele examina o próprio documento para descobrir a codificação. Por isso, nesta semana, **entregamos os bytes ao BeautifulSoup** (`resposta.content`), e não o texto (`resposta.text`).

## // O tempo limite: o erro que trava programas

Se você não disser quanto esperar, o `requests` **espera o tempo que o servidor quiser**. O Mural Tech tem uma página que demora 3 segundos (`/lento`). Este script (`05_c_erros_e_timeout.py`) mede:

```python
inicio = time.perf_counter()
requests.get(f"{BASE}/lento")
print(f"esperou {time.perf_counter() - inicio:.1f} s")

inicio = time.perf_counter()
try:
    requests.get(f"{BASE}/lento", timeout=1)
except requests.exceptions.ReadTimeout as erro:
    print(f"ReadTimeout depois de {time.perf_counter() - inicio:.1f} s")
    print("é um Timeout?", isinstance(erro, requests.exceptions.Timeout))
```

```
esperou 3.0 s
ReadTimeout depois de 1.0 s
é um Timeout? True
```

Três segundos parecem pouco, mas um servidor que **trava de verdade** deixaria o programa esperando para sempre, e é assim que um scraper agendado (Módulo 13) "some" no meio da madrugada. A regra: **todo pedido leva um timeout**. Ele aceita um número (segundos) ou um par `(conexão, leitura)`, como `(3.05, 10)`: até 3,05 s para conseguir conectar, e até 10 s para o servidor responder. É o que o pipeline usa.

## // Quando o pedido dá errado

Dois tipos de problema, que se tratam de formas diferentes:

**O pedido nem chegou ao servidor** (o site está fora do ar, a rede caiu): o `requests` levanta uma exceção.

```python
try:
    requests.get("http://127.0.0.1:9/", timeout=3)
except requests.exceptions.ConnectionError as erro:
    print("ConnectionError:", type(erro.args[0]).__name__)
```

```
ConnectionError: MaxRetryError
```

(O `requests` embrulha o erro de baixo nível, e o `MaxRetryError` é o nome do embrulho. Dentro dele está a causa: no Linux, "Connection refused".)

**O pedido chegou, mas a resposta é de erro** (`404`, `500`...): **não há exceção**, e o programa segue como se nada tivesse acontecido, a não ser que você pergunte. Para isso existe o `raise_for_status()`, que levanta um erro se o status for `4xx` ou `5xx`:

```python
resposta = requests.get(f"{BASE}/vagas/v999", timeout=10)
print("status:", resposta.status_code, "| ok:", resposta.ok)
try:
    resposta.raise_for_status()
except requests.exceptions.HTTPError as erro:
    print("HTTPError:", erro)
```

```
status: 404 | ok: False
HTTPError: 404 Client Error: Not Found for url: http://127.0.0.1:8080/vagas/v999
```

| Situação | O que o `requests` faz |
|---|---|
| O site não responde, ou a rede falha | Levanta `ConnectionError` |
| O servidor demora mais que o `timeout` | Levanta `Timeout` (`ReadTimeout`, ou `ConnectTimeout` na conexão) |
| O servidor responde `404`, `500`... | **Nada.** Você chama `raise_for_status()` para virar `HTTPError` |

## // A sessão e o User-Agent

Cada `requests.get(...)` solto abre uma conexão nova. Uma **sessão** reaproveita a conexão e repete os mesmos cabeçalhos em todos os pedidos, e é o lugar certo para o seu `User-Agent` (lembra do Módulo 03?). O script `05_d_sessao_e_user_agent.py` pergunta ao `/eco` o que o servidor recebeu:

```python
padrao = requests.get(f"{BASE}/eco", timeout=10).json()
print("User-Agent padrão:", padrao["user-agent"])

USER_AGENT = "MuralColetaBot/1.0 (projeto de estudo; contato: voce@example.com)"
sessao = requests.Session()
sessao.headers["User-Agent"] = USER_AGENT

for numero in (1, 2):
    eco = sessao.get(f"{BASE}/eco", timeout=10).json()
    print(f"pedido {numero} pela sessão:", eco["user-agent"])
print("a sessão reaproveita a conexão:", eco["connection"])
```

```
User-Agent padrão: python-requests/2.34.2
pedido 1 pela sessão: MuralColetaBot/1.0
 (projeto de estudo; contato: voce@example.com)
pedido 2 pela sessão: MuralColetaBot/1.0
 (projeto de estudo; contato: voce@example.com)
a sessão reaproveita a conexão: keep-alive
```

(A saída real escreve cada `User-Agent` em uma linha só.)

## // Bom exemplo × mau exemplo

**Mau exemplo**: sem `timeout`, sem checar o status, e lendo `.text` às cegas:

```python
html = requests.get(url).text
```

**Bom exemplo**: uma função que concentra os cuidados, e que você reutiliza em todo o projeto:

```python
def baixar(sessao, url):
    resposta = sessao.get(url, timeout=(3.05, 10))
    resposta.raise_for_status()
    return resposta
```

## // Erros comuns

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| O programa trava e não termina | Faltou o `timeout` | Passe `timeout=` em **todo** pedido |
| `ReadTimeout` | O servidor demorou mais que o limite | Aumente o limite, ou repita o pedido (Módulo 11) |
| `ConnectionError` (no Linux, "Connection refused") | O site não está no ar | Ligue o site, e confira o endereço e a porta |
| O programa lê uma página de erro como se fosse boa | Faltou o `raise_for_status()` | Chame-o logo depois do pedido |
| `PÃ¡gina` no lugar de `Página` | O `resposta.text` supôs a codificação errada | Use `resposta.content` (bytes) com o BeautifulSoup |
| `HTTPError: 404 Client Error` | A página não existe | Confira o endereço; não adianta repetir |

## // Prática guiada

1. Rode `05_a_primeiro_pedido.py` e confira cada linha da saída.
2. Rode `05_b_codificacao.py` e veja o `PÃ¡gina` com os seus olhos.
3. Rode `05_c_erros_e_timeout.py` e compare os tempos (3,0 s sem limite, 1,0 s com).
4. Desligue o Mural Tech (`Ctrl+C` no terminal dele) e rode o `05_a` de novo. Que erro aparece, e em qual linha?
5. Rode `05_d_sessao_e_user_agent.py` e confirme que o servidor recebeu o seu `User-Agent`.

## // Pratique sozinho

> **DESAFIO**
> Escreva a função `baixar(sessao, url)` do "bom exemplo", e use-a para pedir `/vagas/?pagina=3` e `/vagas/v999`. O primeiro deve imprimir o tamanho em bytes, e o segundo deve ser capturado com `try/except` e imprimir `404 Client Error: Not Found for url: ...`. Dica: o `raise_for_status()` levanta `requests.exceptions.HTTPError`.

## // Aplicando no projeto da semana

1. Crie, na pasta do projeto, o arquivo `http_basico.py` com a função `baixar()` e uma sessão com o seu `User-Agent` (o do Módulo 03).
2. Teste-a contra `/vagas/`. Você a reaproveita no Módulo 07.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> O seu scraper roda toda madrugada. Em uma noite, o servidor do site travou e ficou aceitando conexões sem nunca responder. O que acontece com o seu programa, com e sem `timeout`?

Resposta: **sem timeout**, o programa fica parado no primeiro pedido, esperando para sempre. Ele não dá erro, não grava nada e não termina, e de manhã você só descobre porque os dados pararam de chegar. **Com timeout**, o pedido falha em poucos segundos com `Timeout`, o programa trata o erro (por exemplo, tentando de novo mais tarde), registra o problema e segue.

## // Resumo do módulo

- [ ] Sei fazer um pedido com `requests.get` e ler status, cabeçalhos, `.content` e `.text`.
- [ ] Sei usar `params` e sei que os redirecionamentos são seguidos sozinhos.
- [ ] Sei por que passo `resposta.content` ao BeautifulSoup (a armadilha do `PÃ¡gina`).
- [ ] Sei que **todo pedido** leva `timeout`.
- [ ] Sei a diferença entre uma exceção (`ConnectionError`, `Timeout`) e um status de erro (`raise_for_status`).
- [ ] Sei usar uma sessão com um `User-Agent` honesto.

---

**Próximo módulo:** `06-beautifulsoup-lendo-o-html.md`, a página chegou. Agora, ler o que está dentro dela.

`Material de Estudo // Coffee & Code`
