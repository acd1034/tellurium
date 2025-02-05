from dataclasses import dataclass
from textwrap import dedent
from typing import Optional, Union

from tellurium.arguments import dataclass_to_obj, obj_to_dataclass


@dataclass
class Print:
    msg: str


@dataclass
class Main:
    print: Print
    secret: Union[Print, int]
    number: Optional[float] = None


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


def test_obj_to_dataclass2():
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
