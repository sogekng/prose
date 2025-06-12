# ✒️ Prose Lang

Uma linguagem de programação projetada para ser legível como prosa, com uma sintaxe simples, declarativa e totalmente independente, executada por seu próprio **intérprete**.

Este projeto, que começou como um transpilador, evoluiu para uma linguagem interpretada completa, eliminando a dependência do Java e executando o código diretamente.

## Principais Funcionalidades

- **Linguagem Interpretada:** O código Prose é executado diretamente, sem a necessidade de um compilador externo ou da JVM.
- **Tipos de Dados Fortes:** Suporte para `integer`, `rational`, `string`, `boolean`, `list<T>` e `structs` e `functions` como tipos.
- **Checagem de Tipos Estática:** O parser valida a compatibilidade de tipos antes da execução, fornecendo erros claros e imediatos.
- **Funções de Primeira Classe:** Trate funções como valores — armazene-as em variáveis, passe-as como argumentos e retorne-as de outras funções, permitindo o uso de closures e programação funcional.
- **Sistema de Módulos:** Organize seu código em múltiplos arquivos e reutilize funcionalidades com as instruções `import` e `from ... import`.
- **Estruturas de Dados:** Defina seus próprios tipos de dados compostos com `create type`.
- **Estruturas de Controle Modernas:** Lógica condicional com `if/elif/else` e laços `while`, `do-while` e um `for-each` que itera sobre listas e strings.

## Instalação e Uso

Para usar a linguagem Prose, você só precisa ter o **Python 3** instalado no seu sistema.

### No macOS e Linux

1.  Clone este repositório e navegue até a pasta do projeto no terminal.
2.  Execute o script de instalação para tornar o comando `prose` disponível em todo o sistema.
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```
3.  **Abra uma nova janela do terminal.** Agora você pode usar o comando `prose` de qualquer lugar:
    ```bash
    # Para executar um arquivo
    prose meu_arquivo.prose

    # Para iniciar o modo interativo (REPL)
    prose
    ```

### No Windows

1.  Clone ou baixe este repositório.
2.  Abra o Prompt de Comando (CMD) ou PowerShell como **Administrador** e navegue até a pasta do projeto.
3.  Execute o script de instalação:
    ```batch
    setup.bat
    ```
4.  **Abra uma nova janela do terminal.** Agora você pode usar o comando `prose` de qualquer lugar.

## Extensão para VS Code

Para uma melhor experiência de desenvolvimento, este projeto inclui uma extensão para o Visual Studio Code que adiciona:
* Realce de sintaxe para a linguagem Prose.
* Ícone de arquivo personalizado para arquivos `.prose`.
* Um botão de "Play" para executar o arquivo atual diretamente do editor.

#### Como Instalar:

1.  No VS Code, abra a aba de **Extensões** (`Ctrl+Shift+X`).
2.  Clique no menu de três pontos (`...`) e selecione `Install from VSIX...`.
3.  Navegue até a pasta `prose-language-extension/dist` e selecione o arquivo `.vsix` mais recente.
4.  Clique em **Install** e recarregue o VS Code.

#### Ativando os Ícones (Opcional)
Após a instalação, para ver o ícone de arquivo personalizado:
1.  Pressione `Ctrl+Shift+P` para abrir a Paleta de Comandos.
2.  Digite `File Icon Theme` e selecione **Preferences: File Icon Theme**.
3.  Escolha **"Prose Icons"** na lista.

---

## Guia da Sintaxe

### Variáveis e Tipos

Use `create` para declarar variáveis e constantes. A linguagem agora também entende `function` como um tipo.

| Tipo em Prose | Exemplo |
| :--- | :--- |
| `integer` | `create integer variable idade to 42;` |
| `string` | `create string variable nome to "Prose";` |
| `list<string>` | `create list<string> variable itens;` |
| `NomeDoStruct` | `create Pessoa variable p1;` |
| `function(...)` | `create function(integer)->integer var fn;` |

### Módulos
Organize seu código em múltiplos arquivos e importe funcionalidades.

**`math.prose`**
```prose
function dobrar(integer n) -> integer
    return n * 2;
end
```

**`main.prose`**
```prose
# Opção 1: Importa o módulo como um namespace
import math;
writeln math.dobrar(10); # Saída: 20

# Opção 2: Importa um nome específico para o escopo atual
from math import dobrar;
writeln dobrar(5); # Saída: 10
```

### Funções como Cidadãos de Primeira Classe
Funções são valores. Você pode passá-las como argumentos, retorná-las e armazená-las em variáveis.

```prose
# Uma função que retorna outra função (closure)
function criar_somador(integer valor_base) -> function(integer) -> integer
    function somador_interno(integer n) -> integer
        return n + valor_base; # "Lembra" do valor_base
    end
    return somador_interno;
end

# 'soma_cinco' agora é uma função que sempre soma 5
create function(integer)->integer variable soma_cinco to criar_somador(5);

writeln soma_cinco(10); # Saída: 15
```

### Estruturas de Dados (Structs)
Crie seus próprios tipos de dados compostos.
```prose
create type Pessoa (string nome, integer idade);
create Pessoa variable p1;
set p1.nome to "Ana";
set p1.idade to 30;
writeln "Nome: " + p1.nome;
```

### Listas
As listas são fortemente tipadas e podem ser acessadas por índice.

```prose
# Criação de uma lista
create list<integer> variable numeros to [10, 20, 30];

# Acesso por índice (começando em 0)
writeln numeros[1]; # Saída: 20

# Modificação por índice
set numeros[1] to 250;
writeln numeros[1]; # Saída: 250
```

### Laço `for`
O laço `for` pode iterar sobre listas e strings.
```prose
# Iterando sobre uma lista
create list<string> variable nomes to ["Ana", "Beto"];
for nome in nomes do
    writeln "Ola, " + nome;
end

# Iterando sobre uma string
for char in "Prose" do
    write char + "-"; # Saída: P-r-o-s-e-
end
```

## Como Funciona (Processo de Interpretação)

Com sua evolução, o processo de execução da Prose agora é o de um **intérprete clássico**:
1.  **Análise Léxica:** O código-fonte é quebrado em *tokens*.
2.  **Análise Sintática:** Os tokens são organizados em uma Árvore de Sintaxe Abstrata (AST), e a checagem de tipos é realizada para validar a semântica.
3.  **Execução (Interpretação):** O intérprete "caminha" pela AST, executando cada nó diretamente. Ele gerencia uma pilha de escopos para variáveis e funções, garantindo que closures e escopos aninhados funcionem corretamente.
