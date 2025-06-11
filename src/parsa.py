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
        numeric_ops = {
            TokenType.SUBTRACTION, TokenType.MULTIPLICATION, 
            TokenType.DIVISION, TokenType.MODULUS
        }
        op_token_type = self.op.token_type
        if op_token_type == TokenType.ADDITION:
            if (isinstance(self.left, Value) and self.left.token.token_type == TokenType.STRING) or \
               (isinstance(self.right, Value) and self.right.token.token_type == TokenType.STRING):
                return f"({self.left.render(varbank)} + {self.right.render(varbank)})"
            else:
                left_rendered = f"((Number)({self.left.render(varbank)})).doubleValue()"
                right_rendered = f"((Number)({self.right.render(varbank)})).doubleValue()"
                return f"({left_rendered} + {right_rendered})"
        elif op_token_type in numeric_ops:
            left_rendered = f"((Number)({self.left.render(varbank)})).doubleValue()"
            right_rendered = f"((Number)({self.right.render(varbank)})).doubleValue()"
            return f"({left_rendered} {self.op.value} {right_rendered})"
        else:
            return f"({self.left.render(varbank)} {self.op.value} {self.right.render(varbank)})"

@dataclass
class FunctionCall(Expression):
    callee_name: Token
    arguments: list[Expression]
    def render(self, varbank: VariableBank) -> str:
        expected_arity = varbank.get_function_arity(self.callee_name.value)
        if len(self.arguments) != expected_arity:
            raise Exception(f"Função '{self.callee_name.value}' espera {expected_arity} argumentos, mas recebeu {len(self.arguments)}")
        
        rendered_args = [arg.render(varbank) for arg in self.arguments]
        return f"{self.callee_name.value}({', '.join(rendered_args)})"

@dataclass
class Statement:
    def render(self, varbank: VariableBank) -> str:
        raise NotImplementedError

@dataclass
class ExpressionStatement(Statement):
    expression: Expression
    def render(self, varbank: VariableBank) -> str:
        return self.expression.render(varbank) + ";"

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
            expression_code = self.expression.render(varbank)
            
            if lang_type == VariableType.INTEGER:
                expression_code = f"((Number)({expression_code})).intValue()"
            elif lang_type == VariableType.RATIONAL:
                expression_code = f"((Number)({expression_code})).floatValue()"
            elif lang_type == VariableType.BOOLEAN:
                expression_code = f"(Boolean)({expression_code})"
            elif isinstance(self.expression, FunctionCall):
                 if lang_type == VariableType.STRING:
                     expression_code = f"(String)({expression_code})"
                 elif lang_type == VariableType.LIST:
                     expression_code = f"(ArrayList<Object>)({expression_code})"

            parts.append(expression_code)
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
        
        variable = varbank.get(self.identifier.value)
        expression_code = self.expression.render(varbank)

        if variable.vartype == VariableType.INTEGER:
            expression_code = f"((Number)({expression_code})).intValue()"
        elif variable.vartype == VariableType.RATIONAL:
            expression_code = f"((Number)({expression_code})).floatValue()"
        elif variable.vartype == VariableType.BOOLEAN:
            expression_code = f"(Boolean)({expression_code})"
        elif isinstance(self.expression, FunctionCall):
            if variable.vartype == VariableType.STRING:
                expression_code = f"(String)({expression_code})"
            elif variable.vartype == VariableType.LIST:
                expression_code = f"(ArrayList<Object>)({expression_code})"

        return f"{self.identifier.value} = {expression_code};"

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

@dataclass
class FunctionDeclaration(Statement):
    name: Token
    params: list[Token]
    body: list[Statement]
    def render(self, varbank: VariableBank) -> str:
        varbank.create_function(self.name.value, len(self.params))
        varbank.start_scope()
        java_params = []
        for param in self.params:
            varbank.create(param.value, constant=False, vartype=None, value=True)
            java_params.append(f"Object {param.value}")
        rendered_body = "\n".join([stmt.render(varbank) for stmt in self.body])
        varbank.end_scope()
        needs_default_return = not (self.body and isinstance(self.body[-1], ReturnStatement))
        function_code = (
            f"public static Object {self.name.value}({', '.join(java_params)}) {{\n"
            f"{rendered_body}"
        )
        if needs_default_return:
            function_code += "\nreturn null;"
        function_code += "\n}"
        return function_code

@dataclass
class ReturnStatement(Statement):
    expression: Expression | None
    def render(self, varbank: VariableBank) -> str:
        if self.expression:
            return f"return {self.expression.render(varbank)};"
        return "return;"

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
        declarations = []
        while self.current_token.token_type != TokenType.EOF:
            if self.current_token.token_type == TokenType.FUNCTION:
                declarations.append(self.parse_function_declaration())
            else:
                declarations.append(self.parse_statement())
        return declarations

    def parse_block(self) -> list[Statement]:
        statements = []
        terminators = {TokenType.END, TokenType.ELSE, TokenType.ELIF, TokenType.WHILE, TokenType.EOF}
        
        while self.current_token.token_type not in terminators:
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
        elif token_type == TokenType.RETURN:
            stmt = self.parse_return_statement()
        elif token_type == TokenType.IDENTIFIER and self.tokens[self.pos + 1].token_type == TokenType.LPAREN:
            expression = self.parse_function_call()
            stmt = ExpressionStatement(expression)
        else:
            raise ParseException("Declaração inválida ou inesperada", self.current_token)
        self.consume(TokenType.SEMICOLON)
        return stmt

    def parse_function_declaration(self) -> FunctionDeclaration:
        self.consume(TokenType.FUNCTION)
        name = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.LPAREN)
        params = []
        if self.current_token.token_type != TokenType.RPAREN:
            params.append(self.consume(TokenType.IDENTIFIER))
            while self.current_token.token_type == TokenType.COMMA:
                self.consume(TokenType.COMMA)
                params.append(self.consume(TokenType.IDENTIFIER))
        self.consume(TokenType.RPAREN)
        body = self.parse_block()
        self.consume(TokenType.END)
        return FunctionDeclaration(name, params, body)
    
    def parse_return_statement(self) -> ReturnStatement:
        self.consume(TokenType.RETURN)
        expression = None
        if self.current_token.token_type != TokenType.SEMICOLON:
            expression = self.parse_expression()
        return ReturnStatement(expression)

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
        self.consume(TokenType.END)
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

    def parse_function_call(self) -> FunctionCall:
        callee_name = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.LPAREN)
        arguments = []
        if self.current_token.token_type != TokenType.RPAREN:
            arguments.append(self.parse_expression())
            while self.current_token.token_type == TokenType.COMMA:
                self.consume(TokenType.COMMA)
                arguments.append(self.parse_expression())
        self.consume(TokenType.RPAREN)
        return FunctionCall(callee_name, arguments)

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
        if token.token_type == TokenType.IDENTIFIER:
            next_token_pos = self.pos + 1
            if next_token_pos < len(self.tokens) and self.tokens[next_token_pos].token_type == TokenType.LPAREN:
                return self.parse_function_call()
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
        raise ParseException("Expressão primária inválida", token)

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