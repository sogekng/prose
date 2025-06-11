from dataclasses import dataclass
from util.token import Token, TokenType
from render import VariableBank, IntegerType, RationalType, StringType, BooleanType, ListType, VoidType, FunctionSignature, Type, StructType

def assert_type_compatible(expected_type: Type, actual_type: Type, token: Token, message_prefix=""):
    if not (expected_type == actual_type):
        raise ParseException(f"{message_prefix}Esperava o tipo '{expected_type}', mas obteve '{actual_type}'", token)

LITERAL_AND_IDENTIFIER_TOKENS = {TokenType.BOOLEAN, TokenType.RATIONAL, TokenType.INTEGER, TokenType.STRING, TokenType.IDENTIFIER}
NATIVE_METHOD_MAP = {('list', 'length'): 'size', ('list', 'add'): 'add', ('list', 'get'): 'get', ('list', 'remove'): 'remove', ('string', 'uppercase'): 'toUpperCase', ('string', 'lowercase'): 'toLowerCase', ('string', 'substring'): 'substring'}

@dataclass
class TypeNode:
    def to_type_object(self) -> Type: raise NotImplementedError
    def to_java_type(self) -> str: raise NotImplementedError

@dataclass
class SimpleTypeNode(TypeNode):
    type_token: Token
    varbank: VariableBank 
    def to_type_object(self) -> Type:
        type_map = {'integer': IntegerType(), 'rational': RationalType(), 'string': StringType(), 'boolean': BooleanType(), 'void': VoidType()}
        if self.type_token.value in type_map: return type_map[self.type_token.value]
        return self.varbank.get_struct_type(self.type_token.value)
    def to_java_type(self) -> str:
        type_map = {'integer': 'int', 'rational': 'float', 'string': 'String', 'boolean': 'boolean', 'void': 'void'}
        if self.type_token.value in type_map: return type_map[self.type_token.value]
        return self.type_token.value
    def __repr__(self): return self.type_token.value

@dataclass
class ListTypeNode(TypeNode):
    element_type: TypeNode
    def to_type_object(self) -> Type: return ListType(self.element_type.to_type_object())
    def to_java_type(self) -> str: 
        inner_java_type = self.element_type.to_java_type()
        wrapper_map = {'int': 'Integer', 'float': 'Float', 'boolean': 'Boolean'}
        boxed_type = wrapper_map.get(inner_java_type, inner_java_type)
        return f"java.util.ArrayList<{boxed_type}>"
    def __repr__(self): return f"list<{self.element_type}>"

class ParseException(Exception):
    def __init__(self, message, token): super().__init__(f"Erro na linha {token.line} coluna {token.column}: {message} (token: '{token.value}')"); self.token = token

@dataclass
class Expression:
    def render(self, varbank: VariableBank) -> str: raise NotImplementedError
    def get_type(self, varbank: VariableBank) -> Type: raise NotImplementedError

@dataclass
class Value(Expression):
    token: Token
    def render(self, varbank: VariableBank) -> str: return f"{self.token.value}f" if self.token.token_type == TokenType.RATIONAL else self.token.value
    def get_type(self, varbank: VariableBank) -> Type:
        if self.token.token_type == TokenType.INTEGER: return IntegerType()
        if self.token.token_type == TokenType.RATIONAL: return RationalType()
        if self.token.token_type == TokenType.STRING: return StringType()
        if self.token.token_type == TokenType.BOOLEAN: return BooleanType()
        if self.token.token_type == TokenType.IDENTIFIER: return varbank.get(self.token.value).vartype
        raise ParseException("Tipo de valor desconhecido", self.token)

@dataclass
class BinOp(Expression):
    left: Expression; op: Token; right: Expression
    def render(self, varbank: VariableBank) -> str: return f"({self.left.render(varbank)} {self.op.value} {self.right.render(varbank)})"
    def get_type(self, varbank: VariableBank) -> Type:
        left_type, right_type = self.left.get_type(varbank), self.right.get_type(varbank)
        if self.op.token_type in {TokenType.ADDITION, TokenType.SUBTRACTION, TokenType.MULTIPLICATION, TokenType.DIVISION, TokenType.MODULUS}:
            if isinstance(left_type, (IntegerType, RationalType)) and isinstance(right_type, (IntegerType, RationalType)): return RationalType() if isinstance(left_type, RationalType) or isinstance(right_type, RationalType) else IntegerType()
            if self.op.token_type == TokenType.ADDITION and isinstance(left_type, StringType): return StringType()
            raise ParseException(f"Operador '{self.op.value}' inválido para os tipos {left_type} e {right_type}", self.op)
        if self.op.token_type in {TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.GREATER, TokenType.LESS, TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL, TokenType.AND, TokenType.OR}: return BooleanType()
        raise ParseException(f"Operador desconhecido ou inválido '{self.op.value}'", self.op)

@dataclass
class MemberAccess(Expression):
    obj: Expression
    member: Token
    def render(self, varbank: VariableBank) -> str: return f"{self.obj.render(varbank)}.{self.member.value}"
    def get_type(self, varbank: VariableBank) -> Type:
        obj_type = self.obj.get_type(varbank)
        if isinstance(obj_type, ListType) and self.member.value == 'length': return IntegerType()
        if not isinstance(obj_type, StructType): raise ParseException(f"Tentativa de acessar membro em um tipo que não é uma struct ('{obj_type}')", self.member)
        if self.member.value not in obj_type.fields: raise ParseException(f"O tipo '{obj_type.name}' não possui um membro chamado '{self.member.value}'", self.member)
        return obj_type.fields[self.member.value]

@dataclass
class FunctionCall(Expression):
    callee: Expression
    arguments: list[Expression]
    def render(self, varbank: VariableBank) -> str:
        if isinstance(self.callee, Value):
            func_name = self.callee.token.value
            if varbank.is_native_function(func_name):
                if func_name == 'readme':
                    if len(self.arguments) != 1: raise ParseException("'readme' espera exatamente um argumento (o prompt)", self.callee.token)
                    return f"readme({self.arguments[0].render(varbank)}, scanner)"
                else:
                    if not self.arguments: raise ParseException(f"Função nativa '{func_name}' chamada sem o objeto alvo.", self.callee.token)
                    obj_expr, method_args = self.arguments[0], self.arguments[1:]
                    obj_code, rendered_args = obj_expr.render(varbank), [arg.render(varbank) for arg in method_args]
                    obj_type = obj_expr.get_type(varbank)
                    type_key = 'list' if isinstance(obj_type, ListType) else 'string'
                    java_method_name = NATIVE_METHOD_MAP.get((type_key, func_name))
                    if java_method_name is None: raise ParseException(f"A função nativa '{func_name}' não pode ser usada com o tipo '{type_key}'", self.callee.token)
                    return f"{obj_code}.{java_method_name}({', '.join(rendered_args)})"
        
        rendered_args = [arg.render(varbank) for arg in self.arguments]
        callee_code = self.callee.render(varbank)
        return f"{callee_code}({', '.join(rendered_args)})"

    def get_type(self, varbank: VariableBank) -> Type:
        if isinstance(self.callee, Value):
            func_name = self.callee.token.value
            if func_name == 'readme': return StringType()
            if varbank.is_native_function(func_name):
                if func_name == 'get':
                    if len(self.arguments) < 1: raise ParseException("'get' precisa de argumentos", self.callee.token)
                    list_type = self.arguments[0].get_type(varbank)
                    if not isinstance(list_type, ListType): raise ParseException(f"'get' só pode ser chamado em listas, não em '{list_type}'", self.callee.token)
                    return list_type.element_type
                if func_name == 'length': return IntegerType()
                if func_name in ['uppercase', 'lowercase', 'substring']: return StringType()
                return VoidType()
            return varbank.get_function_signature(func_name).return_type
        
        if isinstance(self.callee, MemberAccess):
            return self.callee.get_type(varbank)
            
        return VoidType()

@dataclass
class Statement:
    def render(self, varbank: VariableBank) -> str: raise NotImplementedError

@dataclass
class StructDefinition(Statement):
    name: Token
    fields: list[tuple[TypeNode, Token]]
    def render(self, varbank: VariableBank) -> str:
        java_fields = "\n".join([f"    public {type_node.to_java_type()} {field_name.value};" for type_node, field_name in self.fields])
        return f"public static class {self.name.value} {{\n{java_fields}\n}}"

@dataclass
class ExpressionStatement(Statement):
    expression: Expression
    def render(self, varbank: VariableBank) -> str: return self.expression.render(varbank) + ";"

@dataclass
class ListLiteral(Expression):
    elements: list[Expression]
    def render(self, varbank: VariableBank) -> str:
        list_type = self.get_type(varbank)
        if isinstance(list_type.element_type, VoidType): raise ParseException("Não é possível criar uma lista literal vazia sem tipo explícito", Token(TokenType.NONE, '[]', 0, 0))
        java_type = {'IntegerType': 'Integer', 'RationalType': 'Float', 'StringType': 'String', 'BooleanType': 'Boolean'}.get(list_type.element_type.__class__.__name__, list_type.element_type.name if isinstance(list_type.element_type, StructType) else 'Object')
        return f"new java.util.ArrayList<{java_type}>(java.util.Arrays.asList({', '.join([elem.render(varbank) for elem in self.elements])}))"
    def get_type(self, varbank: VariableBank) -> Type: return ListType(self.elements[0].get_type(varbank) if self.elements else VoidType())

@dataclass
class ListAccess(Expression):
    list_expr: Expression; index_expression: Expression
    def render(self, varbank: VariableBank) -> str: return f"{self.list_expr.render(varbank)}.get({self.index_expression.render(varbank)})"
    def get_type(self, varbank: VariableBank) -> Type:
        list_type = self.list_expr.get_type(varbank)
        if isinstance(list_type, ListType): return list_type.element_type
        raise ParseException("Tentativa de acesso por índice em um não-lista", Token(TokenType.NONE, '[]', 0, 0))

@dataclass
class ListAssignmentStatement(Statement):
    list_access: ListAccess; expression: Expression
    def render(self, varbank: VariableBank) -> str:
        list_var_type = self.list_access.list_expr.get_type(varbank)
        assert_type_compatible(list_var_type.element_type, self.expression.get_type(varbank), Token(TokenType.NONE, '[]', 0,0))
        return f"{self.list_access.list_expr.render(varbank)}.set({self.list_access.index_expression.render(varbank)}, {self.expression.render(varbank)});"

@dataclass
class MemberAssignmentStatement(Statement):
    member_access: MemberAccess
    expression: Expression
    def render(self, varbank: VariableBank) -> str:
        expected_type = self.member_access.get_type(varbank)
        actual_type = self.expression.get_type(varbank)
        assert_type_compatible(expected_type, actual_type, self.member_access.member)
        return f"{self.member_access.render(varbank)} = {self.expression.render(varbank)};"

@dataclass
class CreateStatement(Statement):
    type_node: TypeNode; const_or_var: Token; identifier: Token; expression: Expression | None
    def render(self, varbank: VariableBank) -> str:
        expected_type = self.type_node.to_type_object()
        if self.expression: assert_type_compatible(expected_type, self.expression.get_type(varbank), self.identifier, f"Na criação da variável '{self.identifier.value}': ")
        varbank.create(self.identifier.value, self.const_or_var.value == 'constant', expected_type, self.expression is not None)
        parts = ["final" if self.const_or_var.value == 'constant' else "", self.type_node.to_java_type(), self.identifier.value]
        if self.expression: parts.extend(["=", self.expression.render(varbank)])
        elif isinstance(expected_type, (ListType, StructType)): parts.extend(["=", f"new {self.type_node.to_java_type()}()"])
        return " ".join(filter(None, parts)) + ";"

@dataclass
class SetStatement(Statement):
    identifier: Token; expression: Expression
    def render(self, varbank: VariableBank) -> str:
        var = varbank.get(self.identifier.value)
        if var.constant: raise ParseException(f"Não é possível alterar o valor da constante '{self.identifier.value}'", self.identifier)
        assert_type_compatible(var.vartype, self.expression.get_type(varbank), self.identifier, f"Na atribuição para '{self.identifier.value}': ")
        return f"{self.identifier.value} = {self.expression.render(varbank)};"

@dataclass
class ReadmeStatement(Statement):
    target_variable: Token; prompt_expression: Expression
    def render(self, varbank: VariableBank) -> str:
        variable = varbank.get(self.target_variable.value)
        vartype = variable.vartype.__class__
        readme_call = f"readme({self.prompt_expression.render(varbank)}, scanner)"
        if vartype == IntegerType: return f"{self.target_variable.value} = Integer.parseInt({readme_call});"
        if vartype == RationalType: return f"{self.target_variable.value} = Float.parseFloat({readme_call});"
        if vartype == BooleanType: return f"{self.target_variable.value} = Boolean.parseBoolean({readme_call});"
        if vartype == StringType: return f"{self.target_variable.value} = {readme_call};"
        raise ParseException(f"A função 'readme' não pode atribuir a uma variável do tipo '{vartype.__name__}'", self.target_variable)

@dataclass
class ReadStatement(Statement):
    identifier: Token
    def render(self, varbank: VariableBank) -> str:
        vartype = varbank.get(self.identifier.value).vartype.__class__
        if vartype == StringType: return f"if(scanner.hasNextLine()) scanner.nextLine();\n            {self.identifier.value} = scanner.nextLine();"
        method = {IntegerType: "nextInt", RationalType: "nextFloat", BooleanType: "nextBoolean"}.get(vartype)
        if method: return f"{self.identifier.value} = scanner.{method}();"
        raise ParseException(f"Não é possível ler o tipo {vartype}", self.identifier)

@dataclass
class BaseWriteStatement(Statement):
    expression: Expression; newline: bool = False
    def render(self, varbank: VariableBank) -> str: return f"System.out.println({self.expression.render(varbank)});" if self.newline else f"System.out.print({self.expression.render(varbank)});"

class WriteStatement(BaseWriteStatement): __init__ = lambda self, expression: super().__init__(expression, newline=False)
class WriteLnStatement(BaseWriteStatement): __init__ = lambda self, expression: super().__init__(expression, newline=True)

@dataclass
class IfStructure(Statement):
    conditions: list[Expression]; bodies: list[list[Statement]]; else_body: list[list[Statement]] | None
    def render(self, varbank: VariableBank) -> str:
        varbank.start_scope(); code = f"if ({self.conditions[0].render(varbank)}) {{\n" + "\n".join([f"    {stmt.render(varbank)}" for stmt in self.bodies[0]]) + "\n}"
        varbank.end_scope()
        for i, cond in enumerate(self.conditions[1:], 1):
            varbank.start_scope(); code += f" else if ({cond.render(varbank)}) {{\n" + "\n".join([f"    {stmt.render(varbank)}" for stmt in self.bodies[i]]) + "\n}"
            varbank.end_scope()
        if self.else_body is not None: varbank.start_scope(); code += " else {\n" + "\n".join([f"    {stmt.render(varbank)}" for stmt in self.else_body]) + "\n}"; varbank.end_scope()
        return code

@dataclass
class WhileStructure(Statement):
    condition: Expression; body: list[Statement]
    def render(self, varbank: VariableBank) -> str:
        varbank.start_scope(); code = f"while ({self.condition.render(varbank)}) {{\n" + "\n".join([f"    {stmt.render(varbank)}" for stmt in self.body]) + "\n}"; varbank.end_scope()
        return code

@dataclass
class DoWhileStructure(Statement):
    condition: Expression; body: list[Statement]
    def render(self, varbank: VariableBank) -> str:
        varbank.start_scope(); code = "do {\n" + "\n".join([f"    {stmt.render(varbank)}" for stmt in self.body]) + f"\n}} while ({self.condition.render(varbank)});"; varbank.end_scope()
        return code

@dataclass
class ForStructure(Statement):
    loop_variable: Token; iterable_expression: Expression; body: list[Statement]
    def render(self, varbank: VariableBank) -> str:
        iterable_type = self.iterable_expression.get_type(varbank)
        if not isinstance(iterable_type, ListType): raise ParseException(f"O laço 'for' só pode iterar sobre listas, não sobre o tipo '{iterable_type}'", self.loop_variable)
        element_type = iterable_type.element_type
        if isinstance(element_type, StructType):
            java_element_type = element_type.name
        else:
            java_element_type = {'IntegerType': 'Integer', 'RationalType': 'Float', 'StringType': 'String', 'BooleanType': 'Boolean'}.get(element_type.__class__.__name__, 'Object')
        
        varbank.start_scope()
        varbank.create(self.loop_variable.value, True, element_type, True)
        rendered_body = "\n".join([f"    {stmt.render(varbank)}" for stmt in self.body])
        varbank.end_scope()
        return f"for ({java_element_type} {self.loop_variable.value} : {self.iterable_expression.render(varbank)}) {{\n{rendered_body}\n}}"

@dataclass
class FunctionDeclaration(Statement):
    name: Token; params: list[tuple[TypeNode, Token]]; return_type_node: TypeNode; body: list[Statement]
    def render(self, varbank: VariableBank) -> str:
        signature = FunctionSignature([p[0].to_type_object() for p in self.params], self.return_type_node.to_type_object())
        varbank.create_function(self.name.value, signature)
        varbank.start_scope(return_type=signature.return_type)
        java_params = [f"{p[0].to_java_type()} {p[1].value}" for p in self.params]
        for type_node, name_token in self.params: varbank.create(name_token.value, False, type_node.to_type_object(), True)
        rendered_body = "\n".join([f"    {stmt.render(varbank)}" for stmt in self.body])
        varbank.end_scope()
        return f"public static {self.return_type_node.to_java_type()} {self.name.value}({', '.join(java_params)}) {{\n{rendered_body}\n}}"

@dataclass
class ReturnStatement(Statement):
    return_token: Token; expression: Expression | None
    def render(self, varbank: VariableBank) -> str:
        expected_return_type = varbank.get_current_return_type()
        if expected_return_type is None: raise ParseException("Declaração 'return' encontrada fora de uma função", self.return_token)
        actual_return_type = self.expression.get_type(varbank) if self.expression else VoidType()
        assert_type_compatible(expected_return_type, actual_return_type, self.return_token, "Tipo de retorno incompatível. ")
        return f"return {self.expression.render(varbank)};" if self.expression else "return;"

class Parser:
    def __init__(self, tokens: list[Token]): 
        self.tokens, self.pos = tokens, 0
        self.varbank = VariableBank()
    @property
    def current_token(self) -> Token: return self.tokens[self.pos]
    def advance(self): self.pos += 1
    def consume(self, expected_type: TokenType):
        if self.current_token.token_type == expected_type: token = self.current_token; self.advance(); return token
        raise ParseException(f"Esperava o token {expected_type.name}, mas encontrou {self.current_token.token_type.name}", self.current_token)
    def parse(self) -> list[Statement]:
        declarations = []
        while self.current_token.token_type != TokenType.EOF:
            if self.current_token.token_type == TokenType.CREATE and self.pos + 1 < len(self.tokens) and self.tokens[self.pos+1].token_type == TokenType.TYPE_KEYWORD:
                declarations.append(self.parse_struct_definition())
            elif self.current_token.token_type == TokenType.FUNCTION:
                declarations.append(self.parse_function_declaration())
            else:
                declarations.append(self.parse_statement())
        return declarations
    def parse_block(self) -> list[Statement]:
        statements = []; terminators = {TokenType.END, TokenType.ELSE, TokenType.ELIF, TokenType.WHILE, TokenType.EOF}
        while self.current_token.token_type not in terminators: statements.append(self.parse_statement())
        return statements
    def parse_statement(self) -> Statement:
        token_type = self.current_token.token_type
        if token_type == TokenType.IDENTIFIER and self.current_token.value == 'readme' and self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].token_type == TokenType.IDENTIFIER:
            stmt = self.parse_readme_statement()
        elif token_type == TokenType.CREATE: stmt = self.parse_create_statement()
        elif token_type == TokenType.SET: stmt = self.parse_set_statement()
        elif token_type == TokenType.READ: stmt = self.parse_read_statement()
        elif token_type == TokenType.WRITE: stmt = self.parse_write_statement()
        elif token_type == TokenType.WRITELN: stmt = self.parse_writeln_statement()
        elif token_type == TokenType.IF: return self.parse_if_structure()
        elif token_type == TokenType.FOR: return self.parse_for_structure()
        elif token_type == TokenType.WHILE: return self.parse_while_structure()
        elif token_type == TokenType.DO: return self.parse_do_while_structure()
        elif token_type == TokenType.RETURN: stmt = self.parse_return_statement()
        else: stmt = ExpressionStatement(self.parse_expression())
        self.consume(TokenType.SEMICOLON)
        return stmt
    def parse_readme_statement(self) -> ReadmeStatement:
        self.consume(TokenType.IDENTIFIER); target_variable = self.consume(TokenType.IDENTIFIER); prompt_expression = self.parse_expression()
        return ReadmeStatement(target_variable, prompt_expression)
    def parse_for_structure(self) -> ForStructure:
        self.consume(TokenType.FOR); loop_variable = self.consume(TokenType.IDENTIFIER); self.consume(TokenType.IN); iterable_expression = self.parse_expression(); self.consume(TokenType.DO)
        body = self.parse_block(); self.consume(TokenType.END)
        return ForStructure(loop_variable, iterable_expression, body)
    def parse_struct_definition(self) -> StructDefinition:
        self.consume(TokenType.CREATE); self.consume(TokenType.TYPE_KEYWORD); name = self.consume(TokenType.IDENTIFIER); self.consume(TokenType.LPAREN)
        fields = []
        while self.current_token.token_type != TokenType.RPAREN:
            type_node = self.parse_type()
            field_name = self.consume(TokenType.IDENTIFIER)
            fields.append((type_node, field_name))
            if self.current_token.token_type != TokenType.COMMA: break
            self.consume(TokenType.COMMA)
        self.consume(TokenType.RPAREN); self.consume(TokenType.SEMICOLON)
        field_types = {field_name.value: type_node.to_type_object() for type_node, field_name in fields}
        self.varbank.create_struct(name.value, field_types)
        return StructDefinition(name, fields)
    def parse_type(self) -> TypeNode:
        type_token = self.current_token
        if type_token.token_type == TokenType.TYPE and type_token.value == 'list':
            self.consume(TokenType.TYPE)
            self.consume(TokenType.LESS); element_type = self.parse_type(); self.consume(TokenType.GREATER)
            return ListTypeNode(element_type)
        if type_token.token_type not in {TokenType.TYPE, TokenType.IDENTIFIER}: raise ParseException("Esperava um nome de tipo", type_token)
        self.advance()
        return SimpleTypeNode(type_token, self.varbank)
    def parse_function_declaration(self) -> FunctionDeclaration:
        self.consume(TokenType.FUNCTION); name = self.consume(TokenType.IDENTIFIER); self.consume(TokenType.LPAREN)
        params = []
        if self.current_token.token_type != TokenType.RPAREN:
            param_type = self.parse_type(); param_name = self.consume(TokenType.IDENTIFIER); params.append((param_type, param_name))
            while self.current_token.token_type == TokenType.COMMA:
                self.consume(TokenType.COMMA); param_type = self.parse_type(); param_name = self.consume(TokenType.IDENTIFIER); params.append((param_type, param_name))
        self.consume(TokenType.RPAREN)
        return_type_node = SimpleTypeNode(Token(TokenType.TYPE, 'void', 0, 0), self.varbank)
        if self.current_token.token_type == TokenType.ARROW: self.consume(TokenType.ARROW); return_type_node = self.parse_type()
        body = self.parse_block(); self.consume(TokenType.END)
        return FunctionDeclaration(name, params, return_type_node, body)
    def parse_return_statement(self) -> ReturnStatement:
        return_token = self.consume(TokenType.RETURN)
        return ReturnStatement(return_token, self.parse_expression() if self.current_token.token_type != TokenType.SEMICOLON else None)
    def parse_create_statement(self):
        self.consume(TokenType.CREATE); type_node = self.parse_type(); const_or_var = self.consume(TokenType.VARTYPE); identifier = self.consume(TokenType.IDENTIFIER)
        expression = None
        if self.current_token.token_type != TokenType.SEMICOLON:
            if self.current_token.token_type == TokenType.TO: self.consume(TokenType.TO)
            expression = self.parse_expression()
        return CreateStatement(type_node, const_or_var, identifier, expression)
    def parse_set_statement(self):
        self.consume(TokenType.SET); target_expr = self.parse_expression()
        self.consume(TokenType.TO); value_expression = self.parse_expression()
        if isinstance(target_expr, MemberAccess): return MemberAssignmentStatement(target_expr, value_expression)
        if isinstance(target_expr, ListAccess): return ListAssignmentStatement(target_expr, value_expression)
        if isinstance(target_expr, Value) and target_expr.token.token_type == TokenType.IDENTIFIER: return SetStatement(target_expr.token, value_expression)
        raise ParseException("Alvo de atribuição inválido", self.current_token)
    def parse_read_statement(self): return ReadStatement(self.consume(TokenType.READ) and self.consume(TokenType.IDENTIFIER))
    def parse_write_statement(self): return WriteStatement(self.consume(TokenType.WRITE) and self.parse_expression())
    def parse_writeln_statement(self): return WriteLnStatement(self.consume(TokenType.WRITELN) and self.parse_expression())
    def parse_if_structure(self):
        self.consume(TokenType.IF); conditions = [self.parse_expression()]; self.consume(TokenType.THEN)
        bodies = [self.parse_block()]; else_body = None
        while self.current_token.token_type == TokenType.ELIF: self.consume(TokenType.ELIF); conditions.append(self.parse_expression()); self.consume(TokenType.THEN); bodies.append(self.parse_block())
        if self.current_token.token_type == TokenType.ELSE: self.consume(TokenType.ELSE); else_body = self.parse_block()
        self.consume(TokenType.END); return IfStructure(conditions, bodies, else_body)
    def parse_while_structure(self):
        self.consume(TokenType.WHILE); condition = self.parse_expression(); self.consume(TokenType.DO)
        body = self.parse_block(); self.consume(TokenType.END); return WhileStructure(condition, body)
    def parse_do_while_structure(self):
        self.consume(TokenType.DO); body = self.parse_block(); self.consume(TokenType.WHILE)
        condition = self.parse_expression(); self.consume(TokenType.END); return DoWhileStructure(condition, body)
    def parse_list_literal(self) -> ListLiteral:
        self.consume(TokenType.LBRACKET); elements = []
        if self.current_token.token_type != TokenType.RBRACKET:
            elements.append(self.parse_expression())
            while self.current_token.token_type == TokenType.COMMA: self.consume(TokenType.COMMA); elements.append(self.parse_expression())
        self.consume(TokenType.RBRACKET); return ListLiteral(elements)
    def parse_call_expression(self, callee: Expression) -> FunctionCall:
        self.consume(TokenType.LPAREN); arguments = []
        if self.current_token.token_type != TokenType.RPAREN:
            arguments.append(self.parse_expression())
            while self.current_token.token_type == TokenType.COMMA: self.consume(TokenType.COMMA); arguments.append(self.parse_expression())
        self.consume(TokenType.RPAREN); return FunctionCall(callee, arguments)
    PRECEDENCE = {TokenType.OR: 1, TokenType.AND: 2, TokenType.EQUAL: 3, TokenType.NOT_EQUAL: 3, TokenType.LESS: 3, TokenType.GREATER: 3, TokenType.LESS_EQUAL: 3, TokenType.GREATER_EQUAL: 3, TokenType.ADDITION: 4, TokenType.SUBTRACTION: 4, TokenType.MULTIPLICATION: 5, TokenType.DIVISION: 5, TokenType.MODULUS: 5}
    def get_precedence(self, token_type: TokenType): return self.PRECEDENCE.get(token_type, 0)
    def parse_primary_expression(self):
        token = self.current_token
        if token.token_type in LITERAL_AND_IDENTIFIER_TOKENS: self.advance(); return Value(token)
        if token.token_type == TokenType.LPAREN: self.consume(TokenType.LPAREN); expr = self.parse_expression(); self.consume(TokenType.RPAREN); return expr
        if token.token_type == TokenType.LBRACKET: return self.parse_list_literal()
        raise ParseException("Expressão primária inválida", token)
    def parse_expression(self, precedence=0):
        left_expr = self.parse_primary_expression()
        while self.pos < len(self.tokens):
            op_token = self.current_token
            if op_token.token_type == TokenType.LPAREN:
                left_expr = self.parse_call_expression(left_expr)
                continue
            if op_token.token_type == TokenType.DOT:
                self.consume(TokenType.DOT)
                member_name = self.consume(TokenType.IDENTIFIER)
                left_expr = MemberAccess(left_expr, member_name)
                continue
            if op_token.token_type == TokenType.LBRACKET:
                self.consume(TokenType.LBRACKET)
                index_expr = self.parse_expression()
                self.consume(TokenType.RBRACKET)
                left_expr = ListAccess(left_expr, index_expr)
                continue
            op_precedence = self.get_precedence(op_token.token_type)
            if op_precedence <= precedence: break
            self.advance()
            right_expr = self.parse_expression(op_precedence)
            left_expr = BinOp(left_expr, op_token, right_expr)
        return left_expr
