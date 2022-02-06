import unittest
import plox_scanner as lex

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
                "    for(var i = 0, i < 10, "

    def setUp(self):
        self.scanner = lex.Scanner("")

    def tearDown(self):
        pass

    def count_tokens(self, scanner, token_type):
        tokens = scanner.get_scanner().get_tokens()
        count = [t for t in tokens if t.get_type() == token_type]
        return len(count)

    def test_basic_token_counts(self):
        self.scanner = lex.Scanner(self.program_1)
        self.scanner.get_scanner().scan()
        self.assertEqual(self.count_tokens(self.scanner, lex.OPEN_PAREN), 2)
        self.assertEqual(self.count_tokens(self.scanner, lex.CLOSE_PAREN), 2)
        self.assertEqual(self.count_tokens(self.scanner, lex.OPEN_BRACE), 2)
        self.assertEqual(self.count_tokens(self.scanner, lex.CLOSE_BRACE), 2)
        self.assertEqual(self.count_tokens(self.scanner, lex.KEYWORD_IF), 1)
        self.assertEqual(self.count_tokens(self.scanner, lex.KEYWORD_ELSE), 1)
        self.assertEqual(self.count_tokens(self.scanner, lex.NUMBER), 4)
        self.assertEqual(self.count_tokens(self.scanner, lex.KEYWORD_VAR), 6)
        self.assertEqual(self.count_tokens(self.scanner, lex.STRING), 1)
        self.assertEqual(self.count_tokens(self.scanner, lex.SEMI_COLON), 7)



