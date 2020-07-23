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
DEMO_BASE_URL = f'{DEMO_HOST}/speidemows/rest'
DEMO_SOAP_URL = f'{DEMO_HOST}/speidemo/webservices/SpeiConsultaServices'

PROD_HOST = 'https://prod.stpmex.com'
PROD_BASE_URL = f'{PROD_HOST}/speiws/rest'
PROD_SOAP_URL = f'{PROD_HOST}/spei/webservices/SpeiConsultaServices'


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
    ):
        self.session = Session()
        self.session.headers['User-Agent'] = f'stpmex-python/{client_version}'
        if demo:
            self.base_url = DEMO_BASE_URL
            self.soap_url = DEMO_SOAP_URL
            self.session.verify = False
        else:
            self.base_url = PROD_BASE_URL
            self.soap_url = PROD_SOAP_URL
            self.session.verify = True
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
        response = self.session.request(method, url, json=data, **kwargs,)
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
                if 'descripcionError' in resp['resultado']:
                    _raise_description_error_exc(resp)
            except KeyError:
                if 'descripcion' in resp and resp['descripcion']:
                    _raise_description_exc(resp)
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

    if id == 1 and desc == 'Cuenta Duplicada':
        raise DuplicatedAccount(**resp)
    elif id == 1 and desc == 'rfc/curp invalido':
        raise InvalidRfcOrCurp(**resp)
    elif id == 1 and re.match(r'El campo \w+ es invalido', desc):
        raise InvalidField(**resp)
    else:
        raise StpmexException(**resp)
