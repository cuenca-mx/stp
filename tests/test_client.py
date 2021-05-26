import pytest
from requests import HTTPError

from stpmex.client import Client
from stpmex.exc import (
    AccountDoesNotExist,
    BankCodeClabeMismatch,
    ClaveRastreoAlreadyInUse,
    DuplicatedAccount,
    InvalidAccountType,
    InvalidAmount,
    InvalidField,
    InvalidInstitution,
    InvalidPassphrase,
    InvalidRfcOrCurp,
    InvalidTrackingKey,
    MandatoryField,
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

ORDEN_PAGO_ENDPOINT = '/ordenPago/registra'
CUENTA_ENDPOINT = '/cuentaModule/fisica'


def _desc_error(desc, id):
    return dict(resultado=dict(descripcionError=desc, id=id))


@pytest.mark.vcr
def test_forbidden_without_vpn(client):
    client = Client('TAMIZI', PKEY, '12345678', demo=False)
    with pytest.raises(HTTPError) as exc_info:
        client.request('get', '/application.wadl', {})
    assert exc_info.value.response.status_code == 403


def test_incorrect_passphrase():
    with pytest.raises(InvalidPassphrase):
        Client('TAMIZI', PKEY, 'incorrect')


@pytest.mark.parametrize(
    'client_mock,endpoint,expected_exc',
    [
        (
            _desc_error('No se recibió respuesta del servicio', 0),
            ORDEN_PAGO_ENDPOINT,
            NoServiceResponse,
        ),
        (
            _desc_error('Error validando la firma', 0),
            ORDEN_PAGO_ENDPOINT,
            SignatureValidationError,
        ),
        (
            _desc_error('El campo &lt;CONCEPTO PAGO> es obligatorio', 0),
            ORDEN_PAGO_ENDPOINT,
            MandatoryField,
        ),
        (
            _desc_error(
                'La clave de rastreo {foo123} para la fecha {20200314} de '
                'la institucion {123} ya fue utilizada',
                -1,
            ),
            ORDEN_PAGO_ENDPOINT,
            ClaveRastreoAlreadyInUse,
        ),
        (
            _desc_error('La cuenta {646180257067226640} no existe ', -7),
            ORDEN_PAGO_ENDPOINT,
            AccountDoesNotExist,
        ),
        (
            _desc_error('La Institucion 90679 no es valida', -9),
            ORDEN_PAGO_ENDPOINT,
            InvalidInstitution,
        ),
        (
            _desc_error('El tipo de cuenta 3 es invalido', -11),
            ORDEN_PAGO_ENDPOINT,
            InvalidAccountType,
        ),
        (
            _desc_error('El monto {500.0} no es válido', -20),
            ORDEN_PAGO_ENDPOINT,
            InvalidAmount,
        ),
        (
            _desc_error(
                'La cuenta CLABE {6461801570} no coincide para la '
                'institucion operante {40072}',
                -22,
            ),
            ORDEN_PAGO_ENDPOINT,
            BankCodeClabeMismatch,
        ),
        (
            _desc_error('Cuenta {646180157000000000} - {MISMA_CUENTA}', -24),
            ORDEN_PAGO_ENDPOINT,
            SameAccount,
        ),
        (
            _desc_error('Clave rastreo invalida : ABC123', -34),
            ORDEN_PAGO_ENDPOINT,
            InvalidTrackingKey,
        ),
        (
            _desc_error(
                'Orden sin cuenta ordenante. Se rechaza por PLD', -200
            ),
            ORDEN_PAGO_ENDPOINT,
            PldRejected,
        ),
        (
            _desc_error('unknown code', 9999999),
            ORDEN_PAGO_ENDPOINT,
            StpmexException,
        ),
        (
            dict(descripcion='Cuenta Duplicada', id=3),
            CUENTA_ENDPOINT,
            DuplicatedAccount,
        ),
        (
            dict(descripcion='El campo NOMBRE es invalido', id=1),
            CUENTA_ENDPOINT,
            InvalidField,
        ),
        (
            dict(descripcion='rfc/curp invalido', id=1),
            CUENTA_ENDPOINT,
            InvalidRfcOrCurp,
        ),
        (
            dict(descripcion='unknown code', id=999999),
            CUENTA_ENDPOINT,
            StpmexException,
        ),
        (
            dict(
                descripcion='El campo Apellido materno '
                'obligatorio 6461801500000000',
                id=5,
            ),
            CUENTA_ENDPOINT,
            MandatoryField,
        ),
    ],
    indirect=['client_mock'],
)
def test_errors(
    client_mock: Client, endpoint: str, expected_exc: type
) -> None:
    with pytest.raises(expected_exc) as exc_info:
        client_mock.put(endpoint, dict(firma='{hola}'))
    exc = exc_info.value
    assert repr(exc)
    assert str(exc)


@pytest.mark.vcr
def test_account_registration(client) -> None:
    client = Client('TAMIZI', PKEY, '12345678')
    response = client.put(CUENTA_ENDPOINT, dict(firma='{hola}'))
    assert response['id'] == 0
    assert response['descripcion'] == 'Cuenta en revisión.'
