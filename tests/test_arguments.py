from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Optional, Union

from tellurium.arguments import dataclass_to_obj, obj_to_dataclass
from tellurium.functional import FunListStr, FunStr


@dataclass
class Print:
    msg: str


@dataclass
class Main:
    print: Print
    secret: Union[Print, int]
    number: Optional[float] = None


@dataclass
class Empty:
    pass


def test_dataclass_to_obj():
    obj = dataclass_to_obj(Main)
    # assert obj == {}, str(obj)
    assert obj["print"]["msg"] == "<class 'str'>"
    assert obj["secret"] == dedent("""
        - ALT: Print
          ARGS:
            msg: <class 'str'>
        - ALT: int
          ARGS: <class 'int'>
        """).lstrip("\n")
    assert obj["number"] is None


def test_dataclass_to_obj_empty_dataclass():
    obj = dataclass_to_obj(Union[Empty, str])
    assert obj == dedent("""
        - ALT: Empty
        - ALT: str
          ARGS: <class 'str'>
        """).lstrip("\n"), str(obj)


def test_obj_to_dataclass():
    obj = {
        "print": {
            "msg": "Hello world!",
        },
        "secret": {
            "ALT": "int",
            "ARGS": 42,
        },
    }
    main = obj_to_dataclass(Main, obj)
    assert main.print.msg == "Hello world!"
    assert main.secret == 42
    assert main.number is None


def test_obj_to_dataclass_dataclass_for_alt():
    obj = {
        "print": {
            "msg": "Hello world!",
        },
        "secret": {
            "ALT": "Print",
            "ARGS": {
                "msg": 42,
            },
        },
        "number": 3.14,
    }
    main = obj_to_dataclass(Main, obj)
    assert main.print.msg == "Hello world!"
    assert main.secret.msg == "42"
    assert main.number == 3.14


def test_obj_to_dataclass_alt_without_args():
    obj = {
        "ALT": "Empty",
    }
    data = obj_to_dataclass(Union[Empty, str], obj)
    assert data == Empty(), str(data)


def test_obj_to_dataclass_file_stem():
    obj = {
        "ALT": "FileStem",
    }
    data = obj_to_dataclass(FunStr, obj, Path(__file__))
    assert data == "test_arguments", str(data)


def test_obj_to_dataclass_fun_wildcard():
    obj = {
        "ALT": "FunWildcard",
        "ARGS": {
            "pattern": "*.toml",
        },
    }
    data = obj_to_dataclass(FunListStr, obj)
    assert data == ["pyproject.toml"], str(data)
