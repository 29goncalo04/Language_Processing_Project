from ana_lex import tokens, build_lexer
import ply.yacc as yacc

# Definição da tupla 'precedence'
#    A tupla 'precedence' informa ao parser a associatividade e precedência dos operadores:
#    - 'nonassoc'  : operador não associativo (p.ex., ELSE encadeado com IF)
#    - 'left'      : associatividade à esquerda (p.ex., OR, AND, operadores aritméticos)
#    - 'right'     : associatividade à direita (p.ex., NOT)
precedence = (
    # Evita ambiguidade entre IF-ELSE encadeados
    ('nonassoc', 'IFX'),       # regra interna para IF sem ELSE    
    ('nonassoc', 'ELSE'),      # ELSE não se associa com IFX   
    # Operadores lógicos
    ('left', 'OR'),
    ('left', 'AND'),
    # Operador unário NOT
    ('right', 'NOT'),         # NOT associativo à direita
    # Comparações e operador IN
    ('left', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE', 'IN'),
    # Soma e subtração
    ('left', 'PLUS', 'MINUS'),
    # Produto, divisão real e inteiros
    ('left', 'TIMES', 'DIVIDE', 'DIV', 'MOD'),
    # Dois-pontos usado em rótulos e decl. de rótulos
    ('left', 'COLON'),
)

# PROGRAM <ID> ';' <block> '.'
def p_program(p):
    'program : PROGRAM ID SEMI block DOT'
    p[0] = ('program', p[2], p[4])



# <declarations> BEGIN <statement_list> END
def p_block(p):
    'block : declarations BEGIN statement_list END'
    p[0] = ('block', p[1], p[3])



# Declarações
# Permite zero ou mais declarações sequenciais (const, type, var, ...)
# Se não houver nenhuma declaração, devolve lista vazia.
def p_declarations(p):
    '''declarations : declarations declaration
                    | empty'''
    if p[1] is None:
        p[0] = []
    elif len(p) == 3:
        p[0] = p[1] + [p[2]]



# Uma declaração
# Encapsula qualquer tipo de declaração de topo
def p_declaration(p):
    '''declaration : const_declaration
                    | type_declaration
                    | label_declaration
                    | var_declaration
                    | function_declaration
                    | procedure_declaration'''
    p[0] = p[1]



# Uma declaração com CONST
# Inicia uma secção de constantes
def p_const_declaration(p):
    'const_declaration : CONST const_list'
    p[0] = ('consts', p[2])

# Permite uma lista de declarações individuais de constantes, cada uma terminada por ';'
def p_const_list(p):
    '''const_list : const_list CONST_ITEM SEMI
                  | CONST_ITEM SEMI'''
    if len(p) == 3:
        # Único elemento na lista: inicializa lista com tuplo (nome, expr)
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

# Cada item representa uma constante nomeada com o respetivo valor.
def p_CONST_ITEM(p):
    'CONST_ITEM : ID EQ expression'
    p[0] = (p[1], p[3])



# Uma declaração com TYPE
# Inicia uma secção de definição de tipos
def p_type_declaration(p):
    'type_declaration : TYPE type_list'
    p[0] = ('types', p[2])

# Agrupa múltiplas definições de tipo, cada uma seguida de ';'
# Se for o primeiro, inicializa lista; caso contrário, concatena
def p_type_list(p):
    '''type_list : type_list type_item SEMI
                 | type_item SEMI'''
    if len(p) == 3:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

# Cada item associa um identificador a uma definição de tipo (AST)
def p_type_item(p):
    'type_item : ID EQ type'
    p[0] = (p[1], p[3])



# Label
# Inicia uma secção de declaração de rótulos numéricos
# label_list é lista de inteiros representando rótulos
def p_label_declaration(p):
    'label_declaration : LABEL label_list SEMI'
    p[0] = ('labels', p[2])

# Permite múltiplos rótulos separados por vírgula
# Se for o primeiro, p[1] é INTEGER e len(p)==2. Caso contrário, concatena novo rótulo à lista existente
def p_label_list(p):
    '''label_list : label_list COMMA INTEGER
                  | INTEGER'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]



# Var declarations
# Inicia uma secção de declaração de variáveis
# var_list é lista de tuplos (nomes, tipo_ast)
def p_var_declaration(p):
    'var_declaration : VAR var_list'
    p[0] = ('var_decl', p[2])

# Agrupa múltiplos 'var_item' sem necessidade de ";" entre eles
def p_var_list(p):
    '''var_list : var_list var_item
                | var_item'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

# ID_LIST é uma lista de identificadores separados por vírgula
# Associa múltiplas variáveis ao mesmo tipo
def p_var_item(p):
    'var_item : ID_LIST COLON type SEMI'
    p[0] = ('vars', p[1], p[3])



# Declaração de função
# Define uma função com nome, parâmetros, tipo de retorno e corpo
def p_function_declaration(p):
    'function_declaration : FUNCTION ID LPAREN params RPAREN COLON type SEMI block SEMI'
    p[0] = ('function', p[2], p[4], p[7], p[9])



# Declaração de procedimento
# Define um procedimento (sem retorno) com nome, parâmetros e corpo
def p_procedure_declaration(p):
    'procedure_declaration : PROCEDURE ID LPAREN params RPAREN SEMI block SEMI'
    p[0] = ('procedure', p[2], p[4], p[7])



# Diferentes tipos
# Regra principal que permite reconhecer qualquer tipo de definição de tipo válida.
def p_type(p):
    '''type : packed_type
            | simple_type
            | id_type
            | array_type
            | enum_type
            | subrange_type
            | record_type
            | set_type
            | file_type'''
    p[0] = p[1]

# Reconhece tipos "packed", que forçam a compactação na memória dos dados compostos.
def p_packed_type(p):
    'packed_type : PACKED type'
    p[0] = ('packed', p[2])

# Reconhece os tipos simples
def p_simple_type(p):
    'simple_type : TIPO'
    p[0] = ('simple_type', p[1])

# Reconhece tipos definidos pelo utilizador, referenciados por identificador (ID).
def p_id_type(p):
    'id_type : ID'
    p[0] = ('id_type', p[1])

# Reconhece arrays indexados por intervalos (subranges).
def p_array_type_range(p):
    'array_type : ARRAY LBRACKET range RBRACKET OF type'
    p[0] = ('array_type', p[3], p[6])

# Reconhece tipos enumerados, que consistem numa lista de identificadores entre parêntesis.
# Exemplo: (Red, Green, Blue)
# Cada identificador é tratado como um valor enumerado distinto.
def p_enum_type(p):
    'enum_type : LPAREN ID_LIST RPAREN'
    p[0] = ('enum', p[2])

# Reconhece tipos "subrange", que definem um intervalo de valores permitidos.
# Exemplo: 1..10 ou 'a'..'z'
def p_subrange_type(p):
    'subrange_type : const_expr RANGE const_expr'
    p[0] = ('subrange', p[1], p[3])

# Reconhece tipos "record", que agrupam vários campos de diferentes tipos, semelhantes a structs.
# Opcionalmente, pode conter uma "variant part" para suportar variantes (semelhante a união).
# Exemplo:
# record
#   x: integer;
#   case b: boolean of
#     true: (a: integer);
#     false: (c: real);
# end;
def p_record_type(p):
    '''record_type : RECORD field_list variant_part END
                   | RECORD field_list END'''
    if len(p) == 5:
        p[0] = ('record', p[2], p[3])
    else:
        p[0] = ('record', p[2], None)

# Reconhece o tipo conjunto (set), que representa uma coleção de elementos do mesmo tipo.
# Exemplo: set of 1..10 ou set of char
def p_set_type(p):
    'set_type : SET OF type'
    p[0] = ('set', p[3])

# Reconhece o tipo ficheiro (file), que representa ficheiros com elementos de determinado tipo.
# Exemplo: file of integer
def p_file_type(p):
    'file_type : FILE OF type'
    p[0] = ('file', p[3])



# cada range é um par de CONSTANT .. CONSTANT
# Reconhece um intervalo de constantes (range), utilizado por exemplo em arrays e subranges.
# Um range é constituído por dois valores constantes separados por dois pontos (..)
# Exemplo: 1 .. 10 ou 'a' .. 'z'
def p_range(p):
    'range : const_expr RANGE const_expr'
    p[0] = (p[1], p[3])

# Reconhece uma expressão constante, ou seja, um valor literal que pode ser usado em definições de tipos ou constantes.
# Pode ser um número inteiro, real, valor booleano, caractere, texto, ou identificador (referência a constante).
def p_const_expr(p):
    '''const_expr : INTEGER
                  | REAL
                  | BOOLEAN
                  | CHAR
                  | TEXTO
                  | ID'''
    p[0] = ('const_expr', p.slice[1].type.lower(), p[1])



# Reconhece uma lista de campos de um record (estrutura de dados).
# Cada campo é descrito por uma declaração de variável (`var_item`), e pode haver múltiplos campos.
def p_field_list(p):
    '''field_list : field_list var_item
                  | var_item'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]



# Define uma "variant part" de um registo (record).
# Esta estrutura é usada para representar variantes dentro de um registo, ou seja, campos opcionais cujo conteúdo depende de um identificador (discriminador).
# Exemplo em Pascal: case Tag: Integer of ...
def p_variant_part(p):
    'variant_part : CASE ID COLON TIPO OF variant_list'
    p[0] = ('variant', p[2], p[4], p[6])

# Reconhece uma lista de variantes (branches do CASE em records variant).
# Cada item é separado por ponto e vírgula. Permite uma ou mais variantes.
def p_variant_list(p):
    '''variant_list : variant_list variant_item SEMI
                    | variant_item SEMI'''
    if len(p)==3: 
        p[0] = [p[1]]
    else: 
        p[0] = p[1] + [p[2]]

# Representa uma única alternativa do CASE num registo variante.
# Cada alternativa é associada a uma constante e um conjunto de campos (field_list).
# Exemplo: 1: (campo1: Integer; campo2: Real)
def p_variant_item(p):
    'variant_item : constant COLON LPAREN field_list RPAREN'
    p[0] = (p[1], p[4])



# Lista de identificadores separados por vírgulas.
def p_ID_LIST(p):
    '''ID_LIST : ID
               | ID_LIST COMMA ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]



# Parâmetros formais de funções ou procedimentos.
# Se não houver parâmetros, devolve uma lista vazia (empty).
def p_params(p):
    '''params : param_list
              | empty'''
    p[0] = p[1]

# Lista de declarações de parâmetros, separados por ponto e vírgula.
# Cada parâmetro é tratado como um `param`.
def p_param_list(p):
    '''param_list : param_list SEMI param
                  | param'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

# Um parâmetro pode ser:
# - por valor (ex: `a: Integer`)
# - por referência (ex: `var a: Integer`)
# - como constante (ex: `const a: Integer`)
# O tipo de parâmetro é indicado pela primeira palavra.
def p_param(p):
    '''param : ID_LIST COLON type
             | VAR ID_LIST COLON type
             | CONST ID_LIST COLON type'''
    if len(p) == 4:
        p[0] = ('param_val', p[1], p[3])
    elif p[1].lower() == 'var':
        p[0] = ('param_var', p[2], p[4])
    else:
        p[0] = ('param_const', p[2], p[4])



# Lista de instruções (statements) separadas por ponto e vírgula.
# Pode ser uma única instrução ou uma sequência de várias.
def p_statement_list(p):
    '''statement_list : statement_list SEMI statement
                      | statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        stmts = p[1]
        last = p[3]
        if last is not None:
            stmts = stmts + [last]
        p[0] = stmts



# Bloco composto BEGIN ... END com várias instruções dentro.
# É tratado como um único statement do tipo 'compound'.
def p_compound(p):
    'compound : BEGIN statement_list END'
    p[0] = ('compound', p[2])



# Statement genérico — engloba todos os tipos possíveis de instruções válidas.
# Pode ser uma instrução concreta (if, while, etc.) ou uma instrução vazia (empty).
def p_statement(p):
    '''statement : assignment
                 | procedure_call
                 | if_statement
                 | for_statement
                 | while_statement
                 | repeat_statement
                 | case_statement
                 | with_statement
                 | goto_statement
                 | labeled_statement
                 | compound
                 | empty'''
    p[0] = p[1]



# Instrução de atribuição: variável := expressão
# Exemplo: x := 10
def p_assignment(p):
    'assignment : variable ASSIGN expression'
    p[0] = ('assign', p[1], p[3])



# Variáveis em Pascal podem ser:
# - Simples (ex: x)
# - Indexadas (ex: a[1])
# - Campos de registo (ex: pessoa.nome)
def p_variable(p):
    '''variable : variable LBRACKET expression RBRACKET
                | variable DOT ID
                | ID'''
    if len(p) == 2:
        p[0] = ('var', p[1])
    elif p[2] == '[':
        p[0] = ('array', p[1], p[3])
    else:
        p[0] = ('field', p[1], p[3])



# Chamada de procedimento ou função sem retorno de valor (ex: writeln(x))
# Pode ser com ou sem parêntesis e argumentos.
def p_procedure_call(p):
    '''procedure_call : ID LPAREN expression_list RPAREN
                      | ID'''  
    if len(p) == 2:
        p[0] = ('call', p[1], [])
    else:
        p[0] = ('call', p[1], p[3])



# Instrução condicional IF ... THEN ... [ELSE ...]
# Pode ter só o ramo THEN, ou ambos THEN e ELSE.
def p_if_statement(p):
    '''if_statement : IF expression THEN statement ELSE statement
                    | IF expression THEN statement %prec IFX'''   
    if len(p) == 5:
        p[0] = ('if', p[2], p[4], None)
    else:
        p[0] = ('if', p[2], p[4], p[6])



# Ciclo FOR com direção TO ou DOWNTO
# Exemplo: for i := 1 to 10 do writeln(i);
def p_for_statement(p):
    '''for_statement : FOR ID ASSIGN expression TO expression DO statement
                     | FOR ID ASSIGN expression DOWNTO expression DO statement'''
    direction = 'to' if p[5].lower() == 'to' else 'downto'
    p[0] = ('for', p[2], p[4], p[6], direction, p[8])



# Ciclo WHILE com condição no início
# Exemplo: while x < 10 do x := x + 1;
def p_while_statement(p):
    'while_statement : WHILE expression DO statement'
    p[0] = ('while', p[2], p[4])



# Ciclo REPEAT com condição no fim
# Exemplo: repeat writeln(x); x := x + 1; until x > 10;
def p_repeat_statement(p):
    'repeat_statement : REPEAT statement_list UNTIL expression'
    p[0] = ('repeat', p[2], p[4])



# Instrução CASE (ex: case x of 1: writeln('um'); 2: writeln('dois'); end;)
# Permite selecionar entre vários ramos com base numa expressão.
def p_case_statement(p):
    'case_statement : CASE expression OF case_list END'
    p[0] = ('case', p[2], p[4])

# Lista de ramos do CASE, cada um separado por ';'
def p_case_list(p):
    '''case_list : case_list case_item SEMI
                 | case_item SEMI'''
    if len(p)==3: 
        p[0]=[p[1]]
    else: 
        p[0]=p[1]+[p[2]]

# Cada item do CASE é uma lista de constantes seguida de ':' e de uma lista de statements
def p_case_item(p):
    'case_item : constant_list COLON statement_list'
    p[0] = (p[1], p[3])

# Lista de constantes usadas como rótulos num item do CASE
def p_constant_list(p):
    '''constant_list : const_expr
                     | constant_list COMMA const_expr'''
    if len(p)==2: 
        p[0]=[p[1]]
    else: 
        p[0]=p[1]+[p[3]]



# Instrução WITH (ex: with pessoa do writeln(nome);)
def p_with_statement(p):
    'with_statement : WITH variable_list DO statement'
    p[0] = ('with', p[2], p[4])

# Lista de variáveis usada no WITH
def p_variable_list(p):
    '''variable_list : variable
                     | variable_list COMMA variable'''
    if len(p)==2: 
        p[0]=[p[1]]
    else: 
        p[0]=p[1]+[p[3]]



# Instrução GOTO — transfere o controlo do programa para um label indicado
# Ex: goto 100;
def p_goto_statement(p):
    'goto_statement : GOTO INTEGER'
    p[0] = ('goto', p[2])



# Instrução com label — associa um número a um statement
# Ex: 100: writeln('ola');
def p_labeled_statement(p):
    'labeled_statement : INTEGER COLON statement'
    p[0] = ('label_stmt', p[1], p[3])



# Constantes literais — podem ser inteiros, reais, booleanos, caracteres ou texto
def p_constant(p):
    '''constant : INTEGER
                | REAL
                | BOOLEAN
                | CHAR
                | TEXTO'''
    p[0] = ('const', p.slice[1].type.lower(), p[1])



# Expressões — incluem variáveis, constantes, chamadas, operadores binários e unários, conjuntos, etc.
def p_expression(p):
    '''expression : variable
                  | constant
                  | TIPO LPAREN expression_list RPAREN
                  | ID LPAREN expression_list RPAREN
                  | LPAREN expression RPAREN
                  | LBRACKET expression_list RBRACKET
                  | NOT expression
                  | expression COLON expression
                  | expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression DIV expression
                  | expression MOD expression
                  | expression EQ expression
                  | expression NE expression
                  | expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression
                  | expression IN expression
                  | expression AND expression
                  | expression OR expression'''
    if len(p) == 4 and p[2] == ':':
        left, right = p[1], p[3]
        if isinstance(left, tuple) and left[0] == 'fmt' and left[3] is None:
            p[0] = ('fmt', left[1], left[2], right)
        else:
            p[0] = ('fmt', left, right, None)
        return
    if p.slice[1].type == 'NOT':
        p[0] = ('not', p[2])
    elif len(p) == 2:
        p[0] = p[1]
    elif p[1] == '(':
        p[0] = p[2]
    elif p[2] == '(':
        p[0] = ('call', p[1], p[3])
    elif p[1] == '[':
        p[0] = ('set_lit', p[2])
    else:
        p[0] = ('binop', p[2], p[1], p[3])



# Lista de expressões — usada em chamadas de função, construtores, etc.
def p_expression_list(p):
    '''expression_list : expression
                       | expression_list COMMA expression'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]



# Regra para produções vazias
def p_empty(p):
    'empty :'
    p[0] = None



# Error rule
def p_error(p):
    if p:
        print(f"Erro sintático: token inesperado '{p.value}' na linha {p.lineno}")
    else:
        print("Erro sintático: fim de ficheiro inesperado")



# Construir parser
parser = yacc.yacc()

# Função de interface
def parse(data):
    """
    Analisa sintaticamente o código Pascal em 'data'.
    Retorna a estrutura de programa ou None se erro.
    """
    lexer = build_lexer()
    return parser.parse(data, lexer=lexer)