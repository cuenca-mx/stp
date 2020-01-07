import re
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Optional, Type

import luhnmod10
from clabe import BANK_NAMES, BANKS, compute_control_digit
from pydantic import StrictStr, constr
from pydantic.errors import LuhnValidationError, NotDigitError
from pydantic.types import PaymentCardNumber as PydanticPaymentCardNumber
from pydantic.validators import (
    constr_length_validator,
    constr_strip_whitespace,
    str_validator,
)

from . import exc

if TYPE_CHECKING:
    from pydantic.typing import CallableGenerator  # pragma: no cover


def truncated_str(length) -> Type[str]:
    return constr(strip_whitespace=True, min_length=1, curtail_length=length)


def digits(
    min_length: Optional[int] = None, max_length: Optional[int] = None
) -> Type[str]:
    return constr(regex=r'^\d+$', min_length=min_length, max_length=max_length)


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
    min_length = 13
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


def validate_digits(v: str) -> str:
    if not v.isdigit():
        raise NotDigitError
    return v


class Clabe(str):
    """
    Based on: https://es.wikipedia.org/wiki/CLABE
    """

    strip_whitespace: ClassVar[bool] = True
    min_length: ClassVar[int] = 18
    max_length: ClassVar[int] = 18

    def __init__(self, clabe: str):
        self.bank_code_3_digits = clabe[:3]
        self.bank_code_5_digits = BANKS[clabe[:3]]
        self.bank_name = BANK_NAMES[self.bank_code_5_digits]

    @classmethod
    def __get_validators__(cls) -> 'CallableGenerator':
        yield str_validator
        yield constr_strip_whitespace
        yield constr_length_validator
        yield validate_digits
        yield cls.validate_bank_code
        yield cls.validate_control_digit
        yield cls

    @classmethod
    def validate_bank_code(cls, clabe: str) -> str:
        if clabe[:3] not in BANKS.keys():
            raise exc.BankCodeValidationError
        return clabe

    @classmethod
    def validate_control_digit(cls, clabe: str) -> str:
        if clabe[-1] != compute_control_digit(clabe):
            raise exc.ClabeControlDigitValidationError
        return clabe


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


class PaymentCardNumber(PydanticPaymentCardNumber):
    min_length: ClassVar[int] = 15
    max_length: ClassVar[int] = 16

    @classmethod
    def validate_luhn_check_digit(cls, card_number: str) -> str:
        if not luhnmod10.valid(card_number):
            raise LuhnValidationError
        return card_number
