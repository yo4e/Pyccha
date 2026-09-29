from __future__ import annotations

import ast as py_ast
import keyword
from importlib import resources
from typing import Any

from lark import Lark, Token, Transformer, UnexpectedInput, v_args
from lark.exceptions import VisitError

from .ast import (
    And,
    Assignment,
    Equal,
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
    SourceSpan,
    StringLiteral,
)


class PycchaSyntaxError(Exception):
    def __init__(self, message: str, *, line: int, column: int, context: str = "") -> None:
        super().__init__(message)
        self.line = line
        self.column = column
        self.context = context

    def __str__(self) -> str:
        where = f"{self.line}:{self.column}"
        return f"{super().__str__()} ({where})" + (f"\n{self.context}" if self.context else "")


def _span_from_meta(meta: Any) -> SourceSpan:
    return SourceSpan(meta.line, meta.column, meta.end_line, meta.end_column)


def _span_from_token(token: Token) -> SourceSpan:
    return SourceSpan(token.line, token.column, token.end_line, token.end_column)


def _validate_identifier(identifier: str, span: SourceSpan) -> str:
    if not identifier.isidentifier() or keyword.iskeyword(identifier):
        raise PycchaSyntaxError(
            f"変数名に使えん名前: {identifier}",
            line=span.line,
            column=span.column,
        )
    return identifier


@v_args(meta=True)
class _AstBuilder(Transformer):
    def start(self, meta: Any, children: list[Any]) -> Program:
        return Program(_span_from_meta(meta), tuple(children))

    def string(self, meta: Any, children: list[Any]) -> StringLiteral:
        token = children[0]
        return StringLiteral(_span_from_token(token), py_ast.literal_eval(str(token)))

    def number(self, meta: Any, children: list[Any]) -> NumberLiteral:
        token = children[0]
        text = str(token)
        value: int | float = float(text) if "." in text else int(text)
        return NumberLiteral(_span_from_token(token), value)

    def name(self, meta: Any, children: list[Any]) -> Name:
        token = children[0]
        span = _span_from_token(token)
        identifier = _validate_identifier(str(token), span)
        return Name(span, identifier)

    def assignment(self, meta: Any, children: list[Any]) -> Assignment:
        name_token, value = children
        name = _validate_identifier(str(name_token), _span_from_token(name_token))
        return Assignment(_span_from_meta(meta), name, value)

    def output(self, meta: Any, children: list[Any]) -> Output:
        return Output(_span_from_meta(meta), children[0])

    def equal(self, meta: Any, children: list[Any]) -> Equal:
        return Equal(_span_from_meta(meta), children[0], children[1])

    def not_equal(self, meta: Any, children: list[Any]) -> NotEqual:
        return NotEqual(_span_from_meta(meta), children[0], children[1])

    def greater_than(self, meta: Any, children: list[Any]) -> GreaterThan:
        return GreaterThan(_span_from_meta(meta), children[0], children[1])

    def less_than(self, meta: Any, children: list[Any]) -> LessThan:
        return LessThan(_span_from_meta(meta), children[0], children[1])

    def negation(self, meta: Any, children: list[Any]) -> Negation:
        return Negation(_span_from_meta(meta), children[0])

    def conjunction(self, meta: Any, children: list[Any]):
        if len(children) == 1:
            return children[0]
        return And(_span_from_meta(meta), tuple(children))

    def disjunction(self, meta: Any, children: list[Any]):
        if len(children) == 1:
            return children[0]
        return Or(_span_from_meta(meta), tuple(children))

    def else_clause(self, meta: Any, children: list[Any]) -> tuple[Any, ...]:
        return tuple(children)

    def if_stmt(self, meta: Any, children: list[Any]) -> If:
        condition = children[0]
        tail = children[1:]
        else_body: tuple[Any, ...] = ()
        if tail and isinstance(tail[-1], tuple):
            else_body = tail.pop()
        return If(_span_from_meta(meta), condition, tuple(tail), else_body)

    def repeat_stmt(self, meta: Any, children: list[Any]) -> Repeat:
        count_token, *body = children
        return Repeat(_span_from_meta(meta), int(str(count_token)), tuple(body))


def _load_parser() -> Lark:
    grammar = resources.files("pyccha").joinpath("grammar.lark").read_text(encoding="utf-8")
    return Lark(grammar, parser="lalr", lexer="contextual", propagate_positions=True)


_PARSER = _load_parser()
_BUILDER = _AstBuilder()


def parse_source(source: str) -> Program:
    try:
        tree = _PARSER.parse(source)
    except UnexpectedInput as exc:
        context = exc.get_context(source, span=40).rstrip()
        raise PycchaSyntaxError(
            "Pycchaの構文を読めんかった",
            line=exc.line,
            column=exc.column,
            context=context,
        ) from exc
    try:
        return _BUILDER.transform(tree)
    except VisitError as exc:
        if isinstance(exc.orig_exc, PycchaSyntaxError):
            raise exc.orig_exc from exc
        raise
