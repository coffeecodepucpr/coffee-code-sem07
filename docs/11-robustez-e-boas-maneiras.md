# Módulo 11, Robustez e Boas Maneiras

Português · [English](../docs-eng/11-robustness-and-good-manners.md)

`SEM 07 // Data & Scraping, Parte 1: Coleta`

---

## // Antes de começar

Até aqui, o scraper funciona **quando tudo dá certo**. Na web, nem tudo dá certo: servidores caem por um minuto, pedem calma, mudam o HTML. Um scraper que roda sozinho, de madrugada, precisa **aguentar isso sem ninguém por perto**. Este módulo ensina quatro defesas: tentar de novo, esperar quando o servidor pede, não baixar o que não mudou, e perceber quando o site mudou.

## // Tentar de novo, esperando cada vez mais

<div align="center">
<img src="./assets/svg/retry-com-espera.svg" alt="Três tentativas, com esperas crescentes de 0,5 e 1 segundo entre elas, e as regras de quando repetir e quando não repetir" width="640">
</div>

Alguns erros **passam sozinhos**: um `503` (o servidor está indisponível agora) costuma sumir em segundos. Para esses, vale **tentar de novo**. Mas com duas regras: esperar entre as tentativas, e esperar **cada vez mais** (o dobro a cada vez), para não martelar um servidor que já está com dificuldade. Este script (`11_a_tentativas.py`) tenta um endereço que falha duas vezes e depois funciona:

```python
def baixar_com_tentativas(url, tentativas=4, base=0.5):
    for numero in range(1, tentativas + 1):
        inicio = time.perf_counter()
        resposta = requests.get(url, timeout=10)
        gasto = time.perf_counter() - inicio
        print(f"tentativa {numero}: HTTP {resposta.status_code} ({gasto:.2f} s)")
        if resposta.status_code < 500:
            return resposta
        if numero < tentativas:
            espera = base * 2 ** (numero - 1)
            print(f"   servidor indisponível: esperando {espera} s")
            time.sleep(espera)
    raise RuntimeError(f"{url}: sem sucesso em {tentativas} tentativas")
```

```
tentativa 1: HTTP 503 (0.00 s)
   servidor indisponível: esperando 0.5 s
tentativa 2: HTTP 503 (0.00 s)
   servidor indisponível: esperando 1.0 s
tentativa 3: HTTP 200 (0.00 s)
deu certo: 200 | bytes: 4122
```

A espera foi `0.5`, depois `1.0`: é a base, multiplicada por 2 elevado ao número da tentativa menos 1 (a conta está no código). E há um **número máximo de tentativas**. Com um endereço que falha cinco vezes e `tentativas=4`, o resultado real é:

```
tentativa 4: HTTP 503 (0.00 s)
RuntimeError: ...sem sucesso em 4 tentativas
```

depois de 3,5 segundos de espera (0,5 + 1 + 2). Sem esse teto, um servidor fora do ar prenderia o seu programa para sempre.

### O que repetir, e o que não repetir

| Repita | Não repita |
|---|---|
| Erro de rede e `Timeout` | `404`: a página não existe, e continuará não existindo |
| `429` (pedidos demais) | `403`: o acesso foi negado |
| `502`, `503` e `504` (o servidor está com problema) | Qualquer erro que se repetiria igual |

## // Quando o servidor diz quanto esperar

Um servidor educado diz **quanto** esperar, no cabeçalho `Retry-After`. O Mural Tech tem uma página que aceita só 3 pedidos a cada 5 segundos (`/limitado/vagas`). O script `11_b_retry_after.py` pede cinco vezes:

```python
for numero in range(1, 6):
    resposta = requests.get(f"{BASE}/limitado/vagas", timeout=10)
    print(f"pedido {numero}: HTTP {resposta.status_code}")
    if resposta.status_code == 429:
        pedido = float(resposta.headers["Retry-After"])
        print(f"   o servidor pediu {pedido:.0f} s: eu espero esse tempo")
        time.sleep(pedido)
```

```
pedido 1: HTTP 200
pedido 2: HTTP 200
pedido 3: HTTP 200
pedido 4: HTTP 429
   o servidor pediu 5 s: eu espero esse tempo
pedido 5: HTTP 200
```

O quarto pedido levou `429`, o servidor pediu 5 segundos, o programa esperou, e o quinto funcionou. **Obedecer o Retry-After é melhor do que adivinhar**: o servidor sabe quando vai liberar.

## // O cliente do pipeline

O cliente que o pipeline usa, no arquivo `http.py`, junta tudo isto: as regras do `robots.txt` (Módulo 03), a espera entre pedidos, o `timeout`, as tentativas, o `Retry-After` e o teto. O método `obter` é o coração dele:

```python
    def obter(self, url: str, params: dict | None = None) -> requests.Response:
        if not self.pode(url):
            raise BloqueadoPorRobots(f"o robots.txt não permite: {url}")
        motivo = "sem resposta"
        total = self.config.max_tentativas
        for tentativa in range(1, total + 1):
            self._respeitar_espera()
            retry_after = None
            try:
                resposta = self.sessao.get(
                    url, params=params, timeout=self.config.timeout
                )
            except (requests.Timeout, requests.ConnectionError) as erro:
                motivo = type(erro).__name__
            else:
                self.pedidos += 1
                codigo = resposta.status_code
                if codigo not in STATUS_REPETIVEIS:
                    if codigo >= 400:
                        raise ErroDeColeta(f"{url}: HTTP {codigo}")
                    return resposta
                motivo = f"HTTP {codigo}"
                retry_after = resposta.headers.get("Retry-After")
            if tentativa < total:
                espera = self._espera_da_tentativa(tentativa, retry_after)
                self.repeticoes += 1
                log.warning("%s em %s: tentativa %d de %d, esperando %.1fs",
                            motivo, url, tentativa, total, espera)
                self.dormir(espera)
        raise ErroDeColeta(f"{url}: {motivo} depois de {total} tentativas")
```

E o cálculo da espera de cada tentativa:

```python
    def _espera_da_tentativa(self, tentativa: int, retry_after) -> float:
        base = min(self.config.espera_maxima,
                   self.config.espera_base * 2 ** (tentativa - 1))
        espera = base + random.uniform(0, base * 0.1)
        try:
            pedido = float(retry_after)
        except (TypeError, ValueError):
            return espera
        return max(espera, min(pedido, self.config.espera_maxima))
```

Leia com calma, porque cada linha é uma das lições deste módulo:

- A conta `espera_base`, vezes 2 elevado a `tentativa - 1`: a espera dobra (0,5 s, 1 s, 2 s, 4 s...).
- `min(self.config.espera_maxima, ...)`: **nunca** passa de 30 segundos.
- `random.uniform(0, base * 0.1)`: uma pequena **variação aleatória**, para que vários programas que falharam juntos não tentem de novo exatamente juntos.
- `max(espera, min(pedido, ...))`: se o servidor pediu um tempo (`Retry-After`), vale o **maior** entre o pedido e o cálculo, limitado ao máximo.
- Um `Retry-After` que não é um número (o padrão HTTP admite uma data) é **ignorado**, e vale o cálculo próprio. Um teste automatizado confere isso.
- `404` e outros erros que se repetiriam levantam `ErroDeColeta` **na hora**, sem tentar de novo.

> **E A BIBLIOTECA PRONTA?**
> O `requests` também pode repetir sozinho, com a classe `Retry` do `urllib3`, montada em uma sessão. Rodando contra o mesmo endereço instável: `status final: 200 | repeticoes feitas: 2 | [503, 503]`. Ela serve bem para o caso simples. Este material escreve o laço à mão porque, assim, cada decisão (o teto, o `Retry-After`, o registro no log) fica visível e testável.

## // Perguntar "mudou?" antes de baixar

Baixar de novo uma página que **não mudou** é desperdício, para você e para o servidor. O HTTP resolve isso com a `ETag`, a impressão digital da página (Módulo 01). Você guarda a `ETag` da última vez e a manda de volta no cabeçalho `If-None-Match`. Se a página não mudou, o servidor responde `304` **sem corpo**. O script `11_c_condicional.py` mostra:

```
1ª vez: 200 | bytes recebidos: 4122
ETag guardada: "d3aa7cdebab346b2"
2ª vez: 304 | bytes recebidos: 0
página 2 tem outra ETag: True
no dia seguinte: 200 | bytes recebidos: 4103
```

Na segunda vez, **zero bytes**: o servidor só confirmou que nada mudou. E, no dia seguinte (quando o conteúdo mudou), a página veio inteira de novo. Esse recurso exige que o **servidor** o ofereça, e um scraper que o use precisa **guardar a página anterior** (ou os dados dela), porque um `304` não traz conteúdo. Por isso o pipeline desta semana, que sempre relê tudo para saber o que sumiu, não o usa, e ele fica como técnica para coletas grandes.

## // Perceber que o site mudou

No Módulo 06, você viu que tratar campos ausentes evita quebras, mas **esconde mudanças no site**. A defesa é **contar**: se uma grande parte dos campos vier vazia, algo mudou. O script `11_d_campos_vazios.py` implementa o alarme, com um limite de 30%:

```python
def conferir(vagas, campo):
    vazios = sum(1 for v in vagas if not v[campo])
    proporcao = vazios / len(vagas)
    estado = "ALARME" if proporcao > LIMITE else "ok"
    print(f"{campo}: {vazios} de {len(vagas)} vazios ({proporcao:.0%}) "
          f"-> {estado}")
```

Rodado com o seletor certo e depois com um seletor "velho" (o site renomeou a classe), o resultado real é:

```
seletor certo (.salario):
salario: 0 de 8 vazios (0%) -> ok
o site mudou o nome da classe para .remuneracao, e o seletor ficou velho:
salario: 8 de 8 vazios (100%) -> ALARME
```

É assim que você descobre, em um dia, o que de outro modo levaria semanas: os dados continuam chegando, sem erro, mas **vazios**. Em um pipeline real, o alarme viraria um aviso no log e um status `parcial` na execução.

## // Isolar as falhas

Uma página que falha **não pode derrubar a coleta inteira**. Veja como o coletor de vagas (`coletores.py`) trata uma falha no **detalhe** de uma vaga, em comparação com uma falha em uma **página da lista**:

| Onde falha | O que o coletor faz | Por quê |
|---|---|---|
| O detalhe de **uma** vaga | Registra o erro, guarda a vaga e **preserva a última descrição conhecida** (se nunca houve uma, fica vazia), e segue | "Não consegui buscar hoje" não é o mesmo que "a página não tem": um erro passageiro não pode apagar um dado bom |
| Uma **página da lista** | Registra o erro, **para a coleta** e marca `completo = False` | Não se sabe quais vagas faltam, e o orquestrador **não inativa** ninguém |
| Um item que **existe, mas veio quebrado** (vaga sem título ou sem link) | Registra o erro, descarta o item e marca `completo = False` | Ele apareceu no site: não pode ser tratado como "sumiu" |
| Uma paginação em **ciclo** | Registra "ciclo detectado" e marca `completo = False` | As páginas depois do ciclo nunca foram visitadas |
| O `robots.txt` proíbe o endereço (inclusive o de um detalhe) | **Interrompe tudo** | Não é uma falha passageira: é uma regra |

Os testes automatizados confirmam cada linha desta tabela. Dos 79 testes do projeto, 16 são do cliente HTTP (`test_http.py`), e cobrem: a espera do `Crawl-delay`, o bloqueio por `robots.txt`, o `503` repetido, o `Retry-After` obedecido, o `404` que não se repete, o `Timeout`, o `robots.txt` ausente (que libera a coleta) e o `robots.txt` com erro de servidor (que a bloqueia). E há a **prova ao contrário**: ao desligar de propósito o respeito ao `robots.txt` no código, o teste correspondente **falha**, que é a prova de que ele protege de verdade.

## // Bom exemplo × mau exemplo

**Mau exemplo**: repetir sem esperar, e sem fim:

```python
while True:
    resposta = requests.get(url)
    if resposta.ok:
        break
```

Se o servidor estiver fora do ar, o programa o **ataca sem parar**, e nunca termina.

**Bom exemplo**: poucas tentativas, espera crescente, e respeito ao `Retry-After`:

```python
resposta = cliente.obter(url)    # o Cliente do pipeline faz tudo isto
```

## // Erros comuns

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| O programa ataca um servidor com problemas | Repete sem esperar | Use espera crescente e um teto de tentativas |
| Mais `429` a cada tentativa | Ignora o `Retry-After` e a janela do servidor | Espere o que o servidor pediu |
| Repete um `404` quatro vezes | Trata todo erro como passageiro | Só repita `429`, `502`, `503`, `504` e erros de rede |
| Os dados chegam vazios, sem erro | O site mudou o HTML | Conte os campos vazios e acenda um alarme |
| Uma página ruim derruba a coleta toda | Faltou isolar a falha | Capture o erro por página, e registre |
| Todos os programas tentam de novo juntos | Esperas idênticas | Some uma pequena variação aleatória |

## // Prática guiada

1. Rode `11_a_tentativas.py` e confira as esperas de 0,5 s e 1,0 s.
2. Rode `11_b_retry_after.py` e veja o `429` e a espera de 5 segundos.
3. Rode `11_c_condicional.py` e confirme o `304` com zero bytes.
4. Rode `11_d_campos_vazios.py` e veja o alarme acender.
5. Rode `pytest tests/test_http.py` e leia os nomes dos testes: eles descrevem o comportamento do cliente.

## // Pratique sozinho

> **DESAFIO**
> Altere o `11_a_tentativas.py` para pedir `/instavel/vagas?chave=NOVA&falhas=5`, com `tentativas=4`. O que acontece? Resultado esperado: as quatro tentativas levam `503`, as esperas são de 0,5 s, 1,0 s e 2,0 s (3,5 s no total), e o programa termina com `RuntimeError: ... sem sucesso em 4 tentativas`. Depois, mude para `tentativas=6` com `falhas=5`: o sexto pedido funciona. Quanto tempo de espera foi gasto no total? (0,5 + 1 + 2 + 4 + 8 = 15,5 s.)

## // Aplicando no projeto da semana

1. Na pasta do projeto, crie o `http.py` com o cliente educado (robots, espera, tentativas), a partir do que você montou nos Módulos 03 e 05.
2. Troque o seu `baixar()` por `cliente.obter()`.
3. Acrescente ao seu coletor uma contagem dos campos vazios, e imprima um aviso se passar de 30%.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> O seu pipeline roda toda madrugada, e o servidor responde `503` com `Retry-After: 120` (dois minutos) por vários minutos. O seu cliente espera no máximo 30 segundos por tentativa e faz 4 tentativas. O que acontece?

Resposta: o cliente espera 30 segundos (o teto) depois de cada falha, e depois de 4 tentativas **desiste** com `ErroDeColeta`, mesmo que o servidor tivesse pedido 2 minutos. Isso é intencional: o teto protege o seu programa de ficar parado por tempo demais. A página que falhou entra na lista de erros, a execução termina como **parcial**, e o orquestrador **não inativa** ninguém (a coleta não foi completa). Amanhã, o pipeline tenta de novo, com o servidor, espera-se, recuperado. É melhor falhar com elegância do que esperar sem fim.

## // Resumo do módulo

- [ ] Sei tentar de novo com espera crescente e um teto de tentativas.
- [ ] Sei quais erros repetir e quais não repetir.
- [ ] Sei obedecer o `Retry-After`, e ignorar um valor que não consigo ler.
- [ ] Sei usar `ETag` e `If-None-Match`, e quando isso vale a pena.
- [ ] Sei contar campos vazios para perceber que o site mudou.
- [ ] Sei isolar uma falha por página, sem derrubar a coleta inteira.

---

**Próximo módulo:** `12-o-pipeline-de-ponta-a-ponta.md`, cada peça está pronta. Agora, juntar tudo em um programa que roda sozinho.

`Material de Estudo // Coffee & Code`
