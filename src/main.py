from lexer import Lexer
from parsa import *
import pprint
import sys
from os import path
import subprocess

from src.execute import Executor

EXTENSION = "lang"


def print_(code):
    lexer = Lexer()
    tokens = lexer.tokenize(code)

    print("• [TOKENS]")
    pprint.pp(tokens)
    print()

    print("• [TOKEN GROUPS]")
    token_groups = group_tokens(tokens)
    pprint.pp(token_groups)
    print()

    print("• [RENDERED TOKEN GROUPS]")
    rendered_tokens = render_groups(token_groups)
    pprint.pp(rendered_tokens)
    print()

    print("• [SYNTHESIZED GROUPS]")
    synthesize_statements(rendered_tokens)
    pprint.pp(rendered_tokens)


def main():
    if len(sys.argv) < 2:
        print(f"Missing argument <file.{EXTENSION}>")
        return

    file_path = sys.argv[1]

    if not file_path.endswith(f".{EXTENSION}"):
        print(f"File has the wrong extension; should end with .{EXTENSION}")
        return

    path_dirname = path.dirname(file_path)
    path_basename = path.basename(file_path)

    if len(path_basename) < len(EXTENSION) + 2:
        print("Invalid file name")
        return

    program_name = path_basename[:-len(EXTENSION) - 1]
    output_path = path.join(path_dirname, f"{program_name}.java")

    try:
        code: str
        with open(file_path, 'r') as file:
            code = file.read()

        lexer = Lexer()
        tokens = lexer.tokenize(code)
        token_groups = group_tokens(tokens)
        rendered_tokens = render_groups(token_groups)
        synthesize_statements(rendered_tokens)

        pprint.pp(rendered_tokens)

        print("Output:", output_path)

        executor = Executor()

        for statement in rendered_tokens:
            executor.execute(statement)

        java_code = executor.generate_java_code(rendered_tokens)

        with open(output_path, 'w') as output_file:
            # Preamble
            output_file.write(f"import java.util.Scanner;\n\n")
            output_file.write(f"public class {program_name} {{\n")
            output_file.write("public static void main(String[] args) {\n")
            output_file.write("Scanner scanner = new Scanner(System.in);\n")

            # Código gerado dinamicamente
            output_file.write(java_code)

            # Epilogue
            output_file.write("\nscanner.close();\n")
            output_file.write("}}\n")

        compile_command = ["javac", output_path]
        subprocess.run(compile_command, check=True)
        print(f"Arquivo {output_path} compilado com sucesso.")

        # Executar o arquivo Java compilado
        execute_command = ["java", "-cp", path_dirname, program_name]
        result = subprocess.run(execute_command, check=True, capture_output=True, text=True)

        print("Variaveis:\n")
        pprint.pp(executor.variables)
        print()

        print("Saída da execução do programa Java:\n")
        print(result.stdout)

    except FileNotFoundError:
        print(f"O arquivo {file_path} não foi encontrado.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao compilar ou executar o arquivo Java: {e}")
        print(f"Saída do erro: {e.output}")
    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo: {e}")
        raise e


if __name__ == "__main__":
    main()
