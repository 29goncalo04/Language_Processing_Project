{exemplo 10 inventado}
program ClassificarNumero;

var
  n: integer;

begin
  write('Introduz um inteiro: ');
  readln(n);

  if n < 0 then
    writeln('Negativo')
  else
    if n = 0 then
      writeln('Zero')
    else
      writeln('Positivo');
end.