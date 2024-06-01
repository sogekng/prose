import re
from util.token import Token

class Lexer:
    """
    Classe Lexer para realizar a análise léxica (tokenização).

    Atributos:
        tokens (list): Lista de tokens identificados.
        current_char (str): Caractere atual sendo analisado.
        current_position (int): Posição atual do caractere no texto.
        current_line (int): Linha atual no texto.
        current_column (int): Coluna atual no texto.
        text (str): Texto completo que está sendo analisado.
        token_specs (list): Especificações de tokens com nomes e expressões regulares.
        token_regex (list): Lista de tuplas (tipo de token, expressão regular compilada).
    """
    def __init__(self):
        """
        Inicializa o analisador léxico com especificações de tokens e prepara o ambiente de análise.
        """
        self.reset()
        self.token_specs = [
            # Specials
            ('SKIP', r'([\s\n]+)|#.*'),

            # Operators
            ('ADDITION', r'\+'),
            ('DIVISION', r'/'),
            ('EQUAL', r'=='),
            ('GREATER', r'>'),
            ('LESS', r'<'),
            ('MODULUS', r'%'),
            ('MULTIPLICATION', r'\*'),
            ('NOT_EQUAL', r'!='),
            ('SUBTRACTION', r'-'),

            # Literals
            ('BOOLEAN', r'\btrue|false\b'),
            ('NUMBER', r'\d+(\.\d+)?|\.\d+'),
            ('STRING', r'"([^"\\]|\\.)*"'),

            # Delimiters
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('SEMICOLON', r';'),

            # Types
            ('TYPE', r'\b(string)|(integer)|(rational)|(boolean)\b'),

            # Keywords
            ('VARTYPE', r'\b(constant)|(variable)\b'),
            ('CREATE', r'\bcreate\b'),
            ('DO', r'\bdo\b'),
            ('ELSE', r'\belse\b'),
            ('ELSE', r'\belif\b'),
            ('IF', r'\bif\b'),
            ('READ', r'\bread\b'),
            ('SET', r'\bset\b'),
            ('TO', r'\bto\b'),
            ('WHILE', r'\bwhile\b'),
            ('WRITE', r'\bwrite\b'),
            ('END', r'\bend\b'),
            ('THEN', r'\bthen\b'),

            ('IDENTIFIER', r'([a-zA-Z_][a-zA-Z0-9_]*)'),
        ]
        self.token_regex = [(token_type, re.compile(regex)) for token_type, regex in self.token_specs]


    def reset(self, new_text=""):
        self.current_position = 0
        self.current_line = 1
        self.current_column = 0
        self.tokens = []
        self.current_char = None
        self.text = new_text
        self.current_char = self.text[0] if self.text else None

    
    def tokenize(self, text):
        """
        Processa o texto para extrair tokens conforme as especificações.

        Args:
            text (str): Texto a ser tokenizado.

        Return:
            list: Lista de objetos Token gerados a partir do texto.
        """
        self.reset(text)

        token = None
        while (token := self.next_token()) is not None:
            if token.type != 'SKIP':
                self.tokens.append(token)

        return self.tokens


    def next_token(self):
        """
        Identifica o próximo token no texto baseado nas especificações regulares.

        Return:
            Token: O próximo token identificado ou None se um token deve ser ignorado (como espaços).
        """
        if self.current_char is None:
            # return Token('EOF', '', self.current_line, self.current_column)
            return None

        if self.current_char == '\n':
            token = Token('SKIP', self.current_char, self.current_line, self.current_column)
            self.advance()
            return token

        for token_type, regex in self.token_regex:
            match = regex.match(self.text, self.current_position)

            if not match:
                continue

            lexeme = match.group(0)
            token = Token(token_type, lexeme, self.current_line, self.current_column)
            self.advance(len(lexeme))
            return token

        self.advance()
        return None


    def advance(self, steps=1):
        """
        Avança o caractere atual no texto, atualizando posição, linha e coluna.

        Args:
            steps (int): Número de passos para avançar no texto.

        Return:
            Token: O próximo token identificado ou None se um token deve ser ignorado (como espaços).
        """
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
