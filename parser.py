class Parser(object):
    def __init__(self, code, tokens):
        self.code = code
        self.tokens = tokens
        self.output = ''

    def covert_from_rpn(self):
        """
        This method converts Reverse Polish Notation (RPN) to Python code.

        The method uses a stack to process the RPN tokens and generates Python code.
        It handles various types of tokens such as identifiers, integers, floats, strings,
        boolean values, functions, variables, conditions, loops, and arrays.
        """
        stack = []
        arg_1 = 0
        arg_2 = 0
        block_amount = 0
        block = ' ' * 4
        num_funcs = 0
        R_p = 0
        index_iter = 0
        table_R_p = {}
        for token in self.code:
            type_ = self.iter_classes(token)
            total_blocks = block * block_amount
            # Handle identifiers, integers, floats, strings, boolean values
            if (type_ == 'IDENTIFIERS' or type_ == 'INTEGER' or type_ == 'FLOAT' or type_ == 'REALNUM' or
                    type_ == 'STRING' or type_ == 'AMOUNT' or type_ == 'BOOLEAN'):
                if token == 'console.log':
                    token = 'print'
                elif token == 'true':
                    token = 'True'
                elif token == 'false':
                    token = 'False'
                stack.append(token)

            # Handle function calls
            elif type_ == 'FUNC':
                num = int(stack.pop())
                var_func = []
                for i in range(num):
                    try:
                        var_func.append(stack.pop())
                    except IndexError:
                        continue
                name_func = var_func[-1]
                var_func.remove(name_func)
                var_func.reverse()
                func = f'{name_func}('
                if len(var_func) != 0:
                    for var in var_func:
                        if 'R_' in var:
                            found = True
                        else:
                            found = False
                        while found:
                            var = table_R_p[var]
                            if 'R_' in var:
                                pass
                            else:
                                found = False
                        func += var
                        if var_func[-1] != var:
                            func += ', '
                        else:
                            func += ')'
                else:
                    func += ')'
                tmp_list = self.code[index_iter:index_iter + 4]
                if tmp_list[-1] == 'НП':
                    stack.append(func)
                else:
                    self.output += f'{total_blocks}{func}\n'

            # Handle start of function definition
            elif type_ == 'START_FUNC':
                arg_1 = stack.pop()
                num_funcs = int(stack.pop()) - 1
                arg_2 = stack.pop()
                self.output += f'{block * block_amount}def {arg_2}:\n'
                block_amount += int(arg_1)

            # Handle end of function definition
            elif type_ == 'END_FUNC':
                while len(stack) != 0:
                    char = stack.pop()
                    if 'R_' in char:
                        self.output += f'{total_blocks}{table_R_p[char]}\n'
                self.output += f'\n\n'
                block_amount -= 1
                block_amount -= num_funcs
                if block_amount < 0:
                    block_amount = 0

            # Handle variable declaration
            elif type_ == 'VAR':
                tab = int(stack.pop())
                block_amount = tab
                stack.pop()
                iter = int(stack.pop())
                var = stack[-iter:]
                for i in var:
                    self.output += f'{total_blocks}{i} = 0\n'
                    try:
                        stack.remove(i)
                    except:
                        continue

            # Handle conditions
            elif type_ == 'CONDITIONS':
                arg_1 = stack.pop()
                if 'R_' in arg_1:
                    arg_1 = f'({table_R_p[arg_1]})'
                self.output += f'{total_blocks}if {arg_1}:\n'
                block_amount += 1

            # Handle goto statements
            elif type_ == 'GOTO':
                while len(stack) != 0:
                    arg_1 = stack.pop()
                    if 'R_' in arg_1:
                        arg_1 = f'({table_R_p[arg_1]})'
                    self.output += f'{total_blocks}{arg_1}\n'
                block_amount -= 1
                total_blocks = block * block_amount
                self.output += f'{total_blocks}else:\n'
                block_amount += 1

            # Handle end of conditions
            elif type_ == 'END_CONDITIONS':
                while len(stack) != 0:
                    arg_1 = stack.pop()
                    if 'R_' in arg_1:
                        arg_1 = f'({table_R_p[arg_1]})'
                    self.output += f'{total_blocks}{arg_1}\n'
                block_amount -= 1

            # Handle assignment operator
            elif token == '=':
                arg_1 = stack.pop()
                arg_2 = stack.pop()
                if 'R_' in arg_1:
                    arg_1 = f'({table_R_p[arg_1]})'
                if 'R_' in arg_2:
                    arg_2 = f'({table_R_p[arg_2]})'
                self.output += f'{block * block_amount}{arg_2} {token} {arg_1}\n'

            # Handle operators
            elif type_ == 'OPERATORS':
                if token == '&&':
                    token = 'and'
                if token == '||':
                    token = 'or'
                arg_1 = stack.pop()
                arg_2 = stack.pop()
                if 'R_' in arg_1:
                    arg_1 = f'({table_R_p[arg_1]})'
                if 'R_' in arg_2:
                    arg_2 = f'({table_R_p[arg_2]})'
                R_p += 1
                table_R_p[f'R_{R_p}'] = f'{arg_2} {token} {arg_1}'
                stack.append(f'R_{R_p}')

            # Handle arrays
            elif type_ == 'ARRAY':
                array = []
                num_elements = int(stack.pop())
                for i in range(num_elements):
                    array.append(stack.pop())
                array.reverse()
                name_array = array[0]
                array.remove(name_array)
                index = self.code.index(token)
                for j in array:
                    i = array.index(j)
                    j = int(j)
                    array[i] = j
                if self.code[index + 1] == '=':
                    stack.append(name_array)
                    stack.append(str(array))
                else:
                    stack.append(f'{name_array}{array}')

            index_iter += 1
        # Handle remaining tokens in the stack
        while len(stack) != 0:
            arg_1 = stack.pop()
            self.output += f'{arg_1}'


    def iter_classes(self, token_name):
        type_ = ''
        for token in self.tokens:
            if token.name == token_name:
                type_ = token.type_
                break
        if not type_:
            if token_name == 'Ф':
                type_ = 'FUNC'
            elif token_name == ':':
                type_ = 'MARK'
            elif token_name == 'НП':
                type_ = 'START_FUNC'
            elif token_name == 'КП':
                type_ = 'END_FUNC'
            elif token_name == 'КО':
                type_ = 'VAR'
            elif token_name == 'УПЛ':
                type_ = 'CONDITIONS'
            elif token_name == 'БП':
                type_ = 'GOTO'
            elif token_name == 'КУ':
                type_ = 'END_CONDITIONS'
            elif token_name == 'АЭМ':
                type_ = 'ARRAY'
            else:
                type_ = 'AMOUNT'
        return type_

