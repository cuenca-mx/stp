from base64 import b64encode
from enum import Enum
from typing import List

from OpenSSL import crypto

CUENTA_FIELDNAMES = """
    empresa
    cuenta
    rfcCurp
""".split()


ORDEN_FIELDNAMES = """
    institucionContraparte
    empresa
    fechaOperacion
    folioOrigen
    claveRastreo
    institucionOperante
    monto
    tipoPago
    tipoCuentaOrdenante
    nombreOrdenante
    cuentaOrdenante
    rfcCurpOrdenante
    tipoCuentaBeneficiario
    nombreBeneficiario
    cuentaBeneficiario
    rfcCurpBeneficiario
    emailBeneficiario
    tipoCuentaBeneficiario2
    nombreBeneficiario2
    cuentaBeneficiario2
    rfcCurpBeneficiario2
    conceptoPago
    conceptoPago2
    claveCatUsuario1
    claveCatUsuario2
    clavePago
    referenciaCobranza
    referenciaNumerica
    tipoOperacion
    topologia
    usuario
    medioEntrega
    prioridad
    iva
    """.split()
SIGN_DIGEST = 'RSA-SHA256'


def join_fields(obj: 'Resource', fieldnames: List[str]) -> bytes:  # noqa: F821
    joined_fields = []
    for field in fieldnames:
        value = getattr(obj, field, None)
        if isinstance(value, float):
            value = f'{value:.2f}'
        elif isinstance(value, Enum) and value:
            value = value.value
        joined_fields.append(str(value or ''))
    return '||' + '|'.join(joined_fields) + '||'


def compute_signature(pkey: crypto.PKey, text: str) -> str:
    signature = crypto.sign(pkey, text.encode('utf-8'), SIGN_DIGEST)
    return b64encode(signature).decode('ascii')
