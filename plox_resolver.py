import plox_utilities as utilities
from plox_syntax_trees import *
from plox_interpreter import *

@utilities.singleton
class Resolver:

    def __init__(self):
        self.scopes = []

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        if len(self.scopes) == 0:
            return
        self.scopes.pop()

    def resolve_stmts(self, statements):
        for stmt in statements:
            self.resolve(stmt)

    def resolve_exprs(self, expressions):
        for expr in expressions:
            self.resolve(expr)

    def resolve(self, syntax):
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

    def resolve_local(self, expr, name):
        scopes_depth = len(self.scopes)
        for i in range(scopes_depth):
            if name in self.scopes[scopes_depth - (i + 1)]:
                self.resolve(expr)

    def visit_Block(self, blk, function_params=[]):
        self.push_scope()
        for param in function_params:
            self.declare(param)
            self.define(param)
        self.resolve_stmts(blk.stmts)
        self.pop_scope()

    def visit_Dclr(self, dclr):
        self.declare(dclr.var_name)
        self.resolve(dclr.assign_expr)
        self.define(dclr.var_name)

    def visit_Assign(self, assign):
        self.resolve(assign.right_side)
        self.resolve_local(assign.var_name, assign.right_side)

    def visit_FuncDclr(self, fdclr):
        self.declare(fdclr.handle)
        self.define(fdclr.handle)
        self.resolve_function(fdclr)

    def resolve_function(self, function):
        self.visit_Block(function.body, function.parameters)

    def visit_Binary(self, binary):
        self.resolve(binary.left_expr)
        self.resolve(binary.right_expr)

    def visit_Grouping(self, grouping):
        self.resolve(grouping.expr)

    def visit_Literal(self, ltrl):
        return

    def visit_Unary(self, unry):
        self.resolve(unry.expr)

    def visit_ExprStmt(self, exprstmt):
        self.resolve(exprstmt.expr)

    def visit_PrintStmt(self, prnt):
        self.resolve(prnt.expr)

    def visit_Idnt(self, idnt):
        idnt_name = idnt.identifier.get_value()
        if (len(self.scopes)) > 0 and ((idnt_name in self.get_current_scope()) and
                                       (self.get_current_scope()[idnt_name] is False)):
            raise PloxRuntimeError("Can't read local variable in its own initializer.", idnt.identifier.line)

    def visit_IfStmt(self, ifstmt):
        self.resolve(ifstmt.expr)
        self.resolve(ifstmt.if_block)
        self.resolve(ifstmt.else_block)

    def visit_WhileStmt(self, whilestmt):
        self.resolve(whilestmt.expr)
        self.resolve(whilestmt.while_block)

    def visit_ReturnStmt(self, rtrn):
        self.resolve(rtrn.ret_val)











