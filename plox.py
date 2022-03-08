import sys
import plox_scanner
import plox_parser
import plox_interpreter
import plox_utilities as utilities

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

