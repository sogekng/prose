from enum import Enum, auto


class TokenType(Enum):
    # Specials
    NONE = auto()
    SKIP = auto()

    # Operators
    ADDITION = auto()
    DIVISION = auto()
    EQUAL = auto()
    GREATER = auto()
    LESS = auto()
    MODULUS = auto()
    MULTIPLICATION = auto()
    NOT_EQUAL = auto()
    SUBTRACTION = auto()

    # Literals
    BOOLEAN = auto()
    NUMBER = auto()
    STRING = auto()

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    SEMICOLON = auto()

    # Types
    TYPE = auto()

    # Keywords
    VARTYPE = auto()
    CREATE = auto()
    DO = auto()
    ELIF = auto()
    ELSE = auto()
    IF = auto()
    READ = auto()
    SET = auto()
    TO = auto()
    WHILE = auto()
    WRITE = auto()
    END = auto()
    THEN = auto()

    IDENTIFIER = auto()


STRUCTURE_TOKENS = [TokenType.IF, TokenType.ELIF, TokenType.ELSE, TokenType.WHILE, TokenType.DO]
LITERAL_TOKENS = [TokenType.BOOLEAN, TokenType.NUMBER, TokenType.STRING]


class Token:
    def __init__(self, token_type, value, line, column):
        self.token_type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.token_type}, {repr(self.value)})"
        # return f"Token({self.token_type}, {repr(self.value)}, position[{self.line}:{self.column}])"
