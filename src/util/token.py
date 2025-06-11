from enum import Enum, auto

class TokenType(Enum):
    NONE = auto()
    SKIP = auto()
    EOF = auto()
    NOT = auto()
    AND = auto()
    OR = auto()
    ADDITION = auto()
    DIVISION = auto()
    EQUAL = auto()
    GREATER = auto()
    LESS = auto()
    MODULUS = auto()
    MULTIPLICATION = auto()
    NOT_EQUAL = auto()
    SUBTRACTION = auto()
    BOOLEAN = auto()
    RATIONAL = auto()
    INTEGER = auto()
    STRING = auto()
    LIST = auto()
    LPAREN = auto()
    RPAREN = auto()
    SEMICOLON = auto()
    COMMA = auto()
    COLON = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    TYPE = auto()
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
    WRITELN = auto()
    END = auto()
    THEN = auto()
    FUNCTION = auto()
    RETURN = auto()
    IDENTIFIER = auto()

class Token:
    def __init__(self, token_type, value, line, column):
        self.token_type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"T({self.token_type.name}, {repr(self.value)})"