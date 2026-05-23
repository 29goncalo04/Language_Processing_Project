class SemanticError(Exception):
    pass


class Symbol:
    """
    Representa um símbolo na tabela de símbolos.

    Atributos:
        name (str): Nome do símbolo (identificador).
        type (str | Symbol): Tipo associado ao símbolo (ex: 'integer', 'boolean' ou outro símbolo).
        kind (str): Natureza do símbolo ('var' para variável, 'const' para constante).

    Este objeto é utilizado para armazenar informação semântica sobre identificadores
    declarados no programa, como variáveis, constantes, tipos ou procedimentos.
    """
    def __init__(self, name, type_, kind='var'):
        self.name = name
        self.type = type_
        self.kind = kind  # 'var' ou 'const'

    def __repr__(self):
        return f"<Symbol name={self.name}, type={self.type}, kind={self.kind}>"


class Scope:
    """
    Representa um scope de declaração, como um bloco de código ou função.
    Atributos:
        symbols (dict): Mapeamento entre nomes de identificadores e os seus símbolos.
        parent (Scope): Scope pai, permitindo encadeamento para suportar scopes aninhados.
    Métodos:
        define(name, type_, kind): Adiciona um novo símbolo ao scope atual.
        resolve(name): Procura um símbolo pelo nome, recursivamente nos scopes pai.
    Esta classe é usada para gerir tabelas de símbolos em programas com blocos aninhados,
    garantindo que declarações e utilizações de identificadores respeitam as regras
    de visibilidade e scope do Pascal ISO 7185.
    """
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    """
    Declara um novo símbolo no scope atual. Lança erro se já existir.
    Args:
        name (str): Nome do identificador.
        type_ (str | Symbol): Tipo associado ao símbolo.
        kind (str): 'var' ou 'const'.
    Raises:
        SemanticError: Se o nome já estiver declarado neste scope.
    """
    def define(self, name, type_, kind='var'):
        if name in self.symbols:
            raise SemanticError(f"Variável '{name}' já foi declarada neste scope.")
        if isinstance(type_, Symbol):
            sym = type_
            sym.name = name
            sym.kind = kind  # Define o tipo como 'var' ou 'const'
        else:
            sym = Symbol(name, type_, kind)
        self.symbols[name] = sym

    """
    Procura um símbolo com o nome dado, neste scope ou nos scopes pai.
    Args:
        name (str): Nome do identificador a procurar.
    Returns:
        Symbol: O símbolo correspondente.
    Raises:
        SemanticError: Se o nome não estiver declarado em nenhum scope acessível.
    """
    def resolve(self, name):
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.resolve(name)
        else:
            raise SemanticError(f"Variável '{name}' usada mas não declarada.")


class SemanticAnalyzer:
    """
    Analisador semântico para um programa Pascal (ISO 7185).
    Responsável por:
    - Gerir scopes e símbolos (variáveis, constantes, tipos, etc.).
    - Verificar inicialização e uso correto de variáveis.
    - Validar chamadas e tipos de funções e procedimentos.
    - Aplicar regras semânticas da linguagem Pascal.
    """
    def __init__(self):
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        # Conjunto de variáveis já inicializadas (para validações)
        self.initialized = set()
        self._init_builtins()
    
    def _init_builtins(self):
        """
        Inicializa procedimentos e funções builtin, como write e real().
        """
        for proc in ['write', 'writeln', 'read', 'readln']:
            self.global_scope.symbols[proc] = Symbol(proc, 'procedure')
        # Exemplo de função builtin: real(x: integer): real
        real_sym = Symbol('real', 'function')
        real_sym.params = [('x', 'integer')]  # Cast de integer para real
        real_sym.return_type = 'real'
        self.global_scope.define('real', real_sym)

    def analyze(self, node):
        """
        Ponto de entrada principal para análise semântica.
        Args:
            node (tuple): Nó da AST correspondente ao programa.
        """
        self.visit(node)

    def visit(self, node):
        """
        Despacha o nó para o método apropriado com base no nome do tipo.
        Args:
            node (tuple|list): Nó da AST (tupla com tag ou lista de nós).
        """
        if isinstance(node, tuple):
            method_name = f"visit_{node[0]}"
            method = getattr(self, method_name, self.generic_visit)
            return method(node)
        elif isinstance(node, list):
            for item in node:
                self.visit(item)

    def generic_visit(self, node):
        """
        Método chamado quando não existe implementação para um determinado tipo de nó.
        Raises:
            Exception: Indica que o nó ainda não tem verificação semântica implementada.
        """
        raise Exception(f"visit_{node[0]} não implementado")



    def visit_program(self, node):
        """
        Visita a estrutura principal de um programa Pascal.
        node = ('program', nome, bloco)
        """
        self.visit(node[2])  # Visita o bloco principal



    def visit_block(self, node):
        """
        Visita um bloco, que pode conter declarações e instruções compostas.
        node = ('block', declaracoes, corpo_composto)
        """
        _, decls, comp = node
        if decls:
            for decl in decls:
                self.visit(decl)  # Cada declaração será passada para o método correspondente
        self.visit(comp) # Trata o corpo (instruções) do bloco



    def visit_consts(self, node):
        # Extrai a lista de constantes da árvore sintática
        _, const_list = node
        for nome, expr in const_list:
            # Verifica se a constante já foi declarada no scope atual
            if nome.lower() in self.current_scope.symbols:
                raise SemanticError(f"Constante '{nome}' já declarada.")
            # Avalia a expressão associada à constante e obtém o tipo resultante
            tipo = self.visit(expr).lower()
            # Regista a constante na tabela de símbolos com o tipo e marca como 'const'
            self.current_scope.define(nome.lower(), tipo, kind='const')  # Marca como 'const'
            # Adiciona ao conjunto de identificadores inicializados (para gerir inicializações)
            self.initialized.add(nome.lower())
    


    def visit_types(self, node):
        # Extrai a lista de declarações de tipos
        _, type_list = node
        for name, tipo in type_list:
            kind = tipo[0].lower()
            # Processamento de tipos do tipo RECORD
            if kind == 'record':
                field_list = tipo[1]  # Lista de campos do record
                campos = {}   # Dicionário para armazenar os campos normalizados
                for _, nomes, campo_tipo_node in field_list:   # nodo ('fields', [nomes], tipo_node)
                    t_str = self._normalize_type(campo_tipo_node)
                    for id_name in nomes:
                        key = id_name.lower()
                        if key in campos:
                            raise SemanticError(f"Campo '{id_name}' já definido no record '{name}'.")
                        campos[key] = t_str
                # Cria símbolo para o tipo record, com os campos associados
                rec_sym = Symbol(name.lower(), name.lower())
                rec_sym.fields = campos
                self.current_scope.define(name.lower(), rec_sym)
            else:
                # Processamento de ENUMs
                if kind == 'enum':
                    self.current_scope.define(name.lower(), 'enum')
                    for e in tipo[1]:  # Elementos do enum
                        self.current_scope.define(e.lower(), 'enum')
                        self.initialized.add(e.lower())
                # Processamento de subranges (ex: 1..10)
                elif kind == 'subrange':
                    base_type = self._normalize_type(tipo)   # isto já retorna 'integer'
                    self.current_scope.define(name.lower(), base_type)
                # Processamento de arrays, packed arrays e outros
                else:
                    # Verifica se é um array com limites explícitos
                    if tipo[0].lower() == 'array_type':
                        lower_node, upper_node = tipo[1] 
                        # Garante que os limites são expressões constantes
                        if lower_node[0].lower() != 'const_expr':
                            raise SemanticError(f"Limite inferior do array deve ser constante, mas é {lower_node}")
                        if upper_node[0].lower() != 'const_expr':
                            raise SemanticError(f"Limite superior do array deve ser constante, mas é {upper_node}")
                        # Verifica os tipos dos limites e se são constantes
                        for bound in (lower_node, upper_node):
                            kind = bound[1].lower()
                            if kind == 'id':
                                name2 = bound[2].lower()
                                sym = self.current_scope.resolve(name2)
                                if sym.kind != 'const':
                                    raise SemanticError(
                                        f"Limite do array deve ser constante, mas '{bound[2]}' não é uma constante.")
                                if sym.type != 'integer':
                                     raise SemanticError(
                                         f"Limite do array deve ser do tipo INTEGER, mas '{name2}' é do tipo {sym.type}.")
                            elif kind != 'integer':
                                raise SemanticError(
                                    f"Limite do array deve ser do tipo INTEGER, mas é do tipo '{kind}'.")
                    # Verifica se é um packed array (estrutura compactada)
                    elif tipo[0].lower() == 'packed' and tipo[1][0].lower() == 'array_type':
                        lower_node, upper_node = tipo[1][1] 
                        # cada limite tem de ser const_expr
                        if lower_node[0].lower() != 'const_expr':
                            raise SemanticError(f"Limite inferior do array deve ser constante, mas é {lower_node}")
                        if upper_node[0].lower() != 'const_expr':
                            raise SemanticError(f"Limite superior do array deve ser constante, mas é {upper_node}")
                        # se for id, garante que é constante
                        for bound in (lower_node, upper_node):
                            kind = bound[1].lower()
                            if kind == 'id':
                                name2 = bound[2].lower()
                                sym = self.current_scope.resolve(name2)
                                if sym.kind != 'const':
                                    raise SemanticError(
                                        f"Limite do array deve ser constante, mas '{bound[2]}' não é uma constante.")
                                if sym.type != 'integer':
                                     raise SemanticError(
                                         f"Limite do array deve ser do tipo INTEGER, mas '{name2}' é do tipo {sym.type}.")
                            elif kind != 'integer':
                                raise SemanticError(
                                    f"Limite do array deve ser do tipo INTEGER, mas é do tipo '{kind}'.")
                    # Packed que envolve outro tipo (por exemplo, packed record)
                    elif tipo[0].lower() == 'packed':
                        self.visit(tipo[1])
                    # Outros tipos compostos
                    elif tipo[0].lower() not in ('simple_type', 'array_type', 'id_type'):
                        self.visit(tipo)
                    # Após verificação e processamento, regista o tipo no scope
                    type_str = self._normalize_type(tipo)
                    self.current_scope.define(name.lower(), type_str)



    def visit_labels(self, node):
        _, label_list = node

        for lbl in label_list:
            key = str(lbl).lower()
            # Verifica se já existe uma label com o mesmo nome no scope atual
            if key in self.current_scope.symbols:
                raise SemanticError(f"Label '{lbl}' já declarada neste scope.")
            # Regista a label como símbolo do tipo 'label' na tabela de símbolos
            self.current_scope.symbols[key] = Symbol(key, 'label')



    def visit_var_decl(self, node):
        # Recebe um nó com uma lista de declarações de variáveis
        _, decls = node
        for decl in decls:
            # Visita cada declaração individualmente (normalmente nós 'vars')
            self.visit(decl)

    def visit_vars(self, node):
        # Extrai nomes das variáveis e o tipo declarado
        _, nomes, tipo = node
        # Se for um tipo array, valida os limites do array
        if tipo[0].lower() == 'array_type':
            lower_node, upper_node = tipo[1] 
            # Garante que os limites inferior e superior são expressões constantes
            if lower_node[0].lower() != 'const_expr':
                raise SemanticError(f"Limite inferior do array deve ser constante, mas é {lower_node}")
            if upper_node[0].lower() != 'const_expr':
                raise SemanticError(f"Limite superior do array deve ser constante, mas é {upper_node}")
            # Valida o tipo dos limites (devem ser inteiros e constantes)
            for bound in (lower_node, upper_node):
                kind = bound[1].lower()
                if kind == 'id':
                    name = bound[2].lower()
                    sym = self.current_scope.resolve(name)
                    if sym.kind != 'const':
                        raise SemanticError(
                            f"Limite do array deve ser constante, mas '{bound[2]}' não é uma constante.")
                    if sym.type != 'integer':
                                     raise SemanticError(
                                         f"Limito de array deve ser do tipo INTEGER, mas '{name}' é do tipo {sym.type}.")
                elif kind != 'integer':
                    raise SemanticError(
                        f"Limite do array deve ser do tipo INTEGER, mas é do tipo '{kind}'.")
        # Normaliza o tipo da variável (transforma o nó da árvore num tipo como 'integer', 'real', etc.)
        type_str = self._normalize_type(tipo)
        for nome in nomes:
            # Impede que uma variável tenha o mesmo nome que uma constante
            if nome.lower() in self.current_scope.symbols and self.current_scope.symbols[nome.lower()].kind == 'const':
                raise SemanticError(f"Não pode declarar uma variável '{nome}' com o mesmo nome de uma constante.")
            # Se for um tipo packed complexo, garante que é processado
            if tipo[0].lower() == 'packed':
                if tipo[1][0].lower() not in ('simple_type', 'array_type', 'id_type'):
                    self.visit(tipo[1])
            elif tipo[0].lower() not in ('simple_type', 'array_type', 'id_type'):
                self.visit(tipo)
            # Regista a variável na tabela de símbolos com o tipo e marca como 'var'
            self.current_scope.define(nome.lower(), type_str, kind='var')



    def visit_function(self, node):
        # node = ('function', nome, params, return_type, block)
        _, nome, params, return_type, block = node
        nl = nome.lower()

        # 1) Verifica se a função já foi declarada no scope actual (pai)
        if nl in self.current_scope.symbols:
            raise SemanticError(f"A função '{nome}' já está definida.")

        # 2) Cria o símbolo da função e regista-o no scope actual
        func_sym = Symbol(nl, 'function')
        # Processa os parâmetros: extrai nomes e tipos normalizados
        lista = []
        if params != None:
            for p in params:                        # p = ('param',[nomes], tipo_node)
                _, nomes, tipo_node = p
                tipo_str = self._normalize_type(tipo_node)
                for id_name in nomes:
                    # Visita o tipo se for complexo (ex: record, subrange)
                    if p[2][0] not in ('simple_type', 'array_type', 'id_type'):
                        self.visit(p[2])
                    lista.append((id_name.lower(), tipo_str))
        func_sym.params = lista
        # Guarda o tipo de retorno, depois de normalizado
        func_sym.return_type = self._normalize_type(return_type)
        # Visita o tipo de retorno se for complexo
        if return_type[0] not in ('simple_type', 'array_type', 'id_type'):
            self.visit(return_type)

        # Regista a função na tabela de símbolos do scope actual
        self.current_scope.define(nl, func_sym)

        # 3) Prepara análise do corpo da função
        prev_fn = getattr(self, 'current_function', None)
        self.current_function = nl

        # Cria novo scope filho para os parâmetros e o corpo
        self.current_scope = Scope(self.current_scope)
        for param_nome, param_tipo in func_sym.params:
            self.current_scope.define(param_nome.lower(), param_tipo)
            self.initialized.add(param_nome.lower())   # Marca como inicializado

        # Analisa o bloco da função
        self.visit(block)

        # Fecha o scope e repõe a função anterior (caso haja)
        self.current_scope = self.current_scope.parent
        self.current_function = prev_fn
        # Devolve o tipo de retorno da função (útil para verificação posterior)
        return func_sym.return_type
    


    def visit_procedure(self, node):
        # node = ('procedure', nome, params, block)
        _, nome, params, block = node
        nl = nome.lower()

        # 1) Verifica se já existe uma procedure com esse nome
        if nl in self.current_scope.symbols:
            raise SemanticError(f"Procedimento '{nome}' já está definido neste scope.")

        # 2) Cria o símbolo da procedure
        proc_sym = Symbol(nl, 'procedure')

        # Extrai e valida os parâmetros, tal como em funções
        lista = []
        if params != None:
            for p in params:                  # p = ('param', [nomes], tipo_node)
                _, nomes, tipo_node = p
                # Valida limites se o parâmetro for um array
                if tipo_node[0].lower() == 'array_type':
                        lower_node, upper_node = tipo_node[1] 
                        # cada limite tem de ser const_expr
                        if lower_node[0].lower() != 'const_expr':
                            raise SemanticError(f"Limite inferior do array deve ser constante, mas é {lower_node}")
                        if upper_node[0].lower() != 'const_expr':
                            raise SemanticError(f"Limite superior do array deve ser constante, mas é {upper_node}")
                        # se for id, garante que é constante
                        for bound in (lower_node, upper_node):
                            kind = bound[1].lower()
                            if kind == 'id':
                                name2 = bound[2].lower()
                                sym = self.current_scope.resolve(name2)
                                if sym.kind != 'const':
                                    raise SemanticError(
                                        f"Limite do array deve ser constante, mas '{bound[2]}' não é uma constante.")
                                if sym.type != 'integer':
                                     raise SemanticError(
                                         f"Limite do array deve ser do tipo INTEGER, mas '{name2}' é do tipo {sym.type}.")
                            elif kind != 'integer':
                                raise SemanticError(
                                    f"Limite do array deve ser do tipo INTEGER, mas é do tipo '{kind}'.")
                tipo_str = self._normalize_type(tipo_node)
                for id_name in nomes:
                    if p[2][0] not in ('simple_type', 'array_type', 'id_type'):
                        self.visit(p[2])
                    lista.append((id_name.lower(), tipo_str))
        proc_sym.params = lista

        # Regista a procedure na tabela de símbolos
        self.current_scope.define(nl, proc_sym)

        # 3) Prepara análise do corpo do procedimento
        prev_proc = getattr(self, 'current_procedure', None)
        self.current_procedure = nl

        # 4) Abre novo scope e define os parâmetros como variáveis iniciais
        self.current_scope = Scope(self.current_scope)
        for param_nome, param_tipo in proc_sym.params:
            self.current_scope.define(param_nome, param_tipo)
            self.initialized.add(param_nome.lower())

        # 5) Analisa o bloco do procedimento
        self.visit(block)

        # 6) Fecha o scope e restaura o nome da procedure anterior (se aplicável)
        self.current_scope = self.current_scope.parent
        self.current_procedure = prev_proc
    


    def visit_record(self, node):
        _, field_list, variant_part = node

        # 1) Processa os campos fixos do record (ou seja, os campos normais, não variantes)
        fields_map = {}
        for _, nomes, tipo_ast in field_list:
            # Normalizar o tipo de cada campo
            campo_tipo = self._normalize_type(tipo_ast)
            for nome in nomes:
                key = nome.lower()
                if key in fields_map:
                    raise SemanticError(f"Campo '{nome}' duplicado em record.")
                fields_map[key] = campo_tipo

        # 2) Processa a parte variant (caso exista)
        variant_info = None
        if variant_part is not None:
            _, discrim_id, discrim_tipo_token, variant_list = variant_part

            # Verifica se o discriminador é um campo existente e se é de tipo ordinal
            key_disc = discrim_id.lower()
            if key_disc not in fields_map:
                raise SemanticError(f"Discriminador '{discrim_id}' não declarado como campo do record.")
            discrim_tipo = fields_map[key_disc]
            if discrim_tipo not in ('integer', 'char', 'boolean', 'enum'):
                raise SemanticError(
                    f"Tipo do discriminador '{discrim_id}' inválido para variant: {discrim_tipo} não é ordinal."
                )

            # Processa cada variante associada ao discriminador
            branches = []
            for const_list, inner_fields in variant_list:
                # Valida as constantes associadas a cada variante
                for const_node in const_list:
                    const_tipo = self.visit(const_node)
                    if const_tipo != discrim_tipo:
                        raise SemanticError(
                            f"Label de variant tem tipo {const_tipo}, mas discriminador é {discrim_tipo}."
                        )
                # Processa os campos dentro da variante
                inner_map = {}
                for _, nomes_i, tipo_ast_i in inner_fields:
                    itipo = self._normalize_type(tipo_ast_i)
                    for nome_i in nomes_i:
                        k = nome_i.lower()
                        if k in inner_map:
                            raise SemanticError(f"Campo '{nome_i}' duplicado na variante de {discrim_id}.")
                        inner_map[k] = itipo
                branches.append((const_list, inner_map))
            # Guarda a informação da variante
            variant_info = (discrim_id, discrim_tipo, branches)

        # 3) Devolve representação semântica do record
        return ('record', fields_map, variant_info)


    
    def visit_set(self, node):
        _, tipo_node = node
        # 1) Obter o tipo real da AST do type
        elem_type = None
        if isinstance(tipo_node, tuple):
            # Trata diferentes tipos de nó para o tipo de elemento do conjunto
            kind = tipo_node[0].lower()
            if kind == 'simple_type':
                elem_type = tipo_node[1].lower()
            elif kind == 'id_type':
                # resolve identificador de tipo previamente definido
                sym = self.current_scope.resolve(tipo_node[1].lower())
                elem_type = sym.type
            elif kind == 'enum':
                elem_type = 'enum'
            elif kind == 'subrange':
                lower_node = tipo_node[1] 
                upper_node = tipo_node[2]
                # Verifica se os limites são expressões constantes
                if lower_node[0].lower() != 'const_expr':
                    raise SemanticError(f"Limite inferior do array deve ser constante, mas é {lower_node}")
                if upper_node[0].lower() != 'const_expr':
                    raise SemanticError(f"Limite superior do array deve ser constante, mas é {upper_node}")
                # Se os limites forem identificadores, garante que sejam constantes
                for bound in (lower_node, upper_node):
                    kind = bound[1].lower()
                    if kind == 'id':
                        name2 = bound[2].lower()
                        sym = self.current_scope.resolve(name2)
                        if sym.kind != 'const':
                            raise SemanticError(
                                f"Limite do array deve ser constante, mas '{bound[2]}' não é uma constante.")
                        if sym.type != 'integer':
                             raise SemanticError(
                                 f"Limite do array deve ser do tipo INTEGER, mas '{name2}' é do tipo {sym.type}.")
                    elif kind != 'integer':
                        raise SemanticError(
                            f"Limite do array deve ser do tipo INTEGER, mas é do tipo '{kind}'.")
                elem_type = 'integer'
            else:
                raise SemanticError(
                    f"Tipos de conjuntos só suportam ordinal (integer, char, enum, subrange), "
                    f"mas receberam '{kind}'."
                )
        else:
            # tipo_node já está normalizado como string
            elem_type = tipo_node.lower()
        # 2) Verifica se o tipo do elemento do conjunto é ordinal (integer, char, enum, boolean)
        if elem_type not in ('integer', 'char', 'enum', 'boolean'):
            raise SemanticError(
                f"Tipo de elemento de conjunto inválido: {elem_type} não é ordinal."
            )
        # 3) Retorna a representação semântica do conjunto
        return ('set', elem_type)


        
    def visit_const_expr(self, node):
        # node = ('const_expr', type, b)
        _, type, b = node
        # Se o tipo for 'id', resolve o identificador
        if type == 'id':
            const_node = 'var', b.lower()
            # Visita o identificador e devolve o tipo associado
            return self.visit(const_node).lower()
        # Caso contrário, devolve diretamente o tipo
        return type



    def visit_compound(self, node):
        # node = ('compound', statement_list)
        _, stmts = node
        # Percorre cada instrução no bloco composto (statement_list)
        for stmt in stmts:
            # Se a instrução não for None (pode ser vazio no caso de regra de statement)
            if stmt is not None:
                self.visit(stmt)



    def visit_assign(self, node):
        # node = ('assign', var_node, expr)
        _, var_node, expr = node
        nome_var = var_node[1]

        # Caso de retorno dentro de função
        if not isinstance(nome_var, tuple):
            nome_var = nome_var.lower()
            if nome_var == getattr(self, 'current_function', None):
                # Se for o retorno, verifica tipo de retorno
                expr_type = self.visit(expr).lower()
                # Busca símbolo da função no scope global (onde definimos return_type)
                func_sym = self.global_scope.resolve(nome_var.lower())
                ret_type = func_sym.return_type.lower()
                if expr_type != ret_type:
                    raise SemanticError(
                        f"Tipo de retorno incorreto em '{var_node[1]}': "
                        f"esperado {ret_type}, mas foi {expr_type}."
                    )
                return

        # atribuição normal a variável
        if var_node[0] == 'var':
            # Verifica se a variável é constante e não pode ser alterada
            if nome_var in self.current_scope.symbols:
                if self.current_scope.symbols[nome_var].kind == 'const':
                    raise SemanticError(f"Não pode atribuir a constante '{nome_var}'")
                var_type = self.current_scope.symbols[nome_var].type
            else:
                # Se não encontrar no scope local, tenta no scope global
                if nome_var in self.global_scope.symbols:
                    var_type = self.global_scope.symbols[nome_var].type
                else:
                    raise SemanticError(f"Variável '{nome_var}' não declarada.")

        else:
            # Caso não seja variável, resolve tipo usando visit
            var_type = self.visit(var_node)
        # Verifica se o tipo da expressão é compatível com o tipo da variável
        expr_type = self.visit(expr)
        if isinstance(expr_type, tuple):
            expr_type = expr_type[0]
        if expr_type.upper() != var_type.upper():
            raise SemanticError(
                f"Tipos incompatíveis na atribuição: variável '{var_node}' é {var_type}, "
                f"mas expressão é {expr_type}."
            )
        # Se a variável for normal (não const), marca como inicializada
        if var_node[0] == 'var':
            self.initialized.add(var_node[1].lower())



    def visit_var(self, node):
        # node = ('var', nome)
        _, nome = node
        key = nome.lower()
        # se ainda não foi inicializada, erro
        if key not in self.initialized:
            raise SemanticError(f"Variável '{nome}' usada antes de inicialização.")

        # Se a variável foi inicializada, resolve e retorna o tipo
        sym = self.current_scope.resolve(key)
        return sym.type
    


    def visit_array(self, node):
        _, base, indice = node
        key = base[1].lower()
        # Resolve o tipo da variável base (deve ser um array)
        base_type = self.current_scope.resolve(key).type
        # Verifica se a base é um array
        if not (isinstance(base_type, tuple) and base_type[0] == 'array'):
            raise SemanticError(f"Tentativa de indexar uma variável que não é um array, mas do tipo '{base_type}'")
        idx_type = self.visit(indice)
        # Verifica o tipo do índice (deve ser 'integer')
        if idx_type != 'integer':
            raise SemanticError(f"Índice do array deve ser INTEGER, mas é do tipo {idx_type}.")
        return base_type[1]  # tipo do elemento do array
    


    def visit_field(self, node):
        _, base_node, field_name = node
        # Se a base é uma variável, resolve o tipo diretamente, caso contrário, processa a expressão
        if base_node[0] == 'var':
            base_type = self.current_scope.resolve(base_node[1].lower()).type
        else:    
            base_type = self.visit(base_node)
        # Resolve o símbolo do tipo base
        type_sym = self.current_scope.resolve(base_type)
        # Verifica se o tipo tem campos (ou seja, é uma estrutura ou tipo com campos)
        if not hasattr(type_sym, 'fields'):
            raise SemanticError(f"Tentativa de aceder campo '{field_name}' de ({base_type}).")
        # Verifica se o campo existe no tipo
        key = field_name.lower()
        if key not in type_sym.fields:
            raise SemanticError(f"Campo '{field_name}' não existe em '{base_type}'.")
        # Retorna o tipo do campo
        return type_sym.fields[key]



    def visit_call(self, node):
        _, nome, argumentos = node
        nl = nome.lower()

        # Tenta resolver o símbolo da função no scope atual
        sym = None
        try:
            sym = self.current_scope.resolve(nl)
        except SemanticError:
            pass
        # Se for um cast
        if sym is not None \
           and not hasattr(sym, 'params') \
           and not hasattr(sym, 'return_type') \
           and sym.type.lower() == nl:
            if len(argumentos) != 1:
                raise SemanticError(f"Cast para '{nome}' espera 1 argumento, mas recebeu {len(argumentos)}.")
            # Valida o tipo do argumento no cast
            t = self.visit(argumentos[0])
            return nl   # Retorna o tipo do cast

        # —————— CAST PARA REAL ——————
        if nl == 'real':
            if len(argumentos) != 1:
                raise SemanticError(f"Cast para '{nome}' espera 1 argumento, mas recebeu {len(argumentos)}.")
            at = self.visit(argumentos[0])
            # Valida se o tipo do argumento pode ser convertido
            if nl == 'real' and at not in ('integer','real'):
                raise SemanticError(f"Cast real({at}) inválido; só integer ou real.")
            return nl   # Retorna o tipo do cast
        # Verifica a chamada da função   
        simbolo = self.current_scope.resolve(nl)
        if hasattr(simbolo, 'params'):
            if len(argumentos) != len(simbolo.params):
                raise SemanticError(f"'{nome}' espera {len(simbolo.params)} argumentos, mas recebeu {len(argumentos)}.")
            # Valida os tipos dos argumentos
            for (pname, ptype), a in zip(simbolo.params, argumentos):
                if a[0] != 'var':
                    at = self.visit(a)
                else:
                    at = self.current_scope.resolve(a[1].lower()).type
                if at != ptype:
                    if not ((ptype=='real' and at=='integer') or (ptype=='texto' and at==('array', 'char')) or (ptype==('array', 'char') and at=='texto')):
                        raise SemanticError(f"Argumento para '{pname}' deve ser {ptype}, mas recebeu {at}.")
            # Retorna o tipo de retorno da função, se definido
            if hasattr(simbolo, 'return_type'):
                return simbolo.return_type.casefold()
            return None

        # 5) Built‑in simples (write, writeln, read, readln)
        for a in argumentos:
            if simbolo.name in ('read', 'readln'):
                # Aqui, 'a' pode ser uma variável ou um array.
                if isinstance(a, tuple):
                    tipo = a[0]  # Tipo pode ser 'var' ou 'array'

                    if tipo == 'var':
                        # Caso seja uma variável simples
                        _, nome = a  # Espera-se que 'a' seja uma tupla do tipo ('var', 'nome')
                        key = nome.lower()
                        sym = self.current_scope.resolve(key)
                        if sym.type[0] != ('array'):
                            self.initialized.add(key)
                            return sym.type
                        else:
                            raise SemanticError(f"A função '{simbolo.name}' não pode receber um argumento do tipo '{sym.type[0]}'.")

                    elif tipo == 'array':
                        # Caso seja um array, o segundo elemento é uma tupla com a variável
                        _, nome = a[1]  # 'a[1]' será a tupla ('var', 'nome_do_array')
                        key = nome.lower()
                        sym = self.current_scope.resolve(key)
                        self.initialized.add(key)

                        # Verificar se há um terceiro elemento que representa os índices
                        if len(a) > 2:  # Caso haja índices
                            index = a[2]  # Os índices estão em 'a[2]'
                            index_type = self.visit(index)  # Processa o índice
                            if index_type != 'integer':
                                raise SemanticError(f"O índice do array tem de ser do tipo INTEGER mas é do tipo '{index_type}'.")
                        return sym.type  # Retorna o tipo da variável do tipo array
                    elif tipo == 'field':
                        self.visit_field(a[1])
                    else:
                        raise SemanticError(f"A função '{simbolo.name}' não pode receber um argumento do tipo '{tipo}'.")

                else:
                    # Se 'a' não for uma tupla, apenas visita o argumento
                    self.current_scope.resolve(a[1].lower()).type
            if nl in ('write', 'writeln'):
                for a in argumentos:
                    if a[0] != 'var':
                        self.visit(a)
                    else:
                        key = a[1].lower()
                        sym = self.current_scope.resolve(key)
                        if sym.type not in ('boolean', 'char', 'integer', 'real'):
                            raise SemanticError(f"A função '{nl}' não pode receber um argumento do tipo '{sym.type}'.")
                return None

    

    def visit_if(self, node):
        _, cond, then_stmt, else_stmt = node
        # Verifica o tipo da condição do IF (deve ser boolean)
        cond_type = self.visit(cond)
        if cond_type != 'boolean':
            raise SemanticError(f"A condição do IF deve ser boolean, mas é {cond_type}.")
        # Processa a parte 'then' da instrução
        self.visit(then_stmt)
        if else_stmt is not None:
            # Se existir, processa a parte 'else'
            self.visit(else_stmt)



    def visit_for(self, node):
        # node = ('for', loop_var_name, start_expr, end_expr, direction, body_stmt)
        _, var_name, start_expr, end_expr, _, body = node

        # 1) A variável de controlo do loop deve ser definida e ser do tipo 'integer'
        sym = self.current_scope.resolve(var_name.lower())
        if sym.type.lower() != 'integer'.lower():
            raise SemanticError(
                f"Variável de controlo do FOR '{var_name}' deve ser integer, mas é {sym.type}."
            )

        # 2) A expressão de início e a expressão de fim do loop devem ser do tipo 'integer'
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
        # Marca a variável de controlo como inicializada
        self.initialized.add(var_name.lower())
        # 3) Processa o corpo do laço 'for'
        self.visit(body)



    def visit_while(self, node):
        # node = ('while', condition_expr, body_stmt)
        _, cond_expr, body = node
        # 1) A condição do 'while' deve ser do tipo 'boolean'
        cond_type = self.visit(cond_expr)
        if cond_type != 'boolean':
            raise SemanticError(
                f"Condição de WHILE deve ser boolean, mas é {cond_type}."
            )
        # 2) Analisa o corpo do laço 'while'
        self.visit(body)



    def visit_repeat(self, node):
        # node = ('repeat', statement_list, expression)
        _, stmts, cond = node
        # 1) Analisa cada instrução dentro do 'repeat...until'
        for stmt in stmts:
            if stmt is not None:
                self.visit(stmt)
        # 2) A condição do 'until' deve ser do tipo 'boolean'
        cond_type = self.visit(cond)
        if cond_type.lower() != 'boolean':
            raise SemanticError(
                f"Condição de REPEAT…UNTIL deve ser boolean, mas é {cond_type}."
            )
        


    def visit_case(self, node):
        _, expr_node, case_list = node
        # 1) A expressão do 'case' deve ser do tipo ordinal: 'integer', 'char' ou 'enum'
        expr_type = self.visit(expr_node).lower()
        if expr_type not in ('integer', 'char', 'enum'):
            raise SemanticError(
                f"Expressão de CASE deve ser ordinal (INTEGER, CHAR ou ENUM), mas é {expr_type}."
            )
        # 2) Percorre todas as alternativas do 'case' e valida os tipos das constantes
        seen_labels = set()
        for const_list, stmts in case_list:
            # Cada 'const_list' é uma lista de nós de expressões constantes
            for const_node in const_list:
                label_type = self.visit(const_node).lower()
                if label_type != expr_type:
                    raise SemanticError(
                        f"Label de CASE tem tipo {label_type}, mas a expressão é {expr_type}."
                    )
                # Identifica a constante para detetar duplicados (usa o nó como chave)
                key = repr(const_node)
                if key in seen_labels:
                    raise SemanticError(f"Label de CASE repetida: {const_node}.")
                seen_labels.add(key)

            # 3) Analisa semanticamente todas as instruções dentro do ramo do 'case'
            for stmt in stmts:
                self.visit(stmt)



    def visit_with(self, node):
        _, var_list, stmt = node

        # 1) Prepara um novo scope filho onde vamos introduzir os campos
        old_scope = self.current_scope
        with_scope = Scope(parent=old_scope)

        # 2) Para cada variável em WITH, extrai os campos do seu tipo record
        for var_node in var_list:
            # Só são suportadas variáveis simples (não suportamos, por exemplo, variáveis do tipo 'array' ou 'pointer')
            if var_node[0].lower() != 'var':
                raise SemanticError(f"WITH só suporta variáveis simples, mas recebeu {var_node[0]!r}.")
            var_name = var_node[1].lower()

            # resolve a variável no scope anterior
            sym = old_scope.resolve(var_name)
            # Obtém o nome do tipo da variável, que deve ser um 'record' definido anteriormente
            type_name = sym.type.lower()
            type_sym = old_scope.resolve(type_name)

            # Valida que o tipo da variável é efetivamente um 'record'
            if not hasattr(type_sym, 'fields'):
                raise SemanticError(
                    f"Variável '{var_node[1]}' em WITH não é um record, mas é do tipo '{sym.type}'."
                )

            # Define cada campo do record no scope atual do 'WITH'
            for field_name, field_type in type_sym.fields.items():
                # Os nomes dos campos já estão em minúsculas na definição de 'fields'
                with_scope.define(field_name,
                                  field_type,
                                  kind='var')

        # 3) Passa a usar o scope alargado dentro do bloco 'WITH'
        self.current_scope = with_scope

        # 4) Analisa semanticamente o statement interno dentro do 'WITH'
        self.visit(stmt)

        # 5) Restaura o scope anterior após o fim do bloco 'WITH'
        self.current_scope = old_scope



    def visit_goto(self, node):
        _, label = node
        key = str(label).lower()
        # Resolve o símbolo associado ao rótulo (label) no scope atual
        simbolo = self.current_scope.resolve(key)
        # Verifica se o rótulo está presente no scope e se é do tipo 'label'
        if simbolo is None or simbolo.type != 'label':
            raise SemanticError(f"GOTO para label '{label}' que não está declarada.")
        


    def visit_label_stmt(self, node):
        _, label, stmt = node
        key = str(label).lower()
        # Resolve o símbolo associado ao rótulo (label) no scope atual
        simbolo = self.current_scope.resolve(key)
        # Verifica se o rótulo está declarado antes de ser usado
        if simbolo is None or simbolo.type != 'label':
            raise SemanticError(f"Label '{label}' não declarada antes de ser usada.")
        # Analisa semanticamente a instrução associada ao rótulo
        self.visit(stmt)



    def visit_const(self, node):
        _, type, _ = node
        # A função visita o nó de uma constante e retorna o tipo da constante
        return type

        

    def visit_fmt(self, node):
        _, expr, width_expr, precision_expr = node
        # 1) Analisa a expressão principal (o valor a ser formatado)
        expr_type = self.visit(expr)
        # 2) A largura (width) deve ser do tipo 'integer'
        width_type = self.visit(width_expr)
        if width_type.casefold() != 'integer':
            raise SemanticError(f"Formato width em '{node}' deve ser INTEGER, mas foi {width_type}.")
        # 3) Se a precisão (precision) for fornecida, também deve ser do tipo 'integer'
        if precision_expr is not None:
            prec_type = self.visit(precision_expr)
            if prec_type.casefold() != 'integer':
                raise SemanticError(f"Formato precision em '{node}' deve ser INTEGER, mas foi {prec_type}.")
        # 4) O tipo do resultado do formato (fmt) é o mesmo tipo da expressão analisada
        return expr_type
    


    def visit_not(self, node):
        _, expr = node
        # Analisa o tipo da expressão após o operador 'not'
        expr_type = self.visit(expr)
        # Analisa o tipo da expressão após o operador 'not'
        if expr_type != 'boolean':
            raise SemanticError(f"Operador 'not' espera expressão do tipo boolean, mas é do tipo {expr_type}.")
        # O resultado do operador 'not' também é do tipo 'boolean'
        return 'boolean'
    


    def visit_set_lit(self, node):
        _, elementos = node
        # Se a lista de elementos estiver vazia, considera um conjunto vazio genérico
        if not elementos:
            return ('set', 'unknown')
        # Analisa todos os elementos e verifica se são consistentes em termos de tipo
        tipos = [self.visit(elem) for elem in elementos]
        tipo_base = tipos[0]
        # Verifica se todos os elementos têm o mesmo tipo
        for t in tipos:
            if t != tipo_base:
                raise SemanticError(f"Todos os elementos do conjunto devem ter o mesmo tipo, mas encontrou {tipo_base} e {t}.")
        # Retorna o tipo do conjunto e o tipo base dos seus elementos
        return ('set', tipo_base)
    


    def visit_binop(self, node):
        _, op, esq, dir_ = node
        op = op.lower()
        # Analisa os tipos das expressões à esquerda (esq) e à direita (dir_) do operador
        tipo_esq = self.visit(esq)
        tipo_dir = self.visit(dir_)
    
        # Função auxiliar para obter o nome base do tipo
        def tipo_base(t):
            return t.lower() if isinstance(t, str) else t[0].lower()
    
        base_esq = tipo_base(tipo_esq)
        base_dir = tipo_base(tipo_dir)
    
        # Operadores aritméticos (+, -, *, /)
        if op in ['+', '-', '*', '/']:
            if base_esq not in ['integer', 'real'] or base_dir not in ['integer', 'real']:
                raise SemanticError(f"Operador '{op}' só pode ser aplicado a tipos numéricos, mas recebeu {tipo_esq} e {tipo_dir}.")
            # Se algum dos operandos for 'real' ou o operador for '/', o resultado será 'real'
            if 'real' in [base_esq, base_dir] or op == '/':
                return 'real'
            return 'integer'
    
        # Operadores div e mod (divisão inteira e módulo)
        if op in ['div', 'mod']:
            if base_esq != 'integer' or base_dir != 'integer':
                raise SemanticError(f"Operador '{op}' requer dois inteiros, mas recebeu {tipo_esq} e {tipo_dir}.")
            return 'integer'
    
        # Operadores relacionais (=, <>)
        if op in ['=', '<>']:
            if {base_esq, base_dir} <= {'integer', 'real'}:
                return 'boolean'
            if tipo_esq != tipo_dir:
                raise SemanticError(f"Comparação '{op}' requer operandos compatíveis, mas recebeu {tipo_esq} e {tipo_dir}.")
            if base_esq not in ['boolean', 'char', 'texto', 'set']:
                raise SemanticError(f"Operador '{op}' não suportado para tipo {tipo_esq}.")
            return 'boolean'
    
        # Operadores relacionais (<, <=, >, >=)
        elif op in ['<', '<=', '>', '>=']:
            if base_esq == base_dir and base_esq in ['integer','real','char','texto']:
                return 'boolean'
            raise SemanticError(
                f"Operador relacional '{op}' não suportado para tipos {tipo_esq} e {tipo_dir}."
            )
    
        # Operador IN (verifica se o elemento pertence a um conjunto)
        if op == 'in':
            if tipo_dir == 'set':
                elem_type = tipo_dir.lower()
                if tipo_esq != 'enum':
                    raise SemanticError(f"Elemento do tipo {tipo_esq} não compatível com o conjunto de {elem_type}.")
            else:
                if not (isinstance(tipo_dir, tuple)):
                    raise SemanticError(
                        f"Operador 'in' requer um conjunto do lado direito, mas recebeu {tipo_dir}."
                    )
                # Extrai o tipo dos elementos do conjunto e compara com o tipo do operando à esquerda
                elem_type = tipo_dir[1]
                if tipo_esq != elem_type:
                    raise SemanticError(
                        f"Elemento do tipo {tipo_esq} não compatível com o conjunto de {elem_type}."
                    )
            return 'boolean'
    
        # Operadores lógicos (and, or)
        if op in ['and', 'or']:
            if base_esq != 'boolean' or base_dir != 'boolean':
                raise SemanticError(f"Operador lógico '{op}' requer dois boolean, mas recebeu {tipo_esq} e {tipo_dir}.")
            return 'boolean'
        # Se o operador não for reconhecido ou a operação não for suportada entre os tipos
        raise SemanticError(f"Operador desconhecido '{op}' ou operação não suportada entre {tipo_esq} e {tipo_dir}.")
    


    def _normalize_type(self, tipo_node):
        kind = tipo_node[0].lower()
        # Caso o tipo seja um tipo simples, retorna o tipo simples
        if kind == 'simple_type':
            return tipo_node[1].lower()
        # Caso o tipo seja identificado por um nome (ID), resolve o tipo associado ao identificador
        if kind == 'id_type':
            sym = self.current_scope.resolve(tipo_node[1].lower())
            return sym.type
        # Caso o tipo seja um tipo de array, normaliza o tipo do elemento do array
        if kind == 'array_type':
            elem_type = self._normalize_type(tipo_node[2])
            return ('array', elem_type)
        # Caso o tipo seja um 'enum', retorna 'ENUM'
        if kind == 'enum':
            return 'ENUM'.lower()
        # Caso o tipo seja um subintervalo (subrange), considera como 'integer'
        if kind == 'subrange':
            return 'integer'.lower()
        # Caso o tipo seja 'packed', normaliza o tipo do conteúdo
        if kind == 'packed':
            return self._normalize_type(tipo_node[1])
        # Caso o tipo seja uma short_string, é considerado como 'texto'
        if kind == 'short_string':
            return 'texto'.lower()
        # Caso o tipo seja 'set', é considerado como 'SET'
        if kind == 'set':
            return 'SET'.lower()
        # Caso o tipo seja 'file', é considerado como 'FILE'
        if kind == 'file':
            return 'FILE'.lower()
        # Caso o tipo seja um 'record', é considerado como 'RECORD'
        if kind == 'record':
            return 'RECORD'.lower()
        


    

    # def visit_instrucao_composta(self, node):
    #     _, instrs = node
    #     for instr in instrs:
    #         self.visit(instr)

    # def visit_numero(self, node):
    #     _, valor = node
    #     return 'real' if '.' in str(valor) else 'integer'    