from dataclasses import dataclass
import re

from util.token import TokenType, STRUCTURE_TOKENS, LITERAL_TOKENS, INVALID_EXPRESSION_TOKENS
from render import VariableBank, VariableType, Variable


# NOTE(volatus): these exist because Treesitter is stupid
OPEN_BRACKET = "{"
CLOSE_BRACKET = "}"


def validate_expression(tokens: list, varbank: VariableBank) -> None:
    for token in tokens:
        if token.token_type in INVALID_EXPRESSION_TOKENS:
            raise Exception(f"Invalid token found in expression: '{token}'")

        if token.token_type == TokenType.IDENTIFIER:
            if not varbank.exists(token.value):
                raise Exception(f"No variable named '{token.value}' was declared")

            if varbank.get(token.value).value is None:
                raise Exception(f"Variable declared but unvalued: '{token.value}'")


def lang_type_to_java_type(lang_type: str) -> str:
    if lang_type == VariableType.STRING:
        return "String"
    elif lang_type == VariableType.INTEGER:
        return "int"
    elif lang_type == VariableType.RATIONAL:
        return "float"
    elif lang_type == VariableType.BOOLEAN:
        return "boolean"
    else:
        raise Exception(f"Uknown lang type '{lang_type}'")


def render_expression(tokens: list) -> str:
    return ' '.join([token.value for token in tokens])


@dataclass
class Branch:
    condition_tokens: list
    content_tokens: list

    def __repr__(self) -> str:
        condition = ''
        content = ''

        if self.condition_tokens:
            condition = f"({', '.join([repr(token) for token in self.condition_tokens])})"

        if self.content_tokens:
            content = f"[{', '.join([repr(token) for token in self.content_tokens])}]"

        return f"{condition}=>{content}"


@dataclass
class StructureGroup:
    structure_type: TokenType
    branches: list[Branch]

    def __repr__(self) -> str:
        return f"SG::{self.structure_type}{{{', '.join([repr(branch) for branch in self.branches])}}}"


@dataclass
class StatementGroup:
    tokens: list

    def __repr__(self) -> str:
        return f"({', '.join([repr(token) for token in self.tokens])})"


@dataclass
class Statement:
    tokens: list

    def __repr__(self) -> str:
        return f"<{', '.join([repr(token) for token in self.tokens])}>"

    def validate_syntax(self) -> bool:
        return True

    def render(self, varbank: VariableBank) -> str:
        return ""


class CreateStatement(Statement):
    def __repr__(self) -> str:
        components = []

        if len(self.tokens) >= 1:
            components = self.tokens[1:]

        return f"Create::<{', '.join([repr(token) for token in components])}>"

    def validate_syntax(self) -> bool:
        return (
            len(self.tokens) >= 4
            and self.tokens[0].token_type == TokenType.CREATE
            and self.tokens[1].token_type == TokenType.TYPE
            and self.tokens[2].token_type == TokenType.VARTYPE
            and self.tokens[3].token_type == TokenType.IDENTIFIER
        )

    def render(self, varbank: VariableBank) -> str:
        var_type_str: str = self.tokens[1].value
        is_constant: bool = self.tokens[2].value == 'constant'
        var_name: str = self.tokens[3].value
        var_value = self.tokens[4:] if len(self.tokens) > 4 else None

        var_type: VariableType

        if var_type_str == 'string':
            var_type = VariableType.STRING
        elif var_type_str == 'integer':
            var_type = VariableType.INTEGER
        elif var_type_str == 'rational':
            var_type = VariableType.RATIONAL
        elif var_type_str == 'boolean':
            var_type = VariableType.BOOLEAN
        else:
            raise Exception(f"Unexpected variable type '{var_type_str}'")

        varbank.create(var_name, is_constant, var_type, var_value)

        java_components = []

        if is_constant:
            java_components.append('final')

        java_components.append(lang_type_to_java_type(var_type))
        java_components.append(var_name)

        if var_value is not None:
            java_components.append('=')
            java_components.append(render_expression(var_value))

        return f"{' '.join(java_components)};"


class WriteStatement(Statement):
    def validate_syntax(self) -> bool:
        return (
            len(self.tokens) >= 2
            and self.tokens[0].token_type == TokenType.WRITE
            and self.tokens[1].token_type == TokenType.STRING
        )

    def render(self, varbank: VariableBank) -> str:
        expression_tokens = self.tokens[1:]
        validate_expression(expression_tokens, varbank)
        return f"System.out.printf({', '.join([token.value for token in expression_tokens])});"


class SetStatement(Statement):
    def validate_syntax(self) -> bool:
        return (
            len(self.tokens) >= 4
            and self.tokens[0].token_type == TokenType.SET
            and self.tokens[1].token_type == TokenType.IDENTIFIER
            and self.tokens[2].token_type == TokenType.TO
        )

    def render(self, varbank: VariableBank) -> str:
        expression_tokens = self.tokens[3:]
        validate_expression(expression_tokens, varbank)

        var_name = self.tokens[1].value

        varbank.redefine(var_name, expression_tokens)

        return f"{var_name} = {render_expression(expression_tokens)};"


class ReadStatement(Statement):
    def validate_syntax(self) -> bool:
        return (
            len(self.tokens) == 2 and
            self.tokens[0].token_type == TokenType.READ and
            self.tokens[1].token_type == TokenType.IDENTIFIER
        )

    def render(self, varbank: VariableBank) -> str:
        var_name: str = self.tokens[1].value

        variable: Variable = varbank.get(var_name)
        varbank.redefine(var_name, True)

        method: str

        if variable.vartype == VariableType.STRING:
            method = "nextLine"
        elif variable.vartype == VariableType.INTEGER:
            method = "nextInt"
        elif variable.vartype == VariableType.RATIONAL:
            method = "nextFloat"
        elif variable.vartype == VariableType.BOOLEAN:
            method = "nextBoolean"

        return f"{var_name} = scanner.{method}();"


@dataclass
class Structure:
    branches: list[Branch]

    def __repr__(self) -> str:
        return f"STRUCT::[{', '.join([repr(branch) for branch in self.branches])}]"

    def render(self, varbank: VariableBank) -> list[str]:
        return []

    def render_branch(self, varbank: VariableBank, i: int) -> list[str]:
        lines = []

        for item in self.branches[i].content_tokens:
            if isinstance(item, Statement):
                lines.append(item.render(varbank))
            elif isinstance(item, Structure):
                lines.extend(item.render(varbank))
            else:
                raise Exception(f"Unexpected branch item found {item}")

        return lines


class IfStructure(Structure):
    def render(self, varbank: VariableBank) -> list[str]:
        lines = []

        lines.append(f"if ({render_expression(self.branches[0].condition_tokens)}) {OPEN_BRACKET}")
        lines.extend(self.render_branch(varbank, 0))

        for i in range(1, len(self.branches)):
            branch = self.branches[i]

            if not branch.condition_tokens:
                lines.append(f"{CLOSE_BRACKET} else {OPEN_BRACKET}")
            else:
                lines.append(f"{CLOSE_BRACKET} else if ({render_expression(branch.condition_tokens)}) {OPEN_BRACKET}")

            lines.extend(self.render_branch(varbank, i))

        lines.append(CLOSE_BRACKET)

        return lines


class WhileStructure(Structure):
    def render(self, varbank: VariableBank) -> list[str]:
        lines = []

        lines.append(f"while ({render_expression(self.branches[0].condition_tokens)}) {OPEN_BRACKET}")
        lines.extend(self.render_branch(varbank, 0))
        lines.append(CLOSE_BRACKET)

        return lines


class DoWhileStructure(Structure):
    def render(self, varbank: VariableBank) -> list[str]:
        lines = []

        lines.append(f"do {OPEN_BRACKET}")
        lines.extend(self.render_branch(varbank, 0))
        lines.append(f"{CLOSE_BRACKET} while ({render_expression(self.branches[0].condition_tokens)});")

        return lines


def find_variables_in_condition(variables, condition):
    pattern = re.compile(r'\b\w+\b')

    potential_vars = pattern.findall(condition)

    actual_vars = [var for var in potential_vars if var in variables]

    return actual_vars


def evaluate_condition(condition, variables, executor):
    try:
        identifiers = re.findall(r'\b\w+\b', condition)

        for i, var in enumerate(variables):
            for j, identifier in enumerate(identifiers):
                if var == identifiers[j]:
                    variable = variables[i]
                    value = executor.get().get(identifier)[2]
                    # value = identifiers[j + 1]

                    condition = condition.replace(variable, value)

        result = eval(condition)
        return result
    except Exception as e:
        print(f"Erro na condição: {e}")
        return False


def evaluate_expression(tokens, variables):
    def get_value(token):
        if token.token_type == TokenType.IDENTIFIER:
            if token.value in variables:
                return str(variables[token.value][2])
            else:
                raise ValueError(f"Undefined variable: {token.value}")
        elif token.token_type in LITERAL_TOKENS:
            return str(token.value)
        return str(token.value)

    expression_parts = [get_value(token) for token in tokens]
    expression = ''.join(expression_parts)

    return expression


def find_next_token(tokens, token_type, offset):
    for i in range(offset, len(tokens)):
        if tokens[i].token_type == token_type:
            return i

    return -1


def find_matching_end(tokens, offset):
    pair_count = 0

    for i in range(offset, len(tokens)):
        if tokens[i].token_type in STRUCTURE_TOKENS:
            pair_count += 1
        elif tokens[i].token_type == TokenType.END:
            pair_count -= 1

        if pair_count == 0:
            return i

    return -1


def group_statement(tokens: list, offset: int) -> StatementGroup:
    statement = []

    statement_end = find_next_token(tokens, TokenType.SEMICOLON, offset)

    if statement_end == -1:
        raise Exception("statement is never finished")

    return StatementGroup(tokens[offset:statement_end])


def group_structures(tokens):
    i = 0

    stack = []
    groups = []

    while i < len(tokens):
        token = tokens[i]

        if token.token_type == TokenType.DO:
            stack.append(StructureGroup(
                structure_type=token.token_type,
                branches=[Branch(condition_tokens=[], content_tokens=[])]
            ))

            i += 1

            while tokens[i].token_type != TokenType.WHILE:
                stack[-1].branches[0].content_tokens.append(tokens[i])
                i += 1

        elif token.token_type == TokenType.WHILE:
            stack.append(StructureGroup(
                structure_type=token.token_type,
                branches=[Branch(condition_tokens=[], content_tokens=[])]
            ))

            i += 1

            while tokens[i].token_type != TokenType.DO:
                stack[-1].branches[0].condition_tokens.append(tokens[i])
                i += 1

        elif token.token_type == TokenType.IF:
            stack.append(StructureGroup(
                structure_type=token.token_type,
                branches=[Branch(condition_tokens=[], content_tokens=[])]
            ))

            i += 1

            while tokens[i].token_type != TokenType.THEN:
                stack[-1].branches[0].condition_tokens.append(tokens[i])
                i += 1

        elif token.token_type in [TokenType.ELIF, TokenType.ELSE]:
            if not stack or stack[-1].structure_type != TokenType.IF:
                raise Exception(f"{'elif' if token.token_type == TokenType.ELIF else 'else'} used before an if")

            stack[-1].branches.append(Branch(condition_tokens=[], content_tokens=[]))

            if tokens[i].token_type == TokenType.ELIF:
                i += 1

                while tokens[i].token_type != TokenType.THEN:
                    stack[-1].branches[-1].condition_tokens.append(tokens[i])
                    i += 1

        elif token.token_type == TokenType.END:
            if stack[-1].structure_type in STRUCTURE_TOKENS:
                new_group = stack.pop()
                if stack:
                    stack[-1].branches[-1].content_tokens.append(new_group)
                else:
                    groups.append(new_group)

        elif stack and stack[-1].structure_type == TokenType.DO:
            stack[-1].branches[0].condition_tokens.append(token)

        elif stack:
            stack[-1].branches[-1].content_tokens.append(token)

        else:
            groups.append(token)

        i += 1

    return groups


def group_statements(items):
    if not items:
        return items

    groups = []

    i = 0

    while i < len(items):
        item = items[i]

        if isinstance(item, StructureGroup):
            for branch in item.branches:
                branch.content_tokens = group_statements(branch.content_tokens)

            groups.append(item)
            i += 1
        else:
            grouped = group_statement(items, i)
            groups.append(grouped)
            i += len(grouped.tokens) + 1

    return groups


def build_statement(group: StatementGroup) -> Statement:
    statement: Statement

    if group.tokens[0].token_type == TokenType.CREATE:
        statement = CreateStatement(group.tokens)
    elif group.tokens[0].token_type == TokenType.WRITE:
        statement = WriteStatement(group.tokens)
    elif group.tokens[0].token_type == TokenType.READ:
        statement = ReadStatement(group.tokens)
    elif group.tokens[0].token_type == TokenType.SET:
        statement = SetStatement(group.tokens)
    else:
        raise Exception(f"Unexpected token type '{group.tokens[0].token_type}'")

    if not statement.validate_syntax():
        raise Exception(f"Invalid syntax for token type '{group.tokens[0].token_type}'")

    return statement


def synthesize_statements(items): # -> list[Structure | Statement]
    elements = []

    i = 0

    while i < len(items):
        item = items[i]

        if isinstance(item, StructureGroup):
            structure: Structure

            if item.structure_type == TokenType.IF:
                structure = IfStructure(branches=[])
            if item.structure_type == TokenType.DO:
                structure = DoWhileStructure(branches=[])
            if item.structure_type == TokenType.WHILE:
                structure = WhileStructure(branches=[])

            for branch in item.branches:
                structure.branches.append(Branch(
                    condition_tokens=branch.condition_tokens,
                    content_tokens=synthesize_statements(branch.content_tokens)
                ))

            elements.append(structure)
        elif isinstance(item, StatementGroup):
            if len(item.tokens) == 0:
                raise Exception("Unexpected empty statement group")

            elements.append(build_statement(item))
        else:
            raise Exception(f"Unexpected ungrouped element {item}")

        i += 1

    return elements
