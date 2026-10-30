# Módulo 03, Ética, Termos e robots.txt

Português · [English](../docs-eng/03-ethics-terms-and-robots-txt.md)

`SEM 07 // Data & Scraping, Parte 1: Coleta`

---

## // Antes de começar

Este módulo vem **antes** do primeiro scraper de propósito. Um programa que visita páginas pode causar problemas reais: sobrecarregar um servidor pequeno, ler áreas que o dono pediu para deixar em paz, ou juntar dados de pessoas que ninguém autorizou. Aqui você aprende a perguntar "posso?" e "como faço isso com educação?" antes de escrever qualquer linha de coleta.

> **AVISO**
> Este módulo apresenta boas práticas e noções gerais. **Não é aconselhamento jurídico.** Em caso de dúvida real (um projeto comercial, dados de pessoas, um site que você não conhece), consulte quem entende da lei.

## // O arquivo robots.txt

Quase todo site publica, no endereço `/robots.txt`, um arquivo com **pedidos para robôs**. É um texto simples, e o do Mural Tech é este (resposta real):

```
# Mural Tech (site de treino): regras para robôs
User-agent: *
Allow: /vagas/
Allow: /eventos/
Disallow: /interno/
Crawl-delay: 1

User-agent: BotAbusivo
Disallow: /
```

Leia em grupos. Cada grupo começa com `User-agent` (a quem o grupo se dirige: `*` significa "todos os outros") e continua com regras. Neste arquivo: qualquer robô pode visitar `/vagas/` e `/eventos/`, não deve visitar `/interno/`, e deve esperar 1 segundo entre pedidos. E o robô que se identifica como `BotAbusivo` não deve visitar nada.

O padrão que define esse arquivo é o **RFC 9309**, publicado em setembro de 2022 (a documentação foi consultada em 09/10/2026). Três ideias dele precisam ficar claras:

- **É um pedido, e não uma tranca.** O RFC diz expressamente que essas regras não são uma forma de autorização de acesso. O servidor não impede ninguém. Quem respeita é quem **escolhe** respeitar, e um scraper decente escolhe.
- **Não é segurança.** O próprio RFC avisa que listar um caminho no `robots.txt` o torna público e descobrível. Quem quer proteger uma área de verdade usa autenticação, e não um pedido educado.
- **O Crawl-delay não faz parte do padrão.** O RFC define só `User-agent`, `Allow` e `Disallow`, e diz que os robôs podem interpretar outros registros por conta própria. O `Crawl-delay` é um extra muito usado, e vale respeitá-lo mesmo assim.

A prova de que é só um pedido está no próprio site de treino. A página proibida (`/interno/relatorio`) **responde normalmente**:

```
a página proibida responde: 200 (o servidor não impede)
```

## // Lendo o robots.txt com Python

A biblioteca padrão do Python tem um leitor, o `urllib.robotparser`. Este script o usa para responder "posso coletar isto?":

```python
from urllib.robotparser import RobotFileParser

import requests

BASE = "http://127.0.0.1:8080"
SEU_AGENTE = "MuralColetaBot/1.0 (projeto de estudo; contato: voce@example.com)"

texto = requests.get(f"{BASE}/robots.txt", timeout=10).text

robots = RobotFileParser()
robots.parse(texto.splitlines())

for agente, caminho in [(SEU_AGENTE, "/vagas/"), (SEU_AGENTE, "/eventos/"),
                        (SEU_AGENTE, "/interno/relatorio"),
                        ("BotAbusivo/1.0", "/vagas/")]:
    pode = robots.can_fetch(agente, f"{BASE}{caminho}")
    print(f"{agente.split('/')[0]:14} {caminho:22} pode? {pode}")

print("Crawl-delay para o seu agente:", robots.crawl_delay(SEU_AGENTE))
```

```
MuralColetaBot /vagas/                pode? True
MuralColetaBot /eventos/              pode? True
MuralColetaBot /interno/relatorio     pode? False
BotAbusivo     /vagas/                pode? False
Crawl-delay para o seu agente: 1
```

(O script completo, com a impressão do arquivo, está em `03_robots.py`.) Repare que baixamos o `robots.txt` com o `requests`, e entregamos o texto ao `parse()`. O método `read()` do próprio leitor também existe, mas **não aceita um tempo limite**, e um scraper nunca deve esperar sem limite (Módulo 05). Em testes no Python 3.12.3, antes de ler qualquer regra o `can_fetch` recusa tudo, e depois do `parse()` ele passa a funcionar.

## // Quando o robots.txt falha

E se o arquivo não existir, ou o servidor der erro ao entregá-lo? O RFC responde, e o cliente de coleta desta semana segue a resposta:

| O que acontece com o `/robots.txt` | O que o RFC diz | O que o pipeline faz |
|---|---|---|
| Responde `200` | Siga as regras | Segue as regras |
| Erro `4xx`, como `404` (não existe) | "Indisponível": o robô **pode** acessar tudo | Coleta, sem restrições |
| Erro `5xx`, ou a rede falha | "Inalcançável": o robô **deve** assumir bloqueio total | **Não coleta nada** e termina com falha |

A lógica é prudente: um `404` quer dizer "este site não pediu nada", mas um erro do servidor quer dizer "não sei o que ele pede", e na dúvida não se coleta.

## // Duas armadilhas do leitor do Python

O leitor da biblioteca padrão é simples, e isso tem um preço. Dois testes reais mostram onde ele **diverge do RFC**.

**1. A ordem das linhas importa.** O RFC manda valer a regra **mais específica** (a de caminho mais longo). O exemplo do próprio RFC tem `Allow: /example/page/` seguida de `Disallow: /example/page/disallowed.gif`, e a página `.gif` deve ser **proibida**. O leitor do Python a **permite**, porque usa a primeira regra que casa. Com as duas linhas em ordem inversa, ele proíbe.

**2. Curingas não funcionam.** O RFC exige suporte a `*` (qualquer sequência) e `$` (fim do endereço). Com a regra `Disallow: /*.gif$`, o leitor do Python **não bloqueia** `/a/b.gif`.

Para sites com `robots.txt` mais elaborados, existe a biblioteca **Protego** (`pip install protego`; testada aqui na versão 0.7.0), que segue o RFC nos dois casos:

```python
from protego import Protego

regras = Protego.parse(texto_do_robots)
pode = regras.can_fetch("http://127.0.0.1:8080/vagas/", "MuralColetaBot")
espera = regras.crawl_delay("MuralColetaBot")
```

```
RFC 5.2: /example/page/disallowed.gif pode? False  (o RFC manda proibir)
curinga /*.gif$ bloqueia /a/b.gif? True
crawl_delay: 3.0
```

Atenção à **ordem dos argumentos**, que é invertida em relação ao leitor do Python: no Protego vem primeiro o endereço, e depois o agente. O robots.txt do Mural Tech é simples (sem curingas nem regras sobrepostas), então os dois leitores concordam, e o pipeline usa o da biblioteca padrão. Trocar um pelo outro é o desafio opcional do Módulo 14.

## // Além do robots.txt

O `robots.txt` é só uma das camadas. As outras importam tanto quanto:

| Camada | A pergunta | O que fazer |
|---|---|---|
| **Termos de uso** | O site permite a coleta automatizada? | Leia. Um site pode proibir a coleta nos termos, **mesmo que o robots.txt deixe**. Vale sempre a regra mais restritiva |
| **API ou arquivo de dados** | O site oferece um jeito oficial de pegar os dados? | Use-o. É mais estável, mais leve para o servidor, e é o caminho que o dono quer |
| **Dados pessoais** | A página mostra nome, e-mail ou telefone de alguém? | Colete só o necessário, ou nada. Pela Lei Geral de Proteção de Dados (LGPD, Lei nº 13.709/2018), dado pessoal é a informação relacionada a uma pessoa identificada ou identificável |
| **Direitos sobre os dados** | Posso guardar, mostrar e redistribuir o que coletei? | Ver a página ou coletá-la não dá direito a republicá-la. Verifique a licença antes de compartilhar |
| **Ritmo** | Quantos pedidos por segundo eu faço? | O `Crawl-delay` do site, ou no mínimo um pedido por segundo. Concorrência não é desculpa (Módulo 15) |
| **Identificação** | O site sabe quem eu sou? | Use um `User-Agent` honesto, com o nome do projeto e um contato |
| **Cache** | Preciso baixar isto de novo? | Não, se nada mudou (Módulo 11) |

O Mural Tech deixa ver o `User-Agent` chegar ao servidor. A página `/eco` devolve os cabeçalhos que você enviou:

```
User-Agent padrão: python-requests/2.34.2
pedido 1 pela sessão: MuralColetaBot/1.0
 (projeto de estudo; contato: voce@example.com)
```

(A saída real escreve o segundo valor em uma linha só.)

Quem recebe milhares de pedidos por dia lê esse campo. Um nome claro, com um contato, permite que o dono do site **fale com você** antes de bloquear você.

## // As perguntas, nesta ordem

<div align="center">
<img src="./assets/svg/decisao-robots.svg" alt="As perguntas a fazer antes de coletar: API oficial, termos de uso, robots.txt, Crawl-delay, dados pessoais e boas maneiras" width="640">
</div>

Antes de coletar de **qualquer site real**, percorra o desenho: existe API? Os termos permitem? O `robots.txt` permite este caminho para o seu `User-Agent`? Há `Crawl-delay`? A página tem dados pessoais? Só depois, colete com boas maneiras.

## // O que nunca fazer

> **LINHAS QUE ESTE MATERIAL NÃO ENSINA A CRUZAR**
> - Burlar **login, captcha, bloqueios de IP** ou qualquer proteção do site.
> - Disfarçar o robô de navegador comum (trocar o `User-Agent` para parecer uma pessoa) para escapar de um bloqueio.
> - Ignorar `429`, `503` e o `Retry-After`: eles são o servidor pedindo calma.
> - Coletar o que está atrás de uma área restrita.
> - Continuar depois de receber um pedido para parar. Se o dono do site pedir, **pare** e responda.

## // Bom exemplo × mau exemplo

**Mau exemplo**: um `User-Agent` falso, e nenhuma espera:

```python
cabecalhos = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
for numero in range(1, 1000):
    requests.get(f"{BASE}/vagas/?pagina={numero}", headers=cabecalhos)
```

O programa mente sobre quem é, não espera, não tem tempo limite, e pede mil páginas de uma lista que tem três.

**Bom exemplo**: identificado, devagar, e com limites:

```python
sessao = requests.Session()
sessao.headers["User-Agent"] = SEU_AGENTE
time.sleep(espera)
resposta = sessao.get(url, timeout=10)
```

## // Erros comuns

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| `can_fetch` devolve `False` para tudo | Foi chamado antes de ler as regras com `parse()` | Leia o `robots.txt` primeiro |
| Uma página "permitida" é recusada | O casamento é por **prefixo**: a regra `/busca` também barra `/buscar` | Leia as regras com cuidado, e teste |
| Uma página "proibida" é permitida | O casamento diferencia maiúsculas: `/admin/` não barra `/Admin/painel` | Teste as variações, e não confie que o site seja consistente |
| Um curinga (`*` ou `$`) é ignorado | O leitor do Python não implementa curingas | Use o Protego |
| Achar que "o servidor respondeu 200, então pode" | O `robots.txt` é um pedido, e não uma tranca | Respeite o pedido, mesmo sem ser forçado |

## // Prática guiada

1. Com o Mural Tech ligado, abra `http://127.0.0.1:8080/robots.txt` no navegador e leia cada linha.
2. Rode `03_robots.py` e confira a tabela de permissões.
3. Acesse `/interno/relatorio` no navegador: ele abre. Releia, com isso em mente, a frase "é um pedido, e não uma tranca".
4. Rode `curl http://127.0.0.1:8080/eco` e depois `curl -A "MeuColetor/1.0" http://127.0.0.1:8080/eco`, e compare o `user-agent` devolvido nos dois casos.

## // Pratique sozinho

> **DESAFIO**
> Considere este `robots.txt`, para um robô chamado `MeuBot`:
> ```
> User-agent: *
> Disallow: /admin/
> Disallow: /busca
> Crawl-delay: 5
> ```
> Para cada endereço, diga se é permitido: `/vagas/`, `/admin/painel`, `/busca?q=python`, `/buscar`, `/admin`, `/Admin/painel`. Depois confira com o `RobotFileParser`. Respostas, que os dois leitores confirmaram: permitidos são `/vagas/`, `/admin` (falta a barra final) e `/Admin/painel` (maiúscula diferente); proibidos são `/admin/painel`, `/busca?q=python` e `/buscar` (prefixo de `/busca`). O `Crawl-delay` é 5.

## // Aplicando no projeto da semana

1. Na pasta do seu projeto, copie `03_robots.py` e rode-o.
2. No `anotacoes.md`, escreva o seu `User-Agent`, com o nome do seu projeto e um e-mail seu (use um endereço de verdade, em um projeto real). Neste material, o contato é `voce@example.com`, um domínio reservado para exemplos.
3. Crie a seção "Perguntas antes de coletar" e cole as cinco perguntas do desenho. Você as usará quando for adaptar o pipeline a uma fonte real.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> O `robots.txt` de um site não pede nada contra o seu robô, mas os termos de uso dizem "é proibida a coleta automatizada de conteúdo". O que você faz?

Resposta: **não coleta**, ou pede permissão por escrito. O `robots.txt` e os termos são camadas diferentes, e vale a mais restritiva. O fato de o `robots.txt` não proibir só quer dizer que o dono não **configurou** esse pedido, e não que autorizou. E o fato de o servidor responder `200` não prova nada: ele responderia a qualquer um.

## // Resumo do módulo

- [ ] Sei ler um `robots.txt`: grupos, `User-agent`, `Allow`, `Disallow` e `Crawl-delay`.
- [ ] Sei que ele é um pedido, e não uma tranca, e que não é um recurso de segurança.
- [ ] Sei o que fazer quando ele dá `404` e quando dá `5xx`.
- [ ] Sei que o leitor da biblioteca padrão diverge do RFC (ordem das linhas e curingas).
- [ ] Sei as outras camadas: termos de uso, API, dados pessoais, ritmo, identificação e cache.
- [ ] Sei as linhas que não se cruzam, e identifico um robô com um `User-Agent` honesto.

---

**Próximo módulo:** `04-python-essencial-para-coleta.md`, com as regras claras, falta preparar a ferramenta: o ambiente Python e o essencial da linguagem.

`Material de Estudo // Coffee & Code`
