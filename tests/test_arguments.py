from dataclasses import dataclass
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
    actual = dataclass_to_obj(Main)
    expected = {
        "print": {"msg": "<class 'str'>"},
        "secret": {"alternative": "Print", "arguments": {"msg": "<class 'str'>"}},
        "number": None,
    }
    assert actual == expected, str(actual)


def test_obj_to_dataclass():
    obj = {
        "print": {
            "msg": "Hello world!",
        },
        "secret": {
            "alternative": "int",
            "arguments": 42,
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
            "alternative": "Print",
            "arguments": {
                "msg": 42,
            },
        },
        "number": 3.14,
    }
    main = obj_to_dataclass(Main, obj)
    assert main.print.msg == "Hello world!"
    assert main.secret.msg == "42"
    assert main.number == 3.14
