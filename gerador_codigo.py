# Extrai valor de nós do tipo ('const', tipo, valor) ou de constantes nomeadas
def extrair_valor_constante(ast, consts):
    if isinstance(ast, int):
        return ast
    elif isinstance(ast, float):
        return ast
    elif isinstance(ast, tuple):
        tag = ast[0]
        if tag == 'const_expr':
            tipo = ast[1]
            valor = ast[2]
            if tipo == 'integer':
                return int(valor)
            elif tipo == 'real':
                return float(valor)
            elif tipo == 'boolean':
                return valor.lower() == 'true'
            elif tipo == 'char':
                return valor
            else:
                raise Exception(f"Tipo constante não suportado: {tipo}")
        elif tag == 'var':
            nome = ast[1]
            if nome not in consts:
                raise Exception(f"Constante não definida: {nome}")
            return extrair_valor_constante(consts[nome], consts)
        elif tag == 'binop':
            _, op, left, right = ast
            lval = extrair_valor_constante(left, consts)
            rval = extrair_valor_constante(right, consts)
            if op in ('+', '-', '*', '/', 'div', 'mod'):
                if op == '+': return lval + rval
                if op == '-': return lval - rval
                if op == '*': return lval * rval
                if op == '/': return lval / rval
                if op == 'div': return lval // rval
                if op == 'mod': return lval % rval
            else:
                raise Exception(f"Operador constante não suportado: {op}")
        else:
            raise Exception(f"Nó constante inesperado: {ast}")
    else:
        raise Exception(f"Tipo de nó inesperado: {ast}")





class CodeGenerator:
    def __init__(self):
        self.symtab = {}         # name -> ('const', expr) | ('global', offset) | ('array', off, low, size) | ('local', offset)
        self.consts = {}         # name -> expr AST
        self.subroutines = {}    # name -> (label, nargs)
        self.types = {}          # name -> type AST (para aliases)
        self.code = []
        self.offset = 0
        self.label_counter = 0



    def emit(self, instr):
        self.code.append(instr)



    def write(self, filename):
        with open(filename, 'w') as f:
            for instr in self.code:
                f.write(instr + '\n')



    def emit_check(self, size):
        self.emit(f"CHECK 0,{size-1}")



    def build_symtab(self, ast):
        _, _, block = ast
        decls, _ = block[1], block[2]
        # 0) Capturar aliases de tipo
        for d in decls:
            if d and d[0] == 'types':
                for name, tp in d[1]:
                    self.types[name.lower()] = tp
        # 1) Extrair constantes
        for d in decls:
            if d and d[0] == 'consts':
                for name, expr in d[1]:
                    self.consts[name] = expr
                    self.symtab[name] = ('const', expr)
        # 2) Registar subrotinas
        for d in decls:
            if d and d[0] in ('function', 'procedure'):
                name = d[1].lower()
                params = d[2] or []
                nargs = len(params)
                label = name.upper()
                self.subroutines[name] = (label, nargs)
        # 3) Registar variáveis globais e arrays
        for d in decls:
            if d and d[0] == 'var_decl':
                for _, id_list, raw_tp in d[1]:
                    # resolve alias de tipo
                    tp = raw_tp
                    if isinstance(tp, tuple) and tp[0] == 'id_type':
                        alias = tp[1].lower()
                        if alias in self.types:
                            tp = self.types[alias]
                    for name in id_list:
                        if isinstance(tp, tuple) and tp[0] == 'array_type':
                            low_ast, high_ast = tp[1]
                            low  = extrair_valor_constante(low_ast, self.consts)
                            high = extrair_valor_constante(high_ast, self.consts)
                            size = high - low + 1
                            self.emit(f"PUSHI {size}")
                            self.emit("ALLOCN")
                            self.emit(f"STOREG {self.offset}")
                            # grava também o tipo do elemento (tp[2])
                            elem_tp = tp[2]
                            self.symtab[name] = ('array', self.offset, low, size, elem_tp)
                            self.offset += 1
                        else:
                            self.symtab[name] = ('global', self.offset)
                            self.offset += 1



    def gen(self, node):
        fn = getattr(self, f"gen_{node[0]}", None)
        if not fn:
            raise NotImplementedError(f"gen_{node[0]} não implementado")
        return fn(node)



    def gen_program(self, node):
        _, _, block = node
        # início da execução principal
        self.emit("START")
        self.gen(block)
        self.emit("STOP")
        # agora emite as subrotinas
        for name, (label, _) in self.subroutines.items():
            for d in block[1]:
                if d and d[1].lower() == name:
                    if d[0] == 'function':
                        self.gen_function(d)
                    else:
                        self.gen_procedure(d)



    def gen_block(self, node):
        _, _, stmts = node
        for stmt in stmts:
            if stmt:
                self.gen(stmt)



    def gen_compound(self, node):
        _, stmts = node
        for stmt in stmts:
            if stmt:
                self.gen(stmt)



    def gen_empty(self, node):
        return



    def gen_call(self, node):
        _, name, args = node
        nl = name.lower()
        # --- cast built-ins: real(x) e integer(x) ---
        if nl == 'real':
            if len(args) != 1:
                raise Exception("real() espera 1 argumento")
            self.gen(args[0])
            self.emit("ITOF")
            return
        if nl == 'integer':
            if len(args) != 1:
                raise Exception("integer() espera 1 argumento")
            self.gen(args[0])
            self.emit("FTOI")
            return
        if nl in ('write', 'writeln'):
            for arg in args:
                if isinstance(arg, tuple) and arg[0] == 'const' and arg[1].lower() == 'texto':
                    self.gen(arg)
                    self.emit('WRITES')
                else:
                    self.gen(arg)
                    self.emit('WRITEI')
            if nl == 'writeln':
                self.emit('WRITELN')
            return
        if nl in ('read', 'readln'):
            for arg in args:
                tag = arg[0]
                if tag == 'var':
                    _, var_name = arg
                    kind, *info = self.symtab.get(var_name, (None,))
                    if kind not in ('global','local'):
                        raise Exception(f"Variável não encontrada: {var_name}")
                    store = 'STOREG' if kind=='global' else 'STOREL'
                    self.emit("READ")
                    # se for variável char, converte do endereço de string para código ASCII
                    if self.symtab[var_name][0] == 'global' and isinstance(self.symtab[var_name][-1], tuple) and self.symtab[var_name][-1][0]=='char':
                        self.emit("CHARAT")
                    else:
                        self.emit("ATOI")
                    self.emit(f"{store} {info[0]}")
                elif tag == 'array':
                    # l-value array: ('array', ('var',name), idx_expr)
                    _, base, idx = arg
                    _, var_name = base
                    entry = self.symtab.get(var_name)
                    if not entry or entry[0] != 'array':
                        raise Exception(f"Uso incorreto: {var_name} não é array")
                    _, off, low, size, elem_tp = entry
                    # monta endereço
                    self.emit(f"PUSHG {off}")
                    self.gen(idx)
                    if low != 0:
                        self.emit(f"PUSHI {low}")
                        self.emit("SUB")
                    # leitura
                    self.emit("READ")
                    if isinstance(elem_tp, tuple) and elem_tp[0] == 'char':
                        self.emit("CHARAT")
                    else:
                        self.emit("ATOI")
                    # armazena
                    self.emit("STOREN")
                else:
                    raise Exception(f"{nl} requer variáveis ou arrays: {arg}")
            return
        if nl not in self.subroutines:
            raise Exception(f"Chamada não declarada: {name}")
        label, nargs = self.subroutines[nl]
        if len(args) != nargs:
            raise Exception(f"{name} espera {nargs} args, recebeu {len(args)}")
        # Empilha espaço para valor de retorno
        self.emit("PUSHI 0")
        # Avalia e empilha os argumentos
        for arg in args:
            self.gen(arg)
        # Empilha endereço da subrotina após os argumentos
        self.emit(f"PUSHA {label}")
        self.emit("CALL")



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
            # empurra o código ASCII do carácter
            self.emit(f"PUSHI {ord(val)}")
        else:
            # texto literal
            s = val.replace('"', '""')
            self.emit(f'PUSHS "{s}"')




    def gen_var(self, node):
        _, name = node
        kind, *info = self.symtab.get(name, (None,))
        if kind == 'global':
            self.emit(f"PUSHG {info[0]}")
        elif kind == 'const':
            self.gen(info[0])
        elif kind == 'local':
            self.emit(f"PUSHL {info[0]}")
        else:
            raise Exception(f"Variável ou uso incorreto: {name}")



    def gen_array(self, node):
        _, base, idxs = node
        _, name = base
        _, off, low, size, *_ = self.symtab[name]
        self.emit(f"PUSHG {off}")
        self.gen(idxs)
        if low != 0:
            self.emit(f"PUSHI {low}")
            self.emit("SUB")
        self.emit_check(size)
        self.emit("LOADN")



    def gen_assign(self, node):
        _, lhs, expr = node
        # se for atribuição ao nome da função (retorno), gera apenas a expressão
        if lhs[0] == 'var' and lhs[1].lower() in self.subroutines and self.subroutines[lhs[1].lower()][1] == len(self.symtab):
            # trata como retorno: avalia a expressão e empilha
            self.gen(expr)
            return
        if lhs[0] == 'array':
            _, base, idxs = lhs
            _, name = base
            entry = self.symtab[name]
            off    = entry[1]
            low    = entry[2]
            size   = entry[3]

            self.emit(f"PUSHG {off}")
            self.gen(idxs)
            if low != 0:
                self.emit(f"PUSHI {low}")
                self.emit("SUB")
            self.emit_check(size)
            self.gen(expr)
            self.emit("STOREN")
        else:
            _, name = lhs
            kind, *info = self.symtab.get(name, (None,))
            if kind == 'local' and name in self.subroutines:
                # atribuição ao nome da função -> valor de retorno
                self.gen(expr)  # deixa o valor no topo da pilha
            elif kind == 'global':
                self.gen(expr)
                self.emit(f"STOREG {info[0]}")
            elif kind == 'local':
                self.gen(expr)
                self.emit(f"STOREL {info[0]}")
            else:
                raise Exception(f"Atribuição inválida: {name}")



    def gen_binop(self, node):
        _, op, l, r = node
        if op == '<>':
            self.gen(l)
            self.gen(r)
            self.emit('EQUAL')
            self.emit('NOT')
            return
        self.gen(l)
        self.gen(r)
        int_ops = {
            '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV',
            'div': 'DIV', 'mod': 'MOD',
            '=': 'EQUAL',   '<': 'INF', '<=': 'INFEQ',
            '>': 'SUP', '>=': 'SUPEQ'
        }
        # mapeamentos ponto-flutuante
        float_ops = {
            '+': 'FADD', '-': 'FSUB', '*': 'FMUL', '/': 'FDIV',
            '<': 'FINF', '<=': 'FINFEQ',
            '>': 'FSUP', '>=': 'FSUPEQ'
        }
        # operações lógicas são sempre inteiras
        bool_ops = {'and': 'AND', 'or': 'OR', '=': 'EQUAL', '<>': 'NE'}
        key = op.lower()
        # escolhe float se algum operando for REAL literal
        is_float = False
        for subtree in (l, r):
            if isinstance(subtree, tuple) and subtree[0] == 'const' and subtree[1].lower() == 'real':
                is_float = True
                break
        if key in bool_ops:
            instr = bool_ops[key]
        elif is_float and key in float_ops:
            instr = float_ops[key]
        elif key in int_ops:
            instr = int_ops[key]
        else:
            raise NotImplementedError(f"Operador não suportado: {op}")
        if not instr:
            raise NotImplementedError(f"Operador não suportado: {op}")
        self.emit(instr)



    def gen_not(self, node):
        _, expr = node
        self.gen(expr)
        self.emit('NOT')



    def gen_if(self, node):
        _, cond, then_block, else_block = node
        i = self.label_counter
        self.label_counter += 1
        lbl_else = f"L{i}ELSE"
        lbl_end = f"L{i}ENDIF"
        self.gen(cond)
        self.emit(f"JZ {lbl_else}")
        self.gen(then_block)
        self.emit(f"JUMP {lbl_end}")
        self.emit(f"{lbl_else}:")
        if else_block:
            self.gen(else_block)
        self.emit(f"{lbl_end}:")



    def gen_while(self, node):
        _, cond, body = node
        i = self.label_counter
        self.label_counter += 1
        lbl_start = f"L{i}WHILE"
        lbl_end = f"L{i}ENDWHILE"
        self.emit(f"{lbl_start}:")
        self.gen(cond)
        self.emit(f"JZ {lbl_end}")
        self.gen(body)
        self.emit(f"JUMP {lbl_start}")
        self.emit(f"{lbl_end}:")



    def gen_for(self, node):
        _, var_node, start_expr, end_expr, direction, body = node
        name = var_node[1] if isinstance(var_node, tuple) else var_node
        kind, off = self.symtab[name][:2]
        if kind != 'global':
            raise Exception(f"For inválido: {name}")
        i = self.label_counter
        self.label_counter += 1
        lbl_start = f"L{i}FOR"
        lbl_end = f"L{i}ENDFOR"
        self.gen(start_expr)
        self.emit(f"STOREG {off}")
        self.emit(f"{lbl_start}:")
        self.emit(f"PUSHG {off}")
        self.gen(end_expr)
        self.emit("INFEQ" if direction == 'to' else "SUPEQ")
        self.emit(f"JZ {lbl_end}")
        self.gen(body)
        self.emit(f"PUSHG {off}")
        self.emit("PUSHI 1")
        self.emit("ADD" if direction == 'to' else "SUB")
        self.emit(f"STOREG {off}")
        self.emit(f"JUMP {lbl_start}")
        self.emit(f"{lbl_end}:")



    # def gen_procedure(self, node):
    #     _, name, params, block = node
    #     label, _ = self.subroutines[name.lower()]
    #     self.emit(f"{label}:")
    #     old_sym = self.symtab.copy()
    #     # parâmetros como locais
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
    #     # Snapshot da tabela de símbolos
    #     old_symtab = self.symtab.copy()
    #     # Parâmetros: PUSHL 0 .. PUSHL nargs-1
    #     for idx, param in enumerate(params):
    #         _, ids, _ = param
    #         for id in ids:
    #             self.symtab[id] = ('local', idx)
    #     # Valor de retorno em PUSHL nargs
    #     self.symtab[name] = ('local', nargs)
    #     # Gerar corpo
    #     self.gen(block)
    #     # Empilhar valor de retorno
    #     self.emit(f"PUSHL {nargs}")
    #     self.emit("RETURN")
    #     # Restaurar símbolos
    #     self.symtab = old_symtab