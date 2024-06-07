from enum import Enum, auto


class VariableType(Enum):
    STRING = auto()
    INTEGER = auto()
    RATIONAL = auto()
    BOOLEAN = auto()


class Variable:
    def __init__(self, constant: bool, vartype: VariableType, value):
        self.constant = constant
        self.vartype = vartype
        self.value = value


class VariableBank:
    def __init__(self):
        self._bank: dict[str, bool] = {}

    def create(self, name: str, constant: bool, vartype: VariableType, value):
        self._bank[name] = Variable(constant, vartype, value)

    def exists(self, name: str) -> bool:
        return name in self._bank

    def is_constant(self, name: str) -> bool:
        return self.get(name).constant

    # NOTE(volatus): "set" conflicts with the built-in function set()
    def redefine(self, name: str, value) -> None:
        if not self.exists(name):
            raise Exception(f"No variable named '{name}' was declared")

        if self.is_constant(name):
            raise Exception(f"Unable to change value of constant variable '{name}'")

        self._bank[name].value = value

    def get(self, name: str) -> Variable:
        if not self.exists(name):
            raise Exception(f"No variable named '{token.value}' was declared")

        return self._bank[name]
