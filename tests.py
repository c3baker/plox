import unittest
import plox_scanner as lex
import plox_parser as par
import plox_interpreter as itr
from plox import *


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


class TestPrograms(unittest.TestCase):
    prog_1 = "print (3 * 4) + (17 - 3);"
    prog_2 = "print 3*2 + (11 - 10) - 7;"
    prog_3 = "var x = 4;" \
             "var y = 7;" \
             "print x * y ;"

    def setUp(self):
        self.scanner = lex.Scanner()
        self.parser = par.Parser()
        self.intr = itr.Interpreter()

    def tearDown(self):
        pass


    def test_program_1(self):
        self.scanner.scan(self.prog_1)
        self.parser.parse(self.scanner.get_scanned_tokens())
        self.intr.interpret(self.parser.get_parsed_statements())

    def test_program_2(self):
        self.scanner.scan(self.prog_2)
        self.parser.parse(self.scanner.get_scanned_tokens())
        self.intr.interpret(self.parser.get_parsed_statements())

    def test_program_3(self):
        self.scanner.scan(self.prog_3)
        self.parser.parse(self.scanner.get_scanned_tokens())
        self.intr.interpret(self.parser.get_parsed_statements())

    def test_should_not_work(self):
        program = "var if = 0;" # Should be a Plox error using a keyword as a variable name
        run_program(program)

    def test_should_not_work_2(self):
        program = "var __init__ = 0;" # Should be a Plox error using a keyword as a variable name
        run_program(program)

    def test_code_blocks_and_variables(self):
        program = "var x = 33;" \
                  "var y = \"XY\"; " \
                  "print x;" \
                  "{" \
                  "    var x = 11;" \
                  "    print x;" \
                  "    print y;" \
                  "    {" \
                  "        var x = \"ABCDFDX\"; " \
                  "        print x;" \
                  "        print y;" \
                  "    }" \
                  "    print x;" \
                  "}" \
                  "print x;" \
                  "print y;"
        run_program(program)

    def test_if_statment_true(self):
        program = "if(true)" \
                  "{" \
                  "    print 10;" \
                  "}" \
                  "else" \
                  "{" \
                  "    print 20;" \
                  "}"
        run_program(program)

    def test_if_statment_false(self):
        program = "if(false)" \
                  "{" \
                  "    print 10;" \
                  "}" \
                  "else" \
                  "{" \
                  "    print 20;" \
                  "}"
        run_program(program)

    def test_if_statments_nested(self):
        program = "if(true)" \
                  "{" \
                  "    print 10;" \
                  "    if(true)" \
                  "    {" \
                  "        print 20;" \
                  "        if(false)" \
                  "        {" \
                  "             print 30;" \
                  "        }" \
                  "        else" \
                  "        {" \
                  "            print 40;" \
                  "        }" \
                  "    }" \
                  "    " \
                  "}"
        run_program(program)

    def test_while_statment(self):
        program = "var i = 10;" \
                  "while(i)" \
                  "{" \
                  "    print i;" \
                  "    i = i - 1;" \
                  "}"
        run_program(program)

    def test_or(self):
        program = "if (10 > 7 or 4 == 3)" \
                  "{" \
                  "    print \"OR is True\";" \
                  "}" \
                  "else" \
                  "{" \
                  "   print \"OR is False\";" \
                  "}"
        run_program(program)

    def test_and(self):
        program = "if (10 > 7 and 4 == 3)" \
                  "{" \
                  "    print \"AND is True\";" \
                  "}" \
                  "else" \
                  "{" \
                  "   print \"AND is False\";" \
                  "}"
        run_program(program)

    def test_function_declaration(self):
        program = "fun hello_world()" \
                  "{" \
                  "    print \"Hello World!\";" \
                  "}" \
                  "" \
                  "hello_world();"
        run_program(program)

    def test_functions_and_variables(self):
        program = "var j = 0;" \
                  "fun jot()" \
                  "{" \
                  "    var j = 1;" \
                  "    print j;" \
                  "    j = j + 1;" \
                  "    print j;" \
                  "}" \
                  "" \
                  "jot();" \
                  "print j;"

        run_program(program)

    def test_multi_depth_call(self):
        program = "fun f()" \
                  "{" \
                  "    fun g()" \
                  "    {" \
                  "        fun h()" \
                  "        {" \
                  "            fun q()" \
                  "            {" \
                  "                print \"Q!\";" \
                  "                return 1.0;" \
                  "            }" \
                  "            return q;" \
                  "        }" \
                  "        return h;" \
                  "     }" \
                  "     return g;" \
                  "}" \
                  "" \
                  "var x = f()()();" \
                  "var y = x();" \
                  "print y;" \

        run_program(program)
    def test_fibonacci(self):
        program = "fun fib(n)" \
                  "{" \
                  "   if (n < 0)" \
                  "   {" \
                  "       return 0;" \
                  "   }" \
                  "   if (n <= 1)" \
                  "   {" \
                  "       return n;" \
                  "   }" \
                  "   return fib(n - 1) + fib(n - 2);" \
                  "}" \
                  "" \
                  "fun fib_seq(n)" \
                  "{" \
                  "   var i = 0;" \
                  "   while (i < n)" \
                  "   {" \
                  "       print fib(i);" \
                  "       i = i + 1;" \
                  "   }" \
                  "}" \
                  "" \
                  "fib_seq(15);"
        run_program(program)

    def test_function_closures(self):
        program = "var j = 0;" \
                  "fun jot()" \
                  "{" \
                  "    fun inner(x, y)" \
                  "    {" \
                  "        print x;" \
                  "        print y;" \
                  "        if (x < 0)" \
                  "        {" \
                  "            return;" \
                  "        }" \
                  "        inner(x - 1 ,y - 1);" \
                  "    }" \
                  "    {" \
                  "       inner(10, 11);" \
                  "    }" \
                  "}" \
                  "" \
                  "{" \
                  "   {" \
                  "     {" \
                  "       {" \
                  "            jot();" \
                  "       }" \
                  "     }" \
                  "   }" \
                  "}"

        run_program(program)

    def test_function_closures_2(self):
        program = "fun f(x)" \
                  "{" \
                  "    fun g(y)" \
                  "    {" \
                  "        return x*y;" \
                  "    }" \
                  "    print \"here\";" \
                  "    return g;" \
                  "}" \
                  "" \
                  "var h = f(10);" \
                  "var z = h(3);" \
                  "print z;"

        run_program(program)

    def test_break(self):
        program = "var i = 0;" \
                  "while(true)" \
                  "{" \
                  "    i = i + 1;" \
                  "    print i;" \
                  "    if(i > 5)" \
                  "    {" \
                  "        break;" \
                  "    }" \
                  "}" \
                  "" \
                  "print \"Done\";"

        run_program(program)

    def test_scoping(self):
        program = "var x = \"global\";" \
                  "{" \
                  "    fun f()" \
                  "    {" \
                  "        print x;" \
                  "    }" \
                  "    f();" \
                  "    var x = \"local\";" \
                  "    f();" \
                  "    fun g()" \
                  "    {" \
                  "        print x;" \
                  "    }" \
                  "    g();" \
                  "}"

        run_program(program)

    def test_declare_class_and_create_object(self):
        program = "class simple{}" \
                  "var object = simple();"
        run_program(program)

    def test_class_methods_basic(self):
        program = "class Bakery" \
                  "{" \
                  "    fun bake()" \
                  "    {" \
                  "        print \"Bread\"; " \
                  "    }" \
                  "}" \
                  "" \
                  "var b = Bakery();" \
                  "b.bake();" \
                  "print \"Done\";"
        run_program(program)

    def test_basic_this(self):
        program = "class Bakery" \
                  "{" \
                  "    fun bake()" \
                  "    {" \
                  "        print this.bread_style;" \
                  "    }" \
                  "}" \
                  "" \
                  "var b = Bakery();" \
                  "b.bread_style = \"Rye\";" \
                  "b.bake();"

        run_program(program)

    def test_constructor(self):
        program = "class Bakery" \
                  "{" \
                  "    fun __init__(bread_style)" \
                  "    {" \
                  "       this.bread_style = bread_style" \
                  "    }" \
                  "    fun bake()" \
                  "    {" \
                  "        print this.bread_style;" \
                  "    }" \
                  "}" \
                  "print \"First Bakery\";" \
                  "var br = Bakery(\"Rye\");" \
                  "br.bake();" \
                  "print \"Next Bakery\";" \
                  "var bf = Bakery(\"French Bread\");" \
                  "bf.bake();"

        run_program(program)

    def test_invalid_constructor_access(self):
        program = "class Bakery" \
                  "{" \
                  "    fun __init__(bread_style)" \
                  "    {" \
                  "       this.bread_style = bread_style" \
                  "    }" \
                  "    fun bake()" \
                  "    {" \
                  "        return this.__init__;" \
                  "    }" \
                  "}" \
                  "var br = Bakery(\"Pastry\");" \
                  "var init = br.bake();"

        run_program(program)

    def test_inheritance(self):
        program = "class Store" \
                  "{" \
                  "    fun __init__()" \
                  "    {" \
                  "         print \"Init Store\";" \
                  "    }" \
                  "    " \
                  "    fun buy(cost)" \
                  "    {" \
                  "        print \"You pay: $\" + cost ;" \
                  "    }" \
                  "}" \
                  "" \
                  "class Bakery > Store" \
                  "{" \
                  "     fun __init__(bread_type, bread_price)" \
                  "     {" \
                  "          this.bread_type = bread_type;" \
                  "          this.bread_price = bread_price;" \
                  "     }" \
                  "     fun bake()" \
                  "     {" \
                  "          print \"Baking \" + this.bread_type;" \
                  "     }" \
                  "     " \
                  "     fun buy_bread()" \
                  "     {" \
                  "         this.bake();" \
                  "         super.buy(this.bread_price);" \
                  "     }" \
                  "}" \
                  "" \
                  "var bkry = Bakery(\"French Bread\", 2.25);" \
                  "bkry.bake();" \
                  "bkry.buy(1.30);" \
                  "bkry.buy_bread();"

        run_program(program)














