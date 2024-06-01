from util.token import TokenType, STRUCTURE_TOKENS, LITERAL_TOKENS
from dataclasses import dataclass


@dataclass
class Statement:
    content: list

    def validate_syntax(self) -> bool:
        return True


class CreateStatement(Statement):
    def validate_syntax(self) -> bool:
        return (
            len(self.content) >= 4
            and self.content[0].token_type == TokenType.CREATE
            and self.content[1].token_type == TokenType.TYPE
            and self.content[2].token_type == TokenType.VARTYPE
            and self.content[3].token_type == TokenType.IDENTIFIER
            and len(self.content) == 4 or self.content[4].token_type in LITERAL_TOKENS
        )


@dataclass
class StructureGroup:
    structure_type: TokenType
    condition: list
    content: list

    def __repr__(self):
        return f"StructureGroup(type={self.structure_type}, condition={self.condition}, content={self.content})"


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

        # OBS: Esses carinhas ":D XD" existem por que o do-while é diferente dos outros,
        # resolvi fazer separado para não gerar dor de cabeça.

        if token.token_type == TokenType.DO:  # :D
            # Verifica se o token atual é o último na lista de STRUCTURE_TOKENS, que é 'DO'.
            # Se for 'DO', inicia uma nova estrutura 'DO-WHILE' e a adiciona na pilha.
            stack.append(StructureGroup(
                structure_type=TokenType.DO,
                condition=[],
                content=[]
            ))

        elif token.token_type == TokenType.WHILE and stack and stack[-1].structure_type == TokenType.DO:  # XD
            # Verifica se o token atual é o penúltimo na lista de STRUCTURE_TOKENS, que no caso é o 'WHILE',
            # depois verifica se existe alguma estrutura na pilha e se a última estrutura é o 'DO-WHILE'.
            i += 1
            while tokens[i].token_type != TokenType.END:
                # Continua adicionando tokens à condição até encontrar um 'END'.
                stack[-1].condition.append(tokens[i])
                i += 1
            new_group = stack.pop()
            if stack:
                stack[-1].content.append(new_group)
            else:
                groups.append(new_group)

        elif token.token_type in STRUCTURE_TOKENS:
            # Verifica se o token está na lista de STRUCTURE_TOKENS ('IF', 'WHILE', 'DO').
            # Inicia uma nova estrutura (IF ou WHILE) e adiciona à pilha.
            stack.append(StructureGroup(
                structure_type=token.token_type,
                condition=[],
                content=[]
            ))

            i += 1

            condition_delimiter = TokenType.DO if token.token_type == TokenType.WHILE else TokenType.THEN

            while tokens[i].token_type != condition_delimiter:
                # Continua adicionando tokens na condição até encontrar um 'DO' ou 'THEN'.
                stack[-1].condition.append(tokens[i])
                i += 1

        elif token.token_type == TokenType.END:
            # Verifica se o token é 'END' que significa o fim de uma estrutura.
            if stack[-1].structure_type in STRUCTURE_TOKENS:
                # Verifica se o fim da estrutura faz parte de alguma das estruturas em STRUCTURE_TOKENS,
                new_group = stack.pop()
                if stack:
                    stack[-1].content.append(new_group)
                else:
                    groups.append(new_group)

        elif stack:
            # Caso tenha uma estrutura na pilha, adiciona o token atual ao conteúdo da estrutura atual.
            stack[-1].content.append(token)

        else:
            # adiciona os tokens diretamente na lista de grupos como um token solo.
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

