# Desafios Opcionais da Semana 07

Português · [English](../docs-eng/challenges.md)

`SEM 07 // Data & Scraping, Parte 1: Coleta`

---

Os desafios abaixo são **opcionais**: servem para quem quer ir além do entregável. Cada um tem uma indicação do que deve acontecer, e nenhum exige nada de fora desta semana.

## // Nível básico

**1. Coletar o detalhe dos eventos.** O pipeline só lê a lista de eventos. Acrescente a visita à página de detalhe de cada evento (`/eventos/e001`). O Mural Tech, porém, **não tem** essa página: o `/eventos/e001` devolve `404`. O que o seu coletor deve fazer? (Dica: isole a falha, como no detalhe das vagas.)

**2. Um relatório em texto.** Escreva um script que consulte o banco e imprima: quantas vagas ativas existem por modalidade, o salário máximo médio por nível (em reais) e os próximos 3 eventos gratuitos. Compare com os números do Módulo 10.

**3. Exportar para CSV.** Escreva um script que leia as vagas ativas do banco e as grave em um arquivo `vagas.csv`, com o módulo `csv`. Abra o arquivo em uma planilha e confira os acentos.

## // Nível intermediário

**4. Uma terceira fonte.** O Mural Tech não tem mais páginas, então invente uma: acrescente ao `servidor.py` uma página `/cursos/` com 5 cursos (título, data no formato `17/10/2026`, preço), e escreva o scraper dela seguindo os quatro passos do Módulo 09. O que você reaproveitou, e o que escreveu?

**5. Um alarme de campos vazios no pipeline.** Faça o pipeline contar os campos vazios de cada fonte e, se mais de 30% de um campo (como o salário) vierem `None`, registrar um `WARNING` e marcar a execução como `parcial`. Teste simulando a mudança de classe do Módulo 11.

**6. O leitor de robots.txt do RFC.** Troque o `urllib.robotparser` pelo Protego (veja o Módulo 14), e acrescente um teste com o exemplo 5.2 do RFC 9309 (`Allow: /example/page/` e `Disallow: /example/page/disallowed.gif`), que o leitor da biblioteca padrão erra.

**7. Requisição condicional.** Faça o cliente guardar a `ETag` de cada página de lista e mandar `If-None-Match`. Quando vier `304`, o que o pipeline faz com as vagas daquela página? (Dica: ele precisa de uma cópia dos dados, e o Módulo 11 explica por quê.)

## // Nível avançado

**8. Uma API própria para os dados.** Monte uma pequena API (com a biblioteca que preferir) que sirva as vagas do banco em JSON, com filtros por modalidade e por salário mínimo. Os dados que você coleta passam a ser **consumidos** por outro programa.

**9. Um histórico de preços.** Em vez de só atualizar o salário de uma vaga que mudou, guarde **cada versão** em uma tabela `vagas_historico` (id, data, salário). Rode o dia 1 e o dia 2, e consulte a evolução de `v003`.

**10. Notificações.** Quando uma vaga nova com `python` nas tags aparece, escreva uma linha em um arquivo `novidades.txt`. Rode o dia 2 e confira.

## // Para a trilha veterano

**11. Coleta assíncrona no pipeline.** Substitua, no `coletores.py`, a visita sequencial aos detalhes das vagas pelo coletor assíncrono do Módulo 15, mantendo o respeito ao `Crawl-delay` com o limitador de ritmo. Quanto tempo você ganha? Se o `Crawl-delay` do site for de 1 segundo, ganha alguma coisa?

**12. Playwright com cache.** No Módulo 16, a página `/vagas-js/` é montada por JavaScript. Escreva um coletor que descubra a **chamada à API** com o Playwright **uma vez**, e depois colete todas as páginas diretamente da API, com `httpx`.

**13. Um teste de navegador no pipeline.** Escreva um teste que use o Playwright (e se pule sozinho se não houver navegador) e confira que `/vagas-js/` mostra 8 cartões depois de esperar.

---

`Material de Estudo // Coffee & Code`
