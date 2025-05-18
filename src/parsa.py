from dataclasses import dataclass
import sys

from util.token import Token, TokenType, STRUCTURE_TOKENS, LITERAL_TOKENS, INVALID_EXPRESSION_TOKENS, OPERATOR_TOKENS, BOOLEAN_OPERATOR_TOKENS, NUMERIC_OPERATOR_TOKENS
from render import VariableBank, VariableType, Variable, NUMERIC_TYPES

OPEN_BRACKET = "{"
CLOSE_BRACKET = "}"


PRECEDENCE_TABLE = {
    TokenType.OR: 1,
    TokenType.AND: 2,
    TokenType.NOT: 3,

    TokenType.EQUAL: 4,
    TokenType.GREATER: 4,
    TokenType.LESS: 4,
    TokenType.NOT_EQUAL: 4,

    TokenType.ADDITION: 5,
    TokenType.SUBTRACTION: 5,

    TokenType.MULTIPLICATION: 6,
    TokenType.DIVISION: 6,
    TokenType.MODULUS: 6,
}


class Expression:
    def __repr__(self) -> str:
        return f"EXPR"


@dataclass
class ExpressionValue(Expression):
    literal: Token

    def __repr__(self) -> str:
        return f"VALUE({self.literal})"


@dataclass
class ExpressionOperation(Expression):
    operator: Token
    left: Expression | None 
    right: Expression 

    def __repr__(self) -> str:
        if self.left is None: 
            return f"{self.operator}[{self.right}]"
        return f"[{self.left}]{self.operator}[{self.right}]"


def match_paren_left_to_right(tokens: list[Token], anchor_index: int) -> int:
    open_paren_count = 0
    for k in range(anchor_index, -1, -1): 
        token = tokens[k]
        if token.token_type == TokenType.RPAREN:
            open_paren_count += 1
        elif token.token_type == TokenType.LPAREN:
            open_paren_count -= 1
        
        if open_paren_count == 0: 
            return k 
            
    line_num_info = 'desconhecida'
    if anchor_index < len(tokens) and hasattr(tokens[anchor_index], 'line'):
        line_num_info = str(tokens[anchor_index].line)
    elif tokens and hasattr(tokens[0], 'line'): 
        line_num_info = str(tokens[0].line)
        
    raise Exception(f"Parêntese não correspondido na expressão perto da linha {line_num_info}")


def parse_expression(tokens: list[Token]) -> Expression:
    if not tokens:
        raise Exception("Tentativa de analisar expressão com lista de tokens vazia.")

    if len(tokens) == 1:
        token = tokens[0]
        if token.token_type in LITERAL_TOKENS or token.token_type == TokenType.IDENTIFIER:
            return ExpressionValue(token)
        else:
            line = token.line if hasattr(token, 'line') else 'N/A'
            col = token.column if hasattr(token, 'column') else 'N/A'
            raise Exception(f"Token inesperado '{token.value}' (tipo: {token.token_type}) na linha {line}, coluna {col} encontrado em expressão onde um valor era esperado.")

    if tokens[0].token_type == TokenType.LPAREN and tokens[-1].token_type == TokenType.RPAREN:
        paren_level = 0
        if len(tokens) > 1: 
            temp_level = 0
            first_lparen_matches_last_rparen = False
            is_outer_pair = True
            current_level = 0
            for i_check, t_check in enumerate(tokens[:-1]): 
                if t_check.token_type == TokenType.LPAREN:
                    current_level +=1
                elif t_check.token_type == TokenType.RPAREN:
                    current_level -=1
                if current_level == 0 and i_check < len(tokens) - 2: 
                    is_outer_pair = False 
                    break
            if is_outer_pair and current_level + (1 if tokens[0].token_type == TokenType.LPAREN else 0) - (1 if tokens[-1].token_type == TokenType.RPAREN else 0) == 0 : 
                 return parse_expression(tokens[1:-1])


    root_op_index: int = -1
    lowest_precedence: int = sys.maxsize + 1 
    current_paren_level: int = 0

    for i in range(len(tokens) - 1, -1, -1): 
        token = tokens[i]
        if token.token_type == TokenType.RPAREN:
            current_paren_level += 1
        elif token.token_type == TokenType.LPAREN:
            current_paren_level -= 1
            if current_paren_level < 0: 
                line = token.line if hasattr(token, 'line') else 'N/A'
                raise Exception(f"Parênteses desbalanceados na expressão, '(' extra ou ')' faltando perto de: '{token.value}' linha {line}")
        elif current_paren_level == 0 and token.token_type in PRECEDENCE_TABLE: 
            token_precedence = PRECEDENCE_TABLE[token.token_type]
            if token.token_type == TokenType.NOT: 
                is_potential_unary_not = (i == 0) or (tokens[i-1].token_type in OPERATOR_TOKENS or tokens[i-1].token_type == TokenType.LPAREN)
                if is_potential_unary_not:
                    pass 
            
            if token_precedence <= lowest_precedence:
                lowest_precedence = token_precedence
                root_op_index = i
    
    if current_paren_level != 0: 
        line = tokens[0].line if tokens and hasattr(tokens[0], 'line') else 'N/A'
        raise Exception(f"Parênteses desbalanceados na expressão. Nível final: {current_paren_level}. Perto de: '{tokens[0].value if tokens else ''}' linha {line}")

    if root_op_index != -1: 
        op_token = tokens[root_op_index]
        
        if op_token.token_type == TokenType.NOT:
            is_unary_not = (root_op_index == 0) or \
                           (tokens[root_op_index - 1].token_type in OPERATOR_TOKENS or \
                            tokens[root_op_index - 1].token_type == TokenType.LPAREN)
            
            if is_unary_not:
                right_tokens = tokens[root_op_index + 1:]
                if not right_tokens:
                    line = op_token.line if hasattr(op_token, 'line') else 'N/A'
                    raise Exception(f"Operador unário '{op_token.value}' na linha {line} requer um operando à direita.")
                return ExpressionOperation(op_token, None, parse_expression(right_tokens))

        left_tokens = tokens[:root_op_index]
        right_tokens = tokens[root_op_index + 1:]

        if not left_tokens:
            line = op_token.line if hasattr(op_token, 'line') else 'N/A'
            raise Exception(f"Operador binário '{op_token.value}' na linha {line} requer um operando à esquerda.")
        if not right_tokens:
            line = op_token.line if hasattr(op_token, 'line') else 'N/A'
            raise Exception(f"Operador binário '{op_token.value}' na linha {line} requer um operando à direita.")

        left_expr = parse_expression(left_tokens)
        right_expr = parse_expression(right_tokens)
        return ExpressionOperation(op_token, left_expr, right_expr)

    line_info = tokens[0].line if tokens and hasattr(tokens[0], 'line') else 'N/A'
    raise Exception(f"Estrutura de expressão inválida ou operador faltando perto de: '{tokens[0].value if tokens else ''}' na linha {line_info}. Tokens: {tokens}")


def type_from_literal(literal: Token) -> VariableType:
    if literal.token_type == TokenType.BOOLEAN:
        return VariableType.BOOLEAN
    elif literal.token_type == TokenType.RATIONAL:
        return VariableType.RATIONAL
    elif literal.token_type == TokenType.INTEGER:
        return VariableType.INTEGER
    elif literal.token_type == TokenType.STRING:
        return VariableType.STRING
    else:
        raise Exception(f"Tipo literal inválido '{literal.token_type}'")


def get_expression_type(expression: Expression | None, varbank: VariableBank) -> VariableType:
    if expression is None: 
        raise Exception("Tentativa de obter tipo de uma expressão nula (geralmente de um erro de parsing).")

    if isinstance(expression, ExpressionValue):
        if expression.literal.token_type == TokenType.IDENTIFIER:
            variable = varbank.get(expression.literal.value) 
            return variable.vartype
        elif expression.literal.token_type in LITERAL_TOKENS:
            return type_from_literal(expression.literal)
        else:
            raise Exception(f"Token não literal e não identificador '{expression.literal}' usado como valor")
    elif isinstance(expression, ExpressionOperation):
        op_type = expression.operator.token_type

        if op_type == TokenType.NOT and expression.left is None: 
            if expression.right is None: 
                raise Exception(f"Operador unário NOT sem operando à direita.")
            right_type = get_expression_type(expression.right, varbank)
            if right_type != VariableType.BOOLEAN:
                raise Exception(f"Operador unário NOT requer um operando booleano, obteve {right_type}.")
            return VariableType.BOOLEAN
        
        if expression.left is None or expression.right is None: 
             raise Exception(f"Operador binário {expression.operator.value} com operando(s) faltando.")

        left_type = get_expression_type(expression.left, varbank)
        right_type = get_expression_type(expression.right, varbank)

        if op_type in [TokenType.AND, TokenType.OR]:
            if left_type != VariableType.BOOLEAN or right_type != VariableType.BOOLEAN:
                raise Exception(f"Operadores lógicos '{expression.operator.value}' requerem operandos booleanos. Obtido: {left_type} e {right_type}")
            return VariableType.BOOLEAN
        elif op_type in [TokenType.EQUAL, TokenType.NOT_EQUAL]:
            if (left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES) or \
               (left_type == VariableType.STRING and right_type == VariableType.STRING) or \
               (left_type == VariableType.BOOLEAN and right_type == VariableType.BOOLEAN) or \
               (left_type == right_type): 
                return VariableType.BOOLEAN
            else:
                raise Exception(f"Comparação de igualdade/desigualdade ('{expression.operator.value}') entre tipos incompatíveis: {left_type} e {right_type}")
        elif op_type in [TokenType.GREATER, TokenType.LESS]: 
            if left_type not in NUMERIC_TYPES or right_type not in NUMERIC_TYPES:
                raise Exception(f"Operadores de comparação '{expression.operator.value}' requerem operandos numéricos. Obtido: {left_type} e {right_type}")
            return VariableType.BOOLEAN
        elif op_type in NUMERIC_OPERATOR_TOKENS: 
            if left_type not in NUMERIC_TYPES or right_type not in NUMERIC_TYPES:
                raise Exception(f"Operadores aritméticos ('{expression.operator.value}') requerem operandos numéricos. Obtido: {left_type} e {right_type}")
            if left_type == VariableType.RATIONAL or right_type == VariableType.RATIONAL:
                return VariableType.RATIONAL
            else:
                return VariableType.INTEGER
        else:
            raise Exception(f"Tipo de operador desconhecido ou não tratado na verificação de tipo de expressão: {op_type}")
    else:
        raise Exception(f"Tipo de expressão inválido '{type(expression)}' encontrado durante a verificação de tipo.")


def validate_expression(tokens: list[Token], varbank: VariableBank) -> None:
    for token in tokens:
        if token.token_type in INVALID_EXPRESSION_TOKENS:
            line = token.line if hasattr(token, 'line') else 'N/A'
            raise Exception(f"Token inválido '{token.value}' encontrado na expressão na linha {line}")

        if token.token_type == TokenType.IDENTIFIER:
            if not varbank.exists(token.value):
                line = token.line if hasattr(token, 'line') else 'N/A'
                raise Exception(f"Nenhuma variável chamada '{token.value}' foi declarada (usada na linha {line})")


def lang_type_to_java_type(lang_type: VariableType) -> str: 
    if lang_type == VariableType.STRING: return "String"
    elif lang_type == VariableType.INTEGER: return "int"
    elif lang_type == VariableType.RATIONAL: return "float" 
    elif lang_type == VariableType.BOOLEAN: return "boolean"
    else: raise Exception(f"Tipo de linguagem Prose desconhecido '{lang_type}' ao converter para Java.")


def render_expression_from_ast(expression: Expression | None, varbank: VariableBank) -> str:
    if expression is None:
        return "" 
    
    if isinstance(expression, ExpressionValue):
        return expression.literal.value
    elif isinstance(expression, ExpressionOperation):
        op_value = expression.operator.value
        if expression.operator.token_type == TokenType.NOT and expression.left is None:
            if op_value.lower() == "not": 
                op_value = "!"
            return f"{op_value}({render_expression_from_ast(expression.right, varbank)})"

        left_rendered = render_expression_from_ast(expression.left, varbank)
        right_rendered = render_expression_from_ast(expression.right, varbank)
        
        return f"({left_rendered} {op_value} {right_rendered})"
    else:
        raise Exception(f"Tipo de nó de expressão desconhecido ao renderizar: {type(expression)}")

def render_expression(tokens: list[Token]) -> str:
    return ' '.join([token.value for token in tokens])


@dataclass
class Branch:
    condition_tokens: list[Token] 
    content_elements: list 

    def __repr__(self) -> str:
        condition_str = f"COND({', '.join([repr(token) for token in self.condition_tokens])})" if self.condition_tokens else "COND()"
        content_str = f"CONTENT[{', '.join([repr(c) for c in self.content_elements])}]" if self.content_elements else "CONTENT[]"
        return f"BRANCH::{condition_str}=>{content_str}"

@dataclass
class StructureGroup: 
    structure_type: TokenType
    branches: list[Branch] 

    def __repr__(self) -> str:
        return f"SGROUP::{self.structure_type}{{{', '.join([repr(branch) for branch in self.branches])}}}"

@dataclass
class StatementGroup: 
    tokens: list[Token]

    def __repr__(self) -> str:
        return f"STGROUP::({', '.join([repr(token) for token in self.tokens])})"


@dataclass
class Statement: 
    original_tokens: list[Token] 

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}::{', '.join([repr(token) for token in self.original_tokens])}>"

    def validate_syntax(self) -> bool:
        return True 

    def render(self, varbank: VariableBank) -> str:
        return ""


class CreateStatement(Statement):
    def __init__(self, tokens: list[Token]):
        super().__init__(tokens)
        if not self.validate_syntax(): 
            line = tokens[0].line if tokens else 'N/A'
            raise Exception(f"Sintaxe inválida para declaração CREATE perto da linha {line}. Tokens: {tokens}")
        self.var_type_token: Token = tokens[1]
        self.is_constant: bool = tokens[2].value == 'constant'
        self.var_name: str = tokens[3].value
        self.expression_tokens = tokens[4:] if len(tokens) > 4 else None

    def validate_syntax(self) -> bool:
        return (
                len(self.original_tokens) >= 4
                and self.original_tokens[0].token_type == TokenType.CREATE
                and self.original_tokens[1].token_type == TokenType.TYPE
                and self.original_tokens[2].token_type == TokenType.VARTYPE
                and self.original_tokens[3].token_type == TokenType.IDENTIFIER
        )

    def render(self, varbank: VariableBank) -> str:
        var_type: VariableType
        if self.var_type_token.value == 'string': var_type = VariableType.STRING
        elif self.var_type_token.value == 'integer': var_type = VariableType.INTEGER
        elif self.var_type_token.value == 'rational': var_type = VariableType.RATIONAL
        elif self.var_type_token.value == 'boolean': var_type = VariableType.BOOLEAN
        else:
            raise Exception(f"Tipo de variável inesperado '{self.var_type_token.value}' na linha {self.var_type_token.line}")

        rendered_value_expr = None
        if self.expression_tokens:
            validate_expression(self.expression_tokens, varbank) 
            parsed_expr = parse_expression(self.expression_tokens)
            value_type = get_expression_type(parsed_expr, varbank)
            if value_type != var_type:
                if not (var_type == VariableType.RATIONAL and value_type == VariableType.INTEGER):
                    raise Exception(f"Não é possível atribuir valor do tipo {value_type} à variável '{self.var_name}' do tipo {var_type} na linha {self.original_tokens[0].line}")
            rendered_value_expr = render_expression_from_ast(parsed_expr, varbank)
        
        varbank.create(self.var_name, self.is_constant, var_type, rendered_value_expr)

        java_components = []
        if self.is_constant: java_components.append('final')
        java_components.append(lang_type_to_java_type(var_type))
        java_components.append(self.var_name)

        if rendered_value_expr is not None:
            java_components.append('=')
            java_components.append(rendered_value_expr)

        return f"{' '.join(java_components)};"


class WriteStatement(Statement):
    def __init__(self, tokens: list[Token]):
        super().__init__(tokens)
        if not self.validate_syntax():
            line = tokens[0].line if tokens else 'N/A'
            raise Exception(f"Sintaxe inválida para declaração WRITE perto da linha {line}. Tokens: {tokens}")
        self.expression_tokens = tokens[1:]
        if not self.expression_tokens:
            raise Exception(f"Declaração 'write' vazia na linha {tokens[0].line if tokens else 'N/A'}")

    def validate_syntax(self) -> bool:
        return (len(self.original_tokens) >= 2 and self.original_tokens[0].token_type == TokenType.WRITE)

    def render(self, varbank: VariableBank) -> str:
        validate_expression(self.expression_tokens, varbank)
        parsed_expr = parse_expression(self.expression_tokens)
        rendered_expr = render_expression_from_ast(parsed_expr, varbank)
        return f"System.out.print({rendered_expr});"


class SetStatement(Statement):
    def __init__(self, tokens: list[Token]):
        super().__init__(tokens)
        if not self.validate_syntax():
            line = tokens[0].line if tokens else 'N/A'
            raise Exception(f"Sintaxe inválida para declaração SET perto da linha {line}. Tokens: {tokens}")
        self.var_name_token: Token = tokens[1]
        self.expression_tokens = tokens[3:]
        if not self.expression_tokens:
            raise Exception(f"Declaração 'set' para '{self.var_name_token.value}' sem valor na linha {tokens[0].line if tokens else 'N/A'}")

    def validate_syntax(self) -> bool:
        return (
                len(self.original_tokens) >= 4 
                and self.original_tokens[0].token_type == TokenType.SET
                and self.original_tokens[1].token_type == TokenType.IDENTIFIER
                and self.original_tokens[2].token_type == TokenType.TO
        )

    def render(self, varbank: VariableBank) -> str:
        var_name = self.var_name_token.value
        validate_expression(self.expression_tokens, varbank)
        
        variable_in_bank = varbank.get(var_name) 
        if variable_in_bank.constant:
            raise Exception(f"Não é possível alterar o valor da constante '{var_name}' na linha {self.original_tokens[0].line}")

        parsed_expr = parse_expression(self.expression_tokens)
        value_type = get_expression_type(parsed_expr, varbank)

        if value_type != variable_in_bank.vartype:
            if not (variable_in_bank.vartype == VariableType.RATIONAL and value_type == VariableType.INTEGER):
                 raise Exception(f"Não é possível atribuir valor do tipo {value_type} à variável '{var_name}' do tipo {variable_in_bank.vartype} na linha {self.original_tokens[0].line}")

        rendered_value_expr = render_expression_from_ast(parsed_expr, varbank)
        varbank.redefine(var_name, rendered_value_expr) 

        return f"{var_name} = {rendered_value_expr};"


class ReadStatement(Statement):
    def __init__(self, tokens: list[Token]):
        super().__init__(tokens)
        if not self.validate_syntax():
            line = tokens[0].line if tokens else 'N/A'
            raise Exception(f"Sintaxe inválida para declaração READ perto da linha {line}. Tokens: {tokens}")
        self.var_name_token: Token = tokens[1]

    def validate_syntax(self) -> bool:
        return (
                len(self.original_tokens) == 2 and
                self.original_tokens[0].token_type == TokenType.READ and
                self.original_tokens[1].token_type == TokenType.IDENTIFIER
        )

    def render(self, varbank: VariableBank) -> str:
        var_name = self.var_name_token.value
        variable: Variable = varbank.get(var_name)

        if variable.constant:
            raise Exception(f"Não é possível ler valor para a constante '{var_name}' na linha {self.original_tokens[0].line}")
        
        varbank.redefine(var_name, "[[[RUNTIME_INPUT]]]") 

        method: str
        if variable.vartype == VariableType.STRING: method = "nextLine"
        elif variable.vartype == VariableType.INTEGER: method = "nextInt"
        elif variable.vartype == VariableType.RATIONAL: method = "nextFloat"
        elif variable.vartype == VariableType.BOOLEAN: method = "nextBoolean"
        else:
            raise Exception(f"Tipo de variável desconhecido '{variable.vartype}' para leitura em '{var_name}' na linha {self.original_tokens[0].line}")
        
        line_to_return = f"{var_name} = scanner.{method}();"
        return line_to_return


@dataclass
class Structure: 
    structure_type_token: Token 
    branches: list[Branch] 

    def __repr__(self) -> str:
        return f"<STRUCTURE {self.structure_type_token.token_type}::[{', '.join([repr(branch) for branch in self.branches])}]>"

    def render(self, varbank: VariableBank) -> list[str]:
        return [] 

    def render_branch_content(self, varbank: VariableBank, branch_content_elements: list) -> list[str]:
        lines = []
        varbank.start_scope()
        for item in branch_content_elements:
            if isinstance(item, Statement):
                rendered_statement = item.render(varbank)
                for line_part in rendered_statement.splitlines():
                    lines.append(f"    {line_part}")
            elif isinstance(item, Structure):
                nested_lines = item.render(varbank)
                for line in nested_lines:
                    lines.append(f"    {line}")
            else:
                raise Exception(f"Item de branch inesperado encontrado durante a renderização: {type(item)} - {item}")
        varbank.end_scope()
        return lines


class IfStructure(Structure):
    def render(self, varbank: VariableBank) -> list[str]:
        lines = []
        if not self.branches: return lines

        first_branch = self.branches[0]
        if not first_branch.condition_tokens: 
            raise Exception(f"Estrutura IF (linha {self.structure_type_token.line}) sem condição no primeiro branch.")
        validate_expression(first_branch.condition_tokens, varbank) 
        parsed_cond = parse_expression(first_branch.condition_tokens)
        cond_type = get_expression_type(parsed_cond, varbank)
        if cond_type != VariableType.BOOLEAN:
            raise Exception(f"Condição do IF (linha {self.structure_type_token.line}) deve ser booleana, obteve {cond_type}.")
        
        rendered_condition = render_expression_from_ast(parsed_cond, varbank)
        lines.append(f"if ({rendered_condition}) {OPEN_BRACKET}")
        lines.extend(self.render_branch_content(varbank, first_branch.content_elements))

        for i in range(1, len(self.branches)):
            branch = self.branches[i]
            if branch.condition_tokens: 
                validate_expression(branch.condition_tokens, varbank)
                parsed_elif_cond = parse_expression(branch.condition_tokens)
                elif_cond_type = get_expression_type(parsed_elif_cond, varbank)
                if elif_cond_type != VariableType.BOOLEAN:
                     raise Exception(f"Condição do ELIF (perto da linha {branch.condition_tokens[0].line}) deve ser booleana, obteve {elif_cond_type}.")
                rendered_elif_condition = render_expression_from_ast(parsed_elif_cond, varbank)
                lines.append(f"{CLOSE_BRACKET} else if ({rendered_elif_condition}) {OPEN_BRACKET}")
            else: 
                lines.append(f"{CLOSE_BRACKET} else {OPEN_BRACKET}")
            lines.extend(self.render_branch_content(varbank, branch.content_elements))

        lines.append(CLOSE_BRACKET)
        return lines


class WhileStructure(Structure):
    def render(self, varbank: VariableBank) -> list[str]:
        lines = []
        if not self.branches or not self.branches[0].condition_tokens:
            raise Exception(f"Estrutura WHILE (linha {self.structure_type_token.line}) sem condição.")
        
        branch = self.branches[0]
        validate_expression(branch.condition_tokens, varbank)
        parsed_cond = parse_expression(branch.condition_tokens)
        cond_type = get_expression_type(parsed_cond, varbank)
        if cond_type != VariableType.BOOLEAN:
            raise Exception(f"Condição do WHILE (linha {self.structure_type_token.line}) deve ser booleana, obteve {cond_type}.")

        rendered_condition = render_expression_from_ast(parsed_cond, varbank)
        lines.append(f"while ({rendered_condition}) {OPEN_BRACKET}")
        lines.extend(self.render_branch_content(varbank, branch.content_elements))
        lines.append(CLOSE_BRACKET)
        return lines


class DoWhileStructure(Structure):
    def render(self, varbank: VariableBank) -> list[str]:
        lines = []
        if not self.branches or not self.branches[0].condition_tokens: 
             raise Exception(f"Estrutura DO-WHILE (linha {self.structure_type_token.line}) sem condição.")

        branch = self.branches[0] 
        validate_expression(branch.condition_tokens, varbank)
        parsed_cond = parse_expression(branch.condition_tokens)
        cond_type = get_expression_type(parsed_cond, varbank)
        if cond_type != VariableType.BOOLEAN:
            raise Exception(f"Condição do DO-WHILE (linha {branch.condition_tokens[0].line}) deve ser booleana, obteve {cond_type}.")

        rendered_condition = render_expression_from_ast(parsed_cond, varbank)
        lines.append(f"do {OPEN_BRACKET}")
        lines.extend(self.render_branch_content(varbank, branch.content_elements))
        lines.append(f"{CLOSE_BRACKET} while ({rendered_condition});")
        return lines


def find_next_token(tokens: list[Token], token_type: TokenType, offset: int) -> int:
    for i in range(offset, len(tokens)):
        if tokens[i].token_type == token_type:
            return i
    return -1


def group_structures(tokens: list[Token]) -> list:
    i = 0
    groups = [] 
    
    while i < len(tokens):
        token = tokens[i]
        line_info = token.line if hasattr(token, 'line') else 'N/A'

        if token.token_type == TokenType.IF:
            if_branches = []
            
            i += 1 
            then_idx = find_next_token(tokens, TokenType.THEN, i)
            if then_idx == -1: raise Exception(f"IF na linha {line_info} sem THEN.")
            condition = tokens[i:then_idx]
            if not condition: raise Exception(f"Condição do IF vazia na linha {line_info}.")
            i = then_idx + 1 
            
            if_body_tokens_start = i
            if_nesting_level = 0
            current_branch_body = []

            while i < len(tokens):
                current_token_for_body = tokens[i]
                if current_token_for_body.token_type in [TokenType.IF, TokenType.WHILE, TokenType.DO]: 
                    if_nesting_level +=1
                elif current_token_for_body.token_type == TokenType.END:
                    if if_nesting_level == 0: break 
                    if_nesting_level -=1
                elif current_token_for_body.token_type in [TokenType.ELIF, TokenType.ELSE] and if_nesting_level == 0:
                    break 

                current_branch_body.append(current_token_for_body)
                i += 1
            
            if i >= len(tokens) and if_nesting_level != 0: 
                 raise Exception(f"Estrutura IF iniciada na linha {line_info} não foi fechada corretamente (END faltando ou aninhamento incorreto).")

            if_branches.append(Branch(condition_tokens=condition, content_elements=group_structures(current_branch_body))) 
            
            while i < len(tokens) and tokens[i].token_type in [TokenType.ELIF, TokenType.ELSE]:
                branch_token = tokens[i]
                current_branch_body = []
                condition = []

                if branch_token.token_type == TokenType.ELIF:
                    i += 1 
                    then_idx = find_next_token(tokens, TokenType.THEN, i)
                    if then_idx == -1: raise Exception(f"ELIF na linha {branch_token.line} sem THEN.")
                    condition = tokens[i:then_idx]
                    if not condition: raise Exception(f"Condição do ELIF vazia na linha {branch_token.line}.")
                    i = then_idx + 1 
                else: 
                    i += 1 
                    
                elif_else_body_start = i
                if_nesting_level = 0 
                while i < len(tokens):
                    current_token_for_body = tokens[i]
                    if current_token_for_body.token_type in [TokenType.IF, TokenType.WHILE, TokenType.DO]:
                        if_nesting_level +=1
                    elif current_token_for_body.token_type == TokenType.END:
                        if if_nesting_level == 0: break 
                        if_nesting_level -=1
                    elif current_token_for_body.token_type in [TokenType.ELIF, TokenType.ELSE] and if_nesting_level == 0:
                        raise Exception(f"ELIF/ELSE inesperado na linha {current_token_for_body.line} dentro de um bloco ELIF/ELSE não fechado.")
                    current_branch_body.append(current_token_for_body)
                    i += 1
                
                if i >= len(tokens) and if_nesting_level != 0:
                     raise Exception(f"Estrutura ELIF/ELSE iniciada na linha {branch_token.line} não foi fechada corretamente.")

                if_branches.append(Branch(condition_tokens=condition, content_elements=group_structures(current_branch_body)))

            if i >= len(tokens) or tokens[i].token_type != TokenType.END:
                raise Exception(f"Estrutura IF iniciada na linha {line_info} sem END correspondente.")
            i += 1 
            groups.append(StructureGroup(structure_type=token.token_type, branches=if_branches))

        elif token.token_type == TokenType.WHILE: 
            i += 1 
            do_idx = find_next_token(tokens, TokenType.DO, i)
            if do_idx == -1: raise Exception(f"WHILE na linha {line_info} sem DO.")
            condition = tokens[i:do_idx]
            if not condition: raise Exception(f"Condição do WHILE vazia na linha {line_info}.")
            i = do_idx + 1 

            body_tokens_start = i
            nesting_level = 0
            body_tokens = []
            while i < len(tokens):
                current_token_for_body = tokens[i]
                if current_token_for_body.token_type in [TokenType.IF, TokenType.WHILE, TokenType.DO]:
                    nesting_level +=1
                elif current_token_for_body.token_type == TokenType.END:
                    if nesting_level == 0: break
                    nesting_level -=1
                body_tokens.append(current_token_for_body)
                i += 1
            
            if i >= len(tokens) or tokens[i].token_type != TokenType.END:
                raise Exception(f"Estrutura WHILE iniciada na linha {line_info} sem END correspondente.")
            i += 1 
            
            branch = Branch(condition_tokens=condition, content_elements=group_structures(body_tokens))
            groups.append(StructureGroup(structure_type=token.token_type, branches=[branch]))

        elif token.token_type == TokenType.DO: 
            i += 1 
            body_tokens_start = i
            nesting_level = 0
            body_tokens = []
            
            while i < len(tokens):
                current_token_for_body = tokens[i]
                if current_token_for_body.token_type in [TokenType.IF, TokenType.WHILE]: 
                    nesting_level +=1
                elif current_token_for_body.token_type == TokenType.END: 
                    nesting_level -=1
                elif current_token_for_body.token_type == TokenType.WHILE and nesting_level == 0: 
                    break
                body_tokens.append(current_token_for_body)
                i += 1
            
            if i >= len(tokens) or tokens[i].token_type != TokenType.WHILE:
                raise Exception(f"DO na linha {line_info} sem WHILE correspondente no mesmo nível.")
            i += 1 

            semicolon_idx = find_next_token(tokens, TokenType.SEMICOLON, i)
            if semicolon_idx == -1: raise Exception(f"Condição do DO-WHILE (linha {tokens[i-1].line}) não terminada com ';'.")
            condition = tokens[i:semicolon_idx]
            if not condition: raise Exception(f"Condição do DO-WHILE vazia (linha {tokens[i-1].line}).")
            i = semicolon_idx + 1 
            
            branch = Branch(condition_tokens=condition, content_elements=group_structures(body_tokens))
            groups.append(StructureGroup(structure_type=TokenType.DO, branches=[branch]))
        
        else: 
            groups.append(token)
            i += 1
            
    return groups


def group_statements(items: list) -> list:
    if not items:
        return []

    processed_elements = []
    i = 0
    while i < len(items):
        item = items[i]

        if isinstance(item, StructureGroup):
            for branch in item.branches:
                branch.content_elements = group_statements(branch.content_elements)
            processed_elements.append(item)
            i += 1
        elif isinstance(item, Token):
            current_statement_tokens = []
            start_statement_idx = i
            semicolon_found_at = -1
            
            temp_idx_for_semicolon_search = start_statement_idx
            while temp_idx_for_semicolon_search < len(items):
                if not isinstance(items[temp_idx_for_semicolon_search], Token):
                    line_info = items[start_statement_idx].line if hasattr(items[start_statement_idx], 'line') else 'N/A'
                    raise Exception(f"Declaração iniciada perto da linha {line_info} interrompida por uma estrutura antes de encontrar ';'.")
                
                token_in_stmt = items[temp_idx_for_semicolon_search]
                current_statement_tokens.append(token_in_stmt)
                if token_in_stmt.token_type == TokenType.SEMICOLON:
                    semicolon_found_at = temp_idx_for_semicolon_search
                    break
                temp_idx_for_semicolon_search += 1
            
            if semicolon_found_at == -1:
                line_info = items[start_statement_idx].line if hasattr(items[start_statement_idx], 'line') else 'N/A'
                raise Exception(f"Declaração iniciada perto da linha {line_info} não terminada com ';'.")

            processed_elements.append(StatementGroup(current_statement_tokens[:-1]))
            i = semicolon_found_at + 1 
        else:
            raise Exception(f"Item inesperado '{type(item)}' encontrado durante o agrupamento de declarações.")
            
    return processed_elements


def build_statement(group: StatementGroup) -> Statement:
    if not group.tokens:
        raise Exception("Tentativa de construir declaração a partir de um grupo de tokens vazio.")
        
    first_token = group.tokens[0]
    if first_token.token_type == TokenType.CREATE: return CreateStatement(group.tokens)
    elif first_token.token_type == TokenType.WRITE: return WriteStatement(group.tokens)
    elif first_token.token_type == TokenType.READ: return ReadStatement(group.tokens)
    elif first_token.token_type == TokenType.SET: return SetStatement(group.tokens)
    else:
        line = first_token.line if hasattr(first_token, 'line') else 'N/A'
        raise Exception(f"Tipo de token inesperado '{first_token.token_type}' no início de uma declaração na linha {line}")


def synthesize_statements(items: list) -> list: 
    elements = []
    for item in items:
        if isinstance(item, StatementGroup):
            elements.append(build_statement(item))
        elif isinstance(item, StructureGroup):
            new_branches = []
            for branch_group in item.branches:
                synthesized_content_elements = synthesize_statements(branch_group.content_elements)
                new_branches.append(Branch(
                    condition_tokens=branch_group.condition_tokens, 
                    content_elements=synthesized_content_elements
                ))
            
            structure_node: Structure
            # Assume que o primeiro token da estrutura original pode ser usado para linha/coluna, se necessário
            # Aqui, um token dummy é criado para o structure_type_token, mas idealmente viria do token original (IF, WHILE, DO)
            first_token_of_structure = Token(item.structure_type, item.structure_type.name.lower(), 0,0) # Token dummy
            # Se os tokens originais do início da estrutura estiverem disponíveis, use-os.
            # Por exemplo, se StructureGroup armazenasse o token original (IF, WHILE, DO).

            if item.structure_type == TokenType.IF:
                structure_node = IfStructure(structure_type_token=first_token_of_structure, branches=new_branches) 
            elif item.structure_type == TokenType.DO: 
                structure_node = DoWhileStructure(structure_type_token=first_token_of_structure, branches=new_branches)
            elif item.structure_type == TokenType.WHILE: 
                structure_node = WhileStructure(structure_type_token=first_token_of_structure, branches=new_branches)
            else:
                raise Exception(f"Tipo de StructureGroup desconhecido: {item.structure_type}")
            elements.append(structure_node)
        else:
            raise Exception(f"Item inesperado '{type(item)}' encontrado durante a síntese.")
            
    return elements

