import dataclasses as _dc
import typing as _ty

__all__ = [
    "FileStem",
    "FunStr",
]


@_dc.dataclass
class FileStem:
    pass


FunStr = _ty.Union[str, FileStem]
