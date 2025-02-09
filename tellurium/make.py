import dataclasses as _dc
import subprocess as _sp
from pathlib import Path


# dataclass を使用してルールを定義
@_dc.dataclass
class BuildRule:
    target: Path
    dependencies: list[Path]
    command: list[str]


def needs_update(target: Path, dependencies: list[Path]) -> bool:
    if not target.exists():
        return True
    target_time = target.stat().st_mtime  # 最終更新時間
    return any(dep.stat().st_mtime > target_time for dep in dependencies)


@_dc.dataclass
class Make:
    rules: dict[str, BuildRule]
    dry_run: bool = False
    done: set[str] = _dc.field(default_factory=set)

    # タスクを実行
    def _run(self, name: str) -> None:
        if name not in self.rules:
            if Path(name).exists():
                return
            else:
                raise RuntimeError(f"No rule to make target `{name}`")
        if name in self.done:
            return

        rule = self.rules[name]
        # 依存関係を先に実行
        for dep in rule.dependencies:
            self._run(str(dep))

        if self.dry_run:
            command = " ".join(rule.command)
            print(command)
        else:
            # ソースファイルがターゲットより新しければコマンドを実行
            if needs_update(rule.target, rule.dependencies):
                print(f"Running rule: {name}")
                _sp.run(rule.command)
            else:
                print(f"Task {name} is up to date.")

        self.done.add(name)

    def run(self) -> None:
        for name in self.rules.keys():
            self._run(name)


def run_rules(rules: list[BuildRule], dry_run: bool = False) -> None:
    rules_dict = {str(rule.target): rule for rule in rules}
    Make(rules_dict, dry_run).run()


if __name__ == "__main__":
    from .arguments import make_from_arguments

    run_rules(make_from_arguments(list[BuildRule]))
