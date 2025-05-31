import sys
import ply.lex as lex

# Lista completa de tokens
tokens = (
    # Tipos básicos e literais
    'TIPO',
    'BOOLEAN',

    # Palavras-reservadas da linguagem Pascal
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
    'CHAR',
    'TEXTO',

    # Operadores aritméticos e relacionais
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

    # Símbolos de pontuação e delimitadores
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
# Pascal Standard é case-insensitive - funções construídas de modo a refletir isso

def t_TIPO(t):
    r'\b([iI][nN][tT][eE][gG][eE][rR]|\b[rR][eE][aA][lL]|\b[bB][oO][oO][lL][eE][aA][nN]|\b[cC][hH][aA][rR])\b'
    return t

def t_BOOLEAN(t):
    r'\b([tT][rR][uU][eE]|\b[fF][aA][lL][sS][eE])\b'
    return t

def t_AND(t):      
    r'\b([aA][nN][dD])\b'       
    return t

def t_ARRAY(t):    
    r'\b([aA][rR][rR][aA][yY])\b'     
    return t

def t_BEGIN(t):    
    r'\b([bB][eE][gG][iI][nN])\b'    
    return t

def t_CASE(t):     
    r'\b([cC][aA][sS][eE])\b'     
    return t

def t_CONST(t):    
    r'\b([cC][oO][nN][sS][tT])\b'    
    return t

def t_DIV(t):      
    r'\b([dD][iI][vV])\b'      
    return t

def t_DOWNTO(t):   
    r'\b([dD][oO][wW][nN][tT][oO])\b'   
    return t

def t_DO(t):       
    r'\b([dD][oO])\b'       
    return t

def t_ELSE(t):     
    r'\b([eE][lL][sS][eE])\b'     
    return t

def t_END(t):      
    r'\b([eE][nN][dD])\b'      
    return t

def t_FILE(t):     
    r'\b([fF][iI][lL][eE])\b'     
    return t

def t_FOR(t):      
    r'\b([fF][oO][rR])\b'      
    return t

def t_FUNCTION(t): 
    r'\b([fF][uU][nN][cC][tT][iI][oO][nN])\b' 
    return t

def t_GOTO(t):     
    r'\b([gG][oO][tT][oO])\b'     
    return t

def t_IF(t):       
    r'\b([iI][fF])\b'       
    return t

def t_IN(t):       
    r'\b([iI][nN])\b'       
    return t

def t_LABEL(t):    
    r'\b([lL][aA][bB][eE][lL])\b'    
    return t

def t_MOD(t):      
    r'\b([mM][oO][dD])\b'      
    return t

def t_NOT(t):      
    r'\b([nN][oO][tT])\b'      
    return t

def t_OF(t):       
    r'\b([oO][fF])\b'       
    return t

def t_OR(t):       
    r'\b([oO][rR])\b'       
    return t

def t_PACKED(t):   
    r'\b([pP][aA][cC][kK][eE][dD])\b'   
    return t

def t_PROCEDURE(t):
    r'\b([pP][rR][oO][cC][eE][dD][uU][rR][eE])\b'
    return t

def t_PROGRAM(t):  
    r'\b([pP][rR][oO][gG][rR][aA][mM])\b'  
    return t

def t_RECORD(t):   
    r'\b([rR][eE][cC][oO][rR][dD])\b'
    return t

def t_REPEAT(t):   
    r'\b([rR][eE][pP][eE][aA][tT])\b'   
    return t

def t_SET(t):      
    r'\b([sS][eE][tT])\b'      
    return t

def t_THEN(t):     
    r'\b([tT][hH][eE][nN])\b'     
    return t

def t_TO(t):       
    r'\b([tT][oO])\b'       
    return t

def t_TYPE(t):     
    r'\b([tT][yY][pP][eE])\b'     
    return t

def t_UNTIL(t):    
    r'\b([uU][nN][tT][iI][lL])\b'    
    return t

def t_VAR(t):      
    r'\b([vV][aA][rR])\b'      
    return t

def t_WHILE(t):    
    r'\b([wW][hH][iI][lL][eE])\b'    
    return t

def t_WITH(t):     
    r'\b([wW][iI][tT][hH])\b'     
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

def t_CHAR(t):
    r"\'([^']|\'\')\'"
    valor = t.value[1:-1].replace("''", "'")
    if len(valor) != 1:
        print(f"Erro: literal de carácter inválido '{t.value}' na linha {t.lineno}")
        t.lexer.skip(1)
        return
    t.value = valor
    return t

# Strings (vários caracteres): 'ABC', 'it''s'
def t_TEXTO(t):
    r"\'([^']|'')+\'"
    valor = t.value[1:-1].replace("''", "'")
    if len(valor) == 1:
        # Captado por engano, ignorar este token
        return
    t.value = valor
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
    return lex.lex(module=sys.modules[__name__], **kwargs)