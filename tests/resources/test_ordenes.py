import datetime as dt
import time
from typing import Any, Dict

import pytest

from stpmex import Client
from stpmex.resources import Orden, OrdenEnviada, OrdenRecibida
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
    enviadas = client.consulta_ordenes_enviadas()
    for orden in enviadas:
        assert type(orden) is OrdenEnviada


@pytest.mark.vcr
def test_consulta_ordenes_recibidas(client):
    recibidas = client.consulta_ordenes_recibidas()
    for orden in recibidas:
        assert type(orden) is OrdenRecibida


@pytest.mark.xfail(reason="Looks like STP hasn't implemented this yet")
@pytest.mark.vcr
def test_consulta_ordenes_enviadas_con_fecha(client):
    enviadas = client.consulta_ordenes_enviadas(dt.date(2020, 4, 20))
    for orden in enviadas:
        assert type(orden) is OrdenEnviada
