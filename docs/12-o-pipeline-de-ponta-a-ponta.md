# Módulo 12, O Pipeline de Ponta a Ponta

Português · [English](../docs-eng/12-the-end-to-end-pipeline.md)

`SEM 07 // Data & Scraping, Parte 1: Coleta`

---

## // Antes de começar

Você tem as peças: baixar com educação (Módulos 03, 05 e 11), ler o HTML (06), limpar (08) e guardar sem duplicar (10). Este módulo as junta em **um programa**, que se roda com um comando, que registra o que fez, e que **termina de um jeito que um agendador entende**. É a diferença entre um conjunto de scripts e um pipeline.

## // O desenho

<div align="center">
<img src="./assets/svg/pipeline-de-coleta.svg" alt="O pipeline de coleta: coletar, extrair, limpar, guardar e registrar, com as boas maneiras em todas as etapas e o agendamento" width="640">
</div>

O pipeline é o arquivo `executar.py`, e ele é um **orquestrador**: não sabe ler HTML, nem limpar, nem falar com o servidor. Ele **chama** quem sabe, na ordem certa, e cuida do que ninguém mais cuida: o registro da execução, o resultado final e o código de saída.

## // A função que orquestra

Esta é a função `executar`, na íntegra:

```python
def executar(config: Config, fontes: tuple[str, ...], cliente=None) -> int:
    conn = banco.abrir(config.banco)
    inicio = agora()
    id_execucao = banco.iniciar_execucao(conn, inicio)
    resumos, erros_total, status = [], 0, "ok"
    try:
        cliente = cliente or Cliente(config)
        cliente.carregar_robots()
        etapas = {"vagas": ("vagas", coletores.coletar_vagas),
                  "eventos": ("eventos", coletores.coletar_eventos)}
        for fonte in fontes:
            tabela, coletar = etapas[fonte]
            resultado = coletar(cliente, config)
            with conn:
                contagem = banco.gravar(conn, tabela, resultado.itens, inicio)
                if resultado.completo:
                    contagem.inativadas = banco.inativar_nao_vistas(
                        conn, tabela, coletores.FONTE, inicio)
            erros_total += len(resultado.erros)
            resumos.append(f"{fonte}: {contagem}")
            log.info("%s: %s", fonte, contagem)
            for erro in resultado.erros:
                log.warning("%s: %s", fonte, erro)
        if erros_total:
            status = "parcial"
    except (RobotsIndisponivel, BloqueadoPorRobots) as erro:
        log.error("coleta interrompida: %s", erro)
        status = "falha"
        resumos.append(str(erro))
    except Exception as erro:               # qualquer surpresa vira "falha"
        log.exception("erro inesperado")
        status = "falha"
        resumos.append(f"{type(erro).__name__}: {erro}")
    banco.finalizar_execucao(conn, id_execucao, agora(), status,
                             " | ".join(resumos))
    conn.close()
    log.info("execução %d terminou: %s (%d pedidos, %d repetições)", id_execucao,
             status, getattr(cliente, "pedidos", 0),
             getattr(cliente, "repeticoes", 0))
    return {"ok": SUCESSO, "parcial": PARCIAL, "falha": FALHA}[status]
```

Leia na ordem em que as coisas acontecem:

1. **Abre o banco e registra o início** da execução, com o status `rodando`. Se o programa morrer no meio, o registro mostra que ele não terminou.
2. **Lê o robots.txt**. Se não conseguir (`RobotsIndisponivel`), nada é coletado.
3. **Para cada fonte** (vagas, eventos): coleta, grava e, **só se a coleta foi completa**, inativa o que sumiu. Tudo isso dentro de `with conn:`, uma transação: ou grava o lote inteiro, ou nada.
4. **Decide o status**: `ok` (sem erros), `parcial` (houve erros, mas algo foi guardado) ou `falha` (algo impediu a coleta).
5. **Finaliza o registro** da execução, com o status e um resumo.

O `try/except` final transforma **qualquer surpresa** em `falha`, com o erro no log, e não em um programa que simplesmente some.

## // Quando uma coleta é completa?

Só uma coleta **completa** pode inativar o que sumiu (Módulo 10). Em cada situação abaixo, o coletor marca `completo = False`, e o orquestrador **não inativa nada** naquela fonte:

| Situação | Por que a coleta é incompleta |
|---|---|
| Uma página da lista falhou, mesmo depois das tentativas | Não se sabe quais vagas estavam nela |
| O limite de páginas foi atingido | Pode haver páginas que não foram visitadas |
| A paginação entrou em **ciclo** (uma página aponta de volta a outra já visitada) | As páginas depois do ciclo nunca foram visitadas |
| Um item **existe no site, mas veio quebrado** (uma vaga sem título ou sem link, um evento inválido) | Ele apareceu: se já estava no banco, não pode ser inativado por "não ter aparecido" |

Um caso diferente é a página de **detalhe** que falha. A vaga foi reconhecida, e a coleta continua completa. A descrição, porém, **não deu para ler hoje**: o pipeline não grava um vazio no lugar dela. Ele mantém a última descrição conhecida, e a execução termina como **parcial** (código `1`).

> **UMA LIÇÃO SOBRE O CAMINHO RUIM**
> Em um teste feito durante a produção deste material, uma coleta em que **uma só vaga** veio quebrada inativou as **20 vagas** do banco, porque a coleta era dada como completa. E uma falha temporária de detalhe transformava uma descrição boa em vazio. Os dois defeitos só apareceram quando alguém testou o **caminho ruim**, e não o feliz. Testes automatizados para esses casos agora impedem os dois.

## // Códigos de saída

Quando um programa termina, ele devolve um número ao sistema: o **código de saída**. Por convenção, `0` quer dizer "deu certo", e qualquer outro número, "houve um problema". É assim que um agendador (Módulo 13) sabe se a execução foi boa. O pipeline usa quatro:

| Código | Significa | Quando |
|---|---|---|
| `0` | Sucesso | Coletou tudo, sem erros |
| `1` | Parcial | Coletou, mas houve erros (uma página falhou, uma data ilegível...) |
| `2` | Falha | Não coletou: o `robots.txt` bloqueou ou não pôde ser lido, o site está fora do ar, ou houve um erro inesperado |
| `3` | Já em execução | Outra execução ainda está rodando |

## // O registro (log)

Um programa que roda sozinho **tem que contar o que fez**, porque ninguém está olhando. O Python tem o módulo `logging`, e o pipeline o configura para escrever em **dois lugares**: o terminal e um arquivo (`logs/coleta.log`), que se **rotaciona** ao chegar a 1 MB (guarda 3 arquivos antigos), para nunca crescer sem limite:

```python
def configurar_logging(pasta: str, detalhado: bool = False) -> None:
    Path(pasta).mkdir(parents=True, exist_ok=True)
    formato = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s")
    raiz = logging.getLogger("coleta")
    raiz.handlers.clear()
    raiz.setLevel(logging.DEBUG if detalhado else logging.INFO)
    arquivo = RotatingFileHandler(Path(pasta) / "coleta.log",
                                  maxBytes=1_000_000, backupCount=3,
                                  encoding="utf-8")
    console = logging.StreamHandler()
    for destino in (arquivo, console):
        destino.setFormatter(formato)
        raiz.addHandler(destino)
```

O resultado é um registro com hora e nível (`INFO` para o normal, `WARNING` para o que merece atenção, `ERROR` para falhas). Estas são linhas reais (os horários foram trocados por `HH:MM:SS`):

```
HH:MM:SS INFO    robots.txt lido; espera entre pedidos: 0.05s
HH:MM:SS INFO    vagas: 20 coletadas, 0 erros
HH:MM:SS INFO    vagas: 20 novas, 0 atualizadas, 0 iguais, 0 inativadas
HH:MM:SS INFO    eventos: 8 coletados, 0 erros
HH:MM:SS INFO    eventos: 8 novas, 0 atualizadas, 0 iguais, 0 inativadas
HH:MM:SS INFO    execução 1 terminou: ok (24 pedidos, 0 repetições)
```

## // Argumentos de linha de comando

Os valores que mudam (o endereço do site, o arquivo do banco, a espera) não ficam escritos no código: vêm da linha de comando, pelo módulo `argparse`. A ajuda, gerada sozinha, é esta:

```
usage: python -m coleta [-h] [--base-url BASE_URL] [--banco BANCO]
                        [--pasta-logs PASTA_LOGS] [--espera ESPERA]
                        [--max-paginas MAX_PAGINAS] [--so {vagas,eventos}]
                        [-v]

Coleta vagas e eventos do Mural Tech

options:
  -h, --help            show this help message and exit
  --base-url BASE_URL
  --banco BANCO
  --pasta-logs PASTA_LOGS
  --espera ESPERA       segundos entre pedidos (padrão: o Crawl-delay do site)
  --max-paginas MAX_PAGINAS
  --so {vagas,eventos}
  -v, --detalhado
```

(Os textos `options:` e `show this help message` vêm do próprio Python, em inglês.) Repare em `--espera`: se você **não** passar nada, o pipeline usa o `Crawl-delay` do `robots.txt` (1 segundo). Em estudos locais, `--espera 0.1` acelera as coisas, e é aceitável **só contra o seu site de treino**.

## // A trava contra duas execuções ao mesmo tempo

E se a coleta das 7h ainda estiver rodando quando o agendador disparar a das 7h15? Duas execuções simultâneas poderiam gravar no mesmo banco, e dobrar a carga sobre o site. A solução é uma **trava**: um arquivo que existe enquanto uma execução está em andamento.

```python
class Trava:
    """Impede duas execuções ao mesmo tempo, com um arquivo de trava."""

    def __init__(self, caminho: str, validade_horas: float = 6.0):
        self.caminho = caminho
        self.validade = validade_horas * 3600

    def adquirir(self) -> bool:
        Path(self.caminho).parent.mkdir(parents=True, exist_ok=True)
        for _ in range(2):
            try:
                fd = os.open(self.caminho, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                idade = time.time() - os.path.getmtime(self.caminho)
                if idade < self.validade:
                    return False
                log.warning("trava abandonada há %.1f h: removendo", idade / 3600)
                os.remove(self.caminho)
                continue
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return True
        return False

    def liberar(self) -> None:
        if os.path.exists(self.caminho):
            os.remove(self.caminho)
```

O segredo está no `os.O_CREAT | os.O_EXCL`: criar o arquivo **só se ele não existir**, em uma operação indivisível. Quem consegue criar, é o dono da trava; quem não consegue, sai com o código `3`. Uma trava **abandonada** (o programa morreu sem liberá-la) é removida depois de 6 horas, para o pipeline não ficar bloqueado para sempre. E o `main()` garante que a trava seja liberada ao final, com `finally`:

```python
def main(argv=None) -> int:
    args = ler_argumentos(argv)
    config = Config(base_url=args.base_url, banco=args.banco,
                    pasta_logs=args.pasta_logs, espera=args.espera,
                    max_paginas=args.max_paginas)
    configurar_logging(config.pasta_logs, args.detalhado)
    trava = Trava(config.banco + ".lock")
    if not trava.adquirir():
        log.error("outra execução está em andamento: saindo")
        return JA_EM_EXECUCAO
    try:
        fontes = (args.so,) if args.so else ("vagas", "eventos")
        return executar(config, fontes)
    finally:
        trava.liberar()
```

## // Rodando de verdade

Com o Mural Tech ligado, o pipeline se roda com `python -m coleta`. Estas são **três execuções seguidas** (dia 1, dia 1 de novo, e dia 2 do site), com `--espera 0.05`. Os resumos são os reais:

```
EXECUÇÃO 1 (dia 1)
vagas: 20 novas, 0 atualizadas, 0 iguais, 0 inativadas
eventos: 8 novas, 0 atualizadas, 0 iguais, 0 inativadas
execução 1 terminou: ok (24 pedidos, 0 repetições)       código de saída: 0

EXECUÇÃO 2 (dia 1 de novo)
vagas: 0 novas, 0 atualizadas, 20 iguais, 0 inativadas
eventos: 0 novas, 0 atualizadas, 8 iguais, 0 inativadas
execução 2 terminou: ok (24 pedidos, 0 repetições)       código de saída: 0

EXECUÇÃO 3 (dia 2)
vagas: 3 novas, 2 atualizadas, 17 iguais, 1 inativadas
eventos: 2 novas, 0 atualizadas, 8 iguais, 0 inativadas
execução 3 terminou: ok (26 pedidos, 0 repetições)       código de saída: 0
```

(A saída real tem também as linhas "coletadas" e os horários, e foi resumida aqui.) Veja o que cada execução mostra: a primeira **enche** o banco (24 pedidos: 3 páginas de lista, 20 de detalhe e 1 de eventos). A segunda **não muda nada**: tudo "igual", a idempotência do Módulo 10. A terceira percebe o **dia seguinte**: 3 vagas novas, 2 de salário alterado, 1 que sumiu (inativada), e 2 eventos novos.

O banco guarda o histórico de cada execução, na tabela `execucoes`:

```
(1, 'ok', 'vagas: 20 novas, 0 atualizadas, 0 iguais, 0 inativadas | ...')
(2, 'ok', 'vagas: 0 novas, 0 atualizadas, 20 iguais, 0 inativadas | ...')
(3, 'ok', 'vagas: 3 novas, 2 atualizadas, 17 iguais, 1 inativadas | ...')
```

(Os resumos foram encurtados: cada um continua com a parte dos eventos.)

### Quando o site não está no ar

E o caso ruim? Com o endereço do site apontando para uma porta onde ninguém responde:

```
ERROR   coleta interrompida: robots.txt inacessível: ...Max retries exceeded...
INFO    execução 1 terminou: falha (0 pedidos, 0 repetições)
código de saída: 2
```

O pipeline **não coletou nada** (sem `robots.txt` legível, a regra do RFC é não coletar), registrou o motivo, **gravou a execução como falha** no banco e saiu com o código `2`. É exatamente o que um agendador precisa para saber que algo deu errado.

## // Os testes do pipeline

O arquivo `tests/test_pipeline.py` roda o pipeline **inteiro**, contra o Mural Tech, que sobe dentro do próprio teste. Os nomes dos testes dizem o que garantem:

| Teste | Garante |
|---|---|
| `test_primeira_execucao_grava_vagas_e_eventos` | 20 vagas e 8 eventos no banco |
| `test_executar_de_novo_nao_duplica_nada` | A idempotência |
| `test_o_dia_seguinte_traz_novas_atualizadas_e_inativas` | `3 novas, 2 atualizadas, 17 iguais, 1 inativadas`, `v015` inativa, salário de `v003` atualizado |
| `test_dados_limpos_no_banco` | Salário em centavos, tags, data ISO, preços |
| `test_falha_no_detalhe_gera_resultado_parcial_mas_guarda_a_vaga` | Código `1`, vaga guardada (sem descrição, na primeira coleta) |
| `test_falha_no_detalhe_preserva_a_descricao_ja_conhecida` | A descrição boa **não** vira vazio, e a vaga segue "igual" |
| `test_coleta_incompleta_por_vaga_quebrada_nao_inativa_ninguem` | Uma vaga quebrada não inativa as outras 20 |
| `test_coleta_com_paginacao_em_ciclo_nao_inativa_ninguem` | Um ciclo de paginação não inativa ninguém |
| `test_pagina_de_lista_que_falha_nao_inativa_ninguem` | Coleta incompleta não inativa |
| `test_site_fora_do_ar_devolve_falha` | Código `2` e status `falha` |
| `test_main_recusa_duas_execucoes_ao_mesmo_tempo` | Código `3` |
| `test_trava_abandonada_e_removida` | A trava velha não bloqueia para sempre |

No total, o projeto tem **79 testes**. E a **prova ao contrário**, que mostra que eles servem: ao desligar de propósito o reconhecimento de "igual" no `banco.py`, **3 testes falham** (a idempotência e a atualização deixam de funcionar); ao desligar o respeito ao `robots.txt`, **1 teste falha**. Os testes de completude também foram provados assim: sem a detecção de ciclo, **2 falham**; se a descrição conhecida voltar a ser apagada, **1 falha**; se uma vaga quebrada deixar de tornar a coleta incompleta, **3 falham**. Desfeitas as mudanças, os 79 passam de novo.

## // Bom exemplo × mau exemplo

**Mau exemplo**: um script que, ao dar erro, imprime uma mensagem e termina com código `0`:

```python
try:
    coletar()
except Exception:
    print("deu erro")
```

O agendador acha que **deu certo**, e ninguém fica sabendo.

**Bom exemplo**: registrar, gravar o status e devolver um código que diga a verdade:

```python
return {"ok": SUCESSO, "parcial": PARCIAL, "falha": FALHA}[status]
```

## // Erros comuns

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| O pipeline sai com código `3` | Há uma trava de uma execução anterior | Confira se outra execução está rodando; se não, apague o arquivo `.lock` |
| Todas as vagas aparecem como "atualizadas" | A impressão digital inclui algo que muda sempre (como uma hora) | Deixe fora do hash qualquer campo que varie sem o conteúdo variar |
| Vagas inativadas por engano | Inativou depois de uma coleta incompleta | Só inative quando `completo` for verdadeiro |
| O log cresce sem parar | Faltou a rotação | Use `RotatingFileHandler` |
| O agendador nunca avisa de falhas | O programa sempre sai com `0` | Devolva códigos diferentes de zero quando algo falhar |
| Um erro "some" sem rastro | O `except` engole o erro sem registrar | Use `log.exception(...)` |

## // Prática guiada

1. Com o Mural Tech no dia 1, rode `python -m coleta --espera 0.1`, e depois consulte o banco (`dados/vagas.db`).
2. Rode **de novo**, e confira "20 iguais".
3. Troque o site para o dia 2 (`curl http://127.0.0.1:8080/_dev/dia/2`) e rode: confira as novas, atualizadas e a inativada.
4. Rode `echo $?` logo depois de uma execução, e confira o código de saída.
5. Desligue o site e rode de novo: o código deve ser `2`, e a tabela `execucoes` deve ter uma linha `falha`.
6. Abra o `logs/coleta.log` e leia o histórico.

## // Pratique sozinho

> **DESAFIO**
> Acrescente ao pipeline a opção `--max-paginas 1`, e rode-a. O que acontece com as vagas de fora? Resultado esperado: a coleta pega só a primeira página (8 vagas), o coletor registra o erro "limite de páginas atingido" e marca `completo = False`, a execução termina como **parcial**, e **nenhuma vaga é inativada**. Releia, no `coletores.py`, o `else` do laço `for`, e explique por que ele existe.

## // Aplicando no projeto da semana

1. Na pasta do projeto, monte o pacote `coleta/` com os arquivos `config.py`, `http.py`, `parsers.py`, `limpeza.py`, `modelos.py`, `coletores.py`, `banco.py`, `executar.py`, `__init__.py` e `__main__.py`.
2. Rode `python -m coleta --help`, e depois uma coleta completa.
3. Confira o `dados/vagas.db` e o `logs/coleta.log`.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> Em uma noite, a coleta de vagas termina bem, mas a de eventos falha porque a página de eventos caiu. O que o pipeline grava, qual é o status da execução, e qual é o código de saída?

Resposta: as **vagas são gravadas** normalmente (cada fonte é uma transação separada), os eventos não, e a execução termina como **parcial**, com o código **1**, e o erro da página de eventos no log. Os eventos que já estavam no banco **não são inativados** (a coleta deles foi incompleta). Amanhã, quando o site voltar, o pipeline completa o que faltou. É a razão de o pipeline separar as fontes, e de o código `1` existir: algo deu certo, algo não, e quem lê o registro precisa saber disso.

## // Resumo do módulo

- [ ] Sei que o orquestrador chama as peças na ordem certa, e cuida do registro e do resultado.
- [ ] Sei os quatro códigos de saída, e por que eles importam para um agendador.
- [ ] Sei configurar o `logging` com arquivo rotativo, e ler um log.
- [ ] Sei usar `argparse`, e que `--espera` sem valor usa o `Crawl-delay` do site.
- [ ] Sei usar uma trava para impedir execuções simultâneas.
- [ ] Sei por que o pipeline é idempotente, e o que significa cada contagem do resumo.
- [ ] Sei que só uma coleta completa pode inativar o que sumiu.

---

**Próximo módulo:** `13-agendando-a-coleta.md`, o pipeline funciona quando você o chama. Falta fazê-lo rodar sozinho.

`Material de Estudo // Coffee & Code`
