import sys
import os
from ana_sin import parse
from ana_sem import*
from gerador_codigo import CodeGenerator

from pprint import PrettyPrinter

def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py <nome do ficheiro_pascal>")
        sys.exit(1)

    nome_ficheiro = sys.argv[1]
    caminho_ficheiro = f"./tests/{nome_ficheiro}"

    if not os.path.isfile(caminho_ficheiro):
        print(f"Erro: o ficheiro '{caminho_ficheiro}' não existe.")
        sys.exit(1)

    with open(caminho_ficheiro, 'r', encoding='utf-8') as f:
        codigo = f.read()

    # Cria lexer
    # lexer = build_lexer()
    # lexer.input(codigo)

    # for token in lexer:
    #     print(f"{token.type}({token.value}) na linha {token.lineno}")

    try:
        result = parse(codigo)
        # pp = PrettyPrinter(width=80, indent=4)
        # pp.pprint(result)
        if result!=None:
            analyzer = SemanticAnalyzer()
            analyzer.analyze(result)
            gen = CodeGenerator()
            gen.build_symtab(result)
            gen.gen(result)
            out = caminho_ficheiro.rsplit('.', 1)[0] + '.vm'
            gen.write(out)
            print(f"Código gerado em: {out}")
    except SemanticError as e:
        print(e)


if __name__ == "__main__":
    main()