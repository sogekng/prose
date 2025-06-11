from enum import Enum, auto

class VariableType(Enum):
    STRING   = auto()
    INTEGER  = auto()
    RATIONAL = auto()
    BOOLEAN  = auto()
    LIST     = auto()

class Variable:
    def __init__(self, constant: bool, vartype: VariableType, value):
        self.constant = constant
        self.vartype = vartype
        self.value = value

class VariableBank:
    def __init__(self):
        self.scopes: list[dict[str, Variable]] = [{}]
        self.functions: dict[str, int] = {}

    def start_scope(self) -> None:
        self.scopes.append({})

    def end_scope(self) -> None:
        self.scopes.pop()

    def create(self, name: str, constant: bool, vartype: VariableType, value):
        if name in self.scopes[-1]:
            raise Exception(f"Redeclaração da variável '{name}' no mesmo escopo")
        self.scopes[-1][name] = Variable(constant, vartype, value)

    def exists(self, name: str) -> bool:
        for scope in reversed(self.scopes):
            if name in scope:
                return True
        return False

    def get(self, name: str) -> Variable:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise Exception(f"Nenhuma variável com o nome '{name}' foi declarada")

    def redefine(self, name: str, value) -> None:
        variable = self.get(name)
        if variable.constant:
            raise Exception(f"Não é possível alterar o valor da constante '{name}'")
        variable.value = value

    def create_function(self, name: str, num_params: int):
        if name in self.functions:
            raise Exception(f"Redeclaração da função '{name}'")
        self.functions[name] = num_params

    def get_function_arity(self, name: str) -> int:
        if name not in self.functions:
            raise Exception(f"Tentativa de chamar função não declarada '{name}'")
        return self.functions[name]