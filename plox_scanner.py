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
KEYWORD_NIL = 37
KEYWORD_BREAK = 38
DOT = 39
KEYWORD_THIS = 40

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
        end = self.get_index() if not self.list_end() else len(self._list)
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
        ret = True if self.peek() == char else False
        if ret:
            self.advance()
        return ret


class LexicalError(utilities.PloxError):
    def __init__(self, line, message):
        super().__init__(line, message)

    def get_error_message(self):
        return " Lexical Error: " + self.message


class Token:
    def __init__(self, token_type, literal, line):
        self.type = token_type
        self.literal = literal
        self.line = line

    def get_type(self):
        return self.type

    def get_value(self):
        return self.literal


@utilities.singleton
class Scanner:
    source = None
    start = 0
    current = 0

    simple_token_lookup = {'(': OPEN_PAREN, ')': CLOSE_PAREN, '{': OPEN_BRACE, '}': CLOSE_BRACE,
                           '+': ADD, '-': MINUS, '*': STAR, ';': SEMI_COLON, ',': COMMA, '/': DIV,
                           '"': STRING, "!": BANG, ">": GREATER_THAN, "<": LESS_THAN, "=": ASSIGN, ".": DOT}
    keyword_lookup = {'or': KEYWORD_OR, 'and': KEYWORD_AND, 'class': KEYWORD_CLASS, 'if': KEYWORD_IF,
                      'else': KEYWORD_ELSE, 'true': KEYWORD_TRUE, 'false': KEYWORD_FALSE,
                      'while': KEYWORD_WHILE, 'for': KEYWORD_FOR, 'return': KEYWORD_RETURN,
                      'var': KEYWORD_VAR, 'fun': KEYWORD_FUN, 'print': KEYWORD_PRINT, 'nil': KEYWORD_NIL,
                      'break': KEYWORD_BREAK, 'this': KEYWORD_THIS}
    compound_symbols = {DIV: [COMMENT, '/'], LESS_THAN: [LESS_THAN_EQUALS, '='],
                        GREATER_THAN: [GREATER_THAN_EQUALS, '='], ASSIGN: [EQUALS, '='],
                        BANG: [NOT_EQUALS, '=']}

    def __init__(self):
        self._init_members()

    def _init_members(self):
        self.line = 0
        self.start = 0
        self.current = 0
        self.tokens = []
        self.has_error = False

    def error_occurred(self):
        return self.has_error

    def raise_lexical_error(self, line, message):
        raise LexicalError(line, message)

    def scan(self, source):
        self.has_error = False
        try:
            if not isinstance(source, str):
                self.raise_lexical_error(0, "Plox expected text program")
            self._scan(source)
        except LexicalError as e:
            utilities.report_error(e)
            self.has_error = True

    def set_source(self, source):
        self._init_members(source)

    def get_scanned_tokens(self):
        return self.tokens

    def add_token(self, token_type):
        current_string = self.source.source_current_string()
        if token_type == KEYWORD_TRUE:
            literal = True
        elif token_type == KEYWORD_FALSE:
            literal = False
        else:
            literal = float(current_string) if token_type == NUMBER else current_string
        self.tokens.append(Token(token_type, literal, self.source.get_current_line()))

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

    def _scan(self, source):
        self._init_members()
        self.source = SourceIterator(source)
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
                    self.raise_lexical_error(self.source.get_current_line(),
                                             "Lexical Error: Unrecognized symbol %c." % c)
                else:
                    self.scan_simple_symbol(token_id)



