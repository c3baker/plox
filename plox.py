import sys
import plox_scanner
import plox_parser
import plox_utilities as utilities

def command_line():
    print("WELCOME TO THE PLOX CONSOLE")
    print(" ")
    src_in = ""
    while src_in != "exit":
        src_in = input(">> ")
        scanner = plox_scanner.Scanner(src_in)
        try:
            scanner.get_scanner().scan()
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

