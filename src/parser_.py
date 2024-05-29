class Parser:
    """
    Classe Parser que inclui operações aritméticas, parênteses 
    e possivelmente atribuições de variáveis.
    
    Atributos:
        tokens (list): Lista de tokens a serem analisados.
        current_token (Token): Token atual em processamento.
        token_index (int): Índice do token atual na lista.
    """
    def __init__(self, tokens):
        """
        Inicializa o analisador com uma lista de tokens e prepara o primeiro token.
        
        Args:
            tokens (list): Lista de tokens obtidos de um analisador léxico.
        """
        self.tokens = tokens
        self.current_token = None
        self.token_index = -1
        self.advance()

    def advance(self):
        """
        Avança o 'token_index' para apontar para o próximo token, define 'current_token' como None
        se não houver mais tokens.
        """
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = None

    def parse(self):
        """
        Lida com a análise de todo o programa, incluindo declarações e expressões.
        
        Return: 
            O resultado da expressão ou estrutura analisada.
        
        Exception: 
            Se houver erros de sintaxe ou tokens inesperados.
        """
        result = self.expr()
        if self.current_token and self.current_token.type == 'SEMICOLON':
            self.eat('SEMICOLON')
        if self.current_token is not None:
            raise Exception(f"Token inesperado {self.current_token.type} após a expressão")
        return result

    def eat(self, token_type):
        """
        Consome um token do tipo esperado ou lança uma exceção se o próximo token não for desse tipo.
        
        Args: 
            token_type (str): O tipo de token esperado para consumir.
        
        Exception: 
            Se o token atual não corresponder ao tipo esperado.
        """
        if self.current_token and self.current_token.type == token_type:
            self.advance()
        else:
            raise Exception(f"Token esperado {token_type}, obtido {self.current_token.type}")

    def expr(self):
        """
        Analisa uma expressão que pode incluir operadores de adição e subtração.
        
        Return:
            int: O resultado calculado da expressão.
        """
        result = self.term()
        while self.current_token is not None and self.current_token.type in ['ADDITION', 'SUBTRACTION']:
            if self.current_token.type == 'ADDITION':
                self.eat('ADDITION')
                result += self.term()
            elif self.current_token.type == 'SUBTRACTION':
                self.eat('SUBTRACTION')
                result -= self.term()
        return result

    def term(self):
        """
        Analisa um termo que pode incluir operadores de multiplicação e divisão.
        
        Return:
            int: O resultado calculado do termo.
        
        Exception: 
            Se o divisor for zero durante uma divisão, evitando erro de divisão por zero.
        """
        result = self.factor()
        while self.current_token is not None and self.current_token.type in ['MULTIPLICATION', 'DIVISION']:
            if self.current_token.type == 'MULTIPLICATION':
                self.eat('MULTIPLICATION')
                result *= self.factor()
            elif self.current_token.type == 'DIVISION':
                self.eat('DIVISION')
                divisor = self.factor()
                if divisor == 0:
                    raise Exception('Divisão por zero')
                result /= divisor
        return result

    def factor(self):
        """
        Analisa um fator, que pode ser um número ou uma expressão aninhada entre parênteses.
        
        Return:
            int: O valor numérico do fator.
        
        Exception: 
            Se a sintaxe for inválida ou o fator não for um número ou parênteses.
        """
        token = self.current_token
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return int(token.value)
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            result = self.expr()
            self.eat('RPAREN')
            return result
        else:
            raise Exception('Sintaxe inválida')
