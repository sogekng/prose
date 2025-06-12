from util.token import Token, TokenType
from render import VariableBank
from prose_ast import *

class Parser:
    def __init__(self, tokens: list[Token], varbank: VariableBank = None): 
        self.tokens, self.pos = tokens, 0
        self.varbank = varbank if varbank is not None else VariableBank()
    
    @property
    def current_token(self) -> Token: return self.tokens[self.pos]
    
    def advance(self): self.pos += 1
    
    def consume(self, expected_type: TokenType):
        token = self.current_token
        if token.token_type == expected_type: 
            self.advance()
            return token
        raise ParseException(f"Esperava o token {expected_type.name}, mas encontrou {token.token_type.name}", token)

    def parse(self) -> list[Statement]:
        statements = []
        while self.current_token.token_type != TokenType.EOF:
            statements.append(self._parse_toplevel_statement())
        return statements
    
    def _parse_toplevel_statement(self) -> Statement:
        if self.current_token.token_type == TokenType.CREATE and self.pos + 1 < len(self.tokens) and self.tokens[self.pos+1].token_type == TokenType.TYPE_KEYWORD:
            return self._parse_struct_definition()
        return self._parse_statement()

    def _parse_block(self) -> list[Statement]:
        statements = []; terminators = {TokenType.END, TokenType.ELSE, TokenType.ELIF, TokenType.EOF}
        while self.current_token.token_type not in terminators: 
            statements.append(self._parse_statement())
        return statements

    def _parse_statement(self) -> Statement:
        token_type = self.current_token.token_type
        
        if token_type == TokenType.FUNCTION: return self._parse_function_declaration()
        if token_type == TokenType.IF: return self._parse_if_structure()
        if token_type == TokenType.FOR: return self._parse_for_structure()
        if token_type == TokenType.WHILE: return self._parse_while_structure()
        if token_type == TokenType.DO: return self._parse_do_while_structure()
        
        stmt = None
        if token_type in (TokenType.IMPORT, TokenType.FROM):
            stmt = self._parse_import_statement()
        elif token_type == TokenType.IDENTIFIER and self.current_token.value == 'readme' and self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].token_type == TokenType.IDENTIFIER:
            stmt = self._parse_readme_statement()
        elif token_type == TokenType.CREATE: stmt = self._parse_create_statement()
        elif token_type == TokenType.SET: stmt = self._parse_set_statement()
        elif token_type == TokenType.READ: stmt = self._parse_read_statement()
        elif token_type == TokenType.WRITE: stmt = WriteStatement(self.consume(TokenType.WRITE) and self._parse_expression())
        elif token_type == TokenType.WRITELN: stmt = WriteLnStatement(self.consume(TokenType.WRITELN) and self._parse_expression())
        elif token_type == TokenType.RETURN: stmt = self._parse_return_statement()
        else: stmt = ExpressionStatement(self._parse_expression())
        
        self.consume(TokenType.SEMICOLON)
        return stmt

    def _parse_import_statement(self) -> ImportStatement:
        if self.current_token.token_type == TokenType.IMPORT:
            self.consume(TokenType.IMPORT)
            module_name_token = self.current_token

            if module_name_token.token_type not in {TokenType.IDENTIFIER, TokenType.TYPE}:
                raise ParseException(f"Esperava um nome de módulo, mas encontrou {module_name_token.token_type.name}", module_name_token)
            self.advance()
            return ImportStatement(module_name_token)
        
        self.consume(TokenType.FROM)
        module_name_token = self.current_token
        if module_name_token.token_type not in {TokenType.IDENTIFIER, TokenType.TYPE}:
            raise ParseException(f"Esperava um nome de módulo, mas encontrou {module_name_token.token_type.name}", module_name_token)
        self.advance()

        self.consume(TokenType.IMPORT)
        
        names = []

        while self.current_token.token_type != TokenType.SEMICOLON:
            name_token = self.current_token
            if name_token.token_type not in {TokenType.IDENTIFIER, TokenType.TYPE}:
                raise ParseException(f"Esperava um nome para importar, mas encontrou {name_token.token_type.name}", name_token)
            names.append(name_token)
            self.advance()

            if self.current_token.token_type == TokenType.COMMA:
                self.consume(TokenType.COMMA)
            elif self.current_token.token_type != TokenType.SEMICOLON:
                raise ParseException(f"Esperava ',' ou ';' após o nome importado, mas encontrou {self.current_token.token_type.name}", self.current_token)

        return ImportStatement(module_name_token, names)

    def _parse_type(self) -> TypeNode:
        if self.current_token.token_type == TokenType.FUNCTION:
            return self._parse_function_type_node()

        type_token = self.current_token
        if type_token.token_type == TokenType.TYPE and type_token.value == 'list':
            self.consume(TokenType.TYPE)
            self.consume(TokenType.LESS); element_type = self._parse_type(); self.consume(TokenType.GREATER)
            return ListTypeNode(element_type)
        if type_token.token_type not in {TokenType.TYPE, TokenType.IDENTIFIER}: raise ParseException("Esperava um nome de tipo", type_token)
        self.advance()
        return SimpleTypeNode(type_token, self.varbank)
    
    def _parse_function_type_node(self) -> FunctionTypeNode:
        self.consume(TokenType.FUNCTION)
        self.consume(TokenType.LPAREN)
        param_types = []
        if self.current_token.token_type != TokenType.RPAREN:
            param_types.append(self._parse_type())
            while self.current_token.token_type == TokenType.COMMA:
                self.consume(TokenType.COMMA)
                param_types.append(self._parse_type())
        self.consume(TokenType.RPAREN)
        self.consume(TokenType.ARROW)
        return_type = self._parse_type()
        return FunctionTypeNode(param_types, return_type)

    def _parse_struct_definition(self) -> StructDefinition:
        self.consume(TokenType.CREATE); self.consume(TokenType.TYPE_KEYWORD); name = self.consume(TokenType.IDENTIFIER); self.consume(TokenType.LPAREN)
        fields = []
        while self.current_token.token_type != TokenType.RPAREN:
            type_node = self._parse_type()
            field_name = self.consume(TokenType.IDENTIFIER)
            fields.append((type_node, field_name))
            if self.current_token.token_type != TokenType.COMMA: break
            self.consume(TokenType.COMMA)
        self.consume(TokenType.RPAREN); self.consume(TokenType.SEMICOLON)
        field_types = {field_name.value: type_node.to_type_object() for type_node, field_name in fields}
        self.varbank.create_struct(name.value, field_types)
        return StructDefinition(name, fields)

    def _parse_function_declaration(self) -> FunctionDeclaration:
        self.consume(TokenType.FUNCTION); name = self.consume(TokenType.IDENTIFIER); self.consume(TokenType.LPAREN)
        params = []
        if self.current_token.token_type != TokenType.RPAREN:
            param_type = self._parse_type()
            param_name = self.consume(TokenType.IDENTIFIER); params.append((param_type, param_name))
            while self.current_token.token_type == TokenType.COMMA:
                self.consume(TokenType.COMMA); param_type = self._parse_type(); param_name = self.consume(TokenType.IDENTIFIER); params.append((param_type, param_name))
        self.consume(TokenType.RPAREN)
        return_type_node = SimpleTypeNode(Token(TokenType.TYPE, 'void', 0, 0), self.varbank)
        if self.current_token.token_type == TokenType.ARROW: self.consume(TokenType.ARROW); return_type_node = self._parse_type()
        body = self._parse_block(); self.consume(TokenType.END)
        return FunctionDeclaration(name, params, return_type_node, body)

    def _parse_create_statement(self):
        self.consume(TokenType.CREATE); type_node = self._parse_type(); const_or_var = self.consume(TokenType.VARTYPE); identifier = self.consume(TokenType.IDENTIFIER)
        expression = None
        if self.current_token.token_type != TokenType.SEMICOLON:
            if self.current_token.token_type == TokenType.TO: self.consume(TokenType.TO)
            expression = self._parse_expression()
        return CreateStatement(type_node, const_or_var, identifier, expression)

    def _parse_set_statement(self):
        self.consume(TokenType.SET); target_expr = self._parse_expression()
        self.consume(TokenType.TO); value_expression = self._parse_expression()
        if isinstance(target_expr, MemberAccess): return MemberAssignmentStatement(target_expr, value_expression)
        if isinstance(target_expr, ListAccess): return ListAssignmentStatement(target_expr, value_expression)
        if isinstance(target_expr, Value) and target_expr.token.token_type == TokenType.IDENTIFIER: return SetStatement(target_expr.token, value_expression)
        raise ParseException("Alvo de atribuição inválido", self.current_token)

    def _parse_readme_statement(self) -> ReadmeStatement:
        self.consume(TokenType.IDENTIFIER); target_variable = self.consume(TokenType.IDENTIFIER); prompt_expression = self._parse_expression()
        return ReadmeStatement(target_variable, prompt_expression)

    def _parse_read_statement(self): return ReadStatement(self.consume(TokenType.READ) and self.consume(TokenType.IDENTIFIER))

    def _parse_return_statement(self) -> ReturnStatement:
        return_token = self.consume(TokenType.RETURN)
        return ReturnStatement(return_token, self._parse_expression() if self.current_token.token_type != TokenType.SEMICOLON else None)

    def _parse_if_structure(self):
        self.consume(TokenType.IF); conditions = [self._parse_expression()]; self.consume(TokenType.THEN)
        bodies = [self._parse_block()]; else_body = None
        while self.current_token.token_type == TokenType.ELIF: self.consume(TokenType.ELIF); conditions.append(self._parse_expression()); self.consume(TokenType.THEN); bodies.append(self._parse_block())
        if self.current_token.token_type == TokenType.ELSE: self.consume(TokenType.ELSE); else_body = self._parse_block()
        self.consume(TokenType.END); return IfStructure(conditions, bodies, else_body)

    def _parse_while_structure(self):
        self.consume(TokenType.WHILE); condition = self._parse_expression(); self.consume(TokenType.DO)
        body = self._parse_block(); self.consume(TokenType.END); return WhileStructure(condition, body)
    
    def _parse_do_while_structure(self):
        do_token = self.consume(TokenType.DO)
        body = []
        while self.current_token.token_type != TokenType.WHILE:
            if self.current_token.token_type == TokenType.EOF:
                raise ParseException("Laço 'do' iniciado não foi fechado por um 'while'", do_token)
            body.append(self._parse_statement())
        
        self.consume(TokenType.WHILE)
        condition = self._parse_expression()
        self.consume(TokenType.END)
        return DoWhileStructure(condition, body)

    def _parse_for_structure(self) -> ForStructure:
        self.consume(TokenType.FOR); loop_variable = self.consume(TokenType.IDENTIFIER); self.consume(TokenType.IN); iterable_expression = self._parse_expression(); self.consume(TokenType.DO)
        body = self._parse_block(); self.consume(TokenType.END)
        return ForStructure(loop_variable, iterable_expression, body)

    def _parse_expression(self, precedence=0):
        left_expr = self._parse_primary_expression()
        while self.pos < len(self.tokens):
            op_token = self.current_token
            if op_token.token_type == TokenType.LPAREN:
                left_expr = self._parse_call_expression(left_expr)
                continue
            if op_token.token_type == TokenType.DOT:
                self.consume(TokenType.DOT)
                member_name = self.consume(TokenType.IDENTIFIER)
                left_expr = MemberAccess(left_expr, member_name)
                continue
            if op_token.token_type == TokenType.LBRACKET:
                self.consume(TokenType.LBRACKET)
                index_expr = self._parse_expression()
                self.consume(TokenType.RBRACKET)
                left_expr = ListAccess(left_expr, index_expr)
                continue
            op_precedence = self._get_precedence(op_token.token_type)
            if op_precedence <= precedence: break
            self.advance()
            right_expr = self._parse_expression(op_precedence)
            left_expr = BinOp(left_expr, op_token, right_expr)
        return left_expr
    
    def _parse_primary_expression(self):
        token = self.current_token
        if token.token_type in LITERAL_AND_IDENTIFIER_TOKENS: self.advance(); return Value(token)
        if token.token_type == TokenType.LPAREN: self.consume(TokenType.LPAREN); expr = self._parse_expression(); self.consume(TokenType.RPAREN); return expr
        if token.token_type == TokenType.LBRACKET: return self._parse_list_literal()
        raise ParseException("Expressão primária inválida", token)

    def _parse_list_literal(self) -> ListLiteral:
        self.consume(TokenType.LBRACKET); elements = []
        if self.current_token.token_type != TokenType.RBRACKET:
            elements.append(self._parse_expression())
            while self.current_token.token_type == TokenType.COMMA: self.consume(TokenType.COMMA); elements.append(self._parse_expression())
        self.consume(TokenType.RBRACKET); return ListLiteral(elements)

    def _parse_call_expression(self, callee: Expression) -> FunctionCall:
        self.consume(TokenType.LPAREN); arguments = []
        if self.current_token.token_type != TokenType.RPAREN:
            arguments.append(self._parse_expression())
            while self.current_token.token_type == TokenType.COMMA: self.consume(TokenType.COMMA); arguments.append(self._parse_expression())
        self.consume(TokenType.RPAREN); return FunctionCall(callee, arguments)
    
    def _get_precedence(self, token_type: TokenType): 
        PRECEDENCE = {TokenType.OR: 1, TokenType.AND: 2, TokenType.EQUAL: 3, TokenType.NOT_EQUAL: 3, TokenType.LESS: 3, TokenType.GREATER: 3, TokenType.LESS_EQUAL: 3, TokenType.GREATER_EQUAL: 3, TokenType.ADDITION: 4, TokenType.SUBTRACTION: 4, TokenType.MULTIPLICATION: 5, TokenType.DIVISION: 5, TokenType.MODULUS: 5}
        return PRECEDENCE.get(token_type, 0)