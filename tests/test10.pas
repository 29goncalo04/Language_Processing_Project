program ComplexExamplePure;

const
  MAXPESSOAS = 5;
  MAXLIST = 5;

type
  // Subrange de 0 a 100 para pontuações
  TScore = 0..100;

  // Enumerado para dias da semana
  TDayOfWeek = (Segunda, Terca, Quarta, Quinta, Sexta, Sabado, Domingo);

  // Conjunto de caracteres
  TCharSet = set of Char;

  // Registo para pessoa
  TPessoa = record
    Nome: string[50];
    Idade: 1..120;
    Pontuacao: TScore;
    DiaFavorito: TDayOfWeek;
  end;

  // Array estático para simular lista ligada
  TIntArray = array[1..MAXLIST] of Integer;

  // Matriz 3x3 de reais
  TMatrix = array[1..3, 1..3] of Real;

  // Ficheiro de pessoas
  TPessoaFile = file of TPessoa;

var
  Pessoas: array[1..MAXPESSOAS] of TPessoa;
  Lista: TIntArray;
  LenList: Integer;
  M: TMatrix;
  i: Integer;

// Função que calcula factorial de n recursivamente
function Factorial(n: Integer): LongInt;
begin
  if n <= 1 then
    Factorial := 1
  else
    Factorial := n * Factorial(n - 1);
end;

// Função que retorna o n-ésimo termo de Fibonacci
function Fibonacci(n: Integer): LongInt;
begin
  if n in [0,1] then
    Fibonacci := n
  else
    Fibonacci := Fibonacci(n - 1) + Fibonacci(n - 2);
end;

// Procedimento para inicializar array como lista de 1..m
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

// Procedimento para imprimir "lista" em array
procedure PrintArrayList(const A: TIntArray; Len: Integer);
var
  idx: Integer;
begin
  for idx := 1 to Len do
    Write(A[idx], ' ');
  Writeln;
end;

// Procedimento para mostrar matriz
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

// Procedimento para preencher matriz com valores de exemplo
procedure InitMatrix(var A: TMatrix);
var
  r, c: Integer;
begin
  for r := 1 to 3 do
    for c := 1 to 3 do
      A[r,c] := r * 0.1 + c * 0.2;
end;

// Procedimento para gravar pessoas em ficheiro
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

// Programa principal
begin
  ClrScr;

  // Definir algumas pessoas de exemplo
  for i := 1 to MAXPESSOAS do
  begin
    Pessoas[i].Nome := 'Pessoa_' + Chr(64 + i);
    Pessoas[i].Idade := 20 + i;
    Pessoas[i].Pontuacao := i * 10;
    Pessoas[i].DiaFavorito := TDayOfWeek((i - 1) mod 7);
  end;

  // Mostrar factorial e Fibonacci
  Writeln('Factorial de 5 = ', Factorial(5));
  Writeln('Fibonacci de 10 = ', Fibonacci(10));

  // Simulação de lista usando array
  InitArrayList(Lista, LenList, 5);
  Write('"Lista" em array: ');
  PrintArrayList(Lista, LenList);

  // Matriz 3x3
  InitMatrix(M);
  Writeln('Matriz 3x3:');
  PrintMatrix(M);

  // Guardar em ficheiro
  SavePessoas('pessoas.dat', Pessoas);
  Writeln('Ficheiro pessoas.dat gravado com sucesso.');

  Readln;
end.