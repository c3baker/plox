import plox_scanner as scanner
import plox_syntax_trees as syntax_trees
import plox_utilities as utilties

GLOBAL = 1

class PloxCallable:

    def __init__(self, name, block_stmt, parameter_names=[], context_level=GLOBAL):
        self.function_body = block_stmt
        self.parameter_names = parameter_names
        self.callable_name = name
        self.env_context_level = context_level

    def __call__(self, interpreter, args=[]):
        ret_val = None
        if len(args) != len(self.parameter_names):
            raise PloxRuntimeError("Function %s expects %d arguments but %d given." % (self.callable_name,
                                                                                       len(self.parameter_names),
                                                                                       len(args)))
        interpreter.enter_function_call(self.env_context_level)
        try:
            interpreter.execute_function_body(self.function_body, zip(self.parameter_names, args))
        except Return as ret:
            ret_val = ret.value
        interpreter.exit_function_call()
        return ret_val

    def to_string(self):
        return "<fn " + self.name + ": " + len(self.parameter_names) + ">"


@utilties.singleton
class Environment:
    resolved_identifiers = {}
    reserve_stack = []

    def __init__(self, init_contexts=[]):
        if not isinstance(init_contexts, list):
            raise RuntimeError("Contexts must be stored in a list! Something is being passed wrong here!")
        self.contexts = init_contexts

        self.push_context()

    def push_context(self):
        self.contexts.append({})

    def pop_context(self):
        if len(self.contexts) == 0:
            return
        self.contexts.pop()

    def current_context_depth(self):
        return len(self.contexts)

    def enter_block(self, zipped_params_args):
        self.push_context()
        for param in zipped_params_args:
            # If This is a function call we need
            # To add the function arguments to the local environment
            if len(param) > 0:
                param_name, arg = param
                self.add(param_name, arg)

    def exit_block(self):
        self.pop_context()

    def resolve_identifier(self, expr, scope_depth):
        self.resolved_identifiers[expr] = scope_depth

    def add(self, name, value):
        if name in self.contexts[-1]:
            return False
        self.contexts[-1][name] = value
        return True

    def find(self, name):
        c = None
        i = 0
        self.contexts.reverse()
        for context in self.contexts:
            if name in context:
                c = context
                break
            i += 1
        self.contexts.reverse() # Put the list back to its original order
        context_level = len(self.contexts) - i
        return c, context_level

    def get_at(self, context_level, name):
        return self.contexts[context_level][name]

    def set_at(self, context_level, name, value):
        self.contexts[context_level][name] = value

    def assign(self, assign_expr, value):
        if not isinstance(assign_expr, syntax_trees.Assign):
            raise Exception("Expected Assignment Expression")
        return self.set_at(self.resolved_identifiers[assign_expr], assign_expr.var_name, value)

    def get_value(self, ident_expr):
        if not isinstance(ident_expr, syntax_trees.Idnt):
            return None
        return self.get_at(self.resolved_identifiers[ident_expr], ident_expr.identifier.get_value())

    def get_global_context(self):
        return self.contexts[0]  # The first context in the stack is the global context

    def enter_function_call(self, context_level_limit=[]):
        self.enter_closure_context(context_level_limit)

    def exit_function_call(self):
        self.exit_closure_context()

    def enter_closure_context(self, context_level_limit):
        if context_level_limit >= len(self.contexts):
            return  # Do nothing
        context_level_limit = GLOBAL if context_level_limit <= 0 else context_level_limit
        contexts_to_reserve = self.contexts[context_level_limit:]
        self.reserve_stack.append(contexts_to_reserve)
        # Remove the non-globals from the active environment
        closure_contexts = self.contexts[:context_level_limit]
        self.contexts = []
        self.contexts.extend(closure_contexts)

    def exit_closure_context(self):
        last_contexts = []
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

@utilties.singleton
class Interpreter:
    environment = Environment()

    def __init__(self, console_mode=False):
        super().__init__()
        self._console_mode = console_mode

    def interpret(self, statements):
        for stmt in statements:
            try:
                self.execute(stmt)
            except PloxRuntimeError as e:
                utilties.report_error(e)
            except Break:
                raise PloxRuntimeError("Break must be called within a loop context.")

    def resolve_identifier(self, expr, scope_level):
        self.environment.resolve_identifier(expr, scope_level)

    def enter_function_call(self, context_level):
        return self.environment.enter_function_call(context_level)

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
        var_name = dclr.var_name
        self.environment.add(var_name, None)
        if dclr.assign_expr is not None:
            value = self.evaluate(dclr.assign_expr)
            try:
                self.environment.assign(dclr.assign_expr, value)
            except Exception:
                raise PloxRuntimeError("Redefinition of variable %s\n" % var_name, dclr.identifier.identifier.line)
        return None

    def visit_FuncDclr(self, f_dclr):
        function = PloxCallable( f_dclr.handle, f_dclr.body, f_dclr.parameters,
                                 self.environment.current_context_depth())
        if not self.environment.add(f_dclr.handle, function):
            raise PloxRuntimeError("Redefinition of %s\n" % f_dclr.handle, f_dclr.line)

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
        try:
            for stmt in block.stmts:
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
        try:
            value = self.environment.get_value(idnt)
        except Exception as e:
            raise PloxRuntimeError("Implicit declaration of variable %s." % idnt.identifier.get_value(),
                                   idnt.identifier.line)
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
        assign_value = self.evaluate(assign.right_side)
        try:
            self.environment.assign(assign, self.evaluate(assign.right_side))
        except Exception as e:
            raise PloxRuntimeError("Implicit declaration of variable %s." % assign.var_name,
                                   assign.line)
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
        ret_value = None
        if ret_stmt.ret_val is not None:
            ret_value = self.evaluate(ret_stmt.ret_val)
        raise Return(ret_value)


