import re
from util.token import Token, TokenType

token_regex = {
    TokenType.SKIP:           re.compile(r'([\s\t]+)|#.*'),
    TokenType.RATIONAL:       re.compile(r'\d+\.\d+'),
    TokenType.INTEGER:        re.compile(r'\d+'),
    TokenType.BOOLEAN:        re.compile(r'\b(true|false)\b'),
    TokenType.STRING:         re.compile(r'"([^"\\]|\\.)*"'),
    
    TokenType.TYPE_KEYWORD:   re.compile(r'\btype\b'), # Regra para a palavra-chave 'type'
    TokenType.TYPE:           re.compile(r'\b(string|integer|rational|boolean|list|void)\b'),
    TokenType.VARTYPE:        re.compile(r'\b(constant|variable)\b'),
    
    TokenType.CREATE:         re.compile(r'\bcreate\b'),
    TokenType.DO:             re.compile(r'\bdo\b'),
    TokenType.ELSE:           re.compile(r'\belse\b'),
    TokenType.ELIF:           re.compile(r'\belif\b'),
    TokenType.END:            re.compile(r'\bend\b'),
    TokenType.FOR:            re.compile(r'\bfor\b'),
    TokenType.FUNCTION:       re.compile(r'\bfunction\b'),
    TokenType.IF:             re.compile(r'\bif\b'),
    TokenType.IN:             re.compile(r'\bin\b'),
    TokenType.READ:           re.compile(r'\bread\b'),
    TokenType.RETURN:         re.compile(r'\breturn\b'),
    TokenType.SET:            re.compile(r'\bset\b'),
    TokenType.THEN:           re.compile(r'\bthen\b'),
    TokenType.TO:             re.compile(r'\bto\b'),
    TokenType.WHILE:          re.compile(r'\bwhile\b'),
    TokenType.WRITE:          re.compile(r'\bwrite\b'),
    TokenType.WRITELN:        re.compile(r'\bwriteln\b'),

    TokenType.GREATER_EQUAL:  re.compile(r'>='),
    TokenType.LESS_EQUAL:     re.compile(r'<='),
    TokenType.ARROW:          re.compile(r'->'),
    TokenType.EQUAL:          re.compile(r'=='),
    TokenType.NOT_EQUAL:      re.compile(r'!='),
    TokenType.AND:            re.compile(r'&&'),
    TokenType.OR:             re.compile(r'\|\|'),
    
    TokenType.GREATER:        re.compile(r'>'),
    TokenType.LESS:           re.compile(r'<'),
    TokenType.NOT:            re.compile(r'!'),
    TokenType.ADDITION:       re.compile(r'\+'),
    TokenType.SUBTRACTION:    re.compile(r'-'),
    TokenType.MULTIPLICATION: re.compile(r'\*'),
    TokenType.DIVISION:       re.compile(r'/'),
    TokenType.MODULUS:        re.compile(r'%'),
    TokenType.LPAREN:         re.compile(r'\('),
    TokenType.RPAREN:         re.compile(r'\)'),
    TokenType.LBRACKET:       re.compile(r'\['),
    TokenType.RBRACKET:       re.compile(r'\]'),
    TokenType.SEMICOLON:      re.compile(r';'),
    TokenType.COMMA:          re.compile(r','),
    TokenType.COLON:          re.compile(r':'),
    TokenType.DOT:            re.compile(r'\.'),
    TokenType.IDENTIFIER:     re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*'),
}

class Lexer:
    def __init__(self):
        self.text = ""
        self.pos = 0
        self.line = 1
        self.column = 1

    def tokenize(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        tokens = []

        while self.pos < len(self.text):
            if self.text[self.pos] == '\n':
                self.line += 1
                self.column = 1
                self.pos += 1
                continue

            matched = False
            for token_type, regex in token_regex.items():
                match = regex.match(self.text, self.pos)
                if match:
                    lexeme = match.group(0)
                    if token_type != TokenType.SKIP:
                        tokens.append(Token(token_type, lexeme, self.line, self.column))
                    
                    self.pos += len(lexeme)
                    self.column += len(lexeme)
                    matched = True
                    break
            
            if not matched:
                raise Exception(f"Caractere inválido na linha {self.line}, coluna {self.column}: {self.text[self.pos]}")
        
        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens
