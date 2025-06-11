from dataclasses import dataclass
from util.token import Token, TokenType
from render import VariableBank, VariableType, Variable

LITERAL_AND_IDENTIFIER_TOKENS = {
    TokenType.BOOLEAN, TokenType.RATIONAL, TokenType.INTEGER,
    TokenType.STRING, TokenType.IDENTIFIER
}

class ParseException(Exception):
    def __init__(self, message, token):
        super().__init__(f"Erro na linha {token.line} coluna {token.column}: {message} (token: '{token.value}')")
        self.token = token

@dataclass
class Expression:
    def render(self, varbank: VariableBank) -> str:
        raise NotImplementedError

@dataclass
class Value(Expression):
    token: Token
    def render(self, varbank: VariableBank) -> str:
        return self.token.value

@dataclass
class BinOp(Expression):
    left: Expression
    op: Token
    right: Expression
    def render(self, varbank: VariableBank) -> str:
        return f"({self.left.render(varbank)} {self.op.value} {self.right.render(varbank)})"

@dataclass
class Statement:
    def render(self, varbank: VariableBank) -> str:
        raise NotImplementedError
    
@dataclass
class ListLiteral(Expression):
    elements: list[Expression]
    def render(self, varbank: VariableBank) -> str:
        rendered_elements = [elem.render(varbank) for elem in self.elements]

        return f"new ArrayList<Object>(Arrays.asList({', '.join(rendered_elements)}))"

@dataclass
class ListAccess(Expression):
    identifier: Token
    index_expression: Expression
    def render(self, varbank: VariableBank) -> str:
        return f"{self.identifier.value}.get({self.index_expression.render(varbank)})"

@dataclass
class ListAssignmentStatement(Statement):
    list_access: ListAccess
    expression: Expression
    def render(self, varbank: VariableBank) -> str:
        list_name = self.list_access.identifier.value
        index_code = self.list_access.index_expression.render(varbank)
        value_code = self.expression.render(varbank)
        
        return f"{list_name}.set({index_code}, {value_code});"

@dataclass
class CreateStatement(Statement):
    vartype: Token
    const_or_var: Token
    identifier: Token
    expression: Expression | None
    
    def render(self, varbank: VariableBank) -> str:
        var_type_map = {
            'string': VariableType.STRING, 'integer': VariableType.INTEGER,
            'rational': VariableType.RATIONAL, 'boolean': VariableType.BOOLEAN,
            'list': VariableType.LIST
        }
        lang_type = var_type_map[self.vartype.value]
        is_constant = self.const_or_var.value == 'constant'
        var_name = self.identifier.value

        varbank.create(var_name, is_constant, lang_type, self.expression is not None)

        java_type_map = {
            VariableType.STRING: "String", VariableType.INTEGER: "int",
            VariableType.RATIONAL: "float", VariableType.BOOLEAN: "boolean",
            VariableType.LIST: "ArrayList<Object>"
        }
        java_type = java_type_map[lang_type]
        
        parts = []
        if is_constant:
            parts.append("final")
        parts.append(java_type)
        parts.append(var_name)

        if self.expression:
            parts.append("=")
            parts.append(self.expression.render(varbank))
        elif lang_type == VariableType.LIST:
            parts.append("=")
            parts.append("new ArrayList<Object>()")
            
        return " ".join(parts) + ";"

@dataclass
class SetStatement(Statement):
    identifier: Token
    expression: Expression
    def render(self, varbank: VariableBank) -> str:
        varbank.redefine(self.identifier.value, True)
        return f"{self.identifier.value} = {self.expression.render(varbank)};"

@dataclass
class ReadStatement(Statement):
    identifier: Token
    def render(self, varbank: VariableBank) -> str:
        variable = varbank.get(self.identifier.value)
        varbank.redefine(self.identifier.value, True)
        
        method_map = {
            VariableType.STRING: "nextLine", VariableType.INTEGER: "nextInt",
            VariableType.RATIONAL: "nextFloat", VariableType.BOOLEAN: "nextBoolean"
        }
        method = method_map[variable.vartype]
        return f"{self.identifier.value} = scanner.{method}();"

@dataclass
class BaseWriteStatement(Statement):
    expression: Expression
    newline: bool = False

    def render(self, varbank: VariableBank) -> str:
        rendered_expr = self.expression.render(varbank)
        if self.newline:
            return f"System.out.println({rendered_expr});"
        else:
            return f"System.out.print({rendered_expr});"

class WriteStatement(BaseWriteStatement):
    def __init__(self, expression: Expression):
        super().__init__(expression, newline=False)

class WriteLnStatement(BaseWriteStatement):
    def __init__(self, expression: Expression):
        super().__init__(expression, newline=True)

@dataclass
class IfStructure(Statement):
    conditions: list[Expression]
    bodies: list[list[Statement]]
    else_body: list[Statement] | None
    
    def render(self, varbank: VariableBank) -> str:
        lines = []
        
        varbank.start_scope()
        lines.append(f"if ({self.conditions[0].render(varbank)}) {{")
        lines.extend([stmt.render(varbank) for stmt in self.bodies[0]])
        varbank.end_scope()

        for i in range(1, len(self.bodies)):
            varbank.start_scope()
            lines.append(f"}} else if ({self.conditions[i].render(varbank)}) {{")
            lines.extend([stmt.render(varbank) for stmt in self.bodies[i]])
            varbank.end_scope()
        
        if self.else_body is not None:
            varbank.start_scope()
            lines.append("} else {")
            lines.extend([stmt.render(varbank) for stmt in self.else_body])
            varbank.end_scope()
        
        lines.append("}")
        return "\n".join(lines)

@dataclass
class WhileStructure(Statement):
    condition: Expression
    body: list[Statement]
    def render(self, varbank: VariableBank) -> str:
        lines = []
        varbank.start_scope()
        lines.append(f"while ({self.condition.render(varbank)}) {{")
        lines.extend([stmt.render(varbank) for stmt in self.body])
        lines.append("}")
        varbank.end_scope()
        return "\n".join(lines)

@dataclass
class DoWhileStructure(Statement):
    condition: Expression
    body: list[Statement]
    def render(self, varbank: VariableBank) -> str:
        lines = []
        varbank.start_scope()
        lines.append("do {")
        lines.extend([stmt.render(varbank) for stmt in self.body])
        lines.append(f"}} while ({self.condition.render(varbank)});")
        varbank.end_scope()
        return "\n".join(lines)

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    @property
    def current_token(self) -> Token:
        return self.tokens[self.pos]

    def advance(self):
        self.pos += 1

    def consume(self, expected_type: TokenType):
        if self.current_token.token_type == expected_type:
            token = self.current_token
            self.advance()
            return token
        raise ParseException(f"Esperava o token {expected_type.name}, mas encontrou {self.current_token.token_type.name}", self.current_token)

    def parse(self) -> list[Statement]:
        statements = []
        while self.current_token.token_type != TokenType.EOF:
            statements.append(self.parse_statement())
        return statements

    def parse_block(self) -> list[Statement]:
        statements = []
        while self.current_token.token_type not in {TokenType.END, TokenType.ELSE, TokenType.ELIF, TokenType.EOF}:
             statements.append(self.parse_statement())
        return statements

    def parse_statement(self) -> Statement:
        token_type = self.current_token.token_type
        
        if token_type == TokenType.CREATE:
            stmt = self.parse_create_statement()
        elif token_type == TokenType.SET:
            stmt = self.parse_set_statement()
        elif token_type == TokenType.READ:
            stmt = self.parse_read_statement()
        elif token_type == TokenType.WRITE:
            stmt = self.parse_write_statement()
        elif token_type == TokenType.WRITELN:
            stmt = self.parse_writeln_statement()
        elif token_type == TokenType.IF:
            return self.parse_if_structure()
        elif token_type == TokenType.WHILE:
            return self.parse_while_structure()
        elif token_type == TokenType.DO:
            return self.parse_do_while_structure()
        else:
            raise ParseException("Declaração inválida ou inesperada", self.current_token)
        
        self.consume(TokenType.SEMICOLON)
        return stmt

    def parse_create_statement(self):
        self.consume(TokenType.CREATE)
        vartype = self.consume(TokenType.TYPE)
        const_or_var = self.consume(TokenType.VARTYPE)
        identifier = self.consume(TokenType.IDENTIFIER)
        
        expression = None

        if self.current_token.token_type == TokenType.LBRACKET:
            if vartype.value != 'list':
                raise ParseException("A inicialização com '[]' é permitida apenas para o tipo 'list'", self.current_token)
            expression = self.parse_list_literal()
        elif self.current_token.token_type != TokenType.SEMICOLON:
            expression = self.parse_expression()
            
        return CreateStatement(vartype, const_or_var, identifier, expression)

    def parse_set_statement(self):
        self.consume(TokenType.SET)

        target_token = self.current_token
        if target_token.token_type != TokenType.IDENTIFIER:
            raise ParseException("O alvo de 'set' deve ser um identificador", target_token)
        
        target_expr = self.parse_primary_expression()
        
        self.consume(TokenType.TO)
        value_expression = self.parse_expression()

        if isinstance(target_expr, ListAccess):
            return ListAssignmentStatement(target_expr, value_expression)
        elif isinstance(target_expr, Value):
            return SetStatement(target_expr.token, value_expression)
        else:
            raise ParseException("Alvo de atribuição inválido", target_token)
        
    def parse_read_statement(self):
        self.consume(TokenType.READ)
        identifier = self.consume(TokenType.IDENTIFIER)
        return ReadStatement(identifier)

    def parse_write_statement(self):
        self.consume(TokenType.WRITE)
        expression = self.parse_expression()
        return WriteStatement(expression)
    
    def parse_writeln_statement(self):
        self.consume(TokenType.WRITELN)
        expression = self.parse_expression()
        return WriteLnStatement(expression)

    def parse_if_structure(self):
        self.consume(TokenType.IF)
        conditions = [self.parse_expression()]
        self.consume(TokenType.THEN)
        bodies = [self.parse_block()]
        else_body = None

        while self.current_token.token_type == TokenType.ELIF:
            self.consume(TokenType.ELIF)
            conditions.append(self.parse_expression())
            self.consume(TokenType.THEN)
            bodies.append(self.parse_block())
            
        if self.current_token.token_type == TokenType.ELSE:
            self.consume(TokenType.ELSE)
            else_body = self.parse_block()
            
        self.consume(TokenType.END)
        return IfStructure(conditions, bodies, else_body)
    
    def parse_while_structure(self):
        self.consume(TokenType.WHILE)
        condition = self.parse_expression()
        self.consume(TokenType.DO)
        body = self.parse_block()
        self.consume(TokenType.END)
        return WhileStructure(condition, body)

    def parse_do_while_structure(self):
        self.consume(TokenType.DO)
        body = self.parse_block()
        self.consume(TokenType.WHILE)
        condition = self.parse_expression()
        self.consume(TokenType.SEMICOLON)
        return DoWhileStructure(condition, body)
    
    def parse_list_literal(self) -> ListLiteral:
        self.consume(TokenType.LBRACKET)
        elements = []
        if self.current_token.token_type != TokenType.RBRACKET:
            elements.append(self.parse_expression())
            while self.current_token.token_type == TokenType.COMMA:
                self.consume(TokenType.COMMA)
                elements.append(self.parse_expression())
        
        self.consume(TokenType.RBRACKET)
        return ListLiteral(elements)

    PRECEDENCE = {
        TokenType.OR: 1, TokenType.AND: 2,
        TokenType.EQUAL: 3, TokenType.NOT_EQUAL: 3, TokenType.LESS: 3, TokenType.GREATER: 3,
        TokenType.ADDITION: 4, TokenType.SUBTRACTION: 4,
        TokenType.MULTIPLICATION: 5, TokenType.DIVISION: 5, TokenType.MODULUS: 5
    }

    def get_precedence(self, token_type: TokenType):
        return self.PRECEDENCE.get(token_type, 0)

    def parse_primary_expression(self):
        token = self.current_token
        
        if token.token_type not in LITERAL_AND_IDENTIFIER_TOKENS and token.token_type != TokenType.LPAREN:
             raise ParseException("Expressão primária inválida", token)

        if token.token_type == TokenType.IDENTIFIER:
            self.advance()
            if self.current_token.token_type == TokenType.LBRACKET:
                self.consume(TokenType.LBRACKET)
                index_expr = self.parse_expression()
                self.consume(TokenType.RBRACKET)
                return ListAccess(token, index_expr)
            else:
                return Value(token)
        elif token.token_type in LITERAL_AND_IDENTIFIER_TOKENS:
            self.advance()
            return Value(token)
        elif token.token_type == TokenType.LPAREN:
            self.consume(TokenType.LPAREN)
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN)
            return expr

    def parse_expression(self, precedence=0):
        left_expr = self.parse_primary_expression()

        while self.pos < len(self.tokens):
            op_token = self.current_token
            op_precedence = self.get_precedence(op_token.token_type)

            if op_precedence <= precedence:
                break
                
            self.advance()
            right_expr = self.parse_expression(op_precedence)
            left_expr = BinOp(left_expr, op_token, right_expr)
        
        return left_expr