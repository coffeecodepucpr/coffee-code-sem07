# Módulo 08, Limpando e Normalizando

Português · [English](../docs-eng/08-cleaning-and-normalizing.md)

`SEM 07 // Data & Scraping, Parte 1: Coleta`

---

## // Antes de começar

No Módulo 07, você coletou 20 vagas, e cada campo é um **texto**: o salário é `R$ 7.000 a R$ 9.500`, e não dois números; a data é um texto, e não uma data. Um banco de dados, porém, quer números e datas de verdade, para poder ordenar, somar e comparar. Este módulo ensina a ponte entre os dois mundos: a **limpeza** (ou normalização), que transforma o texto da página em dado utilizável.

## // Texto não é dado

Veja o que o scraper entrega, e o que o banco precisa:

| Campo | O que a página mostra | O que o banco precisa |
|---|---|---|
| Salário | `R$ 7.000 a R$ 9.500` | Um mínimo e um máximo, em números |
| Salário | `A combinar` | "Não informado", e não um número |
| Salário | `até R$ 11.000` | Só o máximo |
| Local | `Curitiba, PR` | A cidade e o estado, separados |
| Data do evento | `sábado, 17 de outubro de 2026, 14h00` | Uma data e hora padronizadas |
| Preço | `R$ 120,00 (estudantes: R$ 60,00)` | Dois valores |
| Texto livre | `  Dev   Python \n Júnior ` | `Dev Python Júnior` |

## // Três decisões de modelagem

Antes de escrever as funções, três decisões, que valem para qualquer projeto de dados.

**1. Dinheiro em centavos, como número inteiro.** Números decimais (`float`) erram em contas simples, e no Brasil há uma armadilha extra, o ponto como separador de milhar:

```
0.1 + 0.2 = 0.30000000000000004
float('7.000') = 7.0         (em português, 7.000 é sete mil)
float('3.200,50') -> ValueError: could not convert string to float: '3.200,50'
```

Guardar `R$ 7.000` como `700000` (centavos, inteiro) elimina os dois problemas.

**2. Datas no formato ISO 8601**, como `2026-10-17T14:00`. É o padrão internacional (ano, mês, dia, hora), e tem uma vantagem prática: **ordena corretamente como texto**, e o SQLite e o Python o entendem.

**3. Ausente é None, e não zero.** Um salário "A combinar" **não é** zero reais: é uma informação que falta. Um evento "Gratuito" **é** zero reais. Misturar os dois estraga qualquer média. A regra: `None` quer dizer "não sei", e `0` quer dizer "é zero".

## // As funções de limpeza

Todas ficam em um arquivo só, o `limpeza.py`, e **não sabem nada** de HTML, de rede ou de banco: recebem um texto e devolvem um valor. Isso as torna fáceis de testar.

**Texto limpo.** Tira espaços repetidos e quebras de linha, e transforma vazio em `None`:

```python
def limpar_texto(texto: str | None) -> str | None:
    """Tira espaços repetidos e quebras de linha. Vazio vira None."""
    if texto is None:
        return None
    limpo = " ".join(texto.split())
    return limpo or None
```

**Dinheiro para centavos.** Usa `Decimal`, que faz contas decimais exatas, e tira o ponto de milhar e troca a vírgula decimal:

```python
def para_centavos(valor: str) -> int:
    """'7.000' vira 700000 e '3.200,50' vira 320050 (inteiros, sem float)."""
    numero = Decimal(valor.replace(".", "").replace(",", "."))
    return int(numero * 100)
```

**A faixa salarial.** Procura os valores `R$ ...` com uma expressão regular, e decide o que fazer conforme quantos achou:

```python
def parse_faixa_salarial(texto: str | None) -> tuple[int | None, int | None]:
    """Devolve (mínimo, máximo) em centavos. Sem valor: (None, None)."""
    if not texto:
        return (None, None)
    valores = [para_centavos(v) for v in _DINHEIRO.findall(texto)]
    if not valores:
        return (None, None)
    if len(valores) == 1:
        if texto.strip().lower().startswith("até"):
            return (None, valores[0])
        return (valores[0], valores[0])
    return (min(valores), max(valores))
```

**O local, a data e o preço:**

```python
def parse_local(texto: str | None) -> tuple[str | None, str | None]:
    """'Curitiba, PR' vira ('Curitiba', 'PR'). 'Remoto' vira (None, None)."""
    texto = limpar_texto(texto)
    if not texto or "," not in texto:
        return (None, None)
    cidade, uf = (parte.strip() for parte in texto.rsplit(",", 1))
    return (cidade, uf.upper())


def parse_data_evento(texto: str | None) -> str | None:
    """'sábado, 17 de outubro de 2026, 14h00' vira '2026-10-17T14:00'."""
    achou = _DATA_LONGA.search(texto or "")
    if not achou:
        return None
    dia, mes, ano, hora, minuto = achou.groups()
    numero_mes = MESES.get(mes.lower())
    if numero_mes is None:
        return None
    try:
        momento = datetime(int(ano), numero_mes, int(dia), int(hora), int(minuto))
    except ValueError:                  # 30 de fevereiro, 25h00...
        return None
    return momento.isoformat(timespec="minutes")


def parse_preco(texto: str | None) -> tuple[int | None, int | None]:
    """Devolve (preço, preço para estudantes) em centavos. 'Gratuito' vale 0."""
    texto = limpar_texto(texto) or ""
    if texto.lower().startswith("gratuito"):
        return (0, None)
    valores = [para_centavos(v) for v in _DINHEIRO.findall(texto)]
    if not valores:
        return (None, None)
    return (valores[0], valores[1] if len(valores) > 1 else None)
```

Os nomes dos meses (`MESES`) e as expressões regulares (`_DINHEIRO` e `_DATA_LONGA`) ficam no início do arquivo. Repare que `parse_data_evento` **ignora o dia da semana** (`sábado`) e usa só os números: o dia da semana é redundante, e um site pode errá-lo.

Este script (`08_demo_limpeza.py`) aplica as funções a exemplos reais, e a saída é a real:

```
--- salários (em centavos)
'R$ 7.000 a R$ 9.500'      -> (700000, 950000)
'R$ 4.500'                 -> (450000, 450000)
'R$ 3.200,50'              -> (320050, 320050)
'até R$ 11.000'            -> (None, 1100000)
'A combinar'               -> (None, None)
--- locais
'Curitiba, PR'               -> ('Curitiba', 'PR')
'São José dos Pinhais, PR'   -> ('São José dos Pinhais', 'PR')
'Remoto'                     -> (None, None)
'Online'                     -> (None, None)
--- datas dos eventos
'sábado, 17 de outubro de 2026, 14h00'         -> 2026-10-17T14:00
'sexta-feira, 6 de novembro de 2026, 08h30'    -> 2026-11-06T08:30
'data a confirmar'                             -> None
--- preços (em centavos)
'Gratuito'                             -> (0, None)
'R$ 40,00'                             -> (4000, None)
'R$ 120,00 (estudantes: R$ 60,00)'     -> (12000, 6000)
--- espaços e quebras de linha
'Dev Python Júnior'
```

## // Datas impossíveis e valores estranhos

A web real está cheia de dados esquisitos, e uma função de limpeza **nunca deve derrubar o programa** por causa de um valor feio. Veja o que o Python faz com uma data como "30 de fevereiro", ou "25h00":

```
ValueError: day is out of range for month
ValueError: hour must be in 0..23
```

Por isso `parse_data_evento` envolve a criação da data em um `try/except` e devolve `None`: o evento será guardado **sem data**, e o scraper registrará um aviso (você o verá no Módulo 09). O mesmo cuidado vale para os valores em dinheiro: o texto `R$ .` faria o `Decimal` levantar `InvalidOperation`, e a expressão regular exige um dígito logo no começo do número para que isso nunca aconteça.

## // O molde dos dados

Depois de limpos, os campos de uma vaga vão para um **dataclass**, um molde com campos nomeados e tipos (Módulo 04). É o arquivo `modelos.py`:

```python
@dataclass
class Vaga:
    fonte: str
    id_externo: str
    titulo: str
    url: str
    empresa: str | None = None
    cidade: str | None = None
    uf: str | None = None
    modalidade: str | None = None
    nivel: str | None = None
    salario_min: int | None = None
    salario_max: int | None = None
    publicada: str | None = None
    tags: list[str] = field(default_factory=list)
    descricao: str | None = None
    # campos que não deu para ler hoje (diferente de "a página não tem")
    indisponiveis: tuple[str, ...] = ()

    def como_linha(self) -> dict:
        linha = {k: v for k, v in self.__dict__.items()
                 if k not in ("fonte", "id_externo", "indisponiveis")}
        linha["tags"] = ",".join(self.tags)
        return linha

    def conteudo_hash(self) -> str:
        return _hash(self.como_linha())
```

Dois métodos merecem atenção. O `como_linha()` devolve os campos como um dicionário pronto para o banco (as tags viram um texto separado por vírgulas). O `conteudo_hash()` calcula uma **impressão digital** do conteúdo: se qualquer campo mudar, o resultado muda. No Módulo 10, é com ela que o pipeline descobre se uma vaga **mudou** desde a última coleta.

Há ainda o campo `indisponiveis`, que não vai para o banco: ele lista os campos que **não deu para ler hoje** (por exemplo, a descrição, se a página de detalhe falhou). É a diferença entre "a página não tem descrição" e "não consegui buscar a descrição agora": o Módulo 10 mostra o que o banco faz com isso.

## // Validando: o que fazer com um registro ruim

Nem todo registro merece ir para o banco. Uma vaga sem título e sem endereço não serve. A função `montar_vaga` (do arquivo `coletores.py`) decide:

```python
def montar_vaga(bruto: dict, descricao: str | None,
                indisponiveis: tuple[str, ...] = ()) -> Vaga | None:
    titulo = limpeza.limpar_texto(bruto["titulo"])
    if not titulo or not bruto["url"]:
        return None
    cidade, uf = limpeza.parse_local(bruto["local"])
    minimo, maximo = limpeza.parse_faixa_salarial(bruto["salario"])
    return Vaga(
        fonte=FONTE, id_externo=bruto["id_externo"], titulo=titulo,
        url=bruto["url"], empresa=limpeza.limpar_texto(bruto["empresa"]),
        cidade=cidade, uf=uf,
        modalidade=limpeza.limpar_texto(bruto["modalidade"]),
        nivel=limpeza.limpar_texto(bruto["nivel"]),
        salario_min=minimo, salario_max=maximo, publicada=bruto["publicada"],
        tags=[t.lower() for t in bruto["tags"]], descricao=descricao,
        indisponiveis=indisponiveis,
    )
```

Se faltar o título ou o endereço, ela devolve `None`, e o coletor **registra um erro** e segue em frente, em vez de gravar lixo ou parar tudo. Mas ele também marca a coleta como **incompleta**: a vaga existe no site, só não deu para reconhecê-la, e o Módulo 10 explica por que isso importa.

## // Testando a limpeza

Funções que só recebem texto e devolvem valores são o melhor terreno para **testes automatizados**: você lista as entradas e as saídas esperadas, e o `pytest` confere todas de uma vez. Este é um trecho do arquivo `tests/test_limpeza.py`:

```python
@pytest.mark.parametrize("texto, esperado", [
    ("R$ 7.000 a R$ 9.500", (700000, 950000)),
    ("R$ 4.500", (450000, 450000)),
    ("R$ 3.200,50", (320050, 320050)),
    ("até R$ 11.000", (None, 1100000)),
    ("A combinar", (None, None)),
    ("R$ .", (None, None)),
    ("", (None, None)),
    (None, (None, None)),
])
def test_faixa_salarial(texto, esperado):
    assert limpeza.parse_faixa_salarial(texto) == esperado
```

```
pytest tests/test_limpeza.py
29 passed
```

Cada linha da lista é um caso de teste. Quando você descobre um caso novo que quebra o código (como a data impossível), **acrescenta uma linha**, corrige a função, e o caso nunca mais volta a quebrar sem que alguém perceba.

## // Bom exemplo × mau exemplo

**Mau exemplo**: guardar o dinheiro como texto, ou como decimal, e `A combinar` como zero:

```python
# e se o texto for "A combinar"?
salario = float(texto.replace("R$", "").replace(".", ""))
```

**Bom exemplo**: converter para centavos inteiros, e devolver `None` quando não há valor:

```python
minimo, maximo = parse_faixa_salarial(texto)
```

## // Erros comuns

Estas mensagens foram obtidas ao executar o código.

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| `float("7.000")` dá `7.0` | Em português o ponto é o separador de milhar, e o Python o lê como decimal | Tire os pontos antes de converter (`para_centavos`) |
| `ValueError: could not convert string to float: '3.200,50'` | A vírgula decimal não é entendida pelo Python | Troque a vírgula por ponto, depois de tirar o milhar |
| `ValueError: day is out of range for month` | Uma data que não existe | Envolva a criação da data em `try/except` |
| `decimal.InvalidOperation` | Tentou converter um texto vazio ou sem dígitos em `Decimal` | Exija um dígito na expressão regular |
| Médias de salário estranhas | `A combinar` foi gravado como zero | Use `None` para "não informado" |

## // Prática guiada

1. Rode `08_demo_limpeza.py` e confira cada linha da saída com a tabela do começo do módulo.
2. Copie o `limpeza.py` para a pasta do seu projeto.
3. Rode `pytest tests/test_limpeza.py` (instale o `pytest` com `pip install pytest`) e veja os 29 testes passarem.
4. **Quebre de propósito**: em `para_centavos`, troque `* 100` por `* 10`. Rode os testes: quais falham? Depois desfaça.

## // Pratique sozinho

> **DESAFIO**
> Escreva a função `parse_modalidade(texto)` que devolve `remoto`, `hibrido` ou `presencial` (minúsculo e **sem acento**) a partir de `Remoto`, `Híbrido` ou `Presencial`, e `None` para qualquer outra coisa. Dica: `unicodedata.normalize("NFD", texto)` separa a letra do acento, e você pode descartar os caracteres de categoria `Mn`. Escreva também os testes com `parametrize`: `"Híbrido"` deve dar `hibrido`, e `"Outra coisa"` deve dar `None`.

## // Aplicando no projeto da semana

1. Na pasta do projeto, coloque o `limpeza.py` e o `modelos.py`.
2. Altere o seu `coletar_vagas.py` para limpar cada vaga e montar um `Vaga` antes de gravar. Imprima as 3 primeiras.
3. Confira, no `vagas.json` novo, que o salário agora é número (em centavos), e não texto.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> Um dia, o site passa a escrever os salários como `R$ 7 mil a R$ 9,5 mil`. O que acontece com `parse_faixa_salarial`, e como você ficaria sabendo?

Resposta: a expressão regular não acha nenhum `R$ 7.000` (o formato é outro), a função devolve `(None, None)` para **todas** as vagas, e o programa continua rodando, sem nenhum erro. É o mesmo problema do Módulo 06: tratar a ausência evita quebras, mas **esconde mudanças no site**. Você só ficaria sabendo contando os campos vazios: se 100% dos salários virarem `None` de uma hora para outra, algo mudou. O Módulo 11 transforma essa conta em alarme.

## // Resumo do módulo

- [ ] Sei por que o texto da página não serve como dado, e converto para tipos de verdade.
- [ ] Sei guardar dinheiro em centavos inteiros, e por que não usar `float`.
- [ ] Sei usar datas ISO 8601, e sei que ausente é `None`, e não zero.
- [ ] Sei escrever funções de limpeza que **nunca derrubam** o programa.
- [ ] Sei usar um dataclass como molde, e sei o que é a impressão digital do conteúdo.
- [ ] Sei testar a limpeza com `pytest` e `parametrize`.

---

**Próximo módulo:** `09-o-segundo-scraper-eventos.md`, uma fonte já funciona. Agora a segunda, reaproveitando o que você construiu.

`Material de Estudo // Coffee & Code`
