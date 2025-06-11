from enum import Enum, auto
from dataclasses import dataclass, field

class Type:
    def __eq__(self, other):
        if isinstance(self, RationalType) and isinstance(other, IntegerType): return True
        if isinstance(self, ListType) and isinstance(other, ListType):
            if self.element_type is None or other.element_type is None: return True
            if isinstance(self.element_type, VoidType) or isinstance(other.element_type, VoidType): return True
            return self.element_type == other.element_type
        if isinstance(self, StructType) and isinstance(other, StructType):
            return self.name == other.name
        return isinstance(other, self.__class__)

    def __repr__(self):
        return self.__class__.__name__.replace("Type", "").lower()

class IntegerType(Type): pass
class RationalType(Type): pass
class StringType(Type): pass
class BooleanType(Type): pass
class VoidType(Type): pass

@dataclass
class ListType(Type):
    element_type: Type
    def __repr__(self): return f"list<{self.element_type}>"

@dataclass
class StructType(Type):
    name: str
    fields: dict[str, Type] = field(default_factory=dict)
    def __repr__(self): return self.name

@dataclass
class FunctionSignature:
    param_types: list[Type]
    return_type: Type

class Variable:
    def __init__(self, constant: bool, vartype: Type, value):
        self.constant = constant
        self.vartype = vartype
        self.value = value

class VariableBank:
    def __init__(self):
        self.scopes: list[dict[str, Variable]] = [{}]
        self.functions: dict[str, FunctionSignature] = {}
        self.structs: dict[str, StructType] = {}
        self.scope_metadata: list[dict] = [{'return_type': None}]
        self.native_functions: dict[str, FunctionSignature] = {
            "length": FunctionSignature(param_types=[ListType(None)], return_type=IntegerType()),
            "add": FunctionSignature(param_types=[ListType(None), None], return_type=VoidType()),
            "get": FunctionSignature(param_types=[ListType(None), IntegerType()], return_type=None),
            "remove": FunctionSignature(param_types=[ListType(None), IntegerType()], return_type=VoidType()),
            "uppercase": FunctionSignature(param_types=[StringType()], return_type=StringType()),
            "lowercase": FunctionSignature(param_types=[StringType()], return_type=StringType()),
            "substring": FunctionSignature(param_types=[StringType(), IntegerType(), IntegerType()], return_type=StringType()),
            "readme": FunctionSignature(param_types=[StringType()], return_type=StringType()),
        }

    def start_scope(self, return_type: Type = None) -> None:
        self.scopes.append({})
        parent_return_type = self.get_current_return_type()
        self.scope_metadata.append({'return_type': return_type if return_type is not None else parent_return_type})

    def end_scope(self) -> None:
        if len(self.scopes) > 1: self.scopes.pop()
        if len(self.scope_metadata) > 1: self.scope_metadata.pop()
        
    def get_current_return_type(self) -> Type | None:
        if not self.scope_metadata: return None
        return self.scope_metadata[-1]['return_type']

    def create(self, name: str, constant: bool, vartype: Type, value):
        if name in self.scopes[-1]: raise Exception(f"Redeclaração da variável '{name}' no mesmo escopo")
        self.scopes[-1][name] = Variable(constant, vartype, value)

    def get(self, name: str) -> Variable:
        for scope in reversed(self.scopes):
            if name in scope: return scope[name]
        raise Exception(f"Nenhuma variável com o nome '{name}' foi declarada")

    def create_function(self, name: str, signature: FunctionSignature):
        if name in self.functions or name in self.native_functions: raise Exception(f"Redeclaração da função '{name}'")
        self.functions[name] = signature
    
    def create_struct(self, name: str, fields: dict[str, Type]):
        if name in self.structs: raise Exception(f"Redeclaração do tipo '{name}'")
        self.structs[name] = StructType(name, fields)
    
    def get_struct_type(self, name: str) -> StructType:
        if name in self.structs: return self.structs[name]
        raise Exception(f"Tipo desconhecido '{name}'")

    def is_native_function(self, name: str) -> bool:
        return name in self.native_functions

    def get_function_signature(self, name: str) -> FunctionSignature:
        if name in self.functions: return self.functions[name]
        if name in self.native_functions: return self.native_functions[name]
        raise Exception(f"Tentativa de chamar função não declarada '{name}'")
