from dataclasses import dataclass, field
from util.token import Token, TokenType
from render import (Type, VariableBank, FunctionType, IntegerType, RationalType, 
                    StringType, BooleanType, ListType, StructType, VoidType)

class ProseException(Exception):
    def __init__(self, message, token):
        line = token.line if token else 'desconhecida'
        super().__init__(f"Erro na linha {line}: {message}")
        self.token = token

class ParseException(ProseException): pass
class RuntimeException(ProseException): pass

def assert_type_compatible(expected_type: Type, actual_type: Type, token: Token, message_prefix=""):
    if not (expected_type == actual_type):
        raise ParseException(f"{message_prefix}Esperava o tipo '{expected_type}', mas obteve '{actual_type}'", token)

LITERAL_AND_IDENTIFIER_TOKENS = {TokenType.BOOLEAN, TokenType.RATIONAL, TokenType.INTEGER, TokenType.STRING, TokenType.IDENTIFIER}
NATIVE_METHOD_MAP = {('list', 'length'): 'size', ('list', 'add'): 'add', ('list', 'get'): 'get', ('list', 'remove'): 'remove', ('string', 'uppercase'): 'toUpperCase', ('string', 'lowercase'): 'toLowerCase', ('string', 'substring'): 'substring'}

@dataclass
class ModuleType(Type):
    name: str
    def __repr__(self): return f"module<{self.name}>"

@dataclass
class TypeNode:
    def to_type_object(self) -> Type: raise NotImplementedError

@dataclass
class SimpleTypeNode(TypeNode):
    type_token: Token
    varbank: VariableBank 
    def to_type_object(self) -> Type:
        type_map = {'integer': IntegerType(), 'rational': RationalType(), 'string': StringType(), 'boolean': BooleanType(), 'void': VoidType()}
        if self.type_token.value in type_map: return type_map[self.type_token.value]
        return self.varbank.get_struct_type(self.type_token.value)
    def __repr__(self): return self.type_token.value

@dataclass
class ListTypeNode(TypeNode):
    element_type: TypeNode
    def to_type_object(self) -> Type: return ListType(self.element_type.to_type_object())
    def __repr__(self): return f"list<{self.element_type}>"

@dataclass
class FunctionTypeNode(TypeNode):
    param_types: list[TypeNode]
    return_type: TypeNode
    def to_type_object(self) -> Type:
        param_type_objects = [pt.to_type_object() for pt in self.param_types]
        return_type_object = self.return_type.to_type_object()
        return FunctionType(param_type_objects, return_type_object)
    def __repr__(self): return f"function(...)"

@dataclass
class Expression:
    def get_type(self, varbank: VariableBank) -> Type: raise NotImplementedError

@dataclass
class Value(Expression):
    token: Token
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
    def get_type(self, varbank: VariableBank) -> Type:
        left_type, right_type = self.left.get_type(varbank), self.right.get_type(varbank)
        if self.op.token_type in {TokenType.ADDITION, TokenType.SUBTRACTION, TokenType.MULTIPLICATION, TokenType.DIVISION, TokenType.MODULUS}:
            if isinstance(left_type, StringType) and self.op.token_type == TokenType.ADDITION: return StringType()
            if isinstance(left_type, (IntegerType, RationalType)) and isinstance(right_type, (IntegerType, RationalType)): return RationalType() if isinstance(left_type, RationalType) or isinstance(right_type, RationalType) else IntegerType()
            raise ParseException(f"Operador '{self.op.value}' inválido para os tipos {left_type} e {right_type}", self.op)
        if self.op.token_type in {TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.GREATER, TokenType.LESS, TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL, TokenType.AND, TokenType.OR}: return BooleanType()
        raise ParseException(f"Operador desconhecido ou inválido '{self.op.value}'", self.op)

@dataclass
class MemberAccess(Expression):
    obj: Expression
    member: Token
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
        callee_type = self.callee.get_type(varbank)
        if isinstance(callee_type, FunctionType): return callee_type.return_type
        raise ParseException(f"Expressão do tipo '{callee_type}' não é chamável.", self.callee.token if isinstance(self.callee, Value) else Token(TokenType.NONE,'',0,0))

@dataclass
class Statement: pass

@dataclass
class ImportStatement(Statement):
    module_path: Token
    imported_names: list[Token] | None = field(default=None)

@dataclass
class StructDefinition(Statement):
    name: Token
    fields: list[tuple[TypeNode, Token]]

@dataclass
class ExpressionStatement(Statement):
    expression: Expression

@dataclass
class ListLiteral(Expression):
    elements: list[Expression]
    def get_type(self, varbank: VariableBank) -> Type: return ListType(self.elements[0].get_type(varbank) if self.elements else VoidType())

@dataclass
class ListAccess(Expression):
    list_expr: Expression; index_expression: Expression
    def get_type(self, varbank: VariableBank) -> Type:
        list_type = self.list_expr.get_type(varbank)
        if isinstance(list_type, ListType): return list_type.element_type
        raise ParseException("Tentativa de acesso por índice em um não-lista", Token(TokenType.NONE, '[]', 0, 0))

@dataclass
class ListAssignmentStatement(Statement):
    list_access: ListAccess; expression: Expression

@dataclass
class MemberAssignmentStatement(Statement):
    member_access: MemberAccess; expression: Expression

@dataclass
class CreateStatement(Statement):
    type_node: TypeNode; const_or_var: Token; identifier: Token; expression: Expression | None

@dataclass
class SetStatement(Statement):
    identifier: Token; expression: Expression

@dataclass
class ReadmeStatement(Statement):
    target_variable: Token; prompt_expression: Expression

@dataclass
class ReadStatement(Statement):
    identifier: Token

@dataclass
class BaseWriteStatement(Statement):
    expression: Expression; newline: bool = False

class WriteStatement(BaseWriteStatement): __init__ = lambda self, expression: super().__init__(expression, newline=False)
class WriteLnStatement(BaseWriteStatement): __init__ = lambda self, expression: super().__init__(expression, newline=True)

@dataclass
class IfStructure(Statement):
    conditions: list[Expression]; bodies: list[list[Statement]]; else_body: list[list[Statement]] | None

@dataclass
class WhileStructure(Statement):
    condition: Expression; body: list[Statement]

@dataclass
class DoWhileStructure(Statement):
    condition: Expression; body: list[Statement]

@dataclass
class ForStructure(Statement):
    loop_variable: Token; iterable_expression: Expression; body: list[Statement]

@dataclass
class FunctionDeclaration(Statement):
    name: Token; params: list[tuple[TypeNode, Token]]; return_type_node: TypeNode; body: list[Statement]

@dataclass
class ReturnStatement(Statement):
    return_token: Token; expression: Expression | None
