# Prose Lang

Uma linguagem para escrever código como prosa, com foco em usar *keywords*.

O source é um transpilador de Prose Lang para Java.

## Processo

O processo de transpilação de Prose Lang para Java pode ser reduzido nos seguintes passos:

1. Tokenize: o arquivo de texto em Prose Lang é convertido para uma série de **Tokens**, unidades mínimas de compilação.
2. Group Structures: tokens que representam estruturas (e.g. `while`, `if`, etc.) são agrupados em **StructureGroups**.
3. Group Statements: tokens livres e que moram dentro das estruturas são agrupados em **StatementGroups**.
4. Synthesize: **StructureGroups** tornam-se **Structures** e **StatementGroups** tornam-se **Statements**, que possuem lógica de validação e renderização para Java.
5. Render: ocorrem validações lógicas e transformação de objetos conceituais em linhas de texto na linguagem Java.
6. Compile: o arquivo Java é compilado para um arquivo `.class`.
7. Execute: o arquivo `.class` é executado para gerar a saída do programa ou capturar input pelo terminal.

## Sintaxe

A sintaxe da Prose Lang é focada em *keywords* substituindo a maioria dos operadores comuns e tentando fazer
*statements* tornarem-se mais próximos de frases em inglês, ainda que mantenha a estrutura de um programa clássico.

### Manipulação de variáveis

Criar uma variável requer a sintaxe `create <type> <kind> <name> [value];`, onde `<type>` é um dos quatro tipos da Prose Lang:

- `string`: estrutura textual (cadeia de caracteres, `String` no Java)
- `integer`: valor numérico inteiro (`int` no Java)
- `rational`: valor decimal (`float` no Java)
- `boolean`: valor booleano (`boolean` no Java)

E `<kind>` é uma das duas categorias de variáveis:

- `constant`: determina que o valor não pode adquirir algum valor após ser criado
- `variable`: determina que o valor pode adquirir novos valores após ser criado

E então, `<name>` é um identificador (nome) da variável sendo criada o e valor opcional `[value]` vai ser o valor inicial da variável, se provido.

Mudar o valor de uma variável requer a sintaxe `set <name> to <value>;`, onde `<name>` é o nome da variável sendo alterada e `<value>` é um valor ou expressão que vai se tornar o novo valor da variável.

### I/O (Input e Output)

Para escrever um valor utilizando a sintaxe do `System.out.printf()` do Java,
é necessária a sintaxe `write <format_string> ...args;`, onde `<format_string>` é a string de formatação (primeiro valor passado ao `printf()` do Java), e o vararg opcional
`args` é uma série de valores separados por espaços que vão compor o resto dos argumentos.

Para ler um valor é preciso ter antes criado uma variável (da categoria `variable`), e então usa-se a sintaxe `read <name>;`, que vai utilizar um método de leitura
de input baseado no tipo da variável declarada.

### Estruturas de repetição

É possível fazer uma repetição condicional usando a estrutura `while <condition> do ...statement end`, onde `<condition>` é a condição (uma expressão booleana) para continuar o loop,
e `...statement` é uma coleção de zero ou mais *statements* como descritos anteriormente (`create`, `set`, `read`, `write`). A toda iteração a condição será checada e se for verdadeira
(valor literal `true`), vai resultar na execução de cada um dos statements do corpo.

Para garantir que ao menos um ciclo de repetição ocorra antes da verificação condicional, efetivamente invertendo a ordem de checar a condição e executar as declarações,
utilize a estrutura `do ...statement while <condition> end`, onde os parâmetros nomeados são idênticos aos da estrutura `while`.

### Estrutura condicional

Para condicionalmente seguir caminhos de código, utilize a estrutura `if <condition> then ...statement end`, com parâmetros nomeados idênticos à estrutura `while`.

Caso a condição seja verdadeira, o conjunto de declarações dentro do corpo é executado.

Para gerar mais caminhos condicionais, após o fim do corpo desse item (antes do primeiro `end`), continue com estruturas `elif <condition> then ...statement`.

Por fim, para ter um caminho condicional de *fall-off* (executado somente se sobrar), adicione, antes do primeiro `end`, a estrutura `else ...statement`.

### O restante

O esperado existe na Prose Lang: operadores aritméticos `+` (som. adição), `-` (som. subtração), `*` (mul. multiplicação), `/` (mul. divisão), `%` (mul. módulo)
(onde as precedências dos multiplicadores são idênticas e maiores que as dos somadores), operadores booleanos relacionais `>` (maior), `<` (menor), `==` (igual), `!=` (diferente)
e operadores booleanos diretos `&&` (bool. e), `!` (bool. negação), `||` (bool. ou).

Statements (declarações) precisam ser finalizados com ponto e vírgula (`;`).

Comentários são desconsiderados do programa, e começam a partir de qualquer caractere *hashtag* `#`.

### Exemplo de programas em Prose Lang

`arithmetic.prose`
```prose
create integer variable x 25;
create integer constant Y 35;

create integer variable z;
set z to x + Y;

write "z = %d\n" z;  # z = 60

# Erro: não é possível alterar uma `constant`
# set Y to 5;

create string constant WELCOME "Welcome to my program\n";

write WELCOME;  # Welcome to my program

create integer variable j;
read j;  # Lê um inteiro para dentro de `j`

create integer variable i 0;

# i = 0
# i = 1
# ...
# i = n - 1
while i < j do
    write "i = %d\n" i;
    set i to i + 1;
end

# i reached its maximum
if i == j - 1 then
    write "i reached its maximum\n";
elif i > 0 then
    write "i did not progress\n";
else
    write "i decreased somehow\n";
end

do
    write "Testing!\n";
while false end
```

### Executando

Rode o script `src/main.py` passando como input o nome do arquivo, e.g. `python src/main.py test_file.prose`.

### Mais

A Prose Lang faz verificação de tipos nas expressões dadas ao `set`, `create`, e nas condicionais das
estruturas. *Full type parsing* nos permite encontrar erros nas expressões e corretamente identificar
o tipo final delas.

Erros de sintaxe, onde práticos, são indicados pra correção.

Escopo de sintaxe dentro das estruturas também existe, seguindo as mesmas regras que as de escopo
do Java (e.g. redeclaração é apontada como erro).
