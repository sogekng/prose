# linguagem (sem nome)

## Fluxo da aplicação

### Lexer(Analisador Léxico):
- Inicialização (__init__): Configura as especificações dos tokens e palavras reservadas.
- Tokenização (tokenize): Inicia o processo de análise léxica.
  ##### Token
  - Type
  - Value
  - Line
  - Column
- Avanço (advance): Move para o próximo caractere.
- Próximo Token (next_token): Determina e retorna o próximo token válido.
- Log (log_token): Registra os tokens no log

### Main:
- Registra os tokens de acordo com a classe criada

