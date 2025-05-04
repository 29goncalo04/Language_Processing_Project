import sys
import os
from lexico import build_lexer

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

    lexer = build_lexer()
    lexer.input(codigo)

    for token in lexer:
        print(f"{token.type}({token.value}) na linha {token.lineno}")

if __name__ == "__main__":
    main()