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
            ('ADDITION', r'(\+)'),
            ('BOOLEAN', r'\b(true|false)\b'),
            ('CONSTANT', r'\b(constant)\b'),
            ('CREATE', r'\b(create)\b'),
            ('DIVISION', r'(/)'),
            ('DO', r'\b(do)\b'),
            ('ELSE', r'\b(else)\b'),
            ('EQUAL', r'(==)'),
            ('FORMAT_STRING', r'"([^"\\]|\\.)*(%[sdfb]([^"\\]|\\.)*)*"'),
            ('GREATER', r'>'),
            ('IDENTIFIER', r'([a-zA-Z_][a-zA-Z0-9_]*)'),
            ('IF', r'\b(if)\b'),
            ('LBRACE', r'(\{)'),
            ('LESS', r'(<)'),
            ('LPAREN', r'(\()'),
            ('MODULUS', r'(%)'),
            ('MULTIPLICATION', r'(\*)'),
            ('NEWLINE', r'(\n)'),
            ('NOT_EQUAL', r'(!=)'),
            ('NUMBER', r'\d+(\.\d+)?|\.\d+'),
            # ('NUMBER', r'(\d+)'),
            ('RBRACE', r'(\})'),
            ('READ', r'\b(read)\b'),
            ('RPAREN', r'(\))'),
            ('SEMICOLON', r'(;)'),
            ('SET', r'\b(set)\b'),
            # ('SKIP', r'([ \t]+)'),
            ('SKIP', r'\s+'),
            ('STRING', r'"([^"\\]|\\.)*"'),
            ('SUBTRACTION', r'(-)'),
            ('TO', r'\b(to)\b'),
            ('VARIABLE', r'\b(variable)\b'),
            ('WHILE', r'\b(while)\b'),
            ('WRITE', r'\b(write)\b'),
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
            token = Token('NEWLINE', self.current_char, self.current_line, self.current_column)
            self.advance()
            return token

        for token_type, regex in self.token_regex:
            match = regex.match(self.text, self.current_position)

            if not match:
                continue

            lexeme = match.group(0)
            if token_type == 'SKIP':
                self.advance(len(lexeme))
                # return None
                continue
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
