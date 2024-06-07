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
    COMMA = auto()
    COLON = auto()

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

    # functions
    FUNCTION = auto()
    RETURN = auto()

    IDENTIFIER = auto()


STRUCTURE_TOKENS = [
    TokenType.IF,
    TokenType.ELIF,
    TokenType.ELSE,
    TokenType.DO,
    TokenType.WHILE,
    TokenType.FUNCTION
]

LITERAL_TOKENS = [
    TokenType.BOOLEAN,
    TokenType.NUMBER,
    TokenType.STRING,
]

INVALID_EXPRESSION_TOKENS = [
    TokenType.TYPE,
    TokenType.VARTYPE,
    TokenType.CREATE,
    TokenType.DO,
    TokenType.ELIF,
    TokenType.ELSE,
    TokenType.IF,
    TokenType.READ,
    TokenType.SET,
    TokenType.TO,
    TokenType.WHILE,
    TokenType.WRITE,
    TokenType.END,
    TokenType.THEN,
]


class Token:
    def __init__(self, token_type, value, line, column):
        self.token_type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"T({self.token_type}, {repr(self.value)})"
