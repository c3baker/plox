import plox_utilities as utilities
from plox_syntax_trees import *
from plox_interpreter import *


@utilities.singleton
class Resolver:

    def __init__(self):
        self.scopes = [{}]
        self.has_error = False
        self.interpreter = None
        self.loop_depth = 0
        self.func_depth = 0

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        if len(self.scopes) == 0:
            return
        self.scopes.pop()

    def error_occurred(self):
        return self.has_error

    def resolve(self, interpreter, syntaxes):
        self.interpreter = interpreter
        self.has_error = False
        self.scopes = [{}]
        self.loop_depth = 0
        self.func_depth = 0

        try:
            self.resolve_statements(syntaxes)
        except PloxRuntimeError as e:
            utilities.report_error(e)
            self.has_error = True

    def resolve_statements(self, stmts):
            for s in stmts:
                self._resolve(s)

    def _resolve(self, syntax):
        if syntax is None:
            return
        syntax.accept(self)

    def declare(self, name):
        if len(self.scopes) == 0:
            return
        self.get_current_scope()[name] = False

    def define(self, name):
        if len(self.scopes) == 0:
            return
        self.get_current_scope()[name] = True

    def get_current_scope(self):
        if len(self.scopes) == 0:
            return None
        return self.scopes[-1]

    def resolve_identifier(self, expr, name):
        scopes_depth = len(self.scopes)
        if scopes_depth == 0:
            return
        '''
        Look back "up" the context stack to see in which context
        the matching identifier is declared. 0 means the declaration is in
        the same context as the usage, 1 means the previous context, etc. 
        '''
        for i in range(scopes_depth):
            if name in self.scopes[scopes_depth - (i + 1)]:
                self.interpreter.resolve_identifier(expr, i)
                break

    def visit_Block(self, blk, function_params=[]):
        self.push_scope()
        for param in function_params:
            self.declare(param)
            self.define(param)
        self.resolve_statements(blk.stmts)
        self.pop_scope()

    def visit_Dclr(self, dclr):
        self.declare(dclr.var_name)
        if dclr.assign_expr is not None:
            self._resolve(dclr.assign_expr)
        self.define(dclr.var_name)

    def visit_Assign(self, assign):
        self._resolve(assign.right_side)
        self.resolve_identifier(assign, assign.var_name)

    def visit_FuncDclr(self, fdclr):
        self.declare(fdclr.handle)
        self.define(fdclr.handle)
        self.resolve_function(fdclr)

    def visit_ClassDclr(self, cldclr):
        self.declare(cldclr.class_name)
        self.push_scope()
        self.declare("this")
        self.define("this")
        for method in cldclr.methods:
            self.resolve_function(method)
        self.pop_scope()
        self.define(cldclr.class_name)


    def resolve_function(self, function):
        self.visit_Block(function.body, function.parameters)

    def visit_Binary(self, binary):
        self._resolve(binary.left_expr)
        self._resolve(binary.right_expr)

    def visit_Grouping(self, grouping):
        self._resolve(grouping.expr)

    def visit_Literal(self, ltrl):
        return

    def visit_Unary(self, unry):
        self._resolve(unry.expr)

    def visit_ExprStmt(self, exprstmt):
        self._resolve(exprstmt.expr)

    def visit_PrintStmt(self, prnt):
        self._resolve(prnt.expr)

    def visit_Idnt(self, idnt):
        idnt_name = idnt.identifier.get_value()
        if (len(self.scopes)) > 0 and ((idnt_name in self.get_current_scope()) and
                                       (self.get_current_scope()[idnt_name] is False)):
            raise PloxRuntimeError("Can't read local variable in its own initializer.", idnt.identifier.line)
        self.resolve_identifier(idnt, idnt_name)

    def visit_IfStmt(self, ifstmt):
        self._resolve(ifstmt.expr)
        self._resolve(ifstmt.if_block)
        self._resolve(ifstmt.else_block)

    def visit_WhileStmt(self, whilestmt):
        self._resolve(whilestmt.expr)
        self.loop_depth += 1
        self._resolve(whilestmt.while_block)
        self.loop_depth -= 1

    def visit_ReturnStmt(self, rtrn):
        self._resolve(rtrn.ret_val)

    def visit_Call(self, call):
        self._resolve(call.callee)
        for arg in call.arguments:
            self._resolve(arg)

    def visit_BrkStmt(self, bstmt):
        if self.loop_depth == 0:
            raise PloxRuntimeError("Illegal break from non-loop context", bstmt.line)

    def visit_Get(self, get):
        self._resolve(get.object)

    def visit_Set(self, set):
        self._resolve(set.right_side)
        self.resolve(set.object)

    def visit_ThisStmt(self, this):
        self.resolve_identifier(this, "this")













