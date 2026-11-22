"""Узлы абстрактного синтаксического дерева языка варианта №2."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Number:
    """Целочисленный числовой литерал."""

    value: int


@dataclass(frozen=True)
class Array:
    """Массив значений."""

    values: tuple[object, ...]


@dataclass(frozen=True)
class Reference:
    """Ссылка на ранее объявленную константу."""

    name: str


@dataclass(frozen=True)
class PushNumber:
    """Число, помещаемое в стек постфиксного выражения."""

    value: int


@dataclass(frozen=True)
class Add:
    """Операция сложения в постфиксном выражении."""


@dataclass(frozen=True)
class Subtract:
    """Операция вычитания в постфиксном выражении."""


@dataclass(frozen=True)
class Minimum:
    """Функция минимума двух аргументов."""


@dataclass(frozen=True)
class Expression:
    """Постфиксное выражение, представленное последовательностью токенов."""

    items: tuple[object, ...]


@dataclass(frozen=True)
class Declaration:
    """Объявление константы времени трансляции."""

    name: str
    value: object


@dataclass(frozen=True)
class Document:
    """Документ, состоящий из набора объявлений констант."""

    declarations: tuple[Declaration, ...]
