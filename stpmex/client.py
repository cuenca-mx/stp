from typing import Any, ClassVar, Dict, List, Union

from OpenSSL import crypto
from requests import Response, Session

from .exc import (
    ClaveRastreoAlreadyInUse,
    InvalidAccountType,
    InvalidPassphrase,
    InvalidRfcOrCurp,
    NoOrdenesEncontradas,
    NoServiceResponse,
    PldRejected,
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
            self.pkey = crypto.load_privatekey(
                crypto.FILETYPE_PEM,
                priv_key,
                priv_key_passphrase.encode('ascii'),
            )
        except crypto.Error:
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
        if response.ok:
            resp = response.json()
            if isinstance(resp, dict):
                try:
                    if 'descripcionError' in resp['resultado']:
                        id = resp['resultado']['id']
                        error = resp['resultado']['descripcionError']
                        if id == -11:
                            raise InvalidAccountType(**resp['resultado'])
                        elif (
                            id == 0
                            and error == 'No se recibió respuesta del servicio'
                        ):
                            raise NoServiceResponse(**resp['resultado'])
                        elif id == 0 and error == 'Error validando la firma':
                            raise SignatureValidationError(**resp['resultado'])
                        elif id == -1:
                            raise ClaveRastreoAlreadyInUse(**resp['resultado'])
                        elif id == -100 and error.startswith('No se encontr'):
                            raise NoOrdenesEncontradas
                        elif id == -200:
                            raise PldRejected(**resp['resultado'])
                        else:
                            raise StpmexException(**resp['resultado'])
                except KeyError:
                    if 'descripcion' in resp and resp['descripcion']:
                        id = resp['id']
                        if id == 1:
                            raise InvalidRfcOrCurp(**resp)
                        else:
                            raise StpmexException(**resp)
        response.raise_for_status()
