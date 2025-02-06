import dataclasses as _dc
import re
import typing as _ty
from pathlib import Path

__all__ = [
    "FileName",
    "FileStem",
    "StrFunction",
    "FunWildcard",
    "FunPatSubst",
    "ListStrFunction",
]


@_dc.dataclass
class FileName:
    pass


@_dc.dataclass
class FileStem:
    pass


StrFunction = _ty.Union[FileName, FileStem]


def _path_to_str(path: Path) -> str:
    if path.is_dir():
        return f"{path}/"
    else:
        return str(path)


@_dc.dataclass
class FunWildcard:
    pattern: str

    def run(self) -> list[str]:
        return [_path_to_str(path) for path in Path(".").glob(self.pattern)]


@_dc.dataclass
class FunPatSubst:
    pattern: str
    replacement: str
    texts: list[str]

    def run(self) -> list[str]:
        pattern = f'^{self.pattern.replace("%", "(.*)")}$'
        return [
            re.sub(pattern, self.replacement.replace("%", r"\1"), text)
            for text in self.texts
        ]


ListStrFunction = _ty.Union[FunWildcard, FunPatSubst]
