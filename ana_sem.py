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
        if isinstance(type_, Symbol):
            sym = type_
            sym.name = name
        else:
            sym = Symbol(name, type_)
        self.symbols[name] = sym

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
        for proc in ['write', 'writeln', 'read', 'readln', 'rewrite']:
            self.global_scope.symbols[proc] = Symbol(proc, 'procedure')
        # length: function que recebe um array e devolve integer
        length_sym = Symbol('length','function')
        length_sym.params = [('arr','array')]
        length_sym.return_type = 'integer'
        self.global_scope.symbols['length'] = length_sym

        # assign(fileVar, fileName)
        assign_sym = Symbol('assign', 'procedure')
        assign_sym.params = [
            ('filevar', 'file'),
            ('filename', [('array', 'char'), 'texto'])
        ]
        self.global_scope.symbols['assign'] = assign_sym

        high_sym = Symbol('high','function')
        high_sym.params = [('arr','array')]
        high_sym.return_type = 'integer'
        self.global_scope.define('high', high_sym)

        close_sym = Symbol('close','procedure')
        close_sym.params = [('filevar','file')]
        self.global_scope.define('close', close_sym)

        chr_sym = Symbol('chr','function')
        chr_sym.params = [('code','integer')]
        chr_sym.return_type = 'char'
        self.global_scope.define('chr', chr_sym)

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
            if nome.lower() in self.current_scope.symbols:
                raise SemanticError(f"Constante '{nome}' já declarada.")
            tipo = self.visit(expr).lower()
            self.current_scope.define(nome.lower(), tipo)

    def visit_var_decl(self, node):
        _, decls = node
        for decl in decls:
            self.visit(decl)

    def visit_vars(self, node):
        _, nomes, tipo = node
        type_str = self._normalize_type(tipo)
        for nome in nomes:
            self.current_scope.define(nome.lower(), type_str)

    def _normalize_type(self, tipo_node):
        kind = tipo_node[0].lower()
        if kind == 'simple_type':
            return tipo_node[1].lower()
        if kind == 'id_type':
            sym = self.current_scope.resolve(tipo_node[1].lower())
            return sym.type
        if kind == 'array_type':
            elem_type = self._normalize_type(tipo_node[2])
            return ('array', elem_type)
        if kind == 'open_array':
            elem_type = self._normalize_type(tipo_node[1])
            return ('array', elem_type)
        if kind == 'enum':
            return 'ENUM'.lower()
        if kind == 'subrange':
            return 'integer'.lower()
        if kind == 'packed':
            return self._normalize_type(tipo_node[1])
        if kind == 'short_string':
            return 'texto'.lower()
        if kind == 'set':
            return 'SET'.lower()
        if kind == 'file':
            return 'FILE'.lower()
        if kind == 'record':
            return 'RECORD'.lower()

    def visit_instrucao_composta(self, node):
        _, instrs = node
        for instr in instrs:
            self.visit(instr)

    def visit_assign(self, node):
        # node = ('assign', var_node, expr)
        _, var_node, expr = node
        nome_var = var_node[1]

        # caso “return” dentro de função
        if not isinstance(nome_var, tuple):
            nome_var = nome_var.lower()
            if nome_var == getattr(self, 'current_function', None):
                expr_type = self.visit(expr).lower()
                # busca símbolo da função no escopo global (onde definimos return_type)
                func_sym = self.global_scope.resolve(nome_var.lower())
                ret_type = func_sym.return_type.lower()
                if expr_type != ret_type:
                    raise SemanticError(
                        f"Tipo de retorno incorreto em '{var_node[1]}': "
                        f"esperado {ret_type}, mas foi {expr_type}."
                    )
                return

        # atribuição normal a variável
        var_type = self.visit(var_node)
        expr_type = self.visit(expr)
        if expr_type.upper() != var_type.upper():
            raise SemanticError(
                f"Tipos incompatíveis na atribuição: variável '{var_node}' é {var_type}, "
                f"mas expressão é {expr_type}."
            )

    def visit_numero(self, node):
        _, valor = node
        return 'real' if '.' in str(valor) else 'integer'

    def visit_var(self, node):
        _, nome = node
        sym = self.current_scope.resolve(nome.lower())
        return sym.type

    def visit_array(self, node):
        _, base, _ = node
        base_type = self.visit(base)
        if isinstance(base_type, tuple) and base_type[0] == 'array':
            return base_type[1]  # tipo do elemento
        else:
            raise SemanticError(f"Tentativa de indexar uma variável que não é um array: {base_type}")

    def visit_field(self, node):
        _, base_node, field_name = node

        # obtém o tipo do base (pode vir de visit_var ou visit_array)
        base_type = self.visit(base_node)    # ex.: "tregistopessoa"
        # resolve o símbolo desse tipo
        type_sym = self.current_scope.resolve(base_type)

        if not hasattr(type_sym, 'fields'):
            raise SemanticError(f"Tentativa de aceder campo '{field_name}' de não‑record ({base_type}).")

        key = field_name.lower()
        if key not in type_sym.fields:
            raise SemanticError(f"Campo '{field_name}' não existe em record '{base_type}'.")
        return type_sym.fields[key]

    def visit_const(self, node):
        _, type, _ = node
        return type

    def visit_binop(self, node):
        _, op, esq, dir_ = node
        op = op.lower()
        tipo_esq = self.visit(esq)
        tipo_dir = self.visit(dir_)
    
        # Função auxiliar para obter o nome base (e.g. 'set' ou 'integer')
        def tipo_base(t):
            return t.lower() if isinstance(t, str) else t[0].lower()
    
        base_esq = tipo_base(tipo_esq)
        base_dir = tipo_base(tipo_dir)
    
        # Operadores aritméticos
        if op in ['+', '-', '*', '/']:
            if base_esq not in ['integer', 'real'] or base_dir not in ['integer', 'real']:
                raise SemanticError(f"Operador '{op}' só pode ser aplicado a tipos numéricos, mas recebeu {tipo_esq} e {tipo_dir}.")
            if 'real' in [base_esq, base_dir] or op == '/':
                return 'real'
            return 'integer'
    
        # Operadores div e mod
        if op in ['div', 'mod']:
            if base_esq != 'integer' or base_dir != 'integer':
                raise SemanticError(f"Operador '{op}' requer dois inteiros, mas recebeu {tipo_esq} e {tipo_dir}.")
            return 'integer'
    
        # Operadores relacionais
        if op in ['=', '<>']:
            if {base_esq, base_dir} <= {'integer', 'real'}:
                return 'boolean'
            if tipo_esq != tipo_dir:
                raise SemanticError(f"Comparação '{op}' requer operandos compatíveis, mas recebeu {tipo_esq} e {tipo_dir}.")
            if base_esq not in ['boolean', 'char', 'texto', 'set']:
                raise SemanticError(f"Operador '{op}' não suportado para tipo {tipo_esq}.")
            return 'boolean'
    
        elif op in ['<', '<=', '>', '>=']:
            if {base_esq, base_dir} <= {'integer', 'real'}:
                return 'boolean'
            if base_esq == base_dir and base_esq in ['char', 'texto']:
                return 'boolean'
            raise SemanticError(f"Operador relacional '{op}' não suportado para tipos {tipo_esq} e {tipo_dir}.")
    
        # Operador IN (elemento ∈ conjunto)
        if op == 'in':
            if not isinstance(tipo_dir, tuple) or tipo_dir[0] != 'set':
                raise SemanticError(f"Operador 'in' requer um conjunto do lado direito, mas recebeu {tipo_dir}.")
            elem_type = tipo_dir[1].lower()
            if tipo_esq != elem_type:
                raise SemanticError(f"Elemento do tipo {tipo_esq} não compatível com o conjunto de {elem_type}.")
            return 'boolean'
    
        # Operadores lógicos
        if op in ['and', 'or']:
            if base_esq != 'boolean' or base_dir != 'boolean':
                raise SemanticError(f"Operador lógico '{op}' requer dois boolean, mas recebeu {tipo_esq} e {tipo_dir}.")
            return 'boolean'
    
        raise SemanticError(f"Operador desconhecido '{op}' ou operação não suportada entre {tipo_esq} e {tipo_dir}.")
    


    def visit_if(self, node):
        _, cond, then_stmt, else_stmt = node

        cond_type = self.visit(cond)
        if cond_type != 'boolean':
            raise SemanticError(f"A condição do IF deve ser boolean, mas foi {cond_type}.")

        self.visit(then_stmt)
        if else_stmt is not None:
            self.visit(else_stmt)



    def visit_call(self, node):
        _, nome, argumentos = node
        nl = nome.lower()

        sym = None
        try:
            sym = self.current_scope.resolve(nl)
        except SemanticError:
            pass

        if sym is not None \
           and not hasattr(sym, 'params') \
           and not hasattr(sym, 'return_type') \
           and sym.type.lower() == nl:
            # é cast
            if len(argumentos) != 1:
                raise SemanticError(f"Cast para '{nome}' espera 1 argumento, mas recebeu {len(argumentos)}.")
            # valida o interior
            t = self.visit(argumentos[0])
            # podes aqui validar intervalos (e.g. 0..6) se quiseres
            return nl   # devolve o nome do tipo (casefold)

        # caso especial length(array)
        if nl == 'length':
            if len(argumentos) != 1:
                raise SemanticError(f"Função 'length' espera 1 argumento, mas recebeu {len(argumentos)}.")
            t = self.visit(argumentos[0])
            if not (isinstance(t, tuple) and t[0] == 'array'):
                raise SemanticError(f"Função 'length' requer array, mas recebeu {t}.")
            return 'integer'

        if nl == 'assign':
            if len(argumentos) != 2:
                raise SemanticError(f"Procedure 'assign' espera 2 argumentos, mas recebeu {len(argumentos)}.")
            # argumento 1
            t1 = self.visit(argumentos[0])
            if t1.casefold() != 'file':
                raise SemanticError(f"Argumento 1 de 'assign' deve ser FILE, mas recebeu {t1}.")
            # argumento 2
            t2 = self.visit(argumentos[1])
            if not (
                (isinstance(t2, tuple) and t2 == ('array','char'))
                or (isinstance(t2, str) and t2 == 'texto')
            ):
                raise SemanticError(f"Argumento 2 de 'assign' deve ser TEXTO, mas recebeu {t2}.")
            return None
        
        if nl == 'high':
            if len(argumentos) != 1:
                raise SemanticError(f"Função 'high' espera 1 argumento, mas recebeu {len(argumentos)}.")
            t = self.visit(argumentos[0])
            if not (isinstance(t, tuple) and t[0].casefold() == 'array'):
                raise SemanticError(f"Função 'high' requer array, mas recebeu {t}.")
            return 'integer'
        
        if nl == 'close':
            if len(argumentos) != 1:
                raise SemanticError(f"Procedure 'close' espera 1 argumento, mas recebeu {len(argumentos)}.")
            t = self.visit(argumentos[0])
            if t.casefold() != 'file':
                raise SemanticError(f"Argumento de 'close' deve ser FILE, mas recebeu {t}.")
            return None
        
        if nl == 'chr':
            if len(argumentos) != 1:
                raise SemanticError(f"Função 'chr' espera 1 argumento, mas recebeu {len(argumentos)}.")
            t = self.visit(argumentos[0])
            if t.casefold() != 'integer':
                raise SemanticError(f"Argumento de 'chr' deve ser INTEGER, mas recebeu {t}.")
            return 'char'

        simbolo = self.current_scope.resolve(nl)
        if hasattr(simbolo, 'params'):
            if len(argumentos) != len(simbolo.params):
                raise SemanticError(f"'{nome}' espera {len(simbolo.params)} argumentos, mas recebeu {len(argumentos)}.")
            for (pname, ptype), a in zip(simbolo.params, argumentos):
                at = self.visit(a)
                if at != ptype:
                    if not ((ptype=='real' and at=='integer') or (ptype=='texto' and at==('array', 'char')) or (ptype==('array', 'char') and at=='texto')):
                        raise SemanticError(f"Argumento para '{pname}' deve ser {ptype}, mas recebeu {at}.")
            if hasattr(simbolo, 'return_type'):
                return simbolo.return_type.casefold()
            return None

        # 5) Built‑in simples (write, writeln, read, readln)
        for a in argumentos:
            self.visit(a)
        return None
    


    def visit_function(self, node):
        # node = ('function', nome, params, return_type, block)
        _, nome, params, return_type, block = node
        nl = nome.lower()

        # 1) verifica duplicação no escopo pai
        if nl in self.current_scope.symbols:
            raise SemanticError(f"A função '{nome}' já está definida.")

        # 2) cria e regista o símbolo da função no escopo actual (pai)
        func_sym = Symbol(nl, 'function')
        # converte params AST → lista de (nome, TIPO)
        lista = []
        for p in params:                        # p = ('param',[nomes], tipo_node)
            _, nomes, tipo_node = p
            tipo_str = self._normalize_type(tipo_node)
            for id_name in nomes:
                lista.append((id_name.lower(), tipo_str))
        func_sym.params = lista
        # tipo de retorno normalizado
        func_sym.return_type = self._normalize_type(return_type)

        # define a função no escopo actual
        self.current_scope.define(nl, func_sym)

        # 3) prepara análise do corpo
        prev_fn = getattr(self, 'current_function', None)
        self.current_function = nl

        # abre escopo interno e define só os parâmetros
        self.current_scope = Scope(self.current_scope)
        for param_nome, param_tipo in func_sym.params:
            self.current_scope.define(param_nome.lower(), param_tipo)

        # analisa corpo
        self.visit(block)

        # fecha escopo e repõe função corrente
        self.current_scope = self.current_scope.parent
        self.current_function = prev_fn

        return func_sym.return_type



    def visit_for(self, node):
        # node = ('for', loop_var_name, start_expr, end_expr, direction, body_stmt)
        _, var_name, start_expr, end_expr, _, body = node

        # 1) A variável de controlo deve existir e ser integer
        sym = self.current_scope.resolve(var_name.lower())
        if sym.type.lower() != 'integer'.lower():
            raise SemanticError(
                f"Variável de controlo do FOR '{var_name}' deve ser integer, mas é {sym.type}."
            )

        # 2) Início e fim devem ser integer
        t_start = self.visit(start_expr).lower()
        t_end   = self.visit(end_expr).lower()
        if t_start != 'integer'.lower():
            raise SemanticError(
                f"Expressão inicial do FOR deve ser integer, mas é {t_start}."
            )
        if t_end != 'integer'.lower():
            raise SemanticError(
                f"Expressão final do FOR deve ser integer, mas é {t_end}."
            )

        # 3) Processa o corpo do laço
        self.visit(body)
    


    def visit_while(self, node):
        # node = ('while', condition_expr, body_stmt)
        _, cond_expr, body = node

        # 1) A condição do while deve ser boolean
        cond_type = self.visit(cond_expr)
        if cond_type != 'boolean':
            raise SemanticError(
                f"Condição de WHILE deve ser boolean, mas é {cond_type}."
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
            kind = tipo[0].lower()
            if kind == 'record':
                # extrai a lista de declarações de campos
                field_list = tipo[1]
                # normaliza cada campo
                campos = {}
                for _, nomes, campo_tipo_node in field_list:   # nodo ('fields', [nomes], tipo_node)
                    t_str = self._normalize_type(campo_tipo_node)
                    for id_name in nomes:
                        key = id_name.lower()
                        if key in campos:
                            raise SemanticError(f"Campo '{id_name}' já definido em record '{name}'.")
                        campos[key] = t_str
                # cria símbolo do tipo record, com atributo .fields
                rec_sym = Symbol(name.lower(), name.lower())
                rec_sym.fields = campos
                self.current_scope.define(name.lower(), rec_sym)
            else:
                if kind == 'enum':
                    # os enums continuam a ser um tipo próprio
                    self.current_scope.define(name.lower(), name.lower())
                elif kind == 'subrange':
                    # subrange → desce ao tipo base (integer)
                    base_type = self._normalize_type(tipo)   # isto já retorna 'integer'
                    self.current_scope.define(name.lower(), base_type)
                else:
                    type_str = self._normalize_type(tipo)
                    self.current_scope.define(name.lower(), type_str)
    


    def visit_labels(self, node):
        _, label_list = node

        for lbl in label_list:
            key = str(lbl).lower()
            # se já existir um símbolo com esse nome no mesmo escopo, é duplicado
            if key in self.current_scope.symbols:
                raise SemanticError(f"Label '{lbl}' já declarado neste escopo.")
            # define-o como símbolo de tipo 'label'
            self.current_scope.symbols[key] = Symbol(key, 'label')

    

    def visit_procedure(self, node):
        # node = ('procedure', nome, params, block)
        _, nome, params, block = node
        nl = nome.lower()

        # 1) verifica duplicação no escopo actual
        if nl in self.current_scope.symbols:
            raise SemanticError(f"Procedimento '{nome}' já está definido neste escopo.")

        # 2) cria o símbolo da procedure no escopo actual (pai)
        proc_sym = Symbol(nl, 'procedure')

        # ── extrai e normaliza os parâmetros, tal como em visit_function
        lista = []
        for p in params:                  # p = ('param', [nomes], tipo_node)
            _, nomes, tipo_node = p
            tipo_str = self._normalize_type(tipo_node)
            for id_name in nomes:
                lista.append((id_name.lower(), tipo_str))
        proc_sym.params = lista

        # regista a procedure no escopo actual
        self.current_scope.define(nl, proc_sym)

        # 3) prepara‑te para analisar o corpo
        prev_proc = getattr(self, 'current_procedure', None)
        self.current_procedure = nl

        # 4) abre escopo filho e define os parâmetros aí
        self.current_scope = Scope(self.current_scope)
        for param_nome, param_tipo in proc_sym.params:
            self.current_scope.define(param_nome, param_tipo)

        # 5) visita o bloco (corpo da procedure)
        self.visit(block)

        # 6) restaura escopo e current_procedure
        self.current_scope = self.current_scope.parent
        self.current_procedure = prev_proc
    


    def visit_not(self, node):
        _, expr = node
        expr_type = self.visit(expr)
        if expr_type != 'boolean':
            raise SemanticError(f"Operador 'not' espera expressão do tipo boolean, mas recebeu {expr_type}.")
        return 'boolean'



    def visit_goto(self, node):
        _, label = node
        key = str(label).lower()
        simbolo = self.current_scope.resolve(key)
        if simbolo is None or simbolo.type != 'label':
            raise SemanticError(f"GOTO para label '{label}' que não está declarada.")
    


    def visit_label_stmt(self, node):
        _, label, stmt = node
        key = str(label).lower()

        simbolo = self.current_scope.resolve(key)
        if simbolo is None or simbolo.type != 'label':
            raise SemanticError(f"Label '{label}' não declarada antes de ser usada.")

        self.visit(stmt)
    


    def visit_set_lit(self, node):
        _, elementos = node

        # se lista estiver vazia, considera um conjunto vazio genérico
        if not elementos:
            return ('set', 'unknown')

        # visita todos os elementos e verifica consistência de tipo
        tipos = [self.visit(elem) for elem in elementos]
        tipo_base = tipos[0]

        for t in tipos:
            if t != tipo_base:
                raise SemanticError(f"Todos os elementos do conjunto devem ter o mesmo tipo, mas encontrou {tipo_base} e {t}.")

        return ('set', tipo_base)
    


    def visit_fmt(self, node):
        _, expr, width_expr, precision_expr = node

        # 1) Analisa a expressão principal
        expr_type = self.visit(expr)

        # 2) Width deve ser integer
        width_type = self.visit(width_expr)
        if width_type.casefold() != 'integer':
            raise SemanticError(f"Formato width em '{node}' deve ser INTEGER, mas foi {width_type}.")

        # 3) Se houver precision, também deve ser integer
        if precision_expr is not None:
            prec_type = self.visit(precision_expr)
            if prec_type.casefold() != 'integer':
                raise SemanticError(f"Formato precision em '{node}' deve ser INTEGER, mas foi {prec_type}.")

        # 4) O resultado do fmt é do mesmo tipo da expr
        return expr_type