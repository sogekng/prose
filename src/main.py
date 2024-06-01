from lexer import Lexer

def main():
    file_path = "teste.lang"
    
    try:
        with open(file_path, 'r') as file:
            code = file.read()
            lexer = Lexer()
            
            tokens = lexer.tokenize(code)
            
            for token in tokens:
                print(token)
                
            # parser = Parser(tokens)
            # result = parser.parse()
            # print("Resultado da expressão:", result)

    except FileNotFoundError:
        print(f"O arquivo {file_path} não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo: {e}")

if __name__ == "__main__":
    main()
