{exemplo 6 mas com erros semânticos}
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
  read(i);  

  while n <= 0 do  (*Erro semântico: variável 'n' não inicializada*)
  begin
    writeln('O número tem de ser positivo. Tenta novamente:');
    read(n);
  end;

  soma := 0.0;  
  (* ERRO SEMÂNTICO: soma é do tipo inteiro (PosInt), mas está a ser atribuído um real (0.0).*)

  for i := 1 to n do
  begin
    if (i mod 2 = z) then  (*Erro semântico: variável 'z' não inicializada*)
    begin
      soma := soma + i * i;
    end;
  end;

  writeln('A soma dos quadrados dos números pares até ', n, ' é: ', soma);
end.