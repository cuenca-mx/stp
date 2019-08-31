import dataclasses
import os

from OpenSSL import crypto
from zeep import Client as SoapClient

from .auth import compute_signature, join_fields
from .exc import InvalidPassphrase, StpmexException
from .orden import Orden

here = os.path.abspath(os.path.dirname(__file__))
DEMO_WSDL = os.path.join(here, 'demo.wsdl')
PROD_WSDL = os.path.join(here, 'prod.wsdl')


class Client:
    def __init__(
        self,
        empresa: str,
        priv_key: str,
        priv_key_passphrase: str,
        demo: bool = False,
    ):
        self.empresa = empresa
        try:
            self._pkey = crypto.load_privatekey(
                crypto.FILETYPE_PEM,
                priv_key,
                priv_key_passphrase.encode('ascii'),
            )
        except crypto.Error:
            raise InvalidPassphrase
        if demo:
            wsdl = DEMO_WSDL
        else:
            wsdl = PROD_WSDL
        self.soap_client = SoapClient(wsdl)

    def soap_orden(self, orden: Orden) -> 'zeep.objects.ordenPagoWS':
        SoapOrden = self.soap_client.get_type('ns0:ordenPagoWS')
        soap_orden = SoapOrden(**dataclasses.asdict(orden))
        soap_orden.empresa = self.empresa
        return soap_orden

    def registrar_orden(
        self, orden: Orden
    ) -> 'zeep.objects.speiServiceResponse':
        soap_orden = self.soap_orden(orden)
        joined_fields = join_fields(soap_orden)
        soap_orden.firma = compute_signature(self._pkey, joined_fields)
        resp = self.soap_client.service['registraOrden'](soap_orden)
        if 'descripcionError' in resp and resp.descripcionError:
            raise StpmexException(**resp.__values__)
        return resp
