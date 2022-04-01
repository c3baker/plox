import plox_scanner as scanner
import plox_syntax_trees as syntax_trees
import plox_utilities as utilties

GLOBAL = 1


class PloxClass:
    def __init__(self, name, methods, super_class=None):
        self.name = name
        self.methods = methods
        self.super_class = super_class

    def __call__(self, interpreter, args=[]):

        instance = PloxInstance(self)
        try:
            constructor = instance.bind(self.get_method("__init__"))
        except Exception:
            return instance # No constructor declared just return the instance
        constructor(interpreter, args)
        return instance

    def __str__(self):
        return self.name

    def get_method(self, method_name):
        if method_name in self.methods:
            return self.methods[method_name]
        return self.super_class.get_method(method_name)


class PloxInstance:
    def __init__(self, cls):
        self.class_type = cls
        self.fields = {}

    def __str__(self):
        return str(self.class_type())

    def bind(self, method):
        method.bind_class_method(self)
        return method

    def get(self, field_name):
        if field_name in self.fields:
            return self.fields[field_name]
        return self.bind(self.class_type.get_method(field_name))

    def set(self, field_name, value):
        self.fields[field_name] = value



class PloxFunction:

    def __init__(self, name, block_stmt, closure, parameter_names=[]):
        self.function_body = block_stmt
        self.parameter_names = parameter_names
        self.callable_name = name
        self.closure = closure

    def __call__(self, interpreter, args=[]):
        ret_val = None
        if len(args) != len(self.parameter_names):
            raise PloxRuntimeError("Function %s expects %d arguments but %d given." % (self.callable_name,
                                                                                       len(self.parameter_names),
                                                                                       len(args)))
        try:
            interpreter.execute_function_body(self.function_body, zip(self.parameter_names, args), self.closure)
        except Return as ret:
            ret_val = ret.value
        return ret_val

    def bind_class_method(self, instance):
        self.closure.bind_class_instance(instance)

    def to_string(self):
        return "<fn " + self.name + ": " + len(self.parameter_names) + ">"


class Environment:

    def __init__(self, base_environment=None):
        self.scopes = [{}] if base_environment is None else base_environment.create_closure()
        self.resolved_identifiers = {} if base_environment is None else base_environment.resolved_identifiers

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        if len(self.scopes) == 0:
            return
        self.scopes.pop()

    def current_context_depth(self):
        return len(self.scopes)

    def enter_block(self, zipped_params_args):
        self.push_scope()
        for param in zipped_params_args:
            # If This is a function call we need
            # To add the function arguments to the local environment
            if len(param) > 0:
                param_name, arg = param
                self.add(param_name, arg)

    def exit_block(self):
        self.pop_scope()

    def resolve_identifier(self, expr, scope_depth):
        self.resolved_identifiers[expr] = scope_depth

    def add(self, name, value):
        if name in self.scopes[-1]:
            raise PloxRuntimeError("Redeclaration of variable %s" % name)
        self.scopes[-1][name] = value

    def find(self, name):
        c = None
        i = 0
        self.scopes.reverse()
        for scope in self.scopes:
            if name in scope:
                c = scope
                break
            i += 1
        self.scopes.reverse() # Put the list back to its original order
        context_level = len(self.scopes) - i
        return c, context_level

    def get_at(self, context_level, name):
        abs_context_level = len(self.scopes) - context_level - 1
        return self.scopes[abs_context_level][name]

    def set_at(self, context_level, name, value):
        abs_context_level = len(self.scopes) - context_level - 1
        self.scopes[abs_context_level][name] = value

    def assign(self, assign_expr, value):
        if not isinstance(assign_expr, syntax_trees.Assign):
            raise Exception("Expected Assignment Expression")
        return self.set_at(self.resolved_identifiers[assign_expr], assign_expr.var_name, value)

    def get_value(self, expr):
        if isinstance(expr, syntax_trees.Idnt):
            name = expr.identifier.get_value()
        elif isinstance(expr, syntax_trees.ThisStmt):
            name = "this"
        else:
            raise Exception("Invalid lookup value")
        return self.get_at(self.resolved_identifiers[expr], name)

    def get_global_context(self):
        return self.scopes[0]  # The first context in the stack is the global context

    def create_closure(self):
        closure = []
        closure.extend(self.scopes)
        return closure

    def bind_class_instance(self, instance):
        instance_context = {'this': instance}
        self.scopes.append(instance_context)


class PloxRuntimeError(utilties.PloxError):
    def __init__(self, message, line=0):
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

    def __init__(self, console_mode=False):
        super().__init__()
        self._console_mode = console_mode
        self.environments = [Environment()]

    def interpret(self, statements):
        for stmt in statements:
            try:
                self.execute(stmt)
            except PloxRuntimeError as e:
                utilties.report_error(e)
            except Break:
                raise PloxRuntimeError("Break must be called within a loop context.")

    def resolve_identifier(self, expr, scope_level):
        self.environments[-1].resolve_identifier(expr, scope_level)

    def enter_function_call(self, function_closure):
        self.environments.append(function_closure)

    def exit_function_call(self):
        self.environments.pop()

    def execute_function_body(self, func_body_block, call_args, function_env):
        self.enter_function_call(function_env)
        self.visit_Block(func_body_block, call_args)
        self.exit_function_call()

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
        var_name = dclr.var_name
        try:
            self.environments[-1].add(var_name, None)
        except PloxRuntimeError as e:
            raise PloxRuntimeError(e.message, dclr.line)
        if dclr.assign_expr is not None:
            value = self.evaluate(dclr.assign_expr)
            try:
                self.environments[-1].assign(dclr.assign_expr, value)
            except Exception:
                raise PloxRuntimeError("Redefinition of variable %s\n" % var_name, dclr.line)

    def visit_FuncDclr(self, f_dclr):
        function = PloxFunction(f_dclr.handle, f_dclr.body,
                                Environment(self.environments[-1]), f_dclr.parameters)
        try:
            self.environments[-1].add(f_dclr.handle, function)
        except PloxRuntimeError as e:
            raise PloxRuntimeError(e.message, f_dclr.line)

    def visit_ClassDclr(self, clsdclr):
        methods = {}
        for method in clsdclr.methods:
            class_method = PloxFunction(method.handle, method.body,
                                        Environment(self.environments[-1]), method.parameters)
            methods[method.handle] = class_method

        super_class = None
        if clsdclr.super is not None:
            super_class = self.evaluate(clsdclr.super)

        new_class = PloxClass(clsdclr.class_name, methods, super_class)
        try:
            self.environments[-1].add(clsdclr.class_name, new_class)
        except PloxRuntimeError as e:
            raise PloxRuntimeError(e.message, clsdclr.line)

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
        self.environments[-1].enter_block(func_call_args)
        excpt = None
        try:
            for stmt in block.stmts:
                self.execute(stmt)
        except Exception as e:  # Need to make sure we pop the environment stack before exiting
            excpt = e
        self.environments[-1].exit_block()
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
            try:
                self.execute(whilestmt.while_block)
            except Break:
                return
            while_expr = self.is_true(self.evaluate(whilestmt.expr))

    def visit_Binary(self, binary):
        left_result = binary.left_expr.accept(self)
        right_result = binary.right_expr.accept(self)

        operator = binary.operator.type

        if operator == scanner.ADD:
            if isinstance(left_result, str):
                return left_result + str(right_result)
            elif isinstance(left_result, float) and isinstance(right_result, float):
                return left_result + right_result
            elif isinstance(left_result, float) and isinstance(right_result, str):
                return str(left_result) + right_result
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
            value = self.environments[-1].get_value(idnt)
        except Exception as e:
            raise PloxRuntimeError("Implicit declaration of identifier %s." % idnt.identifier.get_value(),
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
            self.environments[-1].assign(assign, assign_value)
        except Exception as e:
            raise PloxRuntimeError("Implicit declaration of variable %s." % assign.var_name,
                                   assign.line)
        return assign_value

    def visit_Call(self, call):
        try:
            function = self.evaluate(call.callee)
        except Exception as e:
            raise PloxRuntimeError("Implicit declaration of function %s." % str(call.callee),
                                   call.line)
        if not callable(function):
            raise PloxRuntimeError("Attempting to call a non-callable object .", call.callee.identifier.line)
        return function(self, [self.evaluate(x) for x in call.arguments])

    def visit_Get(self, get):
        try:
            object = self.evaluate(get.object)
        except Exception:
            raise PloxRuntimeError("Accessing unknown object", get.line)
        if not isinstance(object, PloxInstance):
            raise PloxRuntimeError("Accessing something other than an object", get.line)
        try:
            return object.get(get.field_name)
        except Exception:
            raise PloxRuntimeError("Class %s has no such field %s" % (str(object),
                                                                      get.field_name), get.line)

    def visit_Set(self, set):
        set_value = self.evaluate(set.right_side)
        try:
            object = self.evaluate(set.object)
        except Exception:
            raise PloxRuntimeError("Attempting to set unknown object", set.line)
        if not isinstance(object, PloxInstance):
            raise PloxRuntimeError("Accessing something other than an object", set.line)
        object.set(set.field_name, set_value)
        

    def visit_ReturnStmt(self, ret_stmt):
        ret_value = None
        if ret_stmt.ret_val is not None:
            ret_value = self.evaluate(ret_stmt.ret_val)
        raise Return(ret_value)

    def visit_BrkStmt(self, brk):
        raise Break()

    def visit_ThisStmt(self, this):
        return self.environments[-1].get_value(this)





