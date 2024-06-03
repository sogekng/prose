
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
            code = statement.execute(self)
            if code is not None:
                java_code.append(code)
        return "\n".join(java_code)