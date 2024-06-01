from util.token import Token

class StructureGroup:
    def __init__(self, condition, content):
        self.condition = condition
        self.content = content

STRUCTURE_TOKENS = ['IF', 'WHILE', 'DO']

def find_next_token(tokens, type, offset):
    for i in range(offset, len(tokens)):
        if tokens[i].type == type:
            return i

    return -1

def find_matching_end(tokens, offset):
    pair_count = 0

    for i in range(offset, len(tokens)):
        if tokens[i].type in STRUCTURE_TOKENS:
            pair_count += 1
        elif tokens[i].type == 'END':
            pair_count -= 1

        if pair_count == 0:
            return i

    return -1

def group_tokens(tokens):
    i = 0

    groups = []

    while i < len(tokens):
        token_type = tokens[i].type

        end_idx

        if token_type in STRUCTURE_TOKENS:
            end_idx = find_matching_end(tokens, i)

            if end_idx == -1:
                print(f"Unable to find matching end for '{token_type}'")
                return None

            pass # pense nisso
        else:
            end_idx = find_next_token(tokens, 'SEMICOLON', i)

            if end_idx == -1:
                print(f"Unable to find '{token_type}' delimiter")
                return None

            groups.append(tokens[i:end_idx])

            i = end_idx + 1

        i += 1

    return groups
