import re, sys
import ply.lex as lex

# Lista completa de tokens
tokens = (
    'TIPO',
    'BOOLEAN',

    # Palavras‑reservadas
    'AND',
    'ARRAY',
    'BEGIN',
    'CASE',
    'CONST',
    'DIV',
    'DOWNTO',
    'DO',
    'ELSE',
    'END',
    'FILE',
    'FOR',
    'FUNCTION',
    'GOTO',
    'IF',
    'IN',
    'LABEL',
    'MOD',
    'NIL',
    'NOT',
    'OF',
    'OR',
    'PACKED',
    'PROCEDURE',
    'PROGRAM',
    'RECORD',
    'REPEAT',
    'SET',
    'THEN',
    'TO',
    'TYPE',
    'UNTIL',
    'VAR',
    'WHILE',
    'WITH',

    # Literais e identificadores
    'ID',
    'REAL',
    'INTEGER',
    'STRING',

    # Operadores
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'ASSIGN',
    'EQ',
    'NE',
    'LE',
    'LT',
    'GE',
    'GT',

    # Pontuação
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'SEMI',
    'COMMA',
    'RANGE',
    'DOT',
    'COLON'
)

# Regras para cada palavra-reservada (funções individuais)
# Pascal Standard é case-insensitive, usamos re.IGNORECASE ao construir o lexer

def t_TIPO(t):
    r'(integer|smallint|longint|real|boolean|string|char|byte)'
    return t

def t_BOOLEAN(t):
    r'(true|false)'
    return t

def t_AND(t):      
    r'and'       
    return t

def t_ARRAY(t):    
    r'array'     
    return t

def t_BEGIN(t):    
    r'begin'    
    return t

def t_CASE(t):     
    r'case'     
    return t

def t_CONST(t):    
    r'const'    
    return t

def t_DIV(t):      
    r'div'      
    return t

def t_DOWNTO(t):   
    r'downto'   
    return t

def t_DO(t):       
    r'do'       
    return t

def t_ELSE(t):     
    r'else'     
    return t

def t_END(t):      
    r'end'      
    return t

def t_FILE(t):     
    r'file'     
    return t

def t_FOR(t):      
    r'for'      
    return t

def t_FUNCTION(t): 
    r'function' 
    return t

def t_GOTO(t):     
    r'goto'     
    return t

def t_IF(t):       
    r'if'       
    return t

def t_IN(t):       
    r'in'       
    return t

def t_LABEL(t):    
    r'label'    
    return t

def t_MOD(t):      
    r'mod'      
    return t

def t_NIL(t):      
    r'nil'      
    return t

def t_NOT(t):      
    r'not'      
    return t

def t_OF(t):       
    r'of'       
    return t

def t_OR(t):       
    r'or'       
    return t

def t_PACKED(t):   
    r'packed'   
    return t

def t_PROCEDURE(t):
    r'procedure'
    return t

def t_PROGRAM(t):  
    r'program'  
    return t

def t_RECORD(t):   
    r'record'
    return t

def t_REPEAT(t):   
    r'repeat'   
    return t

def t_SET(t):      
    r'set'      
    return t

def t_THEN(t):     
    r'then'     
    return t

def t_TO(t):       
    r'to'       
    return t

def t_TYPE(t):     
    r'type'     
    return t

def t_UNTIL(t):    
    r'until'    
    return t

def t_VAR(t):      
    r'var'      
    return t

def t_WHILE(t):    
    r'while'    
    return t

def t_WITH(t):     
    r'with'     
    return t

# Operadores e símbolos simples
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_ASSIGN  = r':='
t_EQ      = r'='
t_NE      = r'<>|!='
t_LE      = r'<='
t_LT      = r'<'
t_GE      = r'>='
t_GT      = r'>'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACKET= r'\['
t_RBRACKET= r'\]'
t_SEMI    = r';'
t_COMMA   = r','
t_RANGE   = r'\.\.'  # Intervalo: '..'
t_DOT     = r'\.'
t_COLON   = r':'

# Strings (passa duplo apóstrofo para um único: "it''s" -> "it's")
def t_STRING(t):
    r"'([^']|'')*'"
    t.value = t.value[1:-1].replace("''", "'")
    return t

# Constantes reais
def t_REAL(t):
    r'\d+\.\d+([eE][+-]?\d+)?'
    t.value = float(t.value)
    return t

# Constantes inteiras
def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Identificadores
def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    return t

# Comentários: { ... } ou (* ... *)
def t_COMMENT(t):
    r'\{[^}]*\}|\(\*([^*]|\*+[^*)])*\*+\)'
    pass

# Ignorar espaços e tabs
t_ignore = ' \t\r'

# Contagem de linhas
def t_newline(t):
   r'\n+'
   t.lexer.lineno += len(t.value)

# Erro léxico
def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

def build_lexer(**kwargs):
    return lex.lex(module=sys.modules[__name__], reflags=re.IGNORECASE, **kwargs)