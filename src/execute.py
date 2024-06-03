from src.parsa import StructureGroup
from src.util.token import TokenType


class Executor:
    def __init__(self):
        self.variables = {}

    def get(self):
        return self.variables

    def execute(self, statement):
        return statement.execute(self)

    def generate_java_code(self, statements):
        java_code = []
        block = []  # Para armazenar temporariamente uma sequência de statements condicionais

        for statement in statements:
            if isinstance(statement, StructureGroup) and statement.structure_type in (
                    TokenType.IF, TokenType.ELIF, TokenType.ELSE):
                block.append(statement)

                if statement.structure_type == TokenType.ELSE:  # Finaliza o bloco quando encontra um ELSE
                    java_code.append(self.process_conditional_block(block))
                    block = []  # Reinicia o bloco
            else:
                if block:
                    # Finaliza o bloco anterior se começar um novo statement que não é condicional
                    java_code.append(self.process_conditional_block(block))
                    block = []

                java_code.append(statement.execute(self))

        # Se ainda houver statements no bloco após terminar a iteração
        if block:
            java_code.append(self.process_conditional_block(block))

        return "\n".join(java_code)

    def process_conditional_block(self, block):
        java_code = []
        for index, stmt in enumerate(block):
            if index == 0:
                java_code.append(stmt.execute(self)) # Primeiro statement sempre é IF
            elif stmt.structure_type == TokenType.ELIF:
                # Transforma ELIF em ELSE IF para Java
                condition_code = " ".join([token.value for token in stmt.condition])
                content_code = "\n".join([inner_stmt.execute(self) for inner_stmt in stmt.content])
                java_code.append(f"else if ({condition_code}) {{\n{content_code}\n}}")
            elif stmt.structure_type == TokenType.ELSE:
                # Simples ELSE para Java
                content_code = "\n".join([inner_stmt.execute(self) for inner_stmt in stmt.content])
                java_code.append(f"else {{\n{content_code}\n}}")
        return "\n".join(java_code)
