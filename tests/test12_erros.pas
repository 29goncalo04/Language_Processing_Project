{exemplo 12 inventado mas com erros semânticos}
program PerfeitosAteN;
var
  n, i, j: integer;
  soma: boolean; { Erro semântico: 'soma' declarada como BOOLEAN, mas usada como INTEGER }
begin
  writeln('Introduz um inteiro n: ');
  readln(x); { Erro semântico: identificador 'x' não declarado }
  for i := 1 to n do
  begin
    soma := 0; { Erro semântico: atribuição de INTEGER a 'soma' (BOOLEAN) }
    j := 1;
    while j <= i div 2 do
    begin
      if i mod j = 0 then
        soma := soma + j; { Erro semântico: soma (BOOLEAN) + j (INTEGER)}
      j := j + 1
    end;
    if soma = i then    { Erro semântico: comparação de BOOLEAN ('soma') com INTEGER ('i') }
      writeln(i, ' é perfeito')
  end
end.