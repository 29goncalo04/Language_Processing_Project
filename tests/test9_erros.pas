{exemplo 9 inventado mas com erros semânticos}
program DemoPascalISO7185;

const
  Max = 10;
  Greeting = 'Olá';

type
  SubRange  = 1..Max;                
  MyEnum    = (Low, Medium, High);    
  Day       = (Mon, Tue, Wed, Thu, Fri, Sat, Sun);
  {Erro semântico: tipo de elemento do conjunto é inválido}
  DaySet    = set of Greeting;
  {Erro semântico: tipo 'int' não existe}        
  IntArray  = packed array[1..Max] of int;
  {Erro semântico: tipo 'bool' não existe}        
  RecType   = record                 
               number: integer;
               flag: bool;
             end;
  
var
  i      : SubRange;
  j      : integer;
  arr    : IntArray;
  enumv  : MyEnum;
  daysetv: DaySet;
  {Erro semântico: tipo 'Rec1' não existe}
  rec    : Rec1;
  c      : char;
label
  100, 200;                 

function SumArray(a: IntArray): integer;
var
  idx: SubRange;
  total: integer;
begin
  total := 0;
  {Erro semântico: a expressãp final do ciclo 'FOR' deve ser um inteiro e não um 'real'}
  for idx := 1 to real(10) do
    total := total + a[idx];
  {Erro semântico: 'total' é um inteiro e não um array}
  SumArray := total[1];
end;

procedure FillArray(var a: IntArray);
var
  {Erro semântico: variável de controlo do 'FOR' tem de ser integer}
  idx: set of SubRange;
begin
  for idx := 1 to 10 do
    {Erro semântico: função 'length' não existe}
    a[idx] := length(idx * idx);
end;

procedure RecordDemo(var r: RecType);
begin
  with r do
  begin
    number := 3 + 1;
    {Erro semântico: 'not' precisa de receber algo do tipo 'boolean'}
    flag   := not (3+1);
  end;
end;

function Factorial(n: integer): integer;
begin
  if n <= 1 then
    {Erro semântico: função 'Factorial' precia de retornar um 'integer'}
    Factorial := '1'
  else
    {Erro semântico: função 'Factorial' precisa de receber um argumento do tipo 'integer'}
    Factorial := n * Factorial(true);
end;

begin
{Erro semântico: na label só foi declarado 100 e 200}
300:
  {Erro semântico: 'writeln' não pode receber o nome de uma função como argumento}
  writeln(Factorial);

  {Erro semântico: função 'FillArray' recebe um argumento de outro tipo}
  FillArray('arr');
  writeln('Conteúdos do array:');
  for i := 1 to 10 do
    {Erro semântico: 'writeln' não pode receber diretamente um array}
    writeln(' arr[', i, '] = ', arri);
  j := SumArray(arr);
  writeln('Soma do array = ', j);

  {Erro semântico: 'rec' não é inteiro}
  rec := 10;
  rec.flag   := false;
  RecordDemo(rec);
  {Erro semântico: writeln não pode receber argumento do tipo 'RecType'}
  writeln('Rec.number = ', rec, ', flag = ', rec.flag);

  {Erro semântico: tipos incompatíveis}
  enumv := 1;
  case enumv of
    {Erro semântico: variável não declarada}
    Lower   : writeln('Enumeração: Low');
    Medium: writeln('Enumeração: Medium');
    High  : writeln('Enumeração: High');
  end;

  daysetv := [Mon, Wed, Fri];
  {Erro semântico: do lado direito de 'in' tem de ser um conjunto}
  if Mon in Wed then
    writeln('Segunda-feira está no conjunto');

  j := Factorial(5);
  writeln('Factorial de 5 = ', j);

  {Erro semântico: tipos envolvidos na soma não são válidos}
  writeln('Olá'+1);
  repeat
    writeln('Introduz um carácter (X para sair):');
    readln(c);
  {Erro semântico: condição do REPEAT...UNTIL tem de ser do tipo 'boolean'}
  until c;

  writeln('A terminar o Demo');
200:
end.