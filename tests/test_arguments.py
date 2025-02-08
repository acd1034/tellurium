from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Any, Optional, Union

import pytest

from tellurium.arguments import dataclass_to_obj, isinstance_generic, obj_to_dataclass


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
    # assert obj == {}, f"{obj=}"
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
    expected = dedent("""
        - ALT: Empty
        - ALT: str
          ARGS: <class 'str'>
        """).lstrip("\n")
    assert obj == expected, f"{obj=}"


def test_dataclass_to_obj_list_of_union():
    obj = dataclass_to_obj(list[Union[int, str]])
    expected = [
        {
            "ALT": "int",
            "ARGS": "<class 'int'>",
        },
        {
            "ALT": "str",
            "ARGS": "<class 'str'>",
        },
    ]
    assert obj == expected, f"{obj=}"


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


def test_obj_to_dataclass_dict():
    obj = {
        "print": {
            "msg": "Goodbye",
        },
        "msg": "Hello world!",
        "secret": 42,
    }
    data = obj_to_dataclass(dict, obj)
    assert isinstance(data["print"], dict)
    assert data["print"]["msg"] == "Goodbye"
    assert data["msg"] == "Hello world!"
    assert data["secret"] == 42


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
    assert data == Empty(), f"{data=}"


def test_obj_to_dataclass_file_path():
    obj = {
        "FUNC": "FilePath",
    }
    data = obj_to_dataclass(str, obj, Path(__file__))
    assert data.endswith("test_arguments.py"), f"{data=}"


def test_obj_to_dataclass_file_name():
    obj = {
        "FUNC": "FileName",
    }
    data = obj_to_dataclass(str, obj, Path(__file__))
    assert data == "test_arguments.py", f"{data=}"


def test_obj_to_dataclass_union_without_alt():
    obj = {
        "ALT": "int",
        "ARGS": 42,
    }
    data = obj_to_dataclass(Union[int, str], obj)
    assert data == 42, f"{data=}"

    obj = 42
    data = obj_to_dataclass(Union[int, str], obj)
    assert data == 42, f"{data=}"


def test_obj_to_dataclass_wildcard():
    obj = {
        "FUNC": "Wildcard",
        "ARGS": {
            "pattern": "*.toml",
        },
    }
    data = obj_to_dataclass(list[str], obj)
    assert data == ["pyproject.toml"], f"{data=}"


def test_obj_to_dataclass_pat_subst():
    obj = {
        "FUNC": "PatSubst",
        "ARGS": {
            "pattern": "%.c",
            "replacement": "%.o",
            "texts": ["foo.c", "bar.c", "baz.c"],
        },
    }
    data = obj_to_dataclass(list[str], obj)
    assert data == ["foo.o", "bar.o", "baz.o"], f"{data=}"


def test_obj_to_dataclass_pat_subst_str():
    obj = {
        "FUNC": "PatSubst",
        "ARGS": {
            "pattern": "%.py",
            "replacement": "%_copy.py",
            "texts": {
                "FUNC": "FilePath",
            },
        },
    }
    data = obj_to_dataclass(str, obj, Path(__file__))
    assert data.endswith("test_arguments_copy.py"), f"{data=}"


def test_obj_to_dataclass_pat_subst_with_wildcard():
    obj = {
        "FUNC": "PatSubst",
        "ARGS": {
            "pattern": "%.toml",
            "replacement": "%.yaml",
            "texts": {
                "FUNC": "Wildcard",
                "ARGS": {
                    "pattern": "*.toml",
                },
            },
        },
    }
    data = obj_to_dataclass(list[str], obj)
    assert data == ["pyproject.yaml"], f"{data=}"


def test_obj_to_dataclass_function_in_union():
    obj = {
        "FUNC": "FileName",
    }
    data = obj_to_dataclass(Union[str, int], obj, filepath=Path(__file__))
    assert data == "test_arguments.py", f"{data=}"


def test_obj_to_dataclass_check_loc_in_error():
    @dataclass
    class X:
        int_or_float: Union[int, float]

    obj = {
        "int_or_float": "raw string",
    }
    with pytest.raises(RuntimeError, match=r"test_arguments\.py:int_or_float.*"):
        obj_to_dataclass(X, obj, filepath=Path(__file__))


def test_obj_to_dataclass_any():
    obj = 3.14
    data = obj_to_dataclass(Any, obj)
    assert isinstance(data, float), f"{data=}"
    assert data == 3.14, f"{data=}"


def test_obj_to_dataclass_function_in_any():
    obj = [
        "Hello",
        {"FUNC": "FileName"},
    ]
    data = obj_to_dataclass(Any, obj, filepath=Path(__file__))
    assert isinstance_generic(data, list[str]), f"{data=}"
    assert data[0] == "Hello", f"{data[0]=}"
    assert data[1] == "test_arguments.py", f"{data[1]=}"


def placeholder(key: str) -> dict:
    return {
        "FUNC": "Placeholder",
        "ARGS": {
            "key": key,
        },
    }


def wildcard(pattern: str) -> dict:
    return {
        "FUNC": "Wildcard",
        "ARGS": {
            "pattern": pattern,
        },
    }


def patsubst(pattern: str, replacement: str, texts: Union[list[str], str]) -> dict:
    return {
        "FUNC": "PatSubst",
        "ARGS": {
            "pattern": pattern,
            "replacement": replacement,
            "texts": texts,
        },
    }


def filename() -> dict:
    return {"FUNC": "FileName"}


def test_obj_to_dataclass_matrix():
    obj = {
        "FUNC": "Matrix",
        "ARGS": {
            "mapping": {
                "number": [0, 1, 2, 3],
            },
            "template": placeholder("number"),
        },
    }
    data = obj_to_dataclass(list[int], obj)
    assert isinstance_generic(data, list[int]), f"{data=}"
    assert data == [0, 1, 2, 3], f"{data=}"


def test_obj_to_dataclass_matrix_dataclass_template():
    @dataclass
    class X:
        msg: str
        number: int

    obj = {
        "FUNC": "Matrix",
        "ARGS": {
            "mapping": {
                "number": [0, 1, 2, 3],
            },
            "template": {
                "msg": "Hello",
                "number": placeholder("number"),
            },
        },
    }
    data = obj_to_dataclass(cls=list[X], data=obj)
    assert isinstance_generic(data, list[X]), f"{data=}"
    assert all(item.msg == "Hello" for item in data), f"{data=}"
    for i, item in enumerate(data):
        assert item.number == i


def test_obj_to_dataclass_function_in_dict():
    obj = {
        "msg": {
            "FUNC": "FileName",
        },
    }
    data = obj_to_dataclass(cls=dict, data=obj, filepath=Path(__file__))
    assert isinstance(data, dict), f"{data=}"
    assert data["msg"] == "test_arguments.py", f"{data["msg"]=}"


def test_obj_to_dataclass_matrix_dict_template():
    numbers = [0, 1, 2, 42]
    obj = {
        "FUNC": "Matrix",
        "ARGS": {
            "mapping": {
                "number": numbers,
            },
            "template": {
                "msg": "Hello",
                "number": placeholder("number"),
            },
        },
    }
    data = obj_to_dataclass(cls=list[dict], data=obj)
    assert isinstance_generic(data, list[dict]), f"{data=}"
    assert all(item["msg"] == "Hello" for item in data), f"{data=}"
    for item, n in zip(data, numbers):
        assert item["number"] == n, f"{data=}"


@dataclass
class Task:
    input: str
    output: str
    config: str


def test_obj_to_dataclass_matrix_with_other_function():
    obj = {
        "FUNC": "Matrix",
        "ARGS": {
            "mapping": {
                "input": wildcard("*.toml"),
            },
            "template": {
                "input": placeholder("input"),
                "output": patsubst("%.toml", "%.png", placeholder("input")),
                "config": filename(),
            },
        },
    }
    data = obj_to_dataclass(cls=list[Task], data=obj, filepath=Path(__file__))
    assert isinstance_generic(data, list[Task]), f"{data=}"
    assert len(data) == 1, f"{data=}"
    expected = Task("pyproject.toml", "pyproject.png", "test_arguments.py")
    assert data[0] == expected, f"{data=}"


def test_obj_to_dataclass_type_conversion_in_dict_key():
    obj = {
        42: "no_extension",
    }
    data = obj_to_dataclass(cls=dict[str, str], data=obj)
    assert isinstance_generic(data, dict[str, str]), f"{data=}"
    assert "42" in data, f"{data=}"
    assert data["42"] == "no_extension", f"{data["42"]=}"
