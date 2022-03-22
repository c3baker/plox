Type_Binary = 0
Type_Grouping = 1
Type_Literal = 2
Type_Unary = 3
Type_ExprStmt = 4
Type_PrintStmt = 5
Type_Dclr = 6
Type_Idnt = 7
Type_Assign = 8
Type_Block = 9
Type_IfStmt = 10
Type_WhileStmt = 11
Type_Call = 12
Type_FuncDclr = 13
Type_ReturnStmt = 14
Type_BrkStmt = 15


class Binary:
    def __init__(self, left_expr, operator, right_expr):
        self.left_expr = left_expr
        self.operator = operator
        self.right_expr = right_expr
        self.type = Type_Binary

    def accept(self, visitor): 
        val = visitor.visit_Binary(self)
        return val


class Grouping:
    def __init__(self, expr):
        self.expr = expr
        self.type = Type_Grouping

    def accept(self, visitor): 
        val = visitor.visit_Grouping(self)
        return val


class Literal:
    def __init__(self, literal):
        self.literal = literal
        self.type = Type_Literal

    def accept(self, visitor): 
        val = visitor.visit_Literal(self)
        return val


class Unary:
    def __init__(self, operator, expr):
        self.operator = operator
        self.expr = expr
        self.type = Type_Unary

    def accept(self, visitor): 
        val = visitor.visit_Unary(self)
        return val


class ExprStmt:
    def __init__(self, expr):
        self.expr = expr
        self.type = Type_ExprStmt

    def accept(self, visitor): 
        val = visitor.visit_ExprStmt(self)
        return val


class PrintStmt:
    def __init__(self, expr):
        self.expr = expr
        self.type = Type_PrintStmt

    def accept(self, visitor): 
        val = visitor.visit_PrintStmt(self)
        return val


class Dclr:
    def __init__(self, var_name, assign_expr, line):
        self.var_name = var_name
        self.assign_expr = assign_expr
        self.line = line
        self.type = Type_Dclr

    def accept(self, visitor): 
        val = visitor.visit_Dclr(self)
        return val


class Idnt:
    def __init__(self, identifier):
        self.identifier = identifier
        self.type = Type_Idnt

    def accept(self, visitor): 
        val = visitor.visit_Idnt(self)
        return val


class Assign:
    def __init__(self, var_name, right_side, line):
        self.var_name = var_name
        self.right_side = right_side
        self.line = line
        self.type = Type_Assign

    def accept(self, visitor): 
        val = visitor.visit_Assign(self)
        return val


class Block:
    def __init__(self, stmts):
        self.stmts = stmts
        self.type = Type_Block

    def accept(self, visitor): 
        val = visitor.visit_Block(self)
        return val


class IfStmt:
    def __init__(self, expr, if_block, else_block):
        self.expr = expr
        self.if_block = if_block
        self.else_block = else_block
        self.type = Type_IfStmt

    def accept(self, visitor): 
        val = visitor.visit_IfStmt(self)
        return val


class WhileStmt:
    def __init__(self, expr, while_block):
        self.expr = expr
        self.while_block = while_block
        self.type = Type_WhileStmt

    def accept(self, visitor): 
        val = visitor.visit_WhileStmt(self)
        return val


class Call:
    def __init__(self, callee, arguments):
        self.callee = callee
        self.arguments = arguments
        self.type = Type_Call

    def accept(self, visitor): 
        val = visitor.visit_Call(self)
        return val


class FuncDclr:
    def __init__(self, handle, parameters, body, line):
        self.handle = handle
        self.parameters = parameters
        self.body = body
        self.line = line
        self.type = Type_FuncDclr

    def accept(self, visitor): 
        val = visitor.visit_FuncDclr(self)
        return val


class ReturnStmt:
    def __init__(self, ret_val):
        self.ret_val = ret_val
        self.type = Type_ReturnStmt

    def accept(self, visitor): 
        val = visitor.visit_ReturnStmt(self)
        return val


class BrkStmt:
    def __init__(self, ):
        self.type = Type_BrkStmt

    def accept(self, visitor): 
        val = visitor.visit_BrkStmt(self)
        return val


