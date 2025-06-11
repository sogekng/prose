import sys
import os
import subprocess
from util.token import TokenType
from lexer import Lexer
from parsa import Parser, ParseException, FunctionDeclaration, ExpressionStatement
from render import VariableBank

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True

EXTENSION = "prose"
VERSION = "1.0.4"
USAGE = f"Uso: python main.py <arquivo_de_entrada.{EXTENSION}>"

JAVAC_COMMAND = "javac"
JAVA_COMMAND = "java"

def main():
    if len(sys.argv) < 2:
        print(f"Argumento faltando: <arquivo.{EXTENSION}>")
        print(USAGE)
        return

    file_path = sys.argv[1]

    if not file_path.endswith(f".{EXTENSION}"):
        print(f"O arquivo deve ter a extensão '.{EXTENSION}'")
        return

    input_file_dir = os.path.dirname(file_path) or "."
    input_file_basename = os.path.basename(file_path)
    program_name = os.path.splitext(input_file_basename)[0]
    
    procache_dir = os.path.join(input_file_dir, "procache")
    os.makedirs(procache_dir, exist_ok=True)
        
    output_path = os.path.join(procache_dir, f"{program_name}.java")

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()

        lexer = Lexer()
        tokens = lexer.tokenize(code)
        
        parser = Parser(tokens)
        syntax_tree = parser.parse()

        varbank = VariableBank()
        function_definitions = []
        main_method_statements = []

        for node in syntax_tree:
            if isinstance(node, FunctionDeclaration):
                function_definitions.append(node.render(varbank))
            else:
                main_method_statements.append(node.render(varbank))
        
        java_functions_code = "\n\n".join(function_definitions)
        java_main_code = "\n".join(main_method_statements)

        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write("import java.util.Scanner;\n")
            output_file.write("import java.util.ArrayList;\n")
            output_file.write("import java.util.Arrays;\n\n")
            
            output_file.write(f"public class {program_name} {{\n\n")

            if java_functions_code:
                output_file.write(java_functions_code)
                output_file.write("\n\n")

            output_file.write("    public static void main(String[] args) {\n")
            output_file.write("        try (Scanner scanner = new Scanner(System.in)) {\n")
            for line in java_main_code.split('\n'):
                 output_file.write(f"            {line}\n")
            output_file.write("        }\n")
            output_file.write("    }\n")
            output_file.write("}\n")

        compile_process = subprocess.run(
            [JAVAC_COMMAND, output_path], capture_output=True, text=True, encoding='utf-8'
        )
        if compile_process.returncode != 0:
            print("--- Erro de Compilação Java ---")
            print(compile_process.stderr)
            return
        
        subprocess.run(
            [JAVA_COMMAND, "-cp", procache_dir, program_name], 
            text=True, encoding='utf-8', check=True
        )

    except FileNotFoundError:
        print(f"Erro: Comando não encontrado. Verifique se o Java (JDK) está instalado e no PATH.")
    except ParseException as e:
        print("--- Erro de Análise Sintática ---")
        print(e)
    except subprocess.CalledProcessError as e:
        print("\n--- Erro na Execução do Código ---")
        print(e.stderr)
    except Exception as e:
        print(f"\n--- Ocorreu um erro inesperado ---")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()