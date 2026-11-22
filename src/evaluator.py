"""Вычислитель значений и постфиксных выражений."""

from .ast_nodes import (
    Add,
    Array,
    Expression,
    Minimum,
    Number,
    PushNumber,
    Reference,
    Subtract,
)
from .errors import EvaluationError

BINARY_OPERAND_COUNT = 2
STACK_RESULT_COUNT = 1


class Evaluator:
    """Вычисляет документ с учетом области констант времени трансляции."""

    def evaluate(self, document):
        """Вернуть итоговое значение документа."""
        constants = {}
        for declaration in document.declarations:
            self._add_constant(declaration, constants)
        return constants

    def _add_constant(self, declaration, constants):
        """Проверить и сохранить очередную константу."""
        if declaration.name in constants:
            raise EvaluationError(
                f"Константа '{declaration.name}' объявлена повторно."
            )
        value = self._evaluate_value(declaration.value, constants)
        constants[declaration.name] = value

    def _evaluate_value(self, node, constants):
        """Рекурсивно вычислить узел значения."""
        if isinstance(node, Number):
            return node.value
        if isinstance(node, Array):
            return self._evaluate_array(node, constants)
        if isinstance(node, Expression):
            return self._evaluate_expression(node, constants)
        raise EvaluationError("Неизвестный тип значения.")

    def _evaluate_array(self, node, constants):
        """Вычислить каждый элемент массива."""
        return [self._evaluate_value(value, constants) for value in node.values]

    def _evaluate_expression(self, expression, constants):
        """Вычислить постфиксное выражение стековым алгоритмом."""
        stack = []
        for item in expression.items:
            self._process_item(item, stack, constants)
        if len(stack) != STACK_RESULT_COUNT:
            raise EvaluationError(
                "Постфиксное выражение должно оставлять в стеке одно значение."
            )
        return stack[0]

    def _process_item(self, item, stack, constants):
        """Обработать один операнд или оператор выражения."""
        if isinstance(item, PushNumber):
            stack.append(item.value)
            return
        if isinstance(item, Reference):
            self._push_reference(item, stack, constants)
            return
        self._apply_operator(item, stack)

    @staticmethod
    def _push_reference(item, stack, constants):
        """Поместить значение константы в стек."""
        if item.name not in constants:
            raise EvaluationError(
                f"Неизвестная или еще не объявленная константа '{item.name}'."
            )
        stack.append(constants[item.name])

    def _apply_operator(self, operator, stack):
        """Выполнить бинарный оператор над двумя верхними элементами стека."""
        if len(stack) < BINARY_OPERAND_COUNT:
            raise EvaluationError(
                "Для бинарной операции недостаточно операндов."
            )
        right = stack.pop()
        left = stack.pop()
        self._check_numeric_operands(left, right)
        result = self._calculate(operator, left, right)
        stack.append(result)

    @staticmethod
    def _check_numeric_operands(left, right):
        """Запретить арифметические операции над массивами."""
        if type(left) is not int or type(right) is not int:
            raise EvaluationError(
                "Арифметические операции и min() принимают только числа."
            )

    @staticmethod
    def _calculate(operator, left, right):
        """Вычислить сложение, вычитание или минимум."""
        if isinstance(operator, Add):
            return left + right
        if isinstance(operator, Subtract):
            return left - right
        if isinstance(operator, Minimum):
            return min(left, right)
        raise EvaluationError("Неизвестная операция в постфиксном выражении.")
