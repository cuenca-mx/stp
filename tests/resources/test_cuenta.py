import pytest
from clabe import generate_new_clabes

from stpmex.resources import CuentaFisica


@pytest.mark.vcr
def test_alta_cuenta(client, cuenta_dict):
    cuenta = client.cuentas.alta(**cuenta_dict)
    assert cuenta


@pytest.mark.vcr
def test_baja_cuenta(client, cuenta):
    assert cuenta.baja()


@pytest.mark.vcr
def test_update(client, cuenta_dict):
    del cuenta_dict['rfcCurp']
    old_curp = 'SAHE800416HDFABC01'
    new_curp = 'SAHE800416HDFABC02'
    client.cuentas.alta(**cuenta_dict, rfcCurp=old_curp)
    cuenta = CuentaFisica.update(old_curp, **cuenta_dict, rfcCurp=new_curp)
    cuenta.baja()


@pytest.mark.vcr
def test_update_fail_same_curp(client, cuenta_dict):
    cuenta = client.cuentas.alta(**cuenta_dict)
    with pytest.raises(ValueError):
        CuentaFisica.update(cuenta_dict['rfcCurp'], **cuenta_dict)
    cuenta.baja()


@pytest.mark.vcr
@pytest.mark.parametrize('num_cuentas', [95, 450])
def test_alta_lote(client, cuenta_dict, num_cuentas):
    del cuenta_dict['cuenta']
    clabes = generate_new_clabes(num_cuentas, '6461801570')

    lote = []
    for clabe in clabes:
        cuenta = CuentaFisica(**cuenta_dict, cuenta=clabe)
        lote.append(cuenta)
    resp = client.cuentas.alta_lote(lote)
    assert list(resp.keys()) == clabes
    assert all(r['id'] == 0 for r in resp.values())
    assert all(r['descripcion'] == '' for r in resp.values())
    for cuenta in lote:
        cuenta.baja()
