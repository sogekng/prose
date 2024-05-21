import ply.lex as lex


tokens = (
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'EQUALS',
    'SEMICOLON',
    'IDENTIFIER',
    'STRING',
    'PRINT',
    'IF',
    'ELSE',
    'WHILE',
    'FOR'
)


reserved = {
    'print': 'PRINT',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR'
}


t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_EQUALS    = r'='
t_SEMICOLON = r';'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]
    return t


def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


t_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


lexer = lex.lex()


if __name__ == "__main__":
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
    lexer.input(data)
    for token in lexer:
        print(token)
