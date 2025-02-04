import dataclasses as _dc
import typing as _ty
from argparse import ArgumentParser
from pathlib import Path

import yaml

__all__ = [
    "obj_to_dataclass",
    "dataclass_to_obj",
    "emit_yaml_example",
    "make_from_arguments",
]
_T = _ty.TypeVar("_T")


def _is_optional(cls: type[_ty.Any]):
    return (
        _ty.get_origin(cls) is _ty.Union
        and len(_ty.get_args(cls)) == 2
        and _ty.get_args(cls)[1] is type(None)
    )


def obj_to_dataclass(cls: type[_T], data) -> _T:
    if _dc.is_dataclass(cls):
        assert isinstance(data, dict), f"{type(data)=}"
        field_types = {f.name: f.type for f in _dc.fields(cls)}
        return cls(**{k: obj_to_dataclass(field_types[k], v) for k, v in data.items()})

    if _is_optional(cls):
        if data is not None:
            return obj_to_dataclass(_ty.get_args(cls)[0], data)
        else:
            return None

    if _ty.get_origin(cls) is _ty.Union:
        assert isinstance(data, dict), f"{type(data)=}"
        for alternative in _ty.get_args(cls):
            if alternative.__name__ == data["alternative"]:
                return obj_to_dataclass(alternative, data["arguments"])
        raise RuntimeError(f"{data['alternative']=} should be {cls=}")

    if _ty.get_origin(cls) is list:
        assert isinstance(data, list), f"{type(data)=}"
        return [obj_to_dataclass(_ty.get_args(cls)[0], item) for item in data]

    return cls(data)


def _get_field_default(field: _dc.Field) -> _ty.Any:
    # デフォルト値がある場合はそのまま使用
    if field.default is not _dc.MISSING:
        return field.default
    if field.default_factory is not _dc.MISSING:
        return field.default_factory()

    # デフォルトがない場合
    return dataclass_to_obj(field.type)


def dataclass_to_obj(cls: type[_ty.Any]) -> _ty.Any:
    if _dc.is_dataclass(cls):
        return {f.name: _get_field_default(f) for f in _dc.fields(cls)}

    if _is_optional(cls):
        if nested_types := _ty.get_args(cls):
            return dataclass_to_obj(nested_types[0])
        else:
            return f"{cls}"

    if _ty.get_origin(cls) is _ty.Union:
        assert (nested_types := _ty.get_args(cls))
        return {
            "alternative": nested_types[0].__name__,
            "arguments": dataclass_to_obj(nested_types[0]),
        }

    if _ty.get_origin(cls) is list:
        if nested_types := _ty.get_args(cls):
            return [dataclass_to_obj(nested_types[0])]
        else:
            return ["<_ty.Any>"]

    # その他の型の場合
    return f"{cls}"


def emit_yaml_example(cls: type[_ty.Any], filepath: Path):
    yaml_dict = dataclass_to_obj(cls)
    with open(filepath, "w") as f:
        yaml.safe_dump(yaml_dict, f, default_flow_style=False, sort_keys=False)


def make_from_arguments(cls: type[_T]) -> _T:
    parser = ArgumentParser()
    parser.add_argument("--config", type=Path, help="YAML configuration file")
    parser.add_argument("--emit_example", type=Path, help="emit configuration example")
    args = parser.parse_args()

    if args.emit_example is not None:
        emit_yaml_example(cls, args.emit_example)
        quit()

    with open(args.config) as f:
        data = yaml.safe_load(f)

    return obj_to_dataclass(cls, data)
