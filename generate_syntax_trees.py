ast_types = ['Binary', 'Grouping', 'Literal', 'Unary']
ast_type_enum = {'Binary' : 0, 'Grouping' : 1, 'Literal' : 2, 'Unary' : 3}
ast_defines = {'Binary': ['left_expr', 'operator', 'right_expr'],
               'Grouping': ['expr'], 'Literal': ['value'], 'Unary': ['operator', 'right_expr']}

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
    write_line(output_file, 'self.type = ' + ast_type, 2)
    output_file.write('\n')
    output_file.write('\n')


def define_ast(output_dir, base_name):
    with open(output_dir + '\\' + base_name + '.py', 'w') as f:
        for ast_type in ast_types:
            f.write(ast_type + ' = ' + str(ast_type_enum[ast_type]) + '\n')
        f.write('\n\n')
        for ast_type in ast_types:
            write_ast_class(f, ast_type)


if __name__ == '__main__':
    define_ast('C:\\Users\\CharlesPC\\PycharmProjects\\plox', 'plox_syntax_trees')

