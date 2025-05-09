class SemanticError(Exception):
    pass


class Symbol:
    def __init__(self, name, type_):
        self.name = name
        self.type = type_

    def __repr__(self):
        return f"<Symbol name={self.name}, type={self.type}>"


class Scope:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def define(self, name, type_):
        if name in self.symbols:
            raise SemanticError(f"Variável '{name}' já foi declarada neste escopo.")
        self.symbols[name] = Symbol(name, type_)

    def resolve(self, name):
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.resolve(name)
        else:
            raise SemanticError(f"Variável '{name}' usada mas não declarada.")


class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self._init_builtins()
    
    def _init_builtins(self):
        for proc in ['write', 'writeln', 'read', 'readln']:
            self.global_scope.symbols[proc] = Symbol(proc, 'procedure')
        # length: function que recebe um ARRAY e devolve INTEGER
        length_sym = Symbol('length','function')
        # monkey‑patch dos campos que o teu visit_call espera
        length_sym.params = [('arr','ARRAY')]
        length_sym.return_type = 'INTEGER'
        self.global_scope.symbols['length'] = length_sym

    def analyze(self, node):
        self.visit(node)

    def visit(self, node):
        if isinstance(node, tuple):
            method_name = f"visit_{node[0]}"
            method = getattr(self, method_name, self.generic_visit)
            return method(node)
        elif isinstance(node, list):
            for item in node:
                self.visit(item)

    def generic_visit(self, node):
        raise Exception(f"visit_{node[0]} não implementado")

    def visit_program(self, node):
        self.visit(node[2])

    def visit_block(self, node):
        _, decls, comp = node
        if decls:
            for decl in decls:
                self.visit(decl)  # Cada declaração será passada para o método correspondente
        # Depois processa as instruções compostas (o corpo do bloco)
        self.visit(comp)

    def visit_consts(self, node):
        _, const_list = node
        for nome, expr in const_list:
            if nome in self.current_scope.symbols:
                raise SemanticError(f"Constante '{nome}' já declarada.")
            tipo = self.visit(expr)
            self.current_scope.define(nome, tipo)

    def visit_var_decl(self, node):
        _, decls = node
        for decl in decls:
            self.visit(decl)

    def visit_vars(self, node):
        _, nomes, tipo = node
        type_str = self._normalize_type(tipo)
        for nome in nomes:
            self.current_scope.define(nome, type_str)

    def _normalize_type(self, tipo_node):
        kind = tipo_node[0]
        if kind == 'simple_type':
            return tipo_node[1].upper()
        if kind == 'id_type':
            sym = self.current_scope.resolve(tipo_node[1].upper())
            return sym.type
        if kind in ('array_type', 'open_array'):
            elem_type = self._normalize_type(tipo_node[2])
            return ('ARRAY', elem_type)
        if kind == 'enum':
            return 'ENUM'
        if kind == 'subrange':
            return 'INTEGER'
        if kind == 'packed':
            return self._normalize_type(tipo_node[1])
        if kind == 'short_string':
            return 'TEXTO'
        if kind == 'set':
            return 'SET'
        if kind == 'file':
            return 'FILE'
        if kind == 'record':
            return 'RECORD'

    def visit_instrucao_composta(self, node):
        _, instrs = node
        for instr in instrs:
            self.visit(instr)

    def visit_assign(self, node):
        _, var_node, expr = node
        var_type = self.visit(var_node).upper()
        expr_type = self.visit(expr)
        if expr_type != var_type:
            raise SemanticError(f"Tipos incompatíveis: variável é {var_type}, mas expressão é {expr_type}.")

    def visit_numero(self, node):
        _, valor = node
        return 'real' if '.' in str(valor) else 'integer'

    def visit_var(self, node):
        _, nome = node
        sym = self.current_scope.resolve(nome)
        return sym.type

    def visit_array(self, node):
        _, base, _ = node
        base_type = self.visit(base)
        if isinstance(base_type, tuple) and base_type[0] == 'ARRAY':
            return base_type[1]  # tipo do elemento
        else:
            raise SemanticError(f"Tentativa de indexar uma variável que não é um array: {base_type}")

    def visit_field(self, node):
        _, base, _ = node
        return self.visit(base)

    def visit_const(self, node):
        _, type, _ = node
        return type

    def visit_binop(self, node):
        _, op, esq, dir_ = node
        op = op.upper()
        tipo_esq = self.visit(esq)
        tipo_dir = self.visit(dir_)

        # Operadores aritméticos
        if op in ['+', '-', '*', '/']:
            if tipo_esq not in ['INTEGER', 'REAL'] or tipo_dir not in ['INTEGER', 'REAL']:
                raise SemanticError(f"Operador '{op}' só pode ser aplicado a tipos numéricos, mas recebeu {tipo_esq} e {tipo_dir}.")
            # Se algum dos operandos for REAL, o resultado será REAL
            if tipo_esq == 'REAL' or tipo_dir == 'REAL' or op == '/':
                return 'REAL'
            return 'INTEGER'

        # Operador DIV (divisão inteira)
        if op == 'DIV':
            if tipo_esq != 'INTEGER' or tipo_dir != 'INTEGER':
                raise SemanticError(f"Operador 'DIV' requer dois inteiros, mas recebeu {tipo_esq} e {tipo_dir}.")
            return 'INTEGER'

        # Operador MOD (resto da divisão)
        if op == 'MOD':
            if tipo_esq != 'INTEGER' or tipo_dir != 'INTEGER':
                raise SemanticError(f"Operador 'MOD' requer dois inteiros, mas recebeu {tipo_esq} e {tipo_dir}.")
            return 'INTEGER'

        # Operadores relacionais
        if op in ['=', '<>']:
            # Permitir comparação entre INTEGER e REAL
            if {tipo_esq, tipo_dir} <= {'INTEGER', 'REAL'}:
                return 'BOOLEAN'
            # Outros tipos têm de coincidir
            if tipo_esq != tipo_dir:
                raise SemanticError(f"Comparação '{op}' requer operandos compatíveis, mas recebeu {tipo_esq} e {tipo_dir}.")
            if tipo_esq not in ['BOOLEAN', 'CHAR', 'TEXTO']:
                raise SemanticError(f"Operador '{op}' não suportado para tipo {tipo_esq}.")
            return 'BOOLEAN'

        elif op in ['<', '<=', '>', '>=']:
            # Apenas INTEGER, REAL e STRING são válidos
            if {tipo_esq, tipo_dir} <= {'INTEGER', 'REAL'}:
                return 'BOOLEAN'
            if tipo_esq == tipo_dir == ('CHAR' or 'TEXTO'):
                return 'BOOLEAN'
            raise SemanticError(f"Operador relacional '{op}' não suportado para tipos {tipo_esq} e {tipo_dir}.")

        # Operadores lógicos
        if op in ['AND', 'OR']:
            if tipo_esq != 'BOOLEAN' or tipo_dir != 'BOOLEAN':
                raise SemanticError(f"Operador lógico '{op}' requer dois operandos BOOLEAN, mas recebeu {tipo_esq} e {tipo_dir}.")
            return 'BOOLEAN'

        raise SemanticError(f"Operador desconhecido '{op}' ou operação não suportada entre {tipo_esq} e {tipo_dir}.")
    


    def visit_if(self, node):
        _, cond, then_stmt, else_stmt = node

        cond_type = self.visit(cond)
        if cond_type != 'BOOLEAN':
            raise SemanticError(f"A condição do IF deve ser BOOLEAN, mas foi {cond_type}.")

        self.visit(then_stmt)
        if else_stmt is not None:
            self.visit(else_stmt)

    

    def visit_call(self, node):
        _, nome, argumentos = node
        nl = nome.lower()

        # ── caso especial: length(array) → INTEGER
        if nl == 'length':
            if len(argumentos) != 1:
                raise SemanticError(f"Função 'length' espera 1 argumento, mas recebeu {len(argumentos)}.")
            t = self.visit(argumentos[0])
            if not (isinstance(t, tuple) and t[0] == 'ARRAY'):
                raise SemanticError(f"Função 'length' requer ARRAY, mas recebeu {t}.")
            return 'INTEGER'

        # ── resolve símbolo (procedure ou function)
        simbolo = self.current_scope.resolve(nl)

        # ── procedures predefinidas (write, writeln, read, readln)
        if not hasattr(simbolo, 'params'):
            for arg in argumentos:
                self.visit(arg)
            return  # procedure não devolve tipo

        # ── procedimentos/funções do utilizador (têm .params)
        parametros = simbolo.params
        if len(parametros) != len(argumentos):
            raise SemanticError(
                f"'{nome}' espera {len(parametros)} argumentos, mas recebeu {len(argumentos)}."
            )

        # valida cada argumento
        for (param_nome, param_tipo), arg_expr in zip(parametros, argumentos):
            arg_tipo = self.visit(arg_expr)
            if arg_tipo != param_tipo:
                # coerção INTEGER→REAL permitida
                if not (param_tipo == 'REAL' and arg_tipo == 'INTEGER'):
                    raise SemanticError(
                        f"Argumento para '{param_nome}' deve ser {param_tipo}, mas recebeu {arg_tipo}."
                    )

        # ── se tiver return_type, é function: devolve-o
        if hasattr(simbolo, 'return_type'):
            return simbolo.return_type



    def visit_for(self, node):
        # node = ('for', loop_var_name, start_expr, end_expr, direction, body_stmt)
        _, var_name, start_expr, end_expr, _, body = node

        # 1) A variável de controlo deve existir e ser INTEGER
        sym = self.current_scope.resolve(var_name)
        if sym.type.upper() != 'INTEGER':
            raise SemanticError(
                f"Variável de controlo do FOR '{var_name}' deve ser INTEGER, mas é {sym.type}."
            )

        # 2) Início e fim devem ser INTEGER
        t_start = self.visit(start_expr)
        t_end   = self.visit(end_expr)
        if t_start != 'INTEGER':
            raise SemanticError(
                f"Expressão inicial do FOR deve ser INTEGER, mas é {t_start}."
            )
        if t_end != 'INTEGER':
            raise SemanticError(
                f"Expressão final do FOR deve ser INTEGER, mas é {t_end}."
            )

        # 3) Processa o corpo do laço
        self.visit(body)
    


    def visit_while(self, node):
        # node = ('while', condition_expr, body_stmt)
        _, cond_expr, body = node

        # 1) A condição do while deve ser BOOLEAN
        cond_type = self.visit(cond_expr)
        if cond_type != 'BOOLEAN':
            raise SemanticError(
                f"Condição de WHILE deve ser BOOLEAN, mas é {cond_type}."
            )

        # 2) Analisa semanticamente o corpo do laço
        self.visit(body)
    


    def visit_compound(self, node):
        # node = ('compound', statement_list)
        _, stmts = node

        # Percorre cada instrução do bloco composto
        for stmt in stmts:
            # stmt pode ser None (na regra de statement permite empty)
            if stmt is not None:
                self.visit(stmt)



    def visit_types(self, node):
        _, type_list = node
        for name, tipo in type_list:
            type_str = self._normalize_type(tipo)
            self.current_scope.define(name.upper(), type_str)