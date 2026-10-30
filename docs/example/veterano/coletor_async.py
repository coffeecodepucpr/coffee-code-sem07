"""Coleta assíncrona das vagas com httpx: concorrência com limite e ritmo."""
import asyncio
import re
import time
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from parsers import ler_descricao, ler_vagas_da_pagina

BASE = "http://127.0.0.1:8080"
USER_AGENT = "MuralColetaBot/1.0 (projeto de estudo; contato: voce@example.com)"
RETENTAR = (429, 502, 503, 504)      # a mesma política do pipeline principal


class LimitadorDeRitmo:
    """Garante um intervalo mínimo entre o INÍCIO de dois pedidos, para todos."""

    def __init__(self, intervalo: float):
        self.intervalo = intervalo
        self._proximo = 0.0
        self._trava = asyncio.Lock()

    async def esperar(self) -> None:
        async with self._trava:
            agora = asyncio.get_running_loop().time()
            espera = max(0.0, self._proximo - agora)
            self._proximo = max(agora, self._proximo) + self.intervalo
        if espera:
            await asyncio.sleep(espera)


def segundos_de(retry_after, padrao: float) -> float:
    """Retry-After pode ser um número ou uma data HTTP: se não der, o padrão."""
    try:
        return float(retry_after)
    except (TypeError, ValueError):
        return padrao


async def baixar(cliente, url, semaforo, limitador, tentativas=3,
                 dormir=asyncio.sleep):
    async with semaforo:                 # no máximo N pedidos ao mesmo tempo
        for numero in range(1, tentativas + 1):
            await limitador.esperar()    # e no máximo 1 a cada intervalo
            try:
                resposta = await cliente.get(url)
            except (httpx.TimeoutException, httpx.TransportError):
                resposta = None
            if resposta is not None and resposta.status_code not in RETENTAR:
                resposta.raise_for_status()
                return resposta
            if numero < tentativas:
                pedido = resposta.headers.get("Retry-After") if resposta else None
                espera = segundos_de(pedido, 0.5 * 2 ** (numero - 1))
                await dormir(espera)
        raise RuntimeError(f"{url}: sem sucesso em {tentativas} tentativas")


def sopa(resposta):
    return BeautifulSoup(resposta.content, "lxml")


async def coletar(base=BASE, concorrencia=5, intervalo=0.0):
    semaforo = asyncio.Semaphore(concorrencia)
    limitador = LimitadorDeRitmo(intervalo)
    cabecalhos = {"User-Agent": USER_AGENT}
    tempo = httpx.Timeout(10, connect=3)
    async with httpx.AsyncClient(headers=cabecalhos, timeout=tempo) as cliente:
        url1 = urljoin(base, "/vagas/")
        primeira = sopa(await baixar(cliente, url1, semaforo, limitador))
        rotulo = primeira.select_one(".paginacao span").get_text()
        total = int(re.search(r"de (\d+)", rotulo).group(1))
        urls = [f"{url1}?pagina={n}" for n in range(2, total + 1)]
        outras = await asyncio.gather(
            *(baixar(cliente, u, semaforo, limitador) for u in urls))
        vagas = ler_vagas_da_pagina(primeira, url1)
        for resposta in outras:
            vagas += ler_vagas_da_pagina(sopa(resposta), str(resposta.url))
        detalhes = await asyncio.gather(
            *(baixar(cliente, v["url"], semaforo, limitador) for v in vagas),
            return_exceptions=True)
        for vaga, detalhe in zip(vagas, detalhes):
            if isinstance(detalhe, Exception):
                vaga["descricao"] = None      # uma falha não derruba as outras
            else:
                vaga["descricao"] = ler_descricao(sopa(detalhe))
    return vagas


if __name__ == "__main__":
    inicio = time.perf_counter()
    vagas = asyncio.run(coletar(concorrencia=5, intervalo=0.0))
    print(f"{len(vagas)} vagas em {time.perf_counter() - inicio:.1f} s")
