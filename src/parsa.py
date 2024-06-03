from util.token import TokenType, STRUCTURE_TOKENS, LITERAL_TOKENS
from dataclasses import dataclass


@dataclass
class Statement:
    content: list

    def validate_syntax(self) -> bool:
        return True

    def execute(self, executor):
        pass

    def verify_variable(self, attributes, set_type, set_value):
        pass


class CreateStatement(Statement):
    def validate_syntax(self) -> bool:
        return (
                len(self.content) >= 4
                and self.content[0].token_type == TokenType.CREATE
                and self.content[1].token_type == TokenType.TYPE
                and self.content[2].token_type == TokenType.VARTYPE
                and self.content[3].token_type == TokenType.IDENTIFIER
                and (len(self.content) == 4 or self.content[4].token_type in LITERAL_TOKENS)
        )

    def execute(self, executor):

        type_value = self.content[1].value
        var_type = self.content[2].value
        identifier = self.content[3].value
        value = self.content[4].value if len(self.content) > 4 else None

        executor.variables[identifier] = [type_value, var_type, value]

        if type_value == "integer":
            java_type = "int"
            java_value = None if value is None else int(value)

            return self.verify_variable([identifier, type_value, var_type, value], java_type, java_value)

        elif type_value == "string":
            java_type = "String"
            java_value = None if value is None else value

            return self.verify_variable([identifier, type_value, var_type, value], java_type, java_value)

        elif type_value == "boolean":
            java_type = "boolean"
            java_value = None if value is None else value

            return self.verify_variable([identifier, type_value, var_type, value], java_type, java_value)

    def verify_variable(self, variable, set_type, set_value):

        # Verifica se o valor da variavel é None se for ele cria uma variavel sem valor
        # Ex: boolean variavel;
        # Depois verifica se é uma variavel com o tipo normal ou constant e retorna a atribuição do valor

        identifier = variable[0]
        var_type = variable[2]
        value = variable[3]

        if value == None:
            if var_type == "variable":
                return f'{set_type} {identifier};'
            elif var_type == "constant":
                return f'final {set_type} {identifier};'
        else:
            if var_type == "variable":
                return f'{set_type} {identifier} = {set_value};'
            elif var_type == "constant":
                return f'final {set_type} {identifier} = {set_value};'


class WriteStatement(Statement):
    def validate_syntax(self) -> bool:
        return (
                len(self.content) >= 2
                and self.content[0].token_type == TokenType.WRITE
        )

    def execute(self, executor):
        identifier = self.content[1].value

        if len(self.content) > 2:
            expression_tokens = self.content[1:]

            variables = executor.get()

            new_value = evaluate_expression(expression_tokens, variables)

            return f'System.out.println({new_value});'
        else:
            return f'System.out.println({identifier});'


class SetStatement(Statement):
    def validate_syntax(self) -> bool:
        return (
                len(self.content) >= 4
                and self.content[0].token_type == TokenType.SET
                and self.content[1].token_type == TokenType.IDENTIFIER
                and self.content[2].token_type == TokenType.TO
        )

    def execute(self, executor):
        identifier = self.content[1].value
        second_identifier = self.content[3].token_type

        if len(self.content) >= 5:
            expression_tokens = self.content[3:]

            expression = ' '.join(str(token.value) for token in self.content[3:])

            variables = executor.get()
            variable = variables.get(identifier)
            type_value, var_type, value = variable

            evaluate_expression(expression_tokens, variables)
            new_value = evaluate_expression(expression_tokens, variables)

            variables[identifier] = [type_value, var_type, f'{new_value}']

            return f"{identifier} = {expression};"
        elif second_identifier == TokenType.IDENTIFIER:
            second_identifier = self.content[3].value

            variables = executor.get()

            first_variable = variables.get(identifier)
            type_value, var_type, value = first_variable

            second_variable = variables.get(second_identifier)
            new_value = second_variable[2]

            variables[identifier] = [type_value, var_type, f'{new_value}']

            return f"{identifier} = {second_identifier};"
        else:
            identifier = self.content[1].value
            new_value = self.content[3].value

            variables = executor.get()
            variable = variables.get(identifier)
            type_value, var_type, value = variable

            variables[identifier] = [type_value, var_type, f'{new_value}']

            return f"{identifier} = {new_value};"


class ReadStatement(Statement):
    def validate_syntax(self) -> bool:
        return (
                len(self.content) == 2 and
                self.content[0].token_type == TokenType.READ and
                self.content[1].token_type == TokenType.IDENTIFIER
        )

    def execute(self, executor):
        identifier = self.content[1].value

        variables = executor.get()
        variable = variables.get(identifier)

        if identifier not in variables:
            return f"Essa variável não existe: '{identifier}'"

        type_value = variable[0]

        if type_value == "integer":
            return f'{identifier} = Integer.parseInt(scanner.nextLine());'
        elif type_value == "string":
            return f'{identifier} = scanner.nextLine();'
        elif type_value == "boolean":
            return f'{identifier} = Boolean.parseBoolean(scanner.nextLine());'


@dataclass
class StructureGroup:
    structure_type: TokenType
    condition: list
    content: list

    def __repr__(self):
        return f"StructureGroup(type={self.structure_type}, condition={self.condition}, content={self.content})"

    def execute(self, executor):
        structure = self.structure_type

        content_code = "\n".join([stmt.execute(executor) for stmt in self.content])

        if structure == TokenType.IF:
            condition_code = " ".join([token.value for token in self.condition])
            return f"if ({condition_code}) {{\n{content_code}\n}}"
        elif structure == TokenType.ELIF:
            condition_code = " ".join([token.value for token in self.condition])
            return f"else if ({condition_code}) {{\n{content_code}\n}}"
        elif structure == TokenType.ELSE:
            return f"else {{\n{content_code}\n}}"
        elif structure == TokenType.WHILE:
            condition_code = " ".join([token.value for token in self.condition])
            return f"while ({condition_code}) {{\n{content_code}\n}}"
        elif structure == TokenType.DO:
            condition_code = " ".join([token.value for token in self.condition])
            return f"do {{\n{content_code}\n}} while ({condition_code});"


def evaluate_expression(tokens, variables):
    def get_value(token):
        if token.token_type == TokenType.IDENTIFIER:
            if token.value in variables:
                return variables[token.value][2]  # Retorna o valor da variável
            else:
                raise ValueError(f"Undefined variable: {token.value}")
        return token.value

    # Constrói a expressão a partir dos valores dos tokens
    expression = ''.join(str(get_value(token)) for token in tokens)

    try:
        result = eval(expression)
        if isinstance(result, float):
            return int(result)
        return result
    except SyntaxError as e:
        raise ValueError(f"Syntax error in expression: {expression}") from e
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {expression}") from e


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


def group_statement(tokens: list, offset: int):
    statement = []

    statement_end = find_next_token(tokens, TokenType.SEMICOLON, offset)

    if statement_end == -1:
        raise Exception("statement is never finished")

    return tokens[offset:statement_end]


def group_tokens(tokens):
    i = 0

    stack = []
    groups = []

    while i < len(tokens):
        token = tokens[i]

        if token.token_type == TokenType.DO:
            stack.append(StructureGroup(
                structure_type=TokenType.DO,
                condition=[],
                content=[]
            ))

        elif token.token_type == TokenType.WHILE and stack and stack[-1].structure_type == TokenType.DO:
            i += 1
            while tokens[i].token_type != TokenType.END:
                stack[-1].condition.append(tokens[i])
                i += 1
            new_group = stack.pop()
            if stack:
                stack[-1].content.append(new_group)
            else:
                groups.append(new_group)

        elif token.token_type in STRUCTURE_TOKENS:
            stack.append(StructureGroup(
                structure_type=token.token_type,
                condition=[],
                content=[]
            ))

            i += 1

            condition_delimiter = TokenType.DO if token.token_type == TokenType.WHILE else TokenType.THEN

            while tokens[i].token_type != condition_delimiter:
                stack[-1].condition.append(tokens[i])
                i += 1

        elif token.token_type == TokenType.END:
            if stack[-1].structure_type in STRUCTURE_TOKENS:
                new_group = stack.pop()
                if stack:
                    stack[-1].content.append(new_group)
                else:
                    groups.append(new_group)

        elif stack:
            stack[-1].content.append(token)

        else:
            groups.append(token)

        i += 1

    return groups


def render_groups(items):
    if not items:
        return items

    groups = []

    i = 0

    while i < len(items):
        item = items[i]

        if type(item) == StructureGroup:
            item.content = render_groups(item.content)
            groups.append(item)
            i += 1
        else:
            grouped = group_statement(items, i)
            groups.append(grouped)
            i += len(grouped) + 1

    return groups


def build_statement(group):
    statement: Statement

    if group[0].token_type == TokenType.CREATE:
        statement = CreateStatement(group)
    elif group[0].token_type == TokenType.WRITE:
        statement = WriteStatement(group)
    elif group[0].token_type == TokenType.READ:
        statement = ReadStatement(group)
    elif group[0].token_type == TokenType.SET:
        statement = SetStatement(group)
    else:
        raise Exception(f"Unexpected token type '{group[0].token_type}'")

    if not statement.validate_syntax():
        raise Exception(f"Invalid syntax for token type '{group[0].token_type}'")

    return statement


def synthesize_statements(items):
    i = 0

    while i < len(items):
        item = items[i]

        if type(item) == StructureGroup:
            synthesize_statements(item.content)
        elif type(item) == list:
            if len(item) == 0:
                raise Exception("Unexpected empty statement group")
            items[i] = build_statement(item)
        else:
            raise Exception(f"Unexpected ungrouped element {item}")

        i += 1
