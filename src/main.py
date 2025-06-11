from lexer import Lexer
from parsa import Parser, ParseException
from render import VariableBank
import sys
import os
import subprocess

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
        java_lines = [node.render(varbank) for node in syntax_tree]
        java_code = "\n".join(java_lines)

        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write("import java.util.Scanner;\n")
            output_file.write("import java.util.ArrayList;\n")
            output_file.write("import java.util.Arrays;\n\n")
            
            output_file.write(f"public class {program_name} {{\n")
            output_file.write("    public static void main(String[] args) {\n")
            output_file.write("        try (Scanner scanner = new Scanner(System.in)) {\n")
            for line in java_code.split('\n'):
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

        execute_process = subprocess.run(
            [JAVA_COMMAND, "-cp", procache_dir, program_name], 
            capture_output=True, text=True, encoding='utf-8', check=True
        )
        
        print(execute_process.stdout, end='')

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