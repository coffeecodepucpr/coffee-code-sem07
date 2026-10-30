# Módulo 09, O Segundo Scraper: Eventos

Português · [English](../docs-eng/09-the-second-scraper-events.md)

`SEM 07 // Data & Scraping, Parte 1: Coleta`

---

## // Antes de começar

Você tem um scraper de vagas, funcionando, com limpeza. Este módulo coleta uma **segunda fonte**, os eventos de tecnologia, e serve para mostrar o que um projeto bem organizado ganha: quase tudo o que você construiu é **reaproveitado**, e só o que é realmente específico dos eventos precisa ser escrito.

## // O plano de campos dos eventos

Antes de qualquer código, o plano (Módulo 02). Cada evento da página `/eventos/` é um item de lista (`li.evento`). Este é um trecho real:

```html
<li class="evento" data-id="e001">
  <h3><a href="/eventos/e001">Python Day Curitiba</a></h3>
  <p class="quando">sábado, 17 de outubro de 2026, 14h00</p>
  <p class="onde">Curitiba, PR</p>
  <p class="preco">Gratuito</p>
  <p class="organizacao">Comunidade Py Sul</p>
</li>
```

| Campo | Seletor | Exemplo | Limpeza (Módulo 08) |
|---|---|---|---|
| id | `data-id` do `li.evento` | `e001` | nenhuma |
| título | `h3 a` | `Python Day Curitiba` | `limpar_texto` |
| quando | `.quando` | `sábado, 17 de outubro de 2026, 14h00` | `parse_data_evento` |
| onde | `.onde` | `Curitiba, PR` ou `Online` | `limpar_texto`, e `online` se for `Online` |
| preço | `.preco` | `R$ 120,00 (estudantes: R$ 60,00)` | `parse_preco` |
| organização | `.organizacao` | `Comunidade Py Sul` | `limpar_texto` |
| link | `href` do `h3 a` | `/eventos/e001` | `urljoin` |

## // O que muda, e o que fica igual

| Etapa | Vagas | Eventos |
|---|---|---|
| Baixar a página | `baixar()` do Módulo 05 | **igual** |
| Ler o HTML | `ler_html()` | **igual** |
| Texto limpo e dinheiro | `limpar_texto`, `para_centavos` | **igual** |
| Paginação | 3 páginas, seguindo o link Próxima | **não existe**: é uma página só |
| Página de detalhe | 20 páginas, uma por vaga | **não visitamos** (a lista basta) |
| Seletores | `article.vaga` | `li.evento` (**novo**) |
| Datas | `<time datetime>` (já ISO) | texto longo em português (**novo**: `parse_data_evento`) |
| Molde | `Vaga` | `Evento` (**novo**) |

Quase tudo é reaproveitado. O que é novo cabe em **uma função de leitura** e **um molde**.

## // A leitura dos eventos

Esta é a função nova, no `parsers.py`:

```python
def ler_eventos(sopa, url_pagina: str) -> list[dict]:
    eventos = []
    for item in sopa.select("li.evento"):
        link = item.select_one("h3 a")
        eventos.append({
            "id_externo": item["data-id"],
            "titulo": texto(link),
            "quando": texto(item.select_one(".quando")),
            "onde": texto(item.select_one(".onde")),
            "preco": texto(item.select_one(".preco")),
            "organizacao": texto(item.select_one(".organizacao")),
            "url": (urljoin(url_pagina, link["href"])
                    if link is not None else None),
        })
    return eventos
```

E este é o script (`09_eventos.py`) que a usa, junto das funções de limpeza que você já tem:

```python
import requests

from limpeza import limpar_texto, parse_data_evento, parse_preco
from parsers import ler_eventos, ler_html

BASE = "http://127.0.0.1:8080"
url = f"{BASE}/eventos/"
sopa = ler_html(requests.get(url, timeout=10))

eventos = []
for bruto in ler_eventos(sopa, url):
    preco, preco_estudante = parse_preco(bruto["preco"])
    onde = limpar_texto(bruto["onde"])
    eventos.append({
        "id": bruto["id_externo"],
        "titulo": bruto["titulo"],
        "inicio": parse_data_evento(bruto["quando"]),
        "local": onde,
        "online": (onde or "").lower() == "online",
        "preco_centavos": preco,
        "preco_estudante_centavos": preco_estudante,
    })

print("eventos coletados:", len(eventos))
for e in eventos[:3]:
    print(e)
print("online:", [e["id"] for e in eventos if e["online"]])
print("gratuitos:", [e["id"] for e in eventos if e["preco_centavos"] == 0])
print("sem data:", [e["id"] for e in eventos if e["inicio"] is None])
```

```
eventos coletados: 8
{'id': 'e001', 'titulo': 'Python Day Curitiba', 'inicio': '2026-10-17T14:00',
 'local': 'Curitiba, PR', 'online': False, 'preco_centavos': 0,
 'preco_estudante_centavos': None}
{'id': 'e002', 'titulo': 'Meetup de Dados', 'inicio': '2026-10-22T19:30',
 'local': 'Online', 'online': True, 'preco_centavos': 0,
 'preco_estudante_centavos': None}
{'id': 'e003', 'titulo': 'Workshop de Docker na Prática',
 'inicio': '2026-10-24T09:00', 'local': 'Curitiba, PR', 'online': False,
 'preco_centavos': 4000, 'preco_estudante_centavos': None}
online: ['e002', 'e006', 'e007']
gratuitos: ['e001', 'e002', 'e005', 'e006', 'e008']
sem data: []
```

(A saída real escreve cada dicionário em uma única linha, e foi quebrada aqui para caber na página.)

Repare em dois detalhes. **Gratuito vale 0, e não None**: o evento tem preço, e é zero (Módulo 08). E o campo `online` é uma **decisão de limpeza**: a página só diz `Online` no lugar do local, e o nosso dado precisa de um campo próprio para poder responder "quais eventos são online?".

## // Datas que não dão certo

O evento com a data impossível não derruba nada. No `coletores.py`, o coletor de eventos **guarda o evento mesmo sem data legível, e registra um erro**:

```python
        inicio = limpeza.parse_data_evento(bruto["quando"])
        if inicio is None:              # guarda o evento, mas avisa
            resultado.erros.append(
                f"evento sem data legível: {bruto['id_externo']}")
```

É a mesma filosofia do resto da semana: **não perder o dado** que veio, e **não esconder o problema**. Um evento sem data ainda é útil (tem título e link), e o erro registrado avisa que a data precisa de atenção. Um teste automatizado confere esse comportamento, usando uma página de eventos falsa com uma data impossível.

## // Duas fontes, um jeito de trabalhar

O que você acabou de fazer é o padrão de qualquer projeto de coleta que cresce:

1. **Plano de campos** da fonte nova.
2. **Uma função de leitura** (HTML para dicionários de texto bruto).
3. **A limpeza**, reaproveitando o que existe, e acrescentando só o que é novo.
4. **Um molde** para o dado limpo.

Uma terceira fonte seguiria os mesmos quatro passos. Se, em vez disso, você tivesse **copiado e colado** o scraper de vagas e mudado o que precisava, cada correção (como a da data impossível) teria que ser feita duas vezes, e logo as duas cópias seriam diferentes.

## // Bom exemplo × mau exemplo

**Mau exemplo**: copiar o scraper de vagas inteiro e editar:

```python
# coletar_eventos.py: 90% igual ao coletar_vagas.py
```

**Bom exemplo**: funções pequenas e compartilhadas (`baixar`, `ler_html`, `limpar_texto`), e só o que é diferente em arquivos próprios (`ler_eventos`, `Evento`).

## // Erros comuns

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| `inicio: None` em todos os eventos | O texto da data mudou de formato | Compare com o HTML real, e ajuste `_DATA_LONGA` |
| Um mês não é reconhecido (`março`) | O nome tem acento, e a tabela `MESES` não | Confira a grafia em `MESES`; `\w` já aceita acentos |
| Um evento "Online" aparece com cidade | O texto é `Online` com outra grafia | Compare em minúsculas: `onde.lower() == "online"` |
| O preço de estudante não aparece | O texto tem só um valor | O segundo valor é `None`, e é o esperado |
| Confiar no dia da semana do texto | O site pode errá-lo | Use só dia, mês, ano e hora |

## // Prática guiada

1. Abra `/eventos/` no navegador e leia o HTML de um evento com `Ctrl+U`.
2. Rode `09_eventos.py` e compare a saída com a página.
3. Em `servidor.py`, ligue o dia 2 (`/_dev/dia/2`) e rode de novo: dois eventos novos aparecem (`e009` e `e010`).
4. Edite o HTML do site (ou use uma cópia) para que um evento tenha a data `30 de fevereiro` e rode o script: o que aparece em `sem data`?

## // Pratique sozinho

> **DESAFIO**
> A partir da lista de eventos, imprima os que acontecem **em fim de semana**. Dica: `datetime.date.fromisoformat(inicio[:10]).weekday()` devolve de 0 (segunda) a 6 (domingo), e fim de semana é 5 ou 6. Resultado esperado no dia 1: `e001`, `e003`, `e005` e `e007`.

## // Aplicando no projeto da semana

1. Na pasta do projeto, acrescente `ler_eventos` ao `parsers.py` e o dataclass `Evento` ao `modelos.py`.
2. Crie o `coletar_eventos.py`, que monte uma lista de `Evento` com a limpeza.
3. Imprima os eventos online e os gratuitos, e confira com a página.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> Uma terceira fonte aparece: um site de cursos, com paginação e detalhe, como as vagas, mas com datas no formato `17/10/2026`. Quais partes do seu código você reaproveita, e quais escreve?

Resposta: reaproveita `baixar`, `ler_html`, `limpar_texto`, `para_centavos`, o laço de paginação do Módulo 07 e a ideia de validar o registro. Escreve **a função de leitura** (os seletores do site novo), **uma função de data** para o formato `17/10/2026` (bem mais simples que a dos eventos), e **um molde** para os cursos. É esse o ganho de um projeto organizado: a quantidade de código novo é proporcional ao que é realmente novo.

## // Resumo do módulo

- [ ] Sei fazer o plano de campos de uma fonte nova.
- [ ] Sei separar o que é reaproveitado do que é específico da fonte.
- [ ] Sei ler uma lista de eventos e limpar datas em português e preços.
- [ ] Sei que gratuito é `0`, e não `None`, e que `online` é uma decisão de limpeza.
- [ ] Sei guardar um registro com dado ruim, **avisando**, em vez de perdê-lo ou escondê-lo.
- [ ] Sei por que não copiar e colar um scraper.

---

**Próximo módulo:** `10-sqlite-guardando-os-dados.md`, os dados estão limpos. Falta guardá-los, sem duplicar.

`Material de Estudo // Coffee & Code`
