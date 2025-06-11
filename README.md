# ✒️ Prose Lang

Uma linguagem de programação projetada para ser legível como prosa, com uma sintaxe simples, declarativa e baseada em palavras-chave (*keywords*).

Este projeto é um **transpilador** que converte código escrito em Prose para Java, e então o compila e executa, criando uma ponte entre uma sintaxe de alto nível e a robustez da plataforma Java.

## Principais Funcionalidades

- **Tipos de Dados:** Suporte para `integer`, `rational`, `string`, `boolean` e `list`.
- **Variáveis e Constantes:** Declaração de variáveis mutáveis e constantes imutáveis.
- **Estruturas de Controle:** Lógica condicional com `if/elif/else` e laços de repetição com `while` e `do-while`.
- **Listas:** Suporte nativo para criação, acesso (`lista[i]`) e modificação (`set lista[i] to ...`) de listas.
- **Funções:** Crie blocos de código reutilizáveis com parâmetros e valores de retorno.
- **Entrada e Saída:** Funções para ler dados do terminal (`read`) e imprimir no console (`write`, `writeln`).
- **Transpilação para Java:** O código final é convertido para Java 8+, garantindo performance e portabilidade.

## Instalação e Uso

Para usar a linguagem Prose, você precisa ter o **Python 3** e o **Java (JDK)** instalados no seu sistema.

### No macOS e Linux

1. Clone este repositório e navegue até a pasta do projeto no terminal.
2. Execute o script de instalação para tornar o comando `prose` disponível em todo o sistema. Você precisará da sua senha de administrador.

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
2. Abra o Prompt de Comando (CMD) ou PowerShell como **Administrador**, navegue até a pasta do projeto.
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

1. No VS Code, abra a aba de **Extensões** na barra lateral (ícone de blocos ou `Ctrl+Shift+X`).
2. Clique no menu de três pontos (`...`) no canto superior direito da aba de Extensões.
3. Selecione a opção `Install from VSIX`.

4. Navegue até a pasta deste projeto, entre no diretório `dist` (ou onde você salvou o arquivo) e selecione o arquivo `prose-language-support-0.0.1.vsix`.
5. Clique em **Install** e recarregue o VS Code se for solicitado.

Pronto! Todos os arquivos `.prose` agora terão a sintaxe destacada.

---

## Guia da Sintaxe

A sintaxe da Prose Lang é focada em ser declarativa e legível.

### Variáveis e Constantes

Use `create` para declarar variáveis. A sintaxe é `create <tipo> <natureza> <nome> [valor_inicial];`.

| Tipo em Prose | Tipo em Java      | Exemplo                                    |
|---------------|-------------------|--------------------------------------------|
| `integer`     | `int`             | `create integer variable idade 42;`        |
| `rational`    | `float`           | `create rational constant PI 3.14;`        |
| `string`      | `String`          | `create string variable nome "Prose";`     |
| `boolean`     | `boolean`         | `create boolean variable ativo true;`      |
| `list`        | `ArrayList<Object>` | `create list variable itens;`              |

A natureza da variável pode ser:
* `variable`: Pode ter seu valor alterado com `set`.
* `constant`: Não pode ser alterada após a criação.

Para modificar uma variável, use `set <nome> to <expressao>;`.
```prose
set idade to idade + 1;
```

### Listas

As listas podem ser criadas vazias ou com valores iniciais.

```prose
# Declaração de uma lista com valores
create list variable numeros [10, 20, 30];

# Acesso a um elemento (índices começam em 0)
writeln numeros[1]; # Imprime 20

# Modificação de um elemento
set numeros[1] to 250;
writeln numeros[1]; # Imprime 250
```

### Funções

Funções permitem reutilizar lógica. Elas podem receber parâmetros e retornar valores.

```prose
# Definição de uma função
function somar(a, b)
    return a + b;
end

# Chamada da função dentro de uma expressão
set resultado to somar(5, 3); # resultado será 8

# Funções sem retorno (procedimentos) podem ser chamadas diretamente
function imprimir_saudacao(nome)
    writeln "Ola, " + nome;
end

imprimir_saudacao("Mundo"); # Chama o procedimento
```

### Entrada e Saída (I/O)

-   `read <nome_variavel>;`: Lê uma entrada do terminal e a armazena na variável.
-   `write <expressao>;`: Imprime o resultado da expressão no console sem pular linha.
-   `writeln <expressao>;`: Imprime o resultado e pula uma linha.

```prose
create string variable nome_usuario;
write "Digite seu nome: ";
read nome_usuario;
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

# Do-While: executa uma vez e depois checa a condição
do
    writeln "Este bloco executa pelo menos uma vez.";
while false end
```

### Operadores, Comentários e Outros

- **Operadores Aritméticos:** `+`, `-`, `*`, `/`, `%` (com precedência padrão).
- **Operadores Relacionais e Lógicos:** `==`, `!=`, `>`, `<`, `&&` (E), `||` (OU).
- **Fim da Declaração:** Todas as instruções simples devem terminar com ponto e vírgula (`;`).
- **Comentários:** Qualquer texto após um `#` é ignorado até o final da linha.

---

## Exemplo Completo

O arquivo `suite_de_testes.prose` neste repositório demonstra todas as funcionalidades da linguagem em ação.

---

## Como Funciona (Processo de Transpilação)

O processo de conversão de Prose para Java ocorre em uma série de etapas bem definidas:
1.  **Análise Léxica:** O código-fonte é lido e quebrado em unidades mínimas, os *tokens* (palavras-chave, operadores, etc.).
2.  **Análise Sintática:** Os tokens são analisados para verificar se a gramática da linguagem está correta. Durante essa fase, uma Árvore de Sintaxe Abstrata (AST) é construída para representar a estrutura lógica do programa.
3.  **Geração de Código:** O transpilador percorre a AST. Cada nó da árvore (uma declaração, uma estrutura `if`, etc.) é traduzido para seu equivalente em código Java. Um "banco de variáveis" gerencia os escopos para garantir que variáveis e funções sejam declaradas e usadas corretamente.
4.  **Compilação e Execução:** O código Java gerado é salvo em um arquivo `.java`, compilado para bytecode (`.class`) usando `javac`, e finalmente executado pela JVM com `java`. A saída do programa é exibida no terminal.