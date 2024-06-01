from lexer import Lexer
import parsa
import pprint
import sys
from os import path


EXTENSION = "lang"


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

        print("• [TOKENS]")

        pprint.pp(tokens)

        print()

        print("• [TOKEN GROUPS]")

        token_groups = parsa.group_tokens(tokens)
        pprint.pp(token_groups)

        print()

        print("• [RENDERED TOKEN GROUPS]")

        rendered_tokens = parsa.render_groups(token_groups)
        pprint.pp(rendered_tokens)

        print()

        print("• [SYNTHESIZED GROUPS]")

        parsa.synthesize_statements(rendered_tokens)
        pprint.pp(rendered_tokens)

        print("Output:", output_path)

        with open(output_path, 'w') as output_file:
            # Preamble
            output_file.write(f"public class {program_name} {{\n")
            output_file.write("public static void main(String[] args) {\n")

            output_file.write('System.out.printf("Amogus");\n')

            # Epilogue
            output_file.write("}}\n")

    except FileNotFoundError:
        print(f"O arquivo {file_path} não foi encontrado.")
    except Exception as e:
        raise e
        # print(f"Ocorreu um erro ao processar o arquivo: {e}")


if __name__ == "__main__":
    main()
