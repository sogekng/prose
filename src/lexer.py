import re
from util.token import Token

class Lexer:
    def __init__(self):
        self.tokens = []
        self.current_char = None
        self.current_position = -1
        self.current_line = 1
        self.current_column = 0
        self.text = ""
        self.token_specs = [
            ('STRING', r'"([^"\\]|\\.)*"'),
            ('FORMAT_STRING', r'"([^"\\]|\\.)*(%[sdfb]([^"\\]|\\.)*)*"'),
            ('NUMBER', r'\d+(\.\d*)?'),
            ('BOOLEAN', r'\b(true|false)\b'),
            ('CREATE', r'\bcreate\b'),
            ('IF', r'\bif\b'),
            ('ELSE', r'\belse\b'),
            ('WHILE', r'\bwhile\b'),
            ('DO', r'\bdo\b'),
            ('READ', r'\bread\b'),
            ('WRITE', r'\bwrite\b'),
            ('VARIABLE', r'\bvariable\b'),
            ('CONSTANT', r'\bconstant\b'),
            ('SET', r'\bset\b'),
            ('TO', r'\bto\b'),
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('EQUAL', r'=='),
            ('NOT_EQUAL', r'!='),
            ('GREATER', r'>'),
            ('LESS', r'<'),
            ('ADDITION', r'\+'),
            ('SUBTRACTION', r'-'),
            ('MULTIPLICATION', r'\*'),
            ('DIVISION', r'/'),
            ('MODULUS', r'%'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('LBRACE', r'\{'),
            ('RBRACE', r'\}'),
            ('SEMICOLON', r';'),
            ('NEWLINE', r'\n'),
            ('SKIP', r'[ \t]+'),
        ]
        self.token_regex = [(token_type, re.compile(regex)) for token_type, regex in self.token_specs]
        self.current_char = self.text[0] if self.text else None


    def tokenize(self, text):
        self.text = text
        self.current_position = -1
        self.current_line = 1
        self.current_column = 0
        self.tokens = []
        self.advance()

        while self.current_char is not None:
            token = self.next_token()
            if token:
                self.tokens.append(token)

        return self.tokens


    def next_token(self):
        while self.current_char is not None:
            if self.current_char == '\n':
                token = Token('NEWLINE', self.current_char, self.current_line, self.current_column)
                self.advance()
                return token
            for token_type, regex in self.token_regex:
                match = regex.match(self.text, self.current_position)
                if match:
                    lexeme = match.group(0)
                    if token_type == 'SKIP':
                        self.advance(len(lexeme))
                        return None
                    start_line = self.current_line
                    start_column = self.current_column
                    token = Token(token_type, lexeme, start_line, start_column)
                    self.advance(len(lexeme))
                    return token
            self.advance()
        return None


    def advance(self, steps=1):
        for _ in range(steps):
            if self.current_position + 1 >= len(self.text):
                self.current_char = None
            else:
                self.current_position += 1
                self.current_char = self.text[self.current_position]
                if self.current_char == '\n':
                    self.current_line += 1
                    self.current_column = 0
                else:
                    self.current_column += 1
