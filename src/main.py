import os
import sys
from util.token import TokenType
from lexer import Lexer
from parsa import Parser
from prose_ast import ParseException, RuntimeException
from interpreter import Interpreter

EXTENSION = "prose"
VERSION = "2.0.0"
USAGE = f"""Uso:
  prose <arquivo.prose>   (para executar um arquivo)
  prose                   (para iniciar o modo interativo - REPL)"""

def run(code: str, interpreter: Interpreter, base_path: str):
    try:
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        
        parser = Parser(tokens, interpreter.environment)
        syntax_tree = parser.parse()

        interpreter.run(syntax_tree, base_path)

    except (ParseException, RuntimeException) as e:
        print(e)
    except Exception as e:
        print(f"Erro inesperado: {e}")

def run_file(file_path: str):
    interpreter = Interpreter()
    base_path = os.path.dirname(os.path.abspath(file_path))
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
        run(code, interpreter, base_path)
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em '{file_path}'")

def run_prompt():
    interpreter = Interpreter()
    base_path = os.getcwd()
    print(f"Prose Lang v{VERSION}")
    
    while True:
        try:
            line = input("prose > ")
            if line.strip().lower() in ['exit()', 'exit']: break
            if line.strip(): run(line, interpreter, base_path)
        except (EOFError, KeyboardInterrupt):
            break

def main():
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        run_prompt()

if __name__ == "__main__":
    main()
