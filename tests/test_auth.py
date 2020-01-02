from stpmex.auth import (
    CUENTA_FIELDNAMES,
    ORDEN_FIELDNAMES,
    compute_signature,
    join_fields,
)


def test_join_fields_for_orden(orden):
    joined = (
        b'||40072|TAMIZI|||CR1564969083|90646|1.20|1|40||646180110400000007|'
        b'|40|Ricardo Sanchez|072691004495711499|ND||||||Prueba||||||5273144|'
        b'|T||3|1|||'
    )
    assert join_fields(orden, ORDEN_FIELDNAMES) == joined


def test_join_fields_for_cuenta(cuenta):
    cuenta.cuenta = '646180157099999993'
    joined = b'||TAMIZI|646180157099999993|SAHE800416HDFABC01||'
    assert join_fields(cuenta, CUENTA_FIELDNAMES) == joined


def test_compute_signature(client, orden):
    firma = (
        'QSESEqJTcn8hhK2QaA/z9VnIZDktwgPS1VWJxOooZt3vNEi2IKrIoPI+/O/SDo/lZAMAm'
        'xg6De7Sg/OALjibLPpLlONd0VLIa81xsF0FmP+22mT9MtPgf3/kGuZvgSKpzzzNbhxEM+'
        '/j4sgWw9ucbD0Oh+ajsN1MgKjIBaTC7SI='
    )
    sig = compute_signature(client.pkey, join_fields(orden, ORDEN_FIELDNAMES))
    assert sig == firma
