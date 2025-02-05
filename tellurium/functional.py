import dataclasses as _dc
import typing as _ty
from pathlib import Path

__all__ = [
    "FileStem",
    "FunStr",
    "FunWildcard",
    "FunListStr",
]


@_dc.dataclass
class FileStem:
    pass


FunStr = _ty.Union[str, FileStem]


def _path_to_str(path: Path) -> str:
    if path.is_dir():
        return f"{path}/"
    else:
        return str(path)


@_dc.dataclass
class FunWildcard:
    pattern: FunStr

    def run(self) -> list[str]:
        return [_path_to_str(path) for path in Path(".").glob(self.pattern)]


# TODO: list[str] を list[FunStr] に置き換える
FunListStr = _ty.Union[list[str], FunWildcard]
