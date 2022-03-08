import plox_scanner as scanner
import plox_syntax_trees as syntax_trees
import plox_utilities as utilties

class Environment:

    environment = None

    def __init__(self):
        if self.environment is None:
            self.environment = self._Environment()

    def add_variable(self, name, value):
        self.environment.add_variable(name, value)

    def assign_variable(self, name, value):
        return self.environment.assign_variable(name, value)

    def enter_block(self):
        self.environment.push_context()

    def exit_block(self):
        self.environment.pop_context()

    def get_value(self, name):
        return self.environment.get_variable_value(name)

    class _Environment:
        def __init__(self):
            self.contexts = []
            self.push_context()

        def push_context(self):
            self.contexts.append({})

        def pop_context(self):
            self.contexts.pop()

        def add_variable(self, name, value):
            self.contexts[-1][name] = value

        def find_variable(self, name):
            c = None
            self.contexts.reverse()
            for context in self.contexts:
                if name in context:
                   c = context
                   break
            self.contexts.reverse() # Put the list back to its original order
            return c

        def assign_variable(self, name, value):
            context = self.find_variable(name)
            if context is None:
                return False
            context[name] = value
            return True

        def get_variable_value(self, name):
            context = self.find_variable(name)
            if context is None:
                raise Exception("Implicit declaration of variable %s." % name)
            return context[name]

class PloxRuntimeError(utilties.PloxError):
    def __init__(self, message, line):
        super().__init__(line, message)

    def get_error_message(self):
        return " Runtime Error: " + self.message

class TreeEvaluator:

    evaluator = None
    def __init__(self):
        if self.evaluator is None:
            self.evaluator = self._TreeEvaluator()
            self.environment = self.evaluator.environment

    def evaluation(self, expr):
        return self.evaluator.evaluate(expr)

    def is_true(self, result):
        return self.evaluator.is_true(result)

    class _TreeEvaluator:

        def __init__(self):
            self.environment = Environment()

        def is_true(self, value):
            if value is None:
                return False
            if value == 0.0:
                return False
            if value is False:
                return False
            return True

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
            return literal.literal.get_value()

        def visit_Idnt(self, idnt):
            var_name = idnt.identifier.get_value()
            try:
                value = self.environment.get_value(var_name)
            except Exception as e:
                raise PloxRuntimeError("Implicit Declaration of Variable %s." % var_name, idnt.identifier.line)
            return value

        def visit_Unary(self, unary):
            result = unary.expr.accept(self)
            operator = unary.operator.type

            if operator == scanner.BANG:
                bool_result = self.is_true(result)
                return not bool_result

            elif operator == scanner.MINUS:
                if not isinstance(result, float):
                    raise PloxRuntimeError(" Negation expects NUMBER", unary.operator.line)
                return -result

        def visit_Assign(self, assign):
            var_name = self.evaluate(assign.left_side)
            assign_value = self.evaluate(assign.right_side)
            try:
                self.environment.assign_variable(var_name, assign_value)
            except Exception:
                raise RuntimeError("Implicit Declaration of Variable %s." % var_name, assign.left_side.line)
            return None


class Interpreter:

    interpreter = None
    def __init__(self, console_mode=False):
        if self.interpreter is None:
            self.interpreter = self._Interpreter(console_mode)

    def interpret(self, statements):
        for stmt in statements:
            try:
                self.execute(stmt)
            except PloxRuntimeError as e:
                utilties.report_error(e)

    def execute(self, stmt):
        self.interpreter.execute(stmt)

    class _Interpreter(TreeEvaluator):

        def __init__(self, console_mode=False):
            super().__init__()
            self._console_mode = console_mode

        def execute(self, stmt):
            stmt.accept(self)

        def console_print(self, result):
            print("    Result: ")
            print("            " + str(result))
            print("")

        def visit_Dclr(self, dclr):
            value = None
            var_name = dclr.identifier.identifier.get_value()
            if dclr.expr is not None:
                value = self.evaluation(dclr.expr)
            self.environment.add_variable(var_name, value)
            return None

        def visit_PrintStmt(self, printstmt):
            expr_result = self.evaluation(printstmt.expr)
            print(str(expr_result))
            return None

        def visit_ExprStmt(self, exprstmt):
            expr_result = self.evaluation(exprstmt.expr)
            if self._console_mode:
                self.console_print(expr_result)
            return None

        def visit_Block(self, block):
            self.environment.enter_block()
            for stmt in block.stmts:
                self.execute(stmt)
            self.environment.exit_block()
            return None

        def visit_IfStmt(self, ifstmt):
            if_expr_result = self.is_true(self.evaluation(ifstmt.expr))
            if if_expr_result is True:
                self.execute(ifstmt.if_block)
            elif ifstmt.else_block is not None:
                self.execute(ifstmt.else_block)
            return None


