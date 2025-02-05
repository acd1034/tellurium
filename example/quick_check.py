from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import matplotlib.pyplot as plt
import numpy as np

from tellurium.arguments import make_from_arguments
from tellurium.functional import FunStr


@dataclass
class Print:
    msg: FunStr

    def run(self):
        print(self.msg)


@dataclass
class Plot:
    input: Path
    output: Path
    print: Print
    print_or_int: Union[Print, int]
    opt_float: Optional[float]
    list_int: list[int]
    list_only: list
    opt_float_with_default: Optional[float] = None

    @staticmethod
    def load_dat(input_file: Path) -> np.ndarray:
        with open(input_file) as f:
            lines = f.readlines()

        non_comment_idx = None
        for i, line in enumerate(lines):
            if not line.strip().startswith("#") and line.strip():  # 空行も無視
                non_comment_idx = i
                break

        return np.genfromtxt(lines[non_comment_idx:])

    def run(self):
        data = Plot.load_dat(self.input)
        assert data.shape[1] > 0, f"{data.shape=}"

        # data の内容を描画
        plt.style.use("../.matplotlibrc")
        fig, ax = plt.subplots()
        for i in range(1, data.shape[1]):
            ax.scatter(data[:, 0], data[:, i], label=f"#{i}")

        # ラベルやタイトルを設定
        # ax.set_xlabel(r"")
        # ax.set_ylabel(r"")
        # ax.set_ylim(1, 2)
        # ax.set_xmargin(0.0)
        ax.set_title(self.input.name)
        ax.legend()

        # プロットを表示
        plt.tight_layout()
        fig.savefig(self.output, dpi=600)


if __name__ == "__main__":
    make_from_arguments(Plot).run()
