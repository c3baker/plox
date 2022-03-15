import plox_scanner as scanner
import plox_syntax_trees as syntax_trees
import plox_utilities as utilties


class PloxCallable:

    def __init__(self, name, block_stmt, parameter_names=[]):
        self.function_body = block_stmt
        self.parameter_names = parameter_names
        self.callable_name = name

    def __call__(self, interpreter, args=[]):
        ret_val = None
        if len(args) != len(self.parameter_names):
            raise PloxRuntimeError("Function %s expects %d arguments but %d given." % (self.callable_name,
                                                                                       len(self.parameter_names),
                                                                                       len(args)))
        interpreter.enter_function_call()
        try:
            interpreter.execute_function_body(self.function_body, zip(self.parameter_names, args))
        except Return as ret:
            ret_val = ret.value
        interpreter.exit_function_call()
        return ret_val

    def to_string(self):
        return "<fn " + self.name + ": " + len(self.parameter_names) + ">"


class Environment:

    environment = None

    def __init__(self, init_contexts=[]):
        if self.environment is None:
            self.environment = self._Environment(init_contexts)

    def add(self, name, value):
        return self.environment.add(name, value)

    def assign(self, name, value):
        return self.environment.assign(name, value)

    def enter_block(self, zipped_params_args=[]):
        self.environment.enter_block(zipped_params_args)

    def exit_block(self):
        self.environment.pop_context()

    def get_value(self, name):
        return self.environment.get_value(name)

    def get_global_variables(self):
        return self.environment.get_global_context()

    def enter_function_call(self):
        self.environment.push_non_globals_to_stack()

    def exit_function_call(self):
        self.environment.restore_last_context()

    class _Environment:
        def __init__(self, init_contexts):
            if not isinstance(init_contexts, list):
                raise RuntimeError("Contexts must be stored in a list! Something is being passed wrong here!")
            self.contexts = init_contexts
            self.reserve_stack = []
            self.push_context()

        def push_context(self):
            self.contexts.append({})

        def pop_context(self):
            self.contexts.pop()

        def enter_block(self, zipped_params_args):
            self.push_context()
            for param in zipped_params_args:
                # If This is a function call we need
                # To add the function arguments to the local environment
                if len(param) > 0:
                    param_name, arg = param
                    self.add(param_name, arg)

        def add(self, name, value):
            if name in self.contexts[-1]:
                return False
            self.contexts[-1][name] = value
            return True

        def find(self, name):
            c = None
            self.contexts.reverse()
            for context in self.contexts:
                if name in context:
                    c = context
                    break
            self.contexts.reverse() # Put the list back to its original order
            return c

        def assign(self, name, value):
            context = self.find(name)
            if context is None:
                return False
            context[name] = value
            return True

        def get_value(self, name):
            context = self.find(name)
            if context is None:
                raise Exception("Implicit declaration of variable %s." % name)
            return context[name]

        def get_non_global_contexts(self):
            if len(self.contexts) < 2:
                return []
            return self.contexts[1:]

        def get_global_context(self):
            return self.contexts[0]  # The first context in the stack is the global context

        def push_non_globals_to_stack(self):
            non_globals = self.get_non_global_contexts()
            self.reserve_stack.append(non_globals)
            # Remove the non-globals from the active environment
            global_context = self.get_global_context()
            self.contexts = []
            self.contexts.append(global_context)


        def restore_last_context(self):
            if len(self.reserve_stack) > 0:
                last_contexts = self.reserve_stack.pop()
            self.contexts.extend(last_contexts)


class PloxRuntimeError(utilties.PloxError):
    def __init__(self, message, line):
        super().__init__(line, message)

    def get_error_message(self):
        return " Runtime Error: " + self.message


class Return(Exception):
    def __init__(self, ret_value):
        self.value = ret_value


class Break(Exception):
    pass


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
            except Break:
                raise PloxRuntimeError("Break must be called within a loop context.")

    def execute(self, stmt):
        self.interpreter.execute(stmt)

    def enter_function_call(self):
        return self.interpreter.environment.enter_function_call()

    def exit_function_call(self):
        return self.interpreter.environment.exit_function_call()

    def evaluation(self, expr):
        return self.interpreter.evaluate(expr)

    def is_true(self, result):
        return self.interpreter.is_true(result)

    class _Interpreter:

        def __init__(self, console_mode=False):
            super().__init__()
            self._console_mode = console_mode
            self.environment = Environment()

        def enter_function_call(self):
            return self.environment.enter_function_call()

        def exit_function_call(self):
            return self.environment.exit_function_call()

        def execute_function_body(self, func_body_block, call_args):
            self.visit_Block(func_body_block, call_args)

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

        def execute(self, stmt):
            stmt.accept(self)

        def console_print(self, result):
            print("    Result: ")
            print("            " + str(result))
            print("")

        def visit_Dclr(self, dclr):
            value = None
            var_name = dclr.identifier.identifier.get_value()
            self.environment.add(var_name, None)
            if dclr.assign_expr is not None:
                value = self.evaluate(dclr.assign_expr)
            if not self.environment.assign(var_name, value):
                raise PloxRuntimeError("Redefinition of variable %s\n" % var_name, dclr.identifier.identifier.line)
            return None

        def visit_FuncDclr(self, f_dclr):
            func_name = f_dclr.handle.identifier.get_value()
            parameter_names = [x.identifier.get_value() for x in f_dclr.parameters]
            function = PloxCallable(func_name, f_dclr.body, parameter_names)
            if not self.environment.add(func_name, function):
                raise PloxRuntimeError("Redefinition of %s\n" % func_name, f_dclr.handle.identifier.line)

        def visit_PrintStmt(self, printstmt):
            expr_result = self.evaluate(printstmt.expr)
            print(str(expr_result))
            return None

        def visit_ExprStmt(self, exprstmt):
            expr_result = self.evaluate(exprstmt.expr)
            if self._console_mode:
                self.console_print(expr_result)
            return None

        def visit_Block(self, block, func_call_args=[]):
            self.environment.enter_block(func_call_args)
            excpt = None
            for stmt in block.stmts:
                try:
                    self.execute(stmt)
                except Exception as e:  # Need to make sure we pop the environment stack before exiting
                    excpt = e
            self.environment.exit_block()
            if excpt is not None:
                raise excpt
            return None

        def visit_IfStmt(self, ifstmt):
            if_expr_result = self.is_true(self.evaluate(ifstmt.expr))
            if if_expr_result is True:
                self.execute(ifstmt.if_block)
            elif ifstmt.else_block is not None:
                self.execute(ifstmt.else_block)
            return None

        def visit_WhileStmt(self, whilestmt):
            while_expr = self.is_true(self.evaluate(whilestmt.expr))
            while while_expr:
                self.execute(whilestmt.while_block)
                while_expr = self.is_true(self.evaluate(whilestmt.expr))

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
            elif operator == scanner.GREATER_THAN:
                if isinstance(left_result, float) and isinstance(right_result, float):
                    return left_result > right_result
                else:
                    raise PloxRuntimeError(" > Operator: Expected NUMBER", binary.operator.line)
            elif operator == scanner.LESS_THAN:
                if isinstance(left_result, float) and isinstance(right_result, float):
                    return left_result < right_result
                else:
                    raise PloxRuntimeError(" < Operator: Expected NUMBER", binary.operator.line)
            elif operator == scanner.LESS_THAN_EQUALS:
                if isinstance(left_result, float) and isinstance(right_result, float):
                    return left_result <= right_result
                else:
                    raise PloxRuntimeError(" <= Operator: Expected NUMBER", binary.operator.line)
            elif operator == scanner.GREATER_THAN_EQUALS:
                if isinstance(left_result, float) and isinstance(right_result, float):
                    return left_result >= right_result
                else:
                    raise PloxRuntimeError(" >= Operator: Expected NUMBER", binary.operator.line)
            elif operator == scanner.EQUALS:
                return left_result == right_result
            else:
                raise PloxRuntimeError(" " + binary.operator.literal + " unsupported operator", binary.operator.line)

        def visit_Grouping(self, grouping):
            return grouping.expr.accept(self)

        def visit_Literal(self, literal):
            return literal.literal.get_value()

        def visit_Idnt(self, idnt):
            var_name = idnt.identifier.get_value()
            try:
                value = self.environment.get_value(var_name)
            except Exception as e:
                raise PloxRuntimeError("Implicit declaration of variable %s." % var_name, idnt.identifier.line)
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
            if not self.environment.assign(var_name, assign_value):
                raise PloxRuntimeError("Implicit declaration of variable %s." % var_name, assign.left_side.identifier.line)
            return assign_value

        def visit_Call(self, call):
            callee_name = call.callee.identifier.get_value()
            try:
                function = self.evaluate(call.callee)
            except Exception:
                raise PloxRuntimeError("Implicit declaration of function %s." % callee_name, call.callee.identifier.line)
            if not callable(function):
                raise PloxRuntimeError("Attempting to call a non-callable object %s." % callee_name,
                                       call.callee.identifier.line)
            return function(self, [self.evaluate(x) for x in call.arguments])

        def visit_ReturnStmt(self, ret_stmt):
            raise Return(self.evaluate(ret_stmt.ret_val))


