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

    def visit_Dclr(self, dclr):
        idnt = dclr.identifier.accept(self)
        if dclr.expr is not None:
            expr = dclr.expr.accept(self)
            return "( VAR = " + idnt + ' ' + expr + ' )'
        return "( VAR " + idnt + ' )'

    def visit_Idnt(self, idnt):
        return idnt.name


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

    def match_previous(self, match_list):
        token = self.previous()
        if token is None:
            return False
        if token.type in match_list:
            return True
        return False


class PloxSyntaxError(utilities.PloxError):
    def __init__(self, message, line):
        super().__init__(line, message)

    def get_error_message(self):
        return " Syntax Error: " + self.message


@utilities.singleton
class Parser:
    parser = None

    def __init__(self):
        self.has_error = False
        self.tokens = None
        self.statements = []

    def parse(self, scanned_tokens=[]):
        self.has_error = False
        if not isinstance(scanned_tokens, list):
            raise Exception("Parser expected tokens to be in a list!")
        try:
            self._parse(scanned_tokens)
        except PloxSyntaxError as e:
            utilities.report_error(e)
            self.has_error = True

    def error_occurred(self):
        return self.has_error

    def get_parsed_statements(self):
        return self.statements

    def _parse(self, scanned_tokens):
        self.statements = []
        self.tokens = TokenIterator(scanned_tokens)
        while self.tokens.list_end() is False:
            dclr = self.declaration()
            if dclr is not None:
                self.statements.append(dclr)
        return self.statements

    def declaration(self):
        if self.tokens.match([ps.KEYWORD_VAR]):
            return self.var_declaration_statement()
        if self.tokens.match([ps.KEYWORD_FUN]):
            return self.func_declaration_statement()
        if self.tokens.match([ps.OPEN_BRACE]):
            return self.block()
        if self.tokens.match([ps.KEYWORD_CLASS]):
            return self.class_declaration_statement()
        return self.statement()


    def var_declaration_statement(self):
        expr = self.expression()
        if isinstance(expr, syntax_trees.Idnt):
            var_name = expr.identifier.get_value()
            expr = None
        elif isinstance(expr, syntax_trees.Assign):
            var_name = expr.var_name
        else:
            raise PloxSyntaxError("Expected identifier in variable declaration.", self.tokens.previous().line)
        if not self.tokens.match([ps.SEMI_COLON]):
            raise PloxSyntaxError("Expected ; after statement.", self.tokens.previous().line)
        return syntax_trees.Dclr(var_name, expr, self.tokens.previous().line)

    def func_declaration_statement(self):
        handle = self.primary()  # Expect function name
        parameters = []
        if not isinstance(handle, syntax_trees.Idnt) and not isinstance(handle, syntax_trees.Construct):
            raise PloxSyntaxError("Expected function declaration.", self.tokens.previous().line)
        if not self.tokens.match([ps.OPEN_PAREN]):
            raise PloxSyntaxError("Function declaration expected parameter list.", self.tokens.previous().line)
        while not self.tokens.match([ps.CLOSE_PAREN]):
            if self.tokens.peek() is None:
                raise PloxSyntaxError("Reached EOF without finding closing \")\".", self.tokens.previous().line)
            if len(parameters) > 0 and not self.tokens.match([ps.COMMA]):
                raise PloxSyntaxError("Expected , separator in parameter list")
            param = self.expression()
            if not isinstance(param, syntax_trees.Idnt):
                raise PloxSyntaxError("Invalid parameter declaration.", self.tokens.previous().line)
            parameters.append(param.identifier.get_value())
        body = self.declaration()
        if not isinstance(body, syntax_trees.Block):
            raise PloxSyntaxError("Expected function body definition.", self.tokens.previous().line)
        func_name = handle.identifier.get_value() if isinstance(handle, syntax_trees.Idnt) else "__init__"
        return syntax_trees.FuncDclr(func_name, parameters, body, self.tokens.previous().line)

    def class_declaration_statement(self):
        class_name = self.expression()
        declaration_line = self.tokens.previous().line
        if not isinstance(class_name, syntax_trees.Idnt):
            raise PloxSyntaxError("Expected class declaration.", self.tokens.previous().line)
        if not self.tokens.match([ps.OPEN_BRACE]):
            raise PloxSyntaxError("Expected \"{\" in class declaration.", self.tokens.previous().line)

        methods = []
        while not self.tokens.match([ps.CLOSE_BRACE]):
            if self.tokens.list_end():
                raise PloxSyntaxError("Reached EOF without finding closing \"}\".", self.tokens.previous().line)
            method = self.declaration()
            if not isinstance(method, syntax_trees.FuncDclr):
                raise PloxSyntaxError("Expected class method declaration.", self.tokens.previous().line)
            methods.append(method)

        return syntax_trees.ClassDclr(class_name.identifier.get_value(), methods, declaration_line)

    def statement(self):
        if self.tokens.match([ps.KEYWORD_PRINT]):
            return self.statement_print()
        elif self.tokens.match([ps.KEYWORD_IF]):
            return self.statement_if()
        elif self.tokens.match([ps.KEYWORD_WHILE]):
            return self.statement_while()
        elif self.tokens.match([ps.KEYWORD_RETURN]):
            return self.return_statement()
        elif self.tokens.match([ps.KEYWORD_BREAK]):
            return self.statement_break()
        else:
            return self.statement_expression()

    def return_statement(self):
        if self.tokens.match([ps.SEMI_COLON]) is True:
            return syntax_trees.ReturnStmt(None, self.tokens.previous().line)
        ret_val = self.expression()
        if isinstance(ret_val, syntax_trees.Construct):
            raise PloxSyntaxError("Cannot return a constructor", self.tokens.previous().line)
        if self.tokens.match([ps.SEMI_COLON]) is False:
            raise PloxSyntaxError("Expected ; after statement.", self.tokens.previous().line)
        return syntax_trees.ReturnStmt(ret_val, self.tokens.previous().line)

    def statement_while(self):
        expr = self.expression()
        if not isinstance(expr, syntax_trees.Grouping):
            raise PloxSyntaxError("Expected valid expression after \"while\" statement")
        execution_block = self.declaration()
        if not isinstance(execution_block, syntax_trees.Block):
            raise PloxSyntaxError("Expected valid execution block \"{...}\" for while statement")
        return syntax_trees.WhileStmt(expr, execution_block)

    def statement_if(self):
        expr = self.expression()
        else_branch = None
        if not isinstance(expr, syntax_trees.Grouping):
            # should be structured as if ( expr )
            raise PloxSyntaxError("Expected valid expression after \"if\" statement")
        if_branch = self.declaration()
        if not isinstance(if_branch, syntax_trees.Block):
            raise PloxSyntaxError("Missing valid execution block \"{...}\" for if-statement true branch")
        if self.tokens.match([ps.KEYWORD_ELSE]):
            else_branch = self.declaration()
            if not isinstance(else_branch, syntax_trees.Block):
                raise PloxSyntaxError("Missing valid execution block \"{...}\" for else branch")

        return syntax_trees.IfStmt(expr, if_branch, else_branch)

    def statement_print(self):
        expr = self.expression()
        if self.tokens.match([ps.SEMI_COLON]) is False:
            raise PloxSyntaxError("Expected ; after statement.", self.tokens.previous().line)
        return syntax_trees.PrintStmt(expr)

    def statement_break(self):
        if self.tokens.match([ps.SEMI_COLON]) is False:
            raise PloxSyntaxError("Expected ; after break statement.", self.tokens.previous().line)
        return syntax_trees.BrkStmt(self.tokens.previous().line)

    def statement_expression(self):
        expr = self.expression()
        # To allow for pure expressions to still be evaluated on the console
        # We will only enforce the ; on end of statement rule if the expression is an assignment or call
        if self.tokens.match([ps.SEMI_COLON]) is False and (isinstance(expr, syntax_trees.Assign) or
                isinstance(expr, syntax_trees.Call)):
            raise PloxSyntaxError("Expected ; after statement.", self.tokens.previous().line)
        return syntax_trees.ExprStmt(expr)

    def block(self):
        block_statements = []
        while self.tokens.peek().type != ps.CLOSE_BRACE and self.tokens.peek() is not None:
            block_statements.append(self.declaration())
        if not self.tokens.match([ps.CLOSE_BRACE]):
            raise PloxSyntaxError("Missing }.", self.tokens.previous().line)
        return syntax_trees.Block(block_statements)

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.equality()
        if self.tokens.match([ps.ASSIGN]):
            assignment = self.equality()
            if isinstance(expr, syntax_trees.Idnt):  # Normal assignment
                return syntax_trees.Assign(expr.identifier.get_value(), assignment, self.tokens.previous().line)
            if isinstance(expr, syntax_trees.Get):  # Class setter
                return syntax_trees.Set(expr.object, expr.field_name, assignment, self.tokens.previous().line)
            if isinstance(expr, syntax_trees.Construct):
                raise PloxSyntaxError("Reassignment of class constructor not allowed.", self.tokens.previous().line)
            raise PloxSyntaxError("Assignment target wrong type.", self.tokens.previous().line)
        return expr

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
            return self.call()

    def call(self):
        callee = self.primary()
        '''
        Since x() is a valid call with callee x but so is
        x()() with callee x() which itself is a call
        or x()()() with callee x()() which itself is a call with callee
        x() which itself is a call with callee x... and so on
        the call must be parsed somewhat recursively
        Alternatively a call could be accessing a class method
        object.something.something_else.another_thing.function(); or
        object.get_another_object().run_function_1().this_thing.another_thing.get_value();
        '''
        while self.tokens.match([ps.OPEN_PAREN, ps.DOT]):
            if self.tokens.match_previous([ps.DOT]):
                identifier = self.primary()
                if isinstance(identifier, syntax_trees.Construct):
                    raise PloxSyntaxError("Explicit invocation of a constructor is not allowed.",
                                          self.tokens.previous().line)
                if not isinstance(identifier, syntax_trees.Idnt):
                    raise PloxSyntaxError("Expected method or property.", self.tokens.previous().line)
                callee = syntax_trees.Get(callee, identifier.identifier.get_value(), self.tokens.previous().line)
            else:
                if isinstance(callee, syntax_trees.Construct):
                    raise PloxSyntaxError("Explicit invocation of a constructor is not allowed.", self.identifier.line)
                callee = self.parse_function_call(callee)
        return callee

    def parse_function_call(self, callee):
        arguments = []
        while not self.tokens.match([ps.CLOSE_PAREN]):
            if len(arguments) > 0 and not self.tokens.match([ps.COMMA]):
                raise PloxSyntaxError("Expected , separator in argument list", self.tokens.previous().line)
            if self.tokens.peek is None:
                raise PloxSyntaxError("Expected matching \")\" for function call.", self.tokens.previous().line)
            arguments.append(self.expression())
        return syntax_trees.Call(callee, arguments, self.tokens.previous().line)

    def primary(self):
        if self.tokens.match([ps.NUMBER, ps.STRING, ps.KEYWORD_NIL, ps.KEYWORD_TRUE, ps.KEYWORD_FALSE]):
                return syntax_trees.Literal(self.tokens.previous())
        elif self.tokens.match([ps.IDENTIFIER]):
            return syntax_trees.Idnt(self.tokens.previous())
        elif self.tokens.match([ps.OPEN_PAREN]):
            syntax_tree = syntax_trees.Grouping(self.expression())
            if self.tokens.match([ps.CLOSE_PAREN]):
                    return syntax_tree
            else:
                raise PloxSyntaxError("Missing \")\".", self.tokens.peek().line)
        elif self.tokens.match([ps.KEYWORD_THIS]):
            return syntax_trees.ThisStmt(self.tokens.previous())
        elif self.tokens.match([ps.KEYWORD_CONSTRUCTOR]):
            return syntax_trees.Construct(self.tokens.previous().line)

        raise PloxSyntaxError("Invalid PLOX expression.", self.tokens.peek().line)




