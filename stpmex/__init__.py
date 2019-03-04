"""
Configuraciones iniciales para utilizar el cliente posteriormente
"""
from zeep import Client
from zeep.transports import Transport
from OpenSSL import crypto
from requests import Session
from .ordenes import Orden
from .base import STP_EMPRESA, STP_PREFIJO, STP_PRIVKEY, STP_PRIVKEY_PASSPHRASE

DEFAULT_WSDL = ('https://demo.stpmex.com:7024/speidemo/webservices/SpeiActual'
                'izaServices?wsdl')


def configure(empresa: str, priv_key: str, priv_key_passphrase: str,
              prefijo: int, wsdl_path: str = DEFAULT_WSDL, proxy: str = None,
              proxy_user: str = None, proxy_password: str = None):
    """
    Configura las credenciales y parámetros necesarios para poder hacer
    peticiones a STP
    :param empresa: Nombre de la empresa
    :param priv_key: Contenido de la llave privada
    :param priv_key_passphrase: Password de la llave privada
    :param prefijo: Prefijo en STP
    :param wsdl_path: URL del WSDL a utilizar
    :param proxy: Si es necesario, se puede especificar un proxy
    :param proxy_user: Usuario del proxy
    :param proxy_password: Contraseña del proxy
    :return:
    """
    base.STP_EMPRESA = empresa
    base.STP_PRIVKEY = crypto.load_privatekey(
        crypto.FILETYPE_PEM, priv_key, priv_key_passphrase. encode('ascii'))
    base.STP_PRIVKEY_PASSPHRASE = priv_key_passphrase
    base.STP_PREFIJO = prefijo
    base.WSDL_PATH = wsdl_path

    base.ACTUALIZA_CLIENT = Client(wsdl_path)
    if proxy is not None:
        base.ACTUALIZA_CLIENT = Client(
            wsdl_path,
            transport=Transport(session=Session(proxies={
                    'https': f"https://{proxy_user}:{proxy_password}@{proxy}",
                    'http':  f"http://{proxy_user}:{proxy_password}@{proxy}"
                })
            )
        )
