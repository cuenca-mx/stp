import datetime as dt
import random
import time
from dataclasses import field, make_dataclass
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
    TipoOperacion,
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

    @classmethod
    def _consulta(
        cls,
        tipo: Optional[TipoOperacion] = None,
        fechaOperacion: Optional[dt.date] = None,
        claveRastreo: Optional[str] = None,
        institucionOperante: Optional[int] = None,
    ) -> List['OrdenConsultada']:  # noqa: F821
        endpoint = cls._endpoint + '/consOrdenesFech'
        consulta = dict(empresa=cls.empresa)
        if tipo:
            consulta['estado'] = tipo
        if fechaOperacion:
            consulta['fechaOperacion'] = fechaOperacion.strftime('%Y%m%d')
            if claveRastreo and institucionOperante:
                consulta['claveRastreo'] = claveRastreo
                consulta['institucionOperante'] = institucionOperante
        consulta['firma'] = cls._firma_consulta(consulta)
        resp = cls._client.post(endpoint, consulta)['lst']
        sanitized = [cls._sanitize_consulta(orden) for orden in resp if orden]
        return sanitized

    @classmethod
    def consulta_recibidas(
        cls, fecha_operacion: Optional[dt.date] = None
    ) -> List['OrdenConsultada']:  # noqa: F821
        return cls._consulta(TipoOperacion.recibida, fecha_operacion)

    @classmethod
    def consulta_enviadas(
        cls, fecha_operacion: Optional[dt.date] = None
    ) -> List['OrdenConsultada']:  # noqa: F821
        return cls._consulta(TipoOperacion.enviada, fecha_operacion)

    @classmethod
    def consulta_clave_rastreo(
        cls,
        fechaOperacion: dt.date,
        claveRastreo: str,
        institucionOperante: int,
    ) -> 'OrdenConsultada':  # noqa: F821
        return cls._consulta(
            fechaOperacion=fechaOperacion,
            claveRastreo=claveRastreo,
            institucionOperante=institucionOperante,
        )

    @staticmethod
    def _sanitize_consulta(
        orden: Dict[str, Any]
    ) -> 'OrdenConsultada':  # noqa: F821
        sanitized = {}
        for k, v in orden.items():
            if k.startswith('ts'):
                v /= 10 ** 3  # convertir de milisegundos a segundos
                if v > 10 ** 9:
                    v = dt.datetime.fromtimestamp(v)
            elif k == 'fechaOperacion':
                v = dt.datetime.strptime(str(v), '%Y%m%d').date()
            elif k == 'estado':
                v = Estado(v)
            elif isinstance(v, str):
                v = v.rstrip()
            sanitized[k] = v
        return make_dataclass('OrdenConsultada', sanitized.keys())(**sanitized)
