"""Исключения транслятора."""


class ConfigError(Exception):
    """Базовая ошибка конфигурационного языка."""


class ParseError(ConfigError):
    """Ошибка синтаксического разбора исходного текста."""


class EvaluationError(ConfigError):
    """Ошибка вычисления константы или выражения."""
