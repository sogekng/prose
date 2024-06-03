
class Executor:
    def __init__(self):
        self.variables = {}

    def get(self):
        return self.variables

    def execute(self, statement):
        return statement.execute(self)

    def generate_java_code(self, statements):
        java_code = []
        for statement in statements:
            java_code.append(statement.execute(self))
        return "\n".join(java_code)