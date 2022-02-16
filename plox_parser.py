import plox_scanner as ps
import plox_syntax_trees as syntax_trees
import plox_utilities as utilities


class TreePrinter:
    def visit_Binary(self, binary):
        left_expr = binary.left_expr.accept(self)
        right_expr = binary.right_expr.accept(self)
        return left_expr + ' ' + binary.operator + ' ' + right_expr

    def visit_Grouping(self, grouping):
        grouping_expr = grouping.expr.accept(self)
        return "( " + grouping_expr + " )"

    def visit_Literal(self, literal):
        return literal.value

    def visit_Unary(self, unary):
        return unary.operator + unary.right_expr.accept(self)


class TokenIterator(utilities.PloxIterator):
    def __init__(self, tokens):
        super().__init__(tokens)

    def match(self, token, match_list):
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
        return self.message


class Parser:
    parser = None

    def __init__(self, scanned_tokens):
        if self.parser is None:
            self.parser = self._Parser(scanned_tokens)

    def parse(self):
        syntax_tree = self.parser.parse()
        return syntax_tree

    class _Parser:
        def __init__(self, scanned_tokens):
            self.tokens = TokenIterator(scanned_tokens)
            self.index = 0

        def parse(self):
            p_expr = self.expression()
            return p_expr

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
                        self.tokens.advance()
                        return syntax_tree
                else:
                    raise PloxSyntaxError("Syntax Error; Missing )", self.tokens.peek().line)
            raise PloxSyntaxError("Syntax Error: Unexpected Construct", self.tokens.peek().line)



