from util.token import TokenType

class StructureGroup:
    def __init__(self, structure_type, condition, content):
        self.structure_type = structure_type
        self.condition = condition
        self.content = content

    def __repr__(self):
        return f"StructureGroup(type={self.structure_type}, condition={self.condition}, content={self.content})"


STRUCTURE_TOKENS = [TokenType.IF, TokenType.WHILE, TokenType.DO]


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
