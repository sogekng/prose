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
        if isinstance(self, FunctionType) and isinstance(other, FunctionType):
            return self.return_type == other.return_type and self.param_types == other.param_types
        return isinstance(other, self.__class__)

    def __repr__(self):
        return self.__class__.__name__.replace("Type", "").lower()

class IntegerType(Type): pass
class RationalType(Type): pass
class StringType(Type): pass
class BooleanType(Type): pass
class VoidType(Type): pass


@dataclass
class ModuleType(Type):
    name: str
    def __repr__(self): return f"module<{self.name}>"

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
class FunctionType(Type):
    param_types: list[Type]
    return_type: Type
    def __repr__(self):
        params = ", ".join(map(str, self.param_types))
        return f"function({params}) -> {self.return_type}"

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
    def __init__(self, parent=None):
        self.variables: dict[str, Variable] = {}
        self.parent = parent
        
        if parent is None:
            self.functions: dict[str, FunctionSignature] = {}
            self.structs: dict[str, StructType] = {}
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

    def create(self, name: str, constant: bool, vartype: Type, value):
        if name in self.variables: raise Exception(f"Redeclaração da variável '{name}' no mesmo escopo")
        self.variables[name] = Variable(constant, vartype, value)

    def get(self, name: str) -> Variable:
        if name in self.variables: return self.variables[name]
        if self.parent: return self.parent.get(name)
        raise Exception(f"Nenhuma variável com o nome '{name}' foi declarada")

    def set(self, name: str, value):
        if name in self.variables:
            if self.variables[name].constant: raise Exception(f"Não é possível alterar o valor da constante '{name}'")
            self.variables[name].value = value
            return
        if self.parent:
            self.parent.set(name, value)
            return
        raise Exception(f"Nenhuma variável com o nome '{name}' foi declarada")

    def get_global_scope(self):
        scope = self
        while scope.parent:
            scope = scope.parent
        return scope

    def create_function(self, name: str, signature: FunctionSignature):
        globals = self.get_global_scope()
        if name in globals.functions or name in globals.native_functions: raise Exception(f"Redeclaração da função '{name}'")
        globals.functions[name] = signature
    
    def create_struct(self, name: str, fields: dict[str, Type]):
        globals = self.get_global_scope()
        if name in globals.structs: raise Exception(f"Redeclaração do tipo '{name}'")
        globals.structs[name] = StructType(name, fields)
    
    def get_struct_type(self, name: str) -> StructType:
        globals = self.get_global_scope()
        if name in globals.structs: return globals.structs[name]
        raise Exception(f"Tipo desconhecido '{name}'")
    
    def is_native_function(self, name: str) -> bool:
        globals = self.get_global_scope()
        return name in globals.native_functions

    def get_function_signature(self, name: str) -> FunctionSignature:
        globals = self.get_global_scope()
        if name in globals.functions: return globals.functions[name]
        if name in globals.native_functions: return globals.native_functions[name]
        raise Exception(f"Tentativa de chamar função não declarada '{name}'")