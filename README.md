# linguagem (sem nome)

## Fluxo da aplicação

### Lexer(Analisador Léxico):
- Inicialização (__init__): Configura as especificações dos tokens e palavras reservadas.
- Tokenização (tokenize): Inicia o processo de análise léxica.
  ##### Token
  - Type
  - Value
  - Position[Line, Column]
- Avanço (advance): Avança `steps` posições no texto.
- Próximo Token (next_token): Determina e retorna o próximo token válido.
- Log (log_token): Registra os tokens no log

### Main:
- Registra os tokens de acordo com a classe criada

