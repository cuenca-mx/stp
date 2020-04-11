from pydantic.errors import PydanticValueError


class StpmexException(Exception):
    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def __repr__(self):
        return (
            self.__class__.__name__
            + '('
            + ', '.join(
                [
                    f'{attr}={repr(value)}'
                    for attr, value in self.__dict__.items()
                ]
            )
            + ')'
        )

    def __str__(self):
        return repr(self)


class InvalidPassphrase(StpmexException):
    """El passphrase es incorrecto"""


class InvalidAccountType(StpmexException):
    """Tipo de cuenta inválida"""


class SignatureValidationError(StpmexException):
    """Error validando la firma"""


class InvalidRfcOrCurp(StpmexException):
    """RFC o CURP inválido"""


class ClaveRastreoAlreadyInUse(StpmexException):
    """La clave de rastreo es repetida"""


class PldRejected(StpmexException):
    """'Orden sin cuenta ordenante. Se rechaza por PLD"""


class NoServiceResponse(StpmexException):
    """No se recibió respuesta del servicio"""


class BankCodeValidationError(PydanticValueError):
    code = 'clabe.bank_code'
    msg_template = 'código de banco no es válido'


class ClabeControlDigitValidationError(PydanticValueError):
    code = 'clabe.control_digit'
    msg_template = 'clabe dígito de control no es válido'
