from typing import ClassVar, List

from pydantic.dataclasses import dataclass
from pydantic import PositiveFloat, PositiveInt

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
    def consulta(cls) -> List['Saldo']:
        joined = f'|||{cls.empresa}||||||||||||||||||||||||||||||||||'
        firma = compute_signature(cls._client.pkey, joined.encode('ascii'))
        data = dict(empresa=cls.empresa, firma=firma)
        resp = cls._client.post(cls._endpoint, data)
        saldos = []
        for saldo in resp['saldos']:
            del saldo['empresa']
            saldos.append(cls(**saldo))
        return saldos
