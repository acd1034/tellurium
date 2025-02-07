import dataclasses as _dc
import itertools as _it
import typing as _ty
from argparse import ArgumentParser
from pathlib import Path

import yaml as _yaml

from . import functional as _func

__all__ = [
    "isinstance_generic",
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


def isinstance_generic(obj, typ) -> bool:
    if typ is _ty.Any:
        return True

    if isinstance(typ, type):
        return isinstance(obj, typ)

    origin = _ty.get_origin(typ)
    args = _ty.get_args(typ)

    if origin is None:
        return False

    if origin is _ty.Union:
        return any(isinstance_generic(obj, arg) for arg in args)

    if not isinstance(obj, origin):
        return False

    if args:
        if origin is list:
            return all(isinstance_generic(x, args[0]) for x in obj)
        elif origin is dict:
            return all(
                isinstance_generic(k, args[0]) and isinstance_generic(v, args[1])
                for k, v in obj.items()
            )
        elif origin is tuple:
            if len(args) == 2 and args[1] is ...:
                return all(isinstance_generic(x, args[0]) for x in obj)
            elif len(args) == len(obj):
                return all(isinstance_generic(x, t) for x, t in zip(obj, args))


def _concat_keys(left: _ty.Optional[str], right: str) -> str:
    if left:
        return f"{left}.{right}"
    else:
        return right


def _product_mapping(mapping: dict[str, list]) -> list[dict]:
    keys = mapping.keys()
    values = mapping.values()
    product = list(_it.product(*values))
    return [dict(zip(keys, combination)) for combination in product]


@_dc.dataclass
class _ObjToDataclass:
    filepath: _ty.Optional[Path]

    def run_time_error(self, msg: str, data, key: _ty.Optional[str]) -> RuntimeError:
        filename = str(self.filepath.name) if self.filepath else "<unknown>"
        if key is not None:
            line = f"{filename}:{key}: {msg}"
        else:
            line = f"{filename}: {msg}"

        actual = repr(data)
        if len(actual) > 80:
            line2 = f"actual: {actual[:77]}..."
        else:
            line2 = f"actual: {actual}"

        return RuntimeError(f"{line}\n{line2}")

    def dict_get(self, data: dict, keyword: str, key: _ty.Optional[str]):
        if isinstance(data, dict) and keyword in data:
            return data[keyword]
        else:
            raise self.run_time_error(f"expected to contain {keyword!r}", data, key)

    def get_union(
        self, cls: type[_T], data, key: _ty.Optional[str], mapping: dict
    ) -> _T:
        for alternative in _ty.get_args(cls):
            if alternative.__name__ == data["ALT"]:
                new_key = _concat_keys(key, "ARGS")
                return self.run(
                    alternative, data.get("ARGS", {}), key=new_key, mapping=mapping
                )
        raise self.run_time_error(f"expected to be {cls}", data, key)

    def get_builtin_function(
        self, data, key: _ty.Optional[str], mapping: dict
    ) -> _func.BuiltinFunction:
        for alternative in _ty.get_args(_func.BuiltinFunction):
            if data["FUNC"] == alternative.__name__:
                new_key = _concat_keys(key, "ARGS")
                return self.run(
                    alternative, data.get("ARGS", {}), key=new_key, mapping=mapping
                )
        raise self.run_time_error("expected to be a built-in function", data, key)

    def run(
        self,
        cls: type[_T],
        data,
        key: _ty.Optional[str] = None,
        mapping: _ty.Optional[dict] = None,
    ) -> _T:
        if mapping is None:
            mapping = {}

        if isinstance(data, dict) and "FUNC" in data:
            if data["FUNC"] == "Matrix":
                if _ty.get_origin(cls) is not list:
                    raise self.run_time_error(f"expected to be {cls}", data, key)

                matrix_args = self.dict_get(data, "ARGS", key=key)
                args_key = _concat_keys(key, "ARGS")

                matrix_mapping = self.dict_get(matrix_args, "mapping", key=args_key)
                mapping_key = _concat_keys(args_key, "mapping")
                intermediate_mapping = self.run(
                    dict[str, list],
                    matrix_mapping,
                    key=mapping_key,
                    mapping=mapping,
                )
                mappings = _product_mapping(intermediate_mapping)

                matrix_template = self.dict_get(matrix_args, "template", key=args_key)
                template_key = _concat_keys(args_key, "template")
                return [
                    self.run(
                        _ty.get_args(cls)[0],
                        matrix_template,
                        key=template_key,
                        mapping=mapping | new_items,
                    )
                    for new_items in mappings
                ]

            func = self.get_builtin_function(data, key=key, mapping=mapping)

            match func:
                case _func.FilePath():
                    result = str(self.filepath) if self.filepath else "<unknown>"
                case _func.FileName():
                    result = self.filepath.name if self.filepath else "<unknown>"
                case _func.Placeholder():
                    if func.key not in mapping:
                        raise self.run_time_error(
                            f"Matrix.mapping should contain {func.key!r}", mapping, key
                        )
                    result = mapping[func.key]
                case _:
                    result = func.run()

            if not isinstance_generic(result, cls):
                raise self.run_time_error(f"expected to be {cls}", result, key)

            return result

        if _dc.is_dataclass(cls):
            if not isinstance(data, dict):
                raise self.run_time_error("expected to be dict", data, key)
            field_types = {f.name: f.type for f in _dc.fields(cls)}
            cls_args = {
                k: self.run(
                    field_types[k], v, key=_concat_keys(key, k), mapping=mapping
                )
                for k, v in data.items()
            }
            return cls(**cls_args)

        if _is_optional(cls):
            if data is not None:
                new_key = _concat_keys(key, "Optional")
                return self.run(
                    _ty.get_args(cls)[0], data, key=new_key, mapping=mapping
                )
            else:
                return None

        if _ty.get_origin(cls) is _ty.Union:
            if isinstance(data, dict) and "ALT" in data:
                return self.get_union(cls, data, key=key, mapping=mapping)
            elif any(isinstance_generic(data, ty) for ty in _ty.get_args(cls)):
                return data
            else:
                raise self.run_time_error(
                    f"expected to contain {"ALT"!r} or be {cls}", data, key
                )

        if _ty.get_origin(cls) is list:
            if not isinstance(data, list):
                raise self.run_time_error("expected to be list", data, key)
            new_key = _concat_keys(key, "list")
            return [
                self.run(_ty.get_args(cls)[0], item, key=new_key, mapping=mapping)
                for item in data
            ]

        if cls is _ty.Any:
            return data

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
