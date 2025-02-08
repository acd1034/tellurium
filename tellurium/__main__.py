import dataclasses as _dc
import typing as _ty

import yaml as _yaml

from .arguments import make_from_arguments


@_dc.dataclass
class Print:
    msg: str


@_dc.dataclass
class Main:
    output: str
    print: Print
    print_or_int: _ty.Union[Print, int]
    opt_float: _ty.Optional[float]
    list_int: list[int]
    fun_list_str: list[str]
    opt_float_with_default: _ty.Optional[float] = None

    def run(self):
        with open(self.output, "w") as f:
            _yaml.safe_dump(
                _dc.asdict(self), f, default_flow_style=False, sort_keys=False
            )


if __name__ == "__main__":
    make_from_arguments(Main).run()
