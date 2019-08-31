import pytest
from zeep.exceptions import TransportError

from stpmex.client import Client
from stpmex.exc import InvalidPassphrase, StpmexException

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


def test_client():
    pkey_passphrase = '12345678'
    empresa = 'TAMIZI'
    client = Client(
        empresa=empresa,
        priv_key=PKEY,
        priv_key_passphrase=pkey_passphrase,
        demo=True,
    )
    assert client.soap_client.get_type('ns0:ordenPagoWS')


@pytest.mark.vcr
def test_forbidden_without_vpn(orden):
    pkey_passphrase = '12345678'
    empresa = 'TAMIZI'
    client = Client(
        empresa=empresa, priv_key=PKEY, priv_key_passphrase=pkey_passphrase
    )
    with pytest.raises(TransportError) as exc_info:
        client.registrar_orden(orden)
    assert exc_info.value.status_code == 403


def test_incorrect_passphrase():
    pkey_passphrase = 'incorrect'
    empresa = 'TAMIZI'
    with pytest.raises(InvalidPassphrase):
        Client(
            empresa=empresa, priv_key=PKEY, priv_key_passphrase=pkey_passphrase
        )


@pytest.mark.vcr
def test_response_error(client, orden):
    orden.medioEntrega = 9999999
    with pytest.raises(StpmexException) as exc_info:
        client.registrar_orden(orden)
    exc = exc_info.value
    assert exc.descripcionError
    assert repr(exc)
    assert str(exc)
