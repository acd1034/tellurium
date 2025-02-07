import dataclasses as _dc
import re
import typing as _ty
from pathlib import Path

__all__ = [
    "FileName",
    "FileStem",
    "FunPatSubst",
    "FunWildcard",
    "BuiltinFunction",
]


@_dc.dataclass
class FileName:
    pass


@_dc.dataclass
class FileStem:
    pass


@_dc.dataclass
class FunPatSubst:
    pattern: str
    replacement: str
    texts: _ty.Union[str, list[str]]

    def run(self) -> _ty.Union[str, list[str]]:
        pattern = re.compile(f'^{self.pattern.replace("%", "(.*)")}$')
        repl = self.replacement.replace("%", r"\1")
        if isinstance(self.texts, str):
            pattern.sub(repl, self.texts)
        else:
            return [pattern.sub(repl, text) for text in self.texts]


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


BuiltinFunction = _ty.Union[FileName, FileStem, FunPatSubst, FunWildcard]
