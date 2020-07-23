import re
import unicodedata
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Optional, Type

from clabe.types import validate_digits
from pydantic import ConstrainedStr, StrictStr, constr
from pydantic.validators import (
    constr_length_validator,
    constr_strip_whitespace,
    str_validator,
)

if TYPE_CHECKING:
    from pydantic.typing import CallableGenerator  # pragma: no cover


def unicode_to_ascii(unicode: str) -> str:
    v = unicodedata.normalize('NFKD', unicode).encode('ascii', 'ignore')
    return v.decode('ascii')


class AsciiStr(ConstrainedStr):
    @classmethod
    def validate(cls, value: str) -> str:
        value = super().validate(value)
        return unicode_to_ascii(value).strip()


class StpStr(AsciiStr):
    """
    based on:
    https://stpmex.zendesk.com/hc/es/articles/360038242071-Registro-de-Cuentas-de-Personas-f%C3%ADsicas
    """

    @classmethod
    def validate(cls, value: str) -> str:
        value = super().validate(value)
        value = re.sub(r'[-,.]', ' ', value)
        value = value.upper()
        return value


def truncated_str(length: int) -> Type[str]:
    namespace = dict(
        strip_whitespace=True, min_length=1, curtail_length=length
    )
    return type('TruncatedStrValue', (AsciiStr,), namespace)


def truncated_stp_str(length: int) -> Type[str]:
    namespace = dict(
        strip_whitespace=True, min_length=1, curtail_length=length
    )
    return type('TruncatedStpStrValue', (StpStr,), namespace)


def digits(
    min_length: Optional[int] = None, max_length: Optional[int] = None
) -> Type[str]:
    return constr(regex=r'^\d+$', min_length=min_length, max_length=max_length)


class Estado(str, Enum):
    """
    Based on: https://stpmex.zendesk.com/hc/es/articles/360040200791
    """

    capturada = 'C'
    pendiente_liberar = 'PL'
    liberada = 'L'
    pendiente_autorizar = 'PA'
    autorizada = 'A'
    enviada = 'E'
    liquidada = 'LQ'
    cancelada = 'CN'
    traspaso_liberado = 'TL'
    traspaso_capturado = 'TC'
    traspaso_autorizado = 'TA'
    traspaso_liquidado = 'TLQ'
    traspaso_cancelado = 'TCL'
    recibida = 'R'
    por_devolver = 'XD'
    devuelta = 'D'
    por_enviar_confirmacion = 'CXO'
    confirmacion_enviada = 'CCE'
    confirmada = 'CCO'
    confirmacion_rechazada = 'CCR'
    por_cancelar = 'XC'
    cancelada_local = 'CL'
    cancelada_rechazada = 'CR'
    rechazada_local = 'RL'
    cancelada_adapter = 'CA'
    rechazada_adapter = 'RA'
    enviada_adapter = 'EA'
    rechazada_banxico = 'RB'
    eliminada = 'EL'
    por_retornar = 'XR'
    retornada = 'RE'
    exportacion_poa = 'EP'
    exportacion_cep = 'EC'


class Prioridad(int, Enum):
    normal = 0
    alta = 1


class TipoCuenta(int, Enum):
    card = 3
    phone_number = 10
    clabe = 40


class Genero(str, Enum):
    mujer = 'M'
    hombre = 'H'


class Curp(StrictStr):
    min_length = 18
    max_length = 18
    regex = re.compile(r'^[A-Z]{4}[0-9]{6}[A-Z]{6}[A-Z|0-9][0-9]$')


class Rfc(StrictStr):
    min_length = 12
    max_length = 13


class EntidadFederativa(int, Enum):
    # NE = Nacido en el Extranjero. Aún STP no soporte
    AS = 1  # Aguascalientes
    BC = 2  # Baja California
    BS = 3  # Baja California Sur
    CC = 4  # Campeche
    CS = 5  # Chiapas
    CH = 6  # Chihuahua
    CL = 7  # Coahuila
    CM = 8  # Colima
    DF = 9  # CDMX
    DG = 10  # Durango
    MC = 11  # Estado de México
    GT = 12  # Guanajuato
    GR = 13  # Guerrero
    HG = 14  # Hidalgo
    JC = 15  # Jalisco
    MN = 16  # Michoacan
    MS = 17  # Morelos
    NT = 18  # Nayarit
    NL = 19  # Nuevo León
    OC = 20  # Oaxaca
    PL = 21  # Puebla
    QT = 22  # Querétaro
    QR = 23  # Quintana Roo
    SP = 24  # San Luis Potosí
    SL = 25  # Sinaloa
    SR = 26  # Sonora
    TC = 27  # Tabasco
    TS = 28  # Tamualipas
    TL = 29  # Tlaxcala
    VZ = 30  # Veracruz
    YN = 31  # Yucatán
    ZS = 32  # Zacatecas


class TipoOperacion(str, Enum):
    enviada = 'E'
    recibida = 'R'


class MxPhoneNumber(str):
    strip_whitespace: ClassVar[bool] = True
    min_length: ClassVar[int] = 10
    max_length: ClassVar[int] = 10

    @classmethod
    def __get_validators__(cls) -> 'CallableGenerator':
        yield str_validator
        yield constr_strip_whitespace
        yield constr_length_validator
        yield validate_digits
