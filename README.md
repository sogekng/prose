# ✒️ Prose Lang

Uma linguagem de programação projetada para ser legível como prosa, com uma sintaxe simples, declarativa e baseada em palavras-chave (*keywords*).

Este projeto é um **transpilador** que converte código escrito em Prose para Java, e então o compila e executa, criando uma ponte entre uma sintaxe de alto nível e a robustez da plataforma Java.

## Principais Funcionalidades

- **Tipos de Dados Fortes:** Suporte para `integer`, `rational`, `string`, `boolean`, `list<T>` e `structs` definidas pelo usuário.
- **Checagem de Tipos (Type Checking):** O transpilador verifica a compatibilidade de tipos antes de gerar o código, fornecendo erros claros e imediatos.
- **Estruturas de Dados:** Defina seus próprios tipos de dados com `create type`.
- **Variáveis e Constantes:** Declaração de variáveis mutáveis (`variable`) e constantes imutáveis (`constant`).
- **Estruturas de Controle:** Lógica condicional com `if/elif/else` e laços de repetição com `while`, `do-while` e um `for-each` para listas.
- **Funções:** Crie blocos de código reutilizáveis com parâmetros tipados e valores de retorno.
- **Entrada e Saída:** Funções para ler dados do terminal (`read` e `readme`) e imprimir no console (`write`, `writeln`).
- **Transpilação para Java:** O código final é convertido para Java, garantindo performance e portabilidade.

## Instalação e Uso

Para usar a linguagem Prose, você precisa ter o **Python 3** e o **Java (JDK)** instalados no seu sistema.

### No macOS e Linux

1. Clone este repositório e navegue até a pasta do projeto no terminal.
2. Execute o script de instalação para tornar o comando `prose` disponível em todo o sistema.
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
3. **Abra uma nova janela do terminal.** Agora você pode usar o comando `prose` de qualquer lugar:
   ```bash
   prose suite_de_testes.prose
   ```

### No Windows

1. Clone ou baixe este repositório.
2. Abra o Prompt de Comando (CMD) ou PowerShell como **Administrador** e navegue até a pasta do projeto.
3. Execute o script de instalação:
   ```batch
   setup.bat
   ```
4. **Abra uma nova janela do terminal.** Agora você pode usar o comando `prose` de qualquer lugar:
   ```batch
   prose suite_de_testes.prose
   ```

## Extensão para VS Code (Realce de Sintaxe)

Para uma melhor experiência de desenvolvimento, este projeto inclui uma extensão para o Visual Studio Code que adiciona coloração de sintaxe para a linguagem Prose.

#### Como Instalar:

1. No VS Code, abra a aba de **Extensões** (`Ctrl+Shift+X`).
2. Clique no menu de três pontos (`...`) e selecione `Install from VSIX...`.
3. Navegue até a pasta deste projeto, entre no diretório `dist` e selecione o arquivo `prose-language-support-0.0.1.vsix`.
4. Clique em **Install** e recarregue o VS Code se for solicitado.

Pronto! Todos os arquivos `.prose` agora terão a sintaxe destacada.

---

## Guia da Sintaxe

A sintaxe da Prose Lang é focada em ser declarativa e legível.

### Variáveis e Constantes

Use `create` para declarar variáveis. A sintaxe é `create <tipo> <natureza> <nome> ["to" valor_inicial];`.

| Tipo em Prose | Tipo em Java | Exemplo |
| :--- | :--- | :--- |
| `integer` | `int` | `create integer variable idade to 42;` |
| `rational` | `float` | `create rational constant PI to 3.14;` |
| `string` | `String` | `create string variable nome to "Prose";` |
| `boolean` | `boolean` | `create boolean variable ativo to true;` |
| `list<string>` | `ArrayList<String>` | `create list<string> variable itens;` |
| `NomeDoStruct` | `NomeDoStruct` (classe) | `create Pessoa variable p1;` |

Para modificar uma variável, use `set <nome> to <expressao>;`.
```prose
set idade to idade + 1;
```

### Estruturas de Dados (Structs)

Você pode criar seus próprios tipos de dados. A definição deve ocorrer no escopo global.

```prose
# Definição de um novo tipo 'Pessoa'
create type Pessoa (
    string nome,
    integer idade
);

# Criação de uma instância
create Pessoa variable p1;

# Acesso e atribuição aos membros
set p1.nome to "Ana";
set p1.idade to 30;

writeln "Nome: " + p1.nome; # Imprime "Nome: Ana"
```

### Listas

As listas são fortemente tipadas e podem conter tipos primitivos ou structs.

```prose
# Lista de tipos primitivos
create list<integer> variable numeros to [10, 20, 30];

# Lista de structs
create list<Pessoa> variable agenda;
create Pessoa variable p1;
set p1.nome to "Carlos";
set p1.idade to 42;
add(agenda, p1);

# Acesso a um elemento (índices começam em 0)
writeln numeros[1]; # Imprime 20
writeln agenda[0].nome; # Imprime "Carlos"
```

### Funções

Funções permitem reutilizar lógica, com parâmetros e retornos tipados.

```prose
# Definição de uma função com tipos
function somar(integer a, integer b) -> integer
    return a + b;
end

# Funções sem retorno (procedimentos) usam 'void'
function imprimir_saudacao(string nome) -> void
    writeln "Ola, " + nome;
end
```

### Entrada e Saída (I/O)

- `read <nome_variavel>;`: Lê uma entrada do terminal sem um prompt.
- `readme <nome_variavel> <expressao_prompt>;`: Exibe um prompt e lê a entrada.
- `write <expressao>;`: Imprime no console sem pular linha.
- `writeln <expressao>;`: Imprime no console e pula uma linha.

```prose
create string variable nome_usuario;
readme nome_usuario "Digite seu nome: ";
writeln "Bem-vindo, " + nome_usuario;
```

### Estruturas de Controle

**Condicionais:**
```prose
if x > 10 then
    writeln "x e maior que 10";
elif x == 10 then
    writeln "x e exatamente 10";
else
    writeln "x e menor que 10";
end
```

**Laços de Repetição:**
```prose
# While: checa a condição antes de executar
while contador < 5 do
    set contador to contador + 1;
end

# For: itera sobre os elementos de uma lista
create list<string> variable nomes to ["Ana", "Beto", "Caio"];
for nome in nomes do
    writeln "Ola, " + nome;
end
```

### Operadores, Comentários e Outros

- **Operadores Aritméticos:** `+`, `-`, `*`, `/`, `%`.
- **Operadores Relacionais e Lógicos:** `==`, `!=`, `>`, `<`, `>=`, `<=`, `&&`, `||`.
- **Fim da Declaração:** Todas as instruções simples devem terminar com ponto e vírgula (`;`).
- **Comentários:** Qualquer texto após um `#` é ignorado até o final da linha.

## Exemplo Completo

O arquivo `suite_de_testes.prose` neste repositório demonstra todas as funcionalidades da linguagem em ação.

## Como Funciona (Processo de Transpilação)

O processo de conversão de Prose para Java ocorre em uma série de etapas bem definidas:
1.  **Análise Léxica:** O código-fonte é quebrado em *tokens* (palavras-chave, operadores, etc.).
2.  **Análise Sintática:** Os tokens são analisados para verificar se a gramática da linguagem está correta. Durante essa fase, uma Árvore de Sintaxe Abstrata (AST) é construída.
3.  **Análise Semântica (Checagem de Tipos):** O transpilador percorre a AST para validar a lógica dos tipos, como atribuições, operações e retornos de função, garantindo que sejam válidos antes de gerar o código.
4.  **Geração de Código:** Cada nó da AST é traduzido para seu equivalente em código Java.
5.  **Compilação e Execução:** O código Java gerado é salvo, compilado para bytecode (`.class`) com `javac`, e finalmente executado pela JVM com `java`.
