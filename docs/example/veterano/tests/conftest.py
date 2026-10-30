import sys
import threading
from pathlib import Path

import pytest
import requests

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / ".." / "site-treino"))

import servidor  # noqa: E402  (o site de treino, usado como servidor de teste)


@pytest.fixture(scope="session")
def site():
    srv = servidor.criar_servidor(porta=0, dia=1, silencioso=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


@pytest.fixture(autouse=True)
def site_no_estado_inicial(site):
    requests.get(site + "/_dev/reset", timeout=5)
