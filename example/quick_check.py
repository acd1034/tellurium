from dataclasses import dataclass
from typing import Optional, Union

from tellurium.arguments import make_from_arguments
from tellurium.functional import FunListStr, FunStr


@dataclass
class Print:
    msg: FunStr

    def run(self):
        print(self.msg)


@dataclass
class Main:
    print: Print
    print_or_int: Union[Print, int]
    opt_float: Optional[float]
    list_int: list[int]
    fun_list_str: FunListStr
    opt_float_with_default: Optional[float] = None

    def run(self):
        self.print.run()
        print(f"{self.fun_list_str=}")


if __name__ == "__main__":
    make_from_arguments(Main).run()
