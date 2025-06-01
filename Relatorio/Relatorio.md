# Relatório do Trabalho Prático do Compilador para Pascal Standard

![Foto](uminho.png)  


#### Trabalho realizado por:
Gonçalo Monteiro Cunha - a104003  
Gonçalo Oliveira Cruz - a104346  
Nuno Miguel Matos Ribeiro - a104177  


#### Unidade Curricular de Processamento de Linguagens

**Ano Letivo** 2024/25  
**Data:** 31/05/2025  



## Introdução

O presente relatório descreve o desenvolvimento de um projeto cujo objetivo foi a implementação de um compilador completo para a linguagem Pascal (versão *standard*). O compilador foi construído por fases, englobando a análise léxica, a análise sintática, a análise semântica e, por fim, a geração de código para uma máquina virtual (VM) previamente definida no enunciado.  

A fase de criação do analisador léxico teve como objetivo identificar e classificar os diferentes elementos da linguagem (*tokens*), como identificadores, operadores, palavras-chave e literais.  
Seguiu-se a análise sintática, responsável por validar a estrutura gramatical dos programas, assegurando que estes obedecem às regras da linguagem Pascal.  
A análise semântica verificou a coerência dos programas, como declarações prévias de variáveis, compatibilidade de tipos e utilização correta de identificadores.  

Posteriormente, foi desenvolvida a componente de geração de código, que transforma os programas validados em código máquina para a EWVM. Esta máquina virtual executa um conjunto de instruções, permitindo assim a execução dos programas Pascal convertidos.

Para testar o sistema, foram utilizados vários exemplos de código Pascal, que foram processados pelo compilador e convertidos corretamente em código máquina executável na máquina virtual. O resultado final é uma ferramenta capaz de compilar e executar programas em Pascal *standard*.





## Analisador Léxico

O analisador léxico é a primeira fase do compilador e tem como principal função ler o texto-fonte em Pascal *standard*, segmentando-o em elementos atómicos chamados ***tokens***. Este está definido no ficheiro `ana_lex.py`. Cada *token* representa uma unidade sintática básica, como palavras-chave, identificadores, literais numéricos, literais de texto, operadores aritméticos e sinais de pontuação. A implementação apresentada, que recorre à biblioteca PLY, está estruturada de modo a:

1. **Reconhecer todas as palavras-chave da linguagem** (por exemplo, `BEGIN`, `END`, `VAR`, `IF`, `THEN`, entre outras), independentemente de estarem escritas em maiúsculas ou minúsculas (Pascal é case-insensitive).  
2. **Identificar literais e tipos básicos** (`INTEGER`, `REAL`, `CHAR`, `BOOLEAN`, bem como valores concretos como números inteiros, números reais, caracteres isolados e cadeias de texto).  
3. **Detetar identificadores** (nomes de variáveis, procedimentos, funções, rótulos etc.), garantindo que comecem por letra ou underscore e continuem com letras, dígitos ou underscore.  
4. **Classificar operadores aritméticos, relacionais e sinais de pontuação/delimitação** (`+`, `-`, `*`, `/`, `:=`, `=`, `<>`, `<=`, `>=`, parêntesis, parêntesis retos, ponto, ponto e vírgula, vírgula, dois pontos e intervalo `..`).  
5. **Ignorar comentários** (tanto no formato `{ … }` como no formato `(* … *)`), bem como espaços em branco, tabulações e quebras de linha, enquanto atualiza corretamente o número de linha para efeitos de diagnóstico de erros posteriores.  
6. **Reportar erros léxicos** sempre que se depare com um carácter ilegal ou um literal de carácter inválido.

A seguir, descrevem-se os principais componentes do analisador léxico e a sua lógica de funcionamento.

---

### 1. Definição dos Tokens

Antes de mais, declara-se uma tupla chamada `tokens` que inclui **todos** os nomes simbólicos dos tokens reconhecidos pelo analisador léxico. Esta lista é composta por:

- **Tipos básicos e literais de tipo**:  
  - `TIPO` (para reconhecer palavras como `INTEGER`, `REAL`, `BOOLEAN` e `CHAR`),  
  - `BOOLEAN` (para valores literais `TRUE` ou `FALSE`).  

- **Palavras-reservadas de Pascal ISO 7185**:  
  `AND`, `ARRAY`, `BEGIN`, `CASE`, `CONST`, `DIV`, `DOWNTO`, `DO`, `ELSE`, `END`, `FILE`, `FOR`, `FUNCTION`, `GOTO`, `IF`, `IN`, `LABEL`, `MOD`, `NOT`, `OF`, `OR`, `PACKED`, `PROCEDURE`, `PROGRAM`, `RECORD`, `REPEAT`, `SET`, `THEN`, `TO`, `TYPE`, `UNTIL`, `VAR`, `WHILE`, `WITH`.  

- **Identificadores e literais**:  
  - `ID` (identificadores genéricos),  
  - `REAL` (números reais),  
  - `INTEGER` (números inteiros),  
  - `CHAR` (literais de carácter único, entre aspas simples),  
  - `TEXTO` (cadeias de texto, com mais de um carácter).  

- **Operadores aritméticos e relacionais**:  
  - `PLUS` (`+`), `MINUS` (`-`), `TIMES` (`*`), `DIVIDE` (`/`),  
  - `ASSIGN` (`:=`), `EQ` (`=`), `NE` (`<>` ou `!=`), `LE` (`<=`), `LT` (`<`), `GE` (`>=`), `GT` (`>`).  

- **Símbolos de pontuação e delimitadores**:  
  - `LPAREN` (`(`), `RPAREN` (`)`), `LBRACKET` (`[`), `RBRACKET` (`]`),  
  - `SEMI` (`;`), `COMMA` (`,`), `RANGE` (`..`), `DOT` (`.`), `COLON` (`:`).  

Esta enumeração completa permite ao analisador léxico reconhecer qualquer elemento válido da sintaxe Pascal, fornecendo um nome de token específico que será passado à fase sintática.

---

### 2. Regras para Palavras-Reservadas e Tipos Básicos

Em Pascal, as palavras-reservadas são case-insensitive, ou seja, `BEGIN`, `begin` ou `BeGiN` devem ser tratadas como o mesmo token. Para isso, cada palavra-reservada é associada a uma função cujo nome começa por `t_` seguido do nome do token (por ex., `t_BEGIN`, `t_END`, `t_IF`, etc.). Cada função contém uma expressão regular que utiliza classes de caracteres para aceitar ambas as versões maiúsculas e minúsculas de cada letra.

O reconhecimento de identificadores como as palavras-reservadas também obedece ao mesmo padrão, sendo necessário definir antes de `t_ID` todas as funções que capturam keywords (com uma expressão regular específica para cada). O mecanismo Lex, do PLY, dá prioridade às regras definidas por função em relação ao token genérico ID. Assim, quando um lexema corresponde a uma palavra-reservada, a função correspondente será invocada em vez de t_ID.

A definição das regras seguiu uma ordem lógica a fim de evitar que regras mais simples captassem indevidamente *tokens* mais complexos. Por exempli, a regra de `t_REAL` é definida antes de `t_INTEGER`, para evitar que lexemas como `3.14` sejam captados primeiro como INTEGER (o 3) seguido de '.' e de outro INTEGER (o 14).

---

### Resumo

Em resumo, o analisador léxico apresentado:

- Segmenta o código-fonte em tokens que representam unidades semânticas fundamentais em Pascal *standard*.

- Classifica as palavras-reservadas, identificadores, literais e operadores, garantindo que a insensibilidade a maiúsculas/minúsculas seja respeitada.

- Ignora comentários e espaços em branco, mantendo apenas a informação útil para as fases seguintes.

- Controla o número da linha para permitir um diagnóstico rigoroso de erros posteriores.

- Reporta imediatamente eventuais caracteres ilegais ou literais de carácter inválidos.

Este componente léxico assegura que a fase sintática receba uma sequência consistente de tokens, sem ruído, sobre a qual pode aplicar a verificação de estrutura gramatical. Deste modo, toda a arquitetura do compilador fica apoiada numa base sólida e fiável.





## Analisador Sintático

Nesta secção, iremos descrever as decisões tomadas ao implementar o analisador sintático para Pascal *standard*, recorrendo à ferramenta YACC do PLY. Em vez de analisar cada linha de código isoladamente, focámo-nos na **estrutura global**, na **construção das produções** e nos **motivos por detrás de cada escolha de design**. O objetivo é deixar claro porque é que o *parser* criado nesta fase está organizado desta forma, como se evita ambiguidade e como se constrói uma Árvore de Sintaxe Abstrata (AST) coerente para fases posteriores (análise semântica e geração de código).  

---

### 1. Uso do YACC e Filosofia de Construção

1. **Separação de Léxico e Sintaxe**  
   - O *lexer* implementado fornece o tuplo `tokens` e a função `build_lexer()`.  
   - No parser, invoca-se `build_lexer()` apenas como interface de leitura de tokens, garantindo que o analisador se concentre unicamente na estrutura gramatical, sem misturar lógica de reconhecimento de caracteres.

2. **Construção da AST**  
   - Em cada produção, em vez de executar directamente a tradução para código, constrói-se um **tuplo** ou uma pequena estrutura (nós da AST), que representa o tipo de construção Pascal (p.e. `('assign', variável, expressão)`).  
   - Esta filosofia simplifica a posterior travessia, quer para análise semântica, quer para geração de código, bastando percorrer a árvore e interpretar cada nó, sem ter de reanalisar strings de entrada.

---

### 2. Gramáticas Ambíguas em Pascal

O problema do “dangling else” (ou “ELSE pendente”) significa que, ao ter produções como

```pascal
if expression then statement
if expression then statement else statement
```

há ambiguidade sobre o **if** a que o **else** se associa.  
Para resolver isto, define-se um token fictício `IFX` (**if** sem **else**) e indica-se que `ELSE` é *nonassoc* relativamente a `IFX`.  
Assim, a regra com `%prec IFX` na produção `if_statement` (o segundo caso sem **else**) força o *PLY* a preferir associar o **else** ao **if** mais interno.

---

### 3.Precedência de Operadores

A gramática aritmética e lógica em Pascal é definida com precedência típica:

**NOT** (unário) — alto.

Comparações (`=`, `<>`, `<`, `<=`, `>`, `>=`, `IN`) — médio-alto.

**AND**, **OR** — associatividade à esquerda.

Aritmética: `*`, `/`, `DIV`, `MOD` (produto) têm precedência sobre `+`, `-` (soma/subtração).

O operador de dois-pontos (`:`) surge em rótulos e declarações — colocado no fim, pois raramente causa ambiguidade com expressões.

Com a especificação de *precedence*, garantimos que produções como

```pascal
expression : expression PLUS expression 
           | expression TIMES expression
           | NOT expression
           | expression EQ expression
           | expression AND expression
           | …
```

sejam interpretadas de acordo com a semântica Pascal (e não ambíguas), sem ter de reescrever separadamente.

---

### 4. Organização Modular das Produções

1. **Secções Distintas para Declarações e Instruções**  
   - A gramática foi organizada de forma a refletir o esquema de Pascal: em primeiro lugar, **declarações de topo** (constantes, tipos, rótulos, variáveis, funções e procedimentos); em seguida, o bloco principal de instruções (`BEGIN ... END`).  
   - Esta distinção em **bloco de declarações** e **bloco de instruções** permite separar o tratamento semântico do processamento das instruções propriamente ditas.  
   - Além disso, o agrupamento de múltiplas declarações é feito recursivamente (por exemplo, várias declarações de `const` ou de `var` em sequência), assegurando que não haja restrição quanto ao número de blocos do mesmo tipo.

2. **Produções Genéricas para Listas**  
   - Cada vez que fosse necessário agrupar vários itens (por exemplo, lista de identificadores ou lista de declarações), recorremos a **recursividade à esquerda**, por ser mais eficiente e simples de implementar. Isto significa que, por exemplo,  
     ```  
     lista : lista elemento  
           | elemento  
     ```  
     cria uma implementação onde é fácil concatenar listas em cada passo.  
   - As vantagens desta técnica são: manter a ordem textual original intacta (não se está a inverter a lista ao construir recursivamente) e produzir diretamente, em `p[0]`, uma lista de nós AST.

3. **Separação de Cada Tipo de Declaração**  
   - Optou-se por criar produções distintas para cada categoria de declaração de topo:  
     - `const_declaration`,  
     - `type_declaration`,  
     - `label_declaration`,  
     - `var_declaration`,  
     - `function_declaration`,  
     - `procedure_declaration`.  
   - Este grau de fragmentação torna o *parser* muito mais claro: cada fragmento da gramática corresponde a um conceito específico de Pascal e não há sobreposição de regras.

4. **Reutilização de Subproduções Comuns**  
   - Algumas construções aparecem em mais do que um contexto, pelo que reaproveitámos regras já escritas. Um bom exemplo é `var_item`, que é usado tanto no bloco `var` principal (`var_declaration`) como dentro de `record_type` (para definir campos de um registo).  
   - O mesmo acontece com `ID_LIST`: sempre que precisámos de ler uma lista de identificadores (seja numa declaração, seja num parâmetro, seja num tipo enumerado), invocamos esta mesma produção. Esta escolha garante coerência, pois não há duas versões diferentes de “lista de IDs” a coexistir no *parser*.

---

### 5. Critérios de Construção das Produções

1. **Modularidade e Coesão de Cada Produção**  
   - Cada agrupamento de sintaxe (declarações, tipos, instruções e expressões) foi projetado como um “módulo” autocontido.  
   - Se, noutro momento, se quiser adicionar, por exemplo, diretivas de compilador à secção `declarations`, basta acrescentar uma produção nova em `p_declaration` sem ter de mexer nas instruções ou nas expressões.  
   - Este princípio de coesão permite também testar cada subparte isoladamente: caso haja um problema no reconhecimento de `case_statement`, basta construir testes para *statements* `case ... of ... end` sem ter de compilar todo o parser.

2. **AST Padronizada e Simplificada**  
   - A opção por representar cada construtor Pascal com um tuplo, cujo primeiro elemento identifica o tipo de nó, segue um padrão consistente. Por exemplo:  
     - Declarações de variáveis tornam-se `('vars', [lista_de_ids], tipo)`;  
     - Ciclos `for` passam a `('for', id, expr_inicial, expr_final, direção, corpo)`;  
     - Registos geram `('record', [lista_de_campos], parte_variante_se_existir)`.  
   - Esta padronização garante que, na fase semântica, sabemos exatamente que campo de cada tuplo corresponde ao que interessa (nome, tipo, sub-AST, etc.).  
   - Evitou-se criar classes ou objetos demasiado sofisticados que, embora poderosos, aumentariam a complexidade de percorrer a árvore e manusear informações durante a geração de código final.

---

### 6. Tratamento de Erros e Robustez

1. **Manutenção da Linha de Código para Diagnóstico**  
   - Cada token chega ao parser com informação do número de linha (`lineno`) fornecido pelo lexer.  
   - Ao denunciar um erro, o parser usa esse número de linha para indicar ao utilizador exatamente onde o problema surgiu, facilitando a posterior correção.  
   - Esta decisão torna-se crucial quando surgem erros em produções mais complexas, pois saber exatamente a linha onde o token que causou o problema apareceu ajuda imenso a rastrear a falha na gramática.

2. **Esquema Uniforme da AST Mesmo em Caso de Erro Parcial**  
   - Embora o parser acabe por abortar ao primeiro erro, procurámos manter a produção da AST intacta até ao ponto do problema. Ou seja, se uma parte do código estiver correta, o tuplo correspondente é produzido; só falha quando realmente não há forma de encaixar tokens válidos.  
   - Isto facilita a introdução de futuros mecanismos de recuperação de erros: bastaria, em vez de abortar, inserir nós especiais de erro e continuar a parsear o restante da entrada.

---

### Resumo

1. **Uso de Precedência em Vez de Fatorização Excessiva**  
   - Em vez de reescrever manualmente cada combinação de operadores binários para evitar ambiguidades, recorremos às regras de `precedence` do YACC, garantindo que os conflitos mais comuns (aritméticos, lógicos, `if-else`) sejam resolvidos sem sacrificar legibilidade.  

2. **AST Simples e Uniforme**  
   - Resolver cada produção com um tuplo padrão facilita a integração com as fases seguinte do compilador, sendo mais leve do que classes *Python* e igualmente expressivo para um protótipo académico.  

3. **Modularidade Máxima**  
   - Ao manter produções distintas por categoria (declarações, tipos, instruções, expressões), a gramática fica escalável.  
   - Se for necessário suportar alterações ou extensões da linguagem, basta acrescentar, substituir ou remover sub-produções sem reescrever blocos inteiros.  

4. **Tratamento de Erros Básico Mas Objetivo**  
   - O parser reporta imediatamente o primeiro erro sintático, permitindo ao utilizador corrigir antes de prosseguir.  
   - A simplicidade desta abordagem é intencional para reduzir complexidade neste projeto; o foco principal foi garantir que, quando a sintaxe está correta, a AST gerada reflete fielmente o programa Pascal.  

Em conjunto, estas escolhas resultam num analisador sintático que é, ao mesmo tempo, **fiel** ao Pascal, **claro** para quem o lê, **flexível** para evoluir e suficientemente **robusto** para fornecer ASTs coerentes para fases posteriores de análise semântica e geração de código.  





## Analisador Semântico

O analisador semântico, implementado através da classe `SemanticAnalyzer` do ficheiro `ana_sem.py` e das classes auxiliares `Scope` e `Symbol`, aplica um conjunto de verificações que visam garantir que o programa Pascal está correto, não apenas em termos de sintaxe, mas também em termos de uso de identificadores, consistência de tipos, validade de constantes e conformidade com as regras *standard*. A seguir descrevem-se, de forma agrupada por categoria, todos os casos de erro que são explicitamente detetados e reportados durante a análise semântica.

---

### 1. Gestão de Tabela de Símbolos e *Visibility*

1. **Redeclaração no Mesmo *Scope***  
   - Sempre que se tenta definir (via `Scope.define`) um símbolo cujo nome já existe no *scope* atual, é lançado um erro `SemanticError`. Isso aplica-se a variáveis, constantes, tipos, funções ou procedimentos.  
   Exemplo:  
     ```pascal
     var x: integer;
     var x: real;   (* Erro: Variável 'x' já foi declarada neste scope *)
     ```

2. **Uso de Identificador Não Declarado**  
   - Ao tentar resolver (`Scope.resolve`) um nome que não foi definido em nenhum *scope* acessível, lança-se `SemanticError`. Isto evita referências a variáveis ou funções que ainda não existem.  
   Exemplo:  
     ```pascal
     begin
       writeln(a);   (* Erro: Variável 'a' usada mas não declarada *)
     end;
     ```

3. **Visibilidade Corretamente Aninhada (*Nested Scopes*)**  
   - Cada bloco (função, procedimento ou bloco principal) cria um novo *scope* filho. Um nome previamente definido num *scope* pai fica acessível, mas redeclarações só são possíveis em *scopes* distintos.  
   - Ocorre um erro, no mesmo *scope*, se tentar definir duplicadamente. Se for num *scope* filho, não há erro; porém, se o pai já tiver um símbolo com o mesmo nome, o `resolve` encontra-o, mas não impede uma definição local.  

---

### 2. Declarações de Constantes

Na declaração de constantes, foi necessário ter em atenção a declaração de **constantes com o mesmo nome**  
   - Se, numa `visit_consts`, o nome da constante já existir no *scope* atual, reporta-se esse erro.  
     ```pascal
     const pi = 3.14;
     const pi = 22/7;   (* Erro: Constante 'pi' já declarada. *)
     ```

---

### 3. Declarações de Tipos

1. **Redeclaração de Tipo**  
   - Se o identificador de tipo já existir no *scope* atual, `define` lança erro.  
     ```pascal
     type T = integer;
     type T = real;   (* Erro: Variável 'T' já foi declarada neste scope. *)
     ```

2. **Tipos `RECORD`**  
   - Para cada `record`, verifica-se:  
     - **Campos Duplicados**: dois campos com o mesmo nome no mesmo `record` provocam erro.  
       ```pascal
       type R = record
         x: integer;
         x: real;  (* Erro: Campo 'x' já definido no record 'R'. *)
       end;
       ```

3. **Tipos `ENUM`**  
   - Ao declarar um `enum`, cada etiqueta (identificador) passa a ser definida como símbolo de tipo `enum` e marcada como constante já inicializada. Se o mesmo identificador de enumarado já existir como outro símbolo (constante ou variável), error.  
     ```pascal
     type Cores = (Red, Green, Blue, Red);  (* Erro: Variável 'Red' já foi declarado neste scope. *)
     ```

4. **Tipos `ARRAY`**  
   - Para `array [lower..upper] of T`:  
     - `lower` e `upper` devem ser `const_expr`. Se não forem (por exemplo, algum deles for uma expressão não constante), lança erro.  
       ```pascal
       type A = array[x..10] of integer;   (* Erro: 'x' não é constante. *)
       ```
     - Se o `const_expr` for `id`, resolve-se esse identificador; se não for `kind='const'` ou não for do tipo `integer`, erro.  
       ```pascal
       const M = 'hello';
       type A = array[M..10] of integer;  (* Erro: M não é constante integer. *)
       ```
     - Verifica-se também se `lower <= upper`.  

5. **Tipos `PACKED`**  
   - Se for `packed record`, simplesmente delega-se no processamento normal de `record`.  
   - Se for `packed array`, aplica-se o mesmo esquema de verificação de limites constantes como em `array`.  
   - Caso o `packed` envolva outro tipo que não seja `array` ou `record`, verifica-se recursivamente até se encontrar um tipo básico ou `id_type`.  

6. **Outros Tipos Compostos e `SET`**  
   - `set of T`: Verifica-se que `T` seja um tipo ordinal (`integer`, `char`, `boolean`, `enum` ou `subrange`).  
     - Se `T` for `subrange`, as regras de subrange são aplicadas: extremos devem ser constantes e `integer` (ou `char`).  
     - Caso contrário, identifica-se `T` como string (nome de tipo) e resolve-se no *scope*; se `T` não for de tipo válido ou não existir, erro.  
       ```pascal
       type C = set of real;   (* Erro: Tipo do elemento do conjunto inválido: real não é ordinal. *)
       ```
   - Se `T` for `id_type` que referencia outro tipo definido, verifica-se recursivamente até se obter o tipo base e confirma-se se é ordinal.  

---

### 4. Declarações de Variáveis

1. **Nome de Variável Idêntico a Constante**  
   - Se se tentar declarar uma variável cujo nome já existe como constante no mesmo *scope*, lança-se erro.  
     ```pascal
     const pi = 3.14;
     var pi: integer;  (* Erro: não pode declarar uma variável 'pi' com o mesmo nome de uma constante. *)
     ```

2. **Validação de Limites de Array em Declaração de Variável**  
   - Se o tipo da variável for `array [lower..upper] of T`, aplicam-se exatamente as mesmas verificações usadas em declarações de tipos:  
     - `lower` e `upper` devem ser constantes inteiras, caso contrário, é lançado um erro.  
     - Se forem identificadores, devem ter sido declarados como constantes do tipo integer.  

3. **Tipos Complexos em Variáveis**  
   - Se o tipo for `packed record`, `record`, `enum`, `subrange` ou `set`, o analisador visita (via `visit`) o nó do tipo para validar campos, variantes, subranges, etc.  
   - Apenas após essas validações, a variável é registada no *scope*, com o tipo normalizado (por ex. `record_<nome>`, `enum`, `array_<limites>_of_<tipo>`).

4. **Inicialização Implícita de Parâmetros**  
   - Depois de definir cada variável, a fase semântica não marca automaticamente a variável como inicializada (exceto parâmetros e constantes).  
   - Embora não haja código específico neste analisador para erro de “uso antes de atribuição”, existe o conjunto `self.initialized` para acompanhar constantes e parâmetros.  

---

### 5. Declarações de Funções e Procedimentos

1. **Redeclaração de Função/Procedimento**  
   - Se, no *scope* atual, já existir uma função ou procedimento com o mesmo nome, lança-se erro.  
     ```pascal
     function f(x: integer): integer; begin ... end;
     function f(y: real): real; begin ... end;   (* Erro: A função 'f' já está definida. *)
     ```

2. **Validação de Parâmetros**  
   - Para cada parâmetro `param : <lista_ids> : <tipo>`, verifica-se:  
     - Se `<tipo>` for `array type`, aplicam-se as mesmas regras de limites constantes (e é necessário garantir que limites sejam `const_expr`).  
     - Caso contrário, obtém-se a representação normalizada do tipo (por ex. `integer`, `real`, `record_<nome>`).  
   - Após normalização, insere-se cada `param` no *scope* da função/procedimento como variável inicializada (parte de `self.initialized`).  
   - Se algum identificador do parâmetro entrar em conflito com um símbolo existente no mesmo *scope* do bloco, o `define` rejeita a redeclaração.  

3. **Tipo de Retorno de Função**  
   - O nó `return_type` é normalizado (podendo ser tipo simples, `id_type`, `array`, `record`, etc.).  
   - Se for um tipo composto (por ex. `packed record` ou outro `record`), visita-se o nó correspondente para validar os campos.  
   - O tipo final de retorno (`func_sym.return_type`) fica disponível para validar numa fase posterior.

4. ***Scope* Interno e Visibilidade**  
   - Um novo *scope* filho é criado para os parâmetros e o corpo da função/procedimento.  
   - Dentro desse *scope*, parâmetros não podem ser redeclarados e são considerados já inicializados.  
   - No final da análise do bloco interno, o *scope* volta a ser o anterior, garantindo que símbolos locais não passem para blocos de nível superior.

---

### 6. Validação de Registos (*Records*)

1. **Campos Fixos (*Non-Variant*)**  
   - Cada `field_list` é processada de modo a validar que os tipos de cada campo são válidos e que não existem nomes duplicados.  
     ```pascal
     type R = record
       x, y: integer;
       x: real;    (* Erro: Campo 'x' duplicado em record. *)
     end;
     ```

2. **Parte `VARIANT`**  
   - Se o `record` contiver um bloco `case <discriminador> : <Tipo> of ... end`:
     - O discriminador deve corresponder a um campo fixo (já definido) e ser de tipo ordinal (`integer`, `char`, `boolean` ou `enum`). Caso contrário, erro.  
       ```pascal
       type R = record
         a: real;
         case b: integer of  (* Erro: Discriminador 'b' não declarado como campo do record. *)
       end;
       ```
     - Cada ramo `variant` especifica uma lista de constantes (ex.: `1, 2, 3`) seguidas de `:` e de campos internos. Para cada constante:  
       - A expressão que define a constante deve ter o mesmo tipo do discriminador. Caso contrário, erro.  
         ```pascal
         type R = record
           tag: integer;
           case tag: integer of
             true: (x: integer);   (* Erro: Label de variant tem tipo boolean, mas discriminador é integer. *)
         end;
         ```
       - Dentro do mesmo ramo, verifica-se se há duplicação de campos internos. Se sim, dá erro.  
         ```pascal
         type R = record
           tag: boolean;
           case tag: boolean of
             true: (x: integer; x: real);   (* Erro: Campo 'x' duplicado na variante de 'tag'. *)
         end;
         ```

---

### 7. Conjuntos (SET)

- **Tipo de Elemento Inválido**  
   - Para `set of T`, o tipo `T` deve ser um tipo ordinal. Se `T` for outro tipo (por ex. `real`, `array`, `record` não ordinal), lança-se um erro.  
     ```pascal
     var s: set of real;   (* Erro: Tipo de elemento de conjunto inválido: real não é ordinal. *)
     ```

---

### 8. Atribuições

1. **Retorno em Função**  
   - Se o identificador da atribuição coincidir com o nome da função em análise, trata-se de uma atribuição do valor de retorno.  
   - É verificado que o tipo da expressão atribuída (`expr`) é idêntico ao tipo de retorno da função.  
   - Se `expr_type` for diferente de `return_type`, é lançado o seguinte erro:  
     ```pascal
     function f(x: integer): real;
     begin
       f := x + 1;   (* Erro: Tipo de retorno incorreto em 'f': esperado real, mas foi integer. *)
     end;
     ```

2. **Atribuição a Constante**  
   - Se o lado esquerdo (`var_node`) se referir a um nó do tipo `('var', nome)` e esse nome corresponder a um símbolo já definido como `kind='const'`, gera-se  
     ```pascal
     const pi = 3.14;
     begin
       pi := 3.14159;   (* Erro: Não pode atribuir a constante 'pi' *)
     end;
     ```

3. **Variável Não Declarada**  
   - Se o nome não constar nem no `current_scope` nem no `global_scope`, lança-se  
     ```pascal
     begin
       x := 10;   (* Erro: Variável 'x' não declarada *)
     end;
     ```

4. **Tipos Incompatíveis**  
   - Depois de obter o tipo da variável (`var_type`) e o tipo da expressão (`expr_type`):  
     - Se `expr_type.upper()` for diferente de `var_type.upper()`, é lançado um erro. Por exemplo:    
       ```pascal
       var a: integer;
           b: real;
       begin
         a := b;   (* Tipos incompatíveis na atribuição: variável 'a' é integer, mas expressão é real. *)
       end;
       ```

5. **Inicialização de Variável**  
   - Se a atribuição for válida e o nó for mesmo `('var', nome)`, adiciona-se `nome.lower()` ao conjunto `self.initialized`, para permitir que verificações de uso posterior não falhem por 'uso antes de inicialização'.  
     ```pascal
     var x: integer;
     begin
       x := 5;             (* Aqui 'x' passa a estar inicializada *)
       y := x + 1;         (* Se 'y' não estiver declarada, continua a dar erro de 'Variável não declarada' *)
     end;
     ```

---

### 9. Uso de Variáveis (`visit_var`)

- **Uso Antes de Inicialização**  
   - Se `nome_var.lower()` não pertence a `self.initialized`, lança-se  
     ```pascal
     var x: integer;
     begin
       writeln(x);   (* Erro: Variável 'x' usada antes de inicialização. *)
     end;
     ```

---

### 10. Indexação de Arrays

1. **Base Não é Array**  
   - Obtém-se `base_type` através de `current_scope.resolve(key).type`.  
   - Se `base_type` não for uma tupla com a primeira componente `'array'`, dispara-se  
     ```pascal
     var x: integer;
     begin
       writeln(x[1]);   (* Erro: "Tentativa de indexar uma variável que não é um array, mas do tipo 'integer' *)
     end;
     ```

2. **Índice não Inteiro**  
   - Aplica-se `idx_type = self.visit(indice)`.  
   - Se `idx_type` for diferente de `'integer'`, lança-se  
     ```pascal
     var a: array[1..5] of integer;
         i: real;
     begin
       a[i] := 10;  (* Erro: Índice do array deve ser INTEGER, mas é do tipo real.*)
     end;
     ```

---

### 11. Acesso a Campos de Registo

1. **Resolução do Tipo da Base**  
   - Se `base_node[0] == 'var'`, o tipo de base obtém-se diretamente de `self.current_scope.resolve(base_node[1].lower()).type`.  
   - Caso contrário, usa-se `self.visit(base_node)` para avaliar o tipo de uma expressão aninhada (por ex. outra indexação ou campo).  

2. **Base Não é um `record`**  
   - Resolve-se `type_sym = current_scope.resolve(base_type)`.  
   - Se `type_sym` não tiver atributo `fields` (i.e., não for um símbolo de record), dispara um erro:  
     ```pascal
     var x: integer;
     begin
       writeln(x.field);   (* Erro: Tentativa de aceder campo 'field' de (integer). *)
     end;
     ```

3. **Campo Inexistente**  
   - Se `field_name.lower()` não constar em `type_sym.fields`, dispara este erro:  
     ```pascal
     type Pessoa = record
       nome: string;
       idade: integer;
     end;
     var p: Pessoa;
     begin
       writeln(p.altura);   (* Erro: Campo 'altura' não existe em 'Pessoa'. *)
     end;
     ```

---

### 12. Chamadas de Função/Procedimento e Casts

1. **Identificador Não Registado**  
   - Tenta-se `self.current_scope.resolve(nl)` para encontrar o símbolo. Se falhar, assume-se que pode ser *cast* (ver ponto seguinte).  
   - Se, posteriormente, não se confirmar função nem *cast* válido, lança-se um erro como:  
     ```pascal
     begin
       f(10);   (* Erro: Variável ou função 'f' usada mas não declarada.*)
     end;
     ```

2. **Cast Genérico**  
   - Se o símbolo existe e não tem `params` nem `return_type`, mas `sym.type.lower() == nl`, trata-se de um *cast*.  
   - Se `len(argumentos)` for diferente de 1, dispara:  
     ```pascal
     var x: integer;
     begin
       integer(1,2);   (* Erro: Cast para 'integer' espera 1 argumento, mas recebeu 2. *)
     end;
     ```

3. **Cast Específico para `real(...)`**  
   - Se o nome for exatamente `"real"`, aplica-se a mesma lógica do *cast*, mas verifica-se que o `at` (tipo do argumento) é `'integer'` ou `'real'`.  
   Exemplo de erro:  
     ```pascal
     var b: boolean;
     begin
       real(b);   (* Erro: Cast real(boolean) inválido; só integer ou real. *)
     end;
     ```

4. **Chamada de Função/Procedimento Definido**  
   - Se existe `sym = resolve(nl)` e esse símbolo tem `params`, procede-se a:  
     1. **Aridade Incorreta**:  
        ```pascal
        function soma(a: integer; b: integer): integer;
        begin
          soma := a + b;
        end;
        begin
          writeln(soma(1));   (* Erro: 'soma' espera 2 argumentos, mas recebeu 1. *)
        end;
        ```

     2. **Tipo de Cada Argumento**:  
        - Se `at` for diferente de `ptype`, mas não entrar nos casos de conversão implícita, dispara um erro como:  
          ```pascal
          function f(x: integer; y: real): real;
          begin
            f := x + y;
          end;
          begin
            writeln(f(true, 3.0));   (* Erro: Argumento para 'x' deve ser integer, mas recebeu boolean. *)
          end;
          ```
     - Se o símbolo tem `return_type`, devolve-se `sym.return_type.casefold()`. Caso seja procedimento, devolve-se `None`.

5. **Funções Built-in `write`/`writeln`**  
   - Permitem múltiplos argumentos, mas todos devem ser variáveis já declaradas de tipo válido.  
   Exemplo de erro:  
     ```pascal
     var s: set of integer;
     begin
       writeln(s);   (* Erro: A função 'writeln' não pode receber um argumento do tipo 'set'. *)
     end;
     ```

6. **Funções Built-in `read`/`readln`**  
   - Cada argumento pode ser:
     1. **Variável Simples**:  
        ```pascal
        var x: integer;
        begin
          readln(x);
        end;
        ```

     2. **Array**:  
        - Se `a[0] == 'array'`, obtém‐se `a[1] = ('var', varname)`.  
        - Se houver índices, verifica-se `visit(a[2]) == 'integer'`.  
        Exemplo de erro:  
          ```pascal
          var a: array[1..5] of integer;
              i: boolean;
          begin
            readln(a[i]);   (* Erro: O índice do array tem de ser do tipo INTEGER mas é do tipo boolean.*)
          end;
          ```

     3. **Campo (`'field'`)**:  
        - Chama‐se `visit_field(a[1])` para forçar verificação de acesso a campo.

     4. Caso não seja nenhum destes, lança:  
        ```pascal
        var x: real;
        begin
          readln(1 + x);   (* Erro: A função 'readln' não pode receber um argumento do tipo 'binop'.*)
        end;
        ```

---

### 13. Estruturas de Controlo

#### 13.1 `if`

1. **Condição não Boolean**  
   - Avalia `cond_type = self.visit(cond)`.  
   - Se `cond_type` for diferente de `'boolean'`, lança este erro:  
     ```pascal
     var x: integer;
     begin
       if x then   (* Erro: A condição do IF deve ser boolean, mas é integer. *)
         writeln('OK');
     end;
     ```

2. **Visita de Ramos**  
   - Se `then_stmt` ou `else_stmt` não forem `None`, chama-se recursivamente `self.visit(...)` para validar instruções aninhadas.

#### 13.2 `for`

1. **Variável de Controlo não `integer`**  
   - Resolve-se `sym = current_scope.resolve(var_name.lower())`.  
   - Se `sym.type.lower()` for diferente de `'integer'`, dispara:  
     ```pascal
     var i: real;
     begin
       for i := 1 to 10 do   (* Erro: Variável de controlo do FOR 'i' deve ser integer, mas é real. *)
         writeln(i);
     end;
     ```

2. **Expressão Inicial e Final não Inteiras**  
   - Obtém-se `t_start = self.visit(start_expr).lower()` e `t_end = self.visit(end_expr).lower()`.  
   - Para cada um deles, se for diferente de `integer'`, dispara este erro: 
     ```pascal
     var i: integer;
         r: real;
     begin
       for i := r to 5 do   (* Erro: Expressão inicial do FOR deve ser integer, mas é real. *)
         writeln(i);
     end;
     ```
     ou
     ```pascal
     var i: integer;
         b: boolean;
     begin
       for i := 1 to b do   (* Erro: Expressão final do FOR deve ser integer, mas é boolean. *)
         writeln(i);
     end;
     ```
     respetivamente.

3. **Inicialização da Variável de Controlo**  
   - Se tudo for válido, adiciona-se `var_name.lower()` a `self.initialized`.

4. **Visita do Corpo**  
   - Chama-se `self.visit(body)` para validar instruções internas.

#### 13.3 `while`

1. **Condição não Boolean**  
   - Se `self.visit(cond_expr)` não for 'boolean', é lançado este erro:  
     ```pascal
     var x: integer;
     begin
       while x do   (* Erro: Condição de WHILE deve ser boolean, mas é integer. *)
         x := x - 1;
     end;
     ```

2. **Visita do Corpo**  
   - Chama-se, depois, `self.visit(body)`.

#### 13.4 `repeat`

1. **Visita das Instruções Internas**  
   - Itera sobre `stmts`. Se `stmt` não for `None`, chama `self.visit(stmt)`.

2. **Condição `until` não Boolean**  
   - Se `self.visit(cond).lower()`for diferente de `'boolean'`, dispara este erro:  
     ```pascal
     var x: integer;
     begin
       x := 5;
       repeat
         writeln(x);
         x := x - 1;
       until x   (* Erro: Condição de REPEAT…UNTIL deve ser boolean, mas é integer. *)
     end;
     ```

#### 13.5 `case`

1. **Expressão do `case` não Ordinal**  
   - Se `expr_type = self.visit(expr_node).lower()` não for `'integer'`, `'char'` ou `'enum'`, dispara:  
     ```pascal
     var x: real;
     begin
       case x of   (* Erro: Expressão de CASE deve ser ordinal (INTEGER, CHAR ou ENUM), mas é real. *)
         1: writeln('um');
         2: writeln('dois');
       end;
     end;
     ```

2. **Labels de Cada Alternativa**  
   - Para cada `(const_list, stmts)`:  
     - Cada `const_node` em `const_list` é passado a `self.visit(const_node)`. Se o `label_type` for diferente de `expr_type`, lança este erro:  
       ```pascal
       var c: char;
       begin
         case c of   (* Erro: Label de CASE tem tipo integer, mas a expressão é char. *)
           1: writeln('um');
           'A': writeln('A');
         end;
       end;
       ```

     - É também mantido um `seen_labels` (conjunto) com `repr(const_node)` para detetar duplicados. Se `repr(const_node)` já existir, lança:  
       ```pascal
       var i: integer;
       begin
         case i of   (* Erro: Label de CASE repetida: ('const_expr', 'integer', 1). *)
           1: writeln('um');
           1: writeln('um novamente');
         end;
       end;
       ```

3. **Visita das Instruções em Cada Ramo**  
   - Se `stmts` não for vazio, itera-se e chama-se `self.visit(stmt)` para cada `stmt`.

---

### 14. Bloco `with`

1. **Variável Não Suportada**  
   - Para cada `var_node` em `var_list`, se `var_node[0].lower() ≠ 'var'`, dispara um erro como este:  
     ```pascal
     type Pessoa = record
       nome: string;
     end;
     var p: Pessoa;
     begin
       with (p) do   (* Erro: WITH só suporta variáveis simples, mas recebeu 'compound'. *)
         writeln(nome);
     end;
     ```

2. **Variável Não Registada ou Não `record`**   
   - Se o tipo da variável não tiver o atributo `fields`, lança um erro:  
     ```pascal
     var x: integer;
     begin
       with x do   (* Erro: Variável 'x' em WITH não é um record, mas é do tipo 'integer'. *)
         writeln(x);
     end;
     ```

3. **Definição de Campos no Novo *Scope***  
   - Se existirem campos com nomes repetidos (ou que colidam com símbolos já definidos no próprio `with_scope`), `Scope.define` dispara erro de redeclaração de símbolo.  
   Erro:  
     ```pascal
     type R = record
       a: integer;
       b: integer;
     end;
     var r: R;
     begin
       with r do
         a := 10;   (* Erro: Variável 'a' já foi declarada neste scope. *)
     end;
     ```

### 15. Labels e `GOTO`

1. **Redeclaração de Label**  
   - Se, numa `visit_labels`, um rótulo já tiver sido definido no mesmo *scope*, lança-se erro:  
     ```pascal
     label 10, 20, 10;   (* Erro: Label '10' já declarada neste scope. *)
     ```

2. **Uso de Label sem Declaração (em `GOTO`)**  
   - Quando se encontra uma instrução `goto <INTEGER>`, o analisador verifica se esse inteiro foi declarado previamente como label (procura no *scope* via `resolve`). Se não, sinaliza erro.  
     ```pascal
     begin
       goto 100;   (* Erro: GOTO para label '100' que não está declarada. *)
     end;
     ```

3. **Rótulo Associado a Declaração**  
   - Em `visit_labeled_statement`, garante-se que o número de rótulo (por ex. `100: writeln('ola');`) corresponda a um rótulo previamente declarado. Caso contrário, erro.  
     ```pascal
     100: writeln('ola');  (* Erro: Label '100' não declarada antes de ser usada. *)
     ```
     
### 16. Literais, Formatação e Operadores Unários

#### 16.1 `visit_fmt`

1. **Largura (`width`)**  
   - Avalia se `width_type` é igual a `self.visit(width_expr)`. Se `width_type.casefold()` for diferente de `'integer'`, dispara um erro:  
     ```pascal
     var x: integer;
     begin
       x := 42;
       writeln(x:'5':2);   (* Formato width em '(x:'5':2)' deve ser INTEGER, mas foi texto. *)
     end;
     ```

2. **Precisão (`precision`)**  
   - Se `precision_expr` não for `None`, avalia‐se `prec_type = self.visit(precision_expr)`. Se `prec_type.casefold()` for diferente de `'integer'`, dispara:  
     ```pascal
     var y: real;
         w: integer;
     begin
       y := 2.718;
       w := '3';   (* w é texto, mas precisa ser integer *)
       writeln(y:5:w);   (* Erro: Formato precision em '(y:5:'3')' deve ser INTEGER, mas foi texto. *)
     end;
     ```

3. **Retorno de Tipo**  
   - Devolve `expr_type` como tipo resultante do nó `fmt`.  
     ```pascal
     var c: char;
     begin
       c := 'A';
       writeln(c:3);   (* Retorna tipo CHAR para c *)
     end;
     ```

#### 16.2 `visit_not`

1. **Operador `not` com Operando Não Boolean**  
   - Avalia `expr_type = self.visit(expr)`. Se `expr_type` for diferente de `'boolean'`, lança este erro:  
     ```pascal
     var x: integer;
     begin
       if not x then   (* Erro: Operador 'not' espera expressão do tipo boolean, mas é do tipo integer. *)
         writeln('OK');
     end;
     ```

2. **Retorno**  
   - Se o operando for boolean válido, retorna `'boolean'`.  
   Erro:  
     ```pascal
     var b: boolean;
     begin
       b := true;
       if not b then   (* Válido: 'not b' retorna boolean *)
         writeln('False');
     end;
     ```
     
### 17. Literais de Conjunto

1. **Inconsistência de Tipos**  
   - Avalia `tipos = [self.visit(elem) for elem in elementos]`.  
   - Se existir qualquer `t` em `tipos` diferente de `tipos[0]`, é lançado um erro como este:  
     ```pascal
     var s: set of integer;
     begin
       s := [1, 'A'];   (* Erro: Todos os elementos do conjunto devem ter o mesmo tipo, mas encontrou integer e char. *)
     end;
     ```
     
   - Caso contrário, retorna-se `('set', tipo_base)`.  
     ```pascal
     var s: set of char;
     begin
       s := ['A', 'B', 'C']; (* Válido: todos os elementos são CHAR *)
     end;
     ```
     
### 18. Operações Binárias

1. **Operandos Aritméticos (`+`, `-`, `*`, `/`)**  
   - Se `base_esq` ou `base_dir` (tipos minúsculos) não forem `'integer'` ou `'real'`, é disparado este erro:    
     ```pascal
     var a: integer;
         b: boolean;
     begin
       a := 5 + b;   (* Erro: Operador '+' só pode ser aplicado a tipos numéricos, mas recebeu integer e boolean. *)
     end;
     ```
   - Se algum dos operandos for `real` ou se `op` for `'/'`, retorna `'real'`; caso contrário, retorna `'integer'`.  
     ```pascal
     var x: integer;
         y: real;
         z: real;
     begin
       z := x * y;   (* Válido: um operando é real → resultado é real *)
     end;
     ```

2. **`div` e `mod` (Divisão Inteira)**  
   - É exigido que tanto `base_esq` como `base_dir` sejam `'integer'`.  
   - Se não for o caso, dispara:  
     ```pascal
     var i: integer;
         r: real;
     begin
       i := 10 div r;   (* Erro: Operador 'div' requer dois inteiros, mas recebeu integer e real. *)
     end;

3. **Comparações de Igualdade e Desigualdade (`=`, `<>`)**  
   - Se o conjunto formado por `base_esq` e `base_dir` for um subconjunto de `{'integer', 'real'}`, devolve `'boolean'`.  
     ```pascal
     var i: integer;
         r: real;
         flag: boolean;
     begin
       flag := (i = r);   (* Válido: compara integer e real → devolve boolean *)
     end;
     ```
   - Caso contrário, se `tipo_esq` for diferente `tipo_dir`, lança:  
     ```pascal
     var b: boolean;
         c: char;
     begin
       if b = c then   (* Comparação '=' requer operandos compatíveis, mas recebeu boolean e char. *)
         writeln('ok');
     end;
     ```
   - Se os tipos são iguais mas não estão em `{'boolean','char','texto','set'}`, lança este erro:  
     ```pascal
     type Pessoa = record
       nome: string;
     end;
     var p1, p2: Pessoa;
         flag: boolean;
     begin
       flag := (p1 = p2); (* Erro: Operador '=' não suportado para tipo record. *)
     end;
     ```
   - Caso contrário, devolve `'boolean'`; por exemplo, comparar dois *boolean* é permitido.

4. **Comparações Relacionais (`<`, `<=`, `>`, `>=`)**  
   - Aceita apenas se a `base_esq` for igual à `base_dir` e se a `base_esq` pertencer a `{'integer','real','char','texto'}`.  
   - Em qualquer outro caso, dispara um erro como:  
     ```pascal
     var i: integer;
         b: boolean;
     begin
       if i < b then   (* Erro: Operador relacional '<' não suportado para tipos integer e boolean. *)
         writeln('ok');
     end;
     ```

   - Se válido, devolve `'boolean'`.  
     ```pascal
     var s1, s2: string;
         flag: boolean;
     begin
       flag := (s1 <= s2);   (* Válido: string é 'texto' *)
     end;
     ```

5. **Operador `in`**  
   - Se o `tipo_dir` for `'set'`, verifica-se se `tipo_esq` é `'enum'`. Se não for, lança um erro:  
     ```pascal
     type Cores = (Red, Green, Blue);
     var cor: integer;
         s: set of Cores;
     begin
       if cor in s then   (* Erro: Elemento do tipo integer não compatível com o conjunto de enum. *)
         writeln('ok');
     end;
     ```
   - Caso contrário, espera-se `tipo_dir` como um tuplo `('set', elem_type)` ou similar:  
     - Se não for sequer um tuplo, dispara:  
       ```pascal
       var x: integer;
       begin
         if x in 5 then    (* Erro: Operador 'in' requer um conjunto do lado direito, mas recebeu integer. *)
           writeln('ok');
       end;
       ```
     - Se for tuplo, extrai `elem_type = tipo_dir[1]`. Se o `tipo_esq` for diferente de `elem_type`, dispara este erro:  
       ```pascal
       var x: char;
           s: set of integer;
       begin
         if x in s then   (* Erro: Elemento do tipo char não compatível com o conjunto de integer. *)
           writeln('ok');
       end;
       ```
   - Se válido, devolve `'boolean'`.  
     ```pascal
     type Dias = (Seg, Ter, Qua, Qui, Sex);
     var d: Dias;
         conj: set of Dias;
     begin
       conj := [Seg, Qua, Sex];
       if d in conj then   (* Válido: enum in set of enum *)
         writeln('Sim');
     end;
     ```

6. **Operadores Lógicos (`and`, `or`)**  
   - Se a `base_esq` ou a `base_dir` não forem `'boolean'`, dispara um erro como este:  
     ```pascal
     var b: boolean;
         i: integer;
     begin
       if b and i then   (* Erro: Operador lógico 'and' requer dois boolean, mas recebeu boolean e integer. *)
         writeln('ok');
     end;
     ```
   - Se válido, devolve `'boolean'`.  
     ```pascal
     var a, b: boolean;
         fl: boolean;
     begin
       fl := a or b;   (* Válido: retorna boolean *)
     end;
     ```

7. **Operador Desconhecido ou Não Suportado**  
   - Caso `op` não se enquadre em nenhuma das categorias acima ou a combinação de tipos não seja permitida, dispara  
     ```pascal
     var x: integer;
         y: integer;
     begin
       x := y ** 2;  (* Erro: Operador desconhecido '**' ou operação não suportada entre integer e integer. *)
     end;
     ``` 

### 19. Normalização de Tipos

A função `_normalize_type` tem como objetivo principal converter um nó de tipo da árvore sintática (AST) numa representação interna simples e uniforme que será utilizada em toda a análise semântica e na geração de código. Sempre que o parser identificar um tipo complexo, esta função faz a tradução desse nó AST para um valor que indica claramente, e sem ambiguidades, qual é o tipo subjacente.  
Por exemplo, um tipo simples é convertido numa string minúscula (“integer”, “char”, “boolean” etc.), um array passa a um tuplo `('array', tipo_elemento)` que identifica o tipo dos seus elementos, um enum é representado por “enum” e subranges são tratados como inteiros. No caso de tipos “packed” ou “short_string”, a função desce recursivamente à definição interna, extraindo o tipo base (como converter “packed array” num array simples ou traduzir “short_string” em “texto”).  
Em suma, `_normalize_type` garante que, quando o analisador semântico precisa de comparar, armazenar ou propagar tipos, não existe ambiguidade nem variação de formato. Tudo é padronizado numa string ou numa estrutura (tuplo) com uma keyword que define o construtor (por ex. `('array', 'integer')` ou `'record'`). Isto facilita a validação da coerência de tipos em atribuições, expressões e chamadas de função, pois basta comparar estas representações normalizadas para determinar se dois tipos são compatíveis ou não.


### Resumo



1. **Redeclarações**  
   - Variável/constante/tipo/função/procedimento declarados mais do que uma vez no mesmo *scope*.

2. **Uso de Identificador Não Declarado**  
   - Qualquer referência a variável, constante, tipo, função ou procedimento que não exista em nenhum *scope*.

3. **Tipo Incompatível**  
   - Atribuição de valor a variável de tipo diferente, comparações incorretas, operadores usados com operandos de tipo inadequado e passagem de parâmetro com tipo divergente.

4. **Atribuição a Constante**  
   - Tentativa de atribuir valor a uma constante.

5. **Uso Antes de Inicialização**  
   - Variável utilizada antes de ter sido inicializada (não consta em `self.initialized`).

6. **Base Não é Array**  
   - Tentativa de indexar uma variável cujo tipo não é array.

7. **Índice Não Inteiro**  
   - Índice de array não é do tipo `integer`.

8. **Base Não é um Record**  
   - Tentativa de aceder a campo de um valor cujo tipo não é record.

9. **Campo Inexistente**  
   - Tentativa de aceder a campo que não está declarado no record.

10. **Cast Genérico Inválido**  
    - Cast para um tipo que espera 1 argumento, mas recebeu número diferente de argumentos.

11. **Cast Para Real Inválido**  
    - Cast `real(...)` com argumento cujo tipo não é `integer` nem `real`.

12. **Chamada de Função/Procedimento: Aridade Incorreta**  
    - Chamada de função/procedimento com quantidade de argumentos diferente da esperada.

13. **Chamada de Função/Procedimento: Tipo de Argumento Incompatível**  
    - Argumento passado para parâmetro tem tipo diferente do declarado (exceto casos permitidos de conversão implícita entre `integer` e `real` ou `texto` e `array of char`).

14. **Função/Procedimento Não Declarado**  
    - Tentativa de chamar identificador que não foi definido como função ou procedimento.

15. **Argumento em `write`/`writeln` Inválido**  
    - `write`/`writeln` recebe argumento cujo tipo não é `boolean`, `char`, `integer` ou `real`.

16. **Argumento em `read`/`readln` Inválido**  
    - `read`/`readln` recebe argumento que não seja variável simples, array ou campo válido de record; ou índice de array não é `integer`.

17. **Condição de IF Não Boolean**  
    - Condição em `if` cujo resultado de expressão não é do tipo `boolean`.

18. **Variável de Controlo do FOR Não Integer**  
    - Variável usada em `for` cujo tipo não é `integer`.

19. **Expressão Inicial/Final do FOR Não Integer**  
    - Expressão de início ou fim de loop `for` cujo tipo não é `integer`.

20. **Condição de WHILE Não Boolean**  
    - Condição em `while` cujo resultado não é `boolean`.

21. **Condição de REPEAT…UNTIL Não Boolean**  
    - Condição depois de `until` cujo tipo não é `boolean`.

22. **Expressão de CASE Não Ordinal**  
    - Expressão em `case` cujo tipo não é um tipo ordinal (`integer`, `char` ou `enum`).

23. **Label de CASE com Tipo Divergente**  
    - Rótulo num item de `case` cujo tipo não coincide com o tipo da expressão de `case`.

24. **Label de CASE Repetido**  
    - Rótulo duplicado na mesma construção `case`.

25. **Variável em WITH Não Suportada**  
    - `with` inclui nó que não seja `('var', nome)`.

26. **Variável em WITH Não é Record**  
    - Variável passada para `with` cujo tipo não é um record.

27. **Campo Duplicado em WITH**  
    - Dois campos com o mesmo nome introduzidos no *scope* do bloco `with`.

28. **GOTO para Label Não Declarada**  
    - Uso de `goto` com rótulo que não foi definido previamente.

29. **Label Não Declarada Antes de Ser Usada**  
    - Rótulo associado a instrução (`label_stmt`) sem ter sido declarado na secção `label`.

30. **Formato Width Não Integer**  
    - No nó de formatação `fmt`, o valor de `width` não é do tipo `integer`.

31. **Formato Precision Não Integer**  
    - No nó de formatação `fmt`, o valor de `precision` (se fornecido) não é do tipo `integer`.

32. **Operador `not` com Operando Não Boolean**  
    - Uso de `not` em expressão que não resulta em `boolean`.

33. **Elementos de Conjunto com Tipos Mistos**  
    - Literais de conjunto (`set` literal) contêm elementos de tipos diferentes.

34. **Operador Aritmético com Operandos Não Numéricos**  
    - `+`, `-`, `*`, `/` aplicados a valores cujo tipo não seja `integer` ou `real`.

35. **`div`/`mod` com Operandos Não Inteiros**  
    - Operadores `div` e `mod` usados em operandos cujo tipo não seja `integer`.

36. **Comparação `=`/`<>` com Operandos Incompatíveis ou Tipo Não Suportado**  
    - `=` ou `<>` entre tipos não numéricos compatíveis ou ambos não pertencentes a `boolean`, `char`, `texto` ou `set`.

37. **Comparações Relacionais `<`, `<=`, `>`, `>=` com Tipos Inválidos**  
    - Comparação relacional entre tipos distintos ou tipos não ordenáveis (fora de `integer`, `real`, `char`, `texto`).

38. **Operador `in` Sem Conjunto ou Tipos Incompatíveis**  
    - `in` aplicado quando o operando direito não é um conjunto ou quando o elemento não coincide com o tipo dos elementos desse conjunto.

39. **Operador Lógico `and`/`or` com Operandos Não Boolean**  
    - Uso de `and` ou `or` em operandos cujo tipo não seja `boolean`.

40. **Operador Desconhecido ou Não Suportado para Combinação de Tipos**  
    - Qualquer outro operador binário que não se enquadre nas categorias acima ou combinação de operandos não permitida.

41. **`id_type` Não Declarado**  
    - Ao normalizar tipo de identificador (`id_type`), identificador não encontrado no *scope*.

42. **Subrange com Limites Não Constantes ou Tipos Inválidos**  
    - Definição de subrange cujos limites não sejam `const_expr` ou não sejam `integer`/`char`.

43. **`array_type` com Limites Não Constantes ou Não Inteiros**  
    - Declaração de array cujos limites inferiores ou superiores não sejam constantes inteiras válidas.

44. **`packed array` com Limites Inválidos**  
    - Mesmas verificações de limites constantes que para `array_type`, mas dentro de `packed`.

45. **`set` de Tipo Não Ordinal**  
    - Definição de `set of T` em que `T` não é ordinal (`integer`, `char`, `boolean`, `enum` ou `subrange` válido).

46. **`file` de Tipo Inexistente**  
    - Definição de `file of T` em que `T` não está declarado ou não é tipo válido.

47. **Campo Duplicado em Record**  
    - Dois campos com o mesmo nome declarados no mesmo `record`.

48. **Discriminador de Record Não Existente ou Não Ordinal**  
    - Discriminador de `variant` em record que não corresponde a um campo fixo ou cujo tipo não seja ordinal.

49. **Rótulo de Variant com Tipo Divergente**  
    - Em record `variant`, constante de rótulo cujo tipo não coincide com o tipo do discriminador.

50. **Campo Duplicado Dentro de Ramo Variant**  
    - Dois campos com o mesmo nome dentro de uma única variante de record.

51. **`ID_LIST` Inválido**  
    - Lista de identificadores que inclui nome não válido (não verificado explicitamente, presumem-se regras do léxico).

52. **Parâmetro com Limites de Array Inválidos**  
    - Parâmetro em função/procedimento declarado como `array[...] of T` com limites não constantes ou não inteiros.

53. **Tipo de Retorno de Função Não Existente ou Inválido**  
    - Função cujo `return_type` referencia identificador inexistente ou tipo inválido.

54. **Função com Nome Já Definido**  
    - Criação de função cujo nome colide com símbolo já existente (constante, variável, tipo ou outra função/procedimento) no mesmo *scope*.

55. **Procedimento com Nome Já Definido**  
    - Semelhante ao caso de função: nome colide com símbolo existente no mesmo *scope*.

56. **Parâmetro com Nome Duplicado**  
    - Dois parâmetros com o mesmo nome na mesma lista de parâmetros (detetado porque `define` falha ao inserir duplicatas no novo *scope*).

57. **Variável Declarada com Nome de Constante**  
    - Declaração de variável cujo nome coincide com o de uma constante existente no mesmo *scope*.

58. **Declaração de Variável com Tipo Packed Complexo Inválido**  
    - `packed` envolvendo tipo distinto de `simple_type`, `array_type` ou `id_type` sem validação adicional; se aninhado, delega em `visit` recursivamente.

59. **Uso de Função/Procedimento Dentro de Expressão Incompatível**  
    - Tentar usar resultado de procedimento sem `return_type` em expressão booleana ou aritmética (não implementado explicitamente, mas resoluções falham se `None` for tratado como tipo).

60. **Conversão Implícita Não Permitida**  
    - Qualquer tentativa de comparar `integer` com `boolean` ou `char` com `integer`, sem cast explícito:  





## Gerador de código

O gerador de código apresentado (presente no `gerador_codigo.py`) destina‐se a transformar uma representação em árvore (AST) de um programa Pascal num conjunto de instruções para uma máquina virtual (a EWVM). O principal objetivo é visitar recursivamente cada nó da AST e emitir as instruções correspondentes para: manipulação de variáveis, constantes e arrays; suporte de expressões aritméticas; e ciclos (if, while, for), de acordo com a semântica do Pascal.  
De seguida é descrito, em linhas gerais, a estrutura e o funcionamento deste gerador, bem como as principais decisões tomadas na implementação.

### 1. Objetivo e Visão Geral  
O propósito principal do gerador de código é converter estruturas de alto nível (como declarações de variáveis, expressões aritméticas, chamadas a funções de I/O, ciclos, expressões condicionais, etc.) numa sequência de instruções máquina (como **PUSHI**, **LOADN**, **JZ**, **CALL**, entre outras) compreendida pela VM. Para isso, o gerador mantém:  

- Uma tabela de símbolos (`symtab`) que associa cada identificador a informações de localização (offset do gp, limites do array, tipo de elemento, etc.);  
- Um dicionário de constantes nomeadas (`consts`), para avaliar, em tempo de compilação, literais e expressões constantes;  
- Um mapa de sub‐rotinas (`subroutines`) definidas pelo utilizador, armazenando a label e o número de parâmetros de cada função/procedimento;  
- Uma lista com as instruções de código máquina (`code`) que vai sendo preenchida à medida que as instruções são geradas;  
- Um contador de rótulos (`label_counter`), para gerar identificadores únicos em cada salto condicional ou fim de loop.

O processo geral decorre em duas etapas principais:  

1. **Construção da Tabela de Símbolos**

   Para construir a tabela de símbolos (na função `build_symtab`), é necessário:

   - Percorrer todas as declarações (de tipos, constantes, variáveis, funções e procedimentos);  
   - Registar aliases de tipo para serem resolvidos posteriormente;  
   - Extrair literais constantes e registá-los em consts;  
   - Para cada variável global ou array, calcular o seu tamanho, reservar o espaço (se for um array, emite `PUSHI size`, `ALLOCN`, `STOREG offset`) e guardar a informação de offset e limites em `symtab`;  
   - Para cada sub‐rotina, registar em `subroutines` o nome, a label (nome em maiúsculas) e o número de parâmetros.  

2. **Geração Recursiva de Instruções**
   
   As funções responsáveis pela geração das instruções (cujo nome começa por `gen_`) obtém as informações necessárias a partir do nodo da AST e implementam a sua lógica.  

   - A função de entrada é a `gen_program`, que emite o **START**, processa o bloco principal e depois emite o **STOP**. Em seguida, fica responsável por gerar o código para cada função ou procedimento definido pelo utilizador.  

   - Cada nó da AST é atendido por um método `gen_<tipo>`. Por exemplo:  
     - `gen_const` -> emite **PUSHI**, **PUSHF** ou **PUSHS** dependendo do tipo literal;  

     - `gen_var` -> emite `PUSHG offset` ou `PUSHL offset` para carregar o valor da variável;  

     - `gen_array` -> empilha o endereço base (`gp[offset]`), empilha o índice atualizado (subtraindo o limite inferior, se não for zero), verifica limites com `CHECK 0 , size-1` e emite **LOADN**;  

     - `gen_assign` -> diferencia uma atribuição a uma variável simples de uma atribuição a um elemento de um array eE arrays, deve calcular o índice, fazer C**HECK,** carregar o valor da expressão e usar S**TOREN **para gravar no local correto;  

     - `gen_binop` -> gera comparações e operações aritméticas (por exemplo, **INF**, **INFEQ**, **ADD**, **SUB**, **MUL**, **DIV**, além de versões em ponto flutuante se algum operando for literal real);  

     - `gen_not` -> inverte o valor lógico, o que se traduz numa instrução **NOT**;  

     - `gen_if` -> avalia a condição, emite `JZ label_else`, gera o bloco “then”, emite `JUMP label_end`, emite `label_else:` e, se for caso disso, gera o bloco “else”, terminando em `label_end:`;  

     - `gen_while` -> cria labels `L#_WHILE` e `L#_ENDWHILE`, testa a condição com `JZ L#_ENDWHILE`, gera o corpo e emite `JUMP L#_WHILE`;  

     - `gen_for` -> trata um ciclo for como `for i := inicio to fim do …`, guardando a variável de controlo em `gp[offset]`, testando **INFEQ** ou **SUPEQ** e incrementando/decrementando em cada iteração.  

   Para operações de I/O (como **read**, **readln**, **write**, **writeln**), o gerador de código faz o seguinte:  

     - `write` / `writeln`: para cada argumento, verifica se é um literal de texto e emite um **WRITES**; caso contrário, emite um **WRITEI**, para inteiros. Em seguida, chama **WRITELN** se for o caso.  

     - `read` / `readln`: emite **READ** para ler uma string da heap e empilhar o seu endereço. Se a variável alvo for char, emite **CHARAT** para extrair o primeiro carácter; senão, emite **ATOI** para converter a string em inteiro. Por fim, armazena no registo adequado, com **STOREG** ou **STOREL**. No caso de ler diretamente para um elemento de array, empilha o endereço base, o índice atualizado, faz um **READ**, executa **CHARAT** ou **ATOI** consoante o tipo do elemento e usa **STOREN**.  


### 2. Tratamento de Constantes e Avaliação em Tempo de Compilação  
A função auxiliar `extrair_valor_constante` percorre nodos do tipo:

  - `const_expr` (literal de inteiro, real, boolean ou char), convertendo o valor textual para o tipo adequado;  
  - `var` (constante nomeada), procurando a definição em consts e chamando recursivamente;  
  - `binop` (operação binária de constantes), avaliando recursivamente as subexpressões e aplicando a operação aritmética.  

Este mecanismo é essencial para, por exemplo, calcular limites de arrays declarados com constantes ou expressões constantes, permitindo gerar as instruções `PUSHI size` e **ALLOCN** antes da execução.

### 3. Tabela de Símbolos (symtab) e Offsets
As variáveis globais simples guardam uma entrada `('global', offset)` em `symtab`, onde `offset` é o índice no gp (global pointer).  
Os arrays guardam `('array', offset, low, size, elem_tp)`, indicando:
  - `offset`: localização em gp de onde começa a estrutura,  
  - `low`: limite inferior do índice (por exemplo, 1 em array[1..100]),  
  - `size`: número de elementos (100 - 1 + 1 = 100),  
  - `elem_tp`: tipo dos elementos (ex.: 'char', 'integer' ou outro alias).  

Cada vez que surge uma declaração de um array, o gerador emite as seguintes instruções:
  - `PUSHI size`  
  - `ALLOCN`  
  - `STOREG offset`  

e depois incrementa offset para a próxima variável.

Da mesma forma, variáveis escalares reservam um único `gp[offset]` sem chamar **ALLOCN**.

Este esquema faz com que, em tempo de execução, o programa possa fazer `PUSHG offset` para obter o endereço base de um array ou o valor de uma variável num único passo.


### 4. Estruturas de Controle
De seguida é apresentada a lógica implementada para as estruturas de controlo.  

**If-Then-Else**
- Avalia a condição com chamadas recursivas (recorrendo a `gen(cond)`),
- Emite `JZ label_else`, pelo que, se o resultado for zero, vai para “else”,
- Gera o bloco “then” e emite `JUMP label_end`,
- Emite `label_else:` - se existir bloco “else”, gera‐o,
- Termina com o `label_end:`.

**While**
- Emite `label_start:` antes do teste,
- Gera a condição e emite `JZ label_end` (se for falsa, sai),
- Gera o corpo, emite `JUMP label_start` para a repetição do ciclo e, no fim, emite `label_end:`.

**For**
- Avalia `start_expr` e armazena em `gp[offset]`,
- Emite `label_start:`,
- Empilha `PUSHG offset` (valor atual de `i`) e avalia `end_expr`,
- Emite **INFEQ** (se o ciclo tiver um “to”) ou **SUPEQ** (se tiver antes um “downto”). Em seguida, emite um `JZ label_end` para sair quando a condição não se verificar,
- Gera o corpo do loop,
- Incrementa ou decrementa `gp[offset]` em 1 (**ADD** ou **SUB**) e armazena novamente,
- Emite `JUMP label_start`. No fim, emite `label_end:`.

Esta abordagem assegura que o ciclo se mantém ativo enquanto `i <= fim` (ou `i >= fim`) e executa corretamente a parte central em cada iteração.


### 5. Resumo
O gerador de código implementado traduz cada elemento de Pascal (declarações, expressões, loops, condicionais, chamadas a fuções, variáveis, arrays) num padrão de instruções da VM que respeitam o modelo de alocação em `gp` e `heap`. O código máquina gerado é colocado no ficheiro `.vm` correspondente ao código teste que foi executado (por exemplo, para o `test2.pas` é gerado o `test2.vm` com as instruções em código máquina correspondentes).  
De referir que tentámos implementar a geração para exemplos Pascal com definição de funções e procedimentos por parte do utilizador, não tendo conseguido corrigir alguns erros que apareciam no código máquina gerado para estes casos. No entanto, o código que conseguimos desenvolver para esta parte é na mesma apresentado, em comentário, no final do código do gerador. Também foram implementados, no analisador sintático e no semântico, certos elementos da linguagem Pascal para os quais não chegámos a implementar a geração. No entanto, consideramos importante este trabalho desenvolvido.  
É mantida uma tabela de símbolos para gerir offsets, tipos de elementos de array e dimensões, garantindo acesso correto e verificação de índices.  
O uso de `extrair_valor_constante` permite calcular tamanhos de arrays em tempo de compilação, evitando avaliar expressões em tempo de execução.  
Por fim, AST é percorrida com métodos `gen_<tipo>`, o que assegura que todos os nós válidos no Pascal são cobertos, lançando exceções caso surja um nó não implementado (como os referidos anteriormente).  
Este relatório pretendeu apresentar de forma clara e concisa a arquitetura e o fluxo de funcionamento do gerador de código, indicando as principais decisões de design e ilustrando exemplos. A modularidade (muitos métodos gen_...) e o uso de tabelas auxiliares tornam o código extensível a novas funcionalidades (novos operadores, funções embutidas, etc.), bastando implementar os respetivos métodos ou entradas na tabela de símbolos.





## Testes para avaliação do desempenho dos analisadores léxico, sintático, semânticos e geração de código máquina

Para validar o funcionamento do projeto, criámos um conjunto de ficheiros de teste com código Pascal standard, numerados de 0 a 12 (armazenados na pasta `tests`). Em cada um deles, verificámos as várias fases do compilador (analisador léxico, sintático, semântico e gerador de código para a VM). Em paralelo, foi também sempre criado um ficheiro complementar (`testX_erros.pas`) que inclui, em comentário, os erros semânticos específicos detetados no teste em questão.

- **Testes 0 a 6 e 10 a 12**  
  Nestes ficheiros, conseguimos executar com êxito o analisador léxico, o analisador sintático, o analisador semântico e gerar o respetivo código máquina. Ou seja, todo o código Pascal contido nestes testes utiliza apenas elementos da linguagem para os quais já implementámos geração de código para a VM.

- **Testes 7 a 9**  
  Embora o analisador léxico, sintático e semântico funcionem corretamente (todos os erros semânticos são detetados e assinalados no ficheiro `testX_erros.pas`), não conseguimos produzir código máquina para estes testes. A razão prende-se com o facto destes ficheiros conterem *functions* e *procedures* (e, em geral, construções Pascal mais complexas) para as quais não chegámos a implementar o gerador de código correspondente. Em suma:
  - O **Analisador Léxico** aceita todos os símbolos e literais;  
  - O **Analisador Sintático** reconhece toda a gramática, sem produzir erros sintáticos;  
  - O **Analisador Semântico** sinaliza corretamente todos os erros de tipos, *scopes*, inicializações, etc.;  
  - O **Gerador de Código** é incapaz de traduzir as *functions* e *procedures* presentes nestes testes para instruções válidas na VM, daí não produzir o ficheiro correspondente.

Em todos os testes (0 a 12), criámos um respetivo ficheiro `testX_erros.pas` onde comentámos todos os erros semânticos identificados. Desta forma, basta comparar o ficheiro original com o ficheiro de erros para verificar quais as regras semânticas que estão a ser aplicadas e quais as falhas (por exemplo, uso de variável não inicializada, incompatibilidade de tipos, etc.). Esses ficheiros de erros ajudam a garantir que o analisador semântico está a detetar precisamente cada situação incorreta, mesmo nos casos em que não há geração de código máquina (testes 7 a 9).

Concluindo e resumindo, as **Fases Léxica, Sintática e Semântica** validam com sucesso todos os testes (0 a 12). A **Geração de Código Máquina** é concluída com sucesso nos testes 0 a 6 e 10 a 12, não sendo suportada nos testes 7 a 9.  
Deste modo, demonstrámos a robustez do analisador nas três primeiras fases para todo o conjunto de exemplos, e identificámos claramente onde a geração de código não foi totalmente implementada devido à escassez de tempo.