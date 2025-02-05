import dataclasses as _dc
import typing as _ty
from argparse import ArgumentParser
from pathlib import Path

import yaml as _yaml

from . import functional as _fun

__all__ = [
    "obj_to_dataclass",
    "dataclass_to_obj",
    "emit_yaml_example",
    "make_from_arguments",
]
_T = _ty.TypeVar("_T")
_LIST_STR_FUNCTIONS = [ty for ty in _ty.get_args(_fun.FunListStr) if ty != list[str]]


def _is_optional(cls: type[_ty.Any]):
    return (
        _ty.get_origin(cls) is _ty.Union
        and len(_ty.get_args(cls)) == 2
        and _ty.get_args(cls)[1] is type(None)
    )


@_dc.dataclass
class _ObjToDataclass:
    filepath: _ty.Optional[Path]

    def get_union(self, cls: type[_T], data) -> _T:
        for alternative in _ty.get_args(cls):
            if alternative.__name__ == data["ALT"]:
                return self.run(alternative, data.get("ARGS", {}))
        raise RuntimeError(f'{data["ALT"]=} should be {cls=}')

    def run(self, cls: type[_T], data) -> _T:
        if _dc.is_dataclass(cls):
            assert isinstance(data, dict), f"{type(data)=}"
            field_types = {f.name: f.type for f in _dc.fields(cls)}
            return cls(**{k: self.run(field_types[k], v) for k, v in data.items()})

        if _is_optional(cls):
            if data is not None:
                return self.run(_ty.get_args(cls)[0], data)
            else:
                return None

        if _ty.get_origin(cls) is _ty.Union:
            assert isinstance(data, dict), f"{type(data)=}"
            union = self.get_union(cls, data)

            if isinstance(union, _fun.FileStem) and str in _ty.get_args(cls):
                return self.filepath.stem

            # TODO: list, list[Union[str, ...]] に対応する
            if any(isinstance(union, fun) for fun in _LIST_STR_FUNCTIONS) and (
                list[str] in _ty.get_args(cls)
            ):
                return union.run()

            return union

        if _ty.get_origin(cls) is list:
            assert isinstance(data, list), f"{type(data)=}"
            return [self.run(_ty.get_args(cls)[0], item) for item in data]

        return cls(data)


def obj_to_dataclass(cls: type[_T], data, filepath: _ty.Optional[Path] = None) -> _T:
    return _ObjToDataclass(filepath).run(cls, data)


def _get_field_default(field: _dc.Field) -> _ty.Any:
    # デフォルト値がある場合はそのまま使用
    if field.default is not _dc.MISSING:
        return field.default
    if field.default_factory is not _dc.MISSING:
        return field.default_factory()

    # デフォルトがない場合
    return dataclass_to_obj(field.type)


class _YAMLDumper(_yaml.SafeDumper):
    pass


class _BlockScalarStr(str):
    pass


def _block_scalar_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


_yaml.add_representer(_BlockScalarStr, _block_scalar_representer, Dumper=_YAMLDumper)


def dataclass_to_obj(cls: type[_ty.Any]) -> _ty.Any:
    if _dc.is_dataclass(cls):
        return {f.name: _get_field_default(f) for f in _dc.fields(cls)}

    if _is_optional(cls):
        return dataclass_to_obj(_ty.get_args(cls)[0])

    if _ty.get_origin(cls) is _ty.Union:
        alternatives = []
        for alternative in _ty.get_args(cls):
            arguments = dataclass_to_obj(alternative)
            if isinstance(arguments, dict) and not arguments:
                obj = {"ALT": alternative.__name__}
            else:
                obj = {"ALT": alternative.__name__, "ARGS": arguments}
            alternatives.append(obj)
        return _BlockScalarStr(_yaml.dump(alternatives, Dumper=_YAMLDumper))

    if _ty.get_origin(cls) is list:
        return [dataclass_to_obj(_ty.get_args(cls)[0])]
    if cls is list:
        return [f"{_ty.Any}"]

    # その他の型の場合
    return f"{cls}"


def emit_yaml_example(cls: type[_ty.Any], filepath: Path):
    yaml_obj = dataclass_to_obj(cls)
    with open(filepath, "w") as f:
        _yaml.dump(
            yaml_obj, f, Dumper=_YAMLDumper, default_flow_style=False, sort_keys=False
        )


def make_from_arguments(cls: type[_T]) -> _T:
    parser = ArgumentParser()
    parser.add_argument("--config", type=Path, help="YAML configuration file")
    parser.add_argument("--emit_example", type=Path, help="emit configuration example")
    args = parser.parse_args()

    if args.emit_example is not None:
        emit_yaml_example(cls, args.emit_example)
        quit()

    with open(args.config) as f:
        data = _yaml.safe_load(f)

    return obj_to_dataclass(cls, data, filepath=args.config)
