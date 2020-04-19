import datetime as dt
import time
from typing import Any, Dict

import pytest

from stpmex import Client
from stpmex.exc import StpmexException
from stpmex.resources import Orden
from stpmex.types import TipoCuenta


@pytest.mark.vcr
def test_registra_orden(client: Client, orden_dict: Dict[str, Any]):
    orden_dict['claveRastreo'] = f'CR{int(time.time())}'
    orden = client.ordenes.registra(**orden_dict)
    assert isinstance(orden.id, int)


@pytest.mark.parametrize(
    'cuenta, tipo',
    [
        ('072691004495711499', TipoCuenta.clabe),
        ('4000000000000002', TipoCuenta.card),
        ('5512345678', TipoCuenta.phone_number),
        ('123', None),
    ],
)
def test_tipoCuentaBeneficiario(cuenta: str, tipo: TipoCuenta):
    assert Orden.get_tipo_cuenta(cuenta) == tipo


@pytest.mark.vcr
def test_consulta_ordenes_enviadas(client):
    enviadas = client.ordenes.consulta_enviadas()
    assert len(enviadas) > 0


@pytest.mark.vcr
def test_consulta_ordenes_recibidas(client):
    recibidas = client.ordenes.consulta_recibidas()
    assert len(recibidas) > 0


@pytest.mark.xfail(
    raises=StpmexException, reason="fails in demo but works in prod"
)
@pytest.mark.vcr
def test_consulta_ordenes_enviadas_con_fecha(client):
    enviadas = client.ordenes.consulta_enviadas(dt.date(2020, 4, 20))
    assert len(enviadas) > 0


@pytest.mark.xfail(
    raises=StpmexException, reason="can't find the transaction in demo"
)
@pytest.mark.vcr
def test_consulta_orden_por_clave_rastreo(client):
    client.ordenes.consulta_clave_rastreo(
        dt.date(2020, 4, 20), 'CR1564969083', 90646
    )
