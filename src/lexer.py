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
            ('PLUS', r'\+'),
            ('MINUS', r'-'),
            ('TIMES', r'\*'),
            ('DIVIDE', r'/'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('LBRACE', r'\{'),
            ('RBRACE', r'\}'),
            ('EQUALS', r'='),
            ('SEMICOLON', r';'),
            ('NEWLINE', r'\n'),
            ('SKIP', r'[ \t]+'),
            ('PRINT', r'print'),
            ('IF', r'if'),
            ('ELSE', r'else'),
            ('WHILE', r'while'),
            ('FOR', r'for'),
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z_0-9]*'),
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


    def next_token(self):
        for pattern, regex in self.token_specs:
            regex = re.compile(regex)
            match = regex.match(self.text, self.current_position)
            if match:
                lexeme = match.group(0)
                value = lexeme
                if pattern == 'NUMBER':
                    value = int(value)
                elif pattern == 'STRING':
                    value = value[1:-1]  # Remove as aspas

                if pattern == 'NEWLINE':
                    self.advance()
                    return None
                elif pattern == 'SKIP':
                    self.advance()
                    return None

                token = Token(pattern, value, self.current_line, self.current_column)
                self.current_position += len(lexeme) - 1
                self.advance()
                return token
        self.advance()
        return None


if __name__ == "__main__":
    lexer = Lexer()
    data = '''
        print("Hello, World!");
        x = 10;
        if (x > 5) {
            x = x + 1;
        } else {
            x = x - 1;
        }
        while (x < 20) {
            x = x + 2;
        }
        for(i=1;i<=10;i++){}
    '''
    tokens = lexer.tokenize(data)
    for token in tokens:
        print(token)
