program ComplexExamplePure;

const
  MAXPESSOAS = 5;
  MAXLIST = 5;

type
  TScore = 0..100;

  TDayOfWeek = (Segunda, Terca, Quarta, Quinta, Sexta, Sabado, Domingo);

  TCharSet = set of Char;

  TPessoa = record
    Nome: char[50];
    Idade: 1..120;
    Pontuacao: TScore;
    DiaFavorito: TDayOfWeek;
  end;

  TIntArray = array[1..MAXLIST] of Integer;

  TMatrix = array[1..3, 1..3] of Real;

  TPessoaFile = file of TPessoa;

var
  Pessoas: array[1..MAXPESSOAS] of TPessoa;
  Lista: TIntArray;
  LenList: Integer;
  M: TMatrix;
  i: Integer;

function Factorial(n: Integer): LongInt;
begin
  if n <= 1 then
    Factorial := 1
  else
    Factorial := n * Factorial(n - 1);
end;

function Fibonacci(n: Integer): LongInt;
begin
  if n in [0,1] then
    Fibonacci := n
  else
    Fibonacci := Fibonacci(n - 1) + Fibonacci(n - 2);
end;

procedure InitArrayList(var A: TIntArray; var Len: Integer; m: Integer);
var
  k: Integer;
begin
  if m > MAXLIST then
    Len := MAXLIST
  else
    Len := m;
  for k := 1 to Len do
    A[k] := k;
end;

procedure PrintArrayList(const A: TIntArray; Len: Integer);
var
  idx: Integer;
begin
  for idx := 1 to Len do
    Write(A[idx], ' ');
  Writeln;
end;

procedure PrintMatrix(const A: TMatrix);
var
  r, c: Integer;
begin
  for r := 1 to 3 do
  begin
    for c := 1 to 3 do
      Write(A[r,c]:8:2);
    Writeln;
  end;
end;

procedure InitMatrix(var A: TMatrix);
var
  r, c: Integer;
begin
  for r := 1 to 3 do
    for c := 1 to 3 do
      A[r,c] := r * 0.1 + c * 0.2;
end;

procedure SavePessoas(const FileName: string; const Arr: array of TPessoa);
var
  F: TPessoaFile;
  j: Integer;
begin
  Assign(F, FileName);
  Rewrite(F);
  for j := 0 to High(Arr) do
    Write(F, Arr[j]);
  Close(F);
end;

begin
  ClrScr;

  for i := 1 to MAXPESSOAS do
  begin
    Pessoas[i].Nome := 'Pessoa_' + Chr(64 + i);
    Pessoas[i].Idade := 20 + i;
    Pessoas[i].Pontuacao := i * 10;
    Pessoas[i].DiaFavorito := TDayOfWeek((i - 1) mod 7);
  end;

  Writeln('Factorial de 5 = ', Factorial(5));
  Writeln('Fibonacci de 10 = ', Fibonacci(10));

  InitArrayList(Lista, LenList, 5);
  Write('"Lista" em array: ');
  PrintArrayList(Lista, LenList);

  InitMatrix(M);
  Writeln('Matriz 3x3:');
  PrintMatrix(M);

  SavePessoas('pessoas.dat', Pessoas);
  Writeln('Ficheiro pessoas.dat gravado com sucesso.');

  Readln;
end.