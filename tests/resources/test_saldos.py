import pytest

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
