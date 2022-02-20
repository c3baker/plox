import plox_scanner as scanner

class PloxRuntimeError(Exception):
    def __init__(self, message, line):
        self.message = message
        self.line = line
        super().__init__(self.message)

    def get_error_message(self):
        return " Runtime Error: " + self.message

class TreeEvaluator:

    evaluator = None
    def __init__(self):
        if self.evaluator is None:
            self.evaluator = self._TreeEvaluator()

    class _TreeEvaluator:

        def evaluate(self, expr):
            return expr.accept(self)

        def visit_Binary(self, binary):
            left_result = binary.left_expr.accept(self)
            right_result = binary.right_expr.accept(self)

            operator = binary.operator.type

            if operator == scanner.ADD:
                if isinstance(left_result, float) and isinstance(right_result, float):
                    return left_result + right_result
                elif isinstance(left_result, str) and isinstance(right_result, str):
                    return left_result + right_result
                else:
                    raise PloxRuntimeError(" + Operator: Expected NUMBER or STRING", binary.operator.line)
            elif operator == scanner.MINUS:
                if isinstance(left_result, float) and isinstance(right_result, float):
                    return left_result - right_result
                else:
                    raise PloxRuntimeError(" - Operator: Expected NUMBER", binary.operator.line)
            elif operator == scanner.STAR:
                if isinstance(left_result, float) and isinstance(right_result, float):
                    return left_result * right_result
                else:
                    raise PloxRuntimeError(" * Operator: Expected NUMBER", binary.operator.line)
            elif operator == scanner.DIV:
                if isinstance(left_result, float) and isinstance(right_result, float):
                    return left_result / right_result
                else:
                    raise PloxRuntimeError(" / Operator: Expected NUMBER", binary.operator.line)
            else:
                raise PloxRuntimeError(" " + binary.operator.literal + " unsuppoerted operator", binary.operator.line)

        def visit_Grouping(self, grouping):
            return grouping.expr.accept(self)

        def visit_Literal(self, literal):
            return literal.value

        def visit_Unary(self, unary):
            result = unary.expr.accept(self)
            operator = unary.operator.type

            if operator == scanner.BANG:
                if result is False or isinstance(result, float):
                    return not result
                return False

            elif operator == scanner.MINUS:
                if not isinstance(result, float):
                    raise PloxRuntimeError(" Negation Expected NUMBER", unary.operator.line)
                return -result
