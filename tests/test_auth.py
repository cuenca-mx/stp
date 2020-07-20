from stpmex.auth import (
    CUENTA_FIELDNAMES,
    ORDEN_FIELDNAMES,
    compute_signature,
    join_fields,
)


def test_join_fields_for_orden(orden):
    joined = (
        '||40072|TAMIZI|||CR1564969083|90646|1.20|1|40||646180110400000007|'
        '|40|Ricardo Sanchez|072691004495711499|ND||||||Prueba||||||5273144|'
        '|T||3|0|||'
    )
    assert join_fields(orden, ORDEN_FIELDNAMES) == joined


def test_join_fields_for_cuenta(cuenta):
    cuenta.cuenta = '646180157099999993'
    joined = '||TAMIZI|646180157099999993|SAHE800416HDFABC01||'
    assert join_fields(cuenta, CUENTA_FIELDNAMES) == joined


def test_compute_signature(client, orden):
    firma = (
        'KDNKDVVuyNt9oTXPAlofGXGH5L5IH9PAzOsx0JZFtmGlU+10QRf2RHSg0OVCnYYpu5sC3'
        'DJ6vlXuYM40+uNw0tMc0y8Dv26uO8Vv2GhOhMqaGk72LwgwgmqVg17xzjgGbJHzAzMav3'
        'fx4/3No+mSnf7vxpe4ePf6yK1yU5U28L4='
    )
    sig = compute_signature(client.pkey, join_fields(orden, ORDEN_FIELDNAMES))
    assert sig == firma
