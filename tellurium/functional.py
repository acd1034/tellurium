import dataclasses as _dc
import re
import typing as _ty
from pathlib import Path

__all__ = [
    "FilePath",
    "FileName",
    "FileDir",
    "FileFmt",
    "PatSubst",
    "path_to_str",
    "Wildcard",
    "Matrix",
    "Placeholder",
    "BuiltinFunction",
]


@_dc.dataclass
class FilePath:
    pass


@_dc.dataclass
class FileName:
    pass


@_dc.dataclass
class FileDir:
    pass


@_dc.dataclass
class FileFmt:
    """Generate a file path using a format like ${parent}/${stem}${suffix}"""

    fmt: str


@_dc.dataclass
class PatSubst:
    pattern: str
    replacement: str
    texts: _ty.Union[str, list[str]]

    def run(self) -> _ty.Union[str, list[str]]:
        pattern = re.compile(f'^{self.pattern.replace("%", "(.*)")}$')
        repl = self.replacement.replace("%", r"\1")
        if isinstance(self.texts, str):
            return pattern.sub(repl, self.texts)
        else:
            return [pattern.sub(repl, text) for text in self.texts]


def path_to_str(path: Path) -> str:
    if path.is_dir():
        return f"{path}/"
    else:
        return str(path)


@_dc.dataclass
class Wildcard:
    pattern: str

    def run(self) -> list[str]:
        return [path_to_str(path) for path in Path(".").glob(self.pattern)]


@_dc.dataclass
class Matrix:
    pass


@_dc.dataclass
class Placeholder:
    key: str


BuiltinFunction = _ty.Union[
    FilePath,
    FileName,
    FileDir,
    FileFmt,
    PatSubst,
    Wildcard,
    Matrix,
    Placeholder,
]
