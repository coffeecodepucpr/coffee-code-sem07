# Módulo 07, O Primeiro Scraper: Vagas

Português · [English](../docs-eng/07-the-first-scraper-jobs.md)

`SEM 07 // Data & Scraping, Parte 1: Coleta`

---

## // Antes de começar

Você já sabe pedir uma página (Módulo 05), ler o HTML (Módulo 06) e as regras do jogo (Módulo 03). Este módulo junta tudo em um programa que faz a **coleta completa**: a lista de vagas, o detalhe de cada uma e todas as páginas. É o primeiro programa da semana que merece o nome de scraper.

## // O plano

O Mural Tech tem 20 vagas, divididas em 3 páginas de 8. Para ter todos os dados, o scraper precisa de dois níveis de visita:

1. Visitar cada **página da lista** (`/vagas/`, `/vagas/?pagina=2`, ...), e ler os cartões.
2. Visitar o **detalhe** de cada vaga (`/vagas/v002`), para pegar a descrição, que não aparece na lista.

Isso dá 3 páginas de lista e 20 de detalhe: **23 pedidos**, mais o `robots.txt`.

## // Paginar em laço

<div align="center">
<img src="./assets/svg/paginacao-em-laco.svg" alt="O laço de paginação: baixar a página, ler as vagas, procurar o link Próxima e repetir, até a última página, que não tem Próxima" width="640">
</div>

A ideia: comece na primeira página, leia as vagas, procure o link **Próxima**, e, se ele existir, repita com o endereço dele. Quando uma página não tiver o link, a coleta acabou. A função `proxima_pagina()` que você escreveu no `parsers.py` faz a busca (`a[rel=next]`) e já devolve o endereço completo.

### A armadilha: "até a página vir vazia"

Muita gente escreve o laço de outro jeito: "peça a página 1, a 2, a 3... até uma vir **vazia**". Neste site, isso **nunca termina**. Veja o resultado real, com uma trava que o corta na sexta página (`07_a_armadilha_pagina_vazia.py`):

```
pedi a página 1: 8 vagas | Página 1 de 3 | v002..v007
pedi a página 2: 8 vagas | Página 2 de 3 | v010..v015
pedi a página 3: 4 vagas | Página 3 de 3 | v018..v019
pedi a página 4: 4 vagas | Página 3 de 3 | v018..v019
pedi a página 5: 4 vagas | Página 3 de 3 | v018..v019
pedi a página 6: 4 vagas | Página 3 de 3 | v018..v019
```

Pedir a página 4 devolve a página 3 de novo, e nunca vem vazia. Sites reais se comportam de formas variadas com páginas inexistentes: alguns dão `404`, outros devolvem a última, outros devolvem uma página vazia. Não dá para saber de antemão, e por isso o laço certo **não depende disso**: ele segue o link Próxima, e tem **duas travas de segurança**:

- um conjunto `visitadas`, para nunca visitar o mesmo endereço duas vezes;
- um `MAX_PAGINAS`, um teto de páginas, para o caso de tudo o mais falhar.

## // O scraper completo

Este é o `07_b_primeiro_scraper.py`, na íntegra:

```python
import json
import time
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests

from parsers import ler_descricao, ler_html, ler_vagas_da_pagina, proxima_pagina

BASE = "http://127.0.0.1:8080"
USER_AGENT = "MuralColetaBot/1.0 (projeto de estudo; contato: voce@example.com)"
MAX_PAGINAS = 20

sessao = requests.Session()
sessao.headers["User-Agent"] = USER_AGENT

robots = RobotFileParser()
robots.parse(sessao.get(f"{BASE}/robots.txt", timeout=10).text.splitlines())
espera = float(robots.crawl_delay(USER_AGENT) or 0)
print(f"robots.txt lido. Espera entre pedidos: {espera} s")


def baixar(url):
    if not robots.can_fetch(USER_AGENT, url):
        raise RuntimeError(f"o robots.txt não permite {url}")
    time.sleep(espera)
    resposta = sessao.get(url, timeout=10)
    resposta.raise_for_status()
    return ler_html(resposta)


inicio = time.perf_counter()
vagas, visitadas = [], set()
url = urljoin(BASE, "/vagas/")
while url and url not in visitadas and len(visitadas) < MAX_PAGINAS:
    visitadas.add(url)
    sopa = baixar(url)
    da_pagina = ler_vagas_da_pagina(sopa, url)
    print(f"página {len(visitadas)}: {len(da_pagina)} vagas")
    for vaga in da_pagina:
        vaga["descricao"] = ler_descricao(baixar(vaga["url"]))
        vagas.append(vaga)
    url = proxima_pagina(sopa, url)

with open("vagas.json", "w", encoding="utf-8") as arquivo:
    json.dump(vagas, arquivo, ensure_ascii=False, indent=2)

print(f"total: {len(vagas)} vagas em {len(visitadas)} páginas")
print(f"tempo: {time.perf_counter() - inicio:.0f} s")
print("primeira:", vagas[0]["titulo"], "|", vagas[0]["empresa"])
print("descrição:", vagas[0]["descricao"][:50] + "...")
```

```
robots.txt lido. Espera entre pedidos: 1.0 s
página 1: 8 vagas
página 2: 8 vagas
página 3: 4 vagas
total: 20 vagas em 3 páginas
tempo: 23 s
primeira: Analista de Dados Pleno | Pinhão Dados
descrição: A Pinhão Dados procura uma pessoa para a posição d...
```

Quatro coisas merecem atenção:

- **Respeita o robots.txt**: lê as regras uma vez, e confere **cada endereço** com `can_fetch` antes de pedi-lo. Uma página proibida levanta um erro, em vez de ser visitada.
- **Espera entre pedidos**: usa o `Crawl-delay` do próprio site (1 segundo). É por isso que 23 pedidos levam **23 segundos**: o scraper está sendo educado, e não lento.
- **Reaproveita o seu trabalho**: a leitura dos cartões vem do `parsers.py` do Módulo 06, e o `baixar()` junta os cuidados do Módulo 05 (sessão, `timeout`, `raise_for_status`).
- **Grava em um arquivo**: o resultado vai para o `vagas.json`, para você examinar. O arquivo tem 20 itens, cada um com os campos `descricao`, `empresa`, `id_externo`, `local`, `modalidade`, `nivel`, `publicada`, `salario`, `tags`, `titulo` e `url`.

> **UMA PEÇA AINDA FALTA: O PROGRAMA PARA NO PRIMEIRO ERRO**
> Neste primeiro scraper, uma página que falhe derruba a coleta inteira, e as vagas já lidas se perdem. O Módulo 11 resolve isso com tentativas e isolamento de falhas, e o Módulo 12 grava o que deu certo mesmo quando algo falha.

## // Bom exemplo × mau exemplo

**Mau exemplo**: paginar por contagem, e nunca parar:

```python
numero = 1
while True:
    vagas = ler(pedir(f"/vagas/?pagina={numero}"))
    if not vagas:
        break
    numero += 1
```

Neste site, `vagas` nunca é vazio, e o programa pede páginas para sempre.

**Bom exemplo**: seguir o link, com travas:

```python
while url and url not in visitadas and len(visitadas) < MAX_PAGINAS:
    visitadas.add(url)
    ...
    url = proxima_pagina(sopa, url)
```

## // Erros comuns

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| O programa nunca termina | Paginou "até vir vazia", e o site repete a última página | Siga o link Próxima, e use `visitadas` e `MAX_PAGINAS` |
| O programa leva mais de 20 segundos | Respeita o `Crawl-delay` de 1 s | É o esperado: 23 pedidos, 1 s cada |
| `RuntimeError: o robots.txt não permite ...` | Tentou visitar uma área proibida | Remova essa página do plano |
| Os links vêm como `/vagas/v002` e não funcionam | São relativos | Use `urljoin` (já feito dentro do `parsers.py`) |
| A mesma vaga aparece duas vezes na lista | A página foi visitada duas vezes | Confira o conjunto `visitadas` |
| `AttributeError: 'NoneType' object has no attribute 'get_text'` | Um campo faltou em uma vaga | Use `texto()` (Módulo 06) |

## // Prática guiada

1. Rode `07_a_armadilha_pagina_vazia.py` e veja a página 3 se repetir.
2. Rode `07_b_primeiro_scraper.py` e **espere os 23 segundos**: a pausa é a educação em ação.
3. Abra o `vagas.json` e confira os campos de uma vaga.
4. Mude o `espera` para `0`, rode de novo e veja a diferença. Depois **volte a usar o valor do robots.txt**: o Mural Tech é local e aguenta, mas o hábito é o que vale.

## // Pratique sozinho

> **DESAFIO**
> Leia o `vagas.json` e conte quantas vagas cada empresa tem, com `collections.Counter`. Resultado esperado: as 5 empresas (Orbita Software, Pinhão Dados, Araucária Labs, Cafeteria Digital e Serra Azul Tech) aparecem com **4 vagas cada**, somando 20. Depois, imprima o título das vagas que têm `python` nas tags.

## // Aplicando no projeto da semana

1. Na pasta do projeto, crie `coletar_vagas.py` com o código deste módulo, importando as funções do seu `parsers.py`.
2. Rode-o e confira o `vagas.json`.
3. Se você versiona com Git, faça um commit: `git commit -m "Adiciona o primeiro scraper de vagas"`. Não inclua o `vagas.json` (ele é resultado, e não código).

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> O seu scraper roda bem por semanas. Um dia, o site acrescenta uma quarta página, e o link "Próxima" da terceira passa a apontar para ela. O seu scraper precisa mudar?

Resposta: **não**. Como ele **segue o link** em vez de contar páginas, a quarta página será visitada naturalmente, e a coleta acabará na que não tiver o link. Um scraper que tivesse o número `3` escrito no código perderia a página nova sem avisar. A lição vale além da paginação: sempre que o site já **diz** algo (onde está a próxima página, qual é o id), use o que ele diz, em vez de adivinhar.

## // Resumo do módulo

- [ ] Sei dividir a coleta em dois níveis: a lista e o detalhe.
- [ ] Sei paginar em laço, seguindo o link Próxima.
- [ ] Sei por que "até a página vir vazia" é uma armadilha, e uso `visitadas` e `MAX_PAGINAS`.
- [ ] Sei respeitar o `robots.txt` e o `Crawl-delay` dentro do código.
- [ ] Sei guardar o resultado em um arquivo JSON.
- [ ] Sei que o programa ainda para no primeiro erro, e que isso será corrigido.

---

**Próximo módulo:** `08-limpando-e-normalizando.md`, os dados chegaram. Mas `R$ 7.000 a R$ 9.500` ainda é só um texto.

`Material de Estudo // Coffee & Code`
