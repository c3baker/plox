import sys
import plox_scanner
import plox_parser

def error(line, message):
    report_error(line, "", message)


def report_error(line, where, message):
    print("[ Line %d ] Error %s : %s" % (line, where, message))


def command_line():

    print("WELCOME TO THE PLOX CONSOLE")
    print(" ")
    src_in = input(">> ")
    while src_in != "exit":
        src_in = input(">> ")
        scanner = plox_scanner.Scanner(src_in)
        try:
            scanner.get_scanner().scan()
        except plox_scanner.LexicalError as le:
            report_error(scanner.get_scanner().get_current_line(), "", le.get_error_message())
        except plox_parser.PloxSyntaxError as se:
            report_error(se.line, se.get_error_message())


def interpret_source(source):
    pass


if __name__ == '__main__':
    if len(sys.argv) == 1:
        command_line()

    else:
        source = sys.argv[1]
        interpret_source(source)

