import plox_scanner as scanner
import plox_syntax_trees as syntax_trees
import plox_utilities as utilties


class PloxCallable:

    def __init__(self, name, block_stmt, parameter_names=[]):
        self.function_body = block_stmt
        self.parameter_names = parameter_names
        self.callable_name = name

    def __call__(self, interpreter, args=[]):
        if len(args) != len(self.parameter_names):
            raise PloxRuntimeError("Function %s expects %d arguments but %d given." % (self.callable_name,
                                                                                       len(self.parameter_names),
                                                                                       len(args)))
        interpreter.save_environment()
        interpreter.execute_function_body(self.function_body, zip(self.parameter_names, args))
        interpreter.restore_environment()

    def to_string(self):
        return "<fn " + self.name + ": " + len(self.parameter_names) + ">"


class Environment:

    environment = None

    def __init__(self):
        if self.environment is None:
            self.environment = self._Environment()

    def add(self, name, value):
        self.environment.add(name, value)

    def assign_variable(self, name, value):
        return self.environment.assign_variable(name, value)

    def enter_block(self, zipped_params_args=[]):
        self.environment.enter_block(zipped_params_args)

    def exit_block(self):
        self.environment.pop_context()

    def get_value(self, name):
        return self.environment.get_variable_value(name)

    def get_global_variables(self):
        return self.environment.get_global_variables()

    def save_environment(self):
        self.environment.push_non_globals_to_stack()

    def restore_environment(self):
        self.environment.restore_stack()

    class _Environment:
        def __init__(self):
            self.contexts = []
            self.stack = []
            self.push_context()

        def push_context(self):
            self.contexts.append({})

        def pop_context(self):
            self.contexts.pop()

        def enter_block(self, zipped_params_args):
            self.push_context()
            if len(zipped_params_args) > 0:
                # This is a function call and we need
                # To add the function arguments to the local environment
                for param_name, arg in zipped_params_args:
                    self.add(param_name, arg)

        def add(self, name, value):
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

        def get_global_variables(self):
            return self.contexts[0]  # The first context in the stack is the global context

        def push_non_globals_to_stack(self):
            while len(self.contexts) > 1:
                self.stack.append(self.contexts.pop())

        def restore_stack(self):
            while len(self.stack) > 0:
                self.contexts.append(self.stack.pop())

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
            var_name = assign.left_side.identifier.get_value() # Get the identifier name
            assign_value = self.evaluate(assign.right_side)
            try:
                self.environment.assign_variable(var_name, assign_value)
            except Exception:
                raise RuntimeError("Implicit declaration of variable %s." % var_name, assign.left_side.line)
            return assign_value

        def visit_Call(self, call):
            callee = self.evaluate(call.callee).identifier.get_value()
            callee_name = callee.identifier.get_value()
            try:
                function = self.environment.get_value(callee_name)
            except Exception:
                raise RuntimeError("Implicit declaration of function %s." % callee_name, call.callee.identifier.line)
            if not callable(function):
                raise RuntimeError("Attempting to call a non-callable object %s." % callee_name,
                                   call.callee.identifier.line)

            return function(self, [self.evaluate(x) for x in call.arguments])


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

    def execute_function_body(self, func_body_block, call_args):
        self.interpreter.visit_Block(func_body_block, call_args)

    def save_environment(self):
        return self.interpreter.environment.save_environment()

    def restore_environment(self):
        return self.interpreter.environment.restore_environment()

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
            self.environment.add(var_name, value)
            return None

        def visit_FuncDclr(self, f_dclr):
            func_name = f_dclr.handle.identifier.get_value()
            parameter_names = [x.identifier.get_value() for x in f_dclr.parameters]
            function = PloxCallable(func_name, f_dclr.body, parameter_names)
            self.environment.add(func_name, function)


        def visit_PrintStmt(self, printstmt):
            expr_result = self.evaluation(printstmt.expr)
            print(str(expr_result))
            return None

        def visit_ExprStmt(self, exprstmt):
            expr_result = self.evaluation(exprstmt.expr)
            if self._console_mode:
                self.console_print(expr_result)
            return None

        def visit_Block(self, block, func_call_args=[]):
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

        def visit_WhileStmt(self, whilestmt):
            while_expr = self.is_true(self.evaluation(whilestmt.expr))
            while while_expr:
                self.execute(whilestmt.while_block)
                while_expr = self.is_true(self.evaluation(whilestmt.expr))




