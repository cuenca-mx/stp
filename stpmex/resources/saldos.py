from typing import ClassVar, List

from pydantic import PositiveFloat, PositiveInt
from pydantic.dataclasses import dataclass

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
        data = dict(empresa=cls.empresa, firma=cls._firma_consulta({}))
        resp = cls._client.post(cls._endpoint, data)
        saldos = []
        for saldo in resp['saldos']:
            del saldo['empresa']
            saldos.append(cls(**saldo))
        return saldos
