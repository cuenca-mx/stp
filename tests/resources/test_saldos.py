import pytest
from requests import HTTPError

from stpmex.resources import Saldo

CLABE = '646180157000000004'


@pytest.mark.vcr
def test_consulta_saldo_env_rec(client):
    saldos = client.saldos.consulta_saldo_env_rec()
    assert len(saldos) == 2
    for saldo in saldos:
        assert isinstance(saldo, Saldo)


@pytest.mark.vcr
def test_consulta_saldo(client):
    saldo = client.saldos.consulta(CLABE)
    assert type(saldo) is float
    assert saldo > 0


@pytest.mark.vcr
def test_consulta_saldo_for_nonexistent_cuenta(client):
    with pytest.raises(HTTPError) as e:
        client.saldos.consulta('123456789012345678')
    assert e.value.response.status_code == 500
