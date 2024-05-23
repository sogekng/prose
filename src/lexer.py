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
            ('STRING', r'\"([^\\\n]|(\\.))*?\"'),
            ('NUMBER', r'\d+'),
            ('COMMENT', r'//.*'),
            ('EQ', r'=='),
            ('NEQ', r'!='),
            ('GT', r'>'),
            ('LT', r'<'),
            ('GTE', r'>='),
            ('LTE', r'<='),
            ('ADDITION', r'\+'),
            ('SUBTRACTION', r'-'),
            ('MULTIPLICATION', r'\*'),
            ('DIVISION', r'/'),
            ('ASSIGNMENT', r'='),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('LBRACE', r'\{'),
            ('RBRACE', r'\}'),
            ('SEMICOLON', r';'),
            ('NEWLINE', r'\n'),
            ('SKIP', r'[ \t]+'),
            ('PRINT', r'print'),
            ('IF', r'if'),
            ('ELSE', r'else'),
            ('WHILE', r'while'),
            ('DO', r'do'),
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z_0-9]*')
        ]


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
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char == '\n':
                self.advance()
            else:
                for pattern, regex in self.token_specs:
                    regex = re.compile(regex)
                    match = regex.match(self.text, self.current_position)
                    if match:
                        lexeme = match.group(0)
                        if pattern == 'COMMENT':
                            while self.current_char != '\n' and self.current_char is not None:
                                self.advance()
                            break
                        value = lexeme
                        if pattern == 'NUMBER':
                            value = int(value)
                        elif pattern == 'STRING':
                            value = value[1:-1]

                        start_line = self.current_line
                        start_column = self.current_column - len(lexeme)
                        token = Token(pattern, value, start_line, start_column)
                        self.current_position += len(lexeme) - 1
                        self.advance()
                        return token
                else:
                    self.advance()
        return None


    def advance(self):
        self.current_position += 1
        if self.current_position >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.current_position]
            if self.current_char == '\n':
                self.current_line += 1
                self.current_column = 0
            else:
                self.current_column += 1


    def log_token(self, token):
        with open('tokens.log', 'a') as file:
            file.write(f"{token}\n")


# if __name__ == "__main__":
#     lexer = Lexer()
#     data = '''
#         //print("Hello, World!");
#
#         //x = 10;
#
#         //if (x > 5) {
#         //    x = x + 1;
#         //} else {
#         //    x = x - 1;
#         //}
#
#         //while (x < 20) {
#         //    x = x * 2;
#         //}
#
#         //do {
#         //    x = x / 3;
#         //} while (x < 30);
#
#         // Teste de operadores relacionais
#         y == 10;
#         z != 5;
#         a > 1;
#         b < 2;
#         c >= 3;
#         d <= 4;
#     '''
#     tokens = lexer.tokenize(data)
#     for token in tokens:
#         print(token)
#
#     lexer.log_token(tokens)
