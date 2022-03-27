import sys
import plox_scanner
import plox_parser
import plox_interpreter
import plox_resolver
import plox_utilities as utilities


def run_program(program, console=False):
    scanner = plox_scanner.Scanner()
    parser = plox_parser.Parser()
    resolver = plox_resolver.Resolver()
    interpreter = plox_interpreter.Interpreter(console_mode=console)
    scanner.scan(program)
    if scanner.error_occurred():
        print("Unable to interpret program. Invalid symbols detected.")
        return
    parser.parse(scanner.get_scanned_tokens())
    if parser.error_occurred():
        print("Unable to interpret program. Syntax errors detected.")
        return
    resolver.resolve(interpreter, parser.get_parsed_statements())
    if resolver.error_occurred():
        print("Runtime errors have occurred. Aborting program execution.")
    interpreter.interpret(parser.get_parsed_statements())


def command_line():
    print("WELCOME TO THE PLOX CONSOLE")
    print(" ")
    src_in = ""
    scanner = plox_scanner.Scanner()
    parser = plox_parser.Parser()
    interpreter = plox_interpreter.Interpreter(console_mode=True)

    while True:
        try:
            src_in = input(">> ")
            scanner.scan(src_in)
            if src_in == "exit":
                break
            scanner.scan(src_in)
            parser.parse(scanner.get_scanned_tokens())
            interpreter.interpret(parser.get_parsed_statements())

        except plox_scanner.LexicalError as le:
            utilities.report_error(le)
        except plox_parser.PloxSyntaxError as se:
            utilities.report_error(se)


def interpret_source(source):
    pass


if __name__ == '__main__':
    if len(sys.argv) == 1:
        command_line()

    else:
        source = sys.argv[1]
        interpret_source(source)

