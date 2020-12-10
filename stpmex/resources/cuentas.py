import datetime as dt
from typing import Any, ClassVar, Dict, List, Optional, Union

from clabe.types import Clabe
from pydantic import conint, constr
from pydantic.dataclasses import dataclass

from ..auth import CUENTA_FIELDNAMES
from ..types import (
    Curp,
    EntidadFederativa,
    Genero,
    MxPhoneNumber,
    Rfc,
    digits,
    truncated_stp_str,
)
from .base import Resource

MAX_LOTE = 100


@dataclass
class Cuenta(Resource):
    _base_endpoint: ClassVar[str] = '/cuentaModule'
    _lote_endpoint: ClassVar[str]
    _firma_fieldnames: ClassVar[List[str]] = CUENTA_FIELDNAMES

    cuenta: Clabe
    rfcCurp: Union[Curp, Rfc]

    @classmethod
    def alta(cls, **kwargs) -> 'Cuenta':
        cuenta = cls(**kwargs)
        cuenta._alta()
        return cuenta

    def _alta(self) -> None:
        self._client.put(self._endpoint, self.to_dict())

    @classmethod
    def alta_lote(cls, lote: List['Cuenta']) -> Dict[str, Dict[str, Any]]:
        if len(lote) > MAX_LOTE:
            return {
                **cls.alta_lote(lote[:MAX_LOTE]),
                **cls.alta_lote(lote[MAX_LOTE:]),
            }
        cuentas = dict(cuentasFisicas=[cuenta.to_dict() for cuenta in lote])
        return dict(
            zip(
                [cuenta.cuenta for cuenta in lote],
                cls._client.put(cls._lote_endpoint, cuentas),
            )
        )

    def baja(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        endpoint = endpoint or self._endpoint
        data = dict(
            cuenta=self.cuenta,
            empresa=self.empresa,
            rfcCurp=self.rfcCurp,
            firma=self.firma,
        )
        return self._client.delete(endpoint, data)


@dataclass
class CuentaFisica(Cuenta):
    """
    Based on:
    https://stpmex.zendesk.com/hc/es/articles/360038242071-Registro-de-Cuentas-de-Personas-f%C3%ADsicas
    """

    _endpoint: ClassVar[str] = Cuenta._base_endpoint + '/fisica'
    _lote_endpoint: ClassVar[str] = Cuenta._base_endpoint + '/fisicas'

    nombre: truncated_stp_str(50)
    apellidoPaterno: truncated_stp_str(50)
    paisNacimiento: conint(ge=0, le=275)
    fechaNacimiento: dt.date

    apellidoMaterno: Optional[truncated_stp_str(50)] = None
    genero: Optional[Genero] = None
    # Esperando a que STP agregue Nacido en el Extranjero
    entidadFederativa: Optional[EntidadFederativa] = None
    actividadEconomica: Optional[conint(ge=28, le=74)] = None
    calle: Optional[truncated_stp_str(60)] = None
    numeroExterior: Optional[truncated_stp_str(10)] = None
    numeroInterior: Optional[truncated_stp_str(5)] = None
    colonia: Optional[truncated_stp_str(50)] = None
    alcaldiaMunicipio: Optional[truncated_stp_str(50)] = None
    cp: Optional[digits(5, 5)] = None
    email: Optional[constr(max_length=150)] = None
    idIdentificacion: Optional[digits(max_length=20)] = None
    telefono: Optional[MxPhoneNumber] = None
