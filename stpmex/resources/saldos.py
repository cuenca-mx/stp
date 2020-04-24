from typing import ClassVar, List
from xml.etree import ElementTree

from pydantic import PositiveFloat, PositiveInt
from pydantic.dataclasses import dataclass

from ..auth import compute_signature
from ..types import TipoOperacion
from .base import Resource


@dataclass
class Saldo(Resource):
    _endpoint: ClassVar[str] = '/ordenPago/consSaldoEnvRec'

    montoTotal: PositiveFloat
    tipoOperacion: TipoOperacion
    totalOperaciones: PositiveInt

    @classmethod
    def consulta_saldo_env_rec(cls) -> List['Saldo']:
        data = dict(empresa=cls.empresa, firma=cls._firma_consulta({}))
        resp = cls._client.post(cls._endpoint, data)
        saldos = []
        for saldo in resp['saldos']:
            del saldo['empresa']
            saldos.append(cls(**saldo))
        return saldos

    @classmethod
    def consulta(cls, cuenta: str) -> float:
        """
        cuenta es la CLABE de la empresa

        Based on:
        https://stpmex.zendesk.com/hc/es/articles/360002812571-consultaSaldoCuenta
        """
        client = cls._client
        firma = compute_signature(client.pkey, cuenta)
        data = f'''
<soapenv:Envelope
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:h2h="http://h2h.integration.spei.enlacefi.lgec.com/">
    <soapenv:Body>
        <h2h:consultaSaldoCuenta>
            <cuenta>{cuenta}</cuenta>
            <firma>{firma}</firma>
        </h2h:consultaSaldoCuenta>
    </soapenv:Body>
</soapenv:Envelope>
'''
        resp = client.session.post(client.soap_url, data)
        if not resp.ok:
            resp.raise_for_status()
        root = ElementTree.fromstring(resp.text)
        saldo = root.findtext('.//saldo')
        return float(saldo)
