from __future__ import annotations

import argparse
from pathlib import Path

from .parser import PycchaSyntaxError
from .transpiler import run_source, transpile_source


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pyccha", description="Pyccha (.cha) を実行する")
    parser.add_argument("source", type=Path, help="実行する .cha ファイル")
    parser.add_argument("--emit-python", action="store_true", help="実行せず、変換後の Python を表示する")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source = args.source.read_text(encoding="utf-8")
    try:
        if args.emit_python:
            print(transpile_source(source), end="")
        else:
            run_source(source, filename=str(args.source))
    except PycchaSyntaxError as exc:
        print(f"構文エラー: {exc}")
        return 2
    return 0
