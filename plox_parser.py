import plox_scanner as ps
import plox_syntax_trees as syntax_trees
import plox_utilities as utilities


class TreePrinter:
    def visit_Binary(self, binary):
        left_expr = binary.left_expr.accept(self)
        right_expr = binary.right_expr.accept(self)
        return '( ' + binary.operator.literal + ' ' + left_expr + ' ' + right_expr + ' )'

    def visit_Grouping(self, grouping):
        grouping_expr = grouping.expr.accept(self)
        return "( Group " + grouping_expr + " )"

    def visit_Literal(self, literal):
        return '( ' + str(literal.value) + ' )'

    def visit_Unary(self, unary):
        return '( ' + unary.operator.literal + unary.right_expr.accept(self) + ' )'

    def visit_ExprStmt(self, exprstmt):
        return exprstmt.expr.accept(self)

    def visit_PrintStmt(self, pstmt):
        expr = pstmt.expr.accept(self)
        return "( PRINT " + expr + ' )'


class TokenIterator(utilities.PloxIterator):
    def __init__(self, tokens):
        super().__init__(tokens)

    def match(self, match_list):
        token = self.peek()
        if token is None:
            return False
        if token.type in match_list:
            self.advance()
            return True
        return False


class PloxSyntaxError(Exception):
    def __init__(self, message, line):
        self.message = message
        self.line = line
        super().__init__(self.message)

    def get_error_message(self):
        return " Syntax Error: " + self.message


class Parser:
    parser = None

    def __init__(self, scanned_tokens):
        if self.parser is None:
            self.parser = self._Parser(scanned_tokens)
        else:
            self.parser.tokens = scanned_tokens
            self.parser.statements = []


    def parse(self):
        syntax_tree = self.parser.parse()
        return syntax_tree

    class _Parser:
        def __init__(self, scanned_tokens):
            self.tokens = TokenIterator(scanned_tokens)
            self.statements = []

        def parse(self):
            while self.tokens.list_end() is False:
                stmt = self.statement()
                self.statements.append(stmt)
            return self.statements

        def statement(self):
            if self.tokens.match([ps.KEYWORD_PRINT]):
                return self.statement_print()
            else:
                return self.statement_expression()

        def statement_print(self):
            expr = self.expression()
            if self.tokens.match([ps.SEMI_COLON]) is False:
                raise PloxSyntaxError("Expected ; after statement.", self.tokens.previous().line)
            return syntax_trees.PrintStmt(expr)

        def statement_expression(self):
            expr = self.expression()
            if self.tokens.match([ps.SEMI_COLON]) is False:
                raise PloxSyntaxError("Expected ; after statement.", self.tokens.previous().line)
            return syntax_trees.ExprStmt(expr)

        def expression(self):
            return self.equality()

        def equality(self):
            expr = self.comparision()
            while self.tokens.match([ps.NOT_EQUALS, ps.EQUALS]):
                operator = self.tokens.previous()
                right = self.comparision()
                expr = syntax_trees.Binary(expr, operator, right)
            return expr

        def comparision(self):
            expr = self.term()
            while self.tokens.match([ps.GREATER_THAN_EQUALS, ps.GREATER_THAN, ps.LESS_THAN, ps.LESS_THAN_EQUALS]):
                operator = self.tokens.previous()
                right = self.term()
                expr = syntax_trees.Binary(expr, operator, right)
            return expr

        def term(self):
            expr = self.factor()
            while self.tokens.match([ps.ADD, ps.MINUS]):
                operator = self.tokens.previous()
                right = self.factor()
                expr = syntax_trees.Binary(expr, operator, right)
            return expr

        def factor(self):
            expr = self.unary()
            while self.tokens.match([ps.STAR, ps.DIV]):
                operator = self.tokens.previous()
                right = self.unary()
                expr = syntax_trees.Binary(expr, operator, right)
            return expr

        def unary(self):
            if self.tokens.match([ps.BANG, ps.MINUS]):
                return syntax_trees.Unary(self.tokens.previous(), self.unary())
            else:
                return self.primary()

        def primary(self):
            token = self.tokens.advance()
            if token.type == ps.NUMBER or token.type == ps.STRING or token.type == ps.KEYWORD_TRUE or \
               token.type == ps.KEYWORD_FALSE or token.type == ps.KEYWORD_NIL:
                    return syntax_trees.Literal(token.literal)
            elif token.type == ps.OPEN_PAREN:
                syntax_tree = syntax_trees.Grouping(self.expression())
                if self.tokens.match([ps.CLOSE_PAREN]):
                        return syntax_tree
                else:
                    raise PloxSyntaxError("Syntax Error; Missing )", self.tokens.peek().line)
            raise PloxSyntaxError("Syntax Error: Unexpected Construct", self.tokens.peek().line)



