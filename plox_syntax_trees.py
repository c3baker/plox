Binary = 0
Grouping = 1
Literal = 2
Unary = 3


class Binary:
    def __init__(self, left_expr, operator, right_expr):
        self.left_expr = left_expr
        self.operator = operator
        self.right_expr = right_expr
        self.type = Binary


class Grouping:
    def __init__(self, expr):
        self.expr = expr
        self.type = Grouping


class Literal:
    def __init__(self, value):
        self.value = value
        self.type = Literal


class Unary:
    def __init__(self, operator, right_expr):
        self.operator = operator
        self.right_expr = right_expr
        self.type = Unary


