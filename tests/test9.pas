program TesteCompleto;

{ secção CONST }
const
  PI       = 3.14159;
  MaxN     = 10;
  FlagTrue = True;

{ secção TYPE }
type
  SmallInt = 1..100;
  TArray1  = array[1..MaxN] of Integer;

{ secção LABEL }
label
  10;

{ secção VAR }
var
  i, j : SmallInt;
  a1   : TArray1;
  ok   : Boolean;


{ definição de subprogramas: devem vir ANTES do begin principal }

procedure PreencheArray(var A: TArray1; N: SmallInt);
var k: SmallInt;
begin
  for k := 1 to N do
    A[k] := k div 2 + k mod 2;
end;    { ← termina com ponto‑e‑vírgula }

function SomaArray(const A: TArray1; N: SmallInt): Integer;
var idx, total: Integer;
begin
  total := 0;
  for idx := 1 to N do
    total := total + A[idx];
  SomaArray := total;
end;    { ← termina com ponto‑e‑vírgula }

{ corpo principal }
begin
  PreencheArray(a1, MaxN);
  writeln('Soma = ', SomaArray(a1, MaxN));

  ok := False;
  if not ok then
    goto 10;
10: writeln('Fim do teste.');
end.