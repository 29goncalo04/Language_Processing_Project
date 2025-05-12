{exemplo 6 inventado (não é do enunciado porque não dava para separar a string lida pelos vários caracteres)}
program SomaQuadradosParesAteN;

type
  PosInt = integer;

const
  SOMA_INICIAL = 0;

var
  n: PosInt;
  i: PosInt;
  soma: PosInt;

begin
  writeln('Insere um número inteiro positivo:');
  read(n);

  while n <= 0 do
  begin
    writeln('O número tem de ser positivo. Tenta novamente:');
    read(n);
  end;

  soma := SOMA_INICIAL;

  for i := 1 to n do
  begin
    if (i mod 2 = 0) then
    begin
      soma := soma + i * i;
    end;
  end;

  writeln('A soma dos quadrados dos números pares até ', n, ' é: ', soma);
end.