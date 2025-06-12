import os
from prose_ast import *
from render import (VariableBank, FunctionType, IntegerType, RationalType, 
                    StringType, BooleanType, ListType, StructType, VoidType)
from lexer import Lexer
from parsa import Parser

class ValueWrapper:
    def __init__(self, value, value_type: Type):
        self.value = value
        self.type = value_type
    def __repr__(self): return f"ValueWrapper({self.value}, {self.type})"

class ReturnSignal(Exception):
    def __init__(self, value_wrapper: ValueWrapper):
        self.value_wrapper = value_wrapper

class ProseFunction:
    def __init__(self, declaration: FunctionDeclaration, closure: VariableBank):
        self.declaration = declaration
        self.closure = closure
    def __repr__(self): return f"<ProseFunction {self.declaration.name.value}>"

class StructInstance:
    def __repr__(self):
        fields = ', '.join(f'{k}={v}' for k, v in vars(self).items())
        return f"<StructInstance {fields}>"

class ModuleInstance:
    def __init__(self, name: str, env: VariableBank):
        self.name = name
        self.environment = env
    def __repr__(self): return f"<ModuleInstance {self.name}>"

class Interpreter:
    def __init__(self):
        self.environment = VariableBank()
        self.imported_modules = {}

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'Nenhum método visit_{type(node).__name__} encontrado para o nó {node}')

    def run(self, nodes, base_path='.'):
        previous_path = getattr(self, 'base_path', '.')
        self.base_path = base_path
        
        for node in nodes:
            if isinstance(node, (FunctionDeclaration, StructDefinition, ImportStatement)):
                self.visit(node)
        
        for node in nodes:
            if not isinstance(node, (FunctionDeclaration, StructDefinition, ImportStatement)):
                self.visit(node)
        
        self.base_path = previous_path

    def execute_block(self, statements: list[Statement], environment: VariableBank):
        previous_env = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.visit(statement)
        finally:
            self.environment = previous_env

    def _load_module(self, module_name_token: Token):
        module_name = module_name_token.value
        if module_name in self.imported_modules:
            return self.imported_modules[module_name]

        module_file_name = module_name + '.prose'
        module_path = os.path.join(self.base_path, module_file_name)
        absolute_path = os.path.abspath(module_path)

        try:
            with open(absolute_path, 'r', encoding='utf-8') as file:
                code = file.read()
        except FileNotFoundError:
            raise RuntimeException(f"Módulo '{module_name}' não encontrado.", module_name_token)

        module_interpreter = Interpreter()
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser(tokens, module_interpreter.environment)
        syntax_tree = parser.parse()
        module_interpreter.run(syntax_tree, base_path=os.path.dirname(absolute_path))
        
        self.imported_modules[module_name] = module_interpreter.environment
        return module_interpreter.environment

    def visit_ImportStatement(self, node: ImportStatement):
        module_env = self._load_module(node.module_path)
        
        if node.imported_names:
            for name_token in node.imported_names:
                name = name_token.value
                try:
                    variable = module_env.get(name)
                    self.environment.create(name, variable.constant, variable.vartype, variable.value)
                except Exception:
                    raise RuntimeException(f"Nome '{name}' não encontrado no módulo '{node.module_path.value}'.", name_token)
        else:
            module_name = node.module_path.value
            module_object = ModuleInstance(module_name, module_env)
            for name, var in module_env.variables.items():
                setattr(module_object, name, var.value)
            self.environment.create(module_name, True, ModuleType(module_name), module_object)

    def visit_StructDefinition(self, node: StructDefinition):
        pass

    def visit_FunctionDeclaration(self, node: FunctionDeclaration):
        func_name = node.name.value
        func_obj = ProseFunction(node, self.environment)
        param_types = [p[0].to_type_object() for p in node.params]
        return_type = node.return_type_node.to_type_object()
        func_type = FunctionType(param_types, return_type)
        self.environment.create(func_name, True, func_type, func_obj)
    
    def visit_CreateStatement(self, node: CreateStatement):
        var_type = node.type_node.to_type_object()
        value = None
        if node.expression:
            value = self.visit(node.expression).value
        elif isinstance(var_type, ListType):
            value = []
        elif isinstance(var_type, StructType):
            value = StructInstance()
            for field_name, field_type in var_type.fields.items():
                default_val = None
                if isinstance(field_type, (IntegerType, RationalType)): default_val = 0
                if isinstance(field_type, StringType): default_val = ""
                if isinstance(field_type, BooleanType): default_val = False
                if isinstance(field_type, ListType): default_val = []
                setattr(value, field_name, default_val)
        self.environment.create(node.identifier.value, node.const_or_var.value == 'constant', var_type, value)

    def visit_SetStatement(self, node: SetStatement):
        var_name = node.identifier.value
        value_wrapper = self.visit(node.expression)
        self.environment.set(var_name, value_wrapper.value)

    def visit_MemberAssignmentStatement(self, node: MemberAssignmentStatement):
        obj_wrapper = self.visit(node.member_access.obj)
        value_wrapper = self.visit(node.expression)
        setattr(obj_wrapper.value, node.member_access.member.value, value_wrapper.value)

    def visit_ListAssignmentStatement(self, node: ListAssignmentStatement):
        list_wrapper = self.visit(node.list_access.list_expr)
        index_wrapper = self.visit(node.list_access.index_expression)
        value_wrapper = self.visit(node.expression)
        list_wrapper.value[index_wrapper.value] = value_wrapper.value

    def visit_ExpressionStatement(self, node: ExpressionStatement):
        self.visit(node.expression)

    def visit_Value(self, node: Value) -> ValueWrapper:
        token_type = node.token.token_type
        value = node.token.value
        if token_type == TokenType.INTEGER: return ValueWrapper(int(value), IntegerType())
        if token_type == TokenType.RATIONAL: return ValueWrapper(float(value), RationalType())
        if token_type == TokenType.STRING: return ValueWrapper(value[1:-1], StringType())
        if token_type == TokenType.BOOLEAN: return ValueWrapper(value == 'true', BooleanType())
        if token_type == TokenType.IDENTIFIER:
            var = self.environment.get(value)
            return ValueWrapper(var.value, var.vartype)
            
    def visit_BinOp(self, node: BinOp) -> ValueWrapper:
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op.token_type
        try:
            if op == TokenType.ADDITION:
                if isinstance(left.type, StringType) or isinstance(right.type, StringType):
                    return ValueWrapper(str(left.value) + str(right.value), StringType())
                result = left.value + right.value
            elif op == TokenType.SUBTRACTION: result = left.value - right.value
            elif op == TokenType.MULTIPLICATION: result = left.value * right.value
            elif op == TokenType.DIVISION: result = left.value / right.value
            elif op == TokenType.MODULUS: result = left.value % right.value
            elif op == TokenType.GREATER: result = left.value > right.value
            elif op == TokenType.LESS: result = left.value < right.value
            elif op == TokenType.GREATER_EQUAL: result = left.value >= right.value
            elif op == TokenType.LESS_EQUAL: result = left.value <= right.value
            elif op == TokenType.EQUAL: result = left.value == right.value
            elif op == TokenType.NOT_EQUAL: result = left.value != right.value
            elif op == TokenType.AND: result = left.value and right.value
            elif op == TokenType.OR: result = left.value or right.value
            else: raise Exception(f"Operador binário desconhecido: {op}")
            result_type = BooleanType()
            if op in {TokenType.ADDITION, TokenType.SUBTRACTION, TokenType.MULTIPLICATION, TokenType.DIVISION, TokenType.MODULUS}:
                result_type = RationalType() if isinstance(left.type, RationalType) or isinstance(right.type, RationalType) else IntegerType()
            return ValueWrapper(result, result_type)
        except ZeroDivisionError:
            raise RuntimeException("Divisão por zero.", node.op)
        except TypeError:
            raise RuntimeException(f"Operação inválida entre os tipos {left.type} e {right.type}.", node.op)
    
    def visit_IfStructure(self, node: IfStructure):
        for i, condition in enumerate(node.conditions):
            if self.visit(condition).value:
                self.execute_block(node.bodies[i], VariableBank(parent=self.environment))
                return
        if node.else_body:
            self.execute_block(node.else_body, VariableBank(parent=self.environment))

    def visit_ForStructure(self, node: ForStructure):
        iterable_wrapper = self.visit(node.iterable_expression)
        iterable_value = iterable_wrapper.value
        if not isinstance(iterable_wrapper.type, (ListType, StringType)): raise RuntimeException(f"Laço 'for' só pode iterar sobre listas ou strings, não sobre o tipo '{iterable_wrapper.type}'", node.loop_variable)
        for item in iterable_value:
            loop_env = VariableBank(parent=self.environment)
            element_type = iterable_wrapper.type.element_type if isinstance(iterable_wrapper.type, ListType) else StringType()
            loop_env.create(node.loop_variable.value, True, element_type, item)
            self.execute_block(node.body, loop_env)

    def visit_WhileStructure(self, node: WhileStructure):
        while self.visit(node.condition).value:
            self.execute_block(node.body, VariableBank(parent=self.environment))

    def visit_DoWhileStructure(self, node: DoWhileStructure):
        while True:
            self.execute_block(node.body, VariableBank(parent=self.environment))
            if not self.visit(node.condition).value: break
    
    def visit_FunctionCall(self, node: FunctionCall):
        if isinstance(node.callee, Value) and self.environment.is_native_function(node.callee.token.value):
            return self._visit_native_function_call(node)
        
        callee_wrapper = self.visit(node.callee)
        func_obj = callee_wrapper.value
        
        if not isinstance(func_obj, ProseFunction):
            raise RuntimeException(f"Expressão do tipo '{callee_wrapper.type}' não é chamável.", node.callee.token if isinstance(node.callee, Value) else Token(TokenType.NONE,'',0,0))

        arg_values = [self.visit(arg).value for arg in node.arguments]
        func_env = VariableBank(parent=func_obj.closure)
        for i, param_node in enumerate(func_obj.declaration.params):
            func_env.create(param_node[1].value, False, param_node[0].to_type_object(), arg_values[i])
        return_value_wrapper = ValueWrapper(None, VoidType())
        try:
            self.execute_block(func_obj.declaration.body, func_env)
        except ReturnSignal as rs:
            return_value_wrapper = rs.value_wrapper
        return return_value_wrapper

    def _visit_native_function_call(self, node: FunctionCall):
        func_name = node.callee.token.value
        arg_wrappers = [self.visit(arg) for arg in node.arguments]
        if func_name == 'readme': return
        if not arg_wrappers: raise RuntimeException(f"Função nativa '{func_name}' chamada sem argumentos.", node.callee.token)
        
        target_wrapper = arg_wrappers[0]
        
        try:
            if func_name == 'add': target_wrapper.value.append(arg_wrappers[1].value); return ValueWrapper(None, VoidType())
            if func_name == 'get': return ValueWrapper(target_wrapper.value[arg_wrappers[1].value], target_wrapper.type.element_type)
            if func_name == 'remove': target_wrapper.value.pop(arg_wrappers[1].value); return ValueWrapper(None, VoidType())
            if func_name == 'length': return ValueWrapper(len(target_wrapper.value), IntegerType())
            if func_name == 'uppercase': return ValueWrapper(target_wrapper.value.upper(), StringType())
            if func_name == 'lowercase': return ValueWrapper(target_wrapper.value.lower(), StringType())
            if func_name == 'substring': return ValueWrapper(target_wrapper.value[arg_wrappers[1].value:arg_wrappers[2].value], StringType())
        except IndexError:
            raise RuntimeException(f"Índice fora dos limites.", node.callee.token)
        except Exception as e:
            raise RuntimeException(f"Erro ao executar função nativa '{func_name}': {e}", node.callee.token)

    def visit_ReturnStatement(self, node: ReturnStatement):
        value_wrapper = self.visit(node.expression) if node.expression else ValueWrapper(None, VoidType())
        raise ReturnSignal(value_wrapper)
            
    def visit_WriteLnStatement(self, node: WriteLnStatement):
        value_wrapper = self.visit(node.expression)
        if isinstance(value_wrapper.value, StructInstance): print(f"<Objeto {value_wrapper.type.name}>")
        else: print(value_wrapper.value)

    def visit_WriteStatement(self, node: WriteStatement):
        value_wrapper = self.visit(node.expression)
        if isinstance(value_wrapper.value, StructInstance): print(f"<Objeto {value_wrapper.type.name}>", end='')
        else: print(value_wrapper.value, end='')
    
    def visit_ReadStatement(self, node: ReadStatement):
        var = self.environment.get(node.identifier.value)
        user_input = input()
        try:
            if isinstance(var.vartype, IntegerType): var.value = int(user_input)
            elif isinstance(var.vartype, RationalType): var.value = float(user_input)
            elif isinstance(var.vartype, BooleanType): var.value = user_input.lower() == 'true'
            else: var.value = user_input
        except ValueError: raise RuntimeException(f"Entrada inválida. Esperava um valor do tipo {var.vartype}.", node.identifier)
    
    def visit_ReadmeStatement(self, node: ReadmeStatement):
        prompt_wrapper = self.visit(node.prompt_expression)
        user_input = input(prompt_wrapper.value)
        var = self.environment.get(node.target_variable.value)
        try:
            if isinstance(var.vartype, IntegerType): var.value = int(user_input)
            elif isinstance(var.vartype, RationalType): var.value = float(user_input)
            elif isinstance(var.vartype, BooleanType): var.value = user_input.lower() == 'true'
            else: var.value = user_input
        except ValueError: raise RuntimeException(f"Entrada inválida. Esperava um valor do tipo {var.vartype}.", node.target_variable)

    def visit_ListLiteral(self, node: ListLiteral) -> ValueWrapper:
        elements = [self.visit(elem).value for elem in node.elements]
        return ValueWrapper(elements, node.get_type(self.environment))

    def visit_ListAccess(self, node: ListAccess) -> ValueWrapper:
        list_wrapper = self.visit(node.list_expr)
        index_wrapper = self.visit(node.index_expression)
        try:
            return ValueWrapper(list_wrapper.value[index_wrapper.value], list_wrapper.type.element_type)
        except IndexError:
            raise RuntimeException(f"Índice {index_wrapper.value} fora dos limites da lista.", node.list_expr.token if isinstance(node.list_expr, Value) else Token(TokenType.NONE, '', 0, 0))

    def visit_MemberAccess(self, node: MemberAccess) -> ValueWrapper:
        obj_wrapper = self.visit(node.obj)
        member_name = node.member.value
        obj_value = obj_wrapper.value
        
        if isinstance(obj_value, ModuleInstance):
            try:
                member_var = obj_value.environment.get(member_name)
                return ValueWrapper(member_var.value, member_var.vartype)
            except Exception:
                raise RuntimeException(f"O módulo '{obj_value.name}' não possui um membro chamado '{member_name}'", node.member)
        if isinstance(obj_wrapper.type, StructType):
            try:
                field_value = getattr(obj_value, member_name)
                field_type = obj_wrapper.type.fields[member_name]
                return ValueWrapper(field_value, field_type)
            except AttributeError:
                raise RuntimeException(f"Membro '{member_name}' não encontrado no objeto.", node.member)
        if isinstance(obj_wrapper.type, ListType) and member_name == 'length':
            return ValueWrapper(len(obj_value), IntegerType())
        raise RuntimeException("Acesso a membro inválido.", node.member)
