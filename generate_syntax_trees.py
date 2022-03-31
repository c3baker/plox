import os
import sys

ast_defines = {'Binary': ['left_expr', 'operator', 'right_expr'],
               'Grouping': ['expr'], 'Literal': ['literal'], 'Unary': ['operator', 'expr'],
               'ExprStmt': ['expr'], 'PrintStmt': ['expr'], 'Dclr': ['var_name', 'assign_expr', 'line'],
               'Idnt': ['identifier'], 'Assign': ['var_name', 'right_side', 'line'], 'Block': ['stmts'],
               'IfStmt': ['expr', 'if_block', 'else_block'], 'WhileStmt':['expr', 'while_block'],
               'Call': ['callee', 'arguments', 'line'], 'FuncDclr': ['handle', 'parameters', 'body', 'line'],
               'ReturnStmt': ['ret_val', 'line'], 'BrkStmt': ['line'], 'ClassDclr': ['class_name', 'methods', 'line'],
               'Get': ["object", "field_name", "line"], 'Set': ['object', 'field_name', 'right_side', 'line'],
               'ThisStmt': ["token"], 'Construct': ["line"]}

def write_line(file_name, line, indentation=0):
    for i in range(indentation):
        file_name.write('    ')
    file_name.write(line)
    file_name.write('\n')


def write_ast_class(output_file, ast_type):
    members = ast_defines[ast_type]
    arguments = ''
    for m in members:
        arguments += m + ', '
    arguments = arguments[:-2]
    write_line(output_file, 'class ' + ast_type + ':')
    write_line(output_file, 'def __init__(self, ' + arguments + '):', 1)
    for member in members:
        write_line(output_file, 'self.'+member+' = ' + member, 2)
    write_line(output_file, 'self.type = ' + 'Type_' + ast_type, 2)
    output_file.write('\n')
    write_line(output_file, 'def accept(self, visitor): ', 1)
    write_line(output_file, 'val = visitor.visit_' + str(ast_type) + '(self)', 2)
    write_line(output_file, 'return val', 2)
    output_file.write('\n')
    output_file.write('\n')


def define_ast(output_dir, base_name):
    output_file = os.path.join(output_dir, base_name)
    with open(output_file, 'w') as f:
        i = 0
        for ast_type in ast_defines.keys():
            f.write('Type_' + ast_type + ' = ' + str(i) + '\n')
            i += 1
        f.write('\n\n')
        for ast_type in ast_defines.keys():
            write_ast_class(f, ast_type)


if __name__ == '__main__':
    workspace_dir = os.path.dirname(__file__)
    define_ast(workspace_dir, 'plox_syntax_trees.py')

