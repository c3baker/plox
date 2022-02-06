import sys
import plox_scanner

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
        scanner.scanner.scan()


def interpret_source(source):
    pass


if __name__ == '__main__':
    if len(sys.argv) == 1:
        command_line()

    else:
        source = sys.argv[1]
        interpret_source(source)

