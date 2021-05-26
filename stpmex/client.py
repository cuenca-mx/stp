import re
from typing import Any, ClassVar, Dict, List, NoReturn, Union

from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from requests import Response, Session

from .exc import (
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
    NoOrdenesEncontradas,
    NoServiceResponse,
    PldRejected,
    SameAccount,
    SignatureValidationError,
    StpmexException,
)
from .resources import CuentaFisica, Orden, Resource, Saldo
from .version import __version__ as client_version

DEMO_HOST = 'https://demo.stpmex.com:7024'
PROD_HOST = 'https://prod.stpmex.com'


class Client:
    base_url: str
    soap_url: str
    session: Session

    # resources
    cuentas: ClassVar = CuentaFisica
    ordenes: ClassVar = Orden
    saldos: ClassVar = Saldo

    def __init__(
        self,
        empresa: str,
        priv_key: str,
        priv_key_passphrase: str,
        demo: bool = False,
        base_url: str = None,
        soap_url: str = None,
        timeout: tuple = None,
    ):
        self.timeout = timeout
        self.session = Session()
        self.session.headers['User-Agent'] = f'stpmex-python/{client_version}'
        if demo:
            host_url = DEMO_HOST
            self.session.verify = False
        else:
            host_url = PROD_HOST
            self.session.verify = True
        self.base_url = base_url or f'{host_url}/speiws/rest'
        self.soap_url = (
            soap_url or f'{host_url}/spei/webservices/SpeiConsultaServices'
        )

        try:
            self.pkey = serialization.load_pem_private_key(
                priv_key.encode('utf-8'),
                priv_key_passphrase.encode('ascii'),
                default_backend(),
            )
        except (ValueError, TypeError, UnsupportedAlgorithm):
            raise InvalidPassphrase
        Resource.empresa = empresa
        Resource._client = self

    def post(
        self, endpoint: str, data: Dict[str, Any]
    ) -> Union[Dict[str, Any], List[Any]]:
        return self.request('post', endpoint, data)

    def put(
        self, endpoint: str, data: Dict[str, Any]
    ) -> Union[Dict[str, Any], List[Any]]:
        return self.request('put', endpoint, data)

    def delete(
        self, endpoint: str, data: Dict[str, Any]
    ) -> Union[Dict[str, Any], List[Any]]:
        return self.request('delete', endpoint, data)

    def request(
        self, method: str, endpoint: str, data: Dict[str, Any], **kwargs: Any
    ) -> Union[Dict[str, Any], List[Any]]:
        url = self.base_url + endpoint
        response = self.session.request(
            method,
            url,
            json=data,
            timeout=self.timeout,
            **kwargs,
        )
        self._check_response(response)
        resultado = response.json()
        if 'resultado' in resultado:  # Some responses are enveloped
            resultado = resultado['resultado']
        return resultado

    @staticmethod
    def _check_response(response: Response) -> None:
        if not response.ok:
            response.raise_for_status()
        resp = response.json()
        if isinstance(resp, dict):
            try:
                _raise_description_error_exc(resp)
            except KeyError:
                ...
            try:
                assert resp['descripcion']
                _raise_description_exc(resp)
            except (AssertionError, KeyError):
                ...
        response.raise_for_status()


def _raise_description_error_exc(resp: Dict) -> NoReturn:
    id = resp['resultado']['id']
    error = resp['resultado']['descripcionError']

    if id == 0 and error == 'No se recibió respuesta del servicio':
        raise NoServiceResponse(**resp['resultado'])
    elif id == 0 and error == 'Error validando la firma':
        raise SignatureValidationError(**resp['resultado'])
    elif id == 0 and re.match(r'El campo .+ es obligatorio', error):
        raise MandatoryField(**resp['resultado'])
    elif id == -1 and re.match(
        r'La clave de rastreo .+ ya fue utilizada', error
    ):
        raise ClaveRastreoAlreadyInUse(**resp['resultado'])
    elif id == -7 and re.match(r'La cuenta .+ no existe', error):
        raise AccountDoesNotExist(**resp['resultado'])
    elif id == -9 and re.match(r'La Institucion \d+ no es valida', error):
        raise InvalidInstitution(**resp['resultado'])
    elif id == -11 and re.match(r'El tipo de cuenta \d+ es invalido', error):
        raise InvalidAccountType(**resp['resultado'])
    elif id == -20 and re.match(r'El monto {.+} no es válido', error):
        raise InvalidAmount(**resp['resultado'])
    elif id == -22 and 'no coincide para la institucion operante' in error:
        raise BankCodeClabeMismatch(**resp['resultado'])
    elif id == -24 and re.match(r'Cuenta {\d+} - {MISMA_CUENTA}', error):
        raise SameAccount(**resp['resultado'])
    elif id == -34 and 'Clave rastreo invalida' in error:
        raise InvalidTrackingKey(**resp['resultado'])
    elif id == -100 and error.startswith('No se encontr'):
        raise NoOrdenesEncontradas
    elif id == -200 and 'Se rechaza por PLD' in error:
        raise PldRejected(**resp['resultado'])
    else:
        raise StpmexException(**resp['resultado'])


def _raise_description_exc(resp: Dict) -> NoReturn:
    id = resp['id']
    desc = resp['descripcion']

    if id == 0 and 'Cuenta en revisión' in desc:
        # STP regresa esta respuesta cuando se registra
        # una cuenta. No se levanta excepción porque
        # todas las cuentas pasan por este status.
        ...
    elif id == 1 and desc == 'rfc/curp invalido':
        raise InvalidRfcOrCurp(**resp)
    elif id == 1 and re.match(r'El campo \w+ es invalido', desc):
        raise InvalidField(**resp)
    elif id == 3 and desc == 'Cuenta Duplicada':
        raise DuplicatedAccount(**resp)
    elif id == 5 and re.match(r'El campo .* obligatorio \w+', desc):
        raise MandatoryField(**resp)
    else:
        raise StpmexException(**resp)
