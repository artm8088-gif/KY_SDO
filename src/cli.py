"""Командный интерфейс транслятора."""

import argparse
import json
import sys
from pathlib import Path

from .errors import ConfigError
from .evaluator import Evaluator
from .parser import ConfigParser

JSON_INDENT = 2


def build_argument_parser():
    """Создать разборщик аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Транслятор учебного конфигурационного языка в JSON."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="путь к входному файлу"
    )
    parser.add_argument(
        "-o", "--output", required=True, help="путь к выходному JSON-файлу"
    )
    return parser


def translate(input_path, output_path):
    """Прочитать исходный файл, вычислить конфигурацию и записать JSON."""
    source = Path(input_path).read_text(encoding="utf-8")
    document = ConfigParser().parse(source)
    result = Evaluator().evaluate(document)
    output = json.dumps(result, ensure_ascii=False, indent=JSON_INDENT)
    Path(output_path).write_text(output + "\n", encoding="utf-8")


def main(argv=None):
    """Запустить транслятор и вернуть код завершения процесса."""
    parser = build_argument_parser()
    arguments = parser.parse_args(argv)
    try:
        translate(arguments.input, arguments.output)
    except (OSError, ConfigError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"Внутренняя ошибка транслятора: {error}", file=sys.stderr)
        return 2
    return 0
