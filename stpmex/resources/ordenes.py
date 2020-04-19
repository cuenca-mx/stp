import datetime as dt
import random
import time
from dataclasses import field
from typing import Any, ClassVar, Dict, List, Optional, Union

import clabe
from clabe.types import Clabe
from pydantic import PositiveFloat, conint, constr, validator
from pydantic.dataclasses import dataclass

from ..auth import ORDEN_FIELDNAMES
from ..types import (
    Estado,
    MxPhoneNumber,
    PaymentCardNumber,
    Prioridad,
    TipoCuenta,
    digits,
    truncated_str,
)
from .base import Resource

STP_BANK_CODE = '90646'


@dataclass
class Orden(Resource):
    """
    Based on:
    https://stpmex.zendesk.com/hc/es/articles/360002682851-RegistraOrden-Dispersi%C3%B3n-
    """

    _endpoint: ClassVar[str] = '/ordenPago'
    _firma_fieldnames: ClassVar[List[str]] = ORDEN_FIELDNAMES

    monto: PositiveFloat
    conceptoPago: truncated_str(39)

    cuentaBeneficiario: Union[Clabe, PaymentCardNumber, MxPhoneNumber]
    nombreBeneficiario: truncated_str(39)
    institucionContraparte: digits(5, 5)

    cuentaOrdenante: Clabe
    nombreOrdenante: Optional[truncated_str(39)] = None
    institucionOperante: digits(5, 5) = STP_BANK_CODE

    tipoCuentaBeneficiario: Optional[TipoCuenta] = None
    tipoCuentaOrdenante: TipoCuenta = TipoCuenta.clabe.value

    claveRastreo: truncated_str(29) = field(
        default_factory=lambda: f'CR{int(time.time())}'
    )
    referenciaNumerica: conint(gt=0, lt=10 ** 7) = field(
        default_factory=lambda: random.randint(10 ** 6, 10 ** 7)
    )
    rfcCurpBeneficiario: constr(max_length=18) = 'ND'
    rfcCurpOrdenante: Optional[constr(max_length=18)] = None

    prioridad: int = Prioridad.alta.value
    medioEntrega: int = 3
    tipoPago: int = 1
    topologia: str = 'T'
    iva: Optional[float] = None

    id: Optional[int] = None

    def __post_init__(self):
        # Test before Pydantic coerces it to a float
        if not isinstance(self.monto, float):
            raise ValueError('monto must be a float')
        cb = self.cuentaBeneficiario
        self.tipoCuentaBeneficiario = self.get_tipo_cuenta(cb)

    @classmethod
    def registra(cls, **kwargs) -> 'Orden':
        orden = cls(**kwargs)
        endpoint = orden._endpoint + '/registra'
        resp = orden._client.put(endpoint, orden.to_dict())
        orden.id = resp['id']
        return orden

    @staticmethod
    def get_tipo_cuenta(cuenta: str) -> Optional[TipoCuenta]:
        cuenta_len = len(cuenta)
        if cuenta_len == 18:
            tipo = TipoCuenta.clabe
        elif cuenta_len in {15, 16}:
            tipo = TipoCuenta.card
        elif cuenta_len == 10:
            tipo = TipoCuenta.phone_number
        else:
            tipo = None
        return tipo

    @validator('institucionContraparte')
    def _validate_institucion(cls, v: str) -> str:
        if v not in clabe.BANKS.values():
            raise ValueError(f'{v} no se corresponde a un banco')
        return v


ORDEN_ENVIADA_STRIP = """
empresa
clavePago
cuentaBeneficiario2
nombreBeneficiario2
conceptoPago2
rfcCurpBeneficiario2
referenciaCobranza""".split()


@dataclass
class OrdenEnviada(Resource):
    _endpoint: ClassVar[str] = '/ordenPago/consOrdenesFech'

    monto: PositiveFloat
    conceptoPago: truncated_str(39)

    cuentaBeneficiario: Union[Clabe, PaymentCardNumber, MxPhoneNumber]
    nombreBeneficiario: truncated_str(39)
    institucionContraparte: digits(5, 5)

    cuentaOrdenante: Clabe
    nombreOrdenante: Optional[truncated_str(39)]
    institucionOperante: digits(5, 5)

    tipoCuentaBeneficiario: TipoCuenta
    tipoCuentaOrdenante: TipoCuenta

    claveRastreo: truncated_str(29)
    referenciaNumerica: conint(gt=0, lt=10 ** 7)
    rfcCurpBeneficiario: constr(max_length=18)
    rfcCurpOrdenante: constr(max_length=18)

    medioEntrega: int
    prioridad: int
    tipoPago: int
    topologia: str

    idCliente: str
    folioOrigen: str
    fechaOperacion: dt.date
    estado: Estado
    causaDevolucion: bool
    tsCaptura: dt.datetime
    tsLiquidacion: dt.datetime
    tsAcuseBanxico: dt.datetime
    tsEntrega: float  # segundos
    usuario: str

    tsDevolucion: Optional[float] = None  # segundos
    tsDevolucionRecibida: Optional[dt.datetime] = None
    claveRastreoDevolucion: Optional[str] = None

    @classmethod
    def consulta(
        cls, fecha_operacion: Optional[dt.date] = None
    ) -> List['OrdenEnviada']:
        if fecha_operacion:
            fecha = fecha_operacion.strftime('%Y%m%d')
        else:
            fecha = ''
        data = dict(
            empresa=cls.empresa,
            firma=cls.firma_consulta(fecha),
            estado=Estado.enviada
        )
        if fecha:
            data['fechaOperacion'] = fecha
        ordenes = cls._client.post(cls._endpoint, data)['lst']
        sanitized = [cls._sanitize_orden(orden) for orden in ordenes if orden]
        return [cls(**orden) for orden in sanitized]

    @staticmethod
    def _sanitize_orden(orden: Dict[str, Union[str, int]]) -> Dict[str, Any]:
        sanitized = {}
        for k, v in orden.items():
            if k in ORDEN_ENVIADA_STRIP:
                continue
            if k.startswith('ts'):
                v /= 10 ** 3  # convertir de milisegundos a segundos
            elif k == 'fechaOperacion':
                v = dt.datetime.strptime(str(v), '%Y%m%d')
            sanitized[k] = v
        return sanitized
