{exemplo 11 inventado mas com erros semânticos}
program PrimosAteN;
var
  n, i, j: integer;
  primo: integer; {Erro semântico: 'primo' declarado como INTEGER, mas usado como BOOLEAN abaixo}
begin
  writeln('Introduz um inteiro n: ' );
  readln(x); {Erro semântico: identificador 'x' não declarado}
  for i := 2 to n do
  begin
    primo := true; {Erro semântico: atribuição de BOOLEAN a 'primo' (INTEGER)}
    for j := 2 to i-1 do
      if i mod j = 0 then
        primo := false; {Erro semântico: atribuição de BOOLEAN a 'primo' (INTEGER)}
    if primo then    {Erro semântico: uso de 'primo' (INTEGER) numa expressão boolean}
      writeln(i);
  end
end.