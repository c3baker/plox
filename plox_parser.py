import plox_scanner as ps
import plox_syntax_trees as syntax_trees


class Parser:

    parser = None
    def __init__(self, scanned_tokens):
        if self.parser is None:
            self.parser = self._Parser(scanned_tokens)

    class _Parser:
        def __init__(self, scanned_tokens):
            self.tokens = scanned_tokens
            self.index = 0

        def previous(self):
            if self.index == 0:
                return None
            return self.tokens[self.index - 1]

        def peek(self):
            return None if self.index >= len(self.tokens) else self.tokens[self.index]

        def advance(self):
            self.index = self.index + 1 if self.index < len(self.tokens) else self.index
            return self.previous()

        def match_tokens(self, token, match_list):
            if token is None:
                return False
            if token in match_list:
                self.advance()
                return True
            return False

        def expression(self):
            return self.equality()

        def equality(self):
            expr = self.comparision()
            while self.match_tokens(self.peek(), [ps.NOT_EQUALS, ps.EQUALS]):
                operator = self.previous()
                right = self.comparision()
                expr = syntax_trees.Binary(expr, operator, right)
            return expr

        def comparision(self):
            expr = self.term
            while self.match_tokens(self.peek,
                                    [ps.GREATER_THAN_EQUALS, ps.GREATER_THAN, ps.LESS_THAN, ps.LESS_THAN_EQUALS]):
                operator = self.previous()
                right = self.term()
                expr = syntax_trees.Binary(expr, operator, right)
            return expr

        def term(self):
            expr = self.factor
            while self.match_tokens(self.peek(), [ps.ADD, ps.MINUS]):
                operator = self.previous()
                right = self.factor()
                expr = syntax_trees.Binary(expr, operator, right)
            return expr

        def factor(self):
            expr = self.unary
            while self.match_tokens(self.peek(), [ps.STAR, ps.DIV]):
                operator = self.previous()
                right = self.unary()
                expr = syntax_trees.Binary(expr, operator, right)
            return expr

        def unary(self):
            if self.match_tokens(self.peek(), [ps.BANG, ps.MINUS]):
                return syntax_trees.Unary(self.previous(), self.unary())
            else:
                return self.primary()

        def primary(self):
            token = self.peek()
            if token.type == ps.NUMBER or token.type == ps.STRING or token.type == ps.KEYWORD_TRUE or \
               token.type == ps.KEYWORD_FALSE:
                    return syntax_trees.Literal(token.literal)
            return syntax_trees.Grouping(self.expression())


