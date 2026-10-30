# Módulo 13, Agendando a Coleta

Português · [English](../docs-eng/13-scheduling-the-collection.md)

`SEM 07 // Data & Scraping, Parte 1: Coleta`

---

## // Antes de começar

Um pipeline que só roda quando você lembra de rodá-lo não é automação. Este módulo põe o pipeline do Módulo 12 para rodar **sozinho**, em horários fixos, e ensina o que muda quando ninguém está na frente do terminal: caminhos absolutos, registros em arquivo, e proteção contra execuções sobrepostas.

> **O QUE FOI E O QUE NÃO FOI TESTADO NESTE MÓDULO**
> Foram verificados, com execução real: as **expressões de agendamento** (com a biblioteca `croniter`), o **script que o agendador chama**, o **código de saída** e a **trava** contra execução dupla. **Não foi possível testar** o `cron` em si (ele não estava disponível no ambiente de produção), nem o Agendador de Tarefas do Windows, nem o `launchd` do macOS. As instruções para esses três seguem as convenções conhecidas, e **você deve conferi-las** no seu sistema.

## // O que é o cron

O **cron** é o agendador de tarefas dos sistemas Linux e macOS: um programa que fica rodando e, em cada minuto, confere uma lista de tarefas ("rode isto às 7h todo dia") e dispara as que chegaram na hora. Você edita a sua lista com o comando `crontab -e`, e cada linha tem **cinco campos de horário**, seguidos do comando.

<div align="center">
<img src="./assets/svg/expressao-cron.svg" alt="Os cinco campos da expressão do cron: minuto, hora, dia do mês, mês e dia da semana, e os símbolos asterisco, vírgula, hífen e barra" width="640">
</div>

Leia `30 6 * * 1-5` assim: minuto `30`, hora `6`, qualquer dia do mês, qualquer mês, dias da semana de `1` a `5` (segunda a sexta). Ou seja: **às 6h30, de segunda a sexta**.

## // Conferindo uma expressão antes de usá-la

Errar a expressão é fácil, e o erro só aparece no dia em que a tarefa não roda. Por isso vale **conferir** antes. A biblioteca `croniter` (`pip install croniter`, testada na versão 6.2.4) calcula as próximas execuções de uma expressão. Partindo de um sábado, 10/10/2026, às 06:30, os resultados reais são:

```
0 7 * * *      -> ['Sat 10/10 07:00', 'Sun 11/10 07:00', 'Mon 12/10 07:00']
30 6 * * 1-5   -> ['Mon 12/10 06:30', 'Tue 13/10 06:30', 'Wed 14/10 06:30']
*/15 * * * *   -> ['Sat 10/10 06:45', 'Sat 10/10 07:00', 'Sat 10/10 07:15']
0 7 1 * *      -> ['Sun 01/11 07:00', 'Tue 01/12 07:00', 'Fri 01/01 07:00']
```

Confira o que isso ensina: `30 6 * * 1-5`, em um **sábado**, só dispara na **segunda**; `*/15` dispara a cada 15 minutos; `0 7 1 * *` dispara só no dia 1 de cada mês. E a biblioteca também **valida** expressões:

```
valida? '0 7 * * *'      True
valida? '61 * * * *'     False
valida? '0 25 * * *'     False
valida? '* * * *'        False
```

(Minuto 61, hora 25 e uma expressão com só quatro campos são recusados.) Um detalhe do dia da semana: `0` e `7` são ambos o domingo, o que também foi confirmado.

## // O script que o agendador chama

Quando o cron dispara um comando, ele **não é** o seu terminal: não tem o ambiente virtual ativado, não está na pasta do projeto, e não tem as suas variáveis. Por isso o agendador não deve chamar o `python -m coleta` direto: ele chama um **script curto**, que prepara tudo. Este é o `executar_pipeline.sh`:

```bash
#!/usr/bin/env bash
# Executa o pipeline de coleta. Feito para ser chamado pelo cron.
# Ajuste PROJETO e PYTHON para os caminhos do SEU computador (sempre absolutos).
set -u

PROJETO="${PROJETO:-$(cd "$(dirname "$0")/../pipeline" && pwd)}"
PYTHON="${PYTHON:-$PROJETO/.venv/bin/python}"
LOG="$PROJETO/logs/cron.log"

mkdir -p "$PROJETO/logs"
cd "$PROJETO" || exit 2

{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') inicio"
  "$PYTHON" -m coleta "$@"
  codigo=$?
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') fim (codigo $codigo)"
} >> "$LOG" 2>&1

exit "$codigo"
```

O que ele faz, linha a linha:

- `set -u`: erro se usar uma variável que não existe.
- `PROJETO` e `PYTHON`: **caminhos absolutos**. O padrão deduz a pasta do projeto a partir do próprio script, e usa o Python **do ambiente virtual** (`.venv/bin/python`), com as bibliotecas certas. Você pode sobrescrever as duas variáveis.
- `LOG`: um arquivo de registro do próprio agendador (`logs/cron.log`).
- `cd "$PROJETO" || exit 2`: entra na pasta do projeto (o pipeline cria `dados/` e `logs/` em relação a ela), e **sai com erro** se não conseguir.
- O bloco `{ ... } >> "$LOG" 2>&1`: **tudo** o que o pipeline escrever (a saída normal e a de erro) vai para o arquivo, e não se perde, já que ninguém está olhando o terminal. Marca a hora de início e de fim, e guarda o código de saída.
- `exit "$codigo"`: devolve o **mesmo código** do pipeline. Sem isso, o agendador acharia que sempre deu certo.

## // O que foi verificado do script

Estes são resultados reais, rodando o script com o Mural Tech no ar:

```
codigo do wrapper: 0
--- duas execucoes ao mesmo tempo:
segunda execucao: codigo 3
primeira execucao: codigo 0
```

A primeira execução terminou com `0`. Quando **duas** foram disparadas quase juntas, a segunda encontrou a trava (Módulo 12), recusou-se a rodar e saiu com o código `3`, enquanto a primeira seguiu normalmente e terminou com `0`. O arquivo `cron.log` registrou tudo:

```
=== DATA HORA inicio
=== DATA HORA fim (codigo 0)
=== DATA HORA inicio
=== DATA HORA inicio
DATA HORA ERROR   outra execução está em andamento: saindo
=== DATA HORA fim (codigo 3)
=== DATA HORA fim (codigo 0)
```

(As datas e horas foram trocadas por `DATA HORA`.)

## // A linha do crontab

Com o script pronto, a linha do `crontab` é curta. Este é o arquivo `crontab.exemplo`:

```
# Edite com:  crontab -e
#
# minuto  hora  dia-do-mês  mês  dia-da-semana   comando
#
# Todo dia, às 7h da manhã:
0 7 * * *     /caminho/absoluto/para/executar_pipeline.sh

# De segunda a sexta, às 6h30:
# 30 6 * * 1-5  /caminho/absoluto/para/executar_pipeline.sh

# A cada 15 minutos (só para testar o agendamento, nunca em um site real):
# */15 * * * *  /caminho/absoluto/para/executar_pipeline.sh
```

Três regras para a linha do cron:

1. **Caminho absoluto sempre**: `/caminho/absoluto/para/executar_pipeline.sh`, e não `./executar_pipeline.sh`. Descubra o caminho com `pwd`.
2. **O script precisa ser executável**: `chmod +x executar_pipeline.sh`.
3. **Não agende com mais frequência do que o necessário.** O exemplo de 15 em 15 minutos serve só para testar o agendamento. Vagas e eventos mudam uma vez por dia: **uma execução diária** basta, e é o que um site real tolera sem se incomodar.

## // Windows e macOS

> **NÃO TESTADO**
> Nada desta seção foi executado: o material foi produzido em Linux. Trate-a como ponto de partida, e confira a documentação do seu sistema.

No **Windows**, o equivalente do cron é o **Agendador de Tarefas**, e se pode criar uma tarefa pelo terminal com o comando `schtasks`. O arquivo `agendar_windows.txt` traz o roteiro, e o `executar_pipeline.bat` é o equivalente do script acima. Ele cria a pasta `logs` se ela não existir (o redirecionamento da saída falharia antes de o Python ter a chance de criá-la) e coloca os caminhos entre aspas, para aceitar nomes com espaço:

```
Agendador de Tarefas do Windows (NAO TESTADO: o material foi produzido em Linux).

Pelo terminal (Prompt de Comando), todo dia as 07:00:

  schtasks /Create /SC DAILY /ST 07:00 /TN "ColetaMuralTech" ^
           /TR "C:\Users\voce\projeto-coleta\agendamento\executar_pipeline.bat"

Se o caminho do .bat tiver ESPACOS, o valor de /TR precisa de aspas internas
(escapadas com barra invertida) e o comando deve ser conferido no seu sistema.

Para conferir, rodar agora e remover:

  schtasks /Query /TN "ColetaMuralTech"
  schtasks /Run /TN "ColetaMuralTech"
  schtasks /Delete /TN "ColetaMuralTech" /F
```

No **macOS**, o `cron` também existe, e o sistema oferece o `launchd` como alternativa moderna. Não temos roteiro testado para ele.

## // Saber se o agendamento está funcionando

Agendar e esquecer é como as coisas quebram em silêncio. Duas formas de conferir:

**1. Olhar o arquivo de registro.** O `cron.log` (do script) e o `coleta.log` (do pipeline) mostram cada execução. No Linux e no macOS, `tail -n 20 logs/cron.log` mostra as últimas linhas.

**2. Perguntar ao banco.** A tabela `execucoes` (Módulo 12) guarda cada execução. Esta consulta conta as execuções bem-sucedidas nas últimas 26 horas (um dia, com folga):

```sql
SELECT count(*) FROM execucoes
WHERE status IN ('ok', 'parcial')
  AND datetime(inicio) >= datetime('now', 'localtime', '-26 hours');
```

Se o resultado for `0`, ninguém coletou nada no último dia, e algo precisa de atenção.

O `datetime(inicio)` do lado esquerdo **não é enfeite**. A coluna `inicio` é texto: o pipeline grava `2026-10-10T07:00:00.123456` (com um `T`), e o SQLite devolve a data do `datetime(...)` com um **espaço**. Comparar os dois **como texto** dá o resultado errado, porque o `T` vem depois do espaço na ordem das letras: `'2026-10-10T07:00:00' >= '2026-10-10 10:00:00'` vale `1`, embora 07:00 seja **anterior** a 10:00. Com `datetime()` dos dois lados, vale `0`. Em um teste com quatro execuções (de 3 h, 30 h e 80 h atrás, e uma 1 hora antes do limite de 26 h), a consulta sem `datetime(inicio)` contou **3**, e a corrigida contou **1**, que é o certo. O `datetime()` entende o carimbo com microssegundos que o pipeline grava. (O `localtime` compara no mesmo relógio em que o pipeline grava a hora de início.) Nos testes, o resultado após três execuções foi `3`. Ligar essa consulta a um aviso (por e-mail, por exemplo) está fora do escopo desta semana.

## // Bom exemplo × mau exemplo

**Mau exemplo**: chamar o Python direto, com caminho relativo, sem registro:

```
0 7 * * *  python -m coleta
```

Quando o cron roda, não está na pasta do projeto, e o `python` talvez nem seja o do ambiente virtual. O erro se perde, porque a saída não vai para nenhum lugar.

**Bom exemplo**: um script que prepara tudo, e uma linha com caminho absoluto:

```
0 7 * * *  /caminho/absoluto/para/executar_pipeline.sh
```

## // Erros comuns

> **ATENÇÃO**
> A tabela abaixo reúne os problemas **mais conhecidos** de tarefas agendadas. Eles seguem a documentação e a prática geral, e **não foram reproduzidos** neste ambiente, ao contrário das expressões, do script e da trava, que foram.

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| "Command not found", ou erro de bibliotecas faltando | O cron roda com um ambiente mínimo, sem o seu ambiente virtual | Chame o Python do ambiente virtual por caminho absoluto, como o script faz |
| A tarefa nunca roda | A expressão está errada, ou o script não é executável | Confira a expressão com `croniter`, e rode `chmod +x` |
| Não se sabe o que aconteceu | A saída não foi para um arquivo | Redirecione `>> arquivo 2>&1`, como o script faz |
| Duas execuções se atropelam | A anterior ainda não terminou | A trava do pipeline (código `3`) |
| Roda em horário "errado" | O cron usa o relógio e o fuso do sistema | Confira a hora do sistema, e escreva a hora na sua expressão |
| O pipeline pede muito ao site | Agendou com frequência demais | Uma vez por dia basta |

## // Prática guiada

1. Instale a `croniter` (`pip install croniter`) e liste as próximas execuções de `0 7 * * *`.
2. Rode o `executar_pipeline.sh` à mão (com `PROJETO` e `PYTHON` apontando para o seu projeto e o seu ambiente virtual) e confira o `logs/cron.log`.
3. Rode o script **duas vezes ao mesmo tempo** (uma em cada terminal) e confirme o código `3` na segunda.
4. Se você usa Linux ou macOS, rode `crontab -e` e escreva uma linha com **uma expressão de teste** (a cada 5 minutos, por exemplo), espere o horário e confira o log. **Remova a linha depois.**

## // Pratique sozinho

> **DESAFIO**
> Escreva a expressão do cron para rodar **toda segunda, quarta e sexta, às 7h15**, e confira com a `croniter`. Resposta: `15 7 * * 1,3,5`. A partir de um sábado, 10/10/2026, às 06:30, as próximas execuções são segunda 12/10, quarta 14/10 e sexta 16/10, todas às 07:15.

## // Aplicando no projeto da semana

1. Na pasta do projeto, crie a pasta `agendamento/` com o `executar_pipeline.sh` (ou o `.bat`, no Windows).
2. Ajuste `PROJETO` e `PYTHON` para os seus caminhos.
3. Escreva a sua linha de agendamento **uma vez por dia**, e confira a expressão com `croniter`.
4. Guarde a consulta das últimas 26 horas em um arquivo `conferir.sql`.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> O seu agendamento roda todo dia às 7h. Em uma semana, ninguém olha o banco. Na segunda-feira seguinte, você descobre que ele **parou de coletar na terça**. Que defesas deste módulo e do anterior ajudariam a perceber isso mais cedo?

Resposta: o **código de saída** (`1` ou `2` em caso de problema) aparece no `cron.log` e, em um agendador mais completo, poderia disparar um aviso; a **tabela execucoes** tem o status de cada dia, e a **consulta das últimas 26 horas** devolveria `0` na quarta de manhã; e o **log** mostraria o erro. A lição é que automação sem **observação** é só uma forma de falhar em silêncio: a parte que roda sozinho precisa vir junto da parte que avisa quando para.

## // Resumo do módulo

- [ ] Sei ler uma expressão do cron: os cinco campos, e os símbolos `*`, `,`, `-` e `/`.
- [ ] Sei conferir uma expressão com a `croniter`, antes de usá-la.
- [ ] Sei por que o agendador chama um script, e o que ele prepara.
- [ ] Sei que o código de saída precisa chegar ao agendador.
- [ ] Sei que uma execução por dia basta, e que a trava impede execuções sobrepostas.
- [ ] Sei conferir se a coleta está rodando, pelo log e pela tabela `execucoes`.
- [ ] Sei o que **não** foi testado neste módulo: o `cron` em si, o Windows e o macOS.

---

**Próximo módulo:** `14-projeto-guiado.md`, todas as peças estão prontas. Vamos montar o entregável e conferi-lo, item por item.

`Material de Estudo // Coffee & Code`
