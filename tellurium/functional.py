import dataclasses as _dc
import typing as _ty

__all__ = [
    "FunBasename",
    "FunStr",
]


@_dc.dataclass
class FunBasename:
    pass


FunStr = _ty.Union[str, FunBasename]
