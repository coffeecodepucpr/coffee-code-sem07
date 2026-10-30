# Módulo 16, Playwright: Páginas com JavaScript

Português · [English](../docs-eng/16-playwright-pages-with-javascript.md)

`SEM 07 // Data & Scraping, Parte 1: Coleta` | **Trilha veterano**

---

## // Antes de começar

No Módulo 01, você viu que uma página pode chegar **vazia** e ser preenchida por JavaScript depois. O `requests` e o BeautifulSoup não executam JavaScript, e portanto não enxergam essas páginas. Este módulo apresenta as duas saídas: **controlar um navegador de verdade** com o Playwright, e (melhor, quando dá) **achar a API que a página usa** e chamá-la direto.

## // O problema, de novo

Este é o script `16_a_requests_nao_ve.py`, com o resultado real, contra a página `/vagas-js/`:

```python
resposta = requests.get(f"{BASE}/vagas-js/", timeout=10)
sopa = BeautifulSoup(resposta.content, "lxml")
print("status:", resposta.status_code)
print("cartões na página:", len(sopa.select("article.vaga")))
print("texto do #resultado:", sopa.select_one("#resultado").get_text())
print("há um <script> no HTML?", sopa.find("script") is not None)
```

```
status: 200
cartões na página: 0
texto do #resultado: Carregando...
há um <script> no HTML? True
```

<div align="center">
<img src="./assets/svg/estatico-x-renderizado.svg" alt="Comparação entre uma página estática e uma montada por JavaScript, com as soluções Playwright ou a chamada direta à API" width="640">
</div>

## // O Playwright

> **PLAYWRIGHT: EM PALAVRAS SIMPLES**
> É uma biblioteca que **controla um navegador de verdade** (Chromium, e outros) por código: abre páginas, espera o JavaScript terminar, lê o que apareceu e clica em botões. O Playwright executa a página em um navegador real, incluindo o JavaScript. Isso **não** significa que a automação seja indistinguível de uma pessoa: automação de navegador pode ser detectável.

Instalação, em duas etapas (a segunda baixa o navegador):

```
pip install playwright
playwright install chromium
```

Este material foi verificado com o Playwright **1.63.0**. Um aviso de honestidade: os testes foram feitos com um Chromium **153** empacotado por terceiros, e **não** com o navegador que o `playwright install` baixa (o meu ambiente não tinha acesso ao download). O `playwright install chromium` na sua máquina instalará outro build, e pequenas diferenças são possíveis. Os scripts usam o arquivo `navegador.py`, que **só** altera o comportamento se você definir as variáveis `CHROMIUM_PATH` e `CHROMIUM_ARGS`. No uso normal, não defina nada.

## // O primeiro script

Este é o `16_b_playwright_basico.py`:

```python
"""Playwright: abrir a página de verdade, esperar o JavaScript e extrair."""
import asyncio

from playwright.async_api import async_playwright

from navegador import opcoes_playwright

BASE = "http://127.0.0.1:8080"


async def main():
    async with async_playwright() as p:
        navegador = await p.chromium.launch(**opcoes_playwright())
        pagina = await navegador.new_page()
        await pagina.goto(f"{BASE}/vagas-js/")

        cartoes = pagina.locator("article.vaga")
        print("logo depois do goto:", await cartoes.count(), "cartões")
        print("texto do #resultado:", await pagina.inner_text("#resultado"))

        await cartoes.first.wait_for()          # espera o JavaScript terminar
        print("depois de esperar:", await cartoes.count(), "cartões")

        titulos = await pagina.eval_on_selector_all(
            "article.vaga h2.titulo", "els => els.map(e => e.textContent)")
        print("primeiros títulos:", titulos[:3])
        primeiro = cartoes.first
        print("data-id do primeiro:", await primeiro.get_attribute("data-id"))
        empresa = await primeiro.locator(".empresa").inner_text()
        print("empresa do primeiro:", empresa)
        await navegador.close()


asyncio.run(main())
```

```
logo depois do goto: 0 cartões
texto do #resultado: Carregando...
depois de esperar: 8 cartões
primeiros títulos: ['Analista de Dados Pleno',
 'Desenvolvedor(a) Python Júnior', 'Estágio em Desenvolvimento Web']
data-id do primeiro: v002
empresa do primeiro: Pinhão Dados
```

(A lista de títulos foi quebrada para caber.) O resultado conta a história toda: **logo depois do goto**, a página está no estado de `requests`: 0 cartões, e "Carregando...". Só depois do `wait_for()` (que espera o primeiro cartão aparecer) os 8 cartões existem. O que cada peça faz:

| Peça | O que faz |
|---|---|
| `async_playwright()` e `p.chromium.launch()` | Liga o Playwright e abre o navegador (por padrão, sem janela) |
| `navegador.new_page()` e `pagina.goto(url)` | Abre uma aba, e navega |
| `pagina.locator("article.vaga")` | Um **localizador**: descreve o que procurar, com um seletor CSS, mas não procura ainda |
| `.count()` | Quantos elementos existem **agora** |
| `.first.wait_for()` | **Espera** o primeiro elemento aparecer |
| `inner_text()`, `get_attribute()` | Lê o texto e os atributos |
| `eval_on_selector_all(seletor, js)` | Roda uma pequena função JavaScript sobre todos os elementos |

## // A espera automática

O Playwright foi desenhado para **esperar sozinho**: antes de agir sobre um elemento (clicar, ler o texto), ele confere se o elemento está pronto, e espera o tempo necessário (a documentação chama essas conferências de "actionability", e elas valem para os métodos que agem sobre o elemento). Por isso, em geral **não se usa time.sleep**: ele espera tempo demais (desperdício) ou de menos (erro intermitente). O que o código acima usa é uma **condição**: "espere o primeiro cartão aparecer".

A contagem logo depois do `goto`, que devolveu `0`, é um bom lembrete: `count()` é uma **foto do momento**, e não espera. Para contar o que vai aparecer, espere primeiro.

## // A rota mais robusta: achar a API

Ler uma página montada por JavaScript pelo navegador funciona, mas é **pesado** (abre um navegador inteiro) e **frágil** (depende do HTML final). Há um caminho melhor, quando existe: a página, para se montar, **pede os dados a uma API**. Se você descobre qual, pode chamá-la direto, sem navegador nenhum, e receber o dado já em JSON, organizado.

O Playwright ajuda a **descobrir** a chamada. Este é o `16_c_achar_a_api.py`:

```python
"""O atalho: a página busca os dados em uma API, e você pode usá-la direto."""
import asyncio

import httpx
from playwright.async_api import async_playwright

from navegador import opcoes_playwright

BASE = "http://127.0.0.1:8080"


async def main():
    async with async_playwright() as p:
        navegador = await p.chromium.launch(**opcoes_playwright())
        pagina = await navegador.new_page()
        chamadas = []
        pagina.on("request",
                  lambda r: chamadas.append((r.resource_type, r.url)))
        async with pagina.expect_response("**/api/vagas*") as espera:
            await pagina.goto(f"{BASE}/vagas-js/")
        resposta = await espera.value
        dados = await resposta.json()
        print("a página chamou:", resposta.url)
        print("status:", resposta.status, "| total:", dados["total"],
              "| itens:", len(dados["itens"]))
        api = [u.replace(BASE, "") for tipo, u in chamadas
               if tipo in ("fetch", "xhr")]
        print("chamadas fetch/xhr:", api)
        await navegador.close()

    print("--- o atalho, sem navegador nenhum")
    async with httpx.AsyncClient(base_url=BASE) as cliente:
        resposta2 = await cliente.get(
            "/api/vagas", params={"pagina": 2, "por_pagina": 8})
        pagina2 = resposta2.json()
    print("página 2 direto da API:", [v["id"] for v in pagina2["itens"]])


asyncio.run(main())
```

```
a página chamou: http://127.0.0.1:8080/api/vagas?pagina=1&por_pagina=8
status: 200 | total: 20 | itens: 8
chamadas fetch/xhr: ['/api/vagas?pagina=1&por_pagina=8']
--- o atalho, sem navegador nenhum
página 2 direto da API: ['v010', 'v009', 'v012', 'v011', 'v014', 'v013',
 'v016', 'v015']
```

(A última linha foi quebrada para caber.) O `expect_response` espera uma resposta cujo endereço casa com o padrão do código (qualquer endereço terminado em `/api/vagas` e seus parâmetros), e entrega a resposta, inclusive o JSON. Descoberto o endereço, o resto do script **abandona o navegador** e chama a API com o `httpx`. A API traz o `total` (20), e permite pedir **qualquer página** (`pagina=2`) sem navegar. E, ao contrário da lista em HTML (Módulo 07), **pedir uma página além do fim devolve uma lista vazia**: paginando a API "até vir vazia", o resultado real é de 20 vagas em 3 páginas, 20 ids únicos, e o `total` declarado de 20.

Nos navegadores, as ferramentas do desenvolvedor mostram essas chamadas na aba de rede, e é por ali que se costuma descobrir uma API. A interface dessas ferramentas não foi conferida na produção deste material, e os nomes variam entre navegadores.

> **A API TAMBÉM TEM REGRAS**
> Chamar uma API que a página usa não a torna livre de regras. Os mesmos cuidados do Módulo 03 valem: termos de uso, ritmo, identificação, e (se houver) o que o dono da API declara. Uma API **sem documentação**, que só existe para a página, pode mudar sem aviso.

## // Boas maneiras com um navegador

- **O Playwright não lê o robots.txt por você.** Confira `can_fetch` antes de abrir a página, como no Módulo 07.
- **Um navegador é pesado.** Abra **um** navegador e reutilize-o para várias páginas; não abra um por página.
- **Não use o navegador para escapar de proteções.** Ele executa JavaScript, o que o torna capaz de muitas coisas que este material **não ensina**: contornar captchas, imitar comportamento humano para driblar um bloqueio. Se o site bloqueia robôs, a resposta é perguntar ao dono, e não disfarçar o robô.

## // Erros comuns

Estas mensagens foram obtidas ao executar o código.

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| `strict mode violation: locator("article.vaga") resolved to 8 elements` | O localizador casou com vários elementos, e você pediu **um** texto | Use `.first`, `.nth(i)`, ou `.all_inner_texts()` |
| `TimeoutError: Page.wait_for_selector: Timeout 1000ms exceeded.` | O elemento não apareceu a tempo (ou nunca vai aparecer) | Confira o seletor e a página; aumente o `timeout` só se fizer sentido |
| `count()` devolve `0` logo depois do `goto` | O JavaScript ainda não montou a página | Espere antes: `.first.wait_for()` |
| `BrowserType.launch: Executable doesn't exist at ...` | O navegador não foi baixado | Rode `playwright install chromium` |
| Funciona às vezes, e falha outras | Um `time.sleep` fixo, curto demais | Espere por uma **condição**, e não por um tempo |
| O navegador "fica aberto" depois do script | Faltou o `await navegador.close()` | Feche no fim, de preferência dentro de `try/finally` |

O primeiro erro merece o script `16_d_erros.py` (quebrado para caber):

```
--- 1) o seletor casa com VÁRIOS elementos e você pede um texto
Error: Locator.inner_text: Error: strict mode violation:
 locator("article.vaga") resolved to 8 elements:
--- 2) esperar por algo que nunca aparece
TimeoutError: Page.wait_for_selector: Timeout 1000ms exceeded.
```

O "modo estrito" é uma proteção: o Playwright prefere **recusar** a adivinhar qual dos 8 elementos você quis.

## // Os testes

Os testes de navegador estão em `veterano/tests/test_navegador.py`. Eles **se pulam sozinhos** se não houver navegador instalado. Com um navegador disponível, cinco testes confirmam: que o `requests` não enxerga os cartões, que o Playwright espera o JavaScript e acha os 8 cartões (o primeiro é o `v002`), que ele captura a chamada à API (status `200`, `total` de 20), que o localizador com vários elementos viola o modo estrito, e (no Módulo 17) que o Selenium faz o mesmo. Rodando sem navegador, **12 passam e 4 se pulam**; com o navegador, todos os 16 passam.

## // Bom exemplo × mau exemplo

**Mau exemplo**: um `sleep` fixo, e um seletor de posição:

```python
await pagina.goto(url)
await asyncio.sleep(3)
html = await pagina.content()
```

**Bom exemplo**: esperar por uma condição, e preferir a API quando existir:

```python
await pagina.locator("article.vaga").first.wait_for()
```

## // Prática guiada

1. Rode `16_a_requests_nao_ve.py` e confirme os 0 cartões.
2. Instale o Playwright e o Chromium, e rode `16_b_playwright_basico.py`.
3. Rode `16_c_achar_a_api.py` e observe o endereço da API.
4. Rode `16_d_erros.py` e leia as duas mensagens.
5. Experimente remover o `wait_for()` do `16_b` e veja o que muda.

## // Pratique sozinho

> **DESAFIO**
> Escreva um coletor que, **sem abrir navegador**, colete todas as vagas da API `/api/vagas`, paginando com `por_pagina=8` até a lista vir vazia. Resultado esperado: **20 vagas em 3 páginas**, com 20 ids únicos, e o `total` declarado de 20. Depois, acrescente o limitador de ritmo do Módulo 15 e o `User-Agent` do Módulo 03.

## // Aplicando no projeto da semana

1. Na pasta `veterano/` do projeto, coloque o `navegador.py`, o `16_b` e o `16_c`.
2. Faça o desafio da API, e guarde o resultado no banco com as funções do Módulo 10.
3. Anote no `anotacoes.md` **quando** você escolheria um navegador, e **quando** a API.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> Você precisa coletar uma página montada por JavaScript, e descobre que ela usa uma API interna, sem documentação nem termos próprios. O que você faz antes de chamá-la direto?

Resposta: volta ao **Módulo 03**. Que ela seja fácil de chamar não quer dizer que seja permitida: leia os termos do site, o `robots.txt` (a API está sob um caminho que ele proíbe?), e use um ritmo educado e um `User-Agent` honesto. Uma API interna não tem garantia de estabilidade, então **conte** com ela mudando, e mantenha o alarme de campos vazios (Módulo 11). Se houver dúvida real sobre a permissão, peça ao dono do site.

## // Resumo do módulo

- [ ] Sei por que o `requests` não vê uma página montada por JavaScript.
- [ ] Sei abrir uma página com o Playwright, esperar o JavaScript e extrair com localizadores.
- [ ] Sei que `count()` é uma foto do momento, e que devo esperar por **condições**, e não por tempo.
- [ ] Sei descobrir a API que a página usa, e chamá-la direto.
- [ ] Sei as boas maneiras com um navegador, e o que **não** fazer com ele.
- [ ] Sei reconhecer o modo estrito e o `TimeoutError`.

---

**Próximo módulo:** `17-selenium-e-a-comparacao.md` (**bônus**), a outra ferramenta de navegador, e quando escolher cada uma.

`Material de Estudo // Coffee & Code`
