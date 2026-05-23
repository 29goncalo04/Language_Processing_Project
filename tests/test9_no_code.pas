{exemplo inventado sem geração de código e com análise semântica limitada}
program DemoPascalISO7185;

{ Constantes e arrays empacotados }
const
  Max = 10;
  Greeting = 'Olá';

{ Definições de tipos }
type
  SubRange  = 1..Max;                  { subrange }
  MyEnum    = (Low, Medium, High);     { enumeração }
  Day       = (Mon, Tue, Wed, Thu, Fri, Sat, Sun);
  DaySet    = set of Day;              { conjunto de valores enumerados }
  IntArray  = array[1..Max] of integer;
  RecType   = record                    { registo }
               number: integer;
               flag: boolean;
             end;
  
{ Variáveis globais }
var
  i      : SubRange;
  j      : integer;
  arr    : IntArray;
  enumv  : MyEnum;
  daysetv: DaySet;
  rec    : RecType;
  c      : char;
label
  100, 200;                     { rótulos + goto }

{ Função para somar todos os elementos de um array }
function SumArray(a: IntArray): integer;
var
  idx: SubRange;
  total: integer;
begin
  total := 0;
  for idx := 1 to 10 do
    total := total + a[idx];
  SumArray := total;
end;

{ Procedimento para preencher um array com quadrados }
procedure FillArray(var a: IntArray);
var
  idx: SubRange;
begin
  for idx := 1 to 10 do
    a[idx] := idx * idx;
end;

{ Procedimento que demonstra uso de with e registos }
procedure RecordDemo(var r: RecType);
begin
  with r do
  begin
    number := 3 + 1;
    flag   := not false;
  end;
end;

{ Função recursiva para factorial }
function Factorial(n: integer): integer;
begin
  if n <= 1 then
    Factorial := 1
  else
    Factorial := n * Factorial(n - 1);
end;

begin { Main }
100:
  writeln('*** Início do Demo Pascal ISO 7185 ***');

  { Trabalhar com array e funções }
  FillArray(arr);
  writeln('Conteúdos do array:');
  for i := 1 to 10 do
    writeln(' arr[', i, '] = ', arr[i]);
  j := SumArray(arr);
  writeln('Soma do array = ', j);

  { Registo e with }
  rec.number := 10;
  rec.flag   := false;
  RecordDemo(rec);
  writeln('Rec.number = ', rec.number, ', flag = ', rec.flag);

  { Enumerações e case }
  enumv := High;
  case enumv of
    Low   : writeln('Enumeração: Low');
    Medium: writeln('Enumeração: Medium');
    High  : writeln('Enumeração: High');
  end;

  { Conjuntos }
  daysetv := [Mon, Wed, Fri];
  if Mon in daysetv then
    writeln('Segunda-feira está no conjunto');

  { Factorial }
  j := Factorial(5);
  writeln('Factorial de 5 = ', j);

  { Carácter e repeat…until }
  writeln('Olá');
  repeat
    writeln('Introduz um carácter (X para sair):');
    readln(c);
  until c = 'X';

  writeln('A terminar o Demo');
200:
end.