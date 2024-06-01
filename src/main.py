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

    except FileNotFoundError:
        print(f"O arquivo {file_path} não foi encontrado.")
    except Exception as e:
        raise e
        # print(f"Ocorreu um erro ao processar o arquivo: {e}")


if __name__ == "__main__":
    main()
