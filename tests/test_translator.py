"""Тесты синтаксиса, вычислений и интерфейса командной строки."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.errors import EvaluationError, ParseError
from src.evaluator import Evaluator
from src.parser import ConfigParser

ROOT = Path(__file__).resolve().parents[1]

EXIT_SUCCESS = 0

X_VALUE = 8
Y_VALUE = 16

A_OCTAL = 7
B_OCTAL = 8
C_OCTAL = 15

NESTED_ONE = 1
NESTED_TWO = 2
NESTED_THREE = 3
NESTED_FOUR = 4

BASE_TEN = 8
RESULT_TEN = 8

BASE_TWENTY = 16
SUM_VALUE = 19
DIFF_VALUE = 13

MINIMUM_VALUE = 3

A_FIVE = 5
VALUES_ONE = 1
VALUES_SUM = 7
VALUES_LAST = 7

ARRAY_ONE = 1
ARRAY_TWO = 2

CLI_A = 8
CLI_VALUES_ONE = 8
CLI_VALUES_TWO = 2


def _translate(source):
    """Разобрать исходный текст и вычислить его итоговое значение."""
    document = ConfigParser().parse(source)
    return Evaluator().evaluate(document)


@pytest.fixture
def translate_source():
    """Предоставить функцию трансляции тестам."""
    return _translate


def test_declarations_only_are_valid_and_exported_as_object():
    """Файл может состоять только из объявлений; JSON содержит все константы."""
    expected = {"X": X_VALUE, "Y": Y_VALUE}
    assert _translate("X is 0o10; Y is 0o20;") == expected


def test_octal_numbers(translate_source):
    """Восьмеричные литералы преобразуются в десятичные значения JSON."""
    expected = {"A": A_OCTAL, "B": B_OCTAL, "C": C_OCTAL}
    assert translate_source("A is 0o7; B is 0O10; C is 0o17;") == expected


def test_nested_arrays(translate_source):
    """Массивы могут содержать вложенные массивы."""
    source = "NESTED is (0o1, (0o2, (0o3, 0o4)));"
    expected = {
        "NESTED": [
            NESTED_ONE,
            [NESTED_TWO, [NESTED_THREE, NESTED_FOUR]],
        ]
    }
    assert _translate(source) == expected


def test_constant_declaration_and_reference(translate_source):
    """Константы доступны после объявления через выражение."""
    source = "BASE is 0o10; RESULT is @{BASE};"
    expected = {"BASE": BASE_TEN, "RESULT": RESULT_TEN}
    assert _translate(source) == expected


def test_postfix_addition_and_subtraction(translate_source):
    """Сложение и вычитание работают в постфиксной форме."""
    source = "BASE is 0o20; SUM is @{BASE 0o3 +}; DIFF is @{BASE 0o3 -};"
    expected = {
        "BASE": BASE_TWENTY,
        "SUM": SUM_VALUE,
        "DIFF": DIFF_VALUE,
    }
    assert _translate(source) == expected


def test_postfix_minimum(translate_source):
    """Функция min() извлекает два аргумента из стека."""
    expected = {"MINIMUM": MINIMUM_VALUE}
    assert translate_source("MINIMUM is @{0o7 0o3 min()};") == expected
    assert translate_source("MINIMUM is @{0o7 0o3 min ( )};") == expected


def test_expression_inside_nested_array(translate_source):
    """Выражения вычисляются на любом уровне вложенности массива."""
    source = "A is 0o5; VALUES is (0o1, (@{A 0o2 +}, 0o7));"
    expected = {
        "A": A_FIVE,
        "VALUES": [VALUES_ONE, [VALUES_SUM, VALUES_LAST]],
    }
    assert _translate(source) == expected


def test_array_constant(translate_source):
    """Константа может содержать массив."""
    source = "VALUES is (0o1, 0o2);"
    expected = {"VALUES": [ARRAY_ONE, ARRAY_TWO]}
    assert _translate(source) == expected


def test_invalid_octal_digit():
    """Цифра вне восьмеричной системы вызывает синтаксическую ошибку."""
    with pytest.raises(ParseError):
        ConfigParser().parse("BAD is 0o8;")


def test_missing_array_comma():
    """Элементы массива должны разделяться запятыми."""
    with pytest.raises(ParseError):
        ConfigParser().parse("BAD is (0o1 0o2);")


def test_missing_declaration_semicolon():
    """Объявление константы обязательно заканчивается точкой с запятой."""
    with pytest.raises(ParseError):
        ConfigParser().parse("A is 0o1")


def test_unknown_constant():
    """Использование необъявленной константы вызывает ошибку."""
    with pytest.raises(EvaluationError, match="Неизвестная"):
        _translate("BAD is @{UNKNOWN};")


def test_duplicate_constant():
    """Повторное объявление имени константы запрещено."""
    source = "A is 0o1; A is 0o2;"
    with pytest.raises(EvaluationError, match="повторно"):
        _translate(source)


def test_operator_stack_underflow():
    """Бинарная операция требует два операнда."""
    with pytest.raises(EvaluationError, match="недостаточно"):
        _translate("BAD is @{0o1 +};")


def test_expression_must_leave_one_value():
    """После вычисления выражения в стеке должно остаться одно значение."""
    with pytest.raises(EvaluationError, match="одно значение"):
        _translate("BAD is @{0o1 0o2};")


def test_arithmetic_rejects_arrays():
    """Арифметические операции не принимают массивы."""
    source = "VALUES is (0o1, 0o2); BAD is @{VALUES 0o1 +};"
    with pytest.raises(EvaluationError, match="только числа"):
        _translate(source)


def test_cli_reads_and_writes_files(tmp_path):
    """CLI читает исходный файл и записывает корректный JSON."""
    input_path = tmp_path / "input.conf"
    output_path = tmp_path / "output.json"
    input_path.write_text(
        "A is 0o10; VALUES is ( @{A}, 0o2 );", encoding="utf-8"
    )
    command = [
        sys.executable,
        "-m",
        "src.main",
        "--input",
        str(input_path),
        "--output",
        str(output_path),
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == EXIT_SUCCESS
    expected = {
        "A": CLI_A,
        "VALUES": [CLI_VALUES_ONE, CLI_VALUES_TWO],
    }
    assert json.loads(output_path.read_text(encoding="utf-8")) == expected
