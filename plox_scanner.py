OPEN_PAREN = 0
CLOSE_PAREN = 1
OPEN_BRACE = 2
CLOSE_BRACE = 3
ADD = 4
MINUS = 5
STAR = 6
DIV = 7
ASSIGN = 8
COMMA = 9
SEMI_COLON = 10
GREATER_THAN = 11
GREATER_THAN_EQUALS = 12
LESS_THAN = 13
LESS_THAN_EQUALS = 14
EQUALS = 15
NOT_EQUALS = 16
NOT = 17
KEYWORD_OR = 18
KEYWORD_AND = 19
STRING = 20
COMMENT = 21
KEYWORD_PRINT = 22
KEYWORD_IF = 23
KEYWORD_ELSE = 24
KEYWORD_VAR = 25
KEYWORD_CLASS = 26
KEYWORD_RETURN = 27
KEYWORD_WHILE = 28
KEYWORD_FOR = 29
KEYWORD_FUN = 30
KEYWORD_TRUE = 31
KEYWORD_FALSE = 32
IDENTIFIER = 33
SLASH = 34
BANG = 35
NUMBER = 36


class Token:
    def __init__(self, token_type, literal):
        self.type = token_type
        self.literal = literal
        print("Token: %s" % literal)


class Scanner:
    scanner = None

    class _Scanner:
        source = None
        start = 0
        current = 0

        simple_token_lookup = {'(': OPEN_PAREN, ')': CLOSE_PAREN, '{': OPEN_BRACE, '}': CLOSE_BRACE,
                               '+': [ADD], '-': MINUS, '*': STAR, ';': SEMI_COLON, ',': COMMA, '/': DIV,
                               '"': STRING, "!": BANG, ">": GREATER_THAN, "<": LESS_THAN, "=": ASSIGN}
        keyword_lookup = {'or' : [KEYWORD_OR], 'and': [KEYWORD_AND], 'class': [KEYWORD_CLASS], 'if': [KEYWORD_IF],
                          'else' : [KEYWORD_ELSE], 'true': [KEYWORD_TRUE], 'false': [KEYWORD_FALSE],
                          'while' : [KEYWORD_WHILE], 'for': [KEYWORD_FOR], 'return': [KEYWORD_RETURN],
                          'var' : [KEYWORD_VAR], 'fun' : [KEYWORD_FUN], 'print': [KEYWORD_PRINT]}
        compound_symbols = {DIV: [COMMENT, '/'], LESS_THAN: [LESS_THAN_EQUALS, '='],
                            GREATER_THAN: [GREATER_THAN_EQUALS, '='], ASSIGN: [EQUALS, '='],
                            BANG: [NOT_EQUALS, '=']}

        def __init__(self, source):
            self._init_members(source)

        def _init_members(self, source):
            self.line = 0
            self.start = 0
            self.current = 0
            self.tokens = []
            self.source = source

        def raise_lexical_error(self, message):
            raise Exception(message)

        def set_source(self, source):
            self._init_members(source)

        def advance(self):
            if self.end_of_source() is True:
                return None
            c = self.source[self.current]
            self.current += 1
            return c

        def peek_next(self):
            if self.end_of_source() is True:
                return None
            return self.source[self.current]

        def end_of_source(self):
            return self.current >= len(self.source)

        def add_token(self, token_type):
            self.tokens.append(Token(token_type, self.get_current_source_string()))

        def has_matching_symbol(self, match):
            if self.end_of_source():
                return False
            if self.peek_next() == match:
                self.advance()
                return True
            return False

        def get_current_source_string(self):
            return self.source[self.start:self.current]

        def read_numeric_symbol(self):
            floating_point_count = 0
            c = self.peek_next()
            if c is not None:
                while c.isnumeric():
                    self.advance()
                    c = self.peek_next()
                    if c == '.' and floating_point_count == 0:
                        floating_point_count += 1
                    elif floating_point_count > 0:
                        self.raise_lexical_error("Lexical Error: Too many decimal points in numeric.")

            self.add_token(NUMBER)

        def read_alpha_symbol(self):
            c = self.peek_next()
            if c is not None:
                while c.isalnum() or c == '_':
                    self.advance()
                    c = self.peek_next()
                    if c is None:
                        break

            symbol = self.get_current_source_string()
            token_id = IDENTIFIER if symbol not in self.keyword_lookup.keys() else self.keyword_lookup[symbol]
            self.add_token(token_id) # Token is an identifier

        def could_be_compound_symbol(self, token_id):
            return True if token_id in self.compound_symbols.keys() else False

        def scan_string(self):
            while self.advance() != '"':
                if self.end_of_source():
                    self.raise_lexical_error("Lexical Error: Reached EOF without closing \" ")
            self.add_token(STRING)

        def scan_comment(self):
            while self.peek_next() != "\n":
                if self.end_of_source():
                    return
                self.advance()

        def scan_simple_symbol(self, token_id):
            if self.could_be_compound_symbol(token_id):
                match = self.compound_symbols[token_id]
                if self.has_matching_symbol(match[1]):
                    self.add_token(match[0])
                else:
                    self.add_token(token_id)
            elif token_id == STRING:
                self.scan_string()
            elif token_id == COMMENT:
                self.scan_comment()
            else:
                self.add_token(token_id)

        def scan(self):
            while not self.end_of_source():
                self.start = self.current
                c = self.advance()
                if c == ' ' or c == "\t":
                    continue
                if c == "\n":
                    self.line += 1
                    continue

                if c.isalpha():
                    self.read_alpha_symbol()
                elif c.isnumeric():
                    self.read_numeric_symbol()
                else:
                    token_id = self.simple_token_lookup[c]
                    if token_id is None:
                        self.raise_lexical_error("Lexical Error: Unrecognized symbol %c." % c)
                    else:
                        self.scan_simple_symbol(token_id)




    def __init__(self, source):
        if not self.scanner:
            self.scanner = self._Scanner(source)
        else:
            self.scanner.set_source(source)



