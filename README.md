# Coffee & Code | SEM 07 | Data & Scraping (Parte 1: Coleta)

Português · [English](README.en.md)

```text
> module: sem-07
> tema: data & scraping (coleta)
> status: online
> coffee loaded
```

Material da **Semana 07** da trilha do Coffee & Code, clube de tecnologia fundado por estudantes de Engenharia de Software da PUCPR e aberto a todos que querem aprender construindo.

Esta semana ensina a **coletar dados da web de forma organizada, educada e repetível**: baixar páginas, extrair o que interessa, limpar, guardar em um banco de dados sem duplicar e fazer tudo isso rodar sozinho. O resultado é um **pipeline de captura automática para o banco**, com Requests, BeautifulSoup, SQLite e agendamento.

> **Semana independente:** ela não exige nenhuma outra semana do clube. O HTML, o Python e o SQL de que a coleta precisa são apresentados do zero. Esta é a Parte 1 do módulo "Data & Scraping"; a análise dos dados fica para a Parte 2.

> **Sobre o idioma:** o material em inglês fica em [`docs-eng/`](docs-eng/), com a mesma estrutura de [`docs/`](docs/); os READMEs têm versão em inglês com o sufixo `.en.md`. Os diagramas e o código dos exemplos executáveis (nomes, mensagens e comentários) permanecem em português.

## Por onde começar

**[docs/00-comece-aqui.md](docs/00-comece-aqui.md)**: leia este primeiro. Ele apresenta o panorama da semana e o pipeline de coleta inteiro.

Depois, siga os módulos na ordem. Os módulos `01` a `14` formam a trilha principal:

| # | Módulo | Sobre |
|---|---|---|
| 01 | [Como a web entrega páginas](docs/01-como-a-web-entrega-paginas.md) | Pedido, resposta, status e a página montada por JavaScript |
| 02 | [HTML para quem vai extrair](docs/02-html-para-quem-vai-extrair.md) | Tags, atributos, a árvore e o plano de campos |
| 03 | [Ética, termos e robots.txt](docs/03-etica-termos-e-robots-txt.md) | Pode coletar? E como, com educação? |
| 04 | [Python essencial para coleta](docs/04-python-essencial-para-coleta.md) | Ambiente virtual e o Python que a coleta usa |
| 05 | [requests: baixando páginas](docs/05-requests-baixando-paginas.md) | Timeout, status, codificação e sessão |
| 06 | [BeautifulSoup: lendo o HTML](docs/06-beautifulsoup-lendo-o-html.md) | `find`, seletores CSS e os leitores (parsers) |
| 07 | [O primeiro scraper: vagas](docs/07-o-primeiro-scraper-vagas.md) | Lista, detalhe e paginação |
| 08 | [Limpando e normalizando](docs/08-limpando-e-normalizando.md) | Salários, datas e preços viram dados |
| 09 | [O segundo scraper: eventos](docs/09-o-segundo-scraper-eventos.md) | Reaproveitar o que já existe |
| 10 | [SQLite: guardando os dados](docs/10-sqlite-guardando-os-dados.md) | Upsert, sem duplicar, e saber o que mudou |
| 11 | [Robustez e boas maneiras](docs/11-robustez-e-boas-maneiras.md) | Tentativas, `Retry-After`, `ETag` e alarmes |
| 12 | [O pipeline de ponta a ponta](docs/12-o-pipeline-de-ponta-a-ponta.md) | Orquestração, log, trava e códigos de saída |
| 13 | [Agendando a coleta](docs/13-agendando-a-coleta.md) | `cron`, e rodar sozinho |
| 14 | [Projeto guiado](docs/14-projeto-guiado.md) | Montar, conferir em 14 itens e levar a uma fonte real |

Os módulos `15` e `16` são a **trilha veterano**, e o módulo `17` é um bônus dessa trilha. Todos são opcionais e podem ser lidos depois do essencial:

| # | Módulo | Sobre |
|---|---|---|
| 15 | [Scraping assíncrono com httpx](docs/15-scraping-assincrono-com-httpx.md) | Concorrência com limite e o limitador de ritmo |
| 16 | [Playwright: páginas com JavaScript](docs/16-playwright-paginas-com-javascript.md) | Navegador controlado por código e a API da página |
| 17 | [Selenium e a comparação](docs/17-selenium-e-a-comparacao.md) | Bônus: a outra ferramenta, e quando escolher cada uma |

E, para consultar quando precisar:

- [Exemplos executáveis](docs/example/README.md): o site de treino, os scripts de aula, o pipeline e a trilha veterano
- [Desafios](docs/desafios.md): opcionais, para ir além do pedido
- [Entregável](docs/entregavel.md): checklist final antes de fechar a semana

## O site de treino

A semana usa o **Mural Tech**, um site **fictício** que roda no seu computador (`python3 servidor.py`), com vagas e eventos inventados. Ele se comporta como um site de verdade: tem paginação, `robots.txt`, um "dia 2" com mudanças, páginas lentas, erros `429` e `503`, HTML quebrado e uma página montada por JavaScript.

O motivo: sites reais mudam sem aviso, muitos proíbem a coleta, e o treino precisa funcionar sempre.

## Os exemplos executáveis

A pasta [`docs/example/`](docs/example/) tem todo o código da semana:

- `site-treino/`: o Mural Tech, feito só com a biblioteca padrão do Python.
- `scripts/`: os scripts de aula dos módulos 03 a 11.
- `pipeline/`: o projeto final, com 79 testes automatizados.
- `agendamento/`: o script que o `cron` chama, e exemplos.
- `veterano/`: `httpx` assíncrono, Playwright e Selenium, com testes.

Tudo foi executado, e as saídas citadas nos módulos vêm dessas execuções. Veja o [README da pasta](docs/example/README.md) para instalar e rodar.

É material de **consulta, não gabarito**: o exemplo serve para você ver uma solução possível quando travar, não para copiar.

## O entregável

Ao final da Semana 07, o repositório do **seu projeto** (não este aqui) deve ter um **pipeline de captura automática para o banco**: um programa que, a cada execução, lê o `robots.txt`, coleta as vagas e os eventos do site de treino, limpa os dados, grava em um banco SQLite **sem duplicar**, **inativa** o que saiu do ar, registra a execução, escreve um log e termina com um **código de saída** que um agendador entende.

```text
pipeline-coleta/
├── coleta/           ← o pacote do pipeline (python -m coleta)
├── tests/            ← os testes automatizados
├── requirements.txt
├── .gitignore        ← sem .venv/, dados/ e logs/
└── README.md         ← como instalar, ligar o site, rodar e testar
```

O checklist completo está em [docs/entregavel.md](docs/entregavel.md).

## Entregas da turma

Ainda não há entregas da Semana 07. Quer ser a primeira pessoa? Veja [como entregar](entregas/README.md).

## Versões e data de consulta

Material verificado com **Python 3.12.3**, `requests` 2.34.2, `beautifulsoup4` 4.15.0, `lxml` 6.1.3, `httpx` 0.28.1, `protego` 0.7.0, `croniter` 6.2.4, `pytest` 9.1.1, SQLite 3.45.1, Playwright 1.63.0 e Selenium 4.51.0. A documentação do BeautifulSoup, o RFC 9309 (`robots.txt`) e a documentação do Playwright foram consultados em **09/10/2026**. As bibliotecas mudam com frequência: se algo divergir do que está aqui, a documentação oficial é a referência.

**O que foi e o que não foi testado.** Todo o código foi executado em Linux, e as saídas citadas nos módulos são as reais. Foram testados o site de treino, os scripts de todos os módulos, o pipeline (79 testes), a trilha veterano (16 testes) e as expressões de agendamento. **Não foram testados** sites reais (tudo foi treinado no site fictício), o `cron` em si, o Agendador de Tarefas do Windows, o `launchd` do macOS e, em geral, o Windows e o macOS. Playwright e Selenium foram testados contra um Chromium dirigido por script, e não com o navegador que o `playwright install` baixa.

## Antes de coletar de qualquer site real

Percorra as perguntas do Módulo 03: existe API oficial? Os termos de uso permitem? O `robots.txt` permite o caminho? Há `Crawl-delay`? A página tem dados pessoais? Se qualquer resposta for "não pode" ou "não sei", **pare**. Este material não é aconselhamento jurídico.

## Como funciona

O Coffee & Code é **100% online**. Cada módulo foi escrito para ser autossuficiente: você estuda no seu ritmo, pode avançar mais rápido, voltar em semanas anteriores e consultar o material durante o projeto.

Os encontros semanais, também online, existem para tirar dúvidas, revisar conceitos, programar junto e mostrar o que você produziu, **não para dar aula**:

- **quarta-feira**: 20h00 às 21h30
- **sábado**: 10h00 às 11h30

Os dois trabalham o mesmo conteúdo. Escolha o que couber melhor na sua semana, e não precisa ficar o horário inteiro na call.

## Travou?

Chega no encontro ou no Discord com uma pergunta específica. `"o select('.vaga') devolve lista vazia, mas no navegador os cartões aparecem"` costuma ser resolvido muito mais rápido do que `"meu scraper não funciona"`.

Nesta semana, compare sempre o HTML que o `requests` recebeu com o que o navegador mostra: a diferença entre os dois resolve boa parte dos problemas.

E lembra: não saber alguma coisa não é problema. Saber pesquisar faz parte da área.

## Diagramas

Todos os diagramas usados nos módulos estão em [`docs/assets/svg/`](docs/assets/svg/), em formato SVG.

## Semanas anteriores

- [SEM 01: Kickoff & Design System](https://github.com/coffeecodepucpr/coffee-code-sem01)
- [SEM 02: Interface Web (Parte 1: Layout)](https://github.com/coffeecodepucpr/coffee-code-sem02)
- [SEM 03: Interface Web (Parte 2: Dinâmica)](https://github.com/coffeecodepucpr/coffee-code-sem03)
- [SEM 04: Modelagem de Dados](https://github.com/coffeecodepucpr/coffee-code-sem04)
- [SEM 05: API RESTful Central (Parte 1: CRUD)](https://github.com/coffeecodepucpr/coffee-code-sem05)
- [SEM 06: API RESTful Central (Parte 2: Integração)](https://github.com/coffeecodepucpr/coffee-code-sem06)

Trilha completa e próximas semanas: [perfil do Coffee & Code](https://github.com/coffeecodepucpr)

---

```text
HTTP 418: I'm a teapot
> ready to code
```
