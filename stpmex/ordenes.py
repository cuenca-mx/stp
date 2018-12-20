import random
import time

from .base import Resource
from .types import AccountType, Prioridad

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

ORDEN_DEFAULTS = dict(
    rfcCurpBeneficiario='ND',
    tipoPago=1,
    tipoCuentaBeneficiario=AccountType.CLABE.value,
    topologia='T',
    medioEntrega=3,
    prioridad=Prioridad.alta.value,
    claveRastreo=lambda: f'CR{int(time.time())}',
    referenciaNumerica=lambda: random.randint(10 ** 6, 10 ** 7)
)

VALIDATIONS = dict(
    nombreBeneficiario=dict(
        required=True,
        maxLength=39
    ),
    claveRastreo=dict(
        required=True,
        maxLength=30
    ),
    conceptoPago=dict(
        required=True
    ),
    referenciaNumerica=dict(
        required=True,
        maxLength=7
    )
)


class Orden(Resource):
    __fieldnames__ = ORDEN_FIELDNAMES
    __type__ = 'ns0:ordenPagoWS'
    __validations__ = VALIDATIONS
    _id = None
    _defaults = ORDEN_DEFAULTS

    def registra(self):
        self._is_valid()
        self.firma = self._compute_signature()
        resp = self._invoke_method('registraOrden')
        self._id = resp.id
        return resp
