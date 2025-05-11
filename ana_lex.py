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
    r'(\binteger\b|\breal\b|\bboolean\b|\bchar\b)'
    return t

def t_BOOLEAN(t):
    r'(\btrue\b|\bfalse\b)'
    return t

def t_AND(t):      
    r'\band\b'       
    return t

def t_ARRAY(t):    
    r'\barray\b'     
    return t

def t_BEGIN(t):    
    r'\bbegin\b'    
    return t

def t_CASE(t):     
    r'\bcase\b'     
    return t

def t_CONST(t):    
    r'\bconst\b'    
    return t

def t_DIV(t):      
    r'\bdiv\b'      
    return t

def t_DOWNTO(t):   
    r'\bdownto\b'   
    return t

def t_DO(t):       
    r'\bdo\b'       
    return t

def t_ELSE(t):     
    r'\belse\b'     
    return t

def t_END(t):      
    r'\bend\b'      
    return t

def t_FILE(t):     
    r'\bfile\b'     
    return t

def t_FOR(t):      
    r'\bfor\b'      
    return t

def t_FUNCTION(t): 
    r'\bfunction\b' 
    return t

def t_GOTO(t):     
    r'\bgoto\b'     
    return t

def t_IF(t):       
    r'\bif\b'       
    return t

def t_IN(t):       
    r'\bin\b'       
    return t

def t_LABEL(t):    
    r'\blabel\b'    
    return t

def t_MOD(t):      
    r'\bmod\b'      
    return t

def t_NOT(t):      
    r'\bnot\b'      
    return t

def t_OF(t):       
    r'\bof\b'       
    return t

def t_OR(t):       
    r'\bor\b'       
    return t

def t_PACKED(t):   
    r'\bpacked\b'   
    return t

def t_PROCEDURE(t):
    r'\bprocedure\b'
    return t

def t_PROGRAM(t):  
    r'\bprogram\b'  
    return t

def t_RECORD(t):   
    r'\brecord\b'
    return t

def t_REPEAT(t):   
    r'\brepeat\b'   
    return t

def t_SET(t):      
    r'\bset\b'      
    return t

def t_THEN(t):     
    r'\bthen\b'     
    return t

def t_TO(t):       
    r'\bto\b'       
    return t

def t_TYPE(t):     
    r'\btype\b'     
    return t

def t_UNTIL(t):    
    r'\buntil\b'    
    return t

def t_VAR(t):      
    r'\bvar\b'      
    return t

def t_WHILE(t):    
    r'\bwhile\b'    
    return t

def t_WITH(t):     
    r'\bwith\b'     
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
        # Captado por engano, ignora este token
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
    return lex.lex(module=sys.modules[__name__], reflags=re.IGNORECASE, **kwargs)