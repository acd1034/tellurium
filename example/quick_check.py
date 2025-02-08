import dataclasses as _dc
import typing as _ty
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from tellurium.arguments import make_from_arguments


@_dc.dataclass
class Main:
    input: _ty.Union[str, list[str]]
    output: Path
    xlabel: _ty.Optional[str] = None
    ylabel: _ty.Optional[str] = None
    xlim: list[float] = _dc.field(default_factory=lambda: [None, None])
    ylim: list[float] = _dc.field(default_factory=lambda: [None, None])

    def __post_init__(self):
        if not isinstance(self.input, list):
            self.input = [self.input]

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
        for file in ["../.matplotlibrc", "../../.matplotlibrc"]:
            if Path(file).exists():
                plt.style.use(file)
                break

        fig, ax = plt.subplots()
        nplots = 0

        for input in self.input:
            input_file = Path(input)
            data = Main.load_dat(input_file)
            assert data.shape[1] > 0, f"{data.shape=}"

            # data の内容を描画
            for i in range(1, data.shape[1]):
                ax.plot(data[:, 0], data[:, i], label=f"{input_file.name}#{i}")
                nplots += 1

        # ラベルやタイトルを設定
        if self.xlabel:
            ax.set_xlabel(self.xlabel)
        if self.ylabel:
            ax.set_ylabel(self.ylabel)
        ax.set_xlim(*self.xlim)
        ax.set_ylim(*self.ylim)
        # ax.set_xmargin(0.0)
        if nplots < 9:
            ax.legend()
        elif nplots < 18:
            ax.legend(fontsize="xx-small")

        # プロットを表示
        plt.tight_layout()
        fig.savefig(self.output, dpi=600)


if __name__ == "__main__":
    make_from_arguments(Main).run()
