"""Синтаксический анализатор на базе специализированного парсера Lark."""

from pathlib import Path

from lark import Lark, Transformer, UnexpectedInput, v_args

from .ast_nodes import (
    Add,
    Array,
    Declaration,
    Document,
    Expression,
    Minimum,
    Number,
    PushNumber,
    Reference,
    Subtract,
)
from .errors import ParseError

OCTAL_BASE = 8
GRAMMAR_PATH = Path(__file__).with_name("grammar.lark")


@v_args(inline=True)
class AstBuilder(Transformer):
    """Преобразует дерево Lark в узлы абстрактного синтаксического дерева."""

    def start(self, *declarations):
        """Создать документ из набора объявлений констант."""
        return Document(tuple(declarations))

    def declaration(self, name, value):
        """Создать объявление константы."""
        return Declaration(str(name), value)

    def number(self, token):
        """Преобразовать восьмеричный литерал в целое число."""
        return Number(int(str(token), OCTAL_BASE))

    def array(self, *values):
        """Создать узел массива."""
        return Array(tuple(values))

    def expression(self, *items):
        """Создать узел постфиксного выражения."""
        return Expression(tuple(items))

    def reference(self, token):
        """Создать ссылку на константу."""
        return Reference(str(token))

    def push_number(self, token):
        """Создать элемент выражения с числовым операндом."""
        value = int(str(token), OCTAL_BASE)
        return PushNumber(value)

    def add(self):
        """Создать операцию сложения."""
        return Add()

    def subtract(self):
        """Создать операцию вычитания."""
        return Subtract()

    def minimum(self):
        """Создать операцию минимума."""
        return Minimum()


class ConfigParser:
    """Разбирает исходный текст учебного конфигурационного языка."""

    def __init__(self):
        """Загрузить грамматику Lark и подготовить построитель AST."""
        grammar = GRAMMAR_PATH.read_text(encoding="utf-8")
        self._parser = Lark(grammar, parser="lalr", lexer="contextual")
        self._builder = AstBuilder()

    def parse(self, source):
        """Разобрать документ.

        Возвращает его абстрактное синтаксическое дерево (AST).
        """
        try:
            tree = self._parser.parse(source)
        except UnexpectedInput as error:
            self._raise_parse_error(source, error)
        return self._builder.transform(tree)

    @staticmethod
    def _raise_parse_error(source, error):
        """Создать диагностическое сообщение с позицией ошибки."""
        context = error.get_context(source, span=30).strip()
        line = getattr(error, "line", None) or 1
        column = getattr(error, "column", None) or 1
        expected = getattr(error, "expected", None)
        expected_message = (
            f" Ожидалось: {', '.join(sorted(expected))}." if expected else ""
        )
        message = (
            f"Синтаксическая ошибка: строка {line}, "
            f"столбец {column}.{expected_message}\n{context}"
        )
        raise ParseError(message) from error
