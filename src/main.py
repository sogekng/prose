from lexer import Lexer
import parsa
import pprint


def main():
    file_path = "teste.lang"

    try:
        with open(file_path, 'r') as file:
            code = file.read()
            lexer = Lexer()

            tokens = lexer.tokenize(code)

            token_groups = parsa.group_tokens(tokens)

            pprint.pp(token_groups)

    except FileNotFoundError:
        print(f"O arquivo {file_path} não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo: {e}")


if __name__ == "__main__":
    main()
