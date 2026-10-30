import asyncio

import httpx
import pytest

import coletor_async
from coletor_async import LimitadorDeRitmo, baixar, coletar


def rodar(corotina):
    return asyncio.run(corotina)


def test_semaforo_limita_quantos_rodam_ao_mesmo_tempo():
    async def principal():
        semaforo = asyncio.Semaphore(3)
        ativos, maximo = 0, 0

        async def tarefa():
            nonlocal ativos, maximo
            async with semaforo:
                ativos += 1
                maximo = max(maximo, ativos)
                await asyncio.sleep(0.02)
                ativos -= 1

        await asyncio.gather(*(tarefa() for _ in range(12)))
        return maximo

    assert rodar(principal()) == 3


def test_limitador_espaca_o_inicio_dos_pedidos():
    async def principal():
        limitador = LimitadorDeRitmo(0.05)
        loop = asyncio.get_running_loop()
        inicios = []

        async def pedido():
            await limitador.esperar()
            inicios.append(loop.time())

        await asyncio.gather(*(pedido() for _ in range(5)))
        return sorted(inicios)

    inicios = rodar(principal())
    folgas = [b - a for a, b in zip(inicios, inicios[1:])]
    assert all(f >= 0.045 for f in folgas)


def test_limitador_sem_intervalo_nao_espera_nada():
    async def principal():
        limitador = LimitadorDeRitmo(0.0)
        loop = asyncio.get_running_loop()
        inicio = loop.time()
        for _ in range(50):
            await limitador.esperar()
        return loop.time() - inicio

    assert rodar(principal()) < 0.1


def executar_baixar(respostas):
    """Roda baixar() contra uma lista fixa de respostas, sem rede."""
    chamadas = iter(respostas)

    def manipulador(requisicao):
        return next(chamadas)

    async def principal():
        dormidas = []

        async def dormir(segundos):
            dormidas.append(segundos)

        transporte = httpx.MockTransport(manipulador)
        async with httpx.AsyncClient(transport=transporte) as cliente:
            resposta = await baixar(cliente, "http://x/", asyncio.Semaphore(2),
                                    LimitadorDeRitmo(0), tentativas=4,
                                    dormir=dormir)
        return resposta, dormidas

    return rodar(principal())


def test_baixar_repete_503_obedecendo_o_retry_after():
    resposta, dormidas = executar_baixar([
        httpx.Response(503, headers={"Retry-After": "2"}),
        httpx.Response(503),
        httpx.Response(200, text="ok"),
    ])
    assert resposta.text == "ok"
    assert dormidas == [2.0, 1.0]    # Retry-After na primeira, backoff na segunda


def test_baixar_repete_504_como_o_pipeline_principal():
    resposta, dormidas = executar_baixar([httpx.Response(504),
                                          httpx.Response(200, text="ok")])
    assert resposta.text == "ok" and dormidas == [0.5]


def test_retry_after_em_formato_de_data_cai_no_backoff():
    data = "Wed, 21 Oct 2026 07:28:00 GMT"
    resposta, dormidas = executar_baixar([
        httpx.Response(503, headers={"Retry-After": data}),
        httpx.Response(200, text="ok")])
    assert resposta.text == "ok" and dormidas == [0.5]


def test_baixar_nao_repete_404():
    with pytest.raises(httpx.HTTPStatusError):
        executar_baixar([httpx.Response(404)])


def test_baixar_desiste_depois_das_tentativas():
    with pytest.raises(RuntimeError, match="4 tentativas"):
        executar_baixar([httpx.Response(503)] * 4)


def test_coleta_assincrona_traz_as_20_vagas_com_descricao(site):
    vagas = rodar(coletar(site, concorrencia=5, intervalo=0.0))
    assert len(vagas) == 20
    assert len({v["id_externo"] for v in vagas}) == 20
    assert all(v["descricao"] for v in vagas)


def test_assincrono_e_sequencial_trazem_os_mesmos_ids(site):
    import requests
    from bs4 import BeautifulSoup
    from parsers import ler_vagas_da_pagina

    ids = []
    for pagina in (1, 2, 3):
        resposta = requests.get(f"{site}/vagas/?pagina={pagina}", timeout=5)
        sopa = BeautifulSoup(resposta.content, "lxml")
        ids += [v["id_externo"] for v in ler_vagas_da_pagina(sopa, site)]
    vagas = rodar(coletar(site, concorrencia=4, intervalo=0.0))
    assert sorted(v["id_externo"] for v in vagas) == sorted(ids)


def test_uma_falha_no_detalhe_nao_derruba_as_outras(site, monkeypatch):
    original = coletor_async.baixar

    async def baixar_que_falha(cliente, url, *resto, **nomeados):
        if url.endswith("/vagas/v001"):
            raise RuntimeError("falha simulada")
        return await original(cliente, url, *resto, **nomeados)

    monkeypatch.setattr(coletor_async, "baixar", baixar_que_falha)
    vagas = {v["id_externo"]: v for v in rodar(coletar(site, 5, 0.0))}
    assert len(vagas) == 20
    assert vagas["v001"]["descricao"] is None
    assert vagas["v002"]["descricao"]
