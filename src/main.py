from lexer import Lexer
from parsa import *
from render import VariableBank
import pprint
import sys
from os import path
import subprocess
import os
import shutil

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True

EXTENSION = "prose"
VERSION = "1.0.4" 
USAGE = f"Usage: ProseLang <input_file.{EXTENSION}>"

# Java executables are now expected to be in the system PATH
JAVAC_COMMAND = "javac"
JAVA_COMMAND = "java"

def main():
    #print(f"Lang v{VERSION}")

    if len(sys.argv) < 2:
        print(f"Missing argument <file.{EXTENSION}>")
        print(USAGE)
        return

    file_path = sys.argv[1]

    if not file_path.endswith(f".{EXTENSION}"):
        print(f"File has the wrong extension; should end with '.{EXTENSION}'")
        return

    input_file_dir = path.dirname(file_path)
    if not input_file_dir:
        input_file_dir = "."

    input_file_basename = path.basename(file_path)

    if len(input_file_basename) < len(EXTENSION) + 2:
        print("Invalid file name provided")
        return

    program_name = input_file_basename[:-len(EXTENSION) - 1]
    
    procache_dir = os.path.join(input_file_dir, "procache")
    try:
        os.makedirs(procache_dir, exist_ok=True)
    except OSError as e_mkdir:
        print(f"Erro ao criar o diretório procache '{procache_dir}': {e_mkdir}")
        return
        
    output_path = os.path.join(procache_dir, f"{program_name}.java")
    java_classpath_dir = procache_dir

    try:
        code: str
        try:
            with open(file_path, 'r') as file:
                code = file.read()
        except FileNotFoundError:
            print(f"O arquivo '{file_path}' não foi encontrado.")
            return
        except Exception as e_file:
            print(f"Erro ao ler o arquivo '{file_path}': {e_file}")
            return

        lexer = Lexer()
        tokens = lexer.tokenize(code)
        grouped_tokens = group_statements(group_structures(tokens))
        syntax_tree = synthesize_statements(grouped_tokens)

        varbank = VariableBank()
        lines = []

        for syntax_item in syntax_tree:
            if isinstance(syntax_item, Statement):
                lines.append(syntax_item.render(varbank))
            elif isinstance(syntax_item, Structure):
                lines.extend(syntax_item.render(varbank))
            else:
                raise Exception(f"Unexpected syntax item '{syntax_item}'")

        java_code = "\n".join(lines)

        try:
            with open(output_path, 'w') as output_file:
                output_file.write(f"import java.util.Scanner;\n\n")
                output_file.write(f"public class {program_name} {{\n")
                output_file.write("public static void main(String[] args) {\n")
                output_file.write("Scanner scanner = new Scanner(System.in);\n")
                output_file.write(java_code)
                output_file.write("\nscanner.close();\n")
                output_file.write("}}\n")
        except Exception as e_write_java:
            print(f"Erro ao escrever o arquivo Java de saída '{output_path}': {e_write_java}")
            return

        compile_command = [JAVAC_COMMAND, output_path]
        execute_command = [JAVA_COMMAND, "-cp", java_classpath_dir, program_name]

        #print(f"Compilando com: {' '.join(compile_command)}")
        subprocess.run(compile_command, check=True)
        #print(f"Arquivo {output_path} compilado com sucesso.")

        #print(f"Executando com: {' '.join(execute_command)}")
        result = subprocess.run(execute_command, check=True, capture_output=True, text=True)

        print(result.stdout)

    except subprocess.CalledProcessError as e:
       #print(f"Erro ao compilar ou executar o arquivo Java: {e}")
        stdout_decoded = e.stdout.decode(errors='replace') if isinstance(e.stdout, bytes) else e.stdout
        stderr_decoded = e.stderr.decode(errors='replace') if isinstance(e.stderr, bytes) else e.stderr
        if stdout_decoded:
            print(f"Saída do erro (stdout): {stdout_decoded}")
        if stderr_decoded:
            print(f"Saída do erro (stderr): {stderr_decoded}")
    except FileNotFoundError as e_fnf:
        print(f"Erro: Comando não encontrado ({e_fnf.filename}). Verifique se o Java (JDK) está instalado e configurado corretamente no PATH do sistema.")
        print(f"Detalhe do erro: {e_fnf}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao processar o arquivo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
