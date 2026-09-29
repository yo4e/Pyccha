from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias


@dataclass(frozen=True, slots=True)
class SourceSpan:
    line: int
    column: int
    end_line: int
    end_column: int


@dataclass(frozen=True, slots=True)
class Node:
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class StringLiteral(Node):
    value: str


@dataclass(frozen=True, slots=True)
class NumberLiteral(Node):
    value: int | float


@dataclass(frozen=True, slots=True)
class Name(Node):
    identifier: str


Expr: TypeAlias = StringLiteral | NumberLiteral | Name


@dataclass(frozen=True, slots=True)
class Equal(Node):
    left: Expr
    right: Expr


@dataclass(frozen=True, slots=True)
class NotEqual(Node):
    left: Expr
    right: Expr


@dataclass(frozen=True, slots=True)
class GreaterThan(Node):
    left: Expr
    right: Expr


@dataclass(frozen=True, slots=True)
class LessThan(Node):
    left: Expr
    right: Expr


@dataclass(frozen=True, slots=True)
class Negation(Node):
    target: Expr


@dataclass(frozen=True, slots=True)
class And(Node):
    items: tuple[Condition, ...]


@dataclass(frozen=True, slots=True)
class Or(Node):
    items: tuple[Condition, ...]


Condition: TypeAlias = Equal | NotEqual | GreaterThan | LessThan | Negation | And | Or


@dataclass(frozen=True, slots=True)
class Assignment(Node):
    name: str
    value: Expr


@dataclass(frozen=True, slots=True)
class Output(Node):
    value: Expr


@dataclass(frozen=True, slots=True)
class If(Node):
    condition: Condition
    then_body: tuple[Statement, ...]
    else_body: tuple[Statement, ...]


@dataclass(frozen=True, slots=True)
class Repeat(Node):
    count: int
    body: tuple[Statement, ...]


Statement: TypeAlias = Assignment | Output | If | Repeat


@dataclass(frozen=True, slots=True)
class Program(Node):
    statements: tuple[Statement, ...]
