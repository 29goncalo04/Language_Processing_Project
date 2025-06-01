{exemplo 12 inventado}
program PerfeitosAteN;
var
  n, i, j, soma: integer;
begin
  writeln('Introduz um inteiro n: ');
  readln(n);
  for i := 1 to n do
  begin
    soma := 0;
    j := 1;
    while j <= i div 2 do
    begin
      if i mod j = 0 then
        soma := soma + j;
      j := j + 1
    end;
    if soma = i then
      writeln(i, ' é perfeito')
  end
end.