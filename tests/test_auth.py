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
        '|T||3||||'
    )
    assert join_fields(orden, ORDEN_FIELDNAMES) == joined


def test_join_fields_for_cuenta(cuenta):
    cuenta.cuenta = '646180157099999993'
    joined = '||TAMIZI|646180157099999993|SAHE800416HDFABC01||'
    assert join_fields(cuenta, CUENTA_FIELDNAMES) == joined


def test_compute_signature(client, orden):
    firma = (
        'nuW3v3gV5GqQCGiIfUGOrENSZK+bYRR3RZ8xT0wNm+p+XowkogURPEuFRk2SwkjNn6HUN'
        'XP3OkHFe92s0ViyLad7nN5n8pIvmGdOLopBtXvYBNhJmuCw2D32oGDWm7fKydW17NR9BY'
        'xJFdqSJzMGq4dquFI3ZuG6YfVHo4NYE5A='
    )
    sig = compute_signature(client.pkey, join_fields(orden, ORDEN_FIELDNAMES))
    assert sig == firma
