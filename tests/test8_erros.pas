{exemplo 8 inventado mas com erros semânticos}
program TesteCompleto;

const
  PI       = 3.14159;
  MaxN     = 10;
  FlagTrue = True;

type
  SmallInt = 1..100;
  {Erro semântico: variável 'Max' não declarada}
  TArray1  = array[1..Max] of Integer;

label
  {Erro semântico: tenta ir para o 10 no fim do ficheiro mas label é 1}
  1;

var
  i, j : SmallInt;
  a1   : TArray1;
  {Erro semântico: tipo 'Bool' não declarado}
  ok   : Bool;


{Erro semântico: tipo 'T' não declarado}
procedure PreencheArray(var A: T; N: SmallInt);
var k: SmallInt;
begin
  for k := 1 to N do
    {Erro semântico: k/1 dá real mas 'div' espera integer}
    A[k] := k/1 div 2 + k mod 2;
end;

function SomaArray(const A: TArray1; N: SmallInt): Integer;
var idx, total: Integer;
begin
  total := 0;
  for idx := 0 to N do
    {Erro semântico: índice do array deve ser do tipo 'integer'}
    total := total + A['idx'];
  j := 1;
  {Erro semântico: tipo de retorno da função deveria ser 'integer'}
  SomaArray := 'j';
end;

begin
  PreencheArray(a1, 20);
  {Erro semântico: o primeiro argumento da função 'SomaArray' deveria ser do tipo 'TArray1'}
  writeln('Soma = ', SomaArray('a1', MaxN));

  ok := 2;  {Erro semântico: atribuição de inteiro a uma variável booleana}

  {Erro semântico: condição do IF não pode ser um integer}
  if 1 then
    {Erro semântico: label foi criado com '1'}
    goto 2;
{Erro semântico: tenta ir para o 10 mas a label é 1}
10: writeln('Fim do teste.');
end.