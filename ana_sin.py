from ana_lex import tokens, build_lexer
import ply.yacc as yacc

# Construir o lexer
lexer = build_lexer()

# Precedences
precedence = (
    ('nonassoc', 'IFX'),          
    ('nonassoc', 'ELSE'),          
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('left', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE', 'IN'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'DIV', 'MOD'),
    ('left', 'COLON'),
)

# Programa
def p_program(p):
    'program : PROGRAM ID SEMI block DOT'
    p[0] = ('program', p[2], p[4])



# Bloco principal
def p_block(p):
    'block : declarations BEGIN statement_list END'
    p[0] = ('block', p[1], p[3])



# Declarações
def p_declarations(p):
    '''declarations : declarations declaration
                    | empty'''
    if p[1] is None:
        p[0] = []
    elif len(p) == 3:
        p[0] = p[1] + [p[2]]



# Uma declaração
def p_declaration(p):
    '''declaration : const_declaration
                    | type_declaration
                    | label_declaration
                    | var_declaration
                    | function_declaration
                    | procedure_declaration'''
    p[0] = p[1]



# Uma declaração com CONST
def p_const_declaration(p):
    'const_declaration : CONST const_list'
    p[0] = ('consts', p[2])

def p_const_list(p):
    '''const_list : const_list CONST_ITEM SEMI
                  | CONST_ITEM SEMI'''
    if len(p) == 3:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_CONST_ITEM(p):
    'CONST_ITEM : ID EQ expression'
    p[0] = (p[1], p[3])



# Uma declaração com TYPE
def p_type_declaration(p):
    'type_declaration : TYPE type_list'
    p[0] = ('types', p[2])

def p_type_list(p):
    '''type_list : type_list type_item SEMI
                 | type_item SEMI'''
    if len(p) == 3:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_type_item(p):
    'type_item : ID EQ type'
    p[0] = (p[1], p[3])



# Label
def p_label_declaration(p):
    'label_declaration : LABEL label_list SEMI'
    p[0] = ('labels', p[2])

def p_label_list(p):
    '''label_list : label_list COMMA INTEGER
                  | INTEGER'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]



# Var declarations
def p_var_declaration(p):
    'var_declaration : VAR var_list'
    p[0] = ('var_decl', p[2])

def p_var_list(p):
    '''var_list : var_list var_item
                | var_item'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_var_item(p):
    'var_item : ID_LIST COLON type SEMI'
    p[0] = ('vars', p[1], p[3])



# Declaração de função
def p_function_declaration(p):
    'function_declaration : FUNCTION ID LPAREN params RPAREN COLON type SEMI block SEMI'
    p[0] = ('function', p[2], p[4], p[7], p[9])



# Declaração de procedimento
def p_procedure_declaration(p):
    'procedure_declaration : PROCEDURE ID LPAREN params RPAREN SEMI block SEMI'
    p[0] = ('procedure', p[2], p[4], p[7])



# Diferentes tipos
def p_type(p):
    '''type : packed_type
            | short_string
            | simple_type
            | id_type
            | array_type
            | enum_type
            | subrange_type
            | record_type
            | set_type
            | file_type'''
    p[0] = p[1]

def p_packed_type(p):
    'packed_type : PACKED type'
    p[0] = ('packed', p[2])

def p_short_string(p):
    'short_string : TIPO LBRACKET constant RBRACKET'
    p[0] = ('short_string', p[1], p[3])

def p_simple_type(p):
    'simple_type : TIPO'
    p[0] = ('simple_type', p[1])

def p_id_type(p):
    'id_type : ID'
    p[0] = ('id_type', p[1])

def p_array_type_open(p):
    'array_type : ARRAY OF type'
    p[0] = ('open_array', p[3])

def p_array_type_range(p):
    'array_type : ARRAY LBRACKET range_list RBRACKET OF type'
    p[0] = ('array_type', p[3], p[6])

def p_enum_type(p):
    'enum_type : LPAREN ID_LIST RPAREN'
    p[0] = ('enum', p[2])

def p_subrange_type(p):
    'subrange_type : constant RANGE constant'
    p[0] = ('subrange', p[1], p[3])

def p_record_type(p):
    '''record_type : RECORD field_list variant_part END
                   | RECORD field_list END'''
    if len(p) == 5:
        p[0] = ('record', p[2], p[3])
    else:
        p[0] = ('record', p[2], None)

def p_set_type(p):
    'set_type : SET OF type'
    p[0] = ('set', p[3])

def p_file_type(p):
    'file_type : FILE OF type'
    p[0] = ('file', p[3])



# ----------------------------------------------------------------------------------
def p_range_list(p):
    '''range_list : range_list COMMA range
                  | range'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

# cada range é um par de CONSTANT .. CONSTANT
def p_range(p):
    'range : const_expr RANGE const_expr'
    p[0] = (p[1], p[3])

def p_const_expr(p):
    '''const_expr : INTEGER
                  | REAL
                  | BOOLEAN
                  | CHAR
                  | TEXTO
                  | ID
                  | NIL'''
    p[0] = ('const_expr', p.slice[1].type.lower(), p[1])



# -----------------------------------------------------------------------------
def p_field_list(p):
    '''field_list : field_list var_item
                  | var_item'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]



# ------------------------------------------------------------------------------
def p_variant_part(p):
    'variant_part : CASE ID COLON TIPO OF variant_list'
    p[0] = ('variant', p[2], p[4], p[6])

def p_variant_list(p):
    '''variant_list : variant_list variant_item SEMI
                    | variant_item SEMI'''
    if len(p)==3: 
        p[0] = [p[1]]
    else: 
        p[0] = p[1] + [p[2]]

def p_variant_item(p):
    'variant_item : constant COLON LPAREN field_list RPAREN'
    p[0] = (p[1], p[4])



# ---------------------------------------------------------------------------------
def p_ID_LIST(p):
    '''ID_LIST : ID
               | ID_LIST COMMA ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]



# Parâmetros
def p_params(p):
    '''params : param_list
              | empty'''
    p[0] = p[1]

def p_param_list(p):
    '''param_list : param_list SEMI param
                  | param'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

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



# Lista de statements com ;
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



# ---------------------------------------------------------------
def p_compound(p):
    'compound : BEGIN statement_list END'
    p[0] = ('compound', p[2])



# Statement
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



# Atribuição
def p_assignment(p):
    'assignment : variable ASSIGN expression'
    p[0] = ('assign', p[1], p[3])



# Variáveis
def p_variable(p):
    '''variable : variable LBRACKET expression_list RBRACKET
                | variable DOT ID
                | ID'''
    if len(p) == 2:
        p[0] = ('var', p[1])
    elif p[2] == '[':
        p[0] = ('array', p[1], p[3])
    else:
        p[0] = ('field', p[1], p[3])



# Chamada de procedimento/função sem retorno
def p_procedure_call(p):
    '''procedure_call : ID LPAREN expression_list RPAREN
                      | ID'''  
    if len(p) == 2:
        p[0] = ('call', p[1], [])
    else:
        p[0] = ('call', p[1], p[3])



# If
def p_if_statement(p):
    '''if_statement : IF expression THEN statement ELSE statement
                    | IF expression THEN statement %prec IFX'''   
    if len(p) == 5:
        p[0] = ('if', p[2], p[4], None)
    else:
        p[0] = ('if', p[2], p[4], p[6])



# For, incluindo TO e DOWNTO
def p_for_statement(p):
    '''for_statement : FOR ID ASSIGN expression TO expression DO statement
                     | FOR ID ASSIGN expression DOWNTO expression DO statement'''
    direction = 'to' if p[5].lower() == 'to' else 'downto'
    p[0] = ('for', p[2], p[4], p[6], direction, p[8])



# -------------------------------------------------------------------------------
def p_while_statement(p):
    'while_statement : WHILE expression DO statement'
    p[0] = ('while', p[2], p[4])



# -------------------------------------------------------------------------------
def p_repeat_statement(p):
    'repeat_statement : REPEAT statement_list UNTIL expression'
    p[0] = ('repeat', p[2], p[4])



# -------------------------------------------------------------------------------
def p_case_statement(p):
    'case_statement : CASE expression OF case_list END'
    p[0] = ('case', p[2], p[4])

def p_case_list(p):
    '''case_list : case_list case_item SEMI
                 | case_item SEMI'''
    if len(p)==3: 
        p[0]=[p[1]]
    else: 
        p[0]=p[1]+[p[2]]

def p_case_item(p):
    'case_item : constant_list COLON statement_list'
    p[0] = (p[1], p[3])

def p_constant_list(p):
    '''constant_list : constant
                     | constant_list COMMA constant'''
    if len(p)==2: 
        p[0]=[p[1]]
    else: 
        p[0]=p[1]+[p[3]]



# -------------------------------------------------------------------------------
def p_with_statement(p):
    'with_statement : WITH variable_list DO statement'
    p[0] = ('with', p[2], p[4])

def p_variable_list(p):
    '''variable_list : variable
                     | variable_list COMMA variable'''
    if len(p)==2: 
        p[0]=[p[1]]
    else: 
        p[0]=p[1]+[p[3]]



# -------------------------------------------------------------------------------
def p_goto_statement(p):
    'goto_statement : GOTO INTEGER'
    p[0] = ('goto', p[2])



# ------------------------------------------------------------------------------
def p_labeled_statement(p):
    'labeled_statement : INTEGER COLON statement'
    p[0] = ('label_stmt', p[1], p[3])



# Constantes
def p_constant(p):
    '''constant : INTEGER
                | REAL
                | BOOLEAN
                | CHAR
                | TEXTO
                | NIL'''
    p[0] = ('const', p.slice[1].type.lower(), p[1])



# Expressões
def p_expression(p):
    '''expression : variable
                  | constant
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



# Lista de expressões
def p_expression_list(p):
    '''expression_list : expression
                       | expression_list COMMA expression'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]



# Empty rule
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
parser = yacc.yacc(debug=True, write_tables=True)

# Função de interface
def parse(data):
    """
    Analisa sintaticamente o código Pascal em 'data'.
    Retorna a estrutura de programa ou None se erro.
    """
    lexer = build_lexer()
    return parser.parse(data, lexer=lexer)