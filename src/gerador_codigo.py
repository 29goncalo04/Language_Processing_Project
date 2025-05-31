# Extrai o valor de nós do tipo 'const', tipo ou valor, ou de constantes nomeadas
def extrair_valor_constante(ast, consts):
    # Se o nó for um inteiro, devolve-o diretamente
    if isinstance(ast, int):
        return ast
    # Se for um float, devolve-o diretamente
    elif isinstance(ast, float):
        return ast
    # Se for um tuplo, trata-o conforme o tipo de nó (const_expr, var, binop, etc.)
    elif isinstance(ast, tuple):
        tag = ast[0]
        # Caso seja uma expressão constante ('const_expr', tipo, valor)
        if tag == 'const_expr':
            tipo = ast[1]
            valor = ast[2]
            # Converte o valor para o tipo correspondente
            if tipo == 'integer':
                return int(valor)
            elif tipo == 'real':
                return float(valor)
            elif tipo == 'boolean':
                return valor.lower() == 'true'
            elif tipo == 'char':
                return valor  # Assume que já é um char simples
            else:
                # Se o tipo não for suportado, lança uma exceção
                raise Exception(f"Tipo constante não suportado: {tipo}")
        # Caso seja uma constante nomeada ('var', nome)
        elif tag == 'var':
            nome = ast[1]
            if nome not in consts:
                # Se a constante não estiver definida, lança uma exceção
                raise Exception(f"Constante não definida: {nome}")
            # Chama recursivamente para extrair o valor da constante referenciada
            return extrair_valor_constante(consts[nome], consts)
        # Caso de operação binária de constantes: ('binop', op, left, right)
        elif tag == 'binop':
            _, op, left, right = ast
            # Extrai recursivamente os valores das subexpressões
            lval = extrair_valor_constante(left, consts)
            rval = extrair_valor_constante(right, consts)
            # Se o operador for aritmético, executa-o em lval e rval
            if op in ('+', '-', '*', '/', 'div', 'mod'):
                if op == '+': return lval + rval
                if op == '-': return lval - rval
                if op == '*': return lval * rval
                if op == '/': return lval / rval
                if op == 'div': return lval // rval
                if op == 'mod': return lval % rval
            else:
                # Operador binário constante não suportado
                raise Exception(f"Operador constante não suportado: {op}")
        else:
            # Nó inesperado
            raise Exception(f"Nó constante inesperado: {ast}")
    else:
        # Tipo de nó fora do esperado (nem inteiro, nem float, nem tuplo)
        raise Exception(f"Tipo de nó inesperado: {ast}")



class CodeGenerator:
    def __init__(self):
        # Tabela de símbolos: associa nome a informações de cada identificador
        self.symtab = {}
        # Constantes nomeadas extraídas da AST
        self.consts = {}
        # Sub-rotinas (functions/procedures): nome -> (etiqueta, número_de_parâmetros)
        self.subroutines = {}
        # Aliases de tipos
        self.types = {}
        # Lista de instruções de código máquina geradas
        self.code = []
        # Próximo offset livre do gp (variáveis globais)
        self.offset = 0
        # Contador para criar labels únicas (L0, L1, etc.)
        self.label_counter = 0


    # Insere uma instrução na lista de código gerado
    def emit(self, instr):
        self.code.append(instr)


    # Grava as instruções num ficheiro, uma por linha
    def write(self, filename):
        with open(filename, 'w') as f:
            for instr in self.code:
                f.write(instr + '\n')


    # Emite a instrução de verificação de índice de array: CHECK 0,size-1
    def emit_check(self, size):
        self.emit(f"CHECK 0,{size-1}")


    # Constrói a tabela de símbolos a partir do nó raiz da AST
    def build_symtab(self, ast):
        _, _, block = ast  # node = ('program', nome, block)
        decls, _ = block[1], block[2]  # decls contém todas as declarações (types, consts, var_decl, etc.)

        # Processar declarações de tipos (aliases): armazena em self.types
        for d in decls:
            if d and d[0] == 'types':
                for name, tp in d[1]:
                    self.types[name.lower()] = tp

        # Processar declarações de constantes: armazena em self.consts e em symtab como ('const', expr)
        for d in decls:
            if d and d[0] == 'consts':
                for name, expr in d[1]:
                    self.consts[name] = expr
                    self.symtab[name] = ('const', expr)

        # Processar declarações de sub-rotinas (functions e procedures): para cada uma, é registado o rótulo (upper case) e número de parâmetros
        for d in decls:
            if d and d[0] in ('function', 'procedure'):
                name = d[1].lower()
                params = d[2] or []
                nargs = len(params)
                label = name.upper()
                self.subroutines[name] = (label, nargs)

        # Processar declarações de variáveis globais e arrays
        for d in decls:
            if d and d[0] == 'var_decl':
                for _, id_list, raw_tp in d[1]:
                    # raw_tp pode ser um tipo básico ou um id_type para um alias
                    tp = raw_tp
                    # Se for um alias de tipo, é usado para o tipo concreto
                    if isinstance(tp, tuple) and tp[0] == 'id_type':
                        alias = tp[1].lower()
                        if alias in self.types:
                            tp = self.types[alias]

                    for name in id_list:
                        # Se o tipo for array, é usado ALLOCN para alocar espaço na heap
                        if isinstance(tp, tuple) and tp[0] == 'array_type':
                            low_ast, high_ast = tp[1]  # limites inferior e superior
                            low  = extrair_valor_constante(low_ast, self.consts)
                            high = extrair_valor_constante(high_ast, self.consts)
                            size = high - low + 1
                            self.emit(f"PUSHI {size}")  # faz PUSH do tamanho
                            self.emit("ALLOCN")  # faz ALLOC de um bloco de tamanho 'size'
                            self.emit(f"STOREG {self.offset}")  # guarda o endereço em gp[offset]
                            # Regista a variável do array na tabela: (nome -> ('array', gp_offset, low, size, tipo_elem))
                            elem_tp = tp[2]  # tipo dos elementos
                            self.symtab[name] = ('array', self.offset, low, size, elem_tp)
                            self.offset += 1
                        else:
                            # Variável global simples: regista apenas ('global', offset)
                            self.symtab[name] = ('global', self.offset)
                            self.offset += 1


    # Escolhe qual 'gen' chamar conforme node[0]
    def gen(self, node):
        fn = getattr(self, f"gen_{node[0]}", None)
        if not fn:
            # Se não existir o método gen_<tipo>, lança exceção
            raise NotImplementedError(f"gen_{node[0]} não implementado")
        return fn(node)


    # Gera o código para o nó 'program'
    def gen_program(self, node):
        _, _, block = node
        # Início da execução principal: emitir START
        self.emit("START")
        # Geração do bloco principal
        self.gen(block)
        # Fim do programa: emitir STOP
        self.emit("STOP")

        # Depois de gerar o bloco principal, emite o código das sub-rotinas
        for name, (label, _) in self.subroutines.items():
            # Percorre as declarações para encontrar a definição da sub-rotina
            for d in block[1]:
                if d and d[1].lower() == name:
                    if d[0] == 'function':
                        self.gen_function(d)
                    else:
                        self.gen_procedure(d)


    # Gera o código para 'block' (lista de statements)
    def gen_block(self, node):
        _, _, stmts = node
        for stmt in stmts:
            if stmt:
                self.gen(stmt)


    # Gera o código para 'compound' (lista de statements dentro de begin..end)
    def gen_compound(self, node):
        _, stmts = node
        for stmt in stmts:
            if stmt:
                self.gen(stmt)


    # Gera o código para nó vazio (no-op)
    def gen_empty(self, node):
        return


    # Gera o código para chamadas de function/procedure, bem como operações built-in (read, write, etc.)
    def gen_call(self, node):
        _, name, args = node
        nl = name.lower()

        # Operações built-in de cast: real(x) e integer(x)
        if nl == 'real':
            if len(args) != 1:
                raise Exception("real() espera 1 argumento")
            self.gen(args[0])
            self.emit("ITOF")  # inteiro para real
            return
        if nl == 'integer':
            if len(args) != 1:
                raise Exception("integer() espera 1 argumento")
            self.gen(args[0])
            self.emit("FTOI")  # real para inteiro
            return

        # write / writeln: imprime texto ou inteiro
        if nl in ('write', 'writeln'):
            for arg in args:
                # Se for um literal de texto ('const', 'texto', valor)
                if isinstance(arg, tuple) and arg[0] == 'const' and arg[1].lower() == 'texto':
                    self.gen(arg)
                    self.emit('WRITES')  # imprime string
                else:
                    self.gen(arg)
                    self.emit('WRITEI')  # imprime inteiro
            if nl == 'writeln':
                self.emit('WRITELN')  # nova linha
            return

        # read / readln: lê a string do teclado e converte para char ou inteiro
        if nl in ('read', 'readln'):
            for arg in args:
                tag = arg[0]
                # Caso de variável simples: read(ch)
                if tag == 'var':
                    _, var_name = arg
                    kind, *info = self.symtab.get(var_name, (None,))
                    if kind not in ('global', 'local'):
                        raise Exception(f"Variável não encontrada: {var_name}")
                    store = 'STOREG' if kind == 'global' else 'STOREL'
                    # Lê a string completa e empilha o endereço
                    self.emit("READ")
                    # Se a variável for char, faz CHARAT para extrair 1º carácter
                    if self.symtab[var_name][0] == 'global' and isinstance(self.symtab[var_name][-1], tuple) and self.symtab[var_name][-1][0]=='char':
                        self.emit("CHARAT")
                    else:
                        # Caso contrário, converte a string lida para inteiro
                        self.emit("ATOI")
                    # Armazena no registo apropriado (global ou local)
                    self.emit(f"{store} {info[0]}")

                # Caso de atribuição a um elemento de array: arr[idx] := read(...)
                elif tag == 'array':
                    # arg = ('array', ('var', var_name), idx_expr)
                    _, base, idx = arg
                    _, var_name = base
                    entry = self.symtab.get(var_name)
                    if not entry or entry[0] != 'array':
                        raise Exception(f"Uso incorreto: {var_name} não é array")
                    _, off, low, size, elem_tp = entry
                    # Empilha o endereço base do array
                    self.emit(f"PUSHG {off}")
                    # Gera o código do índice
                    self.gen(idx)
                    if low != 0:
                        # Ajusta pelo limite inferior se não começar em 0
                        self.emit(f"PUSHI {low}")
                        self.emit("SUB")
                    # Lê string completa do teclado
                    self.emit("READ")
                    # Se for array de char, extrai o 1º carácter; senão, converte p/ inteiro
                    if isinstance(elem_tp, tuple) and elem_tp[0] == 'char':
                        self.emit("CHARAT")
                    else:
                        self.emit("ATOI")
                    # Armazena no array (STOREN espera valor, índice, endereço)
                    self.emit("STOREN")

                else:
                    raise Exception(f"{nl} requer variáveis ou arrays: {arg}")
            return

        # Chamada de sub-rotina definida pelo utilizador
        if nl not in self.subroutines:
            raise Exception(f"Chamada não declarada: {name}")
        label, nargs = self.subroutines[nl]
        if len(args) != nargs:
            raise Exception(f"{name} espera {nargs} args, recebeu {len(args)}")
        # Empilha espaço para o valor de retorno
        self.emit("PUSHI 0")
        # Avalia e empilha os argumentos
        for arg in args:
            self.gen(arg)
        # Empilha o endereço da sub-rotina e chama
        self.emit(f"PUSHA {label}")
        self.emit("CALL")

    # Gera o código para constantes literais
    def gen_const(self, node):
        _, tp, val = node
        t = tp.lower()
        if t == 'integer':
            self.emit(f"PUSHI {val}")
        elif t == 'real':
            self.emit(f"PUSHF {val}")
        elif t == 'boolean':
            if isinstance(val, str):
                v = 1 if val.lower() == 'true' else 0
            else:
                v = 1 if val else 0
            self.emit(f"PUSHI {v}")
        elif t == 'char':
            # Usa o código ASCII do carácter
            self.emit(f"PUSHI {ord(val)}")
        else:
            # Literal de texto: duplicar aspas e usar PUSHS
            s = val.replace('"', '""')
            self.emit(f'PUSHS "{s}"')


    # Gera o código para variáveis (push do valor armazenado)
    def gen_var(self, node):
        _, name = node
        kind, *info = self.symtab.get(name, (None,))
        if kind == 'global':
            self.emit(f"PUSHG {info[0]}")
        elif kind == 'const':
            # Se for umaconstante nomeada, avalia a expressão constante
            self.gen(info[0])
        elif kind == 'local':
            self.emit(f"PUSHL {info[0]}")
        else:
            raise Exception(f"Variável ou uso incorreto: {name}")


    # Gera o código para indexação de array: arr[idx]
    def gen_array(self, node):
        _, base, idxs = node
        _, name = base
        _, off, low, size, *_ = self.symtab[name]
        # Empilha endereço base
        self.emit(f"PUSHG {off}")
        # Gera o código para o índice
        self.gen(idxs)
        if low != 0:
            # Ajusta pelo limite inferior
            self.emit(f"PUSHI {low}")
            self.emit("SUB")
        # Verifica o índice (CHECK 0, size-1)
        self.emit_check(size)
        # Carrega o valor do array: LOADN
        self.emit("LOADN")


    # Gera o código para atribuição: lhs := expr
    def gen_assign(self, node):
        _, lhs, expr = node
        # Se for uma atribuição ao nome de função (retorno), gera apenas a expressão
        if lhs[0] == 'var' and lhs[1].lower() in self.subroutines and self.subroutines[lhs[1].lower()][1] == len(self.symtab):
            self.gen(expr)
            return

        # Caso seja um array ('array', ('var', name), idx_expr) := expr
        if lhs[0] == 'array':
            _, base, idxs = lhs
            _, name = base
            entry = self.symtab[name]
            off    = entry[1]
            low    = entry[2]
            size   = entry[3]

            # Empilha o endereço base
            self.emit(f"PUSHG {off}")
            # Gera o código do índice
            self.gen(idxs)
            if low != 0:
                self.emit(f"PUSHI {low}")
                self.emit("SUB")
            # CHECK de índice
            self.emit_check(size)
            # Gera o código da expressão e armazena no array
            self.gen(expr)
            self.emit("STOREN")
        else:  # Caso seja uma variável simples
            _, name = lhs
            kind, *info = self.symtab.get(name, (None,))
            if kind == 'local' and name in self.subroutines:
                # Atribuição ao nome da função define o valor de retorno
                self.gen(expr)
            elif kind == 'global':
                self.gen(expr)
                self.emit(f"STOREG {info[0]}")
            elif kind == 'local':
                self.gen(expr)
                self.emit(f"STOREL {info[0]}")
            else:
                raise Exception(f"Atribuição inválida: {name}")


    # Gera o código para operações binárias lógicas/aritméticas
    def gen_binop(self, node):
        _, op, l, r = node
        # Caso especial: '<>' é implementado como NOT(EQUAL)
        if op == '<>':
            self.gen(l)
            self.gen(r)
            self.emit('EQUAL')
            self.emit('NOT')
            return

        # Caso geral: gera código recursivamente para operandos
        self.gen(l)
        self.gen(r)
        # Mapas de operadores para instruções da VM
        int_ops = {
            '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV',
            'div': 'DIV', 'mod': 'MOD',
            '=': 'EQUAL', '<': 'INF', '<=': 'INFEQ',
            '>': 'SUP', '>=': 'SUPEQ'
        }
        float_ops = {
            '+': 'FADD', '-': 'FSUB', '*': 'FMUL', '/': 'FDIV',
            '<': 'FINF', '<=': 'FINFEQ',
            '>': 'FSUP', '>=': 'FSUPEQ'
        }
        bool_ops = {'and': 'AND', 'or': 'OR', '=': 'EQUAL', '<>': 'NE'}
        key = op.lower()

        # Se algum operando for literal real, usa mapeamento float
        is_float = False
        for subtree in (l, r):
            if isinstance(subtree, tuple) and subtree[0] == 'const' and subtree[1].lower() == 'real':
                is_float = True
                break

        # Escolhe  ainstrução adequada
        if key in bool_ops:
            instr = bool_ops[key]
        elif is_float and key in float_ops:
            instr = float_ops[key]
        elif key in int_ops:
            instr = int_ops[key]
        else:
            raise NotImplementedError(f"Operador não suportado: {op}")

        self.emit(instr)


    # Gera o código para negação lógica: ('not', expr)
    def gen_not(self, node):
        _, expr = node
        self.gen(expr)
        self.emit('NOT')


    # Gera o código para instrução if-then-else
    def gen_if(self, node):
        _, cond, then_block, else_block = node
        i = self.label_counter
        self.label_counter += 1
        lbl_else = f"L{i}ELSE"
        lbl_end = f"L{i}ENDIF"

        # Gera a condição e, se zero, salta para lbl_else
        self.gen(cond)
        self.emit(f"JZ {lbl_else}")
        # Bloco then
        self.gen(then_block)
        self.emit(f"JUMP {lbl_end}")
        # Else
        self.emit(f"{lbl_else}:")
        if else_block:
            self.gen(else_block)
        # End-if
        self.emit(f"{lbl_end}:")


    # Gera o código para ciclo while
    def gen_while(self, node):
        _, cond, body = node
        i = self.label_counter
        self.label_counter += 1
        lbl_start = f"L{i}WHILE"
        lbl_end = f"L{i}ENDWHILE"

        self.emit(f"{lbl_start}:")
        # Se a condição for falsa (0), salta para lbl_end
        self.gen(cond)
        self.emit(f"JZ {lbl_end}")
        # Corpo do while
        self.gen(body)
        # Loop de regresso ao início
        self.emit(f"JUMP {lbl_start}")
        self.emit(f"{lbl_end}:")


    # Gera o código para ciclo for
    def gen_for(self, node):
        _, var_node, start_expr, end_expr, direction, body = node
        # var_node pode ser ('var', nome) ou apenas nome
        name = var_node[1] if isinstance(var_node, tuple) else var_node
        kind, off = self.symtab[name][:2]
        if kind != 'global':
            raise Exception(f"For inválido: {name}")

        i = self.label_counter
        self.label_counter += 1
        lbl_start = f"L{i}FOR"
        lbl_end = f"L{i}ENDFOR"

        # Inicializa a variável do for
        self.gen(start_expr)
        self.emit(f"STOREG {off}")

        self.emit(f"{lbl_start}:")
        # Carrega a variável e compara com end_expr
        self.emit(f"PUSHG {off}")
        self.gen(end_expr)
        self.emit("INFEQ" if direction == 'to' else "SUPEQ")
        self.emit(f"JZ {lbl_end}")

        # Corpo do for
        self.gen(body)

        # Incrementa ou decrementa a variável
        self.emit(f"PUSHG {off}")
        self.emit("PUSHI 1")
        self.emit("ADD" if direction == 'to' else "SUB")
        self.emit(f"STOREG {off}")
        # Regressa ao início do loop
        self.emit(f"JUMP {lbl_start}")
        self.emit(f"{lbl_end}:")




# def gen_procedure(self, node):
#     _, name, params, block = node
#     label, _ = self.subroutines[name.lower()]
#     self.emit(f"{label}:")
#     old_sym = self.symtab.copy()
#     for idx, param in enumerate(params):
#         _, ids, _ = param
#         for id in ids:
#             self.symtab[id] = ('local', idx)
#     self.gen(block)
#     self.emit("RETURN")
#     self.symtab = old_sym


# def gen_function(self, node):
#     _, name, params, _, block = node
#     label, _ = self.subroutines[name.lower()]
#     self.emit(f"{label}:")
#     nargs = len(params)
#     old_symtab = self.symtab.copy()
#     for idx, param in enumerate(params):
#         _, ids, _ = param
#         for id in ids:
#             self.symtab[id] = ('local', idx)
#     self.symtab[name] = ('local', nargs)
#     self.gen(block)
#     self.emit(f"PUSHL {nargs}")
#     self.emit("RETURN")
#     self.symtab = old_symtab