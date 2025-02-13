import re

class Lexer:
    def __init__(self):
        self.token_patterns = {
            'KEYWORD': r'\b(if|elif|else|while|for|fin|break|continue|pass)\b',
            'DATATYPE': r'\b(int|str|arr)\b',
            'ARRAY': r'\[([^\[\]]+|"(?:\\.|[^"\\])*")*\]',
            'PRINT_FUNCTION': r'print',
            'IDENTIFIER': r'\b[a-zA-Z][a-zA-Z0-9_]*\b',
            'NUMBER': r'\b\d+\b',
            'RELATIONAL_OPERATOR': r'(==|!=|<=|>=|<|>)',
            'MATHEMATICAL_OPERATOR': r'(\+|-|\*|/|%|\*\*)',
            'LOGICAL_OPERATOR': r'(\|\||&&)',
            'ASSIGNMENT_OPERATOR': r'=',
            'DOUBLE_COLON': r'::', 
            'DELIMITER': r'[,\[\]\{\}\(\)]',  
            'END_LINE_OPERATOR': r';', 
            'STRING': r'"[^"]*"',
            'COMMENT': r'\$.*',  
            'WHITESPACE': r'\s+',
            'UNKNOWN': r'.',  
        }

        # Combine patterns into a single regex
        self.regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_patterns.items())
    
    def tokenize(self, code):
        tokens = []
        line_number = 1
        position = 0
        

        while position < len(code):
            match = re.match(self.regex, code[position:])
            if not match:
                raise ValueError(f"Lexical Error: Unrecognized token at line {line_number}, position {position}")
            
            for token_type, token_value in match.groupdict().items():
                if token_value is not None:
                    if token_type == 'COMMENT':
                        # Ignore comments
                        pass
                    elif token_type == 'WHITESPACE':
                        # Update line number on newline
                        line_number += token_value.count('\n')
                    elif token_type == 'UNKNOWN':
                        raise ValueError(f"Lexical Error: Unrecognized token '{token_value}' at line {line_number}")
                    else:
                        tokens.append([token_type, token_value, line_number])
                    break
            
            position += len(match.group(0))

        return tokens

    def process_file(self, input_file, output_file):
        with open(input_file, 'r') as file:
            code = file.read()
        
        try:
            tokens = self.tokenize(code)
            with open(output_file, 'w') as file:
                for token in tokens:
                    file.write(f"{token}\n")
            print(f"Tokens successfully written to {output_file}.")
        except ValueError as e:
            print(e)