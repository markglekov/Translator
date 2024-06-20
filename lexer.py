import re


class Token(object):
    def __init__(self, type_, name):
        """_summary_

        Args:
            type_ (_type_): _description_
            name (_type_): _description_
        """
        self.type_ = type_
        self.name = name

    def __repr__(self):
        return f'{self.type_} {self.name}'


class Lexer(object):
    def __init__(self, token_types, precedence):
        """
        Initializes a new instance of the Lexer class.

        Parameters:
            token_types (dict): A dictionary mapping token types to their corresponding regular expressions.
            precedence (dict): A dictionary mapping operators to their precedence levels.

        Attributes:
            code (str): The input code to be tokenized.
            token_types (dict): A dictionary mapping token types to their corresponding regular expressions.
            precedence (dict): A dictionary mapping operators to their precedence levels.
            pos (int): The current position in the code string.
            tokens_table (list): A list to store the generated tokens.
        """
        self.code = ''
        self.token_types = token_types
        self.precedence = precedence
        self.pos = 0
        self.tokens_table = []

    def analysis(self):
        """
        Performs lexical analysis on the input code and generates a list of tokens.

        The analysis method iterates through the code string, matching each character against the defined token patterns.
        It identifies the type of token (e.g., identifier, operator, keyword) and creates a Token object for each token.
        The tokens are then stored in the 'tokens_table' attribute of the Lexer object.
        """
        found = True
        temp_name = ''
        temp_type = ''
        function_found = False
        while found:
            for type_, pattern in self.token_types.items():
                token = re.match(pattern, self.code)
                if token:
                    token_name = token.group()
                    if type_ == 'SPACES':
                        self.move_to_pos(1)
                    elif (token_name == '&' or token_name == '|' or token_name == '>' or token_name == '<' or
                          token_name == '=' or token_name == '+' or token_name == '!' or token_name == '*'):
                        self.move_to_pos(len(token_name))
                        if temp_type and temp_name:
                            self.tokens_table.append(Token(temp_type, temp_name))
                            temp_name = ''
                            temp_type = ''
                        if re.match(pattern, self.code):
                            token_name += re.match(pattern, self.code).group()
                            self.tokens_table.append(Token(type_, token_name))
                        else:
                            self.tokens_table.append(Token(type_, token_name))
                        self.move_to_pos(len(token_name))
                    elif type_ == 'IDENTIFIERS':
                        if function_found:
                            temp_name += token_name
                            self.tokens_table.append(Token(temp_type, temp_name))
                            temp_name = ''
                            temp_type = ''
                            function_found = False
                        else:
                            temp_name = token_name
                            temp_type = type_
                        self.move_to_pos(len(token_name))
                    elif token_name == '.':
                        if temp_name and temp_type:
                            temp_name += token_name
                            function_found = True
                            self.move_to_pos(len(token_name))
                        else:
                            self.tokens_table.append(Token(type_, token_name))
                            self.move_to_pos(len(token_name))
                    else:
                        if temp_type and temp_name:
                            self.tokens_table.append(Token(temp_type, temp_name))
                            temp_name = ''
                            temp_type = ''
                        self.tokens_table.append(Token(type_, token_name))
                        self.move_to_pos(len(token_name))
            if len(self.code) == 0:
                found = False

    def tokenize(self, file):
        """
        Tokenizes the input code file and stores the tokens in the 'code' attribute.

        Args:
            file (str): The path to the input code file.
        """
        with open(file, 'r') as code:
            output = ''
            for line in code:
                output += line
            self.code = output.strip()


    def move_to_pos(self, len_pos):
        """
        Moves the position of the lexer to the specified length in the code.

        This method is used to update the lexer's position in the code string.
        It also updates the remaining code string by removing the processed part.

        Args:
            len_pos (int): The length to move the position in the code.
        """
        self.pos = len_pos
        self.code = self.code[self.pos:]

    def convert_to_rpn(self):
        """
        Converts the tokens table to Reverse Polish Notation (RPN).

        This method uses the Shunting Yard algorithm to convert the tokens table,
        which is a list of Token objects, into Reverse Polish Notation (RPN).
        The RPN is a mathematical notation in which operators follow their operands.

        Returns:
            list: A list of strings representing the tokens in RPN.
        """

        # Perform lexical analysis to tokenize the code.
        self.analysis()

        # Initialize empty stack and output list.
        stack = []
        output = []

        # Initialize counters for 'let', 'function', 'if', 'else', 'continue', 'break'.
        i = 0
        let_num = 0
        func_num = 0
        func_lvl = 0

        # Iterate through each token in the tokens table.
        for token in self.tokens_table:
            found = False

            # Handle identifiers, integers, floats, real numbers, strings, and booleans.
            if (token.type_ == 'IDENTIFIERS' or token.type_ == 'INTEGER' or token.type_ == 'FLOAT' or
                    token.type_ == 'REALNUM' or token.type_ == 'STRING' or token.type_ == 'BOOLEAN'):
                output.append(f'{token.name}')

                # If the previous token was 'break' or 'continue', pop it from the stack and append 'БП'.
                if len(stack) != 0:
                    if stack[-1] == 'break' or stack[-1] == 'continue':
                        stack.pop()
                        output.append('БП')
                    else:
                        continue

            # Handle operators.
            elif token.type_ == 'OPERATORS':
                # While the stack is not empty and the top of the stack has higher precedence, pop it and append to output
                while not found:
                    if len(stack) == 0 or self.precedence[stack[-1]] < self.precedence[token.name]:
                        found = True
                    else:
                        char = stack.pop()
                        output.append(f'{char}')

                # Push the current operator onto the stack.
                stack.append(token.name)

            # Handle delimiters
            elif token.type_ == 'DELIMITERS':
                # Handle parentheses
                if token.name == '(':
                    # If the previous token was an identifier, push 'Ф' onto the stack
                    if (self.tokens_table[self.tokens_table.index(token) - 1].type_ == 'IDENTIFIERS' and
                            self.tokens_table.index(token) != 0):
                        function_operand_counter = 1
                        stack.append('Ф')
                    else:
                        stack.append(token.name)
                # Handle other delimiters
                elif token.name == ':':
                    output.append(f'{token.name}')
                elif token.name == ')':
                    # Pop operators from the stack and append to output until a '(' is encountered
                    while not found:
                        char = stack.pop()
                        if char == '(':
                            found = True
                        elif char == 'Ф':
                            function_operand_counter += 1
                            output.append(f'{function_operand_counter}')
                            output.append(f'{char}')
                            found = True
                        else:
                            output.append(f'{char}')
                elif token.name == '[':
                    address_array_element = 2
                    stack.append('АЭМ')
                elif token.name == ',':
                    # Handle function operands and array elements.
                    if 'АЭМ' in stack:
                        while stack[-1] != 'АЭМ':
                            char = stack.pop()
                            output.append(f'{char}')
                        address_array_element += 1
                    elif 'Ф' in stack:
                        while stack[-1] != 'Ф':
                            char = stack.pop()
                            output.append(f'{char}')
                        function_operand_counter += 1
                    elif stack[-1] == 'let':
                        let_num += 1
                elif token.name == ']':
                    stack.remove('АЭМ')
                    char = f'{address_array_element} АЭМ '
                    output.append(f'{char}')
                elif token.name == '{':
                    # Handle function definitions.
                    if stack[-1] == 'function':
                        output.append(f'{func_num}')
                        output.append(f'{func_lvl}')
                        output.append(f'НП')
                        stack.pop()
                    # Handle 'if' statements.
                    if 'if' in stack:
                        i += 1
                        while stack[-1] != 'if':
                            output.append(f'{stack.pop() }')
                        index = self.tokens_table.index(token)
                        if self.tokens_table[index - 1].name == ')':
                            output.append(f'УПЛ')
                elif token.name == '}':
                    # Handle 'if' and 'else' statements.
                    if 'if' in stack:
                        index = self.tokens_table.index(token)
                        try:
                            if self.tokens_table[index + 1].name != 'else':
                                while not found:
                                    char = stack.pop()
                                    if char == 'if':
                                        found = True
                                    else:
                                        output.append(f'{char}')
                                output.append(f'КУ')
                        except IndexError as e:
                            while not found:
                                char = stack.pop()
                                if char == 'if':
                                    found = True
                                else:
                                    output.append(f'{char}')
                    # Handle function definitions
                    elif f'{func_num}' in output and f'{func_lvl}' in output and f'НП' in output:
                        output.append('КП')
                        func_lvl -= 1
                else:
                    # Handle 'let' statements.
                    if len(stack) != 0:
                        if stack[-1] == 'let':
                            stack.pop()
                            output.append(f'{let_num}')
                            output.append(f'{func_num}')
                            output.append(f'{func_lvl}')
                            output.append(f'КО')
                            let_num = 0
                    # While the stack is not empty and the top of the stack has higher precedence, pop it and append to output.
                    while not found:
                        if len(stack) == 0 or self.precedence[stack[-1]] < self.precedence[token.name]:
                            found = True
                        else:
                            char = stack.pop()
                            output.append(f'{char} ')
                    # If the token is not a semicolon, push it onto the stack.
                    if token.name != ';':
                        stack.append(token.name)

            # Handle keywords.
            elif token.type_ == 'KEYWORDS':
                if token.name == 'if':
                    stack.append(token.name)
                elif token.name == 'else':
                    while stack[-1] != 'if':
                        output.append(f'{stack.pop()}')
                    output.append(f'БП')
                elif token.name == 'continue' or token.name == 'break':
                    stack.append(token.name)
                elif token.name == 'let':
                    stack.append(token.name)
                    let_num += 1
                elif token.name == 'function':
                    func_num += 1
                    func_lvl += 1
                    stack.append(token.name)
        # Pop any remaining operators from the stack and append to output.
        while len(stack) != 0:
            char = stack.pop()
            if char == 'let':
                continue
            output.append(f'{char}')

        # Return the tokens in RPN
        return output
