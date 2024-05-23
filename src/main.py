from lexer import Lexer

def main():
    file_path = "teste"
    try:
        with open(file_path, 'r') as file:
            code = file.read()
            lexer = Lexer()
            tokens = lexer.tokenize(code)

            print("Tokens gerados:")
            for token in tokens:
                print(token)

            lexer.log_token(tokens)
    except FileNotFoundError:
        print(f"O arquivo {file_path} não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo: {e}")

if __name__ == "__main__":
    main()
