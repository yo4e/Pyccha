from __future__ import annotations

from .ast import (
    And,
    Assignment,
    Equal,
    Expr,
    GreaterThan,
    If,
    LessThan,
    Name,
    Negation,
    NotEqual,
    NumberLiteral,
    Or,
    Output,
    Program,
    Repeat,
    Statement,
    StringLiteral,
)
from .parser import parse_source


class PythonTranspiler:
    def __init__(self) -> None:
        self._repeat_index = 0

    def transpile(self, program: Program) -> str:
        lines: list[str] = []
        for statement in program.statements:
            lines.extend(self._statement(statement, 0))
        return "\n".join(lines) + ("\n" if lines else "")

    def _statement(self, statement: Statement, indent: int) -> list[str]:
        prefix = "    " * indent
        if isinstance(statement, Assignment):
            return [f"{prefix}{statement.name} = {self._expr(statement.value)}"]
        if isinstance(statement, Output):
            return [f"{prefix}print({self._expr(statement.value)})"]
        if isinstance(statement, If):
            lines = [f"{prefix}if {self._condition(statement.condition)}:"]
            lines.extend(self._body(statement.then_body, indent + 1))
            if statement.else_body:
                lines.append(f"{prefix}else:")
                lines.extend(self._body(statement.else_body, indent + 1))
            return lines
        if isinstance(statement, Repeat):
            loop_name = f"_pyccha_repeat_{self._repeat_index}"
            self._repeat_index += 1
            lines = [f"{prefix}for {loop_name} in range({statement.count}):"]
            lines.extend(self._body(statement.body, indent + 1))
            return lines
        raise TypeError(f"unsupported statement: {type(statement).__name__}")

    def _body(self, statements: tuple[Statement, ...], indent: int) -> list[str]:
        if not statements:
            return ["    " * indent + "pass"]
        lines: list[str] = []
        for statement in statements:
            lines.extend(self._statement(statement, indent))
        return lines

    def _expr(self, expr: Expr) -> str:
        if isinstance(expr, StringLiteral):
            return repr(expr.value)
        if isinstance(expr, NumberLiteral):
            return repr(expr.value)
        if isinstance(expr, Name):
            return expr.identifier
        raise TypeError(f"unsupported expression: {type(expr).__name__}")

    def _condition(self, condition) -> str:
        if isinstance(condition, Equal):
            return f"{self._expr(condition.left)} == {self._expr(condition.right)}"
        if isinstance(condition, NotEqual):
            return f"{self._expr(condition.left)} != {self._expr(condition.right)}"
        if isinstance(condition, GreaterThan):
            return f"{self._expr(condition.left)} > {self._expr(condition.right)}"
        if isinstance(condition, LessThan):
            return f"{self._expr(condition.left)} < {self._expr(condition.right)}"
        if isinstance(condition, Negation):
            return f"not {self._expr(condition.target)}"
        if isinstance(condition, And):
            return " and ".join(f"({self._condition(item)})" for item in condition.items)
        if isinstance(condition, Or):
            return " or ".join(f"({self._condition(item)})" for item in condition.items)
        raise TypeError(f"unsupported condition: {type(condition).__name__}")


def transpile_source(source: str) -> str:
    return PythonTranspiler().transpile(parse_source(source))


def run_source(source: str, *, filename: str = "<pyccha>") -> None:
    python_source = transpile_source(source)
    code = compile(python_source, filename, "exec")
    namespace = {"__name__": "__main__"}
    exec(code, namespace, namespace)
