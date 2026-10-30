# Módulo 17, Selenium e a Comparação

Português · [English](../docs-eng/17-selenium-and-the-comparison.md)

`SEM 07 // Data & Scraping, Parte 1: Coleta` | **Trilha veterano, bônus**

---

## // Antes de começar

O **Selenium** é a ferramenta de controle de navegadores mais antiga e conhecida, muito usada em testes de sites. Este módulo faz **a mesma tarefa do Módulo 16** com ele, e termina com uma comparação honesta entre as duas ferramentas. É um módulo **bônus**: o Playwright, sozinho, já resolve o que a semana pede.

## // O Selenium

Instalação: `pip install selenium` (verificado na versão **4.51.0**). O Selenium fala com o navegador por meio de um programa intermediário, o **driver** (para o Chrome, o `chromedriver`). Segundo a documentação do Selenium 4, ele costuma encontrar e baixar o driver certo sozinho, por meio do "Selenium Manager". **Este material não testou esse caminho**: o ambiente de produção não tinha acesso ao download. Os testes usaram um `chromedriver` da mesma série do navegador (versão 153), indicado pelas variáveis do `navegador.py`. No seu computador, no uso normal, não defina nada, e confira a documentação do Selenium se algo falhar na partida.

## // A mesma coleta, com Selenium

Este é o `17_a_selenium_basico.py`:

```python
"""Selenium: a mesma coleta, com esperas explícitas."""
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from navegador import opcoes_selenium

BASE = "http://127.0.0.1:8080"

opcoes, servico = opcoes_selenium()
driver = webdriver.Chrome(options=opcoes, service=servico)
try:
    driver.get(f"{BASE}/vagas-js/")
    CARTAO = (By.CSS_SELECTOR, "article.vaga")
    print("logo depois do get:", len(driver.find_elements(*CARTAO)), "cartões")
    print("texto do #resultado:", driver.find_element(By.ID, "resultado").text)

    espera = WebDriverWait(driver, timeout=5)
    espera.until(EC.presence_of_element_located(CARTAO))
    cartoes = driver.find_elements(*CARTAO)
    print("depois de esperar:", len(cartoes), "cartões")
    titulos = [c.find_element(By.CSS_SELECTOR, "h2.titulo").text
               for c in cartoes[:3]]
    print("primeiros títulos:", titulos)
    print("data-id do primeiro:", cartoes[0].get_attribute("data-id"))

    print("--- find_elements não reclama quando não acha; find_element reclama")
    print("find_elements:", driver.find_elements(By.CSS_SELECTOR, ".nao-existe"))
    try:
        driver.find_element(By.CSS_SELECTOR, ".nao-existe")
    except NoSuchElementException as erro:
        print("NoSuchElementException:", erro.msg.splitlines()[0])
finally:
    driver.quit()
```

```
logo depois do get: 0 cartões
texto do #resultado: Carregando...
depois de esperar: 8 cartões
primeiros títulos: ['Analista de Dados Pleno',
 'Desenvolvedor(a) Python Júnior', 'Estágio em Desenvolvimento Web']
data-id do primeiro: v002
--- find_elements não reclama quando não acha; find_element reclama
find_elements: []
NoSuchElementException: no such element: Unable to locate element:
 {"method":"css selector","selector":".nao-existe"}
```

(Duas linhas foram quebradas para caber.) O resultado é o mesmo do Playwright: **0 cartões** logo depois de abrir a página, **8** depois de esperar. As diferenças estão no **jeito** de esperar e de procurar:

- **A espera é explícita.** No Selenium, você escreve o `WebDriverWait(driver, timeout=5).until(...)`, com a condição (`presence_of_element_located`). Sem ela, o `find_element` falha **na hora**, se o elemento ainda não existe.
- **Dois verbos para procurar.** `find_elements` (no plural) devolve uma **lista**, vazia se nada casar. `find_element` (no singular) **levanta** `NoSuchElementException` se nada casar.

## // A espera olha de tempos em tempos

Uma surpresa que a execução mostrou, e que merece atenção. O `WebDriverWait` **não** olha continuamente: ele **confere a condição a cada 0,5 segundo**, por padrão. O script `17_b_esperar_demais.py`:

```python
"""A espera do Selenium: o intervalo entre verificações e o Timeout."""
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from navegador import opcoes_selenium

BASE = "http://127.0.0.1:8080"

opcoes, servico = opcoes_selenium()
driver = webdriver.Chrome(options=opcoes, service=servico)
try:
    driver.get(f"{BASE}/vagas-js/")

    print("--- esperar por algo que nunca aparece")
    inicio = time.perf_counter()
    try:
        WebDriverWait(driver, timeout=1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".nao-existe")))
    except TimeoutException as erro:
        gasto = time.perf_counter() - inicio
        print(f"TimeoutException depois de {gasto:.1f} s | "
              f"mensagem: {erro.msg!r}")

    print("--- a espera olha de tempos em tempos (por padrão, a cada 0,5 s)")
    espera = WebDriverWait(driver, timeout=5, poll_frequency=0.1)
    print("intervalo entre as verificações:", espera._poll, "s")
    espera.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "article.vaga")))
    print("cartões:", len(driver.find_elements(By.CSS_SELECTOR, "article.vaga")))
    print("intervalo padrão:", WebDriverWait(driver, 5)._poll, "s")
finally:
    driver.quit()
```

```
--- esperar por algo que nunca aparece
TimeoutException depois de 1.0 s | mensagem: ''
--- a espera olha de tempos em tempos (por padrão, a cada 0,5 s)
intervalo entre as verificações: 0.1 s
cartões: 8
intervalo padrão: 0.5 s
```

Três fatos: (1) esperar por algo que **nunca aparece** termina em `TimeoutException`, depois do tempo combinado (1,0 s), e **com a mensagem vazia**: não esperem um texto explicativo. (2) O intervalo entre as verificações pode ser ajustado (`poll_frequency=0.1`). (3) O intervalo **padrão** é de 0,5 s. Por isso, uma espera de `timeout=0.1` com a verificação de 0,5 s é um erro conceitual: ela só verifica no instante zero, e no meio da conta estoura.

## // Playwright × Selenium

As duas ferramentas resolveram **o mesmo problema**, na mesma página, e extraíram os mesmos 8 cartões. Esta comparação separa o que foi **observado** do que vem da **documentação** (e não foi testado aqui):

| Aspecto | Playwright | Selenium |
|---|---|---|
| Leu os 8 cartões da página com JavaScript | Sim (observado) | Sim (observado) |
| Como espera | **Automaticamente**, antes de agir; e com `wait_for` para uma condição | **Explicitamente**: você escreve `WebDriverWait(...).until(...)` |
| Elemento que não existe | `count()` devolve `0`, e esperar demais dá `TimeoutError` | `find_elements` devolve `[]`, `find_element` levanta `NoSuchElementException` |
| Vários elementos para um texto só | Recusa (modo estrito) | O `find_element` devolve **o primeiro**, sem reclamar (não testado neste material) |
| Descobrir a chamada à API que a página faz | `expect_response` (observado) | Não é o foco da ferramenta (a documentação do Selenium trata de outros recursos para isso) |
| Navegadores suportados | Segundo a documentação, Chromium, Firefox e WebKit | Segundo a documentação, vários, por meio dos drivers |
| Driver | Vem embutido na instalação do navegador | Um driver à parte (o Selenium Manager tenta cuidar disso) |
| Velocidade | **Não medida** | **Não medida** |

A escolha, então, é menos sobre "qual é melhor" e mais sobre o contexto:

- **Comece pela API** (Módulo 16), se a página tiver uma que você possa usar com permissão.
- **Para um projeto novo de coleta com navegador**, o Playwright poupa o código de espera, que no Selenium é onde mais se erra.
- **Se o seu grupo já usa Selenium** (em testes de sites, por exemplo), reaproveitar o conhecimento e a infraestrutura costuma valer mais que trocar.

## // Os testes

No arquivo `veterano/tests/test_navegador.py`, um teste confirma que o Selenium, com espera explícita, acha os 8 cartões. Como os demais testes de navegador, ele **se pula sozinho** se o navegador ou o driver não estiverem disponíveis.

## // Bom exemplo × mau exemplo

**Mau exemplo**: um `sleep` fixo, ou a "espera implícita" misturada com a explícita:

```python
driver.get(url)
time.sleep(3)
```

**Bom exemplo**: uma espera explícita, por uma condição:

```python
WebDriverWait(driver, timeout=5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "article.vaga")))
```

## // Erros comuns

Estas mensagens foram obtidas ao executar o código.

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| `NoSuchElementException: no such element: Unable to locate element` | O `find_element` não achou nada (talvez a página ainda não montou) | Espere com `WebDriverWait`, ou use `find_elements` e confira a lista |
| `TimeoutException` com a mensagem vazia | A condição não virou verdadeira no tempo combinado | Confira o seletor e a página, e aumente o tempo só se fizer sentido |
| Uma espera curta demais falha, mesmo com a página rápida | A verificação é de 0,5 s, por padrão | Ajuste o `poll_frequency`, ou o tempo |
| O navegador "fica aberto" depois do script | Faltou o `driver.quit()` | Use `try/finally` |
| O driver não inicia | A versão do driver não casa com a do navegador, ou ele não foi encontrado | Confira as versões, e a documentação do Selenium (não reproduzido aqui) |

## // Prática guiada

1. Rode `17_a_selenium_basico.py` (com o Chromium e o `chromedriver`, ou com o Selenium Manager funcionando) e compare com o `16_b`.
2. Rode `17_b_esperar_demais.py` e leia o intervalo padrão de 0,5 s.
3. Acrescente ao `17_a` uma espera por um elemento que não existe, e veja o `TimeoutException`.

## // Pratique sozinho

> **DESAFIO**
> Escreva a mesma extração (título e `data-id` dos 8 cartões de `/vagas-js/`) **duas vezes**, com o Playwright e com o Selenium, e compare: quantas linhas cada uma tem? Onde está a espera em cada uma? Resultado esperado: os mesmos 8 pares (`v002` e `Analista de Dados Pleno` na frente), e uma diferença clara no trecho que cuida da espera.

## // Aplicando no projeto da semana

1. No `anotacoes.md`, escreva as três perguntas que você faz antes de escolher entre a API, o Playwright e o Selenium.
2. Escolha **uma** das duas ferramentas de navegador para o seu projeto, e justifique a escolha em duas frases.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> O seu script com Selenium roda bem no seu computador, e falha de vez em quando em outro, mais lento, com `NoSuchElementException`. O que está acontecendo, e qual é a correção?

Resposta: o computador mais lento monta a página **depois** do momento em que o script já procurou o elemento. No seu computador, a página montava a tempo, por sorte. A correção é a **espera explícita** (`WebDriverWait` com uma condição), e não um `sleep` maior: o `sleep` só **adia** o problema para o próximo computador mais lento. O mesmo vale para o Playwright, em que o `wait_for()` cumpre esse papel.

## // Resumo do módulo

- [ ] Sei fazer a mesma coleta com o Selenium, com espera explícita.
- [ ] Sei a diferença entre `find_element` e `find_elements`.
- [ ] Sei que a espera do Selenium verifica de 0,5 em 0,5 s, por padrão.
- [ ] Sei comparar as duas ferramentas, separando o que foi observado do que vem da documentação.
- [ ] Sei escolher: a API primeiro, e depois a ferramenta que o meu contexto pede.

---

**Fim da trilha veterano.** Confira o `entregavel.md`, para a lista final do que entregar.

`Material de Estudo // Coffee & Code`
