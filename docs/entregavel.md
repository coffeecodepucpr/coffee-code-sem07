# Entregável da Semana 07

Português · [English](../docs-eng/deliverable.md)

`SEM 07 // Data & Scraping, Parte 1: Coleta`

---

## // O que entregar

**Um pipeline de captura automática para o banco**: um projeto que coleta vagas e eventos do site de treino, limpa os dados, guarda tudo em um banco SQLite **sem duplicar**, registra cada execução e pode ser agendado para rodar sozinho.

## // Checklist

### Coleta e boas maneiras
- [ ] O programa lê o `robots.txt` e **não visita** o que ele proíbe.
- [ ] Respeita a espera entre pedidos (o `Crawl-delay`, ou o que você configurou).
- [ ] Usa um `User-Agent` honesto, com o nome do projeto e um contato.
- [ ] **Todo** pedido tem `timeout`.
- [ ] Repete `429`, `502`, `503` e `504` e erros de rede com espera crescente, e **não** repete `404`.
- [ ] A paginação segue o link Próxima, e tem as travas `visitadas` e `MAX_PAGINAS`.

### Dados
- [ ] Os campos de vagas e eventos são extraídos com seletores **por significado**.
- [ ] O dinheiro é guardado em centavos inteiros, e as datas em ISO 8601.
- [ ] Ausente é `None` (nunca zero, e nunca um texto como `A combinar`).
- [ ] Um registro com dado ruim não derruba a coleta: é guardado com aviso, ou descartado com registro.

### Banco
- [ ] O esquema tem chave única (`fonte`, `id_externo`) e `NOT NULL` nos campos essenciais.
- [ ] Rodar **duas vezes** não duplica nada (idempotência).
- [ ] A coleta classifica cada item como nova, atualizada ou igual.
- [ ] O que some do site é **inativado**, e não apagado, e só depois de uma coleta **completa**.
- [ ] Uma coleta é **incompleta** (e nada é inativado) quando uma página falha, a paginação entra em ciclo, o limite de páginas é atingido, ou um item chega quebrado.
- [ ] Uma falha temporária na página de detalhe **não apaga** a descrição já conhecida.
- [ ] Todos os valores vão por parâmetro (`?`), nunca por f-string.

### Execução
- [ ] A cada execução, uma linha na tabela `execucoes`, com status e resumo.
- [ ] O programa escreve um log em arquivo, com rotação.
- [ ] Os códigos de saída são `0` (sucesso), `1` (parcial), `2` (falha) e `3` (já em execução).
- [ ] Uma trava impede duas execuções ao mesmo tempo.

### Agendamento
- [ ] Existe um script que prepara o ambiente e chama o pipeline com caminhos absolutos.
- [ ] A expressão do agendamento foi **conferida** (com `croniter`), e roda **uma vez por dia**.
- [ ] Sei como conferir se a coleta está rodando (log e tabela `execucoes`).

### Testes e documentação
- [ ] Há testes automatizados para a limpeza, o banco e o pipeline, e eles passam.
- [ ] O `README.md` explica como instalar, ligar o site, rodar e testar.
- [ ] O `.gitignore` deixa de fora `.venv/`, `dados/` e `logs/`.

## // Como entregar

1. Coloque o projeto em um repositório (por exemplo, no GitHub), **sem** o ambiente virtual, o banco e os logs.
2. No `README.md`, inclua os comandos para instalar e rodar, e a lista do que foi testado e do que não foi.
3. Mostre ao grupo, em uma reunião, **duas execuções seguidas** do pipeline: a primeira enchendo o banco e a segunda mostrando "tudo igual". Depois, troque o site para o dia 2 e mostre a terceira, com as vagas novas e a inativada.

## // Para quem fez a trilha veterano

- [ ] Um coletor assíncrono com `httpx`, com **limite de concorrência** e **ritmo mínimo** entre os pedidos.
- [ ] Uma página montada por JavaScript, coletada com Playwright (ou Selenium), ou pela API que ela usa.
- [ ] Uma medição, com números seus, de quanto o assíncrono ganha **e de quando ele deixa de ganhar** (Módulo 15).

---

`Material de Estudo // Coffee & Code`
