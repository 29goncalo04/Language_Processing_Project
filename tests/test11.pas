{exemplo 11 criado}
program PrimosAteN;
var
  n, i, j: integer;
  primo: boolean;
begin
  writeln('Introduz um inteiro n: ');
  readln(n);
  for i := 2 to n do
  begin
    primo := true;
    for j := 2 to i-1 do
      if i mod j = 0 then
        primo := false;
    if primo then
      writeln(i);
  end
end.