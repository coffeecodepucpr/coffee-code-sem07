# Exemplos da Semana 07

Português · [English](../../docs-eng/example/README.md)

`SEM 07 // Data & Scraping, Parte 1: Coleta`

Tudo o que está aqui foi **executado em Linux**. Veja o `README.md` da semana para o que foi e o que não foi testado.

## // O que tem em cada pasta

| Pasta | O que é | Módulos |
|---|---|---|
| `site-treino/` | O Mural Tech: o site fictício de treino | 01 a 17 |
| `scripts/` | Scripts de aula, com `parsers.py` e `limpeza.py` | 03 a 11 |
| `pipeline/` | O projeto final, com os testes | 12 e 14 |
| `agendamento/` | O script que o `cron` chama, e exemplos | 13 |
| `veterano/` | `httpx` assíncrono, Playwright e Selenium, com testes | 15 a 17 |

## // Preparando o ambiente

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r pipeline/requirements.txt
pip install -r pipeline/requirements-testes.txt
```

Para a trilha veterano, também `pip install -r veterano/requirements.txt` (e, para o Playwright, `playwright install chromium`). No Windows, a ativação do ambiente é outra, e **não foi testada**.

## // Ligando o site de treino

Em um terminal, dentro de `site-treino/`:

```
python3 servidor.py                    # dia 1, porta 8080
python3 servidor.py --dia 2            # dados do "dia 2"
python3 servidor.py --latencia 0.2     # cada resposta demora 0,2 s
```

Durante os estudos, troque o dia sem reiniciar: `curl http://127.0.0.1:8080/_dev/dia/2` (e `/_dev/dia/1`, `/_dev/reset`).

## // Rodando o pipeline e os testes

Em outro terminal, dentro de `pipeline/`:

```
python -m coleta --espera 0.1          # coleta vagas e eventos
python -m coleta --so vagas            # só as vagas
python -m coleta --help                # todas as opções
pytest                                 # 79 testes (o site sobe sozinho)
```

O pipeline escreve o banco em `dados/vagas.db` e o log em `logs/coleta.log`. Os códigos de saída são `0` (sucesso), `1` (parcial), `2` (falha) e `3` (já em execução). O `--espera 0.1` só é aceitável contra o seu **site de treino**: sem ele, o pipeline usa o `Crawl-delay` do `robots.txt`.

## // Rodando a trilha veterano

Dentro de `veterano/`, com o site ligado:

```
python 15_a_comparar.py                # sequencial contra assíncrono
python 16_b_playwright_basico.py       # exige o Playwright e o Chromium
python 17_a_selenium_basico.py         # exige o Selenium e um driver
pytest  # 16 testes; os de navegador se pulam sem navegador
```

## // O que fica de fora do repositório

`.venv/`, `dados/` e `logs/` (resultado de execuções), e qualquer `__pycache__`.

---

`Material de Estudo // Coffee & Code`
