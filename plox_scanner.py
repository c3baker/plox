import plox_utilities as utilities

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


class SourceIterator(utilities.PloxIterator):
    def __init__(self, source):
        super().__init__(source)
        self._start = 0
        self._line = 0

    def is_whitespace(self):
        c = self.peek()
        return True if c == ' ' or c == '\t' or c == '\n' else False

    def start_next_token(self):
        self._start = self.get_index() - 1 if self.get_index() > 0 else 0

    def source_current_string(self):
        end = self.get_index() if not self.list_end() else len(self._list) - 1
        return self._list[self._start:end]

    def advance(self):
        while self.is_whitespace():
            c = utilities.PloxIterator.advance(self)
            if c == '\n':
                self._line += 1
        return utilities.PloxIterator.advance(self)

    def get_current_line(self):
        return self._line

    def match(self, char):
        ret = True if self.peek_next() == char else False
        if ret:
            self.advance()
        return ret


class LexicalError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def get_error_message(self):
        return self.message


class Token:
    def __init__(self, token_type, literal):
        self.type = token_type
        self.literal = literal

    def get_type(self):
        return self.type

class Scanner:
    scanner = None

    class _Scanner:
        source = None
        start = 0
        current = 0

        simple_token_lookup = {'(': OPEN_PAREN, ')': CLOSE_PAREN, '{': OPEN_BRACE, '}': CLOSE_BRACE,
                               '+': ADD, '-': MINUS, '*': STAR, ';': SEMI_COLON, ',': COMMA, '/': DIV,
                               '"': STRING, "!": BANG, ">": GREATER_THAN, "<": LESS_THAN, "=": ASSIGN}
        keyword_lookup = {'or': KEYWORD_OR, 'and': KEYWORD_AND, 'class': KEYWORD_CLASS, 'if': KEYWORD_IF,
                          'else': KEYWORD_ELSE, 'true': KEYWORD_TRUE, 'false': KEYWORD_FALSE,
                          'while': KEYWORD_WHILE, 'for': KEYWORD_FOR, 'return': KEYWORD_RETURN,
                          'var': KEYWORD_VAR, 'fun': KEYWORD_FUN, 'print': KEYWORD_PRINT}
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
            self.source = SourceIterator(source)

        def raise_lexical_error(self, message):
            raise LexicalError(message)

        def set_source(self, source):
            self._init_members(source)

        def get_tokens(self):
            return self.tokens

        def add_token(self, token_type):
            self.tokens.append(Token(token_type, self.source.source_current_string()))

        def is_valid_numeric_symbol(self, symbol):
            return True if symbol is not None and (symbol.isnumeric() or symbol == '.') else False

        def read_numeric_symbol(self):
            floating_point = False
            while self.is_valid_numeric_symbol(self.source.peek()):
                c = self.source.advance()
                if c == '.' and floating_point:
                    self.raise_lexical_error("Lexical Error: Too many decimal points in numeric.")
                elif c == '.':
                    floating_point = True
            self.add_token(NUMBER)

        def is_valid_name_or_keyword_symbol(self, symbol):
            return False if symbol is None or (symbol != '_' and not symbol.isalnum()) else True

        def read_alpha_symbol(self):
            while self.is_valid_name_or_keyword_symbol(self.source.peek()):
                self.source.advance()

            symbol = self.source.source_current_string()
            token_id = IDENTIFIER if symbol not in self.keyword_lookup.keys() else self.keyword_lookup[symbol]
            self.add_token(token_id) # Token is an identifier

        def could_be_compound_symbol(self, token_id):
            return True if token_id in self.compound_symbols.keys() else False

        def scan_string(self):
            if self.source.seek('"') is None:
                self.raise_lexical_error("Lexical Error: Reached EOF without closing \" ")
            self.add_token(STRING)

        def scan_comment(self):
            # Comments are just ignored. Scan until the next new line
            self.source.seek("\n")

        def scan_simple_symbol(self, token_id):
            if self.could_be_compound_symbol(token_id):
                match = self.compound_symbols[token_id]
                if self.source.match(match[1]):
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
            while not self.source.peek() is None:
                c = self.source.advance()
                self.source.start_next_token()
                if c is None:
                    return
                if c.isalpha():
                    self.read_alpha_symbol()
                elif c.isnumeric():
                    self.read_numeric_symbol()
                else:
                    token_id = None if c not in self.simple_token_lookup.keys() else self.simple_token_lookup[c]
                    if token_id is None:
                        self.raise_lexical_error("Lexical Error: Unrecognized symbol %c." % c)
                    else:
                        self.scan_simple_symbol(token_id)

    def __init__(self, source):
        if not self.scanner:
            self.scanner = self._Scanner(source)
        else:
            self.scanner.set_source(source)

    def get_scanner(self):
        return self.scanner



