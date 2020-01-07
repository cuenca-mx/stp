from typing import Any, ClassVar, Dict, List, Union

from OpenSSL import crypto
from requests import Response, Session

from .exc import InvalidPassphrase, StpmexException
from .resources import CuentaFisica, Orden, Resource
from .version import __version__ as client_version

DEMO_BASE_URL = 'https://demo.stpmex.com:7024/speidemows/rest'
PROD_BASE_URL = 'https://prod.stpmex.com/speiws/rest'


class Client:

    base_url: str
    demo: bool
    headers: Dict[str, str]
    session: Session

    # resources
    cuentas: ClassVar = CuentaFisica
    ordenes: ClassVar = Orden

    def __init__(
        self,
        empresa: str,
        priv_key: str,
        priv_key_passphrase: str,
        demo: bool = False,
    ):
        self.session = Session()
        self.headers = {'User-Agent': f'stpmex-python/{client_version}'}
        if demo:
            self.base_url = DEMO_BASE_URL
        else:
            self.base_url = PROD_BASE_URL
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
            method, url, json=data, headers=self.headers, **kwargs
        )
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
                        raise StpmexException(**resp['resultado'])
                except KeyError:
                    if 'descripcion' in resp and resp['descripcion']:
                        raise StpmexException(**resp)
        response.raise_for_status()
