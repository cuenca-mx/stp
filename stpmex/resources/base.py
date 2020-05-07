import datetime as dt
from dataclasses import asdict
from typing import Any, ClassVar, Dict, List

from ..auth import compute_signature, join_fields
from ..utils import strftime


class Resource:
    _client: ClassVar['stpmex.Client']  # noqa: F821
    _endpoint: ClassVar[str]
    _firma_fieldnames: ClassVar[List[str]]
    empresa: ClassVar[str]

    @property
    def firma(self):
        """
        Based on:
        https://stpmex.zendesk.com/hc/es/articles/360002796012-Firmas-Electr%C3%B3nicas-
        """
        joined_fields = join_fields(self, self._firma_fieldnames)
        return compute_signature(self._client.pkey, joined_fields)

    @classmethod
    def _firma_consulta(cls, consulta: Dict[str, Any]):
        joined = (
            f"|||"
            f"{cls.empresa}|"
            f"{consulta.get('fechaOperacion', '')}||"
            f"{consulta.get('claveRastreo', '')}|"
            f"{consulta.get('institucionOperante', '')}"
            f"||||||||||||||||||||||||||||||"
        )
        return compute_signature(cls._client.pkey, joined)

    def to_dict(self) -> Dict[str, Any]:
        base = dict()
        for k, v in asdict(self).items():
            if isinstance(v, dt.date):
                base[k] = strftime(v)
            elif v:
                base[k] = v
        return {**base, **dict(firma=self.firma, empresa=self.empresa)}
