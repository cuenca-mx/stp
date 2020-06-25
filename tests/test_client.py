import pytest
from requests import HTTPError

from stpmex.client import Client
from stpmex.exc import (
    BankCodeClabeMismatch,
    ClaveRastreoAlreadyInUse,
    DuplicatedAccount,
    InvalidAccountType,
    InvalidField,
    InvalidPassphrase,
    InvalidRfcOrCurp,
    InvalidTrackingKey,
    NoServiceResponse,
    PldRejected,
    SameAccount,
    SignatureValidationError,
    StpmexException,
)

PKEY = """Bag Attributes
    friendlyName: prueba
    localKeyID: 54 69 6D 65 20 31 33 32 34 35 39 35 30 31 35 33 33 30
Key Attributes: <No Attributes>
-----BEGIN ENCRYPTED PRIVATE KEY-----
MIICxjBABgkqhkiG9w0BBQ0wMzAbBgkqhkiG9w0BBQwwDgQIAPOngEipSGICAggA
MBQGCCqGSIb3DQMHBAi3RX0+96FhJASCAoAGX5N8jxBqlyKk8MTz/Q3a/V4fnCNA
IlPYybMbO00HbMNXw20Kn+WzK73VZtBdEf+8CBcqZMwuC0gqn5pdnOVqP0wz8MU5
AlWu0ZJpLo8npjQyV5Smrk1OvFREQ9skuJRBgYjPPTgdYmVN77ZGeFwJlf+OqOIM
JWZIFZY6z3cXn6CnaAvQ6L+/smRt1Us0gEMe1m7rln0M6m64EbOFsOonzp7/CRTd
Mmlsk93Lg8G/uwGrL3gf1TDep1yM1KKMu6pWZ+6zT26ykwNsdUg0NUCpeWeYWzDZ
KLzQ90U+/XlBPbPg/8gK6tc1dresvPbRcvNu+IJq8HbKuUkjrDeFor5Wezic3CyO
/g//2LJbJGy7Ak4V4W9J46GLD8B3fqyDz0itCBRcmlrtAXiV0azb1isD+j8LdOXN
vo/EPjLJnVdbP2RHiKKdp0Kq2FyRbigP86UujxwxfOxNN/w6m48agmVsj1uB6zBp
hn0D/MLkMtoV7NmGhayRxFXs5sO1G/lWOoR96PgNzOur8xnPzvG7ysPv9qKRO1XS
JEaGZXUUQ/sq2d6nLWMz9YLh7YVaVsRfIcUGPnmFh/bj30Pk52PodF6kN3JYftvn
ZaXgOf6E4NLpHjtYRTzyVZQamenDAlvHQwZE284hDPShuJwxFr6FOSR/GrgqbN4d
cOK898ofM+ZxkNkm5LrU3RAXR3336HU9XMky4UCV9L3CA51IlTMqt/CkddFhsjrw
W4Zo1Aj8G7FaoDm7XhkLGDwVjf0Ua1O4YHRpSgVSkrXeBgW7P4Tc+53nFns3rwxs
uzF/x9tl2+BdiDjPOhSRuoa1ypilODdpOGKNKuf0vu2jAbbzDILBYOfw
-----END ENCRYPTED PRIVATE KEY-----"""


@pytest.mark.vcr
def test_forbidden_without_vpn(client):
    client = Client('TAMIZI', PKEY, '12345678', demo=False)
    with pytest.raises(HTTPError) as exc_info:
        client.request('get', '/application.wadl', {})
    assert exc_info.value.response.status_code == 403


def test_incorrect_passphrase():
    with pytest.raises(InvalidPassphrase):
        Client('TAMIZI', PKEY, 'incorrect')


REGISTRA = '/ordenPago/registra'
FISICA = '/cuentaModule/fisica'


@pytest.mark.parametrize(
    'client_exc,endpoint,expected_exc',
    [
        (
            (
                REGISTRA,
                dict(
                    resultado=dict(
                        descripcionError='No se recibió respuesta '
                        'del servicio',
                        id=0,
                    )
                ),
            ),
            REGISTRA,
            NoServiceResponse,
        ),
        (
            (
                FISICA,
                dict(
                    resultado=dict(
                        descripcionError='El tipo de cuenta 3 es invalido',
                        id=-11,
                    )
                ),
            ),
            FISICA,
            InvalidAccountType,
        ),
        (
            (
                FISICA,
                dict(
                    resultado=dict(
                        descripcionError='Error validando la firma', id=0,
                    )
                ),
            ),
            FISICA,
            SignatureValidationError,
        ),
        (
            (
                FISICA,
                dict(
                    resultado=dict(
                        descripcionError='La clave de rastreo {foo123} '
                        'para la fecha {20200314} de la '
                        'institucion {123} ya fue utilizada',
                        id=-1,
                    )
                ),
            ),
            FISICA,
            ClaveRastreoAlreadyInUse,
        ),
        (
            (
                FISICA,
                dict(
                    resultado=dict(
                        descripcionError='Orden sin cuenta ordenante. '
                        'Se rechaza por PLD',
                        id=-200,
                    )
                ),
            ),
            FISICA,
            PldRejected,
        ),
        (
            (
                FISICA,
                dict(
                    resultado=dict(
                        descripcionError='La cuenta CLABE {6461801570} '
                        'no coincide para la institucion '
                        'operante {40072}',
                        id=-22,
                    )
                ),
            ),
            FISICA,
            BankCodeClabeMismatch,
        ),
        (
            (
                FISICA,
                dict(
                    resultado=dict(
                        descripcionError='Cuenta {646180157000000000} - '
                        '{MISMA_CUENTA}',
                        id=-24,
                    )
                ),
            ),
            FISICA,
            SameAccount,
        ),
        (
            (
                FISICA,
                dict(
                    resultado=dict(
                        descripcionError='Clave rastreo invalida : ABC123',
                        id=-34,
                    )
                ),
            ),
            FISICA,
            InvalidTrackingKey,
        ),
        (
            (
                FISICA,
                dict(
                    resultado=dict(
                        descripcionError='unknown code', id=9999999,
                    )
                ),
            ),
            FISICA,
            StpmexException,
        ),
        (
            (REGISTRA, dict(descripcion='Cuenta Duplicada', id=1)),
            REGISTRA,
            DuplicatedAccount,
        ),
        (
            (REGISTRA, dict(descripcion='El campo NOMBRE es invalido', id=1)),
            REGISTRA,
            InvalidField,
        ),
        (
            (REGISTRA, dict(descripcion='rfc/curp invalido', id=1)),
            REGISTRA,
            InvalidRfcOrCurp,
        ),
        (
            (REGISTRA, dict(descripcion='unknown code', id=999999)),
            REGISTRA,
            StpmexException,
        ),
    ],
    indirect=['client_exc'],
)
def test_errors(client_exc: Client, endpoint: str, expected_exc: type) -> None:
    with pytest.raises(StpmexException) as exc_info:
        client_exc.put(endpoint, dict(firma='{hola}'))
    exc = exc_info.value
    assert type(exc) is expected_exc
    assert repr(exc)
    assert str(exc)
