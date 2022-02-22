import unittest
import plox_scanner as lex
import plox_parser as par

class ScannerTests(unittest.TestCase):

    program_1 = "if(x == true) " \
                "{ " \
                "    var k = 100;" \
                "    var z = 432.0322;" \
                "    var big_value = 120302.33;" \
                "    var result_1 = k + z;" \
                "    var result_2 = big_value + 123;" \
                "    var result_3 = result_1 * result_3;" \
                "}" \
                "else" \
                "{" \
                "    print(\"This is an else\");"\
                "}" \
                "" \
                "func basic_function(var blah_blah_blah)" \
                "{" \
                "    print(\"Hello!\");" \
                "    var twee = 30220.0;" \
                "    return twee * blah_blah_blah;" \
                "}" \
                "" \
                "func use_basic_function()" \
                "{" \
                "    var xk = 3838;" \
                "    var r = basic_function(xk / 3);" \
                "    for(var i = 0; i < 10;  "

    program_2 = "(3 + 7) * (8 - 2);"
    printed_syntax_2 = "( * ( Group ( + ( 3.0 ) ( 7.0 ) ) ) ( Group ( - ( 8.0 ) ( 2.0 ) ) ) )"
    program_3 = "!(11 >= 17) + (77 / 8) - 144;"
    printed_syntax_3 = "( - ( + ( !( Group ( >= ( 11.0 ) ( 17.0 ) ) ) ) ( Group ( / ( 77.0 ) ( 8.0 ) ) ) ) ( 144.0 ) )  "

    def setUp(self):
        self.scanner = lex.Scanner("")
        self.parser = par.Parser(None)

    def tearDown(self):
        pass

    def count_tokens(self, scanner, token_type):
        tokens = scanner.get_scanner().get_tokens()
        count = [t for t in tokens if t.get_type() == token_type]
        return len(count)

    def test_basic_token_counts(self):
        self.scanner = lex.Scanner(self.program_1)
        self.scanner.get_scanner().scan()
        self.assertEqual(self.count_tokens(self.scanner, lex.OPEN_PAREN), 7)
        self.assertEqual(self.count_tokens(self.scanner, lex.CLOSE_PAREN), 6)
        self.assertEqual(self.count_tokens(self.scanner, lex.OPEN_BRACE), 4)
        self.assertEqual(self.count_tokens(self.scanner, lex.CLOSE_BRACE), 3)
        self.assertEqual(self.count_tokens(self.scanner, lex.KEYWORD_IF), 1)
        self.assertEqual(self.count_tokens(self.scanner, lex.KEYWORD_ELSE), 1)
        self.assertEqual(self.count_tokens(self.scanner, lex.NUMBER), 9)
        self.assertEqual(self.count_tokens(self.scanner, lex.KEYWORD_VAR), 11)
        self.assertEqual(self.count_tokens(self.scanner, lex.STRING), 2)
        self.assertEqual(self.count_tokens(self.scanner, lex.SEMI_COLON), 14)

    def test_parse_expressions(self):
        expressions = [self.program_2, self.program_3]
        expected_results = [self.printed_syntax_2, self.printed_syntax_3]
        printer = par.TreePrinter()

        for expression, result in zip(expressions, expected_results):
            self.scanner = lex.Scanner(expression)
            self.scanner.scan()
            self.parser = par.Parser(self.scanner.get_scanner().get_tokens())
            parsed_expression = self.parser.parse()
            for p in parsed_expression:
                printed_syntax = p.accept(printer)
                self.assertEqual(printed_syntax.strip(), result.strip(),
                                 "Syntax Tree output does not matched expected result.")
                








