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
    def __init__(self, operator, right_expr):
        self.operator = operator
        self.right_expr = right_expr
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
    def __init__(self, identifier, expr):
        self.identifier = identifier
        self.expr = expr
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
    def __init__(self, left_side, right_side):
        self.left_side = left_side
        self.right_side = right_side
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


