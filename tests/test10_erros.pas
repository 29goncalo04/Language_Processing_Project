{exemplo 10 inventado mas com erros semânticos}
program ClassificarNumero;

var
  n: boolean; { Erro semântico: variável 'n' declarada como BOOLEAN, mas usada em operações numéricas }

begin
  write('Introduz um inteiro: ');
  readln(x); { Erro semântico: identificador 'x' não declarado }

  if n < 0 then { Erro semântico: tentativa de comparar BOOLEAN com INTEGER }
    writeln('Negativo')
  else
    if n = 0 then { Erro semântico: tentativa de comparar BOOLEAN com INTEGER }
      writeln('Zero')
    else
      writeln('Positivo');
end.